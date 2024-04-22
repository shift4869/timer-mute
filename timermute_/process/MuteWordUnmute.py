from logging import INFO, getLogger

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.MainWindowInfo import MainWindowInfo
from timermute.ui.Util import update_mute_word_table

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordUnmute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_UNMUTE-"
        logger.info("MUTE_WORD_UNMUTE -> start")
        # 選択ミュート済ワードを取得
        logger.info("Getting selected muted word -> start")
        index_list = mw.values["-LIST_2-"]
        mute_word_list_all = mw.window["-LIST_2-"].get()
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
            config = mw.config
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
                mw.mute_word_db.unmute(mute_word_str)
                logger.info("DB update -> done")
            logger.info("Unmute by unmute_keyword -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_word_table(mw.window, mw.mute_word_db)
        logger.info("MUTE_WORD_UNMUTE -> done")
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
