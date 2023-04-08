# coding: utf-8
from logging import INFO, getLogger

import PySimpleGUI as sg

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.GuiFunction import update_mute_user_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserMute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        index_list = mw.values["-LIST_3-"]
        mute_user_list_all = mw.window["-LIST_3-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            return

        config = mw.config
        screen_name = config["twitter"]["screen_name"]
        muter = Muter(screen_name)
        for mute_user in mute_user_list:
            mute_user_str = mute_user[1]
            response = muter.mute_user(mute_user_str)
            print(response)
            mw.mute_user_db.mute(mute_user_str)

        update_mute_user_table(mw.window, mw.mute_user_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
