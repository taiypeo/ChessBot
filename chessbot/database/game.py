from sqlalchemy import Column, String, Integer, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from . import Base
from ..config import EXPIRATION_TIMEDELTA

WHITE = 0
BLACK = 1
DRAW = 2


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, nullable=False, primary_key=True)

    white_id = Column(Integer, ForeignKey("users.id"))
    white = relationship("User", foreign_keys=[white_id], backref="white_games")

    black_id = Column(Integer, ForeignKey("users.id"))
    black = relationship("User", foreign_keys=[black_id], backref="black_games")

    pgn = Column(String, default="*", nullable=False)
    winner = Column(SmallInteger)

    expiration_date = Column(
        DateTime,
        default=lambda: datetime.datetime.now() + EXPIRATION_TIMEDELTA,
        nullable=False,
    )

    def __repr__(self) -> str:
        winner_str = (
            "In progress"
            if self.winner is None
            else ["White", "Black", "Draw"][self.winner]
        )
        return f"<Game id={self.id}; winner={winner_str}; expiration_date={self.expiration_date}>"
