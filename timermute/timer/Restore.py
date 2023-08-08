# coding: utf-8
from datetime import datetime
from logging import INFO, getLogger

from timermute.db.Model import MuteUser, MuteWord
from timermute.muter.Muter import Muter
from timermute.timer.Timer import MuteUserUnmuteTimer, MuteWordUnmuteTimer
from timermute.ui.MainWindowInfo import MainWindowInfo

logger = getLogger(__name__)
logger.setLevel(INFO)


class RestoreTimerBase():
    def __init__(self):
        pass

    @classmethod
    def set(self, main_window_info: MainWindowInfo):
        pass


class MuteWordRestoreTimer(RestoreTimerBase):
    def __init__(self):
        super().__init__()
        pass

    @classmethod
    def set(self, main_window_info: MainWindowInfo):
        muter = Muter(main_window_info.config)
        mute_word_all = main_window_info.mute_word_db.select()
        mute_word_restore_list = [r for r in mute_word_all if r.status == "muted"]
        destination_format = "%Y-%m-%d %H:%M:%S"
        for mute_word in mute_word_restore_list:
            target_keyword = mute_word.keyword
            unmuted_at = mute_word.unmuted_at
            if not unmuted_at:
                continue
            delta = datetime.strptime(unmuted_at, destination_format) - datetime.now()
            interval = float(delta.total_seconds())
            if interval < 1:
                # 本来予定されていた時刻はすでに過ぎている
                try:
                    logger.info("Unmute keyword -> start")
                    logger.info(f"Target keyword is '{target_keyword}'.")
                    muter.unmute_keyword(target_keyword)
                    logger.info("Unmute keyword -> done")
                except Exception as e:
                    logger.warning(e)
                    pass
                try:
                    logger.info("DB update -> start")
                    main_window_info.mute_word_db.unmute(target_keyword)
                    logger.info("DB update -> done")
                except Exception as e:
                    logger.warning(e)
                    pass
                continue
            timer = MuteWordUnmuteTimer(main_window_info, muter, interval, target_keyword)
            timer.start()
        pass


class MuteUserRestoreTimer(RestoreTimerBase):
    def __init__(self):
        super().__init__()
        pass

    @classmethod
    def set(self, main_window_info: MainWindowInfo):
        muter = Muter(main_window_info.config)
        mute_user_all = main_window_info.mute_user_db.select()
        mute_user_restore_list = [r for r in mute_user_all if r.status == "muted"]
        destination_format = "%Y-%m-%d %H:%M:%S"
        for mute_user in mute_user_restore_list:
            target_screen_name = mute_user.screen_name
            unmuted_at = mute_user.unmuted_at
            if not unmuted_at:
                continue
            delta = datetime.strptime(unmuted_at, destination_format) - datetime.now()
            interval = float(delta.total_seconds())
            if interval < 1:
                # 本来予定されていた時刻はすでに過ぎている
                try:
                    logger.info("Unmute user -> start")
                    logger.info(f"Target user is '{target_screen_name}'.")
                    muter.unmute_user(target_screen_name)
                    logger.info("Unmute user -> done")
                except Exception as e:
                    logger.warning(e)
                    pass
                try:
                    logger.info("DB update -> start")
                    main_window_info.mute_user_db.unmute(target_screen_name)
                    logger.info("DB update -> done")
                except Exception as e:
                    logger.warning(e)
                    pass
                continue
            timer = MuteUserUnmuteTimer(main_window_info, muter, interval, target_screen_name)
            timer.start()
        pass


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    main_window = MainWindow()
    main_window.run()
    pass
