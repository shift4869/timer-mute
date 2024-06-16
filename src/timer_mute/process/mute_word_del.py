from logging import INFO, getLogger

from timer_mute.process.base import Base
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordDel(Base):
    def __init__(self, main_window_info: MainWindowInfo) -> None:
        super().__init__(main_window_info)

    def run(self) -> Result:
        # "-MUTE_WORD_DEL-"
        logger.info("MUTE_WORD_DEL -> start")
        # 選択ミュートワードを取得
        logger.info("Getting selected mute word -> start")
        index_list = self.main_window_info.values["-LIST_1-"]
        mute_word_list_all = self.main_window_info.window["-LIST_1-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            logger.info(f"Selected mute word is empty.")
            logger.info("Getting selected mute word -> done")
            logger.info("MUTE_WORD_DEL -> done")
            return Result.failed
        logger.info("Getting selected mute word -> done")

        try:
            # ミュートワードをDBから削除
            logger.info("DB delete -> start")
            for mute_word in mute_word_list:
                mute_word_str = mute_word[1]
                self.main_window_info.mute_word_db.delete(mute_word_str)
                logger.info(f"Deleted candidate mute word '{mute_word_str}'.")
            logger.info("DB delete -> done")
        except Exception as e:
            raise e
        finally:
            self.update_mute_word_table()
        logger.info("MUTE_WORD_DEL -> done")
        return Result.success


if __name__ == "__main__":
    from timer_mute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
