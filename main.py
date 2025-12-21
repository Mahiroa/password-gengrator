# -*- coding: utf-8 -*-
# @Time     : 2025/9/15
# @Author   : Mahiro
# @File     : main.py

import sys
from src import pyside_version


class ClickRun:
    def __init__(self):
        pass

    def run_pyside_version(self):
        pyside_version.main()


if __name__ == "__main__":
    app = ClickRun()
    app.run_pyside_version()
