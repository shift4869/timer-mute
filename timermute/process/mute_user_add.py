from logging import INFO, getLogger

from timermute.db.model import MuteUser
from timermute.muter.muter import Muter
from timermute.process.base import Base
from timermute.timer.timer import MuteUserUnmuteTimer
from timermute.ui.main_window_info import MainWindowInfo
from timermute.ui.util import get_future_datetime, now, popup_get_interval, popup_get_text, update_mute_user_table

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserAdd(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_USER_ADD-"
        logger.info("MUTE_USER_ADD -> start")
        # ミュートユーザーをユーザーに問い合せる
        mute_user_str = popup_get_text("mute user input.")
        if not mute_user_str:
            return

        try:
            # デフォルトでミュートする
            logger.info("Mute by mute_user -> start")
            logger.info(f"Target user is '{mute_user_str}'.")
            config = mw.config
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
                timer = MuteUserUnmuteTimer(mw, muter, interval, mute_user_str)
                timer.start()

                logger.info(f"Unmute timer will start {unmuted_at}, target '{mute_user_str}'.")
                logger.info("Unmute timer set -> done")

            # DB追加
            logger.info("DB upsert -> start")
            record = MuteUser(mute_user_str, "muted", now(), now(), unmuted_at)
            mw.mute_user_db.upsert(record)
            logger.info("DB upsert -> start")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_user_table(mw.window, mw.mute_user_db)
        logger.info("MUTE_USER_ADD -> start")
        return


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
    pass
