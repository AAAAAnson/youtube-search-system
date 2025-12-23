"""
YouTube API 封装模块
提供 YouTube Data API v3 的封装和 API Key 智能管理
"""

import time
import ssl
import httplib2
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class APIKeyManager:
    """API Key 智能管理器"""

    def __init__(self, config_manager):
        """
        初始化 API Key 管理器

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.current_key_index = 0
        self.max_quota = 10000
        self.quota_warning_threshold = 9500

    def get_available_key(self) -> Optional[Dict]:
        """
        获取下一个可用的 API Key（智能切换策略）

        Returns:
            Optional[Dict]: API Key 信息，如果没有可用 Key 返回 None
        """
        api_keys = self.config_manager.get_youtube_api_keys(enabled_only=True)

        if not api_keys:
            return None

        # 检查是否需要重置配额（每天UTC 0点）
        self._check_and_reset_quota()

        # 策略：优先使用配额最多的 Key
        available_keys = [
            key for key in api_keys
            if key.get('quota_used', 0) < self.quota_warning_threshold
        ]

        if not available_keys:
            # 所有 Key 都接近耗尽，使用配额最少的
            available_keys = sorted(api_keys, key=lambda x: x.get('quota_used', 0))

        if available_keys:
            # 返回配额使用最少的 Key
            best_key = min(available_keys, key=lambda x: x.get('quota_used', 0))
            return best_key

        return None

    def consume_quota(self, api_key: str, quota: int):
        """
        消耗配额

        Args:
            api_key: API Key
            quota: 消耗的配额数量
        """
        keys = self.config_manager.get_youtube_api_keys(enabled_only=False)

        for key_info in keys:
            if key_info['key'] == api_key:
                current_used = key_info.get('quota_used', 0)
                new_used = current_used + quota
                self.config_manager.update_api_quota(api_key, new_used)
                break

    def mark_key_exhausted(self, api_key: str):
        """
        标记 API Key 配额已耗尽

        Args:
            api_key: API Key
        """
        self.consume_quota(api_key, self.max_quota)

    def _check_and_reset_quota(self):
        """检查并重置配额（如果到了新的一天）"""
        api_keys = self.config_manager.get_youtube_api_keys(enabled_only=False)
        now = datetime.utcnow()

        for key_info in api_keys:
            try:
                last_reset = datetime.fromisoformat(key_info.get('last_reset', now.isoformat()))
                # 如果上次重置时间是昨天或更早，重置配额
                if last_reset.date() < now.date():
                    self.config_manager.reset_api_quota(key_info['key'])
            except Exception:
                # 解析失败，重置配额
                self.config_manager.reset_api_quota(key_info['key'])

    def get_quota_stats(self) -> Dict:
        """
        获取所有 Key 的配额统计

        Returns:
            Dict: {"total_quota": 总配额, "used_quota": 已用配额, "remaining_quota": 剩余配额}
        """
        api_keys = self.config_manager.get_youtube_api_keys(enabled_only=True)

        total_quota = len(api_keys) * self.max_quota
        used_quota = sum(key.get('quota_used', 0) for key in api_keys)
        remaining_quota = total_quota - used_quota

        return {
            'total_quota': total_quota,
            'used_quota': used_quota,
            'remaining_quota': remaining_quota
        }


class YouTubeAPI:
    """YouTube API 封装类"""

    # API 调用配额消耗
    QUOTA_COSTS = {
        'search': 100,
        'videos': 1,
        'channels': 1
    }

    def __init__(self, config_manager, logger=None):
        """
        初始化 YouTube API

        Args:
            config_manager: 配置管理器
            logger: 日志器（可选）
        """
        self.config_manager = config_manager
        self.logger = logger
        self.key_manager = APIKeyManager(config_manager)
        self.current_api_key = None
        self.youtube = None
        self._initialize_youtube_client()

    def _initialize_youtube_client(self):
        """初始化 YouTube API 客户端"""
        key_info = self.key_manager.get_available_key()

        if key_info:
            self.current_api_key = key_info['key']

            # 创建自定义 HTTP 对象，配置更宽松的 SSL 设置
            try:
                # 尝试创建带有自定义 SSL 上下文的 HTTP 对象
                http = httplib2.Http(
                    timeout=30,
                    disable_ssl_certificate_validation=False
                )
                self.youtube = build('youtube', 'v3', developerKey=self.current_api_key, http=http)
            except Exception:
                # 如果失败，使用默认方式
                self.youtube = build('youtube', 'v3', developerKey=self.current_api_key)

            if self.logger:
                self.logger.info(f"使用 API Key: {key_info.get('name', 'Unknown')}")
        else:
            if self.logger:
                self.logger.error("没有可用的 YouTube API Key")
            raise Exception("没有可用的 YouTube API Key，请先配置")

    def _switch_api_key(self):
        """切换到下一个可用的 API Key"""
        if self.logger:
            self.logger.warning("当前 API Key 配额不足，切换到下一个")

        self._initialize_youtube_client()

    def _execute_with_retry(self, request, quota_cost: int, max_retries: int = 3) -> Optional[Dict]:
        """
        执行 API 请求（带重试和 Key 切换）

        Args:
            request: API 请求对象
            quota_cost: 配额消耗
            max_retries: 最大重试次数

        Returns:
            Optional[Dict]: API 响应，失败返回 None
        """
        for attempt in range(max_retries):
            try:
                response = request.execute()

                # 成功，消耗配额
                self.key_manager.consume_quota(self.current_api_key, quota_cost)

                return response

            except HttpError as e:
                error_reason = e.error_details[0]['reason'] if e.error_details else 'unknown'

                if self.logger:
                    self.logger.warning(f"API 请求失败 (尝试 {attempt + 1}/{max_retries}): {error_reason}")

                # 配额耗尽，切换 Key
                if error_reason == 'quotaExceeded':
                    self.key_manager.mark_key_exhausted(self.current_api_key)
                    try:
                        self._switch_api_key()
                        # 重新构建请求
                        return self._execute_with_retry(request, quota_cost, max_retries - attempt)
                    except Exception:
                        if self.logger:
                            self.logger.error("所有 API Key 都已耗尽")
                        return None

                # 请求过快，等待后重试
                elif error_reason == 'rateLimitExceeded':
                    wait_time = 5 * (attempt + 1)
                    if self.logger:
                        self.logger.warning(f"请求频率过高，等待 {wait_time} 秒")
                    time.sleep(wait_time)
                    continue

                # 其他错误
                else:
                    if self.logger:
                        self.logger.error(f"API 请求错误: {e}")
                    return None

            except Exception as e:
                # SSL 错误或网络错误，可以重试
                error_str = str(e).lower()
                is_retryable = any(keyword in error_str for keyword in [
                    'ssl', 'timeout', 'connection', 'network', 'socket'
                ])

                if is_retryable and attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    if self.logger:
                        self.logger.warning(f"网络错误 (尝试 {attempt + 1}/{max_retries}): {e}，{wait_time}秒后重试")
                    time.sleep(wait_time)
                    continue
                else:
                    if self.logger:
                        self.logger.error(f"未知错误: {e}")
                    return None

        return None

    def search_videos(
        self,
        keyword: str,
        max_results: int = 50,
        order: str = 'relevance',
        page_token: Optional[str] = None
    ) -> Tuple[List[str], Optional[str]]:
        """
        搜索视频

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数（每页最多50）
            order: 排序方式 (relevance/date/viewCount/rating)
            page_token: 分页令牌

        Returns:
            Tuple[List[str], Optional[str]]: (视频ID列表, 下一页令牌)
        """
        if self.logger:
            self.logger.info(f"搜索关键词: {keyword}, 排序: {order}, 每页: {max_results}")

        request = self.youtube.search().list(
            part='id',
            q=keyword,
            type='video',
            maxResults=min(max_results, 50),  # API 限制最多50
            order=order,
            pageToken=page_token
        )

        response = self._execute_with_retry(request, self.QUOTA_COSTS['search'])

        if response:
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            next_page_token = response.get('nextPageToken')

            if self.logger:
                self.logger.info(f"找到 {len(video_ids)} 个视频")

            return video_ids, next_page_token
        else:
            return [], None

    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        获取视频详细信息（批量，最多50个）

        Args:
            video_ids: 视频ID列表（最多50个）

        Returns:
            List[Dict]: 视频详情列表
        """
        if not video_ids:
            return []

        # API 限制每次最多50个
        video_ids = video_ids[:50]

        request = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        )

        response = self._execute_with_retry(request, self.QUOTA_COSTS['videos'])

        if response:
            videos = []
            for item in response.get('items', []):
                video_info = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet'].get('description', ''),
                    'duration': item['contentDetails']['duration'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'default_language': item['snippet'].get('defaultAudioLanguage', 'unknown')
                }
                videos.append(video_info)

            return videos
        else:
            return []

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        获取频道信息

        Args:
            channel_id: 频道ID

        Returns:
            Optional[Dict]: 频道信息
        """
        request = self.youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )

        response = self._execute_with_retry(request, self.QUOTA_COSTS['channels'])

        if response and response.get('items'):
            item = response['items'][0]
            channel_info = {
                'channel_id': item['id'],
                'channel_name': item['snippet']['title'],
                'description': item['snippet'].get('description', ''),
                'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                'channel_link': f"https://www.youtube.com/channel/{item['id']}"
            }
            return channel_info
        else:
            return None

    def test_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        测试 API Key 是否有效

        Args:
            api_key: API Key

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            request = youtube.search().list(
                part='id',
                q='test',
                maxResults=1
            )
            request.execute()
            return True, "API Key 有效"
        except HttpError as e:
            error_reason = e.error_details[0]['reason'] if e.error_details else 'unknown'
            if error_reason == 'badRequest':
                return False, "API Key 无效"
            elif error_reason == 'quotaExceeded':
                return True, "API Key 有效（但配额已耗尽）"
            else:
                return False, f"测试失败: {error_reason}"
        except Exception as e:
            return False, f"测试失败: {str(e)}"

    def get_all_videos_from_search(
        self,
        keyword: str,
        max_results: int = 1000,
        order: str = 'relevance',
        progress_callback=None
    ) -> List[str]:
        """
        获取搜索的所有视频ID（自动翻页）

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数
            order: 排序方式
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            List[str]: 视频ID列表
        """
        all_video_ids = []
        next_page_token = None
        page_count = 0

        while len(all_video_ids) < max_results:
            # 计算本次请求数量
            remaining = max_results - len(all_video_ids)
            page_size = min(50, remaining)

            # 搜索
            video_ids, next_page_token = self.search_videos(
                keyword=keyword,
                max_results=page_size,
                order=order,
                page_token=next_page_token
            )

            if not video_ids:
                break

            all_video_ids.extend(video_ids)
            page_count += 1

            if self.logger:
                self.logger.info(f"第 {page_count} 页，累计 {len(all_video_ids)} 个视频")

            # 进度回调
            if progress_callback:
                progress_callback(len(all_video_ids), max_results)

            # 没有下一页了
            if not next_page_token:
                break

            # 请求间隔（防止被限流）
            time.sleep(0.5)

        if self.logger:
            self.logger.info(f"搜索完成，共 {len(all_video_ids)} 个视频")

        return all_video_ids
