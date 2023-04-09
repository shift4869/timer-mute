# coding: utf-8
import json
import pprint
from logging import INFO, getLogger
from pathlib import Path
from time import sleep

from requests.models import Response

from timermute.muter.TwitterSession import TwitterSession

logger = getLogger(__name__)
logger.setLevel(INFO)


class Muter():
    screen_name: str
    twitter_session: TwitterSession
    redirect_urls: list[str]
    content_list: list[str]

    def __init__(self, screen_name) -> None:
        self.screen_name = screen_name
        self.twitter_session = TwitterSession.create(self.screen_name)
        self.redirect_urls = []
        self.content_list = []

    @property
    def cache_path(self) -> Path:
        # キャッシュファイルパス
        return Path(__file__).parent / f"cache/"

    @property
    def loop(self):
        return self.twitter_session.loop

    def get_mute_keyword_list(self) -> Response:
        logger.info("Getting mute word list all -> start")
        url = "https://twitter.com/i/api/1.1/mutes/keywords/list.json"
        response: Response = self.twitter_session.api_get(url)
        logger.info("Getting mute word list all -> done")
        return response

    def mute_keyword(self, keyword: str) -> Response:
        logger.info(f"POST mute word mute, target is '{keyword}' -> start")
        url = "https://twitter.com/i/api/1.1/mutes/keywords/create.json"
        payload = {
            "keyword": keyword,
            "mute_surfaces": "notifications,home_timeline,tweet_replies",
            "mute_option": "",
            "duration": "",
        }
        response: Response = self.twitter_session.api_post(
            url,
            params=payload
        )
        logger.info(f"POST mute word mute, target is '{keyword}' -> done")
        return response

    def unmute_keyword(self, keyword: str) -> Response:
        logger.info(f"POST muted word unmute, target is '{keyword}' -> start")
        url = "https://twitter.com/i/api/1.1/mutes/keywords/destroy.json"

        response = self.get_mute_keyword_list()
        r_dict: dict = json.loads(response.text)
        target_keyword_dict: dict = [d for d in r_dict.get("muted_keywords") if d.get("keyword") == keyword][0]
        unmute_keyword_id = target_keyword_dict.get("id")

        payload = {
            "ids": unmute_keyword_id,
        }
        response: Response = self.twitter_session.api_post(
            url,
            params=payload
        )
        logger.info(f"POST muted word unmute, target is '{keyword}' -> done")
        return response

    def mute_user(self, screen_name: str) -> Response:
        logger.info(f"POST mute user mute, target is '{screen_name}' -> start")
        url = "https://twitter.com/i/api/1.1/mutes/users/create.json"
        payload = {
            "screen_name": screen_name,
        }
        response: Response = self.twitter_session.api_post(
            url,
            params=payload
        )
        logger.info(f"POST mute user mute, target is '{screen_name}' -> done")
        return response

    def unmute_user(self, screen_name: str) -> Response:
        logger.info(f"POST muted user unmute, target is '{screen_name}' -> start")
        url = "https://twitter.com/i/api/1.1/mutes/users/destroy.json"
        payload = {
            "screen_name": screen_name,
        }
        response: Response = self.twitter_session.api_post(
            url,
            params=payload
        )
        logger.info(f"POST muted user unmute, target is '{screen_name}' -> done")
        return response


if __name__ == "__main__":
    import configparser
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    CONFIG_FILE_NAME = "./config/config.ini"
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE_NAME, encoding="utf8"):
        raise IOError

    screen_name = config["twitter"]["screen_name"]
    muter = Muter(screen_name)

    # response = muter.mute_user("_shift4869")
    # pprint.pprint(response.text)
    # sleep(10)
    # response = muter.unmute_user("_shift4869")
    # pprint.pprint(response.text)

    # response = muter.mute_keyword("てすと")
    # pprint.pprint(response.text)
    response = muter.get_mute_keyword_list()
    r_dict: dict = json.loads(response.text)
    pprint.pprint(r_dict)
    sleep(10)
    # target_keyword_dict: dict = [d for d in r_dict.get("muted_keywords") if d.get("keyword") == "てすと"][0]
    # unmute_keyword_id = target_keyword_dict.get("id")
    # response = muter.unmute_keyword("てすと")
    # pprint.pprint(response.text)

    response = muter.get_mute_keyword_list()
    r_dict: dict = json.loads(response.text)
    pprint.pprint(r_dict)
