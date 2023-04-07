# coding: utf-8
import asyncio
import json
import random
import re
import sys
from dataclasses import dataclass
from logging import INFO, getLogger
from pathlib import Path
from time import sleep
from typing import ClassVar, Self

import pyppeteer
import requests
import requests.cookies
from requests.models import Request, Response
from requests_html import HTML, AsyncHTMLSession, Element

from timermute.muter.BearerToken import BearerToken
from timermute.muter.Cookies import Cookies
from timermute.muter.LocalStorage import LocalStorage

logger = getLogger(__name__)
logger.setLevel(INFO)


@dataclass(frozen=True)
class TwitterSession():
    """Twitterセッション

    通常の接続ではページがうまく取得できないので
    クッキーとローカルストレージを予め設定したページセッションを用いる
    """
    screen_name: str
    bearer_token: BearerToken
    cookies: Cookies             # 接続時に使うクッキー
    local_storage: LocalStorage  # 接続時に使うローカルストレージ
    session: ClassVar[AsyncHTMLSession]        # 非同期セッション
    loop: ClassVar[asyncio.AbstractEventLoop]  # イベントループ
    ct0: ClassVar[str]

    # 接続時に使用するヘッダー
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }
    # トップページ
    TOP_URL = "https://twitter.com/"
    # ログインページ
    LOGIN_URL = "https://twitter.com/i/flow/login"

    def __post_init__(self) -> None:
        # 引数チェック
        self._is_valid_args()

        # イベントループ設定
        # 一つのものを使い回す
        object.__setattr__(self, "loop", asyncio.new_event_loop())

        # クッキーとローカルストレージをセットしたセッションを保持する
        session = self.loop.run_until_complete(self._get_session())
        object.__setattr__(self, "session", session)

        # 正しくセッションが作成されたか確認
        if not self._is_valid_session():
            self.loop.close()
            raise ValueError("TwitterSession: session setting failed.")

    @property
    def headers(self) -> dict:
        headers = TwitterSession.HEADERS
        return headers

    def _is_valid_args(self) -> bool:
        """属性の型チェック

        Returns:
            bool: 問題なければTrue

        Raise:
            TypeError: 属性の型が不正な場合
        """
        # 属性型チェック
        if not isinstance(self.bearer_token, BearerToken):
            raise TypeError("bearer_token is not BearerToken, invalid TwitterSession.")
        if not isinstance(self.cookies, Cookies):
            raise TypeError("cookies is not Cookies, invalid TwitterSession.")
        if not isinstance(self.local_storage, LocalStorage):
            raise TypeError("local_storage is not LocalStorage, invalid TwitterSession.")
        return True

    def _is_valid_session(self) -> bool:
        """セッションの正当性チェック

        Returns:
            bool: 正しく following ページが取得できたらTrue, 不正ならFalse
        """
        url = self.TOP_URL
        response: Response = self.page_get(url)
        response.raise_for_status()
        html: HTML = response.html

        # 取得結果の確認
        try:
            div_tags: list[Element] = html.find("div")
            div_tag = [dt for dt in div_tags if "アカウントメニュー" in dt.attrs.get("aria-label", "")][0]
            img_tags: list[Element] = div_tag.find("img")
            result = [self.screen_name == it.attrs.get("alt", "") for it in img_tags]
            return any(result)
        except Exception as e:
            pass
        return False

    async def _get_session(self) -> AsyncHTMLSession:
        """セッション取得

        クッキーとローカルストレージを設定したpyppeteerブラウザに紐づける

        Returns:
            AsyncHTMLSession: 非同期セッション
        """
        url = self.TOP_URL

        # クッキーとローカルストレージをセットしたpyppeteerブラウザを設定する
        browser = await pyppeteer.launch(headless=True)
        page = await browser.newPage()
        await page.goto(url)

        # ローカルストレージをセットする
        javascript_func1 = 'localStorage.setItem(`{}`, `{}`);'
        for key, value in self.local_storage.local_storage.items():
            await page.evaluate(javascript_func1.format(key, value), force_expr=True)

        # クッキーをセットする
        for c in self.cookies.cookies:
            if c.name == "ct0":
                object.__setattr__(self, "ct0", c.value)
            d = {
                "name": c.name,
                "value": c.value,
                "expires": c.expires,
                "path": c.path,
                "domain": c.domain,
                "secure": bool(c.secure),
                "httpOnly": bool(c._rest["HttpOnly"])
            }
            await page.setCookie(d)

        # ローカルストレージとクッキーセット後にページ遷移できるか確認
        # url = self.FOLLOWING_TEMPLATE.format(self.username.name)
        # await asyncio.gather(
        #     page.goto(url),
        #     page.waitForNavigation()
        # )

        # AsyncHTMLSession を作成してブラウザに紐づける
        session = AsyncHTMLSession()
        session._browser = browser

        return session

    def prepare(self) -> Response:
        """セッションを使う準備

        リファラの関係？でTOPページを取得してレンダリングを試みる
        """
        response: Response = self.page_get(self.TOP_URL)
        # await response.html.arender()
        return response

    async def async_request(
        self,
        request_url: str,
        params: dict = {},
        method: str = "GET",
        headers: dict = {},
        cookies: requests.cookies.RequestsCookieJar = {}
    ):
        request_func = None
        match method:
            case "GET":
                request_func = self.session.get
            case "POST":
                request_func = self.session.post
            case _:
                raise ValueError('async_request argument "method" is not in ["GET", "POST"]')

        headers = headers or TwitterSession.HEADERS
        cookies = cookies or self.cookies.cookies
        response: Response = await request_func(
            request_url,
            params=params,
            headers=headers,
            cookies=cookies
        )
        response.raise_for_status()
        return response

    async def async_page_request(self, request_url: str, params: dict = {}, method: str = "GET"):
        response = await self.async_request(
            request_url,
            params,
            method,
            TwitterSession.HEADERS,
            self.cookies.cookies
        )
        await response.html.arender()
        return response

    def page_request(self, request_url: str, params: dict = {}, method: str = "GET"):
        response = self.loop.run_until_complete(
            self.async_page_request(request_url, params, method)
        )
        return response

    def page_get(self, request_url: str, params: dict = {}):
        method: str = "GET"
        response = self.page_request(request_url, params, method)
        return response

    async def async_api_request(self, request_url: str, params: dict = {}, method: str = "GET"):
        headers = TwitterSession.HEADERS
        headers["authorization"] = self.bearer_token.bearer_token
        headers["content-type"] = "application/x-www-form-urlencoded"
        headers["x-csrf-token"] = self.ct0
        response = await self.async_request(
            request_url,
            params,
            method,
            headers,
            self.cookies.cookies
        )
        return response

    def api_request(self, request_url: str, params: dict = {}, method: str = "GET"):
        response = self.loop.run_until_complete(
            self.async_api_request(request_url, params, method)
        )
        return response

    def api_get(self, request_url: str, params: dict = {}):
        method: str = "GET"
        response = self.api_request(request_url, params, method)
        return response

    def api_post(self, request_url: str, params: dict = {}):
        method: str = "POST"
        response = self.api_request(request_url, params, method)
        return response

    @classmethod
    async def _response_listener(cls, r: Request) -> None:
        # レスポンス監視用リスナー
        if "client_event.json" in r.url.lower():
            if BearerToken.is_valid(r.headers):
                BearerToken.save(r.headers)

    @classmethod
    async def get_authorized_token(cls) -> dict:
        """認証済みの Bearer トークン, クッキー, ローカルストレージを取得する

        ブラウザを起動してユーザに認証を求め、そのときの通信をキャプチャする

        Returns:
            _type_: _description_
        """
        login_url = TwitterSession.LOGIN_URL

        browser = await pyppeteer.launch(headless=False)
        page = await browser.newPage()
        logger.info("Login flow start.")

        page.on(
            # "response",
            "request",
            lambda response: asyncio.ensure_future(
                TwitterSession._response_listener(response)
            )
        )

        # 初期化
        bsp = Path(BearerToken.TWITTER_BEARER_TOKEN_PATH)
        bsp.unlink(missing_ok=True)

        # ログインページに遷移
        await asyncio.gather(
            page.goto(login_url),
            page.waitForNavigation()
        )
        content = await page.content()
        cookies = await page.cookies()
        logger.info("Twitter Login Page loaded.")

        # ツイッターログインが完了したかどうかユーザに問い合せる
        async def ainput(string: str) -> str:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda s=string: sys.stdout.write(s + ' ')
            )
            return await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
        user_response = await ainput("Twitter Login complete ? (y,n):")

        # TODO::ツイッターログインが成功かどうか調べる
        content = await page.content()
        cookies = await page.cookies()

        if not bsp.is_file():
            raise ValueError("Getting Bearer token is failed.")

        logger.info("Twitter login is success.")

        # Bearer トークンが取得できたことを確認
        # 正常ならば self._response_listener にてキャプチャされている
        # キャプチャされたファイルを元に BearerToken オブジェクトを作成
        bearer_token = BearerToken.create()
        bearer_token_str = bearer_token.bearer_token
        logger.info("Getting bearer_token is success.")

        # クッキー情報が取得できたことを確認
        if not cookies:
            raise ValueError("Getting cookies is failed.")

        # クッキー情報をファイルに保存する
        Cookies.save(cookies)
        cookies = Cookies.create()
        logger.info("Getting cookies is success.")

        # ローカルストレージ情報を取り出す
        localstorage_get_js = """
            function allStorage() {
                var values = [],
                    keys = Object.keys(localStorage),
                    i = keys.length;

                while ( i-- ) {
                    values.push( keys[i] + ' : ' + localStorage.getItem(keys[i]) );
                }

                return values;
            }
            allStorage()
        """
        RETRY_NUM = 5
        local_storage_list: list[str] = []
        for _ in range(RETRY_NUM):
            local_storage_list = await page.evaluate(localstorage_get_js, force_expr=True)
            if local_storage_list:
                break
        else:
            # ローカルストレージ情報が取得できたことを確認
            # 空白もあり得る？
            # raise ValueError("Getting local_storage is failed.")
            pass

        # 取得したローカルストレージ情報を保存
        LocalStorage.save(local_storage_list)
        local_storage = LocalStorage.create()
        logger.info("Getting local_storage is success.")

        return bearer_token, cookies, local_storage

    @classmethod
    def create(cls, screen_name) -> Self:
        # 以前に接続した時のクッキーとローカルストレージのファイルが存在しているならば
        RETRY_NUM = 5
        for i in range(RETRY_NUM):
            try:
                bearer_token = BearerToken.create()
                cookies = Cookies.create()
                local_storage = LocalStorage.create()
                twitter_session = TwitterSession(screen_name, bearer_token, cookies, local_storage)
                logger.info("Getting Twitter session -> done")
                return twitter_session
            except FileNotFoundError as e:
                logger.info(f"No exist Cookies and LocalStorage file.")
                break
            except Exception as e:
                logger.info(f"Cookies and LocalStorage loading retry ... ({i+1}/{RETRY_NUM}).")
        else:
            logger.info(f"Retry num is exceed RETRY_NUM={RETRY_NUM}.")

        # クッキーとローカルストレージのファイルがない場合
        # または有効なセッションが取得できなかった場合
        # 認証してクッキーとローカルストレージの取得を試みる
        loop = asyncio.new_event_loop()
        token_tuple = loop.run_until_complete(
            TwitterSession.get_authorized_token()
        )
        bearer_token, cookies, local_storage = token_tuple
        loop.close()
        twitter_session = TwitterSession(screen_name, bearer_token, cookies, local_storage)
        logger.info("Getting Twitter session -> done")
        return twitter_session


if __name__ == "__main__":
    import configparser
    import logging.config

    logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
    CONFIG_FILE_NAME = "./config/config.ini"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME, encoding="utf8")

    try:
        screen_name = config["twitter_noapi"]["screen_name"]
        bearer_token = config["twitter_noapi"]["bearer_token"]
        twitter_session = TwitterSession.create(screen_name, bearer_token)
        response = twitter_session.prepare()
        print(response.text)
    except Exception as e:
        logger.exception(e)
