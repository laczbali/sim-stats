from typing import List

from sqlalchemy import distinct, select

from classes.database.DbEngine import engine
from sqlalchemy.orm import Session

from classes.database.models.Base import Base
from classes.database.models.Car import Car
from classes.database.models.Game import Game
from classes.database.models.Run import Run
from classes.database.models.Track import Track
from classes.database.models.Run import Tag

from classes.game.RunData import RunData


# quick note on DB joins, for my future self:
# 
# let's say we have 2 tables:
# | table1          |     | table2      |
# | col1 | table2_a |     | colA | colB |
#
# JOIN appends table1 and table2 side-by-side:
# | joined-table                  |
# | col1 | table2_a | colA | colB |
#
# we define how we want to match rows, with the 'ON' clause:
# select * from table1 JOIN table2 ON table1.table2_a = table2.colA
# This will add a row from table2 to each row in table1, where table1.table2_a = table2.colA
#
# If a row from either table has no matching row from the other table,
# the resulting row will be defined by the type of join:
# - INNER: only return matching rows
# - LEFT: return all rows from 'left'. If it has no match, table2 cols will be null
# - RIGHT: return all rows from 'right'. If it has no match, table1 cols will be null
# - FULL: return all rows from 'left' and 'right'. If it has no match, other table cols will be null


class DBHandler:
  
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

        session: Session
        with Session(engine) as session:
            # the game should be in the DB by default, find it
            game: Game = session.execute(
                select(Game).where(Game.name == run_data.game_name)
            ).scalars().first()
            if game is None:
                raise Exception(f"Game \"{run_data.game_name}\" not found in database")

            # try to find track
            track: Track = session.execute(
                select(Track).where(Track.name == run_data.track, Track.game_id == game.id)
            ).scalars().first()
            # if track does not exist, create it
            if track is None:
                track = Track(name=run_data.track, game=game)
                session.add(track)

            # try to find car
            car: Car = session.execute(
                select(Car).where(Car.name == run_data.car, Car.game_id == game.id)
            ).scalars().first()
            # if car does not exist, create it
            if car is None:
                car = Car(name=run_data.car, game=game, car_class=run_data.car_class)
                session.add(car)

            # create a run for each laptime
            for lap_time in run_data.lap_times_sec:
                run = Run(
                    game=game,

                    conditions=run_data.track_conditions,
                    run_date=run_data.run_date,
                    runtime_seconds=lap_time,

                    track=track,
                    car=car,
                )

                # add tags
                for tag_name in run_data.tags:
                    # try to find tag
                    tag: Tag = session.execute(
                        select(Tag).where(Tag.name == tag_name.lower())
                    ).scalars().first()
                    # if tag does not exist, create it
                    if tag is None:
                        tag = Tag(name=tag_name.lower())
                        session.add(tag)

                    # add tag to run
                    run.tags.append(tag)

                session.add(run)

            # save all changes
            session.commit()


    def get_saved_tracks(game_name: str) -> List[str]:
        """
        Returns all track names in the DB, for a given game
        """

        session: Session
        with Session(engine) as session:
            tracks = session.execute(
                select(Track)
                .join(Game, Track.game_id == Game.id)
                .where(Game.name == game_name)
            ).scalars().all()

        # return the track names
        return [track.name for track in tracks]


    def get_saved_track_conditions(game_name: str) -> List[str]:
        """
        Returns all unique track conditions of RunData saved in the DB, for a given game
        """

        session: Session
        with Session(engine) as session:
            conditions = session.execute(
                select(distinct(Run.conditions))
                .join(Game, Run.game_id == Game.id)
                .where(Game.name == game_name)
            ).scalars().all()

        return conditions


    def get_saved_cars(game_name: str) -> List[str]:
        """
        Returns all cars (name, class) in the DB, for a given game
        """

        session: Session
        with Session(engine) as session:
            cars = session.execute(
                select(Car)
                .join(Game, Car.game_id == Game.id)
                .where(Game.name == game_name)
            ).scalars().all()

        # return car-name, car-class tuples
        return [(car.name, car.car_class) for car in cars]



    def get_saved_car_classes(game_name: str) -> List[str]:
        """
        Returns all unique car classes saved in the DB, for a given game
        """

        session: Session
        with Session(engine) as session:
            car_classes = session.execute(
                select(distinct(Car.car_class))
                .join(Game, Car.game_id == Game.id)
                .where(Game.name == game_name)
            ).scalars().all()

        return car_classes


    def get_saved_tags(game_name: str) -> List[str]:
        """
        Returns all unique tags saved in the DB, for a given game AND for all games

        { "all": [ ], "game": [ ] }
        """

        session: Session
        with Session(engine) as session:
            # get all tags
            all_tags = session.execute(
                select(Tag)
            ).scalars().all()

            # get all runs for the game
            runs = session.execute(
                select(Run)
                .join(Game, Run.game_id == Game.id)
                .where(Game.name == game_name)
            ).scalars().all()

            # get tag names fro all_tags
            all_tag_names = [tag.name for tag in all_tags]

            # get all tags for the runs
            game_tags = []
            for run in runs:
                game_tags.extend(run.tags)

            # get all unique tags
            game_tag_names = list(set(tag.name for tag in game_tags))

        return {
            "all": all_tag_names,
            "game": game_tag_names,
        }