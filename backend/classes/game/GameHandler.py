from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
import math
from numpy import median

from classes.database.DBHandler import DBHandler
from classes.game.RunData import RunData
from classes.base.AppSettings import AppSettings
from classes.base.UdpHandler import UdpHandler



class GameHandlerState(Enum):
    """
    Enum for the game handlers states
    """

    IDLE = 0
    WAITING_FOR_START = 1
    RUNNING = 2
    FINISHED = 3
    ABORTED = 4


class GameHandlerProcessMode(Enum):
    """
    Enum for the game handlers save modes
    """

    DISCARD = 0
    BEST = 1
    LAST = 2
    ALL = 3
    MEAN = 4
    MEDIAN = 5



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
        self._run_result: RunData = None

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
            print("* missing settings for game: " + game_name)
            raise Exception()

        # Create UDP handler
        self.udp_handler = UdpHandler()



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

    def _set_state(self, new_state: GameHandlerState):
        """
        Sets the current state of the game handler
        """
        self._state = new_state
        pass



    def get_state(self) -> GameHandlerState:
        """
        Returns the current state of the game handler
        """
        return self._state



    def is_run_over(self):
        return self._state == GameHandlerState.FINISHED or self._state == GameHandlerState.ABORTED



    def get_run_result(self) -> RunData:
        """
        Returns the RunData if the Run is over, None otherwise
        """
        if self.is_run_over():
            return self._run_result
        else:
            return None



    def process_run(self, process_mode: GameHandlerProcessMode, edited_data: RunData = None):
        """
        Saves or discards the run data, as selected by the user

        :param process_mode: what to do with the data? Discard, or save in one of several ways
        :param edited_data: None, if the data is to be handled as it was, or RunData type if it was edited after the run was over
        :param discard_bottom_percent: how many percent of the data to discard from the bottom
        :param discard_top_percent: how many percent of the data to discard from the top
        """

        # make sure we are in a FINISHED or ABORTED state
        if not self.is_run_over():
            raise RuntimeError("Run is not over yet")

        # use edited_data, if provided
        data_to_process: RunData = edited_data if edited_data is not None else self._run_result

        # process data as needed
        match process_mode:
            case GameHandlerProcessMode.DISCARD:
                # do nothing
                pass

            case GameHandlerProcessMode.BEST:
                # sort laptimes, keep only the smallest one
                data_to_process.lap_times_sec.sort()
                data_to_process.lap_times_sec = data_to_process.lap_times_sec[:1]
                pass

            case GameHandlerProcessMode.LAST:
                # keep only the last lap
                data_to_process.lap_times_sec = data_to_process.lap_times_sec[-1:]
                pass

            case GameHandlerProcessMode.ALL:
                # do nothing
                pass

            case GameHandlerProcessMode.MEAN:
                # calculate mean, keep only that
                lap_mean_time = sum(data_to_process.lap_times_sec) / len(data_to_process.lap_times_sec)
                data_to_process.lap_times_sec = [lap_mean_time]
                pass

            case GameHandlerProcessMode.MEDIAN:
                # calculate median, keep only that
                lap_median_time = median(data_to_process.lap_times_sec)
                data_to_process.lap_times_sec = [lap_median_time]
                pass

            case _:
                raise ValueError("Invalid process mode")

        # save data
        if process_mode != GameHandlerProcessMode.DISCARD:
            DBHandler.save_run(data_to_process)

        # reset instance
        self._reset_instance()



    def _reset_instance(self, keep_config = False):
        """
        Resets the class instance to a known state, so that a new run can be started

        Resets the state to IDLE, and clears the run result (keeps the track and car config if keep_config is True)
        """
        
        if keep_config:
            # keep config values from the previous run
            track_name = self._run_result.track
            track_conditions = self._run_result.track_conditions
            car_name = self._run_result.car
            car_class = self._run_result.car_class

            # set up a new run, with the previous config values
            self._run_result = RunData()
            self._run_result.track = track_name
            self._run_result.track_conditions = track_conditions
            self._run_result.car = car_name
            self._run_result.car_class = car_class
        else:
            self._run_result = None

        self._state = GameHandlerState.IDLE



    def shutdown(self):
        """
        Does everything necessary to properly dispose of the class instance
        """
        
        if self.get_state() == GameHandlerState.IDLE:
            return

        if self.is_run_over() == False:
            self.stop_run()
            self.process_run(GameHandlerProcessMode.DISCARD)
            return

        if self.get_state() == GameHandlerState.FINISHED:
            self.process_run(GameHandlerProcessMode.DISCARD)
            return


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
    def get_attributes():
        pass