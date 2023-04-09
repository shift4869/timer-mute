# coding: utf-8
from logging import INFO, getLogger

import PySimpleGUI as sg

from timermute.db.Model import MuteWord
from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.timer.Timer import MuteWordUnmuteTimer
from timermute.ui.GuiFunction import get_future_datetime, now, popup_get_interval, update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordMute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_MUTE-"
        # 選択ミュートワードを取得
        index_list = mw.values["-LIST_1-"]
        mute_word_list_all = mw.window["-LIST_1-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            return

        try:
            # Muter インスタンスを作成し、選択ワードをミュートする
            config = mw.config
            screen_name = config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            for mute_word in mute_word_list:
                # 選択ワードをミュート
                mute_word_str = mute_word[1]
                response = muter.mute_keyword(mute_word_str)
                print(response)
                
                # 解除タイマー
                # interval をユーザーに問い合せる
                interval_min = popup_get_interval()  # min
                if interval_min:
                    # 解除タイマーセット
                    # interval = 10  # DEBUG
                    interval = interval_min * 60  # sec
                    timer = MuteWordUnmuteTimer(mw, muter, interval, mute_word_str)
                    timer.start()

                # DB追加
                unmuted_at = get_future_datetime(interval_min * 60)
                mw.mute_word_db.mute(mute_word_str, unmuted_at)
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_word_table(mw.window, mw.mute_word_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
