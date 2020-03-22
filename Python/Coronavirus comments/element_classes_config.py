import os
import json

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
config_file = "element_classes_config.json"
config_file_path = os.path.join(WORKING_DIRECTORY, config_file)


class ElementClassesConfig:
    def __init__(self):
        with open(config_file_path, "r") as json_config:
            self.elements = json.load(json_config)
