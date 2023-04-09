# coding: utf-8
from logging import INFO, getLogger

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.timer.Timer import MuteUserUnmuteTimer
from timermute.ui.GuiFunction import get_future_datetime, popup_get_interval, update_mute_user_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserMute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_USER_MUTE-"
        # 選択ミュートユーザーを取得
        index_list = mw.values["-LIST_3-"]
        mute_user_list_all = mw.window["-LIST_3-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            return

        try:
            # Muter インスタンスを作成し、選択ユーザーをミュートする
            config = mw.config
            screen_name = config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            for mute_user in mute_user_list:
                # 選択ユーザーをミュート
                mute_user_str = mute_user[1]
                response = muter.mute_user(mute_user_str)
                print(response)

                # 解除タイマー
                # interval をユーザーに問い合せる
                interval_min = popup_get_interval()  # min
                if interval_min:
                    # 解除タイマーセット
                    # interval = 10  # DEBUG
                    interval = interval_min * 60  # sec
                    timer = MuteUserUnmuteTimer(mw, muter, interval, mute_user_str)
                    timer.start()

                # DB追加
                unmuted_at = get_future_datetime(interval_min * 60)
                mw.mute_user_db.mute(mute_user_str, unmuted_at)
        except Exception as e:
            raise e
        finally:
            # UI表示更新
            update_mute_user_table(mw.window, mw.mute_user_db)
        return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
