import sys
import unittest
from collections import namedtuple
from datetime import datetime, timedelta

import freezegun
from mock import call, patch

from timer_mute.util import Result, get_future_datetime, now, popup_get_interval, popup_get_text


class TestUtil(unittest.TestCase):
    def test_result(self):
        self.assertTrue(hasattr(Result, "success"))
        self.assertTrue(hasattr(Result, "failed"))

    def test_now(self):
        self.enterContext(freezegun.freeze_time("2024-01-20 12:34:56"))
        destination_format = "%Y-%m-%d %H:%M:%S"
        now_datetime = datetime.now()
        expect = now_datetime.strftime(destination_format)
        actual = now()
        self.assertEqual(expect, actual)

    def test_get_future_datetime(self):
        self.enterContext(freezegun.freeze_time("2024-01-20 12:34:56"))
        destination_format = "%Y-%m-%d %H:%M:%S"
        seconds = 15
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

        Params = namedtuple("Params", ["window_read", "result", "msg"])

        def pre_run(params: Params) -> None:
            mock_window.reset_mock()
            mock_window.return_value.read.side_effect = params.window_read

        def post_run(params: Params) -> None:
            self.assertEqual(
                [
                    call().read(),
                    call().close(),
                ],
                mock_window.mock_calls[1:],
            )

        params_list = [
            Params([("Cancel", {})], None, "キャンセル時"),
            Params([("Submit", {"-R0-": True})], None, "no limit 指定時"),
            Params([("Submit", {"-R1-": True})], 1 * 60, "1 hours 指定時"),
            Params([("Submit", {"-R2-": True})], 2 * 60, "2 hours 指定時"),
            Params([("Submit", {"-R3-": True})], 6 * 60, "6 hours 指定時"),
            Params([("Submit", {"-R4-": True})], 12 * 60, "12 hours 指定時"),
            Params([("Submit", {"-R5-": True})], 24 * 60, "24 hours 指定時"),
            Params([("Submit", {"-R6-": "3", "-R7-": "minutes later"})], 3, "minutes later 正常系"),
            Params([("Submit", {"-R6-": "8", "-R7-": "minutes later"})], 8, "minutes later 正常系2"),
            Params(
                [("Submit", {"-R0-": True, "-R6-": "3", "-R7-": "minutes later"})],
                3,
                "no limit と自由入力が同時に指定されている",
            ),
            Params([("Submit", {"-R6-": "3", "-R7-": "hours later"})], 3 * 60, "hours later 正常系"),
            Params([("Submit", {"-R6-": "3", "-R7-": "days later"})], 3 * 60 * 24, "days later 正常系"),
            Params([("Submit", {"-R6-": "3", "-R7-": "weeks later"})], 3 * 60 * 24 * 7, "weeks later 正常系"),
            Params([("Submit", {"-R6-": "3", "-R7-": "months later"})], 3 * 60 * 24 * 31, "months later 正常系"),
            Params([("Submit", {"-R6-": "3", "-R7-": "years later"})], 3 * 60 * 24 * 31 * 12, "years later 正常系"),
            Params([("Submit", {"-R6-": False, "-R7-": "minutes later"})], None, "interval_str が False"),
            Params([("Submit", {"-R6-": "invalid_str", "-R7-": "minutes later"})], None, "interval_str が不正"),
            Params([("Submit", {})], None, "どの radio_button も選択されていない"),
        ]
        for params in params_list:
            with self.subTest(params.msg):
                pre_run(params)
                actual = popup_get_interval()
                expect = params.result
                self.assertEqual(expect, actual)
                post_run(params)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
