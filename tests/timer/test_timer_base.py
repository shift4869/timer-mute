import sys
import unittest
from typing import Callable

from mock import MagicMock, call, patch

from timermute.timer.timer import TimerBase


class TestTimerBase(unittest.TestCase):
    def test_init(self):
        mock_timer = self.enterContext(patch("timermute.timer.timer.threading.Timer"))
        interval = 1.0
        func = MagicMock(spec=Callable)
        args = {"key": "value"}
        instance = TimerBase(interval, func, args)
        self.assertEqual(interval, instance._interval)
        self.assertEqual(func, instance._func)
        self.assertEqual(args, instance._args)
        self.assertEqual([call(interval, func, args)], mock_timer.mock_calls)

    def test_start(self):
        self.enterContext(patch("timermute.timer.timer.logger"))
        mock_timer = self.enterContext(patch("timermute.timer.timer.threading.Timer"))
        interval = 1.0
        func = MagicMock(spec=Callable)
        args = {"key": "value"}
        instance = TimerBase(interval, func, args)
        actual = instance.start()
        self.assertEqual([call(interval, func, args), call().start()], mock_timer.mock_calls)
        self.assertEqual(mock_timer.return_value, actual)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
