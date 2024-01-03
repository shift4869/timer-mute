from logging import INFO, getLogger

from timermute.process.base import Base
from timermute.ui.main_window_info import MainWindowInfo
from timermute.ui.util import update_mute_word_table

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordDel(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_DEL-"
        logger.info("MUTE_WORD_DEL -> start")
        # 選択ミュートワードを取得
        logger.info("Getting selected mute word -> start")
        index_list = mw.values["-LIST_1-"]
        mute_word_list_all = mw.window["-LIST_1-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            logger.info(f"Selected mute word is empty.")
            logger.info("Getting selected mute word -> done")
            logger.info("MUTE_WORD_DEL -> done")
            return
        logger.info("Getting selected mute word -> done")

        try:
            # ミュートワードをDBから削除
            logger.info("DB delete -> start")
            for mute_word in mute_word_list:
                mute_word_str = mute_word[1]
                mw.mute_word_db.delete(mute_word_str)
                logger.info(f"Deleted candidate mute word '{mute_word_str}'.")
            logger.info("DB delete -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_word_table(mw.window, mw.mute_word_db)
        logger.info("MUTE_WORD_DEL -> done")
        return


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
