from typing import List

from classes.database.DbEngine import engine
from sqlalchemy.orm import Session

from classes.database.models.Car import Car
from classes.database.models.Game import Game
from classes.database.models.Track import Track
from classes.database.models.Run import Run
from classes.database.models.Run import Tag

from classes.game.RunData import RunData



class DBHandler:

    # # DEBUG ONLY, WILL REMOVE
    # def test_add():

    #     with Session(engine) as session:
    #         testgame = Game(name="my-game")
    #         session.add(testgame)

    #         testtrack = Track(name="my-track", game=testgame)
    #         session.add(testtrack)

    #         session.commit()

    # # DEBUG ONLY, WILL REMOVE
    # def test_get():

    #     with Session(engine) as session:
    #         # get track with name "my-track"
    #         track = session.query(Track).filter_by(name="my-track").first()
    #         print(track.name, track.game.name)


    def save_run(run_data: RunData):
        """
        Save a run to the database
        - track / tack_condition
        - car / car_class
        - tags
        - runtime (each lap time will be a separate run entry)
        - run date
        """
        
        print("* saving run to database")

        with Session(engine) as session:
            # the game should be in the DB by default, find it
            game = session.query(Game).filter_by(name=run_data.game_name).first()

            # try to find track
            track = session.query(Track).filter_by(name=run_data.track, game=game).first()
            # if track does not exist, create it
            if track is None:
                track = Track(name=run_data.track, game=game)
                session.add(track)

            # try to find car
            car = session.query(Car).filter_by(name=run_data.car, game=game).first()


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