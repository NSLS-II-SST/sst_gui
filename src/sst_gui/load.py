from copy import deepcopy
from nbs_core.autoload import simpleResolver, instantiateOphyd
from .settings import SETTINGS


def instantiateGUIDevice(device_key, info, cls=None, namespace=None):
    """
    Instantiate a device with given information.

    Parameters
    ----------
    device_key : str
        The key identifying the device.
    info : dict
        The information dictionary for the device.
    cls : type, optional
        The class to instantiate the device with. If not provided, it will be resolved from the info dictionary.
    namespace : dict, optional
        The namespace to add the instantiated device to.

    Returns
    -------
    object
        The instantiated device.
    """
    device_info = deepcopy(info)
    if cls is not None:
        device_info.pop("_target", None)
    elif device_info.get("_target", None) is not None:
        cls = simpleResolver(device_info.pop("_target"))
    else:
        raise KeyError("Could not find '_target' in {}".format(device_info))

    popkeys = [key for key in device_info if key.startswith("_")]
    for key in popkeys:
        device_info.pop(key)

    name = device_info.pop("name", device_key)
    device_info.pop("prefix", "")

    obj_info = SETTINGS.object_config[device_key]
    obj = instantiateOphyd(device_key, obj_info)

    group = device_info.pop("group", None)
    long_name = device_info.pop("long_name", name)
    device = cls(name, obj, group, long_name, **device_info)

    return device
