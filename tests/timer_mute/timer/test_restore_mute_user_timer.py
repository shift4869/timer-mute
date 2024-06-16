import configparser
import sys
import unittest
from collections import namedtuple
from datetime import datetime

import freezegun
from mock import MagicMock, call, patch

from timer_mute.db.model import MuteUser
from timer_mute.db.mute_user_db import MuteUserDB
from timer_mute.timer.restore import MuteUserRestoreTimer, RestoreTimerBase
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result


class TestMuteUserRestoreTimer(unittest.TestCase):
    def _get_user_tuple(self, index: int = 0) -> tuple[str]:
        return (
            f"test_user_{index}",
            "muted",
            f"2024-01-07 00:01:{index:02}",
            f"2024-01-07 00:02:{index:02}",
            f"2024-01-07 1{index}:02:00" if index != 0 else "",
        )

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

    def test_init(self):
        instance = MuteUserRestoreTimer()
        main_window_info = MagicMock(spec=MainWindowInfo)
        actual = RestoreTimerBase.set(main_window_info)
        self.assertEqual(Result.success, actual)

    def test_set(self):
        fake_now_str = "2024-01-07 12:34:56"
        self.enterContext(freezegun.freeze_time(fake_now_str))
        self.enterContext(patch("timer_mute.timer.restore.logger"))
        mock_muter = self.enterContext(patch("timer_mute.timer.restore.Muter"))
        mock_mute_user_unmute_timer = self.enterContext(patch("timer_mute.timer.restore.MuteUserUnmuteTimer"))
        mock_main_window_info = MagicMock(spec=MainWindowInfo)
        mock_main_window_info.config = MagicMock(spec=configparser.ConfigParser)
        mock_main_window_info.mute_user_db = MagicMock(spec=MuteUserDB)

        destination_format = "%Y-%m-%d %H:%M:%S"

        def pre_run(mute_user_all, is_valid_unmute_keyuser, is_valid_unmute):
            mock_muter.reset_mock()
            if not is_valid_unmute_keyuser:
                mock_muter.return_value.unmute_user.side_effect = ValueError
            mock_main_window_info.config.reset_mock()
            mock_main_window_info.mute_user_db.reset_mock()
            mock_main_window_info.mute_user_db.select.side_effect = lambda: mute_user_all
            if not is_valid_unmute:
                mock_main_window_info.mute_user_db.unmute.side_effect = ValueError
            mock_mute_user_unmute_timer.reset_mock()

        def post_run(mute_user_all, is_valid_unmute_keyuser, is_valid_unmute):
            expect_muter_calls = [call(mock_main_window_info.config)]
            expect_mute_user_db_calls = [call.select()]

            mute_user = mute_user_all[0]
            target_screen_name = mute_user.screen_name
            unmuted_at = mute_user.unmuted_at
            if not unmuted_at:
                self.assertEqual(expect_mute_user_db_calls, mock_main_window_info.mute_user_db.mock_calls)
                self.assertEqual(expect_muter_calls, mock_muter.mock_calls)
                mock_mute_user_unmute_timer.assert_not_called()
                return
            delta = datetime.strptime(unmuted_at, destination_format) - datetime.now()
            interval = float(delta.total_seconds())
            if interval < 1:
                expect_muter_calls.append(call().unmute_user(target_screen_name))
                expect_mute_user_db_calls.append(call.unmute(target_screen_name))
            else:
                self.assertEqual(
                    [
                        call(mock_main_window_info, mock_muter.return_value, interval, target_screen_name),
                        call().start(),
                    ],
                    mock_mute_user_unmute_timer.mock_calls,
                )
            self.assertEqual(expect_muter_calls, mock_muter.mock_calls)
            self.assertEqual(expect_mute_user_db_calls, mock_main_window_info.mute_user_db.mock_calls)

        Params = namedtuple("Params", ["mute_user_all", "is_valid_unmute_keyuser", "is_valid_unmute", "result"])
        params_list = [
            Params([self._get_mute_user(0)], True, True, Result.success),
            Params([self._get_mute_user(1)], True, True, Result.success),
            Params([self._get_mute_user(2)], True, True, Result.success),
            Params([self._get_mute_user(3)], True, True, Result.success),
            Params([self._get_mute_user(1)], True, False, Result.success),
            Params([self._get_mute_user(1)], False, True, Result.success),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            expect = params[-1]
            actual = MuteUserRestoreTimer.set(mock_main_window_info)
            self.assertEqual(expect, actual)
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
