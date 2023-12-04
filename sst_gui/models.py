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
            print(f"Loading {key} in BeamlineModel")
            setattr(self, key, instantiateGroup(key, filename=config_file))
        self.energy["energy"].energy.rotation_motor = self.manipulators[
            "manipulator"
        ].obj.r
        print("Finished loading BeamlineModel")


class EnergyModel:
    default_controller = "EnergyControl"
    default_monitor = "EnergyMonitor"

    def __init__(
        self,
        name,
        energy,
        energy_motor,
        gap_motor,
        phase_motor,
        grating_motor,
        group,
        label,
        **kwargs,
    ):
        self.name = name
        self.energy = energy
        self.energy_motor = energy_motor
        self.gap_motor = gap_motor
        self.phase_motor = phase_motor
        self.grating_motor = grating_motor
        self.group = group
        self.label = label
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseModel(QWidget):
    default_controller = None
    default_monitor = "PVMonitor"

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__()
        self.name = name
        self.obj = obj
        self.group = group
        self.label = label
        self.enabled = True
        for key, value in kwargs.items():
            setattr(self, key, value)


class GVModel(BaseModel):
    default_controller = "GVControl"
    default_monitor = "GVMonitor"
    gvStatusChanged = Signal(str)

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
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


class PVModelRO(BaseModel):
    valueChanged = Signal(str)

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
        self.value_type = None
        self.obj.subscribe(self._value_changed, run=True)

    def _value_changed(self, value, **kwargs):
        if self.value_type is None:
            if isinstance(value, float):
                self.value_type = float
            elif isinstance(value, int):
                self.value_type = int
            elif isinstance(value, str):
                self.value_type = str
            else:
                self.value_type = type(value)
        if self.value_type is float:
            value = "{:.2f}".format(value)
        elif self.value_type is int:
            value = "{:d}".format(value)
        else:
            value = str(value)
        self.valueChanged.emit(value)


class PVModel(PVModelRO):
    def set(self, val):
        self.obj.set(val).wait()


class ScalarModel(BaseModel):
    valueChanged = Signal(str)

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
        self.value_type = None
        self.obj.target.subscribe(self._value_changed, run=True)

    def _value_changed(self, value, **kwargs):
        if self.value_type is None:
            if isinstance(value, float):
                self.value_type = float
            elif isinstance(value, int):
                self.value_type = int
            elif isinstance(value, str):
                self.value_type = str
            else:
                self.value_type = type(value)
        if self.value_type is float:
            value = "{:.2f}".format(value)
        elif self.value_type is int:
            value = "{:d}".format(value)
        else:
            value = str(value)
        self.valueChanged.emit(value)


class MotorModel(PVModel):
    default_controller = "MotorControl"
    default_monitor = "MotorMonitor"
    movingStatusChanged = Signal(bool)

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
        self.obj.motor_is_moving.subscribe(self._update_moving_status)
        if hasattr(self.obj, "user_setpoint"):
            self.setpoint = self.obj.user_setpoint
        elif hasattr(self.obj, "setpoint"):
            self.setpoint = self.obj.setpoint
        else:
            self.setpoint = self.obj

    def _update_moving_status(self, value, **kwargs):
        self.movingStatusChanged.emit(value)

    @property
    def position(self):
        try:
            return self.obj.position
        except:
            return 0

    def set(self, value):
        self.setpoint.set(value).wait()


class PVPositionerModel(PVModel):
    default_controller = "MotorControl"
    default_monitor = "MotorMonitor"
    movingStatusChanged = Signal(bool)

    def _update_moving_status(self, value, **kwargs):
        if value == 0:
            self.movingStatusChanged.emit(True)
        else:
            self.movingStatusChanged.emit(False)


class ControlModel(BaseModel):
    controlChange = Signal(str)

    def __init__(self, name, obj, group, label, requester=None, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
        self.requester = requester
        self.obj.subscribe(self._control_change)

    def request_control(self, requester=None):
        if requester is None:
            requester = self.requester
        if requester is not None:
            self.obj.set(requester).wait(timeout=10)
        else:
            raise ValueError("Cannot request control with requester None")

    def _control_change(self, *args, value, **kwargs):
        self.controlChange.emit(value)


class HexapodModel(BaseModel):
    pass


class ManipulatorModel(BaseModel):
    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__(name, obj, group, label, **kwargs)
        self.real_axes_models = [
            MotorModel(
                name=real_axis.name, obj=real_axis, group=group, label=real_axis.name
            )
            for real_axis in obj.real_positioners
        ]
