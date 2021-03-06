from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base


class Track(Base):
    __tablename__ = "tracks"
    __table_args__ = (
        UniqueConstraint('name', 'game_id'),
        {"sqlite_autoincrement": True}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    game = relationship("Game", back_populates="tracks")
    runs = relationship("Run", back_populates="track")