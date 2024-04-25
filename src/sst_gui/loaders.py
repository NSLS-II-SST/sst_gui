from .load import instantiateDevice
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
    EnergyAxesModel,
)
from .settings import SETTINGS

# SST_CONFIG = pkg_resources.resource_filename("ucal", "sim_config.yaml")


def modelFromOphyd(
    prefix, group=None, label=None, modelClass=BaseModel, *, name, **kwargs
):
    obj_info = SETTINGS.object_config[prefix]
    obj = instantiateDevice(prefix, obj_info)
    if label is None:
        label = getattr(obj, "long_name", name)
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
    obj_info = SETTINGS.object_config[prefix]
    obj = instantiateDevice(prefix, obj_info)
    name = obj.name
    energy = EnergyAxesModel(name, obj, group, name)
    grating_motor = PVPositionerModel(
        name=obj.monoen.gratingx.name,
        obj=obj.monoen.gratingx,
        group=group,
        label=f"{name} Grating",
    )
    enModel = EnergyModel(
        name,
        obj,
        energy,
        grating_motor,
        group,
        label,
        **kwargs,
    )
    return enModel
