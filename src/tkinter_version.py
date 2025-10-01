import ctypes
import datetime
import json
import logging
import math
import os
import random
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox, font

from src.settings import Settings

# 设置logger格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

SETTINGS = Settings(logger)

try:
    with open("../data/local.json") as f:
        LOCAL = json.load(f)
except Exception as __exp:
    os.makedirs("../data", exist_ok=True)
    __config = {"local": "chinese"}
    with open("../data/local.json", "w") as f:
        json.dump(__config, f)

# 高DPI适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as _e:
    logger.exception(f"高DPI适配失败: {str(_e)}")


class RandomStringGenerator:
    def __init__(self, root):
        # 初始化设置，后续移动到一个json文件中实现程序配置热更新
        self.__settings()

        # 创建主窗口
        self.root = root
        self.root.title(self.window_title)
        self.root.geometry(
            f"{self.default_window_size[0]}x{self.default_window_size[1]}"
        )
        self.root.minsize(self.min_window_size[0], self.min_window_size[1])
        self.bind_keys()

        # 初始化变量
        self.expression_var = tk.StringVar(value=self.default_math_expression)
        self.length_var = tk.IntVar(value=self.length_default)
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_number = tk.BooleanVar(value=True)
        self.include_special = tk.BooleanVar(value=False)
        self.algorithm_var = tk.StringVar(value="secrets")
        self.result_var = tk.StringVar()

        # 创建UI组件
        self.__create_widgets()
        self.generate_string()  # 初始生成
        self.center_window()
        self.root.bind("<Configure>", self.on_window_resize)

    def __settings(self):
        self.window_title = self.__generate_main_window_title(
            title="安全随机字符串生成器", version=(1, 2, 2)
        )
        self.min_window_size = (400, 300)
        self.default_window_size = (550, 400)
        self.default_math_expression = "math.cos(total_seconds)"
        self.length_min = 1
        self.length_default = 16
        self.length_max = 256

    @staticmethod
    def __generate_main_window_title(version: tuple, title: str) -> str:
        window_title = f"{title} V{version[0]}.{version[1]}.{version[2]}.DGZEUFXR"
        return window_title

    def __create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格布局权重
        main_frame.columnconfigure((1, 2), weight=1)
        main_frame.rowconfigure(5, weight=1)

        # 算法选择
        ttk.Label(main_frame, text="生成算法: ").grid(row=0, column=0, sticky=tk.W)
        algorithm_combobox = ttk.Combobox(
            main_frame,
            textvariable=self.algorithm_var,
            values=["secrets (安全随机)", "random (种子随机)"],
            state="readonly",
            width=15,
        )
        algorithm_combobox.grid(row=0, column=1, sticky=tk.W)
        algorithm_combobox.bind("<<ComboboxSelected>>", self.toggle_algorithm)

        # 当前时间显示（含毫秒）
        self.time_label = ttk.Label(main_frame, text="种子生成时间: ")
        self.time_label.grid(row=1, column=0, columnspan=4, sticky=tk.W)

        # 表达式输入
        self.expression_label = ttk.Label(main_frame, text="种子表达式：")
        self.expression_label.grid(row=2, column=0, sticky=tk.W)
        self.expression_entry = ttk.Entry(
            main_frame, textvariable=self.expression_var, width=40
        )
        self.expression_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5)
        self.toggle_algorithm(None)

        # 长度设置
        length_frame = ttk.Frame(main_frame)
        length_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W)
        ttk.Label(length_frame, text="字符串长度：").grid(row=3, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(
            length_frame,
            from_=self.length_min,
            to=self.length_max,
            textvariable=self.length_var,
            width=8,
        )
        length_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5)
        length_spinbox.bind("<KeyRelease>", lambda e: self.generate_string())
        length_spinbox.bind("<ButtonRelease>", lambda e: self.generate_string())
        length_scale = ttk.Scale(  # 滑条（调整为整数步进）
            length_frame,
            from_=self.length_min,
            to=self.length_max,
            variable=self.length_var,
            orient=tk.HORIZONTAL,
            command=lambda val: self.length_var.set(round(float(val))),
        )
        length_scale.grid(row=3, column=2, columnspan=2, sticky=tk.EW)

        self.root.bind("<Right>", self.right_arrow_binding)
        self.root.bind("<Left>", self.left_arrow_binding)
        self.root.bind("<Shift-Right>", self.right_arrow_binding_fast)
        self.root.bind("<Shift-Left>", self.left_arrow_binding_fast)
        length_scale.bind("<KeyRelease>", lambda e: self.generate_string())
        length_scale.bind("<ButtonRelease>", lambda e: self.generate_string())

        # 字符类型选择
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=4, column=0, columnspan=5, sticky=tk.NSEW)
        checkbox_frame.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Label(checkbox_frame, text="包含字符类型: ").pack(side=tk.LEFT)
        ttk.Checkbutton(
            checkbox_frame,
            text="大写字母",
            variable=self.include_upper,
            command=self.generate_string,
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            checkbox_frame,
            text="小写字母",
            variable=self.include_lower,
            command=self.generate_string,
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            checkbox_frame,
            text="阿拉伯数字",
            variable=self.include_number,
            command=self.generate_string,
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            checkbox_frame,
            text="特殊字符",
            variable=self.include_special,
            command=self.generate_string,
        ).pack(side=tk.LEFT)

        # 结果显示区域
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW, pady=10)
        self.result_text = tk.Text(
            result_frame,
            wrap=tk.NONE,
            font=("TkDefaultFont", 12),
            background="white",
            relief="solid",
            padx=5,
            pady=5,
            state=tk.NORMAL,
            exportselection=True,
            takefocus=0,
        )
        self.result_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 滚动条
        scroll_y = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.result_text.yview
        )
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scroll_y.set)

        # 绑定事件
        self.result_text.bind("<Double-Button-1>", self.copy_on_double_click)
        self.result_text.bind("<Key>", lambda e: "break")

        # 按钮布局（居中）
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10, sticky=tk.NSEW)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        ttk.Button(btn_frame, text="怎么使用", command=self.show_help).grid(
            row=0, column=0, sticky=tk.EW
        )
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).grid(
            row=0, column=1, padx=5, sticky=tk.EW
        )
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).grid(
            row=0, column=2, sticky=tk.EW
        )

    def right_arrow_binding(self, event):
        current_value = self.length_var.get()
        if current_value < self.length_max:
            self.length_var.set(current_value + 1)
        self.generate_string()

    def right_arrow_binding_fast(self, event):
        current_value = self.length_var.get()
        if current_value < self.length_max:
            self.length_var.set(current_value + 10)
        self.generate_string()

    def left_arrow_binding(self, event):
        current_value = self.length_var.get()
        if current_value > self.length_min:
            self.length_var.set(current_value - 1)
        self.generate_string()

    def left_arrow_binding_fast(self, event):
        current_value = self.length_var.get()
        if current_value > self.length_min:
            self.length_var.set(current_value - 10)
        self.generate_string()

    def toggle_algorithm(self, event):
        if "secrets" in self.algorithm_var.get():
            self.expression_entry.config(state=tk.DISABLED)
            self.time_label.config(text="安全随机生成（不使用种子）")
        else:
            self.expression_entry.config(state=tk.NORMAL)
            self.generate_string()

    def generate_string(self):
        try:
            char_pool = self.get_char_pool()
            try:
                length = self.format_length(self.length_var.get())
            except tk.TclError:
                self.length_var.set(self.length_default)
                length = self.length_default
            if self.algorithm_var.get().startswith("secrets"):
                generated = "".join(secrets.choice(char_pool) for _ in range(length))
            else:
                current_time = datetime.datetime.now()
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.time_label.config(text=f"种子生成时间: {time_str}")
                total_seconds = (
                        current_time
                        - current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
                context = {
                    "math": math,
                    "total_seconds": total_seconds,
                    "hours": current_time.hour,
                    "minutes": current_time.minute,
                    "seconds": current_time.second,
                    "microseconds": current_time.microsecond,
                }

                seed_value = eval(self.expression_var.get(), context)
                random.seed(abs(seed_value))
                generated = "".join(random.choices(char_pool, k=length))

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, generated)
            self.adjust_wrap_mode()
        except SyntaxError as e:
            if not self.expression_var.get():
                if messagebox.askyesno(
                        "表达式为空", "种子表达式为空，是否使用默认表达式？"
                ):
                    self.expression_var.set(self.default_math_expression)
                    self.generate_string()
            else:
                messagebox.showerror("语法错误", f"生成过程中发生错误：\n{str(e)}")
        except Exception as e:
            messagebox.showerror("未知错误", f"生成过程中发生错误: \n{str(e)}")

    def format_length(self, length):
        if length < self.length_min:
            self.length_var.set(self.length_min)
            length = self.length_min
        elif length > self.length_max:
            self.length_var.set(self.length_max)
            length = self.length_max
        return length

    def get_char_pool(self):
        char_pool = []
        if self.include_upper.get():
            char_pool.extend(string.ascii_uppercase)
        if self.include_lower.get():
            char_pool.extend(string.ascii_lowercase)
        if self.include_number.get():
            char_pool.extend("0123456789")
        if self.include_special.get():
            char_pool.extend("!@#$%^&*()_+-=[]{}|;:',.<>?/`~")

        if not char_pool:
            raise ValueError("至少需要选择一种字符类型！")

        return char_pool

    def on_window_resize(self, event):
        if event.widget == self.root:
            self.root.after(10, self.adjust_wrap_mode)

    def adjust_wrap_mode(self):
        self.result_text.configure(wrap=tk.NONE)
        self.result_text.update_idletasks()

        content = self.result_text.get("1.0", "end-1c").strip()
        if not content:
            return

        current_font = font.Font(font=self.result_text["font"])
        text_width = current_font.measure(content)
        container_width = self.result_text.winfo_width()

        if text_width > container_width:
            self.result_text.configure(wrap=tk.WORD)
        else:
            self.result_text.configure(wrap=tk.NONE)

    def copy_on_double_click(self, event):
        if self.result_text.cget("wrap") == tk.NONE:
            self.result_text.tag_add(tk.SEL, "1.0", tk.END)
            self.copy_to_clipboard()
            return "break"
        else:
            self.root.after(10, self.copy_selected)
            return None

    def copy_selected(self):
        try:
            start = self.result_text.index(tk.SEL_FIRST)
            end = self.result_text.index(tk.SEL_LAST)
            selected = self.result_text.get(start, end)
        except tk.TclError:
            selected = self.result_text.get("1.0", tk.END).strip()

        if selected:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            messagebox.showinfo("成功", "已复制到剪贴板！")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def show_help(self):
        help_text = f"""欢迎使用随机字符串生成器！

使用方法：
1. 安全随机：使用secrets模块生成安全随机字符串
2. 种子表达式：可以使用数学表达式，基于当前时间生成种子（支持math模块函数）
3. 字符串长度：通过滑块或输入框设置长度（{self.length_min}-{self.length_max}）
4. 字符类型：勾选需要包含的字符类型
5. 重新生成：点击按钮或调整设置自动生成新字符串
6. 双击结果框或点击复制按钮将字符串复制到剪贴板

注意事项：
- 至少需要选择一种字符类型
- 种子表达式错误会导致生成失败
- 时间种子精确到毫秒级"""
        messagebox.showinfo("使用帮助", help_text)

    def copy_to_clipboard(self):
        try:
            selected = self.result_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected = self.result_text.get("1.0", tk.END).strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(selected)
        messagebox.showinfo("成功", "已复制到剪贴板！")

    def bind_keys(self):
        """绑定键盘事件"""
        __keys = ['Escape', 'q', 'Control-q', 'Alt-F4']
        for key in __keys:
            self.root.bind(f"<{key}>", self.exit_app)

        # 为文本框添加焦点事件，当获得焦点时设置一个标志
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Text) or isinstance(widget, tk.Entry):
                widget.bind('<FocusIn>', self.on_text_focus)

    def on_text_focus(self, event):
        # 文本框获得焦点时，将事件重新绑定到根窗口
        self.root.focus_set()

    def exit_app(self, event=None):
        self.root.quit()