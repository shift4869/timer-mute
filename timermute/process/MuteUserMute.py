from logging import INFO, getLogger

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.timer.Timer import MuteUserUnmuteTimer
from timermute.ui.MainWindowInfo import MainWindowInfo
from timermute.ui.Util import get_future_datetime, popup_get_interval, update_mute_user_table

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserMute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_USER_MUTE-"
        logger.info("MUTE_USER_MUTE -> start")
        # 選択ミュートユーザーを取得
        index_list = mw.values["-LIST_3-"]
        logger.info("Getting selected mute user -> start")
        mute_user_list_all = mw.window["-LIST_3-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            logger.info("Selected mute user is empty.")
            logger.info("Getting selected mute user -> done")
            logger.info("MUTE_WORD_MUTE -> done")
            return
        logger.info("Getting selected mute user -> start")

        try:
            # Muter インスタンスを作成し、選択ユーザーをミュートする
            logger.info("Mute by mute_user -> start")
            config = mw.config
            muter = Muter(config)
            for mute_user in mute_user_list:
                # 選択ユーザーをミュート
                mute_user_str = mute_user[1]
                logger.info(f"Target user is '{mute_user_str}'.")
                r_dict = muter.mute_user(mute_user_str)
                print(r_dict)
                logger.info(f"'{mute_user_str}' is muted.")

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
                logger.info("DB update -> start")
                mw.mute_user_db.mute(mute_user_str, unmuted_at)
                logger.info("DB update -> done")
            logger.info("Mute by mute_user -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_user_table(mw.window, mw.mute_user_db)
        logger.info("MUTE_USER_MUTE -> done")
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
