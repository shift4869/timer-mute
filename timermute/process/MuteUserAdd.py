# coding: utf-8
from logging import INFO, getLogger

import PySimpleGUI as sg

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.GuiFunction import popup_get_text, update_mute_user_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserAdd(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        mute_user_str = popup_get_text("mute user input.")
        if not mute_user_str:
            return

        # デフォルトでミュートする
        config = mw.config
        screen_name = config["twitter"]["screen_name"]
        muter = Muter(screen_name)
        response = muter.mute_user(mute_user_str)
        print(response)

        mw.mute_user_db.upsert(mute_user_str)

        update_mute_user_table(mw.window, mw.mute_user_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
