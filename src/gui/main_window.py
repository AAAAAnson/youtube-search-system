"""
主窗口模块
YouTube 数据采集工具的主界面
"""

import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.core.cache_manager import CacheManager
from src.core.data_collector import DataCollector
from src.api.youtube_api import YouTubeAPI
from src.api.deepseek_api import DeepSeekAPI
from src.utils.excel_exporter import ExcelExporter
from src.utils.logger import Logger


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self, config_manager: ConfigManager, cache_manager: CacheManager, logger: Logger):
        super().__init__()

        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.logger = logger

        # 窗口配置
        self.title("YouTube 数据采集工具 v1.0.0")
        self.geometry("900x700")

        # 设置主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 数据
        self.collected_data = []
        self.is_collecting = False
        self.collector_thread = None

        # 创建界面
        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部菜单栏
        menu_frame = ctk.CTkFrame(self, height=50)
        menu_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(menu_frame, text="API管理", width=100, command=self._open_api_manager).pack(side="left", padx=5)
        ctk.CTkButton(menu_frame, text="查看日志", width=100, command=self._view_logs).pack(side="left", padx=5)
        ctk.CTkButton(menu_frame, text="清除缓存", width=100, command=self._clear_cache).pack(side="left", padx=5)

        # 搜索配置区域
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=10, pady=5)

        # 关键词
        ctk.CTkLabel(config_frame, text="搜索关键词:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.keyword_entry = ctk.CTkEntry(config_frame, width=300)
        self.keyword_entry.grid(row=0, column=1, padx=10, pady=10)
        self.keyword_entry.insert(0, self.config_manager.get_last_search_keyword())

        # 最大结果数
        ctk.CTkLabel(config_frame, text="最大结果数:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.max_results_combo = ctk.CTkComboBox(
            config_frame,
            values=["50", "100", "200", "500", "1000"],
            width=150
        )
        self.max_results_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.max_results_combo.set(str(self.config_manager.get_last_max_results()))

        # 排序方式
        ctk.CTkLabel(config_frame, text="排序方式:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.sort_combo = ctk.CTkComboBox(
            config_frame,
            values=["相关性", "发布日期", "观看次数", "评分"],
            width=150
        )
        self.sort_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.sort_combo.set("相关性")

        # 可选字段
        self.show_channel_link_var = ctk.BooleanVar(value=self.config_manager.get_show_optional_fields()['show_channel_link'])
        self.show_description_var = ctk.BooleanVar(value=self.config_manager.get_show_optional_fields()['show_video_description'])

        ctk.CTkCheckBox(config_frame, text="显示频道链接", variable=self.show_channel_link_var).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(config_frame, text="显示视频描述", variable=self.show_description_var).grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # 开始按钮
        self.start_button = ctk.CTkButton(config_frame, text="开始搜索", command=self._start_collection, width=200, height=40)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=20)

        # 进度区域
        progress_frame = ctk.CTkFrame(self)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=800)
        self.progress_bar.pack(padx=20, pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(progress_frame, text="就绪")
        self.status_label.pack(pady=5)

        self.cancel_button = ctk.CTkButton(progress_frame, text="取消", command=self._cancel_collection, state="disabled")
        self.cancel_button.pack(pady=5)

        # 数据预览区域
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(preview_frame, text="数据预览（前10条）", font=("微软雅黑", 14, "bold")).pack(pady=5)

        self.preview_text = ctk.CTkTextbox(preview_frame, width=850, height=200)
        self.preview_text.pack(padx=10, pady=5)

        # 底部按钮
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.export_button = ctk.CTkButton(bottom_frame, text="导出Excel", command=self._export_excel, state="disabled")
        self.export_button.pack(side="left", padx=10)

        self.stats_label = ctk.CTkLabel(bottom_frame, text="")
        self.stats_label.pack(side="left", padx=20)

    def _start_collection(self):
        """开始采集"""
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        # 检查 API Key
        if not self.config_manager.get_youtube_api_keys():
            messagebox.showerror("错误", "请先配置 YouTube API Key")
            self._open_api_manager()
            return

        if not self.config_manager.get_deepseek_api_key():
            messagebox.showerror("错误", "请先配置 DeepSeek API Key")
            self._open_api_manager()
            return

        # 保存配置
        max_results = int(self.max_results_combo.get())
        self.config_manager.set_last_search_keyword(keyword)
        self.config_manager.set_last_max_results(max_results)

        # 获取排序方式
        sort_map = {"相关性": "relevance", "发布日期": "date", "观看次数": "viewCount", "评分": "rating"}
        order = sort_map[self.sort_combo.get()]

        # 开始采集
        self.is_collecting = True
        self.start_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.collected_data = []
        self.preview_text.delete("1.0", "end")

        # 在新线程中执行
        self.collector_thread = threading.Thread(
            target=self._collect_data,
            args=(keyword, max_results, order),
            daemon=True
        )
        self.collector_thread.start()

    def _collect_data(self, keyword, max_results, order):
        """采集数据（在后台线程中执行）"""
        try:
            # 初始化 API
            youtube_api = YouTubeAPI(self.config_manager, self.logger)
            deepseek_api = DeepSeekAPI(self.config_manager.get_deepseek_api_key(), self.logger)

            # 创建采集器
            collector = DataCollector(youtube_api, deepseek_api, self.cache_manager, self.logger)

            # 执行采集
            self.collected_data = collector.collect(
                keyword=keyword,
                max_results=max_results,
                order=order,
                progress_callback=self._update_progress,
                status_callback=self._update_status
            )

            # 采集完成
            self._on_collection_complete(collector.get_stats())

        except Exception as e:
            self.logger.error(f"采集失败: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"采集失败: {e}"))
            self.after(0, self._reset_ui)

    def _update_progress(self, percent, current, total, status):
        """更新进度"""
        self.after(0, lambda: self.progress_bar.set(percent / 100))
        self.after(0, lambda: self.status_label.configure(text=f"{status} - {percent}%"))

    def _update_status(self, status):
        """更新状态"""
        self.after(0, lambda: self.status_label.configure(text=status))

    def _on_collection_complete(self, stats):
        """采集完成"""
        self.after(0, self._reset_ui)
        self.after(0, lambda: self._show_preview())
        self.after(0, lambda: self.stats_label.configure(
            text=f"成功: {stats['success']} 条, 失败: {stats['failed']} 条"
        ))

        if self.collected_data:
            self.after(0, lambda: self.export_button.configure(state="normal"))
            self.after(0, lambda: messagebox.showinfo("完成", f"采集完成！共获取 {len(self.collected_data)} 条数据"))

    def _show_preview(self):
        """显示数据预览"""
        self.preview_text.delete("1.0", "end")
        preview_data = self.collected_data[:10]

        for i, item in enumerate(preview_data, 1):
            preview = f"{i}. {item['channel_title']} | {item['video_title'][:30]}... | 播放: {item['view_count']} | 互动率: {item['engagement_rate']}\n"
            self.preview_text.insert("end", preview)

    def _cancel_collection(self):
        """取消采集"""
        if self.is_collecting:
            self.logger.info("用户取消采集")
            self.status_label.configure(text="正在取消...")
            # 这里需要实现取消逻辑
            self._reset_ui()

    def _reset_ui(self):
        """重置UI"""
        self.is_collecting = False
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.progress_bar.set(0)

    def _export_excel(self):
        """导出Excel"""
        if not self.collected_data:
            messagebox.showwarning("提示", "没有数据可导出")
            return

        # 选择保存路径
        default_filename = ExcelExporter.generate_filename(self.keyword_entry.get())
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            initialfile=Path(default_filename).name
        )

        if file_path:
            exporter = ExcelExporter(self.logger)
            success = exporter.export(
                data=self.collected_data,
                output_path=file_path,
                show_channel_link=self.show_channel_link_var.get(),
                show_video_description=self.show_description_var.get()
            )

            if success:
                messagebox.showinfo("成功", f"数据已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出失败，请查看日志")

    def _open_api_manager(self):
        """打开API管理窗口"""
        from src.gui.api_manager_window import APIManagerWindow
        api_window = APIManagerWindow(self, self.config_manager, self.logger)
        api_window.grab_set()

    def _view_logs(self):
        """查看日志"""
        log_content = self.logger.get_log_content()
        log_window = ctk.CTkToplevel(self)
        log_window.title("日志查看器")
        log_window.geometry("800x600")

        text_widget = ctk.CTkTextbox(log_window, width=780, height=550)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", log_content)

    def _clear_cache(self):
        """清除缓存"""
        stats = self.cache_manager.get_cache_stats()
        if messagebox.askyesno("确认", f"确定要清除缓存吗？\n当前缓存: {stats['count']} 个频道"):
            self.cache_manager.clear_all_cache()
            messagebox.showinfo("成功", "缓存已清除")
