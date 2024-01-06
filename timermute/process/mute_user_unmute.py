from logging import INFO, getLogger

from timermute.muter.muter import Muter
from timermute.process.base import Base
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserUnmute(Base):
    def __init__(self, main_winfow_info: MainWindowInfo) -> None:
        super().__init__(main_winfow_info)

    def run(self) -> Result:
        # "-MUTE_USER_UNMUTE-"
        logger.info("MUTE_USER_UNMUTE -> start")
        # 選択ミュート済ユーザーを取得
        logger.info("Getting selected muted user -> start")
        index_list = self.main_winfow_info.values["-LIST_4-"]
        mute_user_list_all = self.main_winfow_info.window["-LIST_4-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            logger.info("Selected muted user is empty.")
            logger.info("Getting selected mute user -> done")
            logger.info("MUTE_WORD_UNMUTE -> done")
            return Result.FAILED
        logger.info("Getting selected muted user -> start")

        try:
            # Muter インスタンスを作成し、選択ユーザーのミュートを解除する
            logger.info("Unmute by unmute_user -> start")
            config = self.main_winfow_info.config
            muter = Muter(config)
            for mute_user in mute_user_list:
                # 選択ユーザーのミュートを解除
                mute_user_str = mute_user[1]
                logger.info(f"Target user is '{mute_user_str}'.")
                r_dict = muter.unmute_user(mute_user_str)
                print(r_dict)
                logger.info(f"'{mute_user_str}' is unmuted.")

                # DB修正
                logger.info("DB update -> start")
                self.main_winfow_info.mute_user_db.unmute(mute_user_str)
                logger.info("DB update -> done")
            logger.info("Unmute by unmute_user -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            self.update_mute_user_table()
        logger.info("MUTE_USER_UNMUTE -> done")
        return Result.SUCCESS


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
