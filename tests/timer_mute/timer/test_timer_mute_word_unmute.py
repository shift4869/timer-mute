import sys
import unittest
from collections import namedtuple

import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timer_mute.db.model import MuteWord
from timer_mute.db.mute_word_db import MuteWordDB
from timer_mute.muter.muter import Muter
from timer_mute.timer.timer import MuteWordUnmuteTimer
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result


class TestTimerMuteWordUnmute(unittest.TestCase):
    def test_init(self):
        mock_timer = self.enterContext(patch("timer_mute.timer.timer.threading.Timer"))
        main_window_info = MagicMock(spec=MainWindowInfo)
        muter = MagicMock(spec=Muter)
        interval = 1.0
        target_keyword = "target_keyword"
        instance = MuteWordUnmuteTimer(main_window_info, muter, interval, target_keyword)
        self.assertEqual(main_window_info, instance.main_window_info)
        self.assertEqual(muter, instance.muter)
        self.assertEqual(target_keyword, instance.keyword)

    def test_update_mute_word_table(self):
        mock_timer = self.enterContext(patch("timer_mute.timer.timer.threading.Timer"))
        muter = MagicMock(spec=Muter)
        interval = 1.0
        target_keyword = "target_keyword"

        main_window_info = MagicMock(spec=MainWindowInfo)
        main_window_info.window = MagicMock(spec=sg.Window)
        main_window_info.mute_word_db = MagicMock(spec=MuteWordDB)
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        main_window_info.mute_word_db.select.side_effect = lambda: [r]
        instance = MuteWordUnmuteTimer(main_window_info, muter, interval, target_keyword)
        actual = instance.update_mute_word_table()
        self.assertEqual(Result.success, actual)
        self.assertEqual(
            [
                call.mute_word_db.select(),
                call.window.__getitem__("-LIST_1-"),
                call.window.__getitem__().update(values=[]),
                call.window.__getitem__("-LIST_2-"),
                call.window.__getitem__().update(values=["to_muted_table_list()"]),
            ],
            main_window_info.mock_calls,
        )
        main_window_info.reset_mock()

        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        main_window_info.mute_word_db.select.side_effect = lambda: [r]
        actual = instance.update_mute_word_table()
        self.assertEqual(Result.success, actual)
        self.assertEqual(
            [
                call.mute_word_db.select(),
                call.window.__getitem__("-LIST_1-"),
                call.window.__getitem__().update(values=["to_unmuted_table_list()"]),
                call.window.__getitem__("-LIST_2-"),
                call.window.__getitem__().update(values=[]),
            ],
            main_window_info.mock_calls,
        )

    def test_run(self):
        self.enterContext(patch("timer_mute.timer.timer.logger"))
        mock_update_mute_word_table = self.enterContext(
            patch("timer_mute.timer.timer.MuteWordUnmuteTimer.update_mute_word_table")
        )
        main_window_info = MagicMock(spec=MainWindowInfo)
        main_window_info.mute_word_db = MagicMock()
        main_window_info.mute_word_db.unmute = MagicMock()
        muter = MagicMock(spec=Muter)
        muter.unmute_keyword = MagicMock()
        interval = 1.0
        target_keyword = "target_keyword"
        instance = MuteWordUnmuteTimer(main_window_info, muter, interval, target_keyword)

        def pre_run(is_valid_unmute_keyword, is_valid_unmute):
            muter.unmute_keyword.reset_mock()
            if not is_valid_unmute_keyword:
                muter.unmute_keyword.side_effect = ValueError
            main_window_info.mute_word_db.unmute.reset_mock()
            if not is_valid_unmute:
                main_window_info.mute_word_db.unmute.side_effect = ValueError
            mock_update_mute_word_table.reset_mock()

        def post_run(is_valid_unmute_keyword, is_valid_unmute):
            muter.unmute_keyword.assert_called_once_with(target_keyword)
            main_window_info.mute_word_db.unmute.assert_called_once_with(target_keyword)
            mock_update_mute_word_table.assert_called_once_with()

        Params = namedtuple("Params", ["is_valid_unmute_keyword", "is_valid_unmute", "result"])
        params_list = [
            Params(True, True, Result.success),
            Params(True, False, Result.success),
            Params(False, True, Result.success),
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
