# coding: utf-8
from logging import INFO, getLogger

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.GuiFunction import update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordUnmute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_UNMUTE-"
        # 選択ミュート済ワードを取得
        index_list = mw.values["-LIST_2-"]
        mute_word_list_all = mw.window["-LIST_2-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            return

        try:
            # Muter インスタンスを作成し、選択ワードのミュートを解除する
            config = mw.config
            screen_name = config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            for mute_word in mute_word_list:
                # 選択ワードのミュートを解除
                mute_word_str = mute_word[1]
                response = muter.unmute_keyword(mute_word_str)
                print(response)

                # DB修正
                mw.mute_word_db.unmute(mute_word_str)
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
