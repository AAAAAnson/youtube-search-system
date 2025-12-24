"""
主窗口模块 - 鸿蒙风格 (HarmonyOS Style)
YouTube 数据采集工具的主界面
"""

import customtkinter as ctk
import threading
from datetime import datetime
from tkinter import filedialog, messagebox
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.core.cache_manager import CacheManager
from src.core.data_collector import DataCollector
from src.core.search_history_manager import SearchHistoryManager
from src.api.youtube_api import YouTubeAPI
from src.api.deepseek_api import DeepSeekAPI
from src.utils.excel_exporter import ExcelExporter
from src.utils.logger import Logger
from src.gui.harmony_style import (
    HarmonyColors, HarmonyRadius, HarmonySpacing,
    HarmonyFonts, HarmonySizes, HarmonyPresets
)


class HarmonyMainWindow(ctk.CTk):
    """鸿蒙风格主窗口"""

    def __init__(self, config_manager: ConfigManager, cache_manager: CacheManager, logger: Logger):
        super().__init__()

        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.logger = logger
        self.search_history_manager = SearchHistoryManager(config_manager.config_dir)

        # 窗口配置
        self.title("YouTube 数据采集工具")
        self.geometry("1200x820")  # 宽屏布局
        self.minsize(1000, 700)

        # 设置主题
        ctk.set_appearance_mode("light")

        # 数据
        self.collected_data = []
        self.is_collecting = False
        self.collector_thread = None

        # 创建界面
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 设置窗口背景色
        self.configure(fg_color=HarmonyColors.BG_SECONDARY)

        # 创建主容器（带左右边距）
        main_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        main_container.pack(fill="both", expand=True, padx=HarmonySpacing.XL, pady=HarmonySpacing.LG)

        # 创建顶部工具栏
        self._create_toolbar(main_container)

        # 创建内容区域（滚动容器）
        content_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, pady=(HarmonySpacing.MD, 0))

        # 搜索配置卡片
        self._create_search_config_card(content_frame)

        # 高级选项卡片
        self._create_advanced_options_card(content_frame)

        # 进度卡片
        self._create_progress_card(content_frame)

        # 数据预览卡片
        self._create_preview_card(content_frame)

        # 底部操作区
        self._create_bottom_actions(main_container)

    def _create_toolbar(self, parent):
        """创建顶部工具栏"""
        toolbar = ctk.CTkFrame(
            parent,
            height=60,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        toolbar.pack(fill="x", pady=(0, HarmonySpacing.MD))

        # 左侧：应用标题和版本
        left_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_frame.pack(side="left", padx=HarmonySpacing.LG, pady=HarmonySpacing.MD)

        title_label = ctk.CTkLabel(
            left_frame,
            text="YouTube 数据采集工具",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H1, HarmonyFonts.WEIGHT_MEDIUM),
            text_color=HarmonyColors.TEXT_PRIMARY
        )
        title_label.pack(side="left")

        version_label = ctk.CTkLabel(
            left_frame,
            text="v1.0",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_CAPTION),
            text_color=HarmonyColors.TEXT_TERTIARY
        )
        version_label.pack(side="left", padx=(HarmonySpacing.SM, 0))

        # 右侧：工具按钮
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=HarmonySpacing.LG, pady=HarmonySpacing.MD)

        # 次级按钮样式
        btn_style = HarmonyPresets.secondary_button()

        self.cache_btn = ctk.CTkButton(
            right_frame,
            text="🗑️ 清除缓存",
            width=110,
            height=HarmonySizes.BUTTON_MEDIUM,
            command=self._clear_cache,
            **btn_style
        )
        self.cache_btn.pack(side="right", padx=(HarmonySpacing.SM, 0))

        self.log_btn = ctk.CTkButton(
            right_frame,
            text="📋 查看日志",
            width=110,
            height=HarmonySizes.BUTTON_MEDIUM,
            command=self._view_logs,
            **btn_style
        )
        self.log_btn.pack(side="right", padx=(HarmonySpacing.SM, 0))

        self.api_btn = ctk.CTkButton(
            right_frame,
            text="⚙️ API 管理",
            width=110,
            height=HarmonySizes.BUTTON_MEDIUM,
            command=self._open_api_manager,
            **btn_style
        )
        self.api_btn.pack(side="right")

    def _create_search_config_card(self, parent):
        """创建搜索配置卡片"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        card.pack(fill="x", pady=(0, HarmonySpacing.MD))

        # 卡片标题
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=HarmonySpacing.LG, pady=(HarmonySpacing.LG, HarmonySpacing.MD))

        ctk.CTkLabel(
            header,
            text="搜索配置",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H2, HarmonyFonts.WEIGHT_MEDIUM),
            text_color=HarmonyColors.TEXT_PRIMARY
        ).pack(side="left")

        # 配置内容区
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=HarmonySpacing.LG, pady=(0, HarmonySpacing.LG))

        # 使用 grid 布局实现两列
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # 第一行：关键词（跨两列）
        ctk.CTkLabel(
            content,
            text="搜索关键词",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", pady=(0, HarmonySpacing.XS))

        self.keyword_entry = ctk.CTkEntry(
            content,
            height=HarmonySizes.INPUT_HEIGHT,
            placeholder_text="请输入关键词，例如：iPhone15",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            **HarmonyPresets.input_field()
        )
        self.keyword_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, HarmonySpacing.LG))
        self.keyword_entry.insert(0, self.config_manager.get_last_search_keyword())

        # 第二行：最大结果数 | 排序方式
        ctk.CTkLabel(
            content,
            text="最大结果数",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).grid(row=2, column=0, sticky="w", pady=(0, HarmonySpacing.XS))

        self.max_results_combo = ctk.CTkComboBox(
            content,
            values=["50", "100", "200", "500", "1000"],
            height=HarmonySizes.INPUT_HEIGHT,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            dropdown_font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            button_color=HarmonyColors.PRIMARY,
            button_hover_color=HarmonyColors.PRIMARY_HOVER,
            border_color=HarmonyColors.BORDER_LIGHT,
            corner_radius=HarmonyRadius.MEDIUM
        )
        self.max_results_combo.grid(row=3, column=0, sticky="ew", padx=(0, HarmonySpacing.SM), pady=(0, HarmonySpacing.LG))
        self.max_results_combo.set(str(self.config_manager.get_last_max_results()))

        ctk.CTkLabel(
            content,
            text="排序方式",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).grid(row=2, column=1, sticky="w", pady=(0, HarmonySpacing.XS), padx=(HarmonySpacing.SM, 0))

        self.sort_combo = ctk.CTkComboBox(
            content,
            values=["相关性", "发布日期", "观看次数", "评分"],
            height=HarmonySizes.INPUT_HEIGHT,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            dropdown_font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            button_color=HarmonyColors.PRIMARY,
            button_hover_color=HarmonyColors.PRIMARY_HOVER,
            border_color=HarmonyColors.BORDER_LIGHT,
            corner_radius=HarmonyRadius.MEDIUM
        )
        self.sort_combo.grid(row=3, column=1, sticky="ew", padx=(HarmonySpacing.SM, 0), pady=(0, HarmonySpacing.LG))
        self.sort_combo.set("相关性")

        # 第三行：年份范围
        ctk.CTkLabel(
            content,
            text="年份范围",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, HarmonySpacing.XS))

        year_frame = ctk.CTkFrame(content, fg_color="transparent")
        year_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, HarmonySpacing.MD))

        current_year = datetime.now().year
        years = ["不限"] + [str(y) for y in range(2005, current_year + 1)]

        ctk.CTkLabel(
            year_frame,
            text="从",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).pack(side="left", padx=(0, HarmonySpacing.SM))

        self.year_from_combo = ctk.CTkComboBox(
            year_frame,
            values=years,
            width=100,
            height=HarmonySizes.INPUT_HEIGHT,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            button_color=HarmonyColors.PRIMARY,
            border_color=HarmonyColors.BORDER_LIGHT,
            corner_radius=HarmonyRadius.MEDIUM
        )
        self.year_from_combo.set("不限")
        self.year_from_combo.pack(side="left", padx=(0, HarmonySpacing.LG))

        ctk.CTkLabel(
            year_frame,
            text="到",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        ).pack(side="left", padx=(0, HarmonySpacing.SM))

        self.year_to_combo = ctk.CTkComboBox(
            year_frame,
            values=years,
            width=100,
            height=HarmonySizes.INPUT_HEIGHT,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            button_color=HarmonyColors.PRIMARY,
            border_color=HarmonyColors.BORDER_LIGHT,
            corner_radius=HarmonyRadius.MEDIUM
        )
        self.year_to_combo.set("不限")
        self.year_to_combo.pack(side="left")

    def _create_advanced_options_card(self, parent):
        """创建高级选项卡片"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        card.pack(fill="x", pady=(0, HarmonySpacing.MD))

        # 卡片标题
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=HarmonySpacing.LG, pady=(HarmonySpacing.LG, HarmonySpacing.MD))

        ctk.CTkLabel(
            header,
            text="高级选项",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H2, HarmonyFonts.WEIGHT_MEDIUM),
            text_color=HarmonyColors.TEXT_PRIMARY
        ).pack(side="left")

        # 选项内容
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=HarmonySpacing.LG, pady=(0, HarmonySpacing.LG))

        # 初始化变量
        self.exact_match_var = ctk.BooleanVar(value=False)
        self.show_channel_link_var = ctk.BooleanVar(
            value=self.config_manager.get_show_optional_fields()['show_channel_link']
        )
        self.show_description_var = ctk.BooleanVar(
            value=self.config_manager.get_show_optional_fields()['show_video_description']
        )
        self.skip_contact_var = ctk.BooleanVar(value=False)

        # 使用两列布局
        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)

        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, padx=(HarmonySpacing.LG, 0))

        # 鸿蒙风格复选框
        checkbox_style = {
            "font": (HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            "text_color": HarmonyColors.TEXT_PRIMARY,
            "fg_color": HarmonyColors.PRIMARY,
            "hover_color": HarmonyColors.PRIMARY_HOVER,
            "border_color": HarmonyColors.BORDER_DEFAULT,
            "corner_radius": HarmonyRadius.SMALL,
        }

        ctk.CTkCheckBox(
            left_col,
            text="精确匹配关键词",
            variable=self.exact_match_var,
            **checkbox_style
        ).pack(anchor="w", pady=HarmonySpacing.XS)

        ctk.CTkCheckBox(
            left_col,
            text="显示频道链接",
            variable=self.show_channel_link_var,
            **checkbox_style
        ).pack(anchor="w", pady=HarmonySpacing.XS)

        ctk.CTkCheckBox(
            right_col,
            text="显示视频描述",
            variable=self.show_description_var,
            **checkbox_style
        ).pack(anchor="w", pady=HarmonySpacing.XS)

        ctk.CTkCheckBox(
            right_col,
            text="跳过联系方式获取（网络问题时启用）",
            variable=self.skip_contact_var,
            **checkbox_style
        ).pack(anchor="w", pady=HarmonySpacing.XS)

    def _create_progress_card(self, parent):
        """创建进度卡片"""
        self.progress_card = ctk.CTkFrame(
            parent,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        self.progress_card.pack(fill="x", pady=(0, HarmonySpacing.MD))

        # 内容区
        content = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        content.pack(fill="x", padx=HarmonySpacing.LG, pady=HarmonySpacing.LG)

        # 进度条容器
        progress_container = ctk.CTkFrame(content, fg_color="transparent")
        progress_container.pack(fill="x", pady=(0, HarmonySpacing.MD))

        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            height=8,
            corner_radius=HarmonyRadius.SMALL,
            progress_color=HarmonyColors.PRIMARY,
            fg_color=HarmonyColors.BG_TERTIARY
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # 状态文本
        self.status_label = ctk.CTkLabel(
            content,
            text="就绪",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        )
        self.status_label.pack(pady=(0, HarmonySpacing.MD))

        # 按钮容器
        btn_container = ctk.CTkFrame(content, fg_color="transparent")
        btn_container.pack()

        # 主操作按钮
        self.start_button = ctk.CTkButton(
            btn_container,
            text="🚀 开始搜索",
            width=180,
            height=HarmonySizes.BUTTON_LARGE,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H3, HarmonyFonts.WEIGHT_MEDIUM),
            command=self._start_collection,
            **HarmonyPresets.primary_button()
        )
        self.start_button.pack(side="left", padx=(0, HarmonySpacing.MD))

        # 取消按钮
        self.cancel_button = ctk.CTkButton(
            btn_container,
            text="取消",
            width=100,
            height=HarmonySizes.BUTTON_LARGE,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            command=self._cancel_collection,
            state="disabled",
            **HarmonyPresets.secondary_button()
        )
        self.cancel_button.pack(side="left")

    def _create_preview_card(self, parent):
        """创建数据预览卡片"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        card.pack(fill="both", expand=True, pady=(0, HarmonySpacing.MD))

        # 卡片标题
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=HarmonySpacing.LG, pady=(HarmonySpacing.LG, HarmonySpacing.MD))

        ctk.CTkLabel(
            header,
            text="数据预览",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H2, HarmonyFonts.WEIGHT_MEDIUM),
            text_color=HarmonyColors.TEXT_PRIMARY
        ).pack(side="left")

        self.preview_count_label = ctk.CTkLabel(
            header,
            text="(前 10 条)",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_CAPTION),
            text_color=HarmonyColors.TEXT_TERTIARY
        )
        self.preview_count_label.pack(side="left", padx=(HarmonySpacing.SM, 0))

        # 预览内容
        self.preview_text = ctk.CTkTextbox(
            card,
            height=200,
            corner_radius=HarmonyRadius.MEDIUM,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            fg_color=HarmonyColors.BG_TERTIARY,
            border_width=0,
            text_color=HarmonyColors.TEXT_PRIMARY
        )
        self.preview_text.pack(fill="both", expand=True, padx=HarmonySpacing.LG, pady=(0, HarmonySpacing.LG))

    def _create_bottom_actions(self, parent):
        """创建底部操作区"""
        bottom = ctk.CTkFrame(
            parent,
            height=70,
            corner_radius=HarmonyRadius.LARGE,
            fg_color=HarmonyColors.BG_PRIMARY
        )
        bottom.pack(fill="x", pady=(HarmonySpacing.MD, 0))

        # 左侧：统计信息
        self.stats_label = ctk.CTkLabel(
            bottom,
            text="",
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_BODY),
            text_color=HarmonyColors.TEXT_SECONDARY
        )
        self.stats_label.pack(side="left", padx=HarmonySpacing.LG)

        # 右侧：导出按钮
        self.export_button = ctk.CTkButton(
            bottom,
            text="📊 导出 Excel",
            width=160,
            height=HarmonySizes.BUTTON_LARGE,
            font=(HarmonyFonts.FAMILY_FALLBACK, HarmonyFonts.SIZE_H3, HarmonyFonts.WEIGHT_MEDIUM),
            command=self._export_excel,
            state="disabled",
            **HarmonyPresets.success_button()
        )
        self.export_button.pack(side="right", padx=HarmonySpacing.LG, pady=HarmonySpacing.MD)

    # ============ 业务逻辑方法（保持不变） ============

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

        skip_contact = self.skip_contact_var.get()

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

        # 获取年份范围
        year_from_str = self.year_from_combo.get()
        year_to_str = self.year_to_combo.get()
        year_from = int(year_from_str) if year_from_str != "不限" else None
        year_to = int(year_to_str) if year_to_str != "不限" else None

        # 获取精确匹配选项
        exact_match = self.exact_match_var.get()

        # 检查是否有历史搜索记录
        search_progress = self.search_history_manager.get_search_progress(
            keyword, year_from, year_to, exact_match, order
        )

        resume_search = False
        if search_progress and not search_progress.get('is_complete'):
            existing_count = search_progress.get('total_videos', 0)
            response = messagebox.askyesnocancel(
                "发现历史搜索",
                f"发现相同条件的历史搜索记录：\n\n"
                f"关键词: {keyword}\n"
                f"年份: {year_from or '不限'} - {year_to or '不限'}\n"
                f"已获取: {existing_count} 个视频\n\n"
                f"是否继续上次搜索？\n"
                f"【是】继续搜索 【否】重新搜索 【取消】取消操作"
            )

            if response is None:
                return
            elif response:
                resume_search = True
            else:
                self.search_history_manager.clear_search_history(keyword, year_from, year_to, exact_match, order)
                search_progress = None

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
            args=(keyword, max_results, order, skip_contact, year_from, year_to, exact_match, search_progress),
            daemon=True
        )
        self.collector_thread.start()

    def _collect_data(self, keyword, max_results, order, skip_contact=False,
                      year_from=None, year_to=None, exact_match=False, search_progress=None):
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
                year_from=year_from,
                year_to=year_to,
                exact_match=exact_match,
                search_progress=search_progress,
                search_history_manager=self.search_history_manager,
                progress_callback=self._update_progress,
                status_callback=self._update_status
            )

            self.logger.info(f"采集完成，collected_data 长度: {len(self.collected_data)}")

            # 采集完成
            self._on_collection_complete(collector.get_stats())

        except Exception as e:
            self.logger.error(f"采集失败: {e}")
            self.logger.exception(e)
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
        success_count = len(self.collected_data)
        failed_count = stats.get('failed', 0)
        total_count = stats.get('total', 0)

        def update_ui():
            # 重置UI状态
            self.is_collecting = False
            self.start_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.progress_bar.set(0)

            # 更新统计信息
            self.stats_label.configure(
                text=f"✅ 成功: {success_count} 条  ❌ 失败: {failed_count} 条  📊 总计: {total_count}"
            )

            # 显示预览
            self.preview_text.delete("1.0", "end")
            preview_data = self.collected_data[:10]
            for i, item in enumerate(preview_data, 1):
                preview = (
                    f"{i}. {item['channel_title']} | {item['video_title'][:40]}...\n"
                    f"   播放: {item['view_count']:,} | 互动率: {item['engagement_rate']} | "
                    f"联系: {item['contact_info'][:20]}...\n\n"
                )
                self.preview_text.insert("end", preview)

            # 启用导出按钮
            if self.collected_data and len(self.collected_data) > 0:
                self.export_button.configure(state="normal")

                if failed_count > 0:
                    messagebox.showwarning(
                        "采集完成",
                        f"采集完成！\n\n✅ 成功: {success_count} 条\n❌ 失败: {failed_count} 条\n\n"
                        f"💡 提示：请点击右下角的【导出 Excel】按钮保存数据"
                    )
                else:
                    messagebox.showinfo(
                        "采集完成",
                        f"🎉 采集完成！共获取 {success_count} 条数据\n\n"
                        f"💡 提示：请点击右下角的【导出 Excel】按钮保存数据"
                    )
            else:
                messagebox.showerror("失败", "采集失败，未获取到任何数据")

        self.after(0, update_ui)

    def _cancel_collection(self):
        """取消采集"""
        if self.is_collecting:
            self.logger.info("用户取消采集")
            self.status_label.configure(text="正在取消...")
            self._reset_ui()

    def _reset_ui(self):
        """重置UI"""
        self.is_collecting = False
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="就绪")

    def _export_excel(self):
        """导出Excel"""
        if not self.collected_data:
            messagebox.showwarning("提示", "没有数据可导出")
            return

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
                messagebox.showinfo("成功", f"✅ 数据已导出到:\n{file_path}")
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
        log_window.geometry("900x650")
        log_window.configure(fg_color=HarmonyColors.BG_SECONDARY)

        # 日志内容
        text_widget = ctk.CTkTextbox(
            log_window,
            corner_radius=HarmonyRadius.MEDIUM,
            font=("Consolas", 12),
            fg_color=HarmonyColors.BG_PRIMARY
        )
        text_widget.pack(fill="both", expand=True, padx=HarmonySpacing.LG, pady=HarmonySpacing.LG)
        text_widget.insert("1.0", log_content)

    def _clear_cache(self):
        """清除缓存"""
        stats = self.cache_manager.get_cache_stats()
        if messagebox.askyesno("确认", f"确定要清除缓存吗？\n\n当前缓存: {stats['count']} 个频道"):
            self.cache_manager.clear_all_cache()
            messagebox.showinfo("成功", "✅ 缓存已清除")
