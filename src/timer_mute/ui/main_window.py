import configparser
import logging
import logging.config
from logging import INFO, getLogger
from pathlib import Path

import orjson
import PySimpleGUI as sg

from timer_mute.db.mute_user_db import MuteUserDB
from timer_mute.db.mute_word_db import MuteWordDB
from timer_mute.muter.muter import Muter
from timer_mute.process import mute_user_add, mute_user_del, mute_user_mute, mute_user_unmute, mute_word_add
from timer_mute.process import mute_word_del, mute_word_mute, mute_word_unmute
from timer_mute.process.base import Base as ProcessBase
from timer_mute.timer.restore import MuteUserRestoreTimer
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result


class MainWindow:
    window: sg.Window = None
    values: dict = {}
    mute_word_db: MuteWordDB = None
    mute_user_db: MuteUserDB = None
    process_dict: dict = {}
    config: dict = {}

    CONFIG_FILE_NAME = "./config/config.json"

    def __init__(self) -> None:
        self.mute_word_db = MuteWordDB()
        self.mute_user_db = MuteUserDB()

        # イベントと処理の辞書
        self.process_dict = {
            "-MUTE_WORD_ADD-": mute_word_add.MuteWordAdd,
            "-MUTE_WORD_DEL-": mute_word_del.MuteWordDel,
            "-MUTE_WORD_MUTE-": mute_word_mute.MuteWordMute,
            "-MUTE_WORD_UNMUTE-": mute_word_unmute.MuteWordUnmute,
            "-MUTE_USER_ADD-": mute_user_add.MuteUserAdd,
            "-MUTE_USER_DEL-": mute_user_del.MuteUserDel,
            "-MUTE_USER_MUTE-": mute_user_mute.MuteUserMute,
            "-MUTE_USER_UNMUTE-": mute_user_unmute.MuteUserUnmute,
        }

        # configファイルロード
        self.config = orjson.loads(Path(self.CONFIG_FILE_NAME).read_bytes())

        # ウィンドウのレイアウト
        layout = self._make_layout()

        # アイコン画像取得
        ICON_PATH = "./image/icon.png"
        icon_binary = Path(ICON_PATH).read_bytes()

        # ウィンドウオブジェクトの作成
        self.window = sg.Window("TimerMute", layout, icon=icon_binary, size=(1220, 900), finalize=True)
        # window["-WORK_URL-"].bind("<FocusIn>", "+INPUT FOCUS+")

        # ロード時にセッションを取得する設定の場合、取得する
        if self.config["on_load"]["prepare_session"]:
            # シングルトンのため、ここでインスタンス生成しておけば以降はそのインスタンスを使い回せる
            muter = Muter(self.config)

        # ロード時にタイマーを復元する設定の場合は復元する
        if self.config["on_load"]["restore_timer"]:
            main_window_info = self._get_main_window_info()
            MuteUserRestoreTimer.set(main_window_info)

        # UI表示更新
        self._update_mute_word_table()
        self._update_mute_user_table()

    def _make_layout(self) -> list[list]:
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

        screen_name = self.config["twitter_api_client"]["screen_name"]
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

    def _update_mute_word_table(self) -> Result:
        """mute_word テーブルを更新する"""
        window: sg.Window = self.window
        mute_word_db: MuteWordDB = self.mute_word_db

        # ミュートワード取得
        # 更新日時で降順ソートする
        mute_word_list = mute_word_db.select()
        mute_word_list_1 = [r for r in mute_word_list if r.status == "unmuted"]
        mute_word_list_1.sort(key=lambda r: r.updated_at)
        mute_word_list_1.reverse()
        mute_word_list_2 = [r for r in mute_word_list if r.status == "muted"]
        mute_word_list_2.sort(key=lambda r: r.updated_at)
        mute_word_list_2.reverse()

        table_data = [r.to_unmuted_table_list() for r in mute_word_list_1]
        window["-LIST_1-"].update(values=table_data)
        table_data = [r.to_muted_table_list() for r in mute_word_list_2]
        window["-LIST_2-"].update(values=table_data)
        return Result.success

    def _update_mute_user_table(self) -> Result:
        """mute_user テーブルを更新する"""
        window: sg.Window = self.window
        mute_user_db: MuteUserDB = self.mute_user_db

        # ミュートユーザー取得
        # 更新日時で降順ソートする
        mute_user_list = mute_user_db.select()
        mute_user_list_1 = [r for r in mute_user_list if r.status == "unmuted"]
        mute_user_list_1.sort(key=lambda r: r.updated_at)
        mute_user_list_1.reverse()
        mute_user_list_2 = [r for r in mute_user_list if r.status == "muted"]
        mute_user_list_2.sort(key=lambda r: r.updated_at)
        mute_user_list_2.reverse()

        table_data = [r.to_unmuted_table_list() for r in mute_user_list_1]
        window["-LIST_3-"].update(values=table_data)
        table_data = [r.to_muted_table_list() for r in mute_user_list_2]
        window["-LIST_4-"].update(values=table_data)
        return Result.success

    def _get_main_window_info(self) -> MainWindowInfo:
        main_window_info = MainWindowInfo(
            self.window,
            self.values,
            self.mute_word_db,
            self.mute_user_db,
            self.config,
        )
        return main_window_info

    def run(self) -> Result:
        logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
        # for name in logging.root.manager.loggerDict:
        #     # 自分以外のすべてのライブラリのログ出力を抑制
        #     if "timer_mute" not in name:
        #         getLogger(name).disabled = True
        logger = getLogger(__name__)
        logger.setLevel(INFO)

        print("---ここにログが表示されます---")

        while True:
            event, values = self.window.read()
            if event in [sg.WIN_CLOSED, "-EXIT-"]:
                break

            if self.process_dict.get(event):
                self.values = values

                try:
                    main_window_info = self._get_main_window_info()
                    pb: ProcessBase = self.process_dict.get(event)(main_window_info)

                    if pb is None or not hasattr(pb, "run"):
                        continue

                    pb.run()
                except Exception as e:
                    logger.error(e)
                    logger.error("main event loop error.")

        # ウィンドウ終了処理
        self.window.close()
        return Result.success


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
