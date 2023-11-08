import logging.config
from logging import INFO, getLogger

from timermute.ui.MainWindow import MainWindow

logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
for name in logging.root.manager.loggerDict:
    if "timermute" not in name:
        getLogger(name).disabled = True

logger = getLogger(__name__)
logger.setLevel(INFO)


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()
