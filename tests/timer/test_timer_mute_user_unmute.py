import sys
import unittest
from collections import namedtuple

import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timermute.db.model import MuteUser
from timermute.db.mute_user_db import MuteUserDB
from timermute.muter.muter import Muter
from timermute.timer.timer import MuteUserUnmuteTimer
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result


class TestTimerMuteUserUnmute(unittest.TestCase):
    def test_init(self):
        mock_timer = self.enterContext(patch("timermute.timer.timer.threading.Timer"))
        main_window_info = MagicMock(spec=MainWindowInfo)
        muter = MagicMock(spec=Muter)
        interval = 1.0
        target_screen_name = "target_screen_name"
        instance = MuteUserUnmuteTimer(main_window_info, muter, interval, target_screen_name)
        self.assertEqual(main_window_info, instance.main_window_info)
        self.assertEqual(muter, instance.muter)
        self.assertEqual(target_screen_name, instance.screen_name)

    def test_update_mute_user_table(self):
        mock_timer = self.enterContext(patch("timermute.timer.timer.threading.Timer"))
        muter = MagicMock(spec=Muter)
        interval = 1.0
        target_screen_name = "target_screen_name"

        main_window_info = MagicMock(spec=MainWindowInfo)
        main_window_info.window = MagicMock(spec=sg.Window)
        main_window_info.mute_user_db = MagicMock(spec=MuteUserDB)
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        main_window_info.mute_user_db.select.side_effect = lambda: [r]
        instance = MuteUserUnmuteTimer(main_window_info, muter, interval, target_screen_name)
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
            main_window_info.mock_calls,
        )
        main_window_info.reset_mock()

        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        main_window_info.mute_user_db.select.side_effect = lambda: [r]
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
            main_window_info.mock_calls,
        )

    def test_run(self):
        self.enterContext(patch("timermute.timer.timer.logger"))
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.timer.timer.MuteUserUnmuteTimer.update_mute_user_table")
        )
        main_window_info = MagicMock(spec=MainWindowInfo)
        main_window_info.mute_user_db = MagicMock()
        main_window_info.mute_user_db.unmute = MagicMock()
        muter = MagicMock(spec=Muter)
        muter.unmute_user = MagicMock()
        interval = 1.0
        target_screen_name = "target_screen_name"
        instance = MuteUserUnmuteTimer(main_window_info, muter, interval, target_screen_name)

        def pre_run(is_valid_unmute_user, is_valid_unmute):
            muter.unmute_user.reset_mock()
            if not is_valid_unmute_user:
                muter.unmute_user.side_effect = ValueError
            main_window_info.mute_user_db.unmute.reset_mock()
            if not is_valid_unmute:
                main_window_info.mute_user_db.unmute.side_effect = ValueError
            mock_update_mute_user_table.reset_mock()

        def post_run(is_valid_unmute_user, is_valid_unmute):
            muter.unmute_user.assert_called_once_with(target_screen_name)
            main_window_info.mute_user_db.unmute.assert_called_once_with(target_screen_name)
            mock_update_mute_user_table.assert_called_once_with()

        Params = namedtuple("Params", ["is_valid_unmute_user", "is_valid_unmute", "result"])
        params_list = [
            Params(True, True, Result.SUCCESS),
            Params(True, False, Result.SUCCESS),
            Params(False, True, Result.SUCCESS),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            expect = params[-1]
            actual = instance.run()
            self.assertEqual(expect, actual)
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
