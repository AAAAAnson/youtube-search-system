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
        self.skip_contact_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(config_frame, text="显示频道链接", variable=self.show_channel_link_var).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(config_frame, text="显示视频描述", variable=self.show_description_var).grid(row=3, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(
            config_frame,
            text="跳过联系方式获取（遇到网络问题时勾选）",
            variable=self.skip_contact_var
        ).grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 开始按钮
        self.start_button = ctk.CTkButton(config_frame, text="开始搜索", command=self._start_collection, width=200, height=40)
        self.start_button.grid(row=5, column=0, columnspan=2, pady=20)

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

        # 数据预览区域 (固定高度,不扩展)
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="x", padx=10, pady=5)  # 改为 fill="x" 而不是 fill="both", expand=True

        ctk.CTkLabel(preview_frame, text="数据预览（前10条）", font=("微软雅黑", 14, "bold")).pack(pady=5)

        self.preview_text = ctk.CTkTextbox(preview_frame, width=850, height=180)  # 固定高度180
        self.preview_text.pack(padx=10, pady=5)

        # 底部按钮
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.export_button = ctk.CTkButton(
            bottom_frame,
            text="📊 导出Excel",
            command=self._export_excel,
            state="disabled",
            width=150,
            height=40,
            font=("微软雅黑", 14, "bold")
        )
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

        # 获取跳过联系方式选项（提前获取，用于判断是否需要 DeepSeek API）
        skip_contact = self.skip_contact_var.get()

        # 只有在不跳过联系方式时才检查 DeepSeek API Key
        if not skip_contact and not self.config_manager.get_deepseek_api_key():
            messagebox.showerror("错误", "请先配置 DeepSeek API Key\n\n或者勾选\"跳过联系方式获取\"选项")
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
            args=(keyword, max_results, order, skip_contact),
            daemon=True
        )
        self.collector_thread.start()

    def _collect_data(self, keyword, max_results, order, skip_contact=False):
        """采集数据（在后台线程中执行）"""
        try:
            # 初始化 API
            youtube_api = YouTubeAPI(self.config_manager, self.logger)
            deepseek_api = DeepSeekAPI(self.config_manager.get_deepseek_api_key(), self.logger) if not skip_contact else None

            # 创建采集器
            collector = DataCollector(youtube_api, deepseek_api, self.cache_manager, self.logger)

            # 执行采集
            self.collected_data = collector.collect(
                keyword=keyword,
                max_results=max_results,
                order=order,
                skip_contact=skip_contact,
                progress_callback=self._update_progress,
                status_callback=self._update_status
            )

            # DEBUG: 记录采集结果
            self.logger.info(f"[DEBUG] 采集完成，collected_data 长度: {len(self.collected_data)}")
            self.logger.info(f"[DEBUG] collected_data 类型: {type(self.collected_data)}")
            if self.collected_data:
                self.logger.info(f"[DEBUG] 第一条数据示例: {list(self.collected_data[0].keys())}")

            # 采集完成
            self._on_collection_complete(collector.get_stats())

        except Exception as e:
            self.logger.error(f"采集失败: {e}")
            self.logger.exception(e)  # 打印完整堆栈
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
        # DEBUG: 记录回调被触发
        self.logger.info(f"[DEBUG] _on_collection_complete 被调用")
        self.logger.info(f"[DEBUG] stats: {stats}")
        self.logger.info(f"[DEBUG] collected_data 长度: {len(self.collected_data)}")

        success_count = len(self.collected_data)
        failed_count = stats.get('failed', 0)
        total_count = stats.get('total', 0)

        self.logger.info(f"[DEBUG] success_count={success_count}, failed_count={failed_count}, total_count={total_count}")

        # 统一在一个 after 回调中更新所有UI
        def update_ui():
            # 重置UI状态
            self.is_collecting = False
            self.start_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.progress_bar.set(0)

            # 更新统计信息
            self.stats_label.configure(
                text=f"成功: {success_count} 条, 失败: {failed_count} 条 (总计: {total_count})"
            )

            # 显示预览
            self.preview_text.delete("1.0", "end")
            preview_data = self.collected_data[:10]
            for i, item in enumerate(preview_data, 1):
                preview = f"{i}. {item['channel_title']} | {item['video_title'][:30]}... | 播放: {item['view_count']} | 互动率: {item['engagement_rate']}\n"
                self.preview_text.insert("end", preview)

            # 启用导出按钮(如果有数据)
            if self.collected_data and len(self.collected_data) > 0:
                self.logger.info(f"[DEBUG] 在UI线程中启用导出按钮，collected_data 有 {len(self.collected_data)} 条数据")
                self.export_button.configure(
                    state="normal",
                    fg_color=("green", "green"),  # 绿色背景使其更醒目
                    hover_color=("darkgreen", "darkgreen")
                )
                # 强制更新UI
                self.export_button.update_idletasks()
                # 再次检查状态
                current_state = str(self.export_button.cget("state"))
                self.logger.info(f"[DEBUG] 导出按钮当前状态: {current_state}")
                self.logger.info(f"[DEBUG] 导出按钮颜色已设置为绿色")

                # 显示完成消息
                if failed_count > 0:
                    messagebox.showwarning(
                        "采集完成",
                        f"采集完成！\n\n成功: {success_count} 条\n失败: {failed_count} 条\n\n" +
                        f"失败原因：部分视频因网络问题（SSL错误）无法获取。\n建议：稍后重试或检查网络环境。\n\n" +
                        f"👉 请点击窗口左下角的【导出Excel】按钮保存数据"
                    )
                else:
                    messagebox.showinfo(
                        "采集完成",
                        f"采集完成！共获取 {success_count} 条数据\n\n" +
                        f"👉 请点击窗口左下角的【导出Excel】按钮保存数据"
                    )
            else:
                self.logger.warning(f"[DEBUG] collected_data 为空，不启用导出按钮")
                messagebox.showerror(
                    "失败",
                    "采集失败，未获取到任何数据。\n\n可能原因：\n1. 网络连接问题（SSL错误）\n2. API Key无效\n\n请检查日志了解详情。"
                )

        # 使用单个 after 调用更新所有UI
        self.after(0, update_ui)

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
