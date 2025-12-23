"""
API 管理窗口模块
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.core.config_manager import ConfigManager
from src.utils.logger import Logger
from src.utils.helpers import import_api_keys
from src.api.youtube_api import YouTubeAPI
from src.api.deepseek_api import DeepSeekAPI


class APIManagerWindow(ctk.CTkToplevel):
    """API 管理窗口"""

    def __init__(self, parent, config_manager: ConfigManager, logger: Logger):
        super().__init__(parent)

        self.config_manager = config_manager
        self.logger = logger

        self.title("API Key 管理")
        self.geometry("700x600")

        self._create_widgets()
        self._load_api_keys()

    def _create_widgets(self):
        """创建界面组件"""
        # YouTube API Keys 区域
        youtube_frame = ctk.CTkFrame(self)
        youtube_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(youtube_frame, text="YouTube API Keys", font=("微软雅黑", 14, "bold")).pack(pady=10)

        # API Keys 列表
        self.keys_text = ctk.CTkTextbox(youtube_frame, width=650, height=200)
        self.keys_text.pack(padx=10, pady=10)

        # 按钮区域
        button_frame = ctk.CTkFrame(youtube_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="单个添加", command=self._add_single_key).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="批量导入", command=self._import_keys).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="刷新列表", command=self._load_api_keys).pack(side="left", padx=5)

        # DeepSeek API Key 区域
        deepseek_frame = ctk.CTkFrame(self)
        deepseek_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(deepseek_frame, text="DeepSeek API Key", font=("微软雅黑", 14, "bold")).pack(pady=10)

        key_input_frame = ctk.CTkFrame(deepseek_frame)
        key_input_frame.pack(pady=10)

        self.deepseek_entry = ctk.CTkEntry(key_input_frame, width=400)
        self.deepseek_entry.pack(side="left", padx=10)
        self.deepseek_entry.insert(0, self.config_manager.get_deepseek_api_key())

        ctk.CTkButton(key_input_frame, text="测试", command=self._test_deepseek_key).pack(side="left", padx=5)
        ctk.CTkButton(key_input_frame, text="保存", command=self._save_deepseek_key).pack(side="left", padx=5)

        # 底部按钮
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(bottom_frame, text="关闭", command=self.destroy).pack()

    def _load_api_keys(self):
        """加载API Keys列表"""
        self.keys_text.delete("1.0", "end")
        api_keys = self.config_manager.get_youtube_api_keys(enabled_only=False)

        if not api_keys:
            self.keys_text.insert("1.0", "暂无 API Key，请添加\n")
            return

        for i, key_info in enumerate(api_keys, 1):
            status = "✓" if key_info.get('enabled', True) else "✗"
            quota_used = key_info.get('quota_used', 0)
            quota_total = key_info.get('quota_total', 10000)
            name = key_info.get('name', 'Unknown')
            key_preview = key_info['key'][:20] + "..."

            line = f"{status} {i}. {name} | {key_preview} | 配额: {quota_used}/{quota_total}\n"
            self.keys_text.insert("end", line)

    def _add_single_key(self):
        """添加单个API Key"""
        dialog = ctk.CTkInputDialog(text="请输入 YouTube API Key:", title="添加 API Key")
        api_key = dialog.get_input()

        if api_key:
            name_dialog = ctk.CTkInputDialog(text="请输入备注名称（可选）:", title="备注名称")
            name = name_dialog.get_input() or f"API Key {len(self.config_manager.get_youtube_api_keys()) + 1}"

            # 测试 API Key
            if messagebox.askyesno("确认", "是否测试 API Key 有效性？"):
                youtube = YouTubeAPI(self.config_manager, self.logger)
                is_valid, message = youtube.test_api_key(api_key)

                if not is_valid:
                    messagebox.showerror("错误", f"API Key 无效: {message}")
                    return

                messagebox.showinfo("成功", message)

            # 添加
            if self.config_manager.add_youtube_api_key(api_key, name):
                messagebox.showinfo("成功", "API Key 已添加")
                self._load_api_keys()
            else:
                messagebox.showwarning("提示", "API Key 已存在")

    def _import_keys(self):
        """批量导入API Keys"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("所有支持格式", "*.csv;*.txt;*.json"),
                ("CSV文件", "*.csv"),
                ("TXT文件", "*.txt"),
                ("JSON文件", "*.json")
            ]
        )

        if file_path:
            keys_data = import_api_keys(file_path)

            if not keys_data:
                messagebox.showerror("错误", "文件格式错误或没有有效的 API Key")
                return

            result = self.config_manager.batch_import_youtube_keys(keys_data)
            messagebox.showinfo(
                "导入完成",
                f"成功: {result['success']} 个\n失败: {result['failed']} 个"
            )
            self._load_api_keys()

    def _save_deepseek_key(self):
        """保存DeepSeek API Key"""
        api_key = self.deepseek_entry.get().strip()

        if api_key:
            self.config_manager.set_deepseek_api_key(api_key)
            messagebox.showinfo("成功", "DeepSeek API Key 已保存")
        else:
            messagebox.showwarning("提示", "请输入 API Key")

    def _test_deepseek_key(self):
        """测试DeepSeek API Key"""
        api_key = self.deepseek_entry.get().strip()

        if not api_key:
            messagebox.showwarning("提示", "请输入 API Key")
            return

        deepseek = DeepSeekAPI(api_key, self.logger)
        is_valid, message = deepseek.test_api_key()

        if is_valid:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
