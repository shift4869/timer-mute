import sys
import unittest

import freezegun
from sqlalchemy.orm.exc import NoResultFound

from timer_mute.db.model import MuteUser
from timer_mute.db.mute_user_db import MuteUserDB
from timer_mute.util import Result, now


class TestMuteUserDB(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = MuteUserDB(db_fullpath=":memory:")
        mute_user_list = self._get_mute_user_list()
        for mute_user in mute_user_list:
            self.instance.upsert(mute_user)

    def _get_user_tuple(self, index: int = 0) -> tuple[str]:
        return (f"test_account_{index}", "unmuted", f"2024-01-05 00:01:{index:02}", f"2024-01-05 00:02:{index:02}", "")

    def _get_mute_user(self, index: int = 0) -> MuteUser:
        mute_user_tuple = self._get_user_tuple(index)
        mute_user_record = MuteUser(
            screen_name=mute_user_tuple[0],
            status=mute_user_tuple[1],
            created_at=mute_user_tuple[2],
            updated_at=mute_user_tuple[3],
            unmuted_at=mute_user_tuple[4],
        )
        mute_user_record.id = index
        return mute_user_record

    def _get_mute_user_list(self, max_index: int = 5) -> list[MuteUser]:
        return [self._get_mute_user(index) for index in range(max_index)]

    def test_select(self):
        expect = self._get_mute_user_list()
        actual = self.instance.select()
        self.assertEqual(expect, actual)

    def test_upsert(self):
        mute_user_list = self._get_mute_user_list()
        n = len(mute_user_list)
        mute_user_record = self._get_mute_user(n)

        # INSERT
        actual = self.instance.upsert(mute_user_record)
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n + 1)
        self.assertEqual(expect, actual)

        # UPDATE
        mute_user_record = self._get_mute_user(0)
        mute_user_record.status = "muted"
        mute_user_record.id = -1
        actual = self.instance.upsert(mute_user_record)
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n + 1)
        expect[0].status = "muted"
        self.assertEqual(expect, actual)

        with self.assertRaises(ValueError):
            actual = self.instance.upsert("invalid_arg")

    def test_delete(self):
        mute_user_list = self._get_mute_user_list()
        n = len(mute_user_list)
        mute_user_record = self._get_mute_user(n - 1)

        actual = self.instance.delete(mute_user_record.screen_name)
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n - 1)
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.delete("invalid_key_screen_name")
        with self.assertRaises(ValueError):
            actual = self.instance.delete(-1)

    def test_mute(self):
        self.enterContext(freezegun.freeze_time("2024-01-05 10:00:00"))
        mute_user_list = self._get_mute_user_list()
        n = len(mute_user_list)
        new_unmuted_at = "2024-01-05 11:01:00"

        mute_user_record = self._get_mute_user(0)
        actual = self.instance.mute(mute_user_record.screen_name, new_unmuted_at)
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n)
        expect[0].status = "muted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = new_unmuted_at
        self.assertEqual(expect, actual)

        actual = self.instance.mute(mute_user_record.screen_name, "")
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n)
        expect[0].status = "muted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = ""
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.mute("invalid_key_screen_name", "")
        with self.assertRaises(ValueError):
            actual = self.instance.mute(-1, "")
        with self.assertRaises(ValueError):
            actual = self.instance.mute(mute_user_record.screen_name, -1)

    def test_unmute(self):
        self.enterContext(freezegun.freeze_time("2024-01-05 10:00:00"))
        mute_user_list = self._get_mute_user_list()
        n = len(mute_user_list)

        mute_user_record = self._get_mute_user(0)
        actual = self.instance.unmute(mute_user_record.screen_name)
        self.assertEqual(Result.success, actual)
        actual = self.instance.select()
        expect = self._get_mute_user_list(n)
        expect[0].status = "unmuted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = ""
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.unmute("invalid_key_screen_name")
        with self.assertRaises(ValueError):
            actual = self.instance.unmute(-1)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
