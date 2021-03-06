import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from classes.database.models.Base import Base
from classes.database.models.Game import Game


# db file is at ./backend/db/db.sqlite3
cwd = os.getcwd()
db_path = os.path.join(cwd, "db.sqlite3")

engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"timeout": 60},
    future=True
)

# create table if missing
Base.metadata.create_all(engine)

# add default contents
session: Session
with Session(engine) as session:
    # add "DirtRally2" game if missing
    game: Game = session.execute(
        select(Game).where(Game.name == "DirtRally2").limit(1)
    ).scalars().first()

    if game is None:
        game = Game(name="DirtRally2")
        session.add(game)
        session.commit()