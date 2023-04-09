# coding: utf-8
from logging import INFO, getLogger

from timermute.process.Base import Base
from timermute.ui.GuiFunction import update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordDel(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_DEL-"
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
            # ミュートワードをDBから削除
            for mute_word in mute_word_list:
                mute_word_str = mute_word[1]
                mw.mute_word_db.delete(mute_word_str)
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
