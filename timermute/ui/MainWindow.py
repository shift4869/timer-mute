# coding: utf-8
import configparser
import logging
import logging.config
import subprocess
from logging import INFO, getLogger
from pathlib import Path

import PySimpleGUI as sg

# 対象サイト
target = ["pixiv pic/manga", "pixiv novel", "nijie", "seiga", "skeb"]


class MainWindow():
    def __init__(self):
        pass

    def _make_layout(self):
        table_cols_name = ["No.", "     ミュートワード     ", "   更新日時   ", "   作成日時   "]
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
        table_style2 = {
            "values": def_data,
            "headings": table_cols_name,
            "max_col_width": 400,
            "def_col_width": cols_width,
            "num_rows": 18,
            "auto_size_columns": True,
            "bind_return_key": True,
            "justification": "right",
            "key": "-LIST_1-",
            "right_click_menu": table_right_click_menu,
        }
        t1 = sg.Table(**table_style1)
        t2 = sg.Table(**table_style2)

        table_cols_name2 = ["No.", "    ミュートアカウント    ", "   更新日時   ", "   作成日時   "]
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
            "key": "-LIST_1-",
            "right_click_menu": table_right_click_menu,
        }
        table_style4 = {
            "values": def_data2,
            "headings": table_cols_name2,
            "max_col_width": 400,
            "def_col_width": cols_width2,
            "num_rows": 18,
            "auto_size_columns": True,
            "bind_return_key": True,
            "justification": "right",
            "key": "-LIST_1-",
            "right_click_menu": table_right_click_menu,
        }
        t3 = sg.Table(**table_style3)
        t4 = sg.Table(**table_style4)

        button_list1 = [
            [sg.Button(" ADD ")],
            [sg.Button("DELETE")],
            [sg.Button("   ON ->")],
            [sg.Button("<- OFF  ")],
        ]
        button_list2 = [
            [sg.Button(" ADD ")],
            [sg.Button("DELETE")],
            [sg.Button("   ON ->")],
            [sg.Button("<- OFF  ")],
        ]

        layout = [
            [sg.Text("TimerMute")],
            [sg.Text("ミュートワード", size=(50, 1))],
            [t1, sg.Column(button_list1, vertical_alignment="top"), t2],
            [sg.Text("ミュートアカウント", size=(50, 1))],
            [t3, sg.Column(button_list2, vertical_alignment="top"), t4],
            [sg.Multiline(key="-OUTPUT-", size=(129, 5), auto_refresh=True, autoscroll=True, reroute_stdout=True, reroute_stderr=True)],
        ]
        return layout

    def run(self):
        # 対象URL例サンプル
        target_url_example = {
            "pixiv pic/manga": "https://www.pixiv.net/artworks/xxxxxxxx",
            "pixiv novel": "https://www.pixiv.net/novel/show.php?id=xxxxxxxx",
            "nijie": "http://nijie.info/view_popup.php?id=xxxxxx",
            "seiga": "https://seiga.nicovideo.jp/seiga/imxxxxxxx",
            "skeb": "https://skeb.jp/@xxxxxxxx/works/xx",
        }

        # configファイルロード
        CONFIG_FILE_NAME = "./config/config.ini"
        config = configparser.ConfigParser()
        if not config.read(CONFIG_FILE_NAME, encoding="utf8"):
            raise IOError

        save_base_path = Path(__file__).parent
        try:
            save_base_path = Path(config["save_base_path"]["save_base_path"])
        except Exception:
            save_base_path = Path(__file__).parent
        save_base_path.mkdir(parents=True, exist_ok=True)

        # ウィンドウのレイアウト
        layout = self._make_layout()

        # アイコン画像取得
        # ICON_PATH = "./image/icon.png"
        # icon_binary = None
        # with Path(ICON_PATH).open("rb") as fin:
        #     icon_binary = fin.read()

        # ウィンドウオブジェクトの作成
        window = sg.Window("TimerMute", layout, icon=None, size=(1020, 900), finalize=True)
        # window["-WORK_URL-"].bind("<FocusIn>", "+INPUT FOCUS+")

        logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
        for name in logging.root.manager.loggerDict:
            # 自分以外のすべてのライブラリのログ出力を抑制
            if "timermute" not in name:
                getLogger(name).disabled = True
        logger = getLogger(__name__)
        logger.setLevel(INFO)

        print("---ここにログが表示されます---")

        while True:
            event, values = window.read()
            if event in [sg.WIN_CLOSED, "-EXIT-"]:
                break
            if event == "-TARGET-":
                work_kind = values["-TARGET-"]
                window["-WORK_URL_SAMPLE-"].update(target_url_example[work_kind])
            if event == "-RUN-":
                work_url = values["-WORK_URL-"]
                try:
                    logger.info("Process -> start")
                    logger.info("Process -> done")
                except Exception:
                    logger.info("Process failed...")
                else:
                    logger.info("Process done: success!")
            if event == "-FOLDER_OPEN-":
                save_path = values["-SAVE_PATH-"]
                subprocess.Popen(["explorer", save_path], shell=True)

        # ウィンドウ終了処理
        window.close()
        return 0


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
