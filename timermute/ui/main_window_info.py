import configparser
from dataclasses import dataclass

import PySimpleGUI as sg

from timermute.db.mute_user_db import MuteUserDB
from timermute.db.mute_word_db import MuteWordDB


@dataclass
class MainWindowInfo:
    window: sg.Window
    values: dict
    mute_word_db: MuteWordDB
    mute_user_db: MuteUserDB
    config: configparser.ConfigParser


if __name__ == "__main__":
    pass
