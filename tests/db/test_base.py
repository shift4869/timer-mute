import sys
from typing import Self
import unittest

from mock import patch

from timermute.db.base import Base
from sqlalchemy.pool import StaticPool

from timermute.db.model import Base as ModelBase
from timermute.util import Result


class ConcreteBase(Base):
    def __init__(self, db_fullpath=":memory:") -> None:
        super().__init__(db_fullpath)

    def select(self) -> list[Self]:
        return ["select()"]

    def upsert(self, record: ModelBase) -> Result:
        return Result.SUCCESS

    def delete(self, key_screen_name: str) -> Result:
        return Result.SUCCESS

    def mute(self, key_screen_name: str, unmuted_at: str) -> Result:
        return Result.SUCCESS

    def unmute(self, key_screen_name: str) -> Result:
        return Result.SUCCESS


class TestBase(unittest.TestCase):
    def test_init(self):
        mock_engine = self.enterContext(patch("timermute.db.base.create_engine"))
        mock_model_base = self.enterContext(patch("timermute.db.base.ModelBase"))

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
        self.assertEqual(Result.SUCCESS, instance.upsert("record"))
        self.assertEqual(Result.SUCCESS, instance.delete("key_screen_name"))
        self.assertEqual(Result.SUCCESS, instance.mute("key_screen_name", "unmuted_at"))
        self.assertEqual(Result.SUCCESS, instance.unmute("key_screen_name"))


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
