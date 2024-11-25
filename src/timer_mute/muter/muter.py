import pprint
import re
from logging import INFO, getLogger
from pathlib import Path
from time import sleep
from typing import cast

import httpx
import orjson
from bs4 import BeautifulSoup
from httpx import Response
from requests.cookies import RequestsCookieJar
# from requests_html import HTMLSession
from twitter.account import Account
from twitter.util import get_headers

from timer_mute.muter.session import CookieSessionUserHandler

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

        # access_token_secret から Cookie を取得
        cookies_dict: dict[str, str] = self.account.session.cookies

        # RequestCookieJar オブジェクトに変換
        cookies = RequestsCookieJar()
        for key, value in cookies_dict.items():
            cookies.set(key, value)

        # 読み込んだ RequestCookieJar オブジェクトを CookieSessionUserHandler に渡す
        # Cookie を指定する際はコンストラクタ内部で API リクエストは行われないため、ログイン時のように await する必要性はない
        self.cookie_session_user_handler = CookieSessionUserHandler(cookies=cookies)
        self.graphql_headers_dict = (
            self.cookie_session_user_handler.get_graphql_api_headers()
        )  # GraphQL API 用ヘッダー
        self.html_headers_dict = self.cookie_session_user_handler.get_html_headers()  # HTML 用ヘッダー
        self.js_headers_dict = self.cookie_session_user_handler.get_js_headers(
            cross_origin=True
        )  # JavaScript 用ヘッダー

        cookies_dict = self.cookie_session_user_handler.get_cookies_as_dict()
        cookies = httpx.Cookies()
        for name, value in cookies_dict.items():
            # ドメインを ".x.com" 、パスを "/" に設定しておくことが重要 (でないと Cookie 更新時にちゃんと上書きできない)
            # ただし "lang" キーだけは ".x.com" でなく "x.com" にする必要がある
            if name == "lang":
                cookies.set(name, value, domain="x.com", path="/")
            else:
                cookies.set(name, value, domain=".x.com", path="/")

        # httpx の非同期 HTTP クライアントのインスタンスを作成
        # 可能な限り Chrome からのリクエストに偽装するため、app.constants.HTTPX_CLIENT は使わずに独自のインスタンスを作成する
        self.httpx_client = httpx.Client(
            # Cookie を設定
            # Cookie はこの HTTP クライアントで行う全リクエストで共有されてほしいので、ここで設定している
            # 一方リクエストヘッダーはリクエスト先のリソース種類によって異なるためここでは設定せず、リクエスト毎に個別に設定する
            # (HTTP クライアントレベルで設定されたヘッダーは上書きや削除が難しそうなため)
            cookies=cookies,
            # リダイレクトを追跡する
            follow_redirects=True,
            # 可能な限り Chrome からのリクエストに偽装するため、HTTP/1.1 ではなく明示的に HTTP/2 で接続する
            http2=True,
        )

        # Twitter Web App (SPA) の HTML を取得
        # HTML リクエスト用のヘッダーに差し替えるのが重要
        twitter_web_app_html = self.httpx_client.get("https://x.com/home", headers=self.html_headers_dict)
        if twitter_web_app_html.status_code != 200:
            logging.error(
                f"[TwitterGraphQLAPI] Failed to fetch Twitter Web App HTML: {twitter_web_app_html.status_code}"
            )
            return ValueError(
                f"Challenge 情報の取得に失敗しました。Twitter Web App の HTML を取得できませんでした。(HTTP Error {twitter_web_app_html.status_code})",
            )
        twitter_web_app_html_text = twitter_web_app_html.text

        # BeautifulSoup を使って HTML をパース
        soup = BeautifulSoup(twitter_web_app_html_text, "html.parser")

        # HTML の meta タグに含まれる検証コードを取得
        meta_tag = soup.select_one('meta[name="twitter-site-verification"]')
        if meta_tag is None:
            logging.error(f"[TwitterGraphQLAPI] Failed to fetch verification code from Twitter Web App HTML")
            return ValueError(
                "Challenge 情報の取得に失敗しました。Twitter Web App の HTML から検証コードを取得できませんでした。",
            )
        verification_code = cast(str, meta_tag["content"])

        # HTML からチャレンジコードを取得
        challenge_code_match = re.search(r'"ondemand.s":"(\w+)"', twitter_web_app_html_text)
        if not challenge_code_match:
            logging.error(f"[TwitterGraphQLAPI] Failed to fetch challenge code from Twitter Web App HTML")
            return ValueError(
                "Challenge 情報の取得に失敗しました。Twitter Web App の HTML からチャレンジコードを取得できませんでした。",
            )
        challenge_code = challenge_code_match.group(1)

        # HTML からアニメーション SVG の outerHTML を取得
        challenge_animation_svg_codes = [str(svg) for svg in soup.select('svg[id^="loading-x"]')]

        # Challenge 情報を取得
        # JavaScript リクエスト用のヘッダーに差し替えるのが重要
        challenge_js_code_response = self.httpx_client.get(
            url=f"https://abs.twimg.com/responsive-web/client-web/ondemand.s.{challenge_code}a.js",
            headers=self.js_headers_dict,
        )
        if challenge_js_code_response.status_code != 200:
            logging.error(f"[TwitterGraphQLAPI] Failed to fetch challenge code from Twitter Web App HTML")
            return ValueError(
                f"Challenge 情報の取得に失敗しました。Twitter Web App のチャレンジコードからチャレンジコードを取得できませんでした。"
                f"(HTTP Error {challenge_js_code_response.status_code})"
            )
        challenge_js_code = challenge_js_code_response.text
        challenge_result = (
            verification_code,
            challenge_js_code,
            challenge_animation_svg_codes,
        )

        # solver_session = HTMLSession()

        headers["x-client-transaction-id"] = (
            "Cm9LTrTawONc60rPTfWVy/0ONFi9Y1VkW16PdOXH/s4BC+td+UXoEjFyNGLpCCTuQ5RS/giOVaMoWVfFOJ8PiK+YGVcbCQ"
        )
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
