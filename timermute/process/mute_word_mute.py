from logging import INFO, getLogger

from timermute.muter.muter import Muter
from timermute.process.base import Base
from timermute.timer.timer import MuteWordUnmuteTimer
from timermute.ui.main_window_info import MainWindowInfo
from timermute.util import Result, get_future_datetime, popup_get_interval

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordMute(Base):
    def __init__(self, main_winfow_info: MainWindowInfo) -> None:
        super().__init__(main_winfow_info)

    def run(self) -> Result:
        # "-MUTE_WORD_MUTE-"
        logger.info("MUTE_WORD_MUTE -> start")
        # 選択ミュートワードを取得
        logger.info("Getting selected mute word -> start")
        index_list = self.main_winfow_info.values["-LIST_1-"]
        mute_word_list_all = self.main_winfow_info.window["-LIST_1-"].get()
        mute_word_list = []
        for i, mute_word in enumerate(mute_word_list_all):
            if i in index_list:
                mute_word_list.append(mute_word)
        if not mute_word_list:
            logger.info("Selected mute word is empty.")
            logger.info("Getting selected mute word -> done")
            logger.info("MUTE_WORD_MUTE -> done")
            return Result.FAILED
        logger.info("Getting selected mute word -> start")

        try:
            # Muter インスタンスを作成し、選択ワードをミュートする
            logger.info("Mute by mute_keyword -> start")
            config = self.main_winfow_info.config
            muter = Muter(config)
            for mute_word in mute_word_list:
                # 選択ワードをミュート
                mute_word_str = mute_word[1]
                logger.info(f"Target keyword is '{mute_word_str}'.")
                r_dict = muter.mute_keyword(mute_word_str)
                print(r_dict)
                logger.info(f"'{mute_word_str}' is muted.")

                # 解除タイマー
                # interval をユーザーに問い合せる
                interval_min = popup_get_interval()  # min
                unmuted_at = get_future_datetime(interval_min * 60) if interval_min else ""
                if interval_min:
                    logger.info("Unmute timer set -> start")
                    # 解除タイマーセット
                    # interval = 10  # DEBUG
                    interval = interval_min * 60  # sec
                    timer = MuteWordUnmuteTimer(self.main_winfow_info, muter, interval, mute_word_str)
                    timer.start()

                    logger.info(f"Unmute timer will start {unmuted_at}, target '{mute_word_str}'.")
                    logger.info("Unmute timer set -> done")

                # DB追加
                logger.info("DB update -> start")
                self.main_winfow_info.mute_word_db.mute(mute_word_str, unmuted_at)
                logger.info("DB update -> done")
            logger.info("Mute by mute_keyword -> done")
        except Exception as e:
            raise e
        finally:
            self.update_mute_word_table()
        logger.info("MUTE_WORD_MUTE -> done")
        return Result.SUCCESS


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
