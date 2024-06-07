import logging.config
from logging import INFO, getLogger

from timer_mute.ui.main_window import MainWindow

logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
for name in logging.root.manager.loggerDict:
    if "timer_mute" not in name:
        getLogger(name).disabled = True

logger = getLogger(__name__)
logger.setLevel(INFO)


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
