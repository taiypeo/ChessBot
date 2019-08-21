from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from loguru import logger
from ..config import DB_PATH

engine = create_engine(DB_PATH)

Base = declarative_base()

from .user import User
from .game import Game, WHITE, BLACK, DRAW

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

logger.info("SQLAlchemy session is ready")
