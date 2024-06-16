from dataclasses import dataclass

import PySimpleGUI as sg

from timer_mute.db.mute_user_db import MuteUserDB
from timer_mute.db.mute_word_db import MuteWordDB


@dataclass
class MainWindowInfo:
    window: sg.Window
    values: dict
    mute_word_db: MuteWordDB
    mute_user_db: MuteUserDB
    config: dict

    def __post_init__(self):
        if not isinstance(self.window, sg.Window):
            raise ValueError("window must be sg.Window.")
        if not isinstance(self.values, dict):
            raise ValueError("values must be dict.")
        if not isinstance(self.mute_word_db, MuteWordDB):
            raise ValueError("mute_word_db must be MuteWordDB.")
        if not isinstance(self.mute_user_db, MuteUserDB):
            raise ValueError("mute_user_db must be MuteUserDB.")
        if not isinstance(self.config, dict):
            raise ValueError("config must be dict.")


if __name__ == "__main__":
    pass
