# -*- coding: utf-8 -*-
# @Time     : 2025/2/11
# @Author   : Mahiro
# @File     : settings.py
import json


class Settings:
    def __init__(self, logger):
        """程序默认设定"""
        self.local = "chinese"
        self.default_math_expression = "math.cos(total_seconds)"

    def load(self):
        """加载配置文件"""
        with open("data/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        self.local = config["local"]

    def save(self):
        """保存配置文件"""
        pass
