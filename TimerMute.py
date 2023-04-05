# coding: utf-8
import argparse
import logging.config
import os
from logging import INFO, getLogger
from pathlib import Path

logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
for name in logging.root.manager.loggerDict:
    if "ffgetter" not in name:
        getLogger(name).disabled = True

logger = getLogger(__name__)
logger.setLevel(INFO)


if __name__ == "__main__":
    logger.info("OK")
