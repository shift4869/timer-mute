import threading
from logging import INFO, getLogger
from typing import Callable

from timermute.muter.muter import Muter
from timermute.ui.main_window_info import MainWindowInfo
from timermute.db.mute_user_db import MuteUserDB
from timermute.db.mute_word_db import MuteWordDB
import PySimpleGUI as sg

logger = getLogger(__name__)
logger.setLevel(INFO)


class TimerBase:
    _interval: float
    _func: Callable
    _args: dict
    _thread: threading.Thread

    def __init__(self, interval: float, func: Callable, args: dict) -> None:
        self._interval = interval
        self._func = func
        self._args = args
        self._thread = threading.Timer(self._interval, self._func, self._args)
        self._thread.setDaemon(True)

    def start(self) -> threading.Thread:
        logger.info(f"Unmute Timer set.")
        self._thread.start()
        return self._thread


class MuteWordUnmuteTimer(TimerBase):
    def __init__(self, mw: MainWindowInfo, muter: Muter, interval: float, target_keyword: str) -> None:
        self.muter = muter
        self.mw = mw
        self.keyword = target_keyword
        super().__init__(interval, self.run, ())

    def update_mute_word_table(self) -> None:
        """mute_word テーブルを更新する"""
        window: sg.Window = self.mw.window
        mute_word_db: MuteWordDB = self.mw.mute_word_db

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

    def run(self) -> None:
        logger.info("Timer run -> start")
        try:
            logger.info("Unmute keyword -> start")
            logger.info(f"Target keyword is '{self.keyword}'.")
            self.muter.unmute_keyword(self.keyword)
            logger.info("Unmute keyword -> done")
        except Exception as e:
            logger.warning(e)
            pass
        try:
            logger.info("DB update -> start")
            self.mw.mute_word_db.unmute(self.keyword)
            logger.info("DB update -> done")
        except Exception as e:
            logger.warning(e)
            pass
        self.update_mute_word_table()
        logger.info("Timer run -> done")


class MuteUserUnmuteTimer(TimerBase):
    def __init__(self, mw: MainWindowInfo, muter: Muter, interval: float, target_screen_name: str) -> None:
        self.muter = muter
        self.mw = mw
        self.screen_name = target_screen_name
        super().__init__(interval, self.run, ())

    def update_mute_user_table(self) -> None:
        """mute_user テーブルを更新する"""
        window: sg.Window = self.mw.window
        mute_user_db: MuteUserDB = self.mw.mute_user_db

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

    def run(self) -> None:
        logger.info("Timer run -> start")
        try:
            logger.info("Unmute user -> start")
            logger.info(f"Target user is '{self.screen_name}'.")
            self.muter.unmute_user(self.screen_name)
            logger.info("Unmute user -> done")
        except Exception as e:
            logger.warning(e)
            pass
        try:
            logger.info("DB update -> start")
            self.mw.mute_user_db.unmute(self.screen_name)
            logger.info("DB update -> done")
        except Exception as e:
            logger.warning(e)
            pass
        self.update_mute_user_table()
        logger.info("Timer run -> done")


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
