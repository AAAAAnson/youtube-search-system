"""
首次启动向导模块
"""

import customtkinter as ctk
import webbrowser
from tkinter import messagebox

from src.core.config_manager import ConfigManager
from src.utils.logger import Logger
from src.api.youtube_api import YouTubeAPI
from src.api.deepseek_api import DeepSeekAPI


class SetupWizard(ctk.CTk):
    """首次启动向导"""

    def __init__(self, config_manager: ConfigManager, logger: Logger):
        super().__init__()

        self.config_manager = config_manager
        self.logger = logger
        self.current_step = 0

        self.title("首次配置向导")
        self.geometry("600x500")

        # 设置主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 创建界面
        self._create_widgets()
        self._show_step(0)

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 步骤容器（将被替换）
        self.step_frame = ctk.CTkFrame(self.main_frame)
        self.step_frame.pack(fill="both", expand=True)

        # 底部按钮
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=20)

        self.prev_button = ctk.CTkButton(button_frame, text="上一步", command=self._prev_step, state="disabled")
        self.prev_button.pack(side="left", padx=10)

        self.next_button = ctk.CTkButton(button_frame, text="下一步", command=self._next_step)
        self.next_button.pack(side="right", padx=10)

    def _show_step(self, step):
        """显示指定步骤"""
        self.current_step = step

        # 清除当前步骤
        self.step_frame.destroy()
        self.step_frame = ctk.CTkFrame(self.main_frame)
        self.step_frame.pack(fill="both", expand=True)

        if step == 0:
            self._show_welcome()
        elif step == 1:
            self._show_youtube_setup()
        elif step == 2:
            self._show_deepseek_setup()

        # 更新按钮状态
        self.prev_button.configure(state="normal" if step > 0 else "disabled")
        self.next_button.configure(text="完成" if step == 2 else "下一步")

    def _show_welcome(self):
        """显示欢迎页面"""
        ctk.CTkLabel(
            self.step_frame,
            text="欢迎使用 YouTube 数据采集工具",
            font=("微软雅黑", 18, "bold")
        ).pack(pady=30)

        info_text = """
本工具可以帮助您：

• 批量采集 YouTube 视频数据
• 自动提取 KOL 联系方式
• 导出为 Excel 格式

在开始之前，需要配置 API Key

点击"下一步"继续
        """

        ctk.CTkLabel(
            self.step_frame,
            text=info_text,
            font=("微软雅黑", 12),
            justify="left"
        ).pack(pady=20)

    def _show_youtube_setup(self):
        """显示YouTube API配置页面"""
        ctk.CTkLabel(
            self.step_frame,
            text="配置 YouTube API Key",
            font=("微软雅黑", 16, "bold")
        ).pack(pady=20)

        # 教程链接
        tutorial_frame = ctk.CTkFrame(self.step_frame)
        tutorial_frame.pack(pady=10)

        ctk.CTkLabel(tutorial_frame, text="如何获取 API Key：").pack(side="left", padx=5)
        ctk.CTkButton(
            tutorial_frame,
            text="打开教程",
            command=lambda: webbrowser.open("https://console.cloud.google.com/"),
            width=100
        ).pack(side="left", padx=5)

        # API Key 输入
        ctk.CTkLabel(self.step_frame, text="输入 YouTube API Key:").pack(pady=10)
        self.youtube_key_entry = ctk.CTkEntry(self.step_frame, width=400)
        self.youtube_key_entry.pack(pady=5)

        # 备注名称
        ctk.CTkLabel(self.step_frame, text="备注名称（可选）:").pack(pady=10)
        self.youtube_name_entry = ctk.CTkEntry(self.step_frame, width=400)
        self.youtube_name_entry.pack(pady=5)
        self.youtube_name_entry.insert(0, "主账号")

        # 测试按钮
        ctk.CTkButton(
            self.step_frame,
            text="测试 API Key",
            command=self._test_youtube_key
        ).pack(pady=20)

    def _show_deepseek_setup(self):
        """显示DeepSeek API配置页面"""
        ctk.CTkLabel(
            self.step_frame,
            text="配置 DeepSeek API Key",
            font=("微软雅黑", 16, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            self.step_frame,
            text="用于智能提取 KOL 联系方式",
            font=("微软雅黑", 11)
        ).pack(pady=5)

        # 教程链接
        tutorial_frame = ctk.CTkFrame(self.step_frame)
        tutorial_frame.pack(pady=10)

        ctk.CTkLabel(tutorial_frame, text="如何获取 API Key：").pack(side="left", padx=5)
        ctk.CTkButton(
            tutorial_frame,
            text="打开官网",
            command=lambda: webbrowser.open("https://platform.deepseek.com/"),
            width=100
        ).pack(side="left", padx=5)

        # API Key 输入
        ctk.CTkLabel(self.step_frame, text="输入 DeepSeek API Key:").pack(pady=10)
        self.deepseek_key_entry = ctk.CTkEntry(self.step_frame, width=400)
        self.deepseek_key_entry.pack(pady=5)

        # 测试按钮
        ctk.CTkButton(
            self.step_frame,
            text="测试 API Key",
            command=self._test_deepseek_key
        ).pack(pady=20)

    def _test_youtube_key(self):
        """测试YouTube API Key"""
        api_key = self.youtube_key_entry.get().strip()

        if not api_key:
            messagebox.showwarning("提示", "请输入 API Key")
            return

        # 创建临时 YouTube API 对象进行测试
        youtube_api = YouTubeAPI(self.config_manager, self.logger)
        is_valid, message = youtube_api.test_api_key(api_key)

        if is_valid:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)

    def _test_deepseek_key(self):
        """测试DeepSeek API Key"""
        api_key = self.deepseek_key_entry.get().strip()

        if not api_key:
            messagebox.showwarning("提示", "请输入 API Key")
            return

        deepseek_api = DeepSeekAPI(api_key, self.logger)
        is_valid, message = deepseek_api.test_api_key()

        if is_valid:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)

    def _prev_step(self):
        """上一步"""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _next_step(self):
        """下一步/完成"""
        if self.current_step == 0:
            # 欢迎页 -> YouTube配置
            self._show_step(1)

        elif self.current_step == 1:
            # YouTube配置 -> DeepSeek配置
            youtube_key = self.youtube_key_entry.get().strip()

            if not youtube_key:
                messagebox.showwarning("提示", "请输入 YouTube API Key")
                return

            # 保存 YouTube API Key
            name = self.youtube_name_entry.get().strip() or "主账号"
            self.config_manager.add_youtube_api_key(youtube_key, name)

            self._show_step(2)

        elif self.current_step == 2:
            # DeepSeek配置 -> 完成
            deepseek_key = self.deepseek_key_entry.get().strip()

            if not deepseek_key:
                if not messagebox.askyesno("确认", "DeepSeek API Key 未配置，将无法提取联系方式。是否继续？"):
                    return

            # 保存 DeepSeek API Key
            if deepseek_key:
                self.config_manager.set_deepseek_api_key(deepseek_key)

            # 标记配置完成
            self.config_manager.set_first_run_completed()

            messagebox.showinfo("完成", "配置完成！即将进入主界面")
            self.destroy()
