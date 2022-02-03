from tkinter import N
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from . import Base


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