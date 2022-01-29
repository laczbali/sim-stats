import datetime
import math

class RunData:
    """
    A general representation of a run, between all games
    """
    
    def __init__(self):
        self.lap_times_sec = [] # user chooses how it is saved in DB (GameHandler.GameHandlerProcessMode)
        self.run_time_sec : float = 0 # does not get saved in DB

        self.total_laps : float = 0 # does not get saved in DB
        self.laps_completed : float = 0 # does not get saved in DB

        self.car = ""
        self.car_class = ""

        self.track = ""
        self.track_conditions = ""

        self.run_date : datetime = datetime.datetime.now()
    


    def format_time(timesec: float) -> str:
        return "{:02.0f}:{:02.0f}:{:03.0f}".format(
            timesec // 60, math.floor(timesec % 60), (timesec % 1) * 1000
        )



    def set_parameters(parameters):
        """
        """
        pass