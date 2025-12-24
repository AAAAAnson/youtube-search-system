"""
数据采集核心模块
整合 YouTube API、DeepSeek API 和缓存管理，实现完整的数据采集流程
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Callable

from src.api.youtube_api import YouTubeAPI
from src.api.deepseek_api import DeepSeekAPI
from src.core.cache_manager import CacheManager
from src.utils.helpers import (
    parse_duration,
    calculate_engagement_rate,
    format_date,
    truncate_text
)


class DataCollector:
    """数据采集器"""

    def __init__(
        self,
        youtube_api: YouTubeAPI,
        deepseek_api: DeepSeekAPI,
        cache_manager: CacheManager,
        logger=None
    ):
        """
        初始化数据采集器

        Args:
            youtube_api: YouTube API 实例
            deepseek_api: DeepSeek API 实例
            cache_manager: 缓存管理器
            logger: 日志器
        """
        self.youtube_api = youtube_api
        self.deepseek_api = deepseek_api
        self.cache_manager = cache_manager
        self.logger = logger

        # 取消标志
        self.cancel_event = threading.Event()

        # 采集统计
        self.stats = {
            'total': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def collect(
        self,
        keyword: str,
        max_results: int = 100,
        order: str = 'relevance',
        skip_contact: bool = False,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        执行完整的数据采集流程

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数
            order: 排序方式
            skip_contact: 是否跳过联系方式获取（遇到网络问题时可开启）
            progress_callback: 进度回调 callback(percent, current, total, status)
            status_callback: 状态回调 callback(status_message)

        Returns:
            List[Dict]: 采集的数据列表
        """
        self.cancel_event.clear()
        self.stats = {'total': 0, 'processed': 0, 'success': 0, 'failed': 0, 'skipped': 0}
        start_time = time.time()

        try:
            # 阶段1: 搜索视频 (0-20%)
            if status_callback:
                status_callback("正在搜索视频...")
            if self.logger:
                self.logger.info(f"开始搜索关键词: {keyword}")

            video_ids = self._search_videos(keyword, max_results, order, progress_callback)

            if self.cancel_event.is_set():
                if self.logger:
                    self.logger.info("采集已取消")
                return []

            self.stats['total'] = len(video_ids)
            if self.logger:
                self.logger.info(f"找到 {len(video_ids)} 个视频")

            if not video_ids:
                if self.logger:
                    self.logger.warning("没有找到视频")
                return []

            # 阶段2: 获取视频详情 (20-80%)
            if status_callback:
                status_callback("正在获取视频详情...")

            videos_data = self._get_videos_details(video_ids, progress_callback)

            if self.cancel_event.is_set():
                if self.logger:
                    self.logger.info("采集已取消")
                return []

            # 阶段3: 获取频道信息和联系方式 (80-95%)
            if skip_contact:
                if status_callback:
                    status_callback("跳过联系方式获取，正在整理数据...")
                if self.logger:
                    self.logger.info("用户选择跳过联系方式获取")
            else:
                if status_callback:
                    status_callback("正在获取频道信息和联系方式...")

            final_data = self._enrich_with_channel_data(
                videos_data,
                keyword,
                skip_contact,
                progress_callback
            )

            if self.cancel_event.is_set():
                if self.logger:
                    self.logger.info("采集已取消")
                return []

            # 完成
            elapsed_time = time.time() - start_time
            if self.logger:
                self.logger.info(
                    f"采集完成！总数: {self.stats['total']}, "
                    f"成功: {self.stats['success']}, "
                    f"失败: {self.stats['failed']}, "
                    f"耗时: {elapsed_time:.1f}秒"
                )
                # DEBUG: 记录返回数据
                self.logger.info(f"[DEBUG] DataCollector.collect() 返回 {len(final_data)} 条数据")
                if final_data:
                    self.logger.info(f"[DEBUG] 返回数据示例字段: {list(final_data[0].keys())}")

            if progress_callback:
                progress_callback(100, self.stats['success'], self.stats['total'], "采集完成")

            return final_data

        except Exception as e:
            if self.logger:
                self.logger.error(f"采集过程出错: {e}")
            return []

    def cancel(self):
        """取消采集"""
        self.cancel_event.set()
        if self.logger:
            self.logger.info("收到取消信号")

    def _search_videos(
        self,
        keyword: str,
        max_results: int,
        order: str,
        progress_callback: Optional[Callable]
    ) -> List[str]:
        """
        搜索视频ID

        Args:
            keyword: 关键词
            max_results: 最大结果数
            order: 排序方式
            progress_callback: 进度回调

        Returns:
            List[str]: 视频ID列表
        """
        def search_progress(current, total):
            if self.cancel_event.is_set():
                return
            if progress_callback:
                percent = int(20 * current / total)
                progress_callback(percent, current, total, f"正在搜索... ({current}/{total})")

        video_ids = self.youtube_api.get_all_videos_from_search(
            keyword=keyword,
            max_results=max_results,
            order=order,
            progress_callback=search_progress
        )

        # 去重
        video_ids = list(dict.fromkeys(video_ids))

        return video_ids

    def _get_videos_details(
        self,
        video_ids: List[str],
        progress_callback: Optional[Callable]
    ) -> List[Dict]:
        """
        批量获取视频详情（多线程）

        Args:
            video_ids: 视频ID列表
            progress_callback: 进度回调

        Returns:
            List[Dict]: 视频数据列表
        """
        videos_data = []
        total = len(video_ids)
        processed = 0

        # 批量处理（每批50个，YouTube API限制）
        batch_size = 50
        batches = [video_ids[i:i+batch_size] for i in range(0, len(video_ids), batch_size)]

        # 使用线程池并发处理（控制并发数为5，避免SSL错误）
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}

            for batch in batches:
                if self.cancel_event.is_set():
                    break

                future = executor.submit(self.youtube_api.get_video_details, batch)
                futures[future] = batch

                # 控制请求间隔（增加到0.3秒，避免SSL错误）
                time.sleep(0.3)

            # 收集结果
            for future in as_completed(futures):
                if self.cancel_event.is_set():
                    break

                try:
                    batch_videos = future.result()

                    if batch_videos:
                        videos_data.extend(batch_videos)
                        # 实际成功的数量
                        actual_success = len(batch_videos)
                    else:
                        actual_success = 0

                    # 请求的数量
                    requested = len(futures[future])
                    failed = requested - actual_success

                    processed += requested
                    self.stats['processed'] = processed

                    if failed > 0:
                        self.stats['failed'] += failed
                        if self.logger:
                            self.logger.warning(f"批次部分失败: 成功 {actual_success}/{requested}")

                    # 更新进度 (20-80%)
                    if progress_callback:
                        percent = 20 + int(60 * processed / total)
                        progress_callback(
                            percent,
                            processed,
                            total,
                            f"正在获取视频详情... ({len(videos_data)}/{processed})"
                        )

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"获取视频详情失败: {e}")
                    batch_size_failed = len(futures[future])
                    processed += batch_size_failed
                    self.stats['failed'] += batch_size_failed

        if self.logger:
            self.logger.info(f"成功获取 {len(videos_data)} 个视频的详情")
            self.logger.info(f"[DEBUG] _get_videos_details() 返回 {len(videos_data)} 条视频数据")

        return videos_data

    def _enrich_with_channel_data(
        self,
        videos_data: List[Dict],
        keyword: str,
        skip_contact: bool,
        progress_callback: Optional[Callable]
    ) -> List[Dict]:
        """
        补充频道信息和联系方式

        Args:
            videos_data: 视频数据列表
            keyword: 搜索关键词
            skip_contact: 是否跳过联系方式获取
            progress_callback: 进度回调

        Returns:
            List[Dict]: 完整的数据列表
        """
        # 如果跳过联系方式，直接组装数据
        if skip_contact:
            return self._assemble_final_data_without_contact(videos_data, keyword, progress_callback)

        # 提取唯一的频道ID
        channel_ids = list(set([v['channel_id'] for v in videos_data]))
        total_channels = len(channel_ids)
        processed_channels = 0

        if self.logger:
            self.logger.info(f"共有 {total_channels} 个唯一频道")

        # 频道数据缓存（本次采集session内）
        channel_data_cache = {}

        # 使用线程池并发获取频道信息（控制并发数为3，进一步降低SSL错误）
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}

            for channel_id in channel_ids:
                if self.cancel_event.is_set():
                    break

                future = executor.submit(self._get_channel_data_with_contact, channel_id)
                futures[future] = channel_id

                # 控制请求间隔
                time.sleep(0.15)

            # 收集频道数据
            for future in as_completed(futures):
                if self.cancel_event.is_set():
                    break

                channel_id = futures[future]
                try:
                    channel_data = future.result()
                    if channel_data:
                        channel_data_cache[channel_id] = channel_data

                    processed_channels += 1

                    # 更新进度 (80-95%)
                    if progress_callback:
                        percent = 80 + int(15 * processed_channels / total_channels)
                        progress_callback(
                            percent,
                            processed_channels,
                            total_channels,
                            f"正在获取频道信息... ({processed_channels}/{total_channels})"
                        )

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"获取频道数据失败 ({channel_id}): {e}")

        # 组装最终数据
        final_data = []
        for video in videos_data:
            channel_id = video['channel_id']
            channel_data = channel_data_cache.get(channel_id, {})

            # 构建完整数据
            data_item = {
                'keyword': keyword,
                'channel_title': video['channel_title'],
                'video_link': f"https://www.youtube.com/watch?v={video['video_id']}",
                'view_count': video['view_count'],
                'engagement_rate': f"{calculate_engagement_rate(video['like_count'], video['comment_count'], video['view_count']):.2f}%",
                'contact_info': channel_data.get('contact_info', '无'),
                'like_count': video['like_count'],
                'comment_count': video['comment_count'],
                'video_title': video['title'],
                'published_at': format_date(video['published_at']),
                'duration': parse_duration(video['duration']),
                'subscriber_count': channel_data.get('subscriber_count', 0),
                'channel_link': channel_data.get('channel_link', ''),
                'description': truncate_text(video.get('description', ''), 200),
                'language': video.get('default_language', 'unknown')
            }

            final_data.append(data_item)
            self.stats['success'] += 1

        # 最后阶段完成 (95-100%)
        if progress_callback:
            progress_callback(100, len(final_data), len(videos_data), "数据处理完成")

        if self.logger:
            self.logger.info(f"[DEBUG] _enrich_with_channel_data() 返回 {len(final_data)} 条数据")

        return final_data

    def _get_channel_data_with_contact(self, channel_id: str) -> Optional[Dict]:
        """
        获取频道数据（包含联系方式）

        Args:
            channel_id: 频道ID

        Returns:
            Optional[Dict]: 频道数据
        """
        if self.cancel_event.is_set():
            return None

        try:
            # 先检查缓存
            cached_data = self.cache_manager.get_channel_data(channel_id)
            if cached_data:
                if self.logger:
                    self.logger.debug(f"从缓存获取频道数据: {cached_data.get('channel_name')}")
                return {
                    'contact_info': cached_data.get('contact_info', '无'),
                    'subscriber_count': 0,  # 缓存中没有订阅数，需要重新获取
                    'channel_link': cached_data.get('channel_link', '')
                }

            # 从 YouTube API 获取频道信息
            channel_info = self.youtube_api.get_channel_info(channel_id)
            if not channel_info:
                if self.logger:
                    self.logger.warning(f"无法获取频道信息: {channel_id}")
                # 返回默认数据，避免整个采集失败
                return {
                    'contact_info': '获取失败',
                    'subscriber_count': 0,
                    'channel_link': f'https://www.youtube.com/channel/{channel_id}'
                }

            # 提取联系方式（使用 DeepSeek AI）
            description = channel_info.get('description', '')
            contact_info = '无'

            if description and self.deepseek_api:
                try:
                    success, extracted_contact = self.deepseek_api.extract_contact_info(description)
                    if success:
                        contact_info = extracted_contact
                    else:
                        contact_info = '提取失败'
                        if self.logger:
                            self.logger.warning(f"DeepSeek 提取联系方式失败: {channel_id}")
                except Exception as deepseek_error:
                    # DeepSeek API 调用失败（如SSL错误）
                    contact_info = '网络错误'
                    if self.logger:
                        error_str = str(deepseek_error)
                        if 'SSL' in error_str:
                            self.logger.error(f"DeepSeek API SSL 错误 ({channel_id}): {deepseek_error}")
                        else:
                            self.logger.error(f"DeepSeek API 调用失败 ({channel_id}): {deepseek_error}")

                # 保存到缓存（即使失败也缓存，避免重复请求）
                self.cache_manager.set_channel_contact(
                    channel_id=channel_id,
                    contact_info=contact_info,
                    channel_name=channel_info['channel_name'],
                    channel_link=channel_info['channel_link'],
                    description=description
                )
            else:
                # 简介为空，也缓存
                self.cache_manager.set_channel_contact(
                    channel_id=channel_id,
                    contact_info='无',
                    channel_name=channel_info['channel_name'],
                    channel_link=channel_info['channel_link'],
                    description=''
                )

            return {
                'contact_info': contact_info,
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'channel_link': channel_info.get('channel_link', '')
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"处理频道 {channel_id} 时出错: {e}")
            # 返回默认数据，而不是 None，避免整个采集失败
            return {
                'contact_info': '获取失败',
                'subscriber_count': 0,
                'channel_link': f'https://www.youtube.com/channel/{channel_id}'
            }

    def _assemble_final_data_without_contact(
        self,
        videos_data: List[Dict],
        keyword: str,
        progress_callback: Optional[Callable]
    ) -> List[Dict]:
        """
        组装数据（不获取联系方式，避免SSL错误）

        Args:
            videos_data: 视频数据列表
            keyword: 搜索关键词
            progress_callback: 进度回调

        Returns:
            List[Dict]: 完整的数据列表
        """
        final_data = []

        total = len(videos_data)
        for index, video in enumerate(videos_data, 1):
            # 构建完整数据（联系方式标记为"未获取"）
            data_item = {
                'keyword': keyword,
                'channel_title': video['channel_title'],
                'video_link': f"https://www.youtube.com/watch?v={video['video_id']}",
                'view_count': video['view_count'],
                'engagement_rate': f"{calculate_engagement_rate(video['like_count'], video['comment_count'], video['view_count']):.2f}%",
                'contact_info': '未获取（跳过）',
                'like_count': video['like_count'],
                'comment_count': video['comment_count'],
                'video_title': video['title'],
                'published_at': format_date(video['published_at']),
                'duration': parse_duration(video['duration']),
                'subscriber_count': 0,  # 未获取
                'channel_link': f"https://www.youtube.com/channel/{video['channel_id']}",
                'description': truncate_text(video.get('description', ''), 200),
                'language': video.get('default_language', 'unknown')
            }

            final_data.append(data_item)
            self.stats['success'] += 1

            # 更新进度 (80-100%)
            if progress_callback:
                percent = 80 + int(20 * index / total)
                progress_callback(
                    percent,
                    index,
                    total,
                    f"正在整理数据... ({index}/{total})"
                )

        if progress_callback:
            progress_callback(100, total, total, "数据处理完成")

        if self.logger:
            self.logger.info(f"[DEBUG] _assemble_final_data_without_contact() 返回 {len(final_data)} 条数据")

        return final_data

    def get_stats(self) -> Dict:
        """获取采集统计信息"""
        return self.stats.copy()
