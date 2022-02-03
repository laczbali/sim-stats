from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (
        UniqueConstraint('name', 'game_id'),
        {"sqlite_autoincrement": True}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    car_class = Column(String)

    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    game = relationship("Game", back_populates="cars")
    runs = relationship("Run", back_populates="car")