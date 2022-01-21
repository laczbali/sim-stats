import json

class AppSettings:
    """
    Reads settings from settings.json
    """

    def read_setting(self, key : str):
        """
        Reads a setting from settings.json
        """
        with open("settings.json", "r") as f:
            settings = json.load(f)
            try:
                return settings[key]
            except KeyError:
                return None