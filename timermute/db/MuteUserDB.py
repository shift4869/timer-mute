# coding: utf-8
import re

from sqlalchemy import asc, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timermute.db.Base import Base


class MuteUserDB(Base):
    def __init__(self, db_fullpath: str = "mute.db"):
        super().__init__(db_fullpath)

    def select(self):
        return []

    def upsert(self, record):
        return []

    def delete(self, key):
        return []

    def mute(self, key):
        return []

    def unmute(self, key):
        return []
