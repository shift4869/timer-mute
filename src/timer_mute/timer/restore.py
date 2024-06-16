from datetime import datetime
from logging import INFO, getLogger

from timer_mute.muter.muter import Muter
from timer_mute.timer.timer import MuteUserUnmuteTimer, MuteWordUnmuteTimer
from timer_mute.ui.main_window_info import MainWindowInfo
from timer_mute.util import Result

logger = getLogger(__name__)
logger.setLevel(INFO)


class RestoreTimerBase:
    def __init__(self) -> None:
        pass

    @classmethod
    def set(self, main_window_info: MainWindowInfo) -> Result:
        return Result.success


class MuteWordRestoreTimer(RestoreTimerBase):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def set(self, main_window_info: MainWindowInfo) -> Result:
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
            else:
                timer = MuteWordUnmuteTimer(main_window_info, muter, interval, target_keyword)
                timer.start()
        return Result.success


class MuteUserRestoreTimer(RestoreTimerBase):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def set(self, main_window_info: MainWindowInfo) -> Result:
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
            else:
                timer = MuteUserUnmuteTimer(main_window_info, muter, interval, target_screen_name)
                timer.start()
        return Result.success


if __name__ == "__main__":
    from timer_mute.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.run()
