import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import string
import datetime
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class RandomStringGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("随机字符串生成器")
        self.root.geometry("460x260")

        # 初始化变量
        self.expression_var = tk.StringVar(value="math.cos(total_seconds)")
        self.length_var = tk.IntVar(value=12)
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_special = tk.BooleanVar(value=False)
        self.result_var = tk.StringVar()

        # 创建UI组件
        self.create_widgets()
        self.generate_string()  # 初始生成
        self.center_window()  # 窗口居中

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格布局权重
        main_frame.columnconfigure((1, 2), weight=1)
        main_frame.rowconfigure(4, weight=1)

        # 当前时间显示（含毫秒）
        self.time_label = ttk.Label(main_frame, text="种子生成时间：")
        self.time_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)

        # 表达式输入
        ttk.Label(main_frame, text="种子表达式：").grid(row=1, column=0, sticky=tk.W)
        expression_entry = ttk.Entry(main_frame, textvariable=self.expression_var, width=40)
        expression_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5)

        # 长度设置
        ttk.Label(main_frame, text="字符串长度：").grid(row=2, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(main_frame, from_=1, to=1024, textvariable=self.length_var, width=10)
        length_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5)
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
        length_scale.grid(row=2, column=2, columnspan=2, sticky=tk.EW)

        # 字符类型选择
        ttk.Label(main_frame, text="包含字符类型：").grid(row=3, column=0, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="大写字母", variable=self.include_upper,
                        command=self.generate_string).grid(row=3, column=1, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="小写字母", variable=self.include_lower,
                        command=self.generate_string).grid(row=3, column=2, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="特殊字符", variable=self.include_special,
                        command=self.generate_string).grid(row=3, column=3, sticky=tk.W)

        # 结果显示
        result_entry = ttk.Entry(main_frame, textvariable=self.result_var, state='readonly', font=('TkDefaultFont', 12))
        result_entry.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW, pady=10)
        result_entry.bind('<Double-Button-1>', self.copy_on_double_click)

        # 按钮布局
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky=tk.EW)
        btn_frame.columnconfigure(0, weight=1)

        ttk.Button(btn_frame, text="怎么使用", command=self.show_help).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

    def generate_string(self):
        try:
            current_time = datetime.datetime.now()
            # 显示包含毫秒的时间
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.time_label.config(text=f"种子生成时间：{time_str}")

            # 计算总秒数（含毫秒）
            total_seconds = (
                    current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds()

            # 计算种子值
            context = {
                "math": math,
                "total_seconds": total_seconds,
                "hours": current_time.hour,
                "minutes": current_time.minute,
                "seconds": current_time.second,
                "microseconds": current_time.microsecond
            }

            seed_value = eval(self.expression_var.get(), context)
            seed = abs(seed_value)
            random.seed(seed)

            # 构建字符池
            char_pool = []
            if self.include_upper.get():
                char_pool.extend(string.ascii_uppercase)
            if self.include_lower.get():
                char_pool.extend(string.ascii_lowercase)
            if self.include_special.get():
                char_pool.extend("!@#$%^&*()_+-=[]{}|;:',.<>?/`~")

            if not char_pool:
                messagebox.showerror("错误", "至少需要选择一种字符类型！")
                return

            # 生成随机字符串
            length = self.length_var.get()
            if length < 1:
                messagebox.showerror("错误", "长度必须大于0！")
                return

            self.result_var.set(''.join(random.choices(char_pool, k=length)))

        except Exception as e:
            messagebox.showerror("错误", f"生成过程中发生错误：\n{str(e)}")

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