from dataclasses import dataclass
from bluesky_widgets.qt.threading import FunctionWorker
from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QWidget
from bluesky_queueserver_api import BFunc
import time
from sst_funcs.configuration import findAndLoadDevice

# loadConfigDB("/home/xf07id1/nsls-ii-sst/ucal/ucal/object_config.yaml")


class UserStatus(QObject):
    def __init__(self, runEngineClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.REClientModel = runEngineClient
        self.REClientModel.events.status_changed.connect(self.on_status_update)
        self._signal_registry = {}
        self._uid_registry = {}
        self._thread = None
        self.updates_activated = False
        self.update_period = 1

    def _start_thread(self):
        self._thread = FunctionWorker(self._reload_status)
        self._thread.finished.connect(self._reload_complete)
        self.updates_activated = True
        self._thread.start()

    def _reload_complete(self):
        if not self._deactivate_updates:
            self._start_thread()
        else:
            self.updates_activated = False
            self._deactivate_updates = False

    def get_update(self, key):
        function = BFunc("request_update", key)
        response = self.REClientModel._client.function_execute(
            function, run_in_background=True
        )
        self.REClientModel._client.wait_for_completed_task(response["task_uid"])
        reply = self.REClientModel._client.task_result(response["task_uid"])
        task_status = reply["status"]
        task_result = reply["result"]
        if task_status == "completed" and task_result.get("success", False):
            return task_result["return_value"]
        else:
            raise ValueError("Update unsuccessful")

    def _reload_status(self):
        function = BFunc("get_status")
        response = self.REClientModel._client.function_execute(
            function, run_in_background=True
        )
        self.REClientModel._client.wait_for_completed_task(response["task_uid"])
        reply = self.REClientModel._client.task_result(response["task_uid"])
        task_status = reply["status"]
        task_result = reply["result"]
        if task_status == "completed" and task_result.get("success", False):
            user_status = task_result["return_value"]
        else:
            raise ValueError("Status did not load successfully")
        new_uids = {}

        for key, signal_list in self._signal_registry.items():
            new_uid = user_status.get(key, "")
            if new_uid != self._uid_registry.get(key, ""):
                update = self.get_update(key)
                for sig in signal_list:
                    sig.emit(update)
                new_uids[key] = new_uid
        self._uid_registry.update(new_uids)
        time.sleep(self.update_period)

    def register_signal(self, key, signal):
        if key in self._signal_registry:
            self._signal_registry[key].append(signal)
        else:
            self._signal_registry[key] = [signal]

    def on_status_update(self, event):
        is_connected = bool(event.is_connected)
        status = event.status
        worker_exists = status.get("worker_environment_exists", False)
        self._deactivate_updates = not is_connected or not worker_exists
        if not self._deactivate_updates and not self.updates_activated:
            self._start_thread()


class BeamlineModel:
    def __init__(self):
        self.energy = findAndLoadDevice("energy")
        self.eslit = findAndLoadDevice("Exit_Slit")
        self.manipulator = findAndLoadDevice("manipulator")
        self.energy.rotation_motor = self.manipulator.r


class ControlModel(QWidget):
    controlChange = Signal(str)

    def __init__(self, signal, requester):
        self.signal = signal
        self.requester = requester
        self.signal.subscribe(self._control_change)

    def request_control(self):
        self.signal.set(self.requester)

    def _control_change(self, *args, value, **kwargs):
        self.controlChange.emit(value)


@dataclass
class OphydModel:
    name: str
    obj: object
    group: str = ""
    label: str = ""


@dataclass
class EnergyModel:
    name: str
    energy_RB: str
    energy_SP: str
    gap_RB: str
    gap_SP: str
    phase_RB: str
    phase_SP: str
    grating_RB: str
    grating_SP: str


class BaseModel:
    def __init__(self, name, obj, group, label):
        self.name = name
        self.obj = obj
        self.group = group
        self.label = label
        self.enabled = True


class GVModel(BaseModel):
    def open(self):
        self.obj.open_nonplan()

    def close(self):
        self.obj.close_nonplan()


class PVModel(BaseModel):
    def set(self, val):
        self.obj.set(val)


class ScalarModel(BaseModel):
    pass


class MotorModel(BaseModel):
    pass


class HexapodModel(BaseModel):
    pass


class ManipulatorModel:
    def __init__(self, manipulator):
        self._manipulator = manipulator
