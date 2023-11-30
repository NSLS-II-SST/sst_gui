from sst_funcs.configuration import findAndLoadDevice
from .models import GVModel, PVModel, MotorModel, EnergyModel, OphydModel

SST_CONFIG = "/home/jamie/work/nsls-ii-sst/ucal/ucal/sim_config.yaml"


def modelFromOphyd(prefix, group=None, label=None):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    model = OphydModel(name, obj, group, label)
    return model


def pvFromOphyd(prefix, group=None, label=None):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    pvModel = PVModel(name, obj, group, label)
    return pvModel


def gvFromOphyd(prefix, group=None, label=None):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    gvModel = GVModel(name, obj, group, label)
    return gvModel


def motorFromOphyd(prefix, group=None, label=None):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    mtrModel = MotorModel(name, obj, group, label)
    return mtrModel


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
