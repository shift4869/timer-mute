from logging import INFO, getLogger

from timermute.muter.muter import Muter
from timermute.process.base import Base
from timermute.ui.main_window_info import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordUnmute(Base):
    def __init__(self, main_winfow_info: MainWindowInfo) -> None:
        super().__init__(main_winfow_info)

    def run(self) -> None:
        # "-MUTE_WORD_UNMUTE-"
        logger.info("MUTE_WORD_UNMUTE -> start")
        # 選択ミュート済ワードを取得
        logger.info("Getting selected muted word -> start")
        index_list = self.main_winfow_info.values["-LIST_2-"]
        mute_word_list_all = self.main_winfow_info.window["-LIST_2-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            logger.info("Selected muted word is empty.")
            logger.info("Getting selected mute word -> done")
            logger.info("MUTE_WORD_UNMUTE -> done")
            return
        logger.info("Getting selected muted word -> done")

        try:
            # Muter インスタンスを作成し、選択ワードのミュートを解除する
            logger.info("Unmute by unmute_keyword -> start")
            config = self.main_winfow_info.config
            muter = Muter(config)
            for mute_word in mute_word_list:
                # 選択ワードのミュートを解除
                mute_word_str = mute_word[1]
                logger.info(f"Target keyword is '{mute_word_str}'.")
                r_dict = muter.unmute_keyword(mute_word_str)
                print(r_dict)
                logger.info(f"'{mute_word_str}' is unmuted.")

                # DB修正
                logger.info("DB update -> start")
                self.main_winfow_info.mute_word_db.unmute(mute_word_str)
                logger.info("DB update -> done")
            logger.info("Unmute by unmute_keyword -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            self.update_mute_word_table()
        logger.info("MUTE_WORD_UNMUTE -> done")
        return


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
