# coding: utf-8
import threading
from typing import Callable

from timermute.muter.Muter import Muter
from timermute.ui.GuiFunction import update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo


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

    def start(self):
        self._thread.start()


class MuteWordUnmuteTimer(TimerBase):
    def __init__(self, mw: MainWindowInfo, muter: Muter, interval: float, target_keyword: str):
        self.muter = muter
        self.mw = mw
        self.keyword = target_keyword
        super().__init__(interval, self.run, ())
        pass

    def run(self):
        self.muter.unmute_keyword(self.keyword)
        self.mw.mute_word_db.unmute(self.keyword)
        update_mute_word_table(self.mw.window, self.mw.mute_word_db)
        return


class MuteUserUnmuteTimer(TimerBase):
    def __init__(self, interval: float, screen_name: str, target_screen_name: str):
        self.muter = Muter(screen_name)
        super().__init__(interval, self.muter.unmute_user, (target_screen_name, ))
        pass


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
