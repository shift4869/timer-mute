# coding: utf-8
import threading
from logging import INFO, getLogger
from typing import Callable

from timermute.muter.Muter import Muter
from timermute.ui.GuiFunction import update_mute_user_table, update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class TimerBase():
    _interval: float
    _func: Callable
    _args: dict
    _thread: threading.Thread

    def __init__(self, interval: float, func: Callable, args: dict):
        self._interval = interval
        self._func = func
        self._args = args
        self._thread = threading.Timer(
            self._interval,
            self._func,
            self._args
        )
        self._thread.setDaemon(True)
        pass

    def start(self) -> threading.Thread:
        logger.info(f"Unmute Timer set.")
        self._thread.start()
        return self._thread


class MuteWordUnmuteTimer(TimerBase):
    def __init__(self, mw: MainWindowInfo, muter: Muter, interval: float, target_keyword: str):
        self.muter = muter
        self.mw = mw
        self.keyword = target_keyword
        super().__init__(interval, self.run, ())
        pass

    def run(self):
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
        update_mute_word_table(self.mw.window, self.mw.mute_word_db)
        logger.info("Timer run -> done")
        return


class MuteUserUnmuteTimer(TimerBase):
    def __init__(self, mw: MainWindowInfo, muter: Muter, interval: float, target_screen_name: str):
        self.muter = muter
        self.mw = mw
        self.screen_name = target_screen_name
        super().__init__(interval, self.run, ())
        pass

    def run(self):
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
        update_mute_user_table(self.mw.window, self.mw.mute_user_db)
        logger.info("Timer run -> done")
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
