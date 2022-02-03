from typing import List

from classes.database.DbEngine import engine
from sqlalchemy.orm import Session

from classes.database.models.Game import Game
from classes.database.models.Track import Track

from classes.game.RunData import RunData



class DBHandler:

    # DEBUG ONLY, WILL REMOVE
    def test_add():

        with Session(engine) as session:
            testgame = Game(name="my-game")
            session.add(testgame)

            testtrack = Track(name="my-track", game=testgame)
            session.add(testtrack)

            session.commit()

    # DEBUG ONLY, WILL REMOVE
    def test_get():

        with Session(engine) as session:
            # get track with name "my-track"
            track = session.query(Track).filter_by(name="my-track").first()
            print(track.name, track.game.name)


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