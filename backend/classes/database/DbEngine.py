import os
from sqlalchemy import create_engine
from classes.database.models.Base import Base


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