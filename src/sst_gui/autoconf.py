import yaml


def modify_yaml(
    input_filename,
    output_filename,
    translation_dict,
    default_target="sst_gui.loaders.modelFromOphyd",
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

    def replace_target_values(data, last_key=None):
        new_data = {}
        for key in list(data.keys()):
            value = data[key]
            if key == "_target_":
                class_name = value.split(".")[-1]
                if value in translation_dict:
                    new_data[key] = translation_dict[value]
                elif class_name in translation_dict:
                    new_data[key] = translation_dict[class_name]
                elif default_target is not None:
                    new_data[key] = default_target
                else:
                    raise KeyError(
                        f"{class_name} not found in translation_dict and no\
                          default target was provided"
                    )
            elif key == "name":
                new_data["label"] = data["name"]
            elif key == "prefix":
                new_data["prefix"] = last_key
            elif isinstance(value, dict):
                new_data[key] = replace_target_values(value, key)
        return new_data

    new_data = replace_target_values(data)

    with open(output_filename, "w") as file:
        yaml.safe_dump(new_data, file)


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
        "I400SingleCh": "sst_gui.loaders.scalarFromOphyd",
        "PrettyMotorFMBO": "sst_gui.loaders.motorFromOphyd",
        "FMBHexapodMirror": "sst_gui.loaders.manipulatorFromOphyd",
        "EpicsSignalRO": "sst_gui.loaders.pvFromOphyd",
        "EpicsSignal": "sst_gui.loaders.pvFromOphyd",
        "ShutterSet": "sst_gui.loaders.gvFromOphyd",
        "EPS_Shutter": "sst_gui.loaders.gvFromOphyd",
        "ManipulatorBuilder": "sst_gui.loaders.manipulatorFromOphyd",
        "ADCBuffer": "sst_gui.loaders.scalarFromOphyd",
        "PrettyMotor": "sst_gui.loaders.motorFromOphyd",
        "NewEnPos": "sst_gui.loaders.energyModelFromOphyd",
        "StandardProsilicaV33": "sst_gui.loaders.pvFromOphyd",
        "MultiMeshBuilder": "sst_gui.loaders.manipulatorFromOphyd",
    }
    default_translation_dict.update(translation_updates)
    modify_yaml(input_filename, output_filename, default_translation_dict)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a beamline config file into a GUI config file."
    )
    parser.add_argument(
        "input_filename",
        type=str,
        help="The path to the input YAML file to be modified.",
    )
    parser.add_argument(
        "output_filename",
        type=str,
        help="The path where the modified YAML data will be written.",
    )

    args = parser.parse_args()

    convert_config(args.input_filename, args.output_filename)
