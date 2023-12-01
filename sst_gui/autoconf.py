import yaml


def modify_yaml(
    input_filename, output_filename, translation_dict, default_target="modelFromOphyd"
):
    """
    Modifies a YAML file based on a translation dictionary and writes the result to a new file.

    This function reads a YAML file, traverses its structure, and replaces certain values based on the provided
    translation dictionary. The modified data is then written to a new YAML file.

    Parameters:
    input_filename (str): The path to the input YAML file to be modified.
    output_filename (str): The path where the modified YAML data will be written.
    translation_dict (dict): A dictionary mapping class names to their new values. Used to replace "_target_" values in the YAML data.
    default_target (dict): A default translation for class names that are not provided in translation_dict. If None, classes not found in the translation_dict will raise a KeyError

    Returns:
    None
    """
    with open(input_filename, "r") as file:
        data = yaml.safe_load(file)

    def replace_target_values(data):
        for key, value in data.items():
            if key == "_target_":
                class_name = value.split(".")[-1]
                if value in translation_dict:
                    data[key] = translation_dict[value]
                elif class_name in translation_dict:
                    data[key] = translation_dict[class_name]
                elif default_target is not None:
                    data[key] = default_target
                else:
                    raise KeyError(
                        f"{class_name} not found in translation_dict and no\
                          default target was provided"
                    )
            elif key == "name":
                data["label"] = data.pop("name")
            elif isinstance(value, dict):
                replace_target_values(value)

    replace_target_values(data)

    with open(output_filename, "w") as file:
        yaml.safe_dump(data, file)


def convert_config(input_filename, output_filename, translation_updates={}):
    """
    Converts a beamline config file into a GUI config file using a default class mapping.

    This function reads a beamline config file, replaces the Ophyd class targets with GUI class targets, and

    Parameters:
    input_filename (str): The path to the input YAML file to be modified.
    output_filename (str): The path where the modified YAML data will be written.
    translation_dict (dict): A dictionary mapping class names to their new values.

    Returns:
    None
    """
    default_translation_dict = {
        "I400SingleCh": "ScalarModel",
        "PrettyMotorFMBO": "MotorModel",
        "FMBHexapodMirror": "HexapodModel",
        "EpicsSignalRO": "ScalarModel",
        "EpicsSignal": "PVModel",
        "ShutterSet": "GVModel",
        "EPS_Shutter": "GVModel",
        "ManipulatorBuilder": "ManipulatorModel",
        "ADCBuffer": "ScalarModel",
        "EPICS_ADR": "ADRModel",
        "PrettyMotor": "MotorModel",
        "NewEnPos": "EnergyModel",
        "StandardProsilicaV33": "PVModel",
        "MultiMeshBuilder": "ManipulatorModel",
    }
    default_translation_dict.update(translation_updates)
    modify_yaml(input_filename, output_filename, default_translation_dict)
