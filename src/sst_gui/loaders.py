from sst_funcs.configuration import findAndLoadDevice
from .models import (
    GVModel,
    PVModel,
    MotorModel,
    PVModelRO,
    ScalarModel,
    ManipulatorModel,
    EnergyModel,
    BaseModel,
    ControlModel,
    PVPositionerModel,
)
import pkg_resources

SST_CONFIG = pkg_resources.resource_filename("ucal", "sim_config.yaml")


def modelFromOphyd(prefix, group=None, label=None, modelClass=BaseModel, **kwargs):
    obj = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = obj.name
    if label is None:
        label = getattr(obj, "display_name", name)
    model = modelClass(name, obj, group, label, **kwargs)
    return model


def scalarFromOphyd(prefix, group=None, label=None, **kwargs):
    return modelFromOphyd(prefix, group, label, modelClass=ScalarModel, **kwargs)


def pvFromOphyd(prefix, group=None, label=None, **kwargs):
    return modelFromOphyd(prefix, group, label, modelClass=PVModel, **kwargs)


def gvFromOphyd(prefix, group=None, label=None, **kwargs):
    return modelFromOphyd(prefix, group, label, modelClass=GVModel, **kwargs)


def motorFromOphyd(prefix, group=None, label=None, **kwargs):
    return modelFromOphyd(prefix, group, label, modelClass=MotorModel, **kwargs)


def manipulatorFromOphyd(prefix, group=None, label=None, **kwargs):
    return modelFromOphyd(prefix, group, label, modelClass=ManipulatorModel, **kwargs)


def controlFromOphyd(prefix, group=None, label=None, requester=None, **kwargs):
    return modelFromOphyd(
        prefix, group, label, modelClass=ControlModel, requester=requester, **kwargs
    )


def energyModelFromOphyd(prefix, group=None, label=None, **kwargs):
    energy = findAndLoadDevice(prefix, filename=SST_CONFIG)
    name = energy.name
    energy_motor = PVPositionerModel(
        name=energy.monoen.name,
        obj=energy.monoen,
        group=group,
        label=f"{name} Monochromator",
    )
    gap_motor = MotorModel(
        name=energy.epugap.name,
        obj=energy.epugap,
        group=group,
        label=f"{name} EPU Gap",
    )
    phase_motor = MotorModel(
        name=energy.epuphase.name,
        obj=energy.epuphase,
        group=group,
        label=f"{name} EPU Phase",
    )
    grating_motor = PVPositionerModel(
        name=energy.monoen.gratingx.name,
        obj=energy.monoen.gratingx,
        group=group,
        label=f"{name} Grating",
    )
    enModel = EnergyModel(
        name,
        energy,
        energy_motor,
        gap_motor,
        phase_motor,
        grating_motor,
        group,
        label,
        **kwargs,
    )
    return enModel
