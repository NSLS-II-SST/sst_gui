from sst_funcs.configuration import findAndLoadDevice
from .models import GVModel, PVModel, MotorModel, EnergyModel, BaseModel

SST_CONFIG = "/home/jamie/work/nsls-ii-sst/ucal/ucal/sim_config.yaml"


def modelFromOphyd(prefix, group=None, label=None, modelClass=BaseModel):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    model = modelClass(name, obj, group, label)
    return model


def pvFromOphyd(prefix, group=None, label=None):
    return modelFromOphyd(prefix, group, label, modelClass=PVModel)


def gvFromOphyd(prefix, group=None, label=None):
    return modelFromOphyd(prefix, group, label, modelClass=GVModel)


def motorFromOphyd(prefix, group=None, label=None):
    return modelFromOphyd(prefix, group, label, modelClass=MotorModel)


def energyModelFromOphyd(prefix, group=None, label=None):
    energy = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = energy.name
    energy_motor = MotorModel(
        name=energy.monoen.name,
        obj=energy.monoen,
        group=group,
        label=energy.monoen.name,
    )
    gap_motor = MotorModel(
        name=energy.epugap.name,
        obj=energy.epugap,
        group=group,
        label=energy.epugap.name,
    )
    phase_motor = MotorModel(
        name=energy.epuphase.name,
        obj=energy.epuphase,
        group=group,
        label=energy.epuphase.name,
    )
    grating_motor = MotorModel(
        name=energy.monoen.gratingx.name,
        obj=energy.monoen.gratingx,
        group=group,
        label=energy.monoen.gratingx.name,
    )
    enModel = EnergyModel(
        name,
        energy_motor,
        gap_motor,
        phase_motor,
        grating_motor,
        group,
        label,
    )
    return enModel
