from abc import ABC, abstractmethod
from typing import Any
from classes.base.AppSettings import AppSettings
from classes.base.UdpHandler import UdpHandler


class GameHandler(ABC):

    def __init__(self) -> None:
        """
        Initializes the game handler.

        Loads game settings from settings.json (settings.game_settings.GAMENAME).
        If it doesn't exist, it creates a default entry, based on Class.get_default_settings()
        """

        self.udp_handler = None
        self.game_settings = None

        classname = self.__class__.__name__
        if classname == "GameHandler":
            raise NotImplementedError("GameHandler is an abstract class and cannot be instantiated directly.")

        # Get game-specific settings, based on the game's name
        game_name = classname.replace("Game", "")
        try:
            self.game_settings = AppSettings().read_setting("game_settings")[game_name]
        except (TypeError, KeyError):
            # if game_settings is missing, "None" is returned. Accessing it with game_name will raise a TypeError
            # if game_settings is found, but the game_name is not it it, a KeyError is raised

            # set default values
            self.game_settings = self.__class__.get_default_settings()
            AppSettings().append_setting("game_settings", game_name, self.game_settings)

        # Create UDP handler
        self.udp_handler = UdpHandler()



    def get_default_settings(self) -> Any:
        """
        Returns the default settings that are common between games
        """
        return {"udp_port": 20777, "udp_buffer_size": 1024}



    def start_listening(self):
        """
        Starts listening for UDP data
        """
        self.udp_handler.start_listen(self.game_settings["udp_port"], self.game_settings["udp_buffer_size"])



    def stop_listening(self):
        """
        Stops listening for UDP data
        """
        self.udp_handler.stop_listen()



    def udp_data(self) -> bytes:
        """
        Returns the last UDP data received
        """
        return self.udp_handler.get_data()



    # --------------------------------------------------------------------------------------------------------------
    # Abstartct (forced to override) methods:
    # --------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def parse_udp_data(self):
        pass



    @abstractmethod
    def wait_for_run_start(self):
        pass



    @abstractmethod
    def wait_for_run_end(self):
        pass



    @abstractmethod
    def get_run_progress(self):
        pass



    @abstractmethod
    def get_run_results(self):
        pass



    @abstractmethod
    def process_run(self):
        pass
