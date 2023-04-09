# coding: utf-8
from logging import INFO, getLogger

from timermute.muter.Muter import Muter
from timermute.process.Base import Base
from timermute.ui.GuiFunction import update_mute_user_table
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class MuteUserUnmute(Base):
    def __init__(self) -> None:
        pass

    def run(self, mw: MainWindowInfo) -> None:
        # "-MUTE_User_UNMUTE-"
        # 選択ミュート済ユーザーを取得
        index_list = mw.values["-LIST_4-"]
        mute_user_list_all = mw.window["-LIST_4-"].get()
        mute_user_list = []
        for i, mute_user in enumerate(mute_user_list_all):
            if i in index_list:
                mute_user_list.append(mute_user)
        if not mute_user_list:
            return

        try:
            # Muter インスタンスを作成し、選択ユーザーのミュートを解除する
            config = mw.config
            screen_name = config["twitter"]["screen_name"]
            muter = Muter(screen_name)
            for mute_user in mute_user_list:
                # 選択ユーザーのミュートを解除
                mute_user_str = mute_user[1]
                response = muter.unmute_user(mute_user_str)
                print(response)

                # DB修正
                mw.mute_user_db.unmute(mute_user_str)
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
