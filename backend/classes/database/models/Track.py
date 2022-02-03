from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from . import Base


class Track(Base):
    __tablename__ = "tracks"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    game_id = Column(Integer, ForeignKey("games.id"))
    
    game = relationship("Game", back_populates="tracks")