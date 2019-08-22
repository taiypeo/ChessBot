from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from loguru import logger
from ..config import DB_PATH

engine = create_engine(DB_PATH)

Base = declarative_base()

from .user import User
from .game import Game

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

from .add_to_database import add_to_database

logger.info("SQLAlchemy session is ready")
