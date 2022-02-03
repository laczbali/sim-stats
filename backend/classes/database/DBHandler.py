from typing import List
from classes.game.RunData import RunData



class DBHandler:

    def save_run(run_data: RunData):
        print("* saving run to database")
        pass


    def get_saved_tracks(game_name: str) -> List[str]:
        return []


    def get_saved_track_conditions(game_name: str) -> List[str]:
        return []


    def get_saved_cars(game_name: str) -> List[str]:
        return []


    def get_saved_car_classes(game_name: str) -> List[str]:
        return []


    def get_saved_tags(game_name: str) -> List[str]:
        return []