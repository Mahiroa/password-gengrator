import ctypes
import datetime
import logging
import math
import random
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox, font

# 设置logger格式
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

# 高DPI适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as _e:
    logger.exception(f"高DPI适配失败：{str(_e)}")


class RandomStringGenerator:
    def __init__(self, root):
        # 初始化设置，后续移动到一个json文件中实现程序配置热更新
        self.__settings()

        # 创建主窗口
        self.root = root
        self.root.title(self.window_title)
        self.root.geometry(f"{self.default_window_size[0]}x{self.default_window_size[1]}")
        self.root.minsize(self.min_window_size[0], self.min_window_size[1])

        # 初始化变量
        self.expression_var = tk.StringVar(value=self.default_math_expression)
        self.length_var = tk.IntVar(value=20)
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_special = tk.BooleanVar(value=False)
        self.algorithm_var = tk.StringVar(value="secrets")
        self.result_var = tk.StringVar()

        # 创建UI组件
        self.__create_widgets()
        self.generate_string()  # 初始生成
        self.center_window()
        self.root.bind('<Configure>', self.on_window_resize)

    def __settings(self):
        self.window_title = "安全随机字符串生成器"
        self.min_window_size = (400, 300)
        self.default_window_size = (550, 400)
        self.default_math_expression = "math.cos(total_seconds)"
        self.length_min = 8
        self.length_default = 20
        self.length_max = 256

    def __create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格布局权重
        main_frame.columnconfigure((1, 2), weight=1)
        main_frame.rowconfigure(5, weight=1)

        # 算法选择
        ttk.Label(main_frame, text="生成算法：").grid(row=0, column=0, sticky=tk.W)
        algorithm_combobox = ttk.Combobox(
            main_frame,
            textvariable=self.algorithm_var,
            values=["secrets (安全随机)", "random (种子随机)"],
            state="readonly",
            width=18
        )
        algorithm_combobox.grid(row=0, column=1, sticky=tk.W)
        algorithm_combobox.bind("<<ComboboxSelected>>", self.toggle_algorithm)

        # 当前时间显示（含毫秒）
        self.time_label = ttk.Label(main_frame, text="种子生成时间：")
        self.time_label.grid(row=1, column=0, columnspan=4, sticky=tk.W)

        # 表达式输入
        self.expression_label = ttk.Label(main_frame, text="种子表达式：")
        self.expression_label.grid(row=2, column=0, sticky=tk.W)
        self.expression_entry = ttk.Entry(main_frame, textvariable=self.expression_var, width=40)
        self.expression_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5)

        # 长度设置
        ttk.Label(main_frame, text="字符串长度：").grid(row=3, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(
            main_frame,
            from_=self.length_min,
            to=self.length_max,
            textvariable=self.length_var,
            width=10
        )
        length_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5)
        length_spinbox.bind('<KeyRelease>', lambda e: self.generate_string())
        length_spinbox.bind('<ButtonRelease>', lambda e: self.generate_string())

        # 滑条（调整为整数步进）
        length_scale = ttk.Scale(
            main_frame,
            from_=self.length_min,
            to=self.length_max,
            variable=self.length_var,
            orient=tk.HORIZONTAL,
            command=lambda val: self.length_var.set(round(float(val)))
        )
        length_scale.grid(row=3, column=2, columnspan=2, sticky=tk.EW)

        # 字符类型选择
        ttk.Label(main_frame, text="包含字符类型：").grid(row=4, column=0, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="大写字母", variable=self.include_upper,
                        command=self.generate_string).grid(row=4, column=1, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="小写字母", variable=self.include_lower,
                        command=self.generate_string).grid(row=4, column=2, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="特殊字符", variable=self.include_special,
                        command=self.generate_string).grid(row=4, column=3, sticky=tk.W)

        # 结果显示区域
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW, pady=10)

        self.result_text = tk.Text(
            result_frame,
            wrap=tk.NONE,
            font=('TkDefaultFont', 12),
            background='white',
            relief='solid',
            padx=5,
            pady=5,
            state=tk.NORMAL,
            exportselection=True,
            takefocus=0
        )
        self.result_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 滚动条
        scroll_x = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.configure(xscrollcommand=scroll_x.set)

        scroll_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scroll_y.set)

        # 绑定事件
        self.result_text.bind('<Double-Button-1>', self.copy_on_double_click)
        self.result_text.bind('<Key>', lambda e: 'break')

        # 按钮布局（居中）
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10, sticky=tk.NSEW)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        ttk.Button(btn_frame, text="怎么使用", command=self.show_help).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).grid(row=0, column=2, sticky=tk.EW)

    def toggle_algorithm(self, event):
        self.__useless_function(event)
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
                generated = ''.join(secrets.choice(char_pool) for _ in range(length))
            else:
                current_time = datetime.datetime.now()
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.time_label.config(text=f"种子生成时间：{time_str}")
                total_seconds = (
                        current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
                context = {
                    "math": math,
                    "total_seconds": total_seconds,
                    "hours": current_time.hour,
                    "minutes": current_time.minute,
                    "seconds": current_time.second,
                    "microseconds": current_time.microsecond
                }

                seed_value = eval(self.expression_var.get(), context)
                random.seed(abs(seed_value))
                generated = ''.join(random.choices(char_pool, k=length))

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, generated)
            self.adjust_wrap_mode()

        except Exception as e:
            messagebox.showerror("错误", f"生成过程中发生错误：\n{str(e)}")

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

        content = self.result_text.get('1.0', 'end-1c').strip()
        if not content:
            return

        current_font = font.Font(font=self.result_text['font'])
        text_width = current_font.measure(content)
        container_width = self.result_text.winfo_width()

        if text_width > container_width:
            self.result_text.configure(wrap=tk.WORD)
        else:
            self.result_text.configure(wrap=tk.NONE)

    def copy_on_double_click(self, event):
        self.__useless_function(event)
        if self.result_text.cget('wrap') == tk.NONE:
            self.result_text.tag_add(tk.SEL, '1.0', tk.END)
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
            selected = self.result_text.get('1.0', tk.END).strip()

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
        self.root.geometry(f'+{x}+{y}')

    @staticmethod
    def show_help():
        help_text = """欢迎使用随机字符串生成器！

使用方法：
1. 种子表达式：可以使用数学表达式，基于当前时间生成种子（支持math模块函数）
2. 字符串长度：通过滑块或输入框设置长度（1-1024）
3. 字符类型：勾选需要包含的字符类型
4. 重新生成：点击按钮或调整设置自动生成新字符串
5. 双击结果框或点击复制按钮将字符串复制到剪贴板

注意事项：
- 至少需要选择一种字符类型
- 种子表达式错误会导致生成失败
- 时间种子精确到毫秒级"""
        messagebox.showinfo("使用帮助", help_text)

    def copy_to_clipboard(self):
        try:
            selected = self.result_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected = self.result_text.get('1.0', tk.END).strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(selected)
        messagebox.showinfo("成功", "已复制到剪贴板！")

    def __useless_function(self, *args):
        """暂时使用该函数来处理事件绑定的参数问题：
        被绑定函数中要含有 event，但又无用。
        """
        pass


if __name__ == "__main__":
    root_window = tk.Tk()
    app = RandomStringGenerator(root_window)
    root_window.mainloop()
