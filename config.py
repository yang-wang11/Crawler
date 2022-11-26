# -*- coding: utf-8 -*-

from yaml import load as yaml_loader
from yaml.loader import FullLoader


class ConfigLoader:

    def __init__(self, file_name="config.yaml"):
        self.file_name = file_name
        self.data = {}
        self._init()

    def _init(self):
        with open(self.file_name) as f:
            self.data = yaml_loader(f.read(), Loader=FullLoader)

    def _get(self, key_name):

        try:
            return self.data.get(key_name)
        except AttributeError:
            return {}

    def get_global_setting(self):
        global_setting = self._get("global_setting")

        return {
            "exclude_articles": global_setting.get("exclude_articles"),
            "include_articles": global_setting.get("include_articles"),
            "file_type": global_setting.get("file_type"),
        }

    def get_account_setting(self):
        account_setting = self._get("account_setting")

        return {
            "username": account_setting.get("username"),
            "password": account_setting.get("password"),
        }
