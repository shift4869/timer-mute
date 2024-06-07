import sys
import unittest

import freezegun
from sqlalchemy.orm.exc import NoResultFound

from timer_mute.db.model import MuteWord
from timer_mute.db.mute_word_db import MuteWordDB
from timer_mute.util import Result, now


class TestMuteWordDB(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = MuteWordDB(db_fullpath=":memory:")
        mute_word_list = self._get_mute_word_list()
        for mute_word in mute_word_list:
            self.instance.upsert(mute_word)

    def _get_word_tuple(self, index: int = 0) -> tuple[str]:
        return (f"test_word_{index}", "unmuted", f"2024-01-05 00:01:{index:02}", f"2024-01-05 00:02:{index:02}", "")

    def _get_mute_word(self, index: int = 0) -> MuteWord:
        mute_word_tuple = self._get_word_tuple(index)
        mute_word_record = MuteWord(
            keyword=mute_word_tuple[0],
            status=mute_word_tuple[1],
            created_at=mute_word_tuple[2],
            updated_at=mute_word_tuple[3],
            unmuted_at=mute_word_tuple[4],
        )
        mute_word_record.id = index
        return mute_word_record

    def _get_mute_word_list(self, max_index: int = 5) -> list[MuteWord]:
        return [self._get_mute_word(index) for index in range(max_index)]

    def test_select(self):
        expect = self._get_mute_word_list()
        actual = self.instance.select()
        self.assertEqual(expect, actual)

    def test_upsert(self):
        mute_word_list = self._get_mute_word_list()
        n = len(mute_word_list)
        mute_word_record = self._get_mute_word(n)

        # INSERT
        actual = self.instance.upsert(mute_word_record)
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n + 1)
        self.assertEqual(expect, actual)

        # UPDATE
        mute_word_record = self._get_mute_word(0)
        mute_word_record.status = "muted"
        mute_word_record.id = -1
        actual = self.instance.upsert(mute_word_record)
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n + 1)
        expect[0].status = "muted"
        self.assertEqual(expect, actual)

        with self.assertRaises(ValueError):
            actual = self.instance.upsert("invalid_arg")

    def test_delete(self):
        mute_word_list = self._get_mute_word_list()
        n = len(mute_word_list)
        mute_word_record = self._get_mute_word(n - 1)

        actual = self.instance.delete(mute_word_record.keyword)
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n - 1)
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.delete("invalid_key_keyword")
        with self.assertRaises(ValueError):
            actual = self.instance.delete(-1)

    def test_mute(self):
        self.enterContext(freezegun.freeze_time("2024-01-05 10:00:00"))
        mute_word_list = self._get_mute_word_list()
        n = len(mute_word_list)
        new_unmuted_at = "2024-01-05 11:01:00"

        mute_word_record = self._get_mute_word(0)
        actual = self.instance.mute(mute_word_record.keyword, new_unmuted_at)
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n)
        expect[0].status = "muted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = new_unmuted_at
        self.assertEqual(expect, actual)

        actual = self.instance.mute(mute_word_record.keyword, "")
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n)
        expect[0].status = "muted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = ""
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.mute("invalid_key_keyword", "")
        with self.assertRaises(ValueError):
            actual = self.instance.mute(-1, "")
        with self.assertRaises(ValueError):
            actual = self.instance.mute(mute_word_record.keyword, -1)

    def test_unmute(self):
        self.enterContext(freezegun.freeze_time("2024-01-05 10:00:00"))
        mute_word_list = self._get_mute_word_list()
        n = len(mute_word_list)

        mute_word_record = self._get_mute_word(0)
        actual = self.instance.unmute(mute_word_record.keyword)
        self.assertEqual(Result.SUCCESS, actual)
        actual = self.instance.select()
        expect = self._get_mute_word_list(n)
        expect[0].status = "unmuted"
        expect[0].updated_at = now()
        expect[0].unmuted_at = ""
        self.assertEqual(expect, actual)

        with self.assertRaises(NoResultFound):
            actual = self.instance.unmute("invalid_key_keyword")
        with self.assertRaises(ValueError):
            actual = self.instance.unmute(-1)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
