import configparser
import sys
import unittest
from collections import namedtuple

import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timermute.db.mute_user_db import MuteUserDB
from timermute.process.mute_user_unmute import MuteUserUnmute
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result


class TestMuteUserUnmute(unittest.TestCase):
    def test_run(self):
        self.enterContext(patch("timermute.process.mute_user_unmute.print"))
        self.enterContext(patch("timermute.process.mute_user_unmute.logger.info"))
        mock_muter = self.enterContext(patch("timermute.process.mute_user_unmute.Muter"))
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.process.mute_user_unmute.Base.update_mute_user_table")
        )
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.values = MagicMock(spec=dict)
        main_winfow_info.window = MagicMock(spec=sg.Window)
        main_winfow_info.mute_user_db = MagicMock(spec=MuteUserDB)
        main_winfow_info.config = MagicMock(spec=configparser.ConfigParser)
        instnace = MuteUserUnmute(main_winfow_info)

        def pre_run(index_list, mute_user_list_all, is_valid_muter):
            main_winfow_info.values.reset_mock()
            main_winfow_info.values.__getitem__.side_effect = lambda key: index_list
            main_winfow_info.window.reset_mock()
            main_winfow_info.window.__getitem__.return_value.get.side_effect = lambda: mute_user_list_all
            main_winfow_info.mute_user_db.reset_mock()
            main_winfow_info.config.reset_mock()
            mock_muter.reset_mock()
            if not is_valid_muter:
                mock_muter.side_effect = ValueError
            mock_update_mute_user_table.reset_mock()

        def post_run(index_list, mute_user_list_all, is_valid_muter):
            self.assertEqual([call.__getitem__("-LIST_4-")], main_winfow_info.values.mock_calls)
            self.assertEqual(
                [call.__getitem__("-LIST_4-"), call.__getitem__().get()], main_winfow_info.window.mock_calls
            )

            mute_user_list = []
            for i, mute_user in enumerate(mute_user_list_all):
                if i in index_list:
                    mute_user_list.append(mute_user)
            if not mute_user_list:
                main_winfow_info.mute_user_db.assert_not_called()
                main_winfow_info.config.assert_not_called()
                mock_muter.assert_not_called()
                mock_update_mute_user_table.assert_not_called()
                return

            mute_user_str = mute_user_list[0][1]
            if is_valid_muter:
                self.assertEqual(
                    [call(main_winfow_info.config), call().unmute_user(mute_user_str)], mock_muter.mock_calls
                )
            else:
                self.assertEqual([call(main_winfow_info.config)], mock_muter.mock_calls)
                main_winfow_info.mute_user_db.assert_not_called()
                self.assertEqual([call()], mock_update_mute_user_table.mock_calls)
                return

            self.assertEqual([call()], mock_update_mute_user_table.mock_calls)

        Params = namedtuple("Params", ["index_list", "mute_user_list_all", "is_valid_muter", "result"])
        params_list = [
            Params([0], [(0, "mute_user_0")], True, Result.SUCCESS),
            Params([], [(0, "mute_user_0")], True, Result.FAILED),
            Params([0], [(0, "mute_user_0")], False, ValueError),
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
