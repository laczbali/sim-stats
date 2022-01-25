from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from classes.game.RunData import RunData
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

        self._state: GameHandlerState = GameHandlerState.IDLE
        self._run_result = None

        classname = self.__class__.__name__
        if classname == "GameHandler":
            raise NotImplementedError(
                "GameHandler is an abstract class and cannot be instantiated directly."
            )

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



    # misc methods --------------------------------------------------------------------

    def get_default_settings(self) -> Any:
        """
        Returns the default settings that are common between games
        """
        return {"udp_port": 20777, "udp_buffer_size": 1024}



    # UDP related methods -------------------------------------------------------------

    def _start_listening(self):
        """
        Starts listening for UDP data
        """
        self.udp_handler.start_listen(
            self.game_settings["udp_port"], self.game_settings["udp_buffer_size"]
        )



    def _stop_listening(self):
        """
        Stops listening for UDP data
        """
        self.udp_handler.stop_listen()



    def udp_data(self) -> bytes:
        """
        Returns the last UDP data received
        """
        return self.udp_handler.get_data()



    # state handling methods ----------------------------------------------------------

    def _set_state(self, new_state):
        """
        Sets the current state of the game handler
        """
        self._state = new_state
        pass



    def get_state(self):
        """
        Returns the current state of the game handler
        """
        return self._state



    def is_run_over(self):
        return self._state == GameHandlerState.FINISHED or self._state == GameHandlerState.ABORTED



    def process_run(self):
        pass

    # --------------------------------------------------------------------------------------------------------------
    # Abstartct (forced to override) methods:
    # --------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def parse_udp_data(self) -> RunData:
        pass



    @abstractmethod
    def start_run(self):
        pass



    @abstractmethod
    def stop_run(self):
        pass


    @abstractmethod
    def get_run_progress(self):
        pass



class GameHandlerState(Enum):
    """
    Enum for the game handlers states
    """

    IDLE = 0
    WAITING_FOR_START = 1
    RUNNING = 2
    FINISHED = 3
    ABORTED = 4
