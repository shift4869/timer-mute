from logging import INFO, getLogger

from timermute.db.Model import MuteWord
from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.timer.Timer import MuteWordUnmuteTimer
from timermute.ui.GuiFunction import get_future_datetime, now, popup_get_interval, popup_get_text, update_mute_word_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteWordAdd(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_WORD_ADD-"
        logger.info("MUTE_WORD_ADD -> start")
        # ミュートワードをユーザーに問い合せる
        mute_word_str = popup_get_text("Mute word input.")
        if not mute_word_str:
            return

        try:
            # デフォルトでミュートする
            logger.info("Mute by mute_keyword -> start")
            logger.info(f"Target keyword is '{mute_word_str}'.")
            config = mw.config
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
                timer = MuteWordUnmuteTimer(mw, muter, interval, mute_word_str)
                timer.start()

                logger.info(f"Unmute timer will start {unmuted_at}, target '{mute_word_str}'.")
                logger.info("Unmute timer set -> done")

            # DB追加
            logger.info("DB upsert -> start")
            record = MuteWord(mute_word_str, "muted", now(), now(), unmuted_at)
            mw.mute_word_db.upsert(record)
            logger.info("DB upsert -> done")
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_word_table(mw.window, mw.mute_word_db)
        logger.info("MUTE_WORD_ADD -> done")
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
