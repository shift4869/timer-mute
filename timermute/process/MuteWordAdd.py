# coding: utf-8
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
        # ミュートワードをユーザーに問い合せる
        mute_word_str = popup_get_text("mute word input.")
        if not mute_word_str:
            return

        try:
            # デフォルトでミュートする
            config = mw.config
            screen_name = config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            response = muter.mute_keyword(mute_word_str)
            print(response)

            # 解除タイマー
            # interval をユーザーに問い合せる
            interval_min = popup_get_interval()  # min
            if interval_min:
                # 解除タイマーセット
                # interval = 10  # DEBUG
                interval = interval_min * 60  # sec
                timer = MuteWordUnmuteTimer(mw, muter, interval, mute_word_str)
                timer.start()

            # DB追加
            unmuted_at = get_future_datetime(interval_min * 60)
            record = MuteWord(mute_word_str, "muted", now(), now(), unmuted_at)
            mw.mute_word_db.upsert(record)
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_word_table(mw.window, mw.mute_word_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
