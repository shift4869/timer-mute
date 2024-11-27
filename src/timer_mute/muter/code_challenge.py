import pprint
import re
from datetime import datetime, timedelta
from logging import INFO, getLogger
from pathlib import Path
from typing import cast

import httpx
import orjson
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from timer_mute.muter.cookie_session_user_handler import CookieSessionUserHandler

logger = getLogger(__name__)
logger.setLevel(INFO)


class CodeChallenger:
    config_dict: dict
    screen_name: str

    CODE_CHALLENGE_CACHE_BASEPATH: Path = Path("./config/")
    CACHE_FILE_NAME: str = "{}_code_challenge.json"

    def __init__(self, config_dict: dict) -> None:
        if not isinstance(config_dict, dict):
            raise ValueError("config_dict must be dict.")
        self.config_dict = config_dict
        self.screen_name = config_dict["twitter_api_client"]["screen_name"]

    def get_cache_path(self) -> Path:
        cache_path = self.CODE_CHALLENGE_CACHE_BASEPATH / self.CACHE_FILE_NAME.format(self.screen_name)
        return cache_path

    def load_challenge_data(self) -> dict:
        cache_path = self.get_cache_path()
        if not cache_path.exists():
            return {}
        challenge_data = orjson.loads(cache_path.read_bytes())
        prev_fetched_date = datetime.fromisoformat(challenge_data["fetched_date"])
        now_date = datetime.now()
        if prev_fetched_date < now_date - timedelta(hours=1):
            # 前回取得時から1時間以上経っているならキャッシュを破棄
            return {}
        return challenge_data

    def save_challenge_data(self, challenge_data: dict) -> None:
        cache_path = self.get_cache_path()
        cache_path.write_bytes(orjson.dumps(challenge_data, option=orjson.OPT_INDENT_2))
        return

    def fetch_challenge_data(self) -> dict:
        logger.info("Fetching Challenge Code -> start")

        # https://github.com/tsukumijima/KonomiTV/blob/master/server/app/utils/TwitterGraphQLAPI.py
        # access_token_secret から Cookie を取得
        config_dict = self.config_dict["twitter_api_client"]
        cookies_dict: dict[str, str] = {
            "ct0": config_dict["ct0"],
            "auth_token": config_dict["auth_token"],
        }

        # RequestCookieJar オブジェクトに変換
        cookies = RequestsCookieJar()
        for key, value in cookies_dict.items():
            cookies.set(key, value)

        # 読み込んだ RequestCookieJar オブジェクトを CookieSessionUserHandler に渡す
        self.cookie_session_user_handler = CookieSessionUserHandler(cookies=cookies)
        # GraphQL API 用ヘッダー
        self.graphql_headers_dict = self.cookie_session_user_handler.get_graphql_api_headers()
        # HTML 用ヘッダー
        self.html_headers_dict = self.cookie_session_user_handler.get_html_headers()
        # JavaScript 用ヘッダー
        self.js_headers_dict = self.cookie_session_user_handler.get_js_headers(cross_origin=True)

        cookies_dict = self.cookie_session_user_handler.get_cookies_as_dict()
        cookies = httpx.Cookies()
        for name, value in cookies_dict.items():
            # ドメインを ".x.com" 、パスを "/" に設定しておくことが重要
            # でないと Cookie 更新時にちゃんと上書きできない
            # ただし "lang" キーだけは ".x.com" でなく "x.com" にする必要がある
            if name == "lang":
                cookies.set(name, value, domain="x.com", path="/")
            else:
                cookies.set(name, value, domain=".x.com", path="/")

        # httpx の非同期 HTTP クライアントのインスタンスを作成
        # 可能な限り Chrome からのリクエストに偽装するため独自のインスタンスを作成する
        self.httpx_client = httpx.Client(
            # Cookie を設定
            # Cookie はこの HTTP クライアントで行う全リクエストで共有されてほしいので、ここで設定している
            # 一方リクエストヘッダーはリクエスト先のリソース種類によって異なるためリクエスト毎に個別に設定する
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
                "Challenge 情報の取得に失敗しました。"
                f"Twitter Web App の HTML を取得できませんでした。(HTTP Error {twitter_web_app_html.status_code})",
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
                "Challenge 情報の取得に失敗しました。"
                "Twitter Web App の HTML からチャレンジコードを取得できませんでした。",
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
                "Challenge 情報の取得に失敗しました。"
                "Twitter Web App のチャレンジコードからチャレンジコードを取得できませんでした。"
                f"(HTTP Error {challenge_js_code_response.status_code})"
            )
        challenge_js_code = challenge_js_code_response.text
        challenge_result = {
            # "action": "init",
            "challenge": challenge_js_code,
            "verificationCode": verification_code,
            "anims": challenge_animation_svg_codes,
        }
        logger.info("Fetching Challenge Code -> done")
        return challenge_result

    def get_challenge_data(self) -> dict:
        # 外部から呼ばれる想定
        challenge_data = self.load_challenge_data()
        if challenge_data:
            # キャッシュが有効だった場合キャッシュを返す
            return challenge_data
        # キャッシュが無効、または初回実行だった場合fetch
        challenge_data = self.fetch_challenge_data()
        # キャッシュとして保存
        challenge_data["fetched_date"] = datetime.now().isoformat()
        self.save_challenge_data(challenge_data)
        return challenge_data


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    CONFIG_FILE_NAME = "./config/config.json"
    config = orjson.loads(Path(CONFIG_FILE_NAME).read_bytes())

    code_challenger = CodeChallenger(config)
    pprint.pprint(code_challenger)
    challenge_data = code_challenger.get_challenge_data()
    pprint.pprint(challenge_data)
