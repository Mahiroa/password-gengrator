import ctypes
import datetime
import math
import random
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class RandomStringGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("安全随机字符串生成器")
        self.root.geometry("550x400")

        # 初始化变量
        self.expression_var = tk.StringVar(value="math.cos(total_seconds)")
        self.length_var = tk.IntVar(value=12)
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_special = tk.BooleanVar(value=False)
        self.algorithm_var = tk.StringVar(value="secrets")
        self.result_var = tk.StringVar()

        # 创建UI组件
        self.create_widgets()
        self.generate_string()  # 初始生成
        self.center_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格布局权重
        main_frame.columnconfigure((1, 2), weight=1)
        main_frame.rowconfigure(6, weight=1)

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
        length_spinbox = ttk.Spinbox(main_frame, from_=1, to=1024, textvariable=self.length_var, width=10)
        length_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5)
        length_spinbox.bind('<KeyRelease>', lambda e: self.generate_string())
        length_spinbox.bind('<ButtonRelease>', lambda e: self.generate_string())

        # 滑条（调整为整数步进）
        length_scale = ttk.Scale(
            main_frame,
            from_=1,
            to=1024,
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

        # 结果显示（支持换行）
        self.result_label = ttk.Label(
            main_frame,
            textvariable=self.result_var,
            wraplength=400,
            anchor=tk.CENTER,
            font=('TkDefaultFont', 12),
            background='white',
            relief='solid',
            padding=5
        )
        self.result_label.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW, pady=10)
        self.result_label.bind('<Double-Button-1>', self.copy_on_double_click)

        # 按钮布局（居中）
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10, sticky=tk.NSEW)
        btn_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(btn_frame, text="怎么使用", command=self.show_help).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).grid(row=0, column=2, sticky=tk.EW)

    def toggle_algorithm(self, event=None):
        """切换算法时的界面更新"""
        if "secrets" in self.algorithm_var.get():
            self.expression_entry.config(state=tk.DISABLED)
            self.time_label.config(text="安全随机生成（不使用种子）")
        else:
            self.expression_entry.config(state=tk.NORMAL)
            self.generate_string()

    def generate_string(self):
        try:
            char_pool = self.get_char_pool()
            length = self.length_var.get()

            if self.algorithm_var.get().startswith("secrets"):
                # 使用加密安全随机生成
                self.generate_with_secrets(char_pool, length)
            else:
                # 使用传统种子随机生成
                self.generate_with_seed(char_pool, length)

            # 自动调整换行长度
            self.result_label.config(wraplength=self.root.winfo_width() - 40)

        except Exception as e:
            messagebox.showerror("错误", f"生成过程中发生错误：\n{str(e)}")

    def get_char_pool(self):
        """获取字符池并进行验证"""
        char_pool = []
        if self.include_upper.get():
            char_pool.extend(string.ascii_uppercase)
        if self.include_lower.get():
            char_pool.extend(string.ascii_lowercase)
        if self.include_special.get():
            char_pool.extend("!@#$%^&*()_+-=[]{}|;:',.<>?/`~")

        if not char_pool:
            messagebox.showerror("错误", "至少需要选择一种字符类型！")
            raise ValueError("Empty character pool")

        return char_pool

    def generate_with_secrets(self, char_pool, length):
        """使用加密安全算法生成"""
        self.result_var.set(
            ''.join(secrets.choice(char_pool) for _ in range(length))
        )

    def generate_with_seed(self, char_pool, length):
        """使用种子随机生成"""
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

        self.result_var.set(
            ''.join(random.choices(char_pool, k=length))
        )

    def center_window(self):
        """使窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def show_help(self):
        """显示帮助信息"""
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

    def copy_on_double_click(self, event):
        event.widget.selection_range(0, tk.END)
        self.copy_to_clipboard()

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_var.get())
        messagebox.showinfo("成功", "已复制到剪贴板！")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomStringGenerator(root)
    root.mainloop()
