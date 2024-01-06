import sys
import unittest
from collections import namedtuple

import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timermute.db.mute_word_db import MuteWordDB
from timermute.process.mute_word_del import MuteWordDel
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result


class TestMuteWordDel(unittest.TestCase):
    def test_run(self):
        self.enterContext(patch("timermute.process.mute_word_del.logger.info"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.process.mute_word_del.Base.update_mute_word_table")
        )
        main_winfow_info = MagicMock(spec=MainWindowInfo)
        main_winfow_info.values = MagicMock(spec=dict)
        main_winfow_info.window = MagicMock(spec=sg.Window)
        main_winfow_info.mute_word_db = MagicMock(spec=MuteWordDB)
        instnace = MuteWordDel(main_winfow_info)

        def pre_run(index_list, mute_word_list_all, is_valid_delete):
            main_winfow_info.values.reset_mock()
            main_winfow_info.values.__getitem__.side_effect = lambda key: index_list
            main_winfow_info.window.reset_mock()
            main_winfow_info.window.__getitem__.return_value.get.side_effect = lambda: mute_word_list_all
            main_winfow_info.mute_word_db.reset_mock()
            if not is_valid_delete:
                main_winfow_info.mute_word_db.delete.side_effect = ValueError
            mock_update_mute_word_table.reset_mock()

        def post_run(index_list, mute_word_list_all, is_valid_delete):
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
                mock_update_mute_word_table.assert_not_called()
                return

            mute_word_str = mute_word_list[0][1]
            self.assertEqual([call.delete(mute_word_str)], main_winfow_info.mute_word_db.mock_calls)
            self.assertEqual([call()], mock_update_mute_word_table.mock_calls)

        Params = namedtuple("Params", ["index_list", "mute_word_list_all", "is_valid_delete", "result"])
        params_list = [
            Params([0], [(0, "mute_word_0")], True, Result.SUCCESS),
            Params([], [(0, "mute_word_0")], True, Result.FAILED),
            Params([0], [(0, "mute_word_0")], False, ValueError),
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
