import sys
import unittest
from collections import namedtuple
from datetime import datetime, timedelta

import freezegun
import PySimpleGUI as sg
from mock import MagicMock, call, patch

from timer_mute.util import Result, get_future_datetime, now, popup_get_interval, popup_get_text


class TestUtil(unittest.TestCase):
    def test_result(self):
        self.assertTrue(hasattr(Result, "SUCCESS"))
        self.assertTrue(hasattr(Result, "FAILED"))

    def test_now(self):
        self.enterContext(freezegun.freeze_time("2024-01-20 12:34:56"))
        destination_format = "%Y-%m-%d %H:%M:%S"
        now_datetime = datetime.now()
        expect = now_datetime.strftime(destination_format)
        actual = now()
        self.assertEqual(expect, actual)

    def test_get_future_datetime(self):
        self.enterContext(freezegun.freeze_time("2024-01-20 12:34:56"))
        seconds = 15
        destination_format = "%Y-%m-%d %H:%M:%S"
        now_datetime = datetime.now()
        delta = timedelta(seconds=seconds)
        future_datetime = now_datetime + delta
        expect = future_datetime.strftime(destination_format)
        actual = get_future_datetime(seconds)
        self.assertEqual(expect, actual)

        another_seconds = 10
        actual = get_future_datetime(another_seconds)
        self.assertNotEqual(expect, actual)

        seconds = -1
        delta = timedelta(seconds=seconds)
        future_datetime = now_datetime + delta
        expect = future_datetime.strftime(destination_format)
        actual = get_future_datetime(seconds)
        self.assertEqual(expect, actual)

        with self.assertRaises(TypeError):
            actual = get_future_datetime("invalid_seconds")

    def test_popup_get_text(self):
        mock_window = self.enterContext(patch("timer_mute.util.sg.Window"))

        def pre_run(window_read):
            mock_window.reset_mock()
            mock_window.return_value.read.side_effect = window_read

        def post_run(window_read):
            self.assertEqual(
                [
                    call().__getitem__("-INPUT-"),
                    call().__getitem__().set_focus(True),
                    call().read(),
                    call().close(),
                ],
                mock_window.mock_calls[1:],
            )

        Params = namedtuple("Params", ["window_read", "result"])
        params_list = [
            Params([("Ok", {"-INPUT-": "text"})], "text"),
            Params([("Cancel", {"-INPUT-": "text"})], None),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            actual = popup_get_text("message")
            expect = params[-1]
            self.assertEqual(expect, actual)
            post_run(*params[:-1])

    def test_popup_get_interval(self):
        mock_window = self.enterContext(patch("timer_mute.util.sg.Window"))

        def pre_run(window_read):
            mock_window.reset_mock()
            mock_window.return_value.read.side_effect = window_read

        def post_run(window_read):
            self.assertEqual(
                [
                    call().__getitem__("-INPUT-"),
                    call().__getitem__().set_focus(True),
                    call().read(),
                    call().close(),
                ],
                mock_window.mock_calls[1:],
            )

        Params = namedtuple("Params", ["window_read", "result"])
        params_list = [
            Params([("Ok", {"-INPUT-": "text"})], "text"),
            Params([("Cancel", {"-INPUT-": "text"})], None),
        ]
        for params in params_list:
            pre_run(*params[:-1])
            actual = popup_get_text("message")
            expect = params[-1]
            self.assertEqual(expect, actual)
            post_run(*params[:-1])


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
