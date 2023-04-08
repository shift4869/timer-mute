# coding: utf-8
from logging import INFO, getLogger

import PySimpleGUI as sg

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.GuiFunction import popup_get_text, update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordAdd(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # try:
        #     self.window = mw.window
        #     self.values = mw.values
        #     self.mute_word = mw.mute_word
        #     self.mute_user = mw.mute_user
        # except AttributeError:
        #     logger.error("Create mylist done failed, argument error.")
        mute_word_str = popup_get_text("mute word input.")
        if not mute_word_str:
            return

        mw.mute_word_db.upsert(mute_word_str)

        # デフォルトでミュートする
        config = mw.config
        screen_name = config["twitter"]["screen_name"]
        muter = Muter(screen_name)
        response = muter.mute_keyword(mute_word_str)
        print(response)

        update_mute_word_table(mw.window, mw.mute_word_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
