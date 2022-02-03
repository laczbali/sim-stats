from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base


run_tag_table = Table(
    "run_tags",
    Base.metadata,
    Column("run_id", Integer, ForeignKey("runs.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
    UniqueConstraint("run_id", "tag_id"),
)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conditions = Column(String)
    run_date = Column(DateTime, nullable=False)
    runtime_seconds = Column(Integer, nullable=False)

    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)

    game = relationship("Game", back_populates="runs")
    track = relationship("Track", back_populates="runs")
    car = relationship("Car", back_populates="runs")
    tags = relationship("Tag", secondary=run_tag_table, back_populates="runs")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    runs = relationship("Run", secondary=run_tag_table, back_populates="tags")