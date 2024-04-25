import toml
from copy import deepcopy
from importlib import import_module


def loadConfigDB(filename):
    """
    Load configuration from a TOML file.

    Parameters
    ----------
    filename : str
        The path to the TOML file containing the configuration.

    Returns
    -------
    dict
        The configuration loaded from the TOML file.
    """
    with open(filename) as f:
        db = toml.load(f)
    return db


def simpleResolver(fullclassname):
    """
    Resolve a full class name to a class object.

    Parameters
    ----------
    fullclassname : str
        The full class name to resolve.

    Returns
    -------
    type
        The class object resolved from the full class name.
    """
    class_name = fullclassname.split(".")[-1]
    module_name = ".".join(fullclassname.split(".")[:-1])
    module = import_module(module_name)
    cls = getattr(module, class_name)
    return cls


def instantiateDevice(device_key, info, cls=None, namespace=None):
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
    prefix = device_info.pop("prefix", "")
    add_to_namespace = device_info.pop("_add_to_ns", True)
    device = cls(prefix, name=name, **device_info)

    if add_to_namespace and namespace is not None:
        namespace[device_key] = device
    return device


def loadDeviceConfig(filename, namespace=None):
    """
    Load device configuration from a file and instantiate devices.

    Parameters
    ----------
    filename : str
        The path to the file containing the device configuration.
    namespace : dict, optional
        The namespace to add the instantiated devices to.

    Returns
    -------
    dict
        A dictionary of instantiated devices.
    """
    db = loadConfigDB(filename)
    device_dict = {}
    for key, info in db.items():
        device = instantiateDevice(key, info, namespace=namespace)
        device_dict[key] = device
    return device_dict
