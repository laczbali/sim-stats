import json
import os
from typing import Any


class AppSettings:
    """
    Reads and writes settings from/to settings.json
    """

    def __init__(self) -> None:
        # create settings.json if missing
        if not os.path.isfile("settings.json"):
            with open("settings.json", "w") as f:
                f.write("{}")



    def read_setting(self, key: str):
        """
        Reads a setting from settings.json
        """

        with open("settings.json", "r") as f:
            settings = json.load(f)
            try:
                return settings[key]
            except KeyError:
                return None



    def set_setting(self, key: str, value: Any):
        """
        Writes a setting to settings.json
        """

        with open("settings.json", "r") as f:
            settings = json.load(f)
            settings[key] = value

        with open("settings.json", "w") as f:
            json.dump(settings, f)



    def append_setting(self, base_key: str, sub_key: str, value: Any):
        """
        Adds a child object (by sub_key) to a parent object (by base_key)

        like so {base: {x: y}} -> {base: {x: y, newkey: newval}}}
        """

        with open("settings.json", "r") as f:
            settings = json.load(f)

        try:
            base_value = settings[base_key]
        except KeyError:
            base_value = {}

        base_value[sub_key] = value
        settings[base_key] = base_value

        with open("settings.json", "w") as f:
            json.dump(settings, f)
