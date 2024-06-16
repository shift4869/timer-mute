import sys
import unittest
from typing import Self

from mock import patch
from sqlalchemy.pool import StaticPool

from timer_mute.db.base import Base
from timer_mute.db.model import Base as ModelBase
from timer_mute.util import Result


class ConcreteBase(Base):
    def __init__(self, db_fullpath=":memory:") -> None:
        super().__init__(db_fullpath)

    def select(self) -> list[Self]:
        return ["select()"]

    def upsert(self, record: ModelBase) -> Result:
        return Result.success

    def delete(self, key_screen_name: str) -> Result:
        return Result.success

    def mute(self, key_screen_name: str, unmuted_at: str) -> Result:
        return Result.success

    def unmute(self, key_screen_name: str) -> Result:
        return Result.success


class TestBase(unittest.TestCase):
    def test_init(self):
        mock_engine = self.enterContext(patch("timer_mute.db.base.create_engine"))
        mock_model_base = self.enterContext(patch("timer_mute.db.base.ModelBase"))

        mock_engine.return_value = "create_engine()"

        instance = ConcreteBase()
        self.assertEqual(":memory:", instance.dbname)
        self.assertEqual("sqlite:///:memory:", instance.db_url)
        self.assertEqual("create_engine()", instance.engine)

        mock_engine.assert_called_once_with(
            "sqlite:///:memory:",
            echo=False,
            poolclass=StaticPool,
            connect_args={
                "timeout": 30,
                "check_same_thread": False,
            },
        )
        mock_model_base.metadata.create_all.assert_called_once_with("create_engine()")

        with self.assertRaises(ValueError):
            instance = ConcreteBase(-1)

    def test_abstractmethod(self):
        instance = ConcreteBase()
        self.assertEqual(["select()"], instance.select())
        self.assertEqual(Result.success, instance.upsert("record"))
        self.assertEqual(Result.success, instance.delete("key_screen_name"))
        self.assertEqual(Result.success, instance.mute("key_screen_name", "unmuted_at"))
        self.assertEqual(Result.success, instance.unmute("key_screen_name"))


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
