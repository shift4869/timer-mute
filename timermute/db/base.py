from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from timermute.db.model import Base as ModelBase


class Base(metaclass=ABCMeta):
    def __init__(self, db_fullpath="Mute.db"):
        self.dbname = db_fullpath
        self.db_url = f"sqlite:///{self.dbname}"

        self.engine = create_engine(
            self.db_url,
            echo=False,
            poolclass=StaticPool,
            # pool_recycle=5,
            connect_args={
                "timeout": 30,
                "check_same_thread": False,
            },
        )
        ModelBase.metadata.create_all(self.engine)

    def now(self):
        destination_format = "%Y-%m-%d %H:%M:%S"
        now_datetime = datetime.now()
        return now_datetime.strftime(destination_format)

    @abstractmethod
    def select(self):
        return []

    @abstractmethod
    def upsert(self, record):
        return []

    @abstractmethod
    def delete(self, key):
        return []

    @abstractmethod
    def mute(self, key):
        return []

    @abstractmethod
    def unmute(self, key):
        return []


if __name__ == "__main__":
    from timermute.db.mute_word_db import MuteWordDB

    db_fullpath = Path("mute.db")
    db_cont = MuteWordDB(db_fullpath=str(db_fullpath))
    pass
