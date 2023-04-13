# coding: utf-8
import configparser
import logging
import logging.config
import subprocess
from logging import INFO, getLogger
from pathlib import Path

import PySimpleGUI as sg

from timermute.db.MuteUserDB import MuteUserDB
from timermute.db.MuteWordDB import MuteWordDB
from timermute.muter.Muter import Muter
from timermute.process import MuteUserAdd, MuteUserDel, MuteUserMute, MuteUserUnmute, MuteWordAdd, MuteWordDel, MuteWordMute, MuteWordUnmute
from timermute.process.Base import Base as ProcessBase
from timermute.ui.GuiFunction import update_mute_user_table, update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo
from timermute.timer.Restore import MuteUserRestoreTimer


class MainWindow():
    window: sg.Window = None
    values: list = []
    mute_word_db: MuteWordDB
    mute_user_db: MuteUserDB
    config: configparser.ConfigParser

    def __init__(self):
        self.mute_word_db = MuteWordDB()
        self.mute_user_db = MuteUserDB()

        # イベントと処理の辞書
        self.process_dict = {
            "-MUTE_WORD_ADD-": MuteWordAdd.MuteWordAdd,
            "-MUTE_WORD_DEL-": MuteWordDel.MuteWordDel,
            "-MUTE_WORD_MUTE-": MuteWordMute.MuteWordMute,
            "-MUTE_WORD_UNMUTE-": MuteWordUnmute.MuteWordUnmute,
            "-MUTE_USER_ADD-": MuteUserAdd.MuteUserAdd,
            "-MUTE_USER_DEL-": MuteUserDel.MuteUserDel,
            "-MUTE_USER_MUTE-": MuteUserMute.MuteUserMute,
            "-MUTE_USER_UNMUTE-": MuteUserUnmute.MuteUserUnmute,
        }

        # configファイルロード
        CONFIG_FILE_NAME = "./config/config.ini"
        self.config = configparser.ConfigParser()
        if not self.config.read(CONFIG_FILE_NAME, encoding="utf8"):
            raise IOError

        # ウィンドウのレイアウト
        layout = self._make_layout()

        # アイコン画像取得
        ICON_PATH = "./image/icon.png"
        icon_binary = None
        with Path(ICON_PATH).open("rb") as fin:
            icon_binary = fin.read()

        # ウィンドウオブジェクトの作成
        self.window = sg.Window("TimerMute", layout, icon=icon_binary, size=(1220, 900), finalize=True)
        # window["-WORK_URL-"].bind("<FocusIn>", "+INPUT FOCUS+")

        # ロード時にセッションを取得する設定の場合、取得する
        if self.config["on_load"].getboolean("prepare_session"):
            # シングルトンのため、ここでインスタンス生成しておけば以降はそのインスタンスを使い回せる
            screen_name = self.config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            # muter.twitter_session.prepare()

        # ロード時にタイマーを復元する設定の場合は復元する
        if self.config["on_load"].getboolean("restore_timer"):
            main_window_info = self.get_main_window_info()
            # restore_mute_word_timer(main_window_info)
            MuteUserRestoreTimer.set(main_window_info)
            pass

        # UI表示更新
        update_mute_word_table(self.window, self.mute_word_db)
        update_mute_user_table(self.window, self.mute_user_db)

    def get_main_window_info(self) -> MainWindowInfo:
        main_window_info = MainWindowInfo(
            self.window,
            self.values,
            self.mute_word_db,
            self.mute_user_db,
            self.config,
        )
        return main_window_info

    def _make_layout(self):
        table_cols_name = ["No.", "     ミュートワード     ", "     更新日時     ", "     作成日時     "]
        cols_width = [20, 100, 60, 60]
        def_data = [["", "", "", ""]]
        table_right_click_menu = [
            "-TABLE_RIGHT_CLICK_MENU-", [
                "! ",
                "---",
            ]
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
            "-TABLE_RIGHT_CLICK_MENU-", [
                "! ",
                "---",
            ]
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

        screen_name = self.config["twitter"]["screen_name"]
        layout = [
            [sg.Text("TimerMute")],
            [sg.Text("操作アカウント", size=(15, 1)), sg.Input(screen_name, size=(50, 1), readonly=True)],
            [sg.Text("ミュートワード", size=(50, 1))],
            [t1, sg.Column(button_list1, vertical_alignment="top"), t2],
            [sg.Text("ミュートアカウント", size=(50, 1))],
            [t3, sg.Column(button_list2, vertical_alignment="top"), t4],
            [sg.Text("ログ", size=(50, 1))],
            [sg.Multiline(key="-OUTPUT-", size=(155, 8), auto_refresh=True, autoscroll=True, reroute_stdout=True, reroute_stderr=True)],
        ]
        return layout

    def run(self):
        logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
        # for name in logging.root.manager.loggerDict:
        #     # 自分以外のすべてのライブラリのログ出力を抑制
        #     if "timermute" not in name:
        #         getLogger(name).disabled = True
        logger = getLogger(__name__)
        logger.setLevel(INFO)

        print("---ここにログが表示されます---")

        while True:
            event, values = self.window.read()
            # print(f"event={event} values={values}")
            if event in [sg.WIN_CLOSED, "-EXIT-"]:
                break

            if self.process_dict.get(event):
                self.values = values

                try:
                    pb: ProcessBase = self.process_dict.get(event)()

                    if pb is None or not hasattr(pb, "run"):
                        continue

                    main_window_info = self.get_main_window_info()
                    pb.run(main_window_info)
                except Exception as e:
                    logger.error(e)
                    logger.error("main event loop error.")

        # ウィンドウ終了処理
        self.window.close()
        return 0


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
