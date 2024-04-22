import configparser
import sys
import unittest
from collections import namedtuple
from datetime import datetime

import freezegun
from mock import MagicMock, call, patch

from timermute.db.model import MuteWord
from timermute.db.mute_word_db import MuteWordDB
from timermute.timer.restore import MuteWordRestoreTimer, RestoreTimerBase
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result


class TestMuteWordRestoreTimer(unittest.TestCase):
    def _get_word_tuple(self, index: int = 0) -> tuple[str]:
        return (
            f"test_word_{index}",
            "muted",
            f"2024-01-07 00:01:{index:02}",
            f"2024-01-07 00:02:{index:02}",
            f"2024-01-07 1{index}:02:00" if index != 0 else "",
        )

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

    def test_init(self):
        instance = MuteWordRestoreTimer()
        main_window_info = MagicMock(spec=MainWindowInfo)
        actual = RestoreTimerBase.set(main_window_info)
        self.assertEqual(Result.SUCCESS, actual)

    def test_set(self):
        fake_now_str = "2024-01-07 12:34:56"
        self.enterContext(freezegun.freeze_time(fake_now_str))
        self.enterContext(patch("timermute.timer.restore.logger"))
        mock_muter = self.enterContext(patch("timermute.timer.restore.Muter"))
        mock_mute_word_unmute_timer = self.enterContext(patch("timermute.timer.restore.MuteWordUnmuteTimer"))
        mock_main_window_info = MagicMock(spec=MainWindowInfo)
        mock_main_window_info.config = MagicMock(spec=configparser.ConfigParser)
        mock_main_window_info.mute_word_db = MagicMock(spec=MuteWordDB)

        destination_format = "%Y-%m-%d %H:%M:%S"

        def pre_run(mute_word_all, is_valid_unmute_keyword, is_valid_unmute):
            mock_muter.reset_mock()
            if not is_valid_unmute_keyword:
                mock_muter.return_value.unmute_keyword.side_effect = ValueError
            mock_main_window_info.config.reset_mock()
            mock_main_window_info.mute_word_db.reset_mock()
            mock_main_window_info.mute_word_db.select.side_effect = lambda: mute_word_all
            if not is_valid_unmute:
                mock_main_window_info.mute_word_db.unmute.side_effect = ValueError
            mock_mute_word_unmute_timer.reset_mock()

        def post_run(mute_word_all, is_valid_unmute_keyword, is_valid_unmute):
            expect_muter_calls = [call(mock_main_window_info.config)]
            expect_mute_word_db_calls = [call.select()]

            mute_word = mute_word_all[0]
            target_keyword = mute_word.keyword
            unmuted_at = mute_word.unmuted_at
            if not unmuted_at:
                self.assertEqual(expect_mute_word_db_calls, mock_main_window_info.mute_word_db.mock_calls)
                self.assertEqual(expect_muter_calls, mock_muter.mock_calls)
                mock_mute_word_unmute_timer.assert_not_called()
                return
            delta = datetime.strptime(unmuted_at, destination_format) - datetime.now()
            interval = float(delta.total_seconds())
            if interval < 1:
                expect_muter_calls.append(call().unmute_keyword(target_keyword))
                expect_mute_word_db_calls.append(call.unmute(target_keyword))
            else:
                self.assertEqual(
                    [call(mock_main_window_info, mock_muter.return_value, interval, target_keyword), call().start()],
                    mock_mute_word_unmute_timer.mock_calls,
                )
            self.assertEqual(expect_muter_calls, mock_muter.mock_calls)
            self.assertEqual(expect_mute_word_db_calls, mock_main_window_info.mute_word_db.mock_calls)

        Params = namedtuple("Params", ["mute_word_all", "is_valid_unmute_keyword", "is_valid_unmute", "result"])
        params_list = [
            Params([self._get_mute_word(0)], True, True, Result.SUCCESS),
            Params([self._get_mute_word(1)], True, True, Result.SUCCESS),
            Params([self._get_mute_word(2)], True, True, Result.SUCCESS),
            Params([self._get_mute_word(3)], True, True, Result.SUCCESS),
            Params([self._get_mute_word(1)], True, False, Result.SUCCESS),
            Params([self._get_mute_word(1)], False, True, Result.SUCCESS),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            expect = params[-1]
            actual = MuteWordRestoreTimer.set(mock_main_window_info)
            self.assertEqual(expect, actual)
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
