import pprint
from logging import INFO, getLogger
from pathlib import Path
from time import sleep

from httpx import Response
import orjson
from twitter.account import Account
from twitter.util import get_headers

logger = getLogger(__name__)
logger.setLevel(INFO)


class Muter:
    account: Account

    def __init__(self, config_dict: dict) -> None:
        if not isinstance(config_dict, dict):
            raise ValueError("config_dict must be dict.")
        if not hasattr(self, "account"):
            twitter_api_client_config = config_dict["twitter_api_client"]
            ct0 = twitter_api_client_config["ct0"]
            auth_token = twitter_api_client_config["auth_token"]
            self.account = Account(cookies={"ct0": ct0, "auth_token": auth_token}, pbar=False)

    def __new__(cls, *args, **kargs):
        # シングルトン
        if not hasattr(cls, "_instance"):
            cls._instance = super(Muter, cls).__new__(cls)
        return cls._instance

    def get_mute_keyword_list(self) -> dict:
        logger.info("Getting mute word list all -> start")
        path = "mutes/keywords/list.json"
        params = {}
        headers = get_headers(self.account.session)
        r: Response = self.account.session.get(f"{self.account.v1_api}/{path}", headers=headers, params=params)
        result: dict = r.json()
        logger.info("Getting mute word list all -> done")
        return result

    def mute_keyword(self, keyword: str) -> dict:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")

        logger.info(f"POST mute word mute, target is '{keyword}' -> start")
        path = "mutes/keywords/create.json"
        payload = {
            "keyword": keyword,
            "mute_surfaces": "notifications,home_timeline,tweet_replies",
            "mute_option": "",
            "duration": "",
        }
        result = self.account.v1(path, payload)
        logger.info(f"POST mute word mute, target is '{keyword}' -> done")
        return result

    def unmute_keyword(self, keyword: str) -> dict:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")

        logger.info(f"POST muted word unmute, target is '{keyword}' -> start")

        r_dict: dict = self.get_mute_keyword_list()
        target_keyword_dict_list: list[dict] = [d for d in r_dict.get("muted_keywords") if d.get("keyword") == keyword]
        if not target_keyword_dict_list:
            raise ValueError("Target muted word is not found.")
        elif len(target_keyword_dict_list) != 1:
            raise ValueError("Target muted word is multiple found.")
        target_keyword_dict = target_keyword_dict_list[0]
        unmute_keyword_id = target_keyword_dict.get("id")

        path = "mutes/keywords/destroy.json"
        payload = {
            "ids": unmute_keyword_id,
        }
        result = self.account.v1(path, payload)
        logger.info(f"POST muted word unmute, target is '{keyword}' -> done")
        return result

    def mute_user(self, screen_name: str) -> dict:
        if not isinstance(screen_name, str):
            raise ValueError("screen_name must be str.")

        logger.info(f"POST mute user mute, target is '{screen_name}' -> start")
        path = "mutes/users/create.json"
        payload = {
            "screen_name": screen_name,
        }
        result = self.account.v1(path, payload)
        logger.info(f"POST mute user mute, target is '{screen_name}' -> done")
        return result

    def unmute_user(self, screen_name: str) -> dict:
        if not isinstance(screen_name, str):
            raise ValueError("screen_name must be str.")

        logger.info(f"POST muted user unmute, target is '{screen_name}' -> start")
        path = "mutes/users/destroy.json"
        payload = {
            "screen_name": screen_name,
        }
        result = self.account.v1(path, payload)
        logger.info(f"POST muted user unmute, target is '{screen_name}' -> done")
        return result


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    CONFIG_FILE_NAME = "./config/config.json"
    config = orjson.loads(Path(CONFIG_FILE_NAME).read_bytes())

    muter = Muter(config)

    r_dict = muter.get_mute_keyword_list()
    pprint.pprint(r_dict)

    r_dict = muter.mute_keyword("てすと")
    pprint.pprint(r_dict)
    r_dict = muter.get_mute_keyword_list()
    pprint.pprint(r_dict)
    sleep(1)

    target_keyword_dict: dict = [d for d in r_dict.get("muted_keywords") if d.get("keyword") == "てすと"][0]
    unmute_keyword_id = target_keyword_dict.get("id")
    r_dict = muter.unmute_keyword("てすと")
    pprint.pprint(r_dict)

    r_dict = muter.mute_user("SplatoonJP")
    pprint.pprint(r_dict)
    sleep(1)

    r_dict = muter.unmute_user("SplatoonJP")
    pprint.pprint(r_dict)
