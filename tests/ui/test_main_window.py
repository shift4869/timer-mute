import sys
import unittest
from collections import namedtuple
from pathlib import Path

import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timermute.process import mute_user_add, mute_user_del, mute_user_mute, mute_user_unmute, mute_word_add
from timermute.process import mute_word_del, mute_word_mute, mute_word_unmute
from timermute.ui.main_window import MainWindow
from timermute.util import Result


class TestMainWindow(unittest.TestCase):
    def test_init(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_layout = self.enterContext(patch("timermute.ui.main_window.MainWindow._make_layout"))
        mock_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_main_window_info = self.enterContext(patch("timermute.ui.main_window.MainWindow._get_main_window_info"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_word_table")
        )
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_user_table")
        )

        ICON_PATH = "./image/icon.png"
        icon_binary = Path(ICON_PATH).read_bytes()

        def pre_run(is_valid_config, prepare_session, restore_timer):
            mock_mute_word_db.reset_mock()
            mock_mute_user_db.reset_mock()
            mock_config.reset_mock()
            if not is_valid_config:
                mock_config.return_value.read.side_effect = lambda filenames, encoding: False
            else:
                on_load_dict = {
                    "prepare_session": prepare_session,
                    "restore_timer": restore_timer,
                }

                def f(key):
                    return on_load_dict[key]

                mock_config.return_value.__getitem__.return_value.getboolean.side_effect = f
            mock_layout.reset_mock()
            mock_window.reset_mock()
            mock_main_window_info.reset_mock()
            mock_muter.reset_mock()
            mock_restore_timer.reset_mock()
            mock_update_mute_word_table.reset_mock()
            mock_update_mute_user_table.reset_mock()

        def post_run(is_valid_config, prepare_session, restore_timer, instance):
            mock_mute_word_db.assert_called_once_with()
            mock_mute_user_db.assert_called_once_with()
            if not is_valid_config:
                self.assertEqual(
                    [
                        call(),
                        call().read("./config/config.ini", encoding="utf8"),
                    ],
                    mock_config.mock_calls,
                )
                mock_layout.assert_not_called()
                mock_window.assert_not_called()
                mock_main_window_info.assert_not_called()
                mock_muter.assert_not_called()
                mock_restore_timer.assert_not_called()
                mock_update_mute_word_table.assert_not_called()
                mock_update_mute_user_table.assert_not_called()
                return

            self.assertEqual(
                [
                    call(),
                    call().read("./config/config.ini", encoding="utf8"),
                    call().read().__bool__(),
                    call().__getitem__("on_load"),
                    call().__getitem__().getboolean("prepare_session"),
                    call().__getitem__("on_load"),
                    call().__getitem__().getboolean("restore_timer"),
                ],
                mock_config.mock_calls,
            )
            mock_layout.assert_called_once_with()
            mock_window.assert_called_once_with(
                "TimerMute", mock_layout.return_value, icon=icon_binary, size=(1220, 900), finalize=True
            )
            if prepare_session:
                mock_muter.assert_called_once_with(mock_config.return_value)
            else:
                mock_muter.assert_not_called()
            if restore_timer:
                mock_main_window_info.assert_called_once_with()
                mock_restore_timer.set.assert_called_once_with(mock_main_window_info.return_value)
            else:
                mock_main_window_info.assert_not_called()
                mock_restore_timer.set.assert_not_called()
            mock_update_mute_word_table.assert_called_once_with()
            mock_update_mute_user_table.assert_called_once_with()

            self.assertEqual(mock_window.return_value, instance.window)
            self.assertEqual({}, instance.values)
            self.assertEqual(mock_mute_word_db.return_value, instance.mute_word_db)
            self.assertEqual(mock_mute_user_db.return_value, instance.mute_user_db)
            self.assertEqual(
                {
                    "-MUTE_WORD_ADD-": mute_word_add.MuteWordAdd,
                    "-MUTE_WORD_DEL-": mute_word_del.MuteWordDel,
                    "-MUTE_WORD_MUTE-": mute_word_mute.MuteWordMute,
                    "-MUTE_WORD_UNMUTE-": mute_word_unmute.MuteWordUnmute,
                    "-MUTE_USER_ADD-": mute_user_add.MuteUserAdd,
                    "-MUTE_USER_DEL-": mute_user_del.MuteUserDel,
                    "-MUTE_USER_MUTE-": mute_user_mute.MuteUserMute,
                    "-MUTE_USER_UNMUTE-": mute_user_unmute.MuteUserUnmute,
                },
                instance.process_dict,
            )

        Params = namedtuple(
            "Params",
            ["is_valid_config", "prepare_session", "restore_timer", "result"],
        )
        params_list = [
            Params(True, True, True, None),
            Params(True, True, False, None),
            Params(True, False, True, None),
            Params(False, True, True, IOError),
        ]
        for params in params_list:
            expect = params[-1]
            pre_run(*params[:-1])
            actual = None
            if expect is not None:
                with self.assertRaises(expect):
                    actual = MainWindow()
            else:
                actual = MainWindow()
            post_run(*params[:-1], actual)

    def test_make_layout(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_main_window_info = self.enterContext(patch("timermute.ui.main_window.MainWindow._get_main_window_info"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_word_table")
        )
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_user_table")
        )
        instance = MainWindow()

        actual = instance._make_layout()
        screen_name = instance.config["twitter"]["screen_name"]

        def expect_layout():
            table_cols_name = ["No.", "     ミュートワード     ", "     更新日時     ", "     作成日時     "]
            cols_width = [20, 100, 60, 60]
            def_data = [["", "", "", ""]]
            table_right_click_menu = [
                "-TABLE_RIGHT_CLICK_MENU-",
                [
                    "! ",
                    "---",
                ],
            ]
            table_style1 = {
                "values": def_data,
                "headings": table_cols_name,
                "max_col_width": 400,
                "def_col_width": cols_width,
                "num_rows": 18,
                "auto_size_columns": True,
                "bind_return_key": True,
                "justification": "left",
                "key": "-LIST_1-",
                "right_click_menu": table_right_click_menu,
            }
            table_cols_name = ["No.", "     ミュートワード     ", "     更新日時     ", "     解除日時     "]
            table_style2 = {
                "values": def_data,
                "headings": table_cols_name,
                "max_col_width": 400,
                "def_col_width": cols_width,
                "num_rows": 18,
                "auto_size_columns": True,
                "bind_return_key": True,
                "justification": "left",
                "key": "-LIST_2-",
                "right_click_menu": table_right_click_menu,
            }
            t1 = sg.Table(**table_style1)
            t2 = sg.Table(**table_style2)

            table_cols_name2 = ["No.", "    ミュートアカウント    ", "     更新日時     ", "     作成日時     "]
            cols_width2 = [20, 100, 60, 60]
            def_data2 = [["", "", "", ""]]
            table_right_click_menu = [
                "-TABLE_RIGHT_CLICK_MENU-",
                [
                    "! ",
                    "---",
                ],
            ]
            table_style3 = {
                "values": def_data2,
                "headings": table_cols_name2,
                "max_col_width": 400,
                "def_col_width": cols_width2,
                "num_rows": 18,
                "auto_size_columns": True,
                "bind_return_key": True,
                "justification": "left",
                "key": "-LIST_3-",
                "right_click_menu": table_right_click_menu,
            }
            table_cols_name2 = ["No.", "    ミュートアカウント    ", "     更新日時     ", "     解除日時     "]
            table_style4 = {
                "values": def_data2,
                "headings": table_cols_name2,
                "max_col_width": 400,
                "def_col_width": cols_width2,
                "num_rows": 18,
                "auto_size_columns": True,
                "bind_return_key": True,
                "justification": "left",
                "key": "-LIST_4-",
                "right_click_menu": table_right_click_menu,
            }
            t3 = sg.Table(**table_style3)
            t4 = sg.Table(**table_style4)

            button_list1 = [
                [sg.Button("ADD ->", key="-MUTE_WORD_ADD-")],
                [sg.Button("-> DELETE", key="-MUTE_WORD_DEL-")],
                [sg.Button("-> ON ->", key="-MUTE_WORD_MUTE-")],
                [sg.Button("<- OFF <-", key="-MUTE_WORD_UNMUTE-")],
            ]
            button_list2 = [
                [sg.Button("ADD ->", key="-MUTE_USER_ADD-")],
                [sg.Button("-> DELETE", key="-MUTE_USER_DEL-")],
                [sg.Button("-> ON ->", key="-MUTE_USER_MUTE-")],
                [sg.Button("<- OFF <-", key="-MUTE_USER_UNMUTE-")],
            ]

            layout = [
                [sg.Text("TimerMute")],
                [sg.Text("操作アカウント", size=(15, 1)), sg.Input(screen_name, size=(50, 1), readonly=True)],
                [sg.Text("ミュートワード", size=(50, 1))],
                [t1, sg.Column(button_list1, vertical_alignment="top"), t2],
                [sg.Text("ミュートアカウント", size=(50, 1))],
                [t3, sg.Column(button_list2, vertical_alignment="top"), t4],
                [sg.Text("ログ", size=(50, 1))],
                [
                    sg.Multiline(
                        key="-OUTPUT-",
                        size=(155, 8),
                        auto_refresh=True,
                        autoscroll=True,
                        reroute_stdout=True,
                        reroute_stderr=True,
                    )
                ],
            ]
            return layout

        expect = expect_layout()

        def check_layout(e, a):
            # typeチェック
            self.assertEqual(type(e), type(a))
            # イテラブルなら再起
            if hasattr(e, "__iter__") and hasattr(a, "__iter__"):
                self.assertEqual(len(e), len(a))
                for e1, a1 in zip(e, a):
                    check_layout(e1, a1)
            # Rows属性を持つなら再起
            if hasattr(e, "Rows") and hasattr(a, "Rows"):
                for e2, a2 in zip(e.Rows, a.Rows):
                    check_layout(e2, a2)
            # 要素チェック
            if hasattr(a, "RightClickMenu") and a.RightClickMenu:
                self.assertEqual(e.RightClickMenu, a.RightClickMenu)
            if hasattr(a, "ColumnHeadings") and a.ColumnHeadings:
                self.assertEqual(e.ColumnHeadings, a.ColumnHeadings)
            if hasattr(a, "ButtonText") and a.ButtonText:
                self.assertEqual(e.ButtonText, a.ButtonText)
            if hasattr(a, "DisplayText") and a.DisplayText:
                self.assertEqual(e.DisplayText, a.DisplayText)
            if hasattr(a, "Key") and a.Key:
                self.assertEqual(e.Key, a.Key)

        check_layout(expect, actual)

    def test_update_mute_word_table(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_layout = self.enterContext(patch("timermute.ui.main_window.MainWindow._make_layout"))
        mock_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_main_window_info = self.enterContext(patch("timermute.ui.main_window.MainWindow._get_main_window_info"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_user_table")
        )

        instance = MainWindow()
        instance.window = mock_window
        instance.mute_word_db = mock_mute_word_db
        instance.window.reset_mock()
        instance.mute_word_db.reset_mock()
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        instance.mute_word_db.select.side_effect = lambda: [r]

        actual = instance._update_mute_word_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.__getitem__("-LIST_1-"),
                call.__getitem__().update(values=[]),
                call.__getitem__("-LIST_2-"),
                call.__getitem__().update(values=["to_muted_table_list()"]),
            ],
            instance.window.mock_calls,
        )
        instance.mute_word_db.select.assert_called_once_with()

        instance.window.reset_mock()
        instance.mute_word_db.reset_mock()
        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        instance.mute_word_db.select.side_effect = lambda: [r]
        actual = instance._update_mute_word_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.__getitem__("-LIST_1-"),
                call.__getitem__().update(values=["to_unmuted_table_list()"]),
                call.__getitem__("-LIST_2-"),
                call.__getitem__().update(values=[]),
            ],
            instance.window.mock_calls,
        )
        instance.mute_word_db.select.assert_called_once_with()

    def test_update_mute_user_table(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_layout = self.enterContext(patch("timermute.ui.main_window.MainWindow._make_layout"))
        mock_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_main_window_info = self.enterContext(patch("timermute.ui.main_window.MainWindow._get_main_window_info"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_word_table")
        )

        instance = MainWindow()
        instance.window = mock_window
        instance.mute_user_db = mock_mute_user_db
        instance.window.reset_mock()
        instance.mute_user_db.reset_mock()
        r = MagicMock()
        r.status = "muted"
        r.to_muted_table_list = lambda: "to_muted_table_list()"
        instance.mute_user_db.select.side_effect = lambda: [r]

        actual = instance._update_mute_user_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.__getitem__("-LIST_3-"),
                call.__getitem__().update(values=[]),
                call.__getitem__("-LIST_4-"),
                call.__getitem__().update(values=["to_muted_table_list()"]),
            ],
            instance.window.mock_calls,
        )
        instance.mute_user_db.select.assert_called_once_with()

        instance.window.reset_mock()
        instance.mute_user_db.reset_mock()
        r = MagicMock()
        r.status = "unmuted"
        r.to_unmuted_table_list = lambda: "to_unmuted_table_list()"
        instance.mute_user_db.select.side_effect = lambda: [r]
        actual = instance._update_mute_user_table()
        self.assertEqual(Result.SUCCESS, actual)
        self.assertEqual(
            [
                call.__getitem__("-LIST_3-"),
                call.__getitem__().update(values=["to_unmuted_table_list()"]),
                call.__getitem__("-LIST_4-"),
                call.__getitem__().update(values=[]),
            ],
            instance.window.mock_calls,
        )
        instance.mute_user_db.select.assert_called_once_with()

    def test_get_main_window_info(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_layout = self.enterContext(patch("timermute.ui.main_window.MainWindow._make_layout"))
        mock_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_word_table")
        )
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_user_table")
        )
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MainWindowInfo"))
        instance = MainWindow()
        actual = instance._get_main_window_info()
        mock_mute_word_db.assert_called_with(
            instance.window,
            instance.values,
            instance.mute_word_db,
            instance.mute_user_db,
            instance.config,
        )

    def test_run(self):
        mock_mute_word_db = self.enterContext(patch("timermute.ui.main_window.MuteWordDB"))
        mock_mute_user_db = self.enterContext(patch("timermute.ui.main_window.MuteUserDB"))
        mock_config = self.enterContext(patch("timermute.ui.main_window.configparser.ConfigParser"))
        mock_layout = self.enterContext(patch("timermute.ui.main_window.MainWindow._make_layout"))
        mock_sg_window = self.enterContext(patch("timermute.ui.main_window.sg.Window"))
        mock_main_window_info = self.enterContext(patch("timermute.ui.main_window.MainWindow._get_main_window_info"))
        mock_muter = self.enterContext(patch("timermute.ui.main_window.Muter"))
        mock_restore_timer = self.enterContext(patch("timermute.ui.main_window.MuteUserRestoreTimer"))
        mock_update_mute_word_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_word_table")
        )
        mock_update_mute_user_table = self.enterContext(
            patch("timermute.ui.main_window.MainWindow._update_mute_user_table")
        )
        mock_logging = self.enterContext(patch("timermute.ui.main_window.logging.config.fileConfig"))
        mock_getLogger = self.enterContext(patch("timermute.ui.main_window.getLogger"))
        mock_print = self.enterContext(patch("timermute.ui.main_window.print"))
        mock_window = MagicMock()
        mock_process_dict = MagicMock()
        mock_process_base = MagicMock()

        def pre_run(instance, window_read, is_valid_process_dict, is_occur_error):
            mock_window.reset_mock()
            mock_window.read.side_effect = window_read
            instance.window = mock_window

            mock_process_dict.reset_mock()
            mock_process_base.reset_mock()
            if is_valid_process_dict:
                mock_process_dict.get.side_effect = lambda key: {"-DO_PROCESS-": mock_process_base}.get(key)
            else:
                if is_occur_error:
                    mock_process_dict.get.side_effect = lambda key: {"-DO_PROCESS-": "invalid_process"}.get(key)
                else:
                    mock_process_base.side_effect = lambda info: None
                    mock_process_dict.get.side_effect = lambda key: {"-DO_PROCESS-": mock_process_base}.get(key)
            instance.process_dict = mock_process_dict

            mock_main_window_info.reset_mock()

        def post_run(window_read, is_valid_process_dict, is_occur_error):
            expect_window_call = [call.read() for _ in range(len(window_read))]
            expect_window_call.append(call.close())
            self.assertEqual(expect_window_call, mock_window.mock_calls)

            is_do_process = any([event == "-DO_PROCESS-" for event, _ in window_read])
            if not is_do_process:
                mock_process_dict.assert_not_called()
                mock_process_base.assert_not_called()
                mock_main_window_info.assert_not_called()
                return

            self.assertEqual([call.get("-DO_PROCESS-"), call.get("-DO_PROCESS-")], mock_process_dict.mock_calls)
            if is_valid_process_dict:
                self.assertEqual(
                    [call.__bool__(), call(mock_main_window_info.return_value), call().run()],
                    mock_process_base.mock_calls,
                )
            else:
                if is_occur_error:
                    mock_process_base.assert_not_called()
                else:
                    self.assertEqual(
                        [call.__bool__(), call(mock_main_window_info.return_value)],
                        mock_process_base.mock_calls,
                    )
            self.assertEqual([call()], mock_main_window_info.mock_calls)

        Params = namedtuple("Params", ["window_read", "is_valid_process_dict", "is_occur_error", "result"])
        params_list = [
            Params([("-EXIT-", {})], True, False, Result.SUCCESS),
            Params([("-NOT_PROCESS-", {}), ("-EXIT-", {})], True, False, Result.SUCCESS),
            Params([("-DO_PROCESS-", {}), ("-EXIT-", {})], True, False, Result.SUCCESS),
            Params([("-DO_PROCESS-", {}), ("-EXIT-", {})], False, False, Result.SUCCESS),
            Params([("-DO_PROCESS-", {}), ("-EXIT-", {})], False, True, Result.SUCCESS),
        ]
        for params in params_list:
            instance = MainWindow()
            pre_run(instance, *params[:-1])
            actual = instance.run()
            expect = params[-1]
            self.assertEqual(expect, actual)
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
