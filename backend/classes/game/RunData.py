import datetime
import math

class RunData:
    """
    A general representation of a run, between all games
    """
    
    def __init__(self):
        self.game_name = ""

        self.lap_times_sec = [] # user chooses how it is saved in DB (GameHandler.GameHandlerProcessMode)
        self.run_time_sec : float = 0 # does not get saved in DB

        self.total_laps : float = 0 # does not get saved in DB
        self.laps_completed : float = 0 # does not get saved in DB

        self.car = ""
        self.car_class = ""

        self.track = ""
        self.track_conditions = ""

        self.tags = []

        self.run_date : datetime = datetime.datetime.now()
    


    def format_time(timesec: float) -> str:
        return "{:02.0f}:{:02.0f}:{:03.0f}".format(
            timesec // 60, math.floor(timesec % 60), (timesec % 1) * 1000
        )



    def set_parameters(self, parameters):
        """
        Set the parameters of the run
        
        Available parameters:
        - car, car_class, track, track_conditions, tags
        """
    
        if "car" in parameters:
            self.car = parameters["car"]

        if "car_class" in parameters:
            self.car_class = parameters["car_class"]

        if "track" in parameters:
            self.track = parameters["track"]

        if "track_conditions" in parameters:
            self.track_conditions = parameters["track_conditions"]

        if "tags" in parameters:
            self.tags = parameters["tags"]

        
