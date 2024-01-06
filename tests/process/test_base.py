import sys
import unittest

import PySimpleGUI as sg
from mock import MagicMock, call

from timermute.db.mute_user_db import MuteUserDB
from timermute.db.mute_word_db import MuteWordDB
from timermute.process.base import Base
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result


class ConcreteBase(Base):
    def __init__(self, main_winfow_info: MainWindowInfo) -> None:
        super().__init__(main_winfow_info)

    def run(self) -> Result:
        return Result.SUCCESS


class TestBase(unittest.TestCase):
    def test_init(self):
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        instance = ConcreteBase(main_winfow_info)
        self.assertEqual(main_winfow_info, instance.main_winfow_info)
        with self.assertRaises(ValueError):
            instance = ConcreteBase("invalid_arg")

    def test_update_mute_word_table(self):
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.window = MagicMock(spec=sg.Window)
        main_winfow_info.mute_word_db = MagicMock(spec=MuteWordDB)
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        main_winfow_info.mute_word_db.select.side_effect = lambda: [r]
        instance = ConcreteBase(main_winfow_info)
        actual = instance.update_mute_word_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.mute_word_db.select(),
                call.window.__getitem__("-LIST_1-"),
                call.window.__getitem__().update(values=[]),
                call.window.__getitem__("-LIST_2-"),
                call.window.__getitem__().update(values=["to_muted_table_list()"]),
            ],
            main_winfow_info.mock_calls,
        )
        main_winfow_info.reset_mock()

        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        main_winfow_info.mute_word_db.select.side_effect = lambda: [r]
        actual = instance.update_mute_word_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.mute_word_db.select(),
                call.window.__getitem__("-LIST_1-"),
                call.window.__getitem__().update(values=["to_unmuted_table_list()"]),
                call.window.__getitem__("-LIST_2-"),
                call.window.__getitem__().update(values=[]),
            ],
            main_winfow_info.mock_calls,
        )

    def test_update_mute_user_table(self):
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.window = MagicMock(spec=sg.Window)
        main_winfow_info.mute_user_db = MagicMock(spec=MuteUserDB)
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        main_winfow_info.mute_user_db.select.side_effect = lambda: [r]
        instance = ConcreteBase(main_winfow_info)
        actual = instance.update_mute_user_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.mute_user_db.select(),
                call.window.__getitem__("-LIST_3-"),
                call.window.__getitem__().update(values=[]),
                call.window.__getitem__("-LIST_4-"),
                call.window.__getitem__().update(values=["to_muted_table_list()"]),
            ],
            main_winfow_info.mock_calls,
        )
        main_winfow_info.reset_mock()

        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        main_winfow_info.mute_user_db.select.side_effect = lambda: [r]
        actual = instance.update_mute_user_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.mute_user_db.select(),
                call.window.__getitem__("-LIST_3-"),
                call.window.__getitem__().update(values=["to_unmuted_table_list()"]),
                call.window.__getitem__("-LIST_4-"),
                call.window.__getitem__().update(values=[]),
            ],
            main_winfow_info.mock_calls,
        )

    def test_run(self):
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        instance = ConcreteBase(main_winfow_info)
        actual = instance.run()
        self.assertEqual(Result.SUCCESS, actual)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
