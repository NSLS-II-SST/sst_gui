from dataclasses import dataclass
from bluesky_widgets.qt.threading import FunctionWorker
from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QWidget
from bluesky_queueserver_api import BFunc
import time
from sst_funcs.configuration import instantiateGroup
import yaml

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
    def __init__(self, config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            for key in config.keys():
                setattr(self, key, instantiateGroup(key, filename=config_file))


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


class EnergyModel:
    def __init__(
        self,
        name,
        energy_motor,
        gap_motor,
        phase_motor,
        grating_motor,
        group,
        label,
    ):
        self.name = name
        self.energy_motor = energy_motor
        self.gap_motor = gap_motor
        self.phase_motor = phase_motor
        self.grating_motor = grating_motor
        self.group = group
        self.label = label


class BaseModel(QWidget):
    def __init__(self, name, obj, group, label):
        super().__init__()
        self.name = name
        self.obj = obj
        self.group = group
        self.label = label
        self.enabled = True


class GVModel(BaseModel):
    gvStatusChanged = Signal(str)

    def __init__(self, name, obj, group, label):
        super().__init__(name, obj, group, label)
        self.obj.state.subscribe(self._status_change, run=True)

    def open(self):
        self.obj.open_nonplan()

    def close(self):
        self.obj.close_nonplan()

    def _status_change(self, value, **kwargs):
        if value == self.obj.openval:
            self.gvStatusChanged.emit("open")
        elif value == self.obj.closeval:
            self.gvStatusChanged.emit("closed")


class PVModel(BaseModel):
    def set(self, val):
        self.obj.set(val)


class ScalarModel(BaseModel):
    pass


class MotorModel(BaseModel):
    positionChanged = Signal(float)
    movingStatusChanged = Signal(bool)

    def __init__(self, name, obj, group, label):
        super().__init__(name, obj, group, label)
        self.obj.subscribe(self._update_position)
        self.obj.motor_is_moving.subscribe(self._update_moving_status)

    def _update_position(self, value, **kwargs):
        self.positionChanged.emit(value)

    def _update_moving_status(self, value, **kwargs):
        self.movingStatusChanged.emit(value)

    def set_position(self, value):
        self.obj.set(value)

    @property
    def position(self):
        try:
            return self.obj.position
        except:
            return 0


class HexapodModel(BaseModel):
    pass


class ManipulatorModel(BaseModel):
    def __init__(self, name, obj, group, label):
        super().__init__(name, obj, group, label)
        self.real_axes_models = [
            MotorModel(
                name=real_axis.name, obj=real_axis, group=group, label=real_axis.name
            )
            for real_axis in obj.real_positioners
        ]
