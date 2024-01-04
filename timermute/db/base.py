from abc import ABCMeta, abstractmethod
from typing import Self

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from timermute.db.model import Base as ModelBase
from timermute.util import Result


class Base(metaclass=ABCMeta):
    def __init__(self, db_fullpath: str = "mute.db") -> None:
        if not isinstance(db_fullpath, str):
            raise ValueError("db_fullpath must be str.")

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

    @abstractmethod
    def select(self) -> list[Self]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, record: ModelBase) -> Result:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key_screen_name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def mute(self, key_screen_name: str, unmuted_at: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def unmute(self, key_screen_name: str) -> Result:
        raise NotImplementedError


if __name__ == "__main__":
    from timermute.db.mute_word_db import MuteWordDB

    db_fullpath = ":memory:"
    mute_word_db = MuteWordDB(db_fullpath=str(db_fullpath))
    pass
