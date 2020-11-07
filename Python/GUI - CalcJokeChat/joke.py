import os
import sys
import json


class Jokes:
    def __init__(self):
        jokes_file = "jokes.json"
        jokes_file_path = self.get_resource_path(jokes_file)

        try:
            with open(jokes_file_path, 'r', encoding='utf-8') as my_file:
                self.JOKES = json.load(my_file)
        except:
            jokes = ["impossible to fetch jokes"]

    @staticmethod
    def get_resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.realpath(__file__))

        return os.path.join(base_path, relative_path)
