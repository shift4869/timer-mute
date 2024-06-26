from logging import INFO, getLogger

from timer_mute.db.model import MuteWord
from timer_mute.muter.muter import Muter
from timer_mute.process.base import Base
from timer_mute.timer.timer import MuteWordUnmuteTimer
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result, get_future_datetime, now, popup_get_interval, popup_get_text

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordAdd(Base):
    def __init__(self, main_window_info: MainWindowInfo) -> None:
        super().__init__(main_window_info)

    def run(self) -> Result:
        # "-MUTE_WORD_ADD-"
        logger.info("MUTE_WORD_ADD -> start")
        # ミュートワードをユーザーに問い合せる
        mute_word_str = popup_get_text("Mute word input.")
        if not mute_word_str:
            return Result.failed

        try:
            # デフォルトでミュートする
            logger.info("Mute by mute_keyword -> start")
            logger.info(f"Target keyword is '{mute_word_str}'.")
            config = self.main_window_info.config
            muter = Muter(config)
            r_dict = muter.mute_keyword(mute_word_str)
            print(r_dict)
            logger.info(f"'{mute_word_str}' is muted.")
            logger.info("Mute by mute_keyword -> done")

            # 解除タイマー
            # interval をユーザーに問い合せる
            interval_min = popup_get_interval()  # min
            unmuted_at = get_future_datetime(interval_min * 60) if interval_min else ""
            if interval_min:
                logger.info("Unmute timer set -> start")
                # 解除タイマーセット
                # interval = 10  # DEBUG
                interval = interval_min * 60  # sec
                timer = MuteWordUnmuteTimer(self.main_window_info, muter, interval, mute_word_str)
                timer.start()

                logger.info(f"Unmute timer will start {unmuted_at}, target '{mute_word_str}'.")
                logger.info("Unmute timer set -> done")

            # DB追加
            logger.info("DB upsert -> start")
            record = MuteWord(mute_word_str, "muted", now(), now(), unmuted_at)
            self.main_window_info.mute_word_db.upsert(record)
            logger.info("DB upsert -> done")
        except Exception as e:
            raise e
        finally:
            self.update_mute_word_table()
        logger.info("MUTE_WORD_ADD -> done")
        return Result.success


if __name__ == "__main__":
    from timer_mute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
