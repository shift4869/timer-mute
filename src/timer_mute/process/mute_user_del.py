from logging import INFO, getLogger

from timer_mute.process.base import Base
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserDel(Base):
    def __init__(self, main_window_info: MainWindowInfo) -> None:
        super().__init__(main_window_info)

    def run(self) -> Result:
        # "-MUTE_USER_DEL-"
        logger.info("MUTE_USER_DEL -> start")
        # 選択ミュートユーザーを取得
        logger.info("Getting selected mute user -> start")
        index_list = self.main_window_info.values["-LIST_3-"]
        mute_user_list_all = self.main_window_info.window["-LIST_3-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            logger.info(f"Selected mute user is empty.")
            logger.info("Getting selected mute user -> done")
            logger.info("MUTE_USER_DEL -> done")
            return Result.FAILED
        logger.info("Getting selected mute user -> done")

        try:
            # ミュートユーザーをDBから削除
            logger.info("DB delete -> start")
            for mute_user in mute_user_list:
                mute_user_str = mute_user[1]
                self.main_window_info.mute_user_db.delete(mute_user_str)
                logger.info(f"Deleted candidate mute user '{mute_user_str}'.")
            logger.info("DB delete -> done")
        except Exception as e:
            raise e
        finally:
            self.update_mute_user_table()
        logger.info("MUTE_WORD_DEL -> done")
        return Result.SUCCESS


if __name__ == "__main__":
    from timer_mute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
