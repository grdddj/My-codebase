import json

from helpers import get_resource_path


class Jokes:
    def __init__(self) -> None:
        jokes_file = "jokes.json"
        jokes_file_path = get_resource_path(jokes_file)

        try:
            with open(jokes_file_path, "r", encoding="utf-8") as my_file:
                self.JOKES = json.load(my_file)
        except Exception as err:
            self.JOKES = [f"Impossible to fetch jokes. Err: {err}"]
