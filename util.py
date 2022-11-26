# -*- coding: utf-8 -*-

from os import path
from pathlib import PurePosixPath
import logging


def GetLogger(filename='crawler.log'):
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        level=logging.INFO)
    handler = logging.FileHandler(filename=filename, mode='w', encoding='utf-8')
    log = logging.getLogger(__name__)
    log.addHandler(handler)

    return log


class TaskPersistentManager:

    def __init__(self, file_name='finished_articles.txt'):
        self.file_name = path.abspath(path.join(PurePosixPath(), file_name))
        self.finish_article = []

    def _check_file_exist(self):
        return path.exists(self.file_name)

    def read(self):
        finish_article = []
        if not self._check_file_exist():
            return []
        with open(self.file_name, 'r', encoding='utf-8') as f:
            [finish_article.append(article_id.strip('\n')) for article_id in f.readlines()]

        return finish_article

    def write(self, articles: list):
        finished_article = self.read()
        finished_article.extend(articles)
        result = [f"{item}\n" for item in list(set(finished_article))]
        with open(self.file_name, 'w+', encoding='utf-8') as f:
            f.writelines(result)
