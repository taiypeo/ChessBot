from typing import TypeVar
from sqlalchemy.exc import DatabaseError
from loguru import logger

from . import session

T = TypeVar("T")


def add_to_database(obj: T) -> None:
    try:
        session.add(obj)
        session.commit()
    except DatabaseError as err:
        logger.error(err)

        session.rollback()
