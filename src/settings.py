# -*- coding: utf-8 -*-
# @Time     : 2025/2/11
# @Author   : Mahiro
# @File     : settings.py
import json
import os


class Settings:
    def __init__(self, logger):
        """程序默认设定"""
        self.logger = logger
        self._config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.json")
        self._default_config = {
            "local": "chinese",
            "default_math_expression": "math.cos(total_seconds)",
            "window_title": "安全随机字符串生成器",
            "version": (1, 3, 3),
            "min_window_size": [400, 300],
            "default_window_size": [550, 400],
            "length_min": 1,
            "length_default": 16,
            "length_max": 1024,
            "default_algorithm": "secrets",
            "default_include_upper": True,
            "default_include_lower": True,
            "default_include_number": True,
            "default_include_special": False,
            "copy_highlight_enabled": True,
            "copy_bubble_enabled": True,
            "copy_highlight_color": "#FFFF99"
        }
        self._config = self._default_config.copy()
        self.load()

    def load(self):
        """加载配置文件"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                self._config.update(loaded_config)
            self._apply_config()
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            self._config = self._default_config.copy()
            self._apply_config()

    def save(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")

    def _apply_config(self):
        """应用配置"""
        for key, value in self._config.items():
            setattr(self, key, value)

    def update(self, key, value):
        """更新配置项"""
        self._config[key] = value
        setattr(self, key, value)
        self.save()

    def reload(self):
        """重新加载配置（热更新）"""
        self.load()
        self.logger.info("配置已热更新")
