# -*- coding: utf-8 -*-

import time
import pathlib
from os import path, mkdir
from request import RequestManager
from config import ConfigLoader
from util import TaskPersistentManager


class GeekCrawler:

    def __init__(self, logger=None):
        self.log = logger
        self.products = []
        self._login()
        self.request_manager = RequestManager(self.log)
        self.configLoader = ConfigLoader()
        self.persistent_manager = TaskPersistentManager()
        self.finished_articles = self.persistent_manager.read()

    def _login(self):
        """ 登录接口方法 """

        url = "https://account.geekbang.org/account/ticket/login"

        headers = self.request_manager.new_header()
        headers["Host"] = "account.geekbang.org"
        headers["Origin"] = "https://account.geekbang.org"

        params = {
            "country": 86,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1,
            "source": ""
        }

        self.request_manager.request(method="POST", url=url, headers=headers, params=params, auth=True)

        self.log.info('-' * 40)

    def refresh_auth(self):
        """ 用户认证接口方法 """

        now_time = int(time.time() * 1000)
        url = f"https://account.geekbang.org/serv/v1/user/auth?t={now_time}"

        headers = self.request_manager.new_header()
        headers["Host"] = "account.geekbang.org"
        headers["Origin"] = "https://time.geekbang.org"

        self.request_manager.request(method="GET", url=url, headers=headers)

        self.log.info('-' * 40)

    def get_products(self, _type='c1'):
        """ 商品列表（就是课程）的接口）方法 """

        url = "https://time.geekbang.org/serv/v3/learn/product"
        method = "POST"

        headers = self.request_manager.new_header()
        headers["Host"] = "time.geekbang.org"
        headers["Origin"] = "https://time.geekbang.org"

        params = {
            "desc": 'true',
            "expire": 1,
            "last_learn": 0,
            "learn_status": 0,
            "prev": 0,
            "size": 20,
            "sort": 1,
            "type": "",
            "with_learn_count": 1
        }

        res = self.request_manager.request(method=method, url=url, headers=headers, params=params)

        data = res.json().get('data', {})
        if data:
            self.products += self._parser_products(data, _type)
        else:
            self.log.info(f"此时 products 的数据为：{self.products}")
            raise Exception(f"课程列表接口没有获取到内容，请检查请求。返回结果为：{res.content.decode()}")

        self.log.info('-' * 40)

    def _parser_products(self, data, _type='c1'):
        """
        解析课程列表内容的方法（从中提取部分数据）
        Args:
            data: 课程相关信息，一般为接口返回的数据
            _type: 课程类型，c1 代表专栏，all 代表全部, 默认只获取专栏的内容
        Returns:
            解析后的结果，以列表形式
        """
        result = []
        keys = ['title', 'type', 'id']  # 定义要拿取的字段
        products = data.get('products', [])
        lists = data.get('list', [])

        for product in products:

            # 如果课程标题在需要排除的列表中，则跳过该课程
            if product.get('title', '') in self.configLoader.get_global_setting()["exclude_articles"]:
                continue

            # 如果没有在下载列表中的跳过该课程
            include_articles = self.configLoader.get_global_setting()["include_articles"]
            if include_articles and product.get('title', '') not in include_articles:
                continue

            new_product = {key: value for key, value in product.items() if key in keys}
            new_product['articles'] = []  # 定义文章列表（用来存储文章信息）
            new_product['article_ids'] = []  # 定义文章 ID 列表（用来存储文章 ID 信息） ）

            for pro in lists:
                if new_product['id'] == pro['pid']:
                    new_product['aid'] = pro['aid']

            if _type.lower() == 'all' or new_product['type'] == _type:
                result.append(new_product)

        return result

    def get_article(self, aid, product):
        """ 通过课程 ID 获取文章信息接口方法 """

        url = "https://time.geekbang.org/serv/v1/article"

        headers = self.request_manager.new_header()
        headers.update({
            "Host": "time.geekbang.org",
            "Origin": "https://time.geekbang.org",
        })

        params = {
            "id": aid,
            "include_neighbors": "true",
            "is_freelyread": "true"
        }

        res = self.request_manager.request(method="POST", url=url, headers=headers, params=params)

        data = res.json().get('data', {})
        if data:
            keys = ['article_content', 'article_title', 'id', 'audio_download_url']  # 定义要拿取的字段
            article = {key: value for key, value in data.items() if key in keys}
            self.save_to_file(
                product['title'],
                article['article_title'],
                article['article_content'],
                audio=article['audio_download_url'],
                file_type=self.configLoader.get_global_setting()["file_type"],
            )

            self.finished_articles.append(article['id'])  # 将该文章 ID 加入到遍历完成的列表中
            self.persistent_manager.write(self.finished_articles)
            product['cid'] = data['cid']
        else:
            self.log.info(f"此时 products 的数据为：{self.products}")
            raise Exception(f"获取文章信息接口没有获取到内容，请检查请求。返回结果为：{res.content.decode()}")

        self.log.info('-' * 40)

    def get_articles(self, pro):
        """ 获取文章列表接口方法 """

        url = "https://time.geekbang.org/serv/v1/column/articles"

        headers = self.request_manager.new_header()
        headers["Host"] = "time.geekbang.org"
        headers["Origin"] = "https://time.geekbang.org"

        params = {
            "cid": pro['id'],
            "size": 100,
            "prev": 0,
            "order": "earliest",
            "sample": "false"
        }

        res = self.request_manager.request(method="POST", url=url, headers=headers, params=params)

        if res.status_code != 200:
            self.log.info(f"此时 products 的数据为：{self.products}")
            raise Exception(f"获取文章列表接口请求出错，返回内容为：{res.json()}")

        data = res.json().get('data', {})
        if data:
            ids = []
            article_list = data.get('list', [])
            for article in article_list:
                ids.append(article['id'])
            pro['article_ids'] += ids  # 更新article_ids列表
        else:
            self.log.info(f"此时 products 的数据为：{self.products}")
            raise Exception(f"获取文章列表接口没有获取到内容，请检查请求。返回结果为：{res.json()}")

        self.log.info('-' * 40)

    @staticmethod
    def save_to_file(dir_name, filename, content, audio=None, file_type="md"):
        """
        将结果保存成文件的方法，保存在当前目录下
        Args:
            dir_name: 文件夹名称，如果不存在该文件夹则会创建文件夹
            filename: 文件名称，直接新建
            content: 需要保存的文本内容
            audio: 需要填入文件中的音频文件（一般为音频地址）
            file_type: 文档类型（需要保存什么类型的文档），默认保存为 Markdown 文档
        Returns:
        """

        dir_path = path.join(pathlib.PurePosixPath(), dir_name)
        if not path.isdir(dir_path):
            mkdir(dir_path)

        # 在 windows 中文件名不能包含('\','/','*','?','<','>','|') 字符
        filename = filename.replace('\\', '') \
            .replace('/', '') \
            .replace('*', 'x') \
            .replace('?', '') \
            .replace('<', '《') \
            .replace('>', '》') \
            .replace('|', '_') \
            .replace('\n', '') \
            .replace('\b', '') \
            .replace('\f', '') \
            .replace('\t', '') \
            .replace('\r', '')

        file_path = path.join(dir_path, f"{filename}.{file_type}")

        # 将所有数据写入文件中
        with open(file_path, 'w', encoding='utf-8') as f:
            if audio:
                audio_text = f'<audio title="{filename}" src="{audio}" controls="controls"></audio> \n'
                f.write(audio_text)
            f.write(content)
