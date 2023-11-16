from dataclasses import dataclass
from bluesky_widgets.qt.threading import FunctionWorker
from qtpy.QtCore import QObject, Slot
from bluesky_queueserver_api import BFunc
import time

from sst_funcs.configuration import loadConfigDB, findAndLoadDevice, getObjConfig
#loadConfigDB("/home/xf07id1/nsls-ii-sst/ucal/ucal/object_config.yaml")

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
        response = self.REClientModel._client.function_execute(function, run_in_background=True)
        self.REClientModel._client.wait_for_completed_task(response['task_uid'])
        reply = self.REClientModel._client.task_result(response['task_uid'])
        task_status = reply['status']
        task_result = reply['result']
        if task_status == 'completed' and task_result.get('success', False):
            return task_result['return_value']
        else:
            raise ValueError("Update unsuccessful")

    def _reload_status(self):
        function = BFunc("get_status")
        response = self.REClientModel._client.function_execute(function, run_in_background=True)
        self.REClientModel._client.wait_for_completed_task(response['task_uid'])
        reply = self.REClientModel._client.task_result(response['task_uid'])
        task_status = reply['status']
        task_result = reply['result']
        if task_status == 'completed' and task_result.get('success', False):
            user_status = task_result['return_value']
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
        self._deactivate_updates = (not is_connected or not worker_exists)
        if not self._deactivate_updates and not self.updates_activated:
            self._start_thread()


class BeamlineModel:
    def __init__(self):
        self.energy = findAndLoadDevice("energy")
        self.eslit = findAndLoadDevice("Exit_Slit")
        self.manipulator = findAndLoadDevice("manipulator")
        self.energy.rotation_motor = self.manipulator.r


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


def energyModelFromOphyd(energy):
    name = energy.name
    energy_RB = energy.monoen.readback.pvname
    energy_SP = energy.monoen.setpoint.pvname
    gap_RB = energy.epugap.user_readback.pvname
    gap_SP = energy.epugap.user_setpoint.pvname
    phase_RB = energy.epuphase.user_readback.pvname
    phase_SP = energy.epuphase.user_setpoint.pvname
    grating_RB = energy.monoen.gratingx.readback.pvname
    grating_SP = energy.monoen.gratingx.setpoint.pvname
    enModel = EnergyModel(name,
                          energy_RB, energy_SP,
                          gap_RB, gap_SP,
                          phase_RB, phase_SP,
                          grating_RB, grating_SP)
    return enModel


@dataclass
class GVModel:
    name: str
    state_RB: str
    cmd_open: str
    cmd_close: str
    openval: int = 1
    closeval: int = 0


def gvFromOphyd(gv):
    name = gv.name
    state_RB = gv.state.pvname
    openval = gv.openval
    closeval = gv.closeval
    cmd_open = gv.opn.pvname
    cmd_close = gv.cls.pvname
    gvModel = GVModel(name, state_RB, cmd_open, cmd_close, openval, closeval)
    return gvModel


@dataclass
class PVModel:
    name: str
    display_name: str
    prefix: str


def pvFromOphyd(oph):
    name = oph.name
    display_name = getattr(oph, "display_name", name)
    prefix = oph.pvname
    pvModel = PVModel(name, display_name, prefix)
    return pvModel


@dataclass
class MotorModel:
    name: str
    display_name: str
    prefix: str


def motorFromOphyd(mtr):
    name = mtr.name
    display_name = getattr(mtr, "display_name", name)
    prefix = mtr.prefix
    mtrModel = MotorModel(name, display_name, prefix)
    return mtrModel


class ManipulatorModel:
    def __init__(self, manipulator):
        self._manipulator = manipulator
        
