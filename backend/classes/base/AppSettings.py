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
