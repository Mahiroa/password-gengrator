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
import webbrowser
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
        # 初始化设置，从配置中加载
        self._settings()

        # 创建主窗口
        self.root = root
        self.root.title(self.window_title)
        self.root.geometry(
            f"{self.default_window_size[0]}x{self.default_window_size[1]}"
        )
        self.root.minsize(self.min_window_size[0], self.min_window_size[1])

        # 初始化变量，从配置中加载默认值
        self.expression_var = tk.StringVar(value=self.default_math_expression)
        self.length_var = tk.IntVar(value=self.length_default)
        self.include_upper = tk.BooleanVar(value=SETTINGS.default_include_upper)
        self.include_lower = tk.BooleanVar(value=SETTINGS.default_include_lower)
        self.include_number = tk.BooleanVar(value=SETTINGS.default_include_number)
        self.include_special = tk.BooleanVar(value=SETTINGS.default_include_special)
        self.algorithm_var = tk.StringVar(value=SETTINGS.default_algorithm)
        self.result_var = tk.StringVar()

        # 创建UI组件
        self._create_widgets()
        self.generate_string()  # 初始生成
        self.center_window()

        # 绑定事件
        self.event_bind()

    def _settings(self):
        """初始化设置，从配置中加载"""
        self._load_settings()

    def _load_settings(self):
        """从配置对象加载设置"""
        # 应用配置
        self.window_title = self._generate_main_window_title(
            title=SETTINGS.window_title, version=tuple(SETTINGS.version)
        )
        self.min_window_size = tuple(SETTINGS.min_window_size)
        self.default_window_size = tuple(SETTINGS.default_window_size)
        self.default_math_expression = SETTINGS.default_math_expression
        self.length_min = SETTINGS.length_min
        self.length_default = SETTINGS.length_default
        self.length_max = SETTINGS.length_max

    def reload_settings(self):
        """重新加载配置"""
        SETTINGS.reload()
        self._load_settings()
        self.root.title(self.window_title)
        self.root.minsize(*self.min_window_size)
        logger.info("配置已热更新")

    def _generate_main_window_title(self, version: tuple, title: str) -> str:
        """生成主窗口标题"""
        window_title = f"{title} V{version[0]}.{version[1]}.{version[2]}.{''.join(random.choices(string.ascii_uppercase, k=8))}"
        return window_title

    def _create_widgets(self):
        """创建UI组件"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格布局权重
        main_frame.columnconfigure((1, 2), weight=1)
        main_frame.rowconfigure(5, weight=1)

        # 当前时间显示（含毫秒）
        self.time_label = ttk.Label(main_frame, text="种子生成时间: ")
        self.time_label.grid(row=0, column=0, columnspan=4, sticky=tk.W)

        # 表达式输入（条件显示）
        self.expression_label = ttk.Label(main_frame, text="种子表达式：")
        self.expression_entry = ttk.Entry(
            main_frame, textvariable=self.expression_var, width=40
        )
        self._update_expression_visibility()

        # 长度设置
        length_frame = ttk.Frame(main_frame)
        length_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W)
        ttk.Label(length_frame, text="字符串长度：").grid(row=0, column=0, sticky=tk.W)
        length_spinbox = ttk.Spinbox(
            length_frame,
            from_=self.length_min,
            to=self.length_max,
            textvariable=self.length_var,
            width=8,
        )
        length_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5)
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
        length_scale.grid(row=0, column=2, columnspan=2, sticky=tk.EW)

        # 绑定方向键控制长度
        self.root.bind("<Right>", self._handle_right_arrow)
        self.root.bind("<Left>", self._handle_left_arrow)
        self.root.bind("<Shift-Right>", self._handle_right_arrow_fast)
        self.root.bind("<Shift-Left>", self._handle_left_arrow_fast)
        length_scale.bind("<KeyRelease>", lambda e: self.generate_string())
        length_scale.bind("<ButtonRelease>", lambda e: self.generate_string())

        # 字符类型选择
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=3, column=0, columnspan=5, sticky=tk.NSEW)
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
        result_frame.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW, pady=10)
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

        # 按钮布局（居中）
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky=tk.NSEW)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)

        ttk.Button(btn_frame, text="设置", command=self.show_settings).grid(
            row=0, column=0, sticky=tk.EW
        )
        ttk.Button(btn_frame, text="怎么使用", command=self.show_help).grid(
            row=0, column=1, padx=5, sticky=tk.EW
        )
        ttk.Button(btn_frame, text="重新生成", command=self.generate_string).grid(
            row=0, column=2, padx=5, sticky=tk.EW
        )
        ttk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard).grid(
            row=0, column=3, sticky=tk.EW
        )

    def _update_expression_visibility(self):
        """根据算法类型更新种子表达式的可见性"""
        if self.algorithm_var.get().startswith("random"):
            self.expression_label.grid(row=1, column=0, sticky=tk.W)
            self.expression_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5)
            self.expression_entry.config(state=tk.NORMAL)
        else:
            self.expression_label.grid_remove()
            self.expression_entry.grid_remove()
            self.expression_entry.config(state=tk.DISABLED)

    def _handle_right_arrow(self, event):
        """处理右箭头键，增加长度"""
        current_value = self.length_var.get()
        if current_value < self.length_max:
            self.length_var.set(current_value + 1)
        self.generate_string()

    def _handle_right_arrow_fast(self, event):
        """处理Shift+右箭头键，快速增加长度"""
        current_value = self.length_var.get()
        if current_value < self.length_max:
            self.length_var.set(current_value + 10)
        self.generate_string()

    def _handle_left_arrow(self, event):
        """处理左箭头键，减少长度"""
        current_value = self.length_var.get()
        if current_value > self.length_min:
            self.length_var.set(current_value - 1)
        self.generate_string()

    def _handle_left_arrow_fast(self, event):
        """处理Shift+左箭头键，快速减少长度"""
        current_value = self.length_var.get()
        if current_value > self.length_min:
            self.length_var.set(current_value - 10)
        self.generate_string()

    def toggle_algorithm(self, event=None):
        """切换算法，更新UI显示"""
        self._update_expression_visibility()
        if self.algorithm_var.get().startswith("secrets"):
            self.time_label.config(text="安全随机生成（不使用种子）")
        else:
            self.time_label.config(text="种子生成时间: ")
            self.generate_string()

    def reload_settings(self):
        """重新加载配置"""
        SETTINGS.reload()
        self._load_settings()
        self.root.title(self.window_title)
        self.root.minsize(*self.min_window_size)
        
        # 更新默认值
        self.algorithm_var.set(SETTINGS.default_algorithm)
        self.include_upper.set(SETTINGS.default_include_upper)
        self.include_lower.set(SETTINGS.default_include_lower)
        self.include_number.set(SETTINGS.default_include_number)
        self.include_special.set(SETTINGS.default_include_special)
        
        # 更新UI
        self._update_expression_visibility()
        self.toggle_algorithm()
        logger.info("配置已热更新")

    def generate_string(self):
        try:
            # 更新算法UI显示
            self.toggle_algorithm()
            
            char_pool = self.get_char_pool()
            length = self._get_valid_length()
            generated = self._generate_with_selected_algorithm(char_pool, length)
            self._display_result(generated)
        except SyntaxError as e:
            self._handle_syntax_error(e)
        except Exception as e:
            messagebox.showerror("未知错误", f"生成过程中发生错误: \n{str(e)}")

    def _get_valid_length(self):
        """获取有效的长度值"""
        try:
            return self.format_length(self.length_var.get())
        except tk.TclError:
            self.length_var.set(self.length_default)
            return self.length_default

    def _generate_with_selected_algorithm(self, char_pool, length):
        """根据选择的算法生成随机字符串"""
        if self.algorithm_var.get().startswith("secrets"):
            return self._generate_secrets(char_pool, length)
        else:
            return self._generate_random_with_seed(char_pool, length)

    def _generate_secrets(self, char_pool, length):
        """使用secrets模块生成安全随机字符串"""
        return "".join(secrets.choice(char_pool) for _ in range(length))

    def _generate_random_with_seed(self, char_pool, length):
        """使用random模块和种子生成随机字符串"""
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
        return "".join(random.choices(char_pool, k=length))

    def _display_result(self, generated):
        """显示生成的结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, generated)
        self.result_text.config(state=tk.DISABLED)
        self.adjust_wrap_mode()

    def _handle_syntax_error(self, e):
        """处理语法错误"""
        if not self.expression_var.get():
            if messagebox.askyesno(
                    "表达式为空", "种子表达式为空，是否使用默认表达式？"
            ):
                self.expression_var.set(self.default_math_expression)
                self.generate_string()
        else:
            messagebox.showerror("语法错误", f"生成过程中发生错误：\n{str(e)}")

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
        """复制选中的文本或全部文本"""
        self.copy_to_clipboard()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def show_help(self):
        """显示帮助文档"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        help_file = os.path.join(current_dir, "help.html")
        if os.path.exists(help_file):
            webbrowser.open(f"file://{help_file}")
        else:
            messagebox.showinfo("帮助", "帮助文件不存在")

    def show_settings(self):
        """显示设置页面"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("450x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(settings_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 算法设置
        ttk.Label(main_frame, text="默认生成算法:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.default_algorithm_var = tk.StringVar(value=SETTINGS.default_algorithm)
        ttk.Radiobutton(main_frame, text="secrets (安全随机)", variable=self.default_algorithm_var, value="secrets").grid(row=1, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(main_frame, text="random (种子随机)", variable=self.default_algorithm_var, value="random").grid(row=2, column=0, sticky=tk.W, padx=20)
        
        # 默认字符类型设置
        ttk.Label(main_frame, text="默认包含字符类型:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(15, 10))
        self.default_upper_var = tk.BooleanVar(value=SETTINGS.default_include_upper)
        self.default_lower_var = tk.BooleanVar(value=SETTINGS.default_include_lower)
        self.default_number_var = tk.BooleanVar(value=SETTINGS.default_include_number)
        self.default_special_var = tk.BooleanVar(value=SETTINGS.default_include_special)
        
        ttk.Checkbutton(main_frame, text="大写字母", variable=self.default_upper_var).grid(row=4, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(main_frame, text="小写字母", variable=self.default_lower_var).grid(row=5, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(main_frame, text="阿拉伯数字", variable=self.default_number_var).grid(row=6, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(main_frame, text="特殊字符", variable=self.default_special_var).grid(row=7, column=0, sticky=tk.W, padx=20)
        
        # 复制设置
        ttk.Label(main_frame, text="复制功能设置:", font=("TkDefaultFont", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=(15, 10))
        self.copy_highlight_var = tk.BooleanVar(value=SETTINGS.copy_highlight_enabled)
        self.copy_bubble_var = tk.BooleanVar(value=SETTINGS.copy_bubble_enabled)
        
        ttk.Checkbutton(main_frame, text="复制时高亮文本", variable=self.copy_highlight_var).grid(row=9, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(main_frame, text="显示复制气泡提示", variable=self.copy_bubble_var).grid(row=10, column=0, sticky=tk.W, padx=20)
        
        # 保存按钮
        save_btn = ttk.Button(main_frame, text="保存设置", command=lambda: self._save_settings(settings_window))
        save_btn.grid(row=11, column=0, pady=20, sticky=tk.E)
        
        # 居中窗口
        settings_window.update_idletasks()
        width = settings_window.winfo_width()
        height = settings_window.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry(f"+{x}+{y}")

    def _save_settings(self, settings_window):
        """保存设置"""
        # 更新配置
        SETTINGS.update("default_algorithm", self.default_algorithm_var.get())
        SETTINGS.update("default_include_upper", self.default_upper_var.get())
        SETTINGS.update("default_include_lower", self.default_lower_var.get())
        SETTINGS.update("default_include_number", self.default_number_var.get())
        SETTINGS.update("default_include_special", self.default_special_var.get())
        SETTINGS.update("copy_highlight_enabled", self.copy_highlight_var.get())
        SETTINGS.update("copy_bubble_enabled", self.copy_bubble_var.get())
        
        # 保存到文件
        SETTINGS.save()
        
        # 重新加载设置
        self.reload_settings()
        
        # 关闭窗口
        settings_window.destroy()
        messagebox.showinfo("成功", "设置已保存！")

    def copy_to_clipboard(self):
        """复制文本到剪贴板，支持高亮和气泡提示"""
        try:
            selected = self.result_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected = self.result_text.get("1.0", tk.END).strip()

        if selected:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            
            # 复制时高亮效果
            if SETTINGS.copy_highlight_enabled:
                self._highlight_text()
            
            # 显示气泡提示
            if SETTINGS.copy_bubble_enabled:
                self._show_temporary_message("已复制到剪贴板！")

    def _highlight_text(self):
        """高亮显示结果文本"""
        # 保存原始背景色
        original_bg = self.result_text.cget("background")
        
        # 设置高亮背景色
        self.result_text.config(background=SETTINGS.copy_highlight_color)
        
        # 恢复原始背景色
        def restore_bg():
            self.result_text.config(background=original_bg)
        
        self.root.after(200, restore_bg)

    def _show_temporary_message(self, message, duration=1500):
        """显示临时消息提示"""
        # 创建临时提示窗口
        temp_window = tk.Toplevel(self.root)
        temp_window.overrideredirect(True)  # 去掉窗口边框
        temp_window.attributes("-topmost", True)  # 置顶显示
        temp_window.attributes("-alpha", 0.8)  # 设置透明度
        
        # 创建标签
        label = ttk.Label(temp_window, text=message, padding=(10, 5), background="#333", foreground="white", relief="solid")
        label.pack()
        
        # 计算位置（底部居中）
        temp_window.update_idletasks()
        x = (self.root.winfo_width() // 2) - (temp_window.winfo_width() // 2)
        y = self.root.winfo_height() - temp_window.winfo_height() - 20
        temp_window.geometry(f"+{x}+{y}")
        
        # 定时销毁窗口
        temp_window.after(duration, temp_window.destroy)

    def event_bind(self):
        """绑定事件"""
        self.root.bind("<Configure>", self.on_window_resize)

        # 绑定复制相关事件
        copy_events = ['<Control-c>', '<Control-a>', '<Double-Button-1>']
        for event in copy_events:
            self.root.bind(event, self.copy_on_double_click)
            self.result_text.bind(event, self.copy_on_double_click)

        # 绑定退出事件
        exit_events = ['<Escape>', '<q>', '<Control-q>', '<Alt-F4>']
        for event in exit_events:
            self.root.bind(event, self.exit_app)
            self.result_text.bind(event, self.exit_app)

        # 绑定焦点事件
        self._bind_focus_events()

    def _bind_focus_events(self):
        """为文本和输入框绑定焦点事件"""
        def bind_focus_recursive(widget):
            if isinstance(widget, (tk.Text, tk.Entry)):
                widget.bind('<FocusIn>', self.on_text_focus)
            for child in widget.winfo_children():
                bind_focus_recursive(child)
        
        bind_focus_recursive(self.root)

    def on_text_focus(self, event):
        # 文本框获得焦点时，将事件重新绑定到根窗口
        self.root.focus_set()

    def exit_app(self, event=None):
        self.root.quit()
