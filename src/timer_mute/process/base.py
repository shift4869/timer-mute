from abc import ABCMeta, abstractmethod

import PySimpleGUI as sg

from timer_mute.db.mute_user_db import MuteUserDB
from timer_mute.db.mute_word_db import MuteWordDB
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result


class Base(metaclass=ABCMeta):
    main_window_info: MainWindowInfo

    def __init__(self, main_window_info: MainWindowInfo) -> None:
        if not isinstance(main_window_info, MainWindowInfo):
            raise ValueError("main_window_info must be MainWindowInfo.")
        self.main_window_info = main_window_info

    def update_mute_word_table(self) -> Result:
        """mute_word テーブルを更新する"""
        window: sg.Window = self.main_window_info.window
        mute_word_db: MuteWordDB = self.main_window_info.mute_word_db

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

    def update_mute_user_table(self) -> Result:
        """mute_user テーブルを更新する"""
        window: sg.Window = self.main_window_info.window
        mute_user_db: MuteUserDB = self.main_window_info.mute_user_db

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

    @abstractmethod
    def run(self) -> Result:
        raise NotImplementedError


if __name__ == "__main__":
    pass
