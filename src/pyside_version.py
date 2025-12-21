# -*- coding: utf-8 -*-
# @Time     : 2025/12/22
# @Author   : Mahiro
# @File     : pyside_version.py

import ctypes
import datetime
import json
import logging
import math
import os
import random
import secrets
import string
from typing import Dict, Any

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QCheckBox, QSpinBox, QSlider,
    QGroupBox, QLineEdit, QRadioButton, QButtonGroup, QFrame,
    QDialog, QDialogButtonBox, QMessageBox
)

from src.settings import Settings

# 设置logger格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

SETTINGS = Settings(logger)

# 高DPI适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as _e:
    logger.exception(f"高DPI适配失败: {str(_e)}")


class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(400, 400)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 算法设置
        algorithm_group = QGroupBox("默认生成算法")
        algorithm_layout = QVBoxLayout()
        
        self.secrets_radio = QRadioButton("secrets (安全随机)")
        self.random_radio = QRadioButton("random (种子随机)")
        
        self.algorithm_group = QButtonGroup(self)
        self.algorithm_group.addButton(self.secrets_radio)
        self.algorithm_group.addButton(self.random_radio)
        
        algorithm_layout.addWidget(self.secrets_radio)
        algorithm_layout.addWidget(self.random_radio)
        algorithm_group.setLayout(algorithm_layout)
        layout.addWidget(algorithm_group)
        
        # 默认字符类型
        char_group = QGroupBox("默认包含字符类型")
        char_layout = QVBoxLayout()
        
        self.upper_check = QCheckBox("大写字母")
        self.lower_check = QCheckBox("小写字母")
        self.number_check = QCheckBox("阿拉伯数字")
        self.special_check = QCheckBox("特殊字符")
        
        char_layout.addWidget(self.upper_check)
        char_layout.addWidget(self.lower_check)
        char_layout.addWidget(self.number_check)
        char_layout.addWidget(self.special_check)
        char_group.setLayout(char_layout)
        layout.addWidget(char_group)
        
        # 复制设置
        copy_group = QGroupBox("复制功能设置")
        copy_layout = QVBoxLayout()
        
        self.highlight_check = QCheckBox("复制时高亮文本")
        self.bubble_check = QCheckBox("显示复制气泡提示")
        
        copy_layout.addWidget(self.highlight_check)
        copy_layout.addWidget(self.bubble_check)
        copy_group.setLayout(copy_layout)
        layout.addWidget(copy_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        """加载设置"""
        # 算法设置
        if SETTINGS.default_algorithm == "secrets":
            self.secrets_radio.setChecked(True)
        else:
            self.random_radio.setChecked(True)
        
        # 字符类型
        self.upper_check.setChecked(SETTINGS.default_include_upper)
        self.lower_check.setChecked(SETTINGS.default_include_lower)
        self.number_check.setChecked(SETTINGS.default_include_number)
        self.special_check.setChecked(SETTINGS.default_include_special)
        
        # 复制设置
        self.highlight_check.setChecked(SETTINGS.copy_highlight_enabled)
        self.bubble_check.setChecked(SETTINGS.copy_bubble_enabled)

    def save_settings(self):
        """保存设置"""
        # 算法设置
        algorithm = "secrets" if self.secrets_radio.isChecked() else "random"
        SETTINGS.update("default_algorithm", algorithm)
        
        # 字符类型
        SETTINGS.update("default_include_upper", self.upper_check.isChecked())
        SETTINGS.update("default_include_lower", self.lower_check.isChecked())
        SETTINGS.update("default_include_number", self.number_check.isChecked())
        SETTINGS.update("default_include_special", self.special_check.isChecked())
        
        # 复制设置
        SETTINGS.update("copy_highlight_enabled", self.highlight_check.isChecked())
        SETTINGS.update("copy_bubble_enabled", self.bubble_check.isChecked())
        
        # 保存到文件
        SETTINGS.save()

    def accept(self):
        """接受对话框"""
        self.save_settings()
        super().accept()


class PasswordGenerator(QMainWindow):
    """密码生成器主窗口"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        self.generate_password()

    def setup_ui(self):
        """设置UI"""
        # 设置窗口
        self.setWindowTitle("安全随机字符串生成器")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(self.get_stylesheet())
        
        # 主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 时间显示
        self.time_label = QLabel("安全随机生成（不使用种子）")
        self.time_label.setObjectName("timeLabel")
        self.main_layout.addWidget(self.time_label)
        
        # 表达式输入（条件显示）
        self.expression_frame = QFrame()
        self.expression_frame.setObjectName("expressionFrame")
        expression_layout = QHBoxLayout(self.expression_frame)
        expression_layout.setSpacing(10)
        
        expression_label = QLabel("种子表达式：")
        self.expression_edit = QLineEdit()
        self.expression_edit.setPlaceholderText("例如: math.cos(total_seconds)")
        
        expression_layout.addWidget(expression_label)
        expression_layout.addWidget(self.expression_edit)
        self.main_layout.addWidget(self.expression_frame)
        
        # 长度设置
        length_frame = QFrame()
        length_layout = QVBoxLayout(length_frame)
        length_layout.setSpacing(10)
        
        length_row = QHBoxLayout()
        length_label = QLabel("字符串长度：")
        self.length_spin = QSpinBox()
        self.length_spin.setRange(1, 1024)
        self.length_spin.setValue(16)
        
        length_row.addWidget(length_label)
        length_row.addWidget(self.length_spin)
        length_row.addStretch()
        
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(1, 1024)
        self.length_slider.setValue(16)
        
        length_layout.addLayout(length_row)
        length_layout.addWidget(self.length_slider)
        self.main_layout.addWidget(length_frame)
        
        # 字符类型选择
        char_frame = QFrame()
        char_layout = QHBoxLayout(char_frame)
        char_layout.setSpacing(15)
        
        char_label = QLabel("包含字符类型: ")
        self.upper_check = QCheckBox("大写字母")
        self.lower_check = QCheckBox("小写字母")
        self.number_check = QCheckBox("阿拉伯数字")
        self.special_check = QCheckBox("特殊字符")
        
        char_layout.addWidget(char_label)
        char_layout.addWidget(self.upper_check)
        char_layout.addWidget(self.lower_check)
        char_layout.addWidget(self.number_check)
        char_layout.addWidget(self.special_check)
        char_layout.addStretch()
        
        self.main_layout.addWidget(char_frame)
        
        # 结果显示
        result_frame = QFrame()
        result_frame.setObjectName("resultFrame")
        result_layout = QVBoxLayout(result_frame)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(150)
        self.result_text.setFont(QFont("Consolas", 12))
        
        result_layout.addWidget(self.result_text)
        self.main_layout.addWidget(result_frame)
        
        # 按钮布局
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        self.settings_btn = QPushButton("设置")
        self.help_btn = QPushButton("怎么使用")
        self.generate_btn = QPushButton("重新生成")
        self.copy_btn = QPushButton("复制到剪贴板")
        
        # 设置按钮样式
        self.settings_btn.setObjectName("settingsButton")
        self.help_btn.setObjectName("helpButton")
        self.generate_btn.setObjectName("generateButton")
        self.copy_btn.setObjectName("copyButton")
        
        # 设置按钮大小策略
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.help_btn)
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        
        self.main_layout.addWidget(button_frame)

    def setup_connections(self):
        """设置信号连接"""
        # 长度控件连接
        self.length_spin.valueChanged.connect(self.length_slider.setValue)
        self.length_slider.valueChanged.connect(self.length_spin.setValue)
        self.length_spin.valueChanged.connect(self.generate_password)
        self.length_slider.valueChanged.connect(self.generate_password)
        
        # 字符类型连接
        self.upper_check.stateChanged.connect(self.generate_password)
        self.lower_check.stateChanged.connect(self.generate_password)
        self.number_check.stateChanged.connect(self.generate_password)
        self.special_check.stateChanged.connect(self.generate_password)
        
        # 表达式连接
        self.expression_edit.textChanged.connect(self.generate_password)
        
        # 按钮连接
        self.settings_btn.clicked.connect(self.show_settings)
        self.help_btn.clicked.connect(self.show_help)
        self.generate_btn.clicked.connect(self.generate_password)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #333;
                background-color: #f5f5f5;
            }
            
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            
            QLabel {
                font-weight: 500;
            }
            
            #timeLabel {
                font-size: 12px;
                color: #666;
            }
            
            QLineEdit, QTextEdit, QSpinBox, QSlider {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            
            QCheckBox, QRadioButton {
                spacing: 8px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton#settingsButton {
                background-color: #2196F3;
            }
            
            QPushButton#settingsButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton#helpButton {
                background-color: #FF9800;
            }
            
            QPushButton#helpButton:hover {
                background-color: #F57C00;
            }
            
            QPushButton#generateButton {
                background-color: #9C27B0;
            }
            
            QPushButton#generateButton:hover {
                background-color: #7B1FA2;
            }
            
            QPushButton#copyButton {
                background-color: #00BCD4;
            }
            
            QPushButton#copyButton:hover {
                background-color: #0097A7;
            }
            
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                font-weight: 600;
            }
            
            QSlider::groove:horizontal {
                background-color: #ddd;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background-color: #4CAF50;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            
            QSpinBox {
                max-width: 80px;
            }
        """

    def load_settings(self):
        """从配置中加载设置"""
        # 加载算法设置
        self.algorithm = SETTINGS.default_algorithm
        
        # 加载字符类型设置
        self.upper_check.setChecked(SETTINGS.default_include_upper)
        self.lower_check.setChecked(SETTINGS.default_include_lower)
        self.number_check.setChecked(SETTINGS.default_include_number)
        self.special_check.setChecked(SETTINGS.default_include_special)
        
        # 加载表达式默认值
        self.expression_edit.setText(SETTINGS.default_math_expression)
        
        # 更新表达式可见性
        self.update_expression_visibility()
        
        # 更新时间标签
        if self.algorithm == "secrets":
            self.time_label.setText("安全随机生成（不使用种子）")
        else:
            self.time_label.setText("种子生成时间: ")

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # 重新加载设置
            SETTINGS.reload()
            self.load_settings()
            self.generate_password()
            QMessageBox.information(self, "成功", "设置已保存！")

    def show_help(self):
        """显示帮助文档"""
        import webbrowser
        current_dir = os.path.dirname(os.path.abspath(__file__))
        help_file = os.path.join(current_dir, "help.html")
        if os.path.exists(help_file):
            webbrowser.open(f"file://{help_file}")
        else:
            QMessageBox.information(self, "帮助", "帮助文件不存在")

    def update_expression_visibility(self):
        """根据算法类型更新表达式可见性"""
        if self.algorithm == "random":
            self.expression_frame.show()
        else:
            self.expression_frame.hide()

    def get_char_pool(self):
        """获取字符池"""
        char_pool = []
        if self.upper_check.isChecked():
            char_pool.extend(string.ascii_uppercase)
        if self.lower_check.isChecked():
            char_pool.extend(string.ascii_lowercase)
        if self.number_check.isChecked():
            char_pool.extend("0123456789")
        if self.special_check.isChecked():
            char_pool.extend("!@#$%^&*()_+-=[]{}|;:',.<>?/`~")
        
        if not char_pool:
            QMessageBox.critical(self, "错误", "至少需要选择一种字符类型！")
            return list(string.ascii_letters + string.digits)  # 默认返回所有字符
        
        return char_pool

    def generate_password(self):
        """生成密码"""
        try:
            char_pool = self.get_char_pool()
            length = self.length_spin.value()
            
            if self.algorithm == "secrets":
                generated = "".join(secrets.choice(char_pool) for _ in range(length))
            else:
                current_time = datetime.datetime.now()
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.time_label.setText(f"种子生成时间: {time_str}")
                
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
                
                expression = self.expression_edit.text() or "math.cos(total_seconds)"
                seed_value = eval(expression, context)
                random.seed(abs(seed_value))
                generated = "".join(random.choices(char_pool, k=length))
            
            self.result_text.setText(generated)
        except SyntaxError as e:
            QMessageBox.critical(self, "语法错误", f"生成过程中发生错误：\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "未知错误", f"生成过程中发生错误: \n{str(e)}")

    def copy_to_clipboard(self):
        """复制到剪贴板"""
        text = self.result_text.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # 复制时高亮效果
            if SETTINGS.copy_highlight_enabled:
                self.highlight_text()
            
            # 显示气泡提示
            if SETTINGS.copy_bubble_enabled:
                self.show_copy_bubble()

    def highlight_text(self):
        """高亮文本"""
        original_palette = self.result_text.palette()
        highlight_palette = QPalette(original_palette)
        highlight_palette.setColor(QPalette.Base, QColor("#FFFF99"))
        
        self.result_text.setPalette(highlight_palette)
        
        def restore_palette():
            self.result_text.setPalette(original_palette)
        
        QTimer.singleShot(200, restore_palette)

    def show_copy_bubble(self):
        """显示复制气泡提示"""
        bubble = QLabel("已复制到剪贴板！", self)
        bubble.setObjectName("copyBubble")
        bubble.setStyleSheet("""
            QLabel#copyBubble {
                background-color: rgba(51, 51, 51, 0.8);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 12px;
            }
        """)
        bubble.adjustSize()
        
        # 计算位置（右下角）
        x = self.width() - bubble.width() - 20
        y = self.height() - bubble.height() - 20
        bubble.move(x, y)
        
        bubble.show()
        
        def hide_bubble():
            bubble.hide()
            bubble.deleteLater()
        
        QTimer.singleShot(1500, hide_bubble)


def main():
    """主函数"""
    app = QApplication([])
    app.setStyle("Fusion")
    
    # 设置应用程序图标（如果有的话）
    # app.setWindowIcon(QIcon("path/to/icon.png"))
    
    window = PasswordGenerator()
    window.show()
    
    app.exec()


if __name__ == "__main__":
    main()
