from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base


class Game(Base):
    __tablename__ = "games"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    tracks = relationship("Track", back_populates="game")
    cars = relationship("Car", back_populates="game")
    runs = relationship("Run", back_populates="game")