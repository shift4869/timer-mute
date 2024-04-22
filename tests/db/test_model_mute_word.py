import sys
import unittest

from timermute.db.model import MuteWord


class TestMuteWord(unittest.TestCase):
    def test_init(self):
        keyword = "mute_word"
        status = "unmuted"
        created_at = "2024-01-05 12:34:56"
        updated_at = "2024-01-05 12:34:56"
        unmuted_at = "2024-01-06 12:34:56"
        instance = MuteWord(keyword, status, created_at, updated_at, unmuted_at)
        self.assertEqual(keyword, instance.keyword)
        self.assertEqual(status, instance.status)
        self.assertEqual(created_at, instance.created_at)
        self.assertEqual(updated_at, instance.updated_at)
        self.assertEqual(unmuted_at, instance.unmuted_at)
        self.assertEqual(f"<MuteWord(id='{None}', keyword='{keyword}')>", repr(instance))

        another_instance = MuteWord(keyword, status, created_at, updated_at, unmuted_at)
        self.assertTrue(instance == another_instance)
        another_instance.keyword = "another_mute_word"
        self.assertFalse(instance == another_instance)

    def test_to_dict(self):
        keyword = "mute_word"
        status = "unmuted"
        created_at = "2024-01-05 12:34:56"
        updated_at = "2024-01-05 12:34:56"
        unmuted_at = "2024-01-06 12:34:56"
        instance = MuteWord(keyword, status, created_at, updated_at, unmuted_at)
        actual = instance.to_dict()
        expect = {
            "id": None,
            "keyword": keyword,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
            "unmuted_at": unmuted_at,
        }
        self.assertEqual(expect, actual)

    def test_to_muted_table_list(self):
        keyword = "mute_word"
        status = "unmuted"
        created_at = "2024-01-05 12:34:56"
        updated_at = "2024-01-05 12:34:56"
        unmuted_at = "2024-01-06 12:34:56"
        instance = MuteWord(keyword, status, created_at, updated_at, unmuted_at)
        actual = instance.to_muted_table_list()
        expect = [
            None,
            keyword,
            updated_at,
            unmuted_at,
        ]
        self.assertEqual(expect, actual)

    def test_to_unmuted_table_list(self):
        keyword = "mute_word"
        status = "unmuted"
        created_at = "2024-01-05 12:34:56"
        updated_at = "2024-01-05 12:34:56"
        unmuted_at = "2024-01-06 12:34:56"
        instance = MuteWord(keyword, status, created_at, updated_at, unmuted_at)
        actual = instance.to_unmuted_table_list()
        expect = [
            None,
            keyword,
            updated_at,
            created_at,
        ]
        self.assertEqual(expect, actual)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
