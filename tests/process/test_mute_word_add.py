import configparser
import sys
import unittest
from collections import namedtuple

import freezegun
from mock import MagicMock, call, patch

from timermute.db.mute_word_db import MuteWordDB
from timermute.process.mute_word_add import MuteWordAdd
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result, get_future_datetime


class TestMuteWordAdd(unittest.TestCase):
    def test_run(self):
        fake_now_str = "2024-01-06 12:34:56"
        self.enterContext(freezegun.freeze_time(fake_now_str))
        self.enterContext(patch("timermute.process.mute_word_add.print"))
        self.enterContext(patch("timermute.process.mute_word_add.logger.info"))
        mock_popup_get_text = self.enterContext(patch("timermute.process.mute_word_add.popup_get_text"))
        mock_muter = self.enterContext(patch("timermute.process.mute_word_add.Muter"))
        mock_popup_get_interval = self.enterContext(patch("timermute.process.mute_word_add.popup_get_interval"))
        mock_mute_word_unmute_timer = self.enterContext(patch("timermute.process.mute_word_add.MuteWordUnmuteTimer"))
        mock_mute_word = self.enterContext(patch("timermute.process.mute_word_add.MuteWord"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.process.mute_word_add.MuteWordAdd.update_mute_word_table")
        )
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.config = MagicMock(spec=configparser.ConfigParser)
        main_winfow_info.mute_word_db = MagicMock(spec=MuteWordDB)
        instnace = MuteWordAdd(main_winfow_info)

        def pre_run(mute_word_str, interval_min, is_valid_muter):
            mock_popup_get_text.reset_mock()
            mock_popup_get_text.side_effect = lambda t: mute_word_str

            mock_muter.reset_mock()
            if not is_valid_muter:
                mock_muter.side_effect = ValueError
            mock_popup_get_interval.reset_mock()
            mock_popup_get_interval.side_effect = lambda: interval_min

            mock_mute_word_unmute_timer.reset_mock()
            mock_mute_word.reset_mock()
            mock_update_mute_word_table.reset_mock()

        def post_run(mute_word_str, interval_min, is_valid_muter):
            self.assertEqual([call("Mute word input.")], mock_popup_get_text.mock_calls)

            if not mute_word_str:
                mock_muter.assert_not_called()
                mock_popup_get_interval.assert_not_called()
                mock_mute_word_unmute_timer.assert_not_called()
                mock_mute_word.assert_not_called()
                mock_update_mute_word_table.assert_not_called()
                return

            if is_valid_muter:
                self.assertEqual(
                    [call(main_winfow_info.config), call().mute_keyword("mute_word_str")], mock_muter.mock_calls
                )
            else:
                self.assertEqual([call(main_winfow_info.config)], mock_muter.mock_calls)
                mock_popup_get_interval.assert_not_called()
                mock_mute_word_unmute_timer.assert_not_called()
                mock_mute_word.assert_not_called()
                self.assertEqual([call()], mock_update_mute_word_table.mock_calls)
                return

            unmuted_at = get_future_datetime(interval_min * 60) if interval_min else ""
            self.assertEqual([call()], mock_popup_get_interval.mock_calls)
            if interval_min:
                self.assertEqual(
                    [
                        call(main_winfow_info, mock_muter.return_value, interval_min * 60, "mute_word_str"),
                        call().start(),
                    ],
                    mock_mute_word_unmute_timer.mock_calls,
                )
            else:
                mock_mute_word_unmute_timer.assert_not_called()

            self.assertEqual(
                [
                    call(mute_word_str, "muted", fake_now_str, fake_now_str, unmuted_at),
                ],
                mock_mute_word.mock_calls,
            )
            self.assertEqual([call()], mock_update_mute_word_table.mock_calls)

        Params = namedtuple("Params", ["mute_word_str", "interval_min", "is_valid_muter", "result"])
        params_list = [
            Params("mute_word_str", 1, True, Result.SUCCESS),
            Params("mute_word_str", 0, True, Result.SUCCESS),
            Params("mute_word_str", 1, False, ValueError),
            Params("", 1, True, Result.FAILED),
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
