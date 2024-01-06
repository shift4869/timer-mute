import configparser
import sys
import unittest
from collections import namedtuple

import freezegun
import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timermute.db.mute_word_db import MuteWordDB
from timermute.process.mute_word_mute import MuteWordMute
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result, get_future_datetime


class TestMuteWordMute(unittest.TestCase):
    def test_run(self):
        fake_now_str = "2024-01-06 12:34:56"
        self.enterContext(freezegun.freeze_time(fake_now_str))
        self.enterContext(patch("timermute.process.mute_word_mute.print"))
        self.enterContext(patch("timermute.process.mute_word_mute.logger.info"))
        mock_muter = self.enterContext(patch("timermute.process.mute_word_mute.Muter"))
        mock_popup_get_interval = self.enterContext(patch("timermute.process.mute_word_mute.popup_get_interval"))
        mock_mute_word_unmute_timer = self.enterContext(patch("timermute.process.mute_word_mute.MuteWordUnmuteTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.process.mute_word_mute.Base.update_mute_word_table")
        )
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.values = MagicMock(spec=dict)
        main_winfow_info.window = MagicMock(spec=sg.Window)
        main_winfow_info.mute_word_db = MagicMock(spec=MuteWordDB)
        main_winfow_info.config = MagicMock(spec=configparser.ConfigParser)
        instnace = MuteWordMute(main_winfow_info)

        def pre_run(index_list, mute_word_list_all, interval_min, is_valid_muter):
            main_winfow_info.values.reset_mock()
            main_winfow_info.values.__getitem__.side_effect = lambda key: index_list
            main_winfow_info.window.reset_mock()
            main_winfow_info.window.__getitem__.return_value.get.side_effect = lambda: mute_word_list_all
            main_winfow_info.mute_word_db.reset_mock()

            mock_muter.reset_mock()
            if not is_valid_muter:
                mock_muter.side_effect = ValueError
            mock_popup_get_interval.reset_mock()
            mock_popup_get_interval.side_effect = lambda: interval_min
            mock_mute_word_unmute_timer.reset_mock()
            mock_update_mute_word_table.reset_mock()

        def post_run(index_list, mute_word_list_all, interval_min, is_valid_muter):
            self.assertEqual([call.__getitem__("-LIST_1-")], main_winfow_info.values.mock_calls)
            self.assertEqual(
                [call.__getitem__("-LIST_1-"), call.__getitem__().get()], main_winfow_info.window.mock_calls
            )

            mute_word_list = []
            for i, mute_word in enumerate(mute_word_list_all):
                if i in index_list:
                    mute_word_list.append(mute_word)
            if not mute_word_list:
                main_winfow_info.mute_word_db.assert_not_called()
                mock_muter.reset_mock()
                mock_popup_get_interval.reset_mock()
                mock_mute_word_unmute_timer.reset_mock()
                mock_update_mute_word_table.assert_not_called()
                return

            mute_word_str = mute_word_list[0][1]
            if is_valid_muter:
                self.assertEqual(
                    [call(main_winfow_info.config), call().mute_keyword(mute_word_str)], mock_muter.mock_calls
                )
            else:
                self.assertEqual([call(main_winfow_info.config)], mock_muter.mock_calls)
                mock_popup_get_interval.assert_not_called()
                mock_mute_word_unmute_timer.assert_not_called()
                self.assertEqual([call()], mock_update_mute_word_table.mock_calls)
                return

            unmuted_at = get_future_datetime(interval_min * 60) if interval_min else ""
            if interval_min:
                self.assertEqual(
                    [
                        call(main_winfow_info, mock_muter.return_value, interval_min * 60, mute_word_str),
                        call().start(),
                    ],
                    mock_mute_word_unmute_timer.mock_calls,
                )
            else:
                mock_mute_word_unmute_timer.assert_not_called()

            self.assertEqual([call.mute(mute_word_str, unmuted_at)], main_winfow_info.mute_word_db.mock_calls)
            self.assertEqual([call()], mock_update_mute_word_table.mock_calls)

        Params = namedtuple("Params", ["index_list", "mute_word_list_all", "interval_min", "is_valid_muter", "result"])
        params_list = [
            Params([0], [(0, "mute_word_0")], 1, True, Result.SUCCESS),
            Params([0], [(0, "mute_word_0")], 0, True, Result.SUCCESS),
            Params([], [(0, "mute_word_0")], 1, True, Result.FAILED),
            Params([0], [(0, "mute_word_0")], 1, False, ValueError),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            expect = params[-1]
            if isinstance(expect, Result):
                actual = instnace.run()
                self.assertEqual(expect, actual)
            else:
                with self.assertRaises(expect):
                    actual = instnace.run()
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
