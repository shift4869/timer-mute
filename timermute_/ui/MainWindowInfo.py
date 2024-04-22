import configparser
from dataclasses import dataclass

import PySimpleGUI as sg

from timermute.db.MuteUserDB import MuteUserDB
from timermute.db.MuteWordDB import MuteWordDB


@dataclass
class MainWindowInfo():
    window: sg.Window
    values: dict
    mute_word_db: MuteWordDB
    mute_user_db: MuteUserDB
    config: configparser.ConfigParser


if __name__ == "__main__":
    pass
