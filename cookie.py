# -*- coding: utf-8 -*-

import re


class Cookie:
    def __init__(self, cookie_string=None):
        self._cookies = {}
        if cookie_string:
            self.load_string_cookie(cookie_string)

    @property
    def cookie_string(self):
        """
        将对象的各属性转换成字符串形式的 Cookies
        Returns:
            字符串形式的 cookies，方便给 HTTP 请求时使用
        """
        return ';'.join([f'{k}={v}' for k, v in self._cookies.items()])

    def set_cookie(self, key, value):
        self._cookies[key] = value

    @staticmethod
    def list_to_dict(lis):
        """
        列表转换成字典的方法
        Args:
            lis: 列表内容
        Returns:
            转换后的字典
        """
        result = {}
        for ind in lis:
            try:
                ind = ind.split('=')
                result[ind[0]] = ind[1]
            except IndexError:
                continue
        return result

    def load_string_cookie(self, cookie_str):
        """
        从字符串中加载 Cookie 的方法（将字符串转换成字典形式）, 相当于 cookie_string 方法的逆反操作
        Args:
            cookie_str: 字符串形式的 Cookies，一般是从抓包请求中复制过来
                eg: gksskpitn=cc662cd7-0a39-430a-a603-a1c61d6f784f; LF_ID=1587783958277-6056470-8195597;
        Returns:
        """
        cookie_list = cookie_str.split(';')
        res = self.list_to_dict(cookie_list)
        self._cookies = {**self._cookies, **res}

    def reset_cookie(self, new_cookie):
        """
        从抓包返回的 Response Headers 中的 set-cookie 中提取 cookie 的方法
        Args:
            new_cookie: set-cookie 的值
        Returns:
        """
        set_cookie = re.sub(".xpires=.*?;", "", new_cookie)
        cookies_list = set_cookie.split(',')
        cookie_list = []
        for cookie in cookies_list:
            cookie_list.append(cookie.split(';')[0])
        res = self.list_to_dict(cookie_list)
        self._cookies = {**self._cookies, **res}

    def __repr__(self):
        return f'The cookies is : {self._cookies}'
