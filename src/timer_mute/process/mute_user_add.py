from logging import INFO, getLogger

from timer_mute.db.model import MuteUser
from timer_mute.muter.muter import Muter
from timer_mute.process.base import Base
from timer_mute.timer.timer import MuteUserUnmuteTimer
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result, get_future_datetime, now, popup_get_interval, popup_get_text

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserAdd(Base):
    def __init__(self, main_window_info: MainWindowInfo) -> None:
        super().__init__(main_window_info)

    def run(self) -> Result:
        # "-MUTE_USER_ADD-"
        logger.info("MUTE_USER_ADD -> start")
        # ミュートユーザーをユーザーに問い合せる
        mute_user_str = popup_get_text("mute user input.")
        if not mute_user_str:
            return Result.failed

        try:
            logger.info("Mute by mute_user -> start")
            logger.info(f"Target user is '{mute_user_str}'.")
            config = self.main_window_info.config
            muter = Muter(config)
            r_dict = muter.mute_user(mute_user_str)
            print(r_dict)
            logger.info(f"'{mute_user_str}' is muted.")
            logger.info("Mute by mute_user -> done")

            # 解除タイマー
            # interval をユーザーに問い合せる
            interval_min = popup_get_interval()  # min
            unmuted_at = get_future_datetime(interval_min * 60) if interval_min else ""
            if interval_min:
                logger.info("Unmute timer set -> start")
                # 解除タイマーセット
                # interval = 10  # DEBUG
                interval = interval_min * 60  # sec
                timer = MuteUserUnmuteTimer(self.main_window_info, muter, interval, mute_user_str)
                timer.start()

                logger.info(f"Unmute timer will start {unmuted_at}, target '{mute_user_str}'.")
                logger.info("Unmute timer set -> done")

            # DB追加
            logger.info("DB upsert -> start")
            record = MuteUser(mute_user_str, "muted", now(), now(), unmuted_at)
            self.main_window_info.mute_user_db.upsert(record)
            logger.info("DB upsert -> start")
        except Exception as e:
            raise e
        finally:
            self.update_mute_user_table()
        logger.info("MUTE_USER_ADD -> start")
        return Result.success


if __name__ == "__main__":
    from timer_mute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
