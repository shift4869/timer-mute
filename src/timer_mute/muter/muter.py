import pprint
from logging import INFO, getLogger
from pathlib import Path
from time import sleep

import orjson
from httpx import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from twitter.account import Account
from twitter.util import get_headers

from timer_mute.muter.code_challenge import CodeChallenger

logger = getLogger(__name__)
logger.setLevel(INFO)


class Muter:
    config_dict: dict
    account: Account

    def __init__(self, config_dict: dict) -> None:
        if not isinstance(config_dict, dict):
            raise ValueError("config_dict must be dict.")
        self.config_dict = config_dict
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

    def get_endpoint_url(self, webapi_path: str) -> str:
        domain = "https://x.com"
        path_prefix = "/i/api/1.1/"
        endpoint = f"{domain}{path_prefix}{webapi_path}"
        return endpoint

    def get_browser(self) -> webdriver.Chrome:
        # シングルトン
        if hasattr(self, "driver"):
            if self.driver and isinstance(self.driver, webdriver.Chrome):
                return self.driver

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # ヘッドレスモードを有効化
        chrome_options.add_argument("--disable-gpu")  # GPUを無効化（古いバージョンのChrome向け）
        chrome_options.add_argument("--window-size=1920x1080")  # ウィンドウサイズを指定
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def get_client_transaction_id(self, webapi_path: str, method: str) -> dict:
        logger.info("Getting client_transaction_id -> start")
        path_prefix = "/i/api/1.1/"
        path = f"{path_prefix}{webapi_path}"

        code_challenge_data = CodeChallenger(config_dict=self.config_dict).get_challenge_data()
        challenge_data = {
            "action": "init",
            "challenge": code_challenge_data["challenge"],
            "verificationCode": code_challenge_data["verificationCode"],
            "anims": code_challenge_data["anims"],
        }

        driver = self.get_browser()
        file_path = (Path(__file__).parent / "solver.html").resolve()
        driver.get(f"file:///{file_path}")
        driver.execute_script(
            """
            window.postMessage(arguments[0], arguments[1]);
            """,
            challenge_data,
            "*",
        )
        challenge_data = {
            "action": "solve",
            "path": path,
            "method": method,
            "id": "id",
        }
        driver.execute_script(
            """
            window.postMessage(arguments[0], arguments[1]);
            """,
            challenge_data,
            "*",
        )

        client_transaction_id = None
        for _ in range(10):
            sleep(1)
            client_transaction_id = driver.execute_script(
                """
                return window.lastMessage || null;
                """
            )
            if client_transaction_id:
                break

        # driver.quit()
        if not client_transaction_id:
            logger.info("Getting client_transaction_id is failed.")
            return ""
        else:
            logger.info(f"Obtained client_transaction_id is [ {client_transaction_id} ]")

        logger.info("Getting client_transaction_id -> done")
        return client_transaction_id

    def get_mute_keyword_list(self) -> dict:
        logger.info("Getting mute word list all -> start")
        webapi_path = "mutes/keywords/list.json"
        endpoint = self.get_endpoint_url(webapi_path)
        params = {}
        headers = get_headers(self.account.session)

        client_transaction_id = self.get_client_transaction_id(webapi_path, "GET")
        headers["x-client-transaction-id"] = client_transaction_id
        r: Response = self.account.session.get(endpoint, headers=headers, params=params)
        result: dict = r.json()
        logger.info("Getting mute word list all -> done")
        return result

    def mute_keyword(self, keyword: str) -> dict:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")

        logger.info(f"POST mute word mute, target is '{keyword}' -> start")
        headers = get_headers(self.account.session)
        webapi_path = "mutes/keywords/create.json"
        endpoint = self.get_endpoint_url(webapi_path)
        payload = {
            "keyword": keyword,
            "mute_surfaces": "notifications,home_timeline,tweet_replies",
            "mute_option": "",
            "duration": "",
        }
        client_transaction_id = self.get_client_transaction_id(webapi_path, "POST")
        headers["x-client-transaction-id"] = client_transaction_id
        headers["content-type"] = "application/x-www-form-urlencoded"
        r: Response = self.account.session.post(endpoint, headers=headers, data=payload)
        result = r.json()
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

        headers = get_headers(self.account.session)
        webapi_path = "mutes/keywords/destroy.json"
        endpoint = self.get_endpoint_url(webapi_path)
        payload = {
            "ids": unmute_keyword_id,
        }
        client_transaction_id = self.get_client_transaction_id(webapi_path, "POST")
        headers["x-client-transaction-id"] = client_transaction_id
        headers["content-type"] = "application/x-www-form-urlencoded"
        r: Response = self.account.session.post(endpoint, headers=headers, data=payload)
        result = r.json()
        logger.info(f"POST muted word unmute, target is '{keyword}' -> done")
        return result

    def mute_user(self, screen_name: str) -> dict:
        if not isinstance(screen_name, str):
            raise ValueError("screen_name must be str.")

        logger.info(f"POST mute user mute, target is '{screen_name}' -> start")
        headers = get_headers(self.account.session)
        webapi_path = "mutes/users/create.json"
        endpoint = self.get_endpoint_url(webapi_path)
        payload = {
            "screen_name": screen_name,
        }
        client_transaction_id = self.get_client_transaction_id(webapi_path, "POST")
        headers["x-client-transaction-id"] = client_transaction_id
        headers["content-type"] = "application/x-www-form-urlencoded"
        r: Response = self.account.session.post(endpoint, headers=headers, data=payload)
        result = r.json()
        logger.info(f"POST mute user mute, target is '{screen_name}' -> done")
        return result

    def unmute_user(self, screen_name: str) -> dict:
        if not isinstance(screen_name, str):
            raise ValueError("screen_name must be str.")

        logger.info(f"POST muted user unmute, target is '{screen_name}' -> start")
        headers = get_headers(self.account.session)
        webapi_path = "mutes/users/destroy.json"
        endpoint = self.get_endpoint_url(webapi_path)
        payload = {
            "screen_name": screen_name,
        }
        client_transaction_id = self.get_client_transaction_id(webapi_path, "POST")
        headers["x-client-transaction-id"] = client_transaction_id
        headers["content-type"] = "application/x-www-form-urlencoded"
        r: Response = self.account.session.post(endpoint, headers=headers, data=payload)
        result = r.json()
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

    keyword = "てすと"
    r_dict = muter.mute_keyword(keyword)
    pprint.pprint(r_dict)
    r_dict = muter.get_mute_keyword_list()
    pprint.pprint(r_dict)
    sleep(1)

    target_keyword_dict: dict = [d for d in r_dict.get("muted_keywords") if d.get("keyword") == keyword][0]
    unmute_keyword_id = target_keyword_dict.get("id")
    r_dict = muter.unmute_keyword(keyword)
    pprint.pprint(r_dict)

    screen_name = "SplatoonJP"
    r_dict = muter.mute_user(screen_name)
    pprint.pprint(r_dict)
    sleep(1)

    r_dict = muter.unmute_user(screen_name)
    pprint.pprint(r_dict)
