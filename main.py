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
        self.root.geometry("430x220")

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

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 当前时间显示
        self.time_label = ttk.Label(main_frame, text="种子生成时间：")
        self.time_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # 表达式输入
        ttk.Label(main_frame, text="种子表达式：").grid(row=1, column=0, sticky=tk.W)
        expression_entry = ttk.Entry(main_frame, textvariable=self.expression_var, width=40)
        expression_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5)

        # 长度设置
        ttk.Label(main_frame, text="字符串长度：").grid(row=2, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(main_frame, from_=1, to=1024, textvariable=self.length_var, width=10)
        length_spinbox.grid(row=2, column=1, sticky=tk.W)
        length_spinbox.bind('<KeyRelease>', lambda e: self.generate_string())  # 绑定键盘输入事件
        length_spinbox.bind('<ButtonRelease>', lambda e: self.generate_string())  # 绑定鼠标点击事件

        # 滑条
        length_scale = ttk.Scale(
            main_frame,
            from_=10,
            to=100,
            variable=self.length_var,
            orient=tk.HORIZONTAL,
            command=lambda value: self.generate_string()
        )
        length_scale.grid(row=2, column=2, rowspan=1, sticky=tk.EW)

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
        result_entry.grid(row=4, column=0, columnspan=4, sticky=tk.EW, pady=10)
        result_entry.bind('<Double-Button-1>', self.copy_on_double_click)

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        # 配置网格布局权重
        main_frame.columnconfigure(1, weight=1)

    def generate_string(self):
        try:
            current_time = datetime.datetime.now()
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=f"种子生成时间：{time_str}")

            # 计算总秒数
            total_seconds = (
                        current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

            # 计算种子值
            context = {
                "math": math,
                "total_seconds": total_seconds,
                "hours": current_time.hour,
                "minutes": current_time.minute,
                "seconds": current_time.second
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