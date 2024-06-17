import sys
import unittest

from mock import MagicMock, call, patch

from timer_mute.muter.muter import Muter


class TestMuter(unittest.TestCase):
    def _get_mock_config(self) -> MagicMock:
        config_dict = {
            "twitter_api_client": {
                "ct0": "ct0",
                "auth_token": "auth_token",
                "target_screen_name": "target_screen_name",
                "target_id": 11111,
            }
        }
        r = MagicMock(spec=dict)
        r.__getitem__.side_effect = lambda key: config_dict[key]
        return r

    def _reset_muter(self) -> None:
        Muter._instance = None
        del Muter._instance

    def test_init(self):
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_config = self._get_mock_config()

        self._reset_muter()

        instance = Muter(mock_config)
        mock_account.assert_called_once_with(cookies={"ct0": "ct0", "auth_token": "auth_token"}, pbar=False)

        mock_account.reset_mock()
        instance = Muter(mock_config)
        mock_account.assert_not_called()

        with self.assertRaises(ValueError):
            instance = Muter("invalid")

    def test_get_mute_keyword_list(self):
        self.enterContext(patch("timer_mute.muter.muter.logger.info"))
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_config = self._get_mock_config()
        self._reset_muter()
        instance = Muter(mock_config)
        actual = instance.get_mute_keyword_list()
        expect = mock_account.return_value.session.get.return_value.json.return_value
        self.assertEqual(expect, actual)

    def test_mute_keyword(self):
        self.enterContext(patch("timer_mute.muter.muter.logger.info"))
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_account.return_value.v1.side_effect = lambda path, params: "v1()"
        mock_config = self._get_mock_config()
        self._reset_muter()
        instance = Muter(mock_config)
        keyword = "keyword"
        actual = instance.mute_keyword(keyword)
        expect = "v1()"
        self.assertEqual(
            [
                call(cookies={"ct0": "ct0", "auth_token": "auth_token"}, pbar=False),
                call().v1(
                    "mutes/keywords/create.json",
                    {
                        "keyword": keyword,
                        "mute_surfaces": "notifications,home_timeline,tweet_replies",
                        "mute_option": "",
                        "duration": "",
                    },
                ),
            ],
            mock_account.mock_calls,
        )
        self.assertEqual(expect, actual)

        with self.assertRaises(ValueError):
            actual = instance.mute_keyword(-1)

    def test_unmute_keyword(self):
        self.enterContext(patch("timer_mute.muter.muter.logger.info"))
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_get_mute_keyword_list = self.enterContext(patch("timer_mute.muter.muter.Muter.get_mute_keyword_list"))

        keyword = "keyword"
        mock_account.return_value.v1.side_effect = lambda path, params: "v1()"
        mock_get_mute_keyword_list.side_effect = lambda: {"muted_keywords": [{"keyword": keyword, "id": 1}]}
        mock_config = self._get_mock_config()

        self._reset_muter()
        instance = Muter(mock_config)
        actual = instance.unmute_keyword(keyword)
        expect = "v1()"
        self.assertEqual(
            [
                call(cookies={"ct0": "ct0", "auth_token": "auth_token"}, pbar=False),
                call().v1("mutes/keywords/destroy.json", {"ids": 1}),
            ],
            mock_account.mock_calls,
        )
        self.assertEqual(expect, actual)

        mock_get_mute_keyword_list.side_effect = lambda: {
            "muted_keywords": [{"keyword": keyword, "id": 1}, {"keyword": keyword, "id": 2}]
        }
        with self.assertRaises(ValueError):
            actual = instance.unmute_keyword(keyword)

        mock_get_mute_keyword_list.side_effect = lambda: {"muted_keywords": []}
        with self.assertRaises(ValueError):
            actual = instance.unmute_keyword(keyword)

        with self.assertRaises(ValueError):
            actual = instance.unmute_keyword(-1)

    def test_mute_user(self):
        self.enterContext(patch("timer_mute.muter.muter.logger.info"))
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_account.return_value.v1.side_effect = lambda path, params: "v1()"
        mock_config = self._get_mock_config()
        self._reset_muter()
        instance = Muter(mock_config)
        screen_name = "screen_name"
        actual = instance.mute_user(screen_name)
        expect = "v1()"
        self.assertEqual(
            [
                call(cookies={"ct0": "ct0", "auth_token": "auth_token"}, pbar=False),
                call().v1(
                    "mutes/users/create.json",
                    {
                        "screen_name": screen_name,
                    },
                ),
            ],
            mock_account.mock_calls,
        )
        self.assertEqual(expect, actual)

        with self.assertRaises(ValueError):
            actual = instance.mute_user(-1)

    def test_unmute_user(self):
        self.enterContext(patch("timer_mute.muter.muter.logger.info"))
        mock_account = self.enterContext(patch("timer_mute.muter.muter.Account"))
        mock_account.return_value.v1.side_effect = lambda path, params: "v1()"
        mock_config = self._get_mock_config()
        self._reset_muter()
        instance = Muter(mock_config)
        screen_name = "screen_name"
        actual = instance.unmute_user(screen_name)
        expect = "v1()"
        self.assertEqual(
            [
                call(cookies={"ct0": "ct0", "auth_token": "auth_token"}, pbar=False),
                call().v1(
                    "mutes/users/destroy.json",
                    {
                        "screen_name": screen_name,
                    },
                ),
            ],
            mock_account.mock_calls,
        )
        self.assertEqual(expect, actual)

        with self.assertRaises(ValueError):
            actual = instance.unmute_user(-1)


if __name__ == "__main__":
    if sys.argv:
        del sys.argv[1:]
    unittest.main(warnings="ignore")
