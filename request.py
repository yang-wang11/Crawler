# -*- coding: utf-8 -*-

from cookie import Cookie
from copy import deepcopy
from config import ConfigLoader
import requests

common_header = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) "
                  "AppleWebKit/537.36 (KHTML, like Gecko)Chrome/81.0.4044.122 Safari/537.36"
}


class RequestManager:

    def __init__(self, logger=None):
        self.cookie = Cookie()
        self.log = logger
        self.conf_loader = ConfigLoader()

    def new_header(self):

        header = deepcopy(common_header)
        header.update({"Cookie": self.cookie.cookie_string})

        return header

    def request(self, method: str, url: str, headers: dict, params: dict, auth=False):

        self.log.info(f"请求{url}，请求参数：{params}")

        if auth:
            _account = self.conf_loader.get_account_setting()

            params.update({
                "cellphone": _account["username"],
                "password": _account["password"],
            })

        res = requests.request(method, url, headers=headers, json=params)

        if res.status_code != 200:
            raise Exception(f"接口请求出错，返回内容为：{res.content.decode()}")

        self.cookie.reset_cookie(res.headers['Set-Cookie'])

        return res
