import configparser
import sys
import unittest
from collections import namedtuple

import PySimpleGUI as sg
from mock import MagicMock

from timermute.db.mute_user_db import MuteUserDB
from timermute.db.mute_word_db import MuteWordDB
from timermute.ui.main_window_info import MainWindowInfo


class TestMainWindowInfo(unittest.TestCase):
    def test_init(self):
        window = MagicMock(spec=sg.Window)
        values = MagicMock(spec=dict)
        mute_word_db = MagicMock(spec=MuteWordDB)
        mute_user_db = MagicMock(spec=MuteUserDB)
        config = MagicMock(spec=configparser.ConfigParser)

        instance = MainWindowInfo(window, values, mute_word_db, mute_user_db, config)
        self.assertEqual(window, instance.window)
        self.assertEqual(values, instance.values)
        self.assertEqual(mute_word_db, instance.mute_word_db)
        self.assertEqual(mute_user_db, instance.mute_user_db)
        self.assertEqual(config, instance.config)

        Params = namedtuple(
            "Params",
            ["window", "values", "mute_word_db", "mute_user_db", "config"],
        )
        params_list = [
            Params("invlid", values, mute_word_db, mute_user_db, config),
            Params(window, "invlid", mute_word_db, mute_user_db, config),
            Params(window, values, "invlid", mute_user_db, config),
            Params(window, values, mute_word_db, "invlid", config),
            Params(window, values, mute_word_db, mute_user_db, "invlid"),
        ]
        for params in params_list:
            with self.assertRaises(ValueError):
                instance = MainWindowInfo(*params)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
