# -*- coding: utf-8 -*-
# @Time     : 2025/9/15
# @Author   : Mahiro
# @File     : main.py

from src import tkinter_version


class CLASSNAME:
    def __init__(self):
        pass

    def run_tkinter_version(self):
        __window = tkinter_version.tk.Tk()
        tkinter_version.RandomStringGenerator(__window)
        __window.mainloop()


if __name__ == "__main__":
    app = CLASSNAME()
    app.run_tkinter_version()
