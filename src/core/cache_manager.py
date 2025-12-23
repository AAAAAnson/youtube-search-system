"""
缓存管理模块
负责管理频道联系方式缓存
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional


class CacheManager:
    """缓存管理器"""

    def __init__(self, config_dir: Path):
        """
        初始化缓存管理器

        Args:
            config_dir: 配置目录路径
        """
        self.cache_file = config_dir / 'cache.json'
        self.cache_expiry_days = 180  # 缓存有效期180天

        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)

        # 加载缓存
        self.cache = self.load_cache()

        # 启动时自动清理过期缓存
        self.clean_expired_cache()

    def load_cache(self) -> Dict:
        """
        加载缓存文件

        Returns:
            Dict: 缓存字典
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                return cache
            except Exception as e:
                print(f"加载缓存文件失败: {e}")
                return {'channels': {}}
        else:
            return {'channels': {}}

    def save_cache(self) -> bool:
        """
        保存缓存到文件

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
            return False

    def get_channel_contact(self, channel_id: str) -> Optional[str]:
        """
        获取频道联系方式（如果缓存中存在且未过期）

        Args:
            channel_id: 频道ID

        Returns:
            Optional[str]: 联系方式，如果不存在或已过期返回 None
        """
        if channel_id not in self.cache['channels']:
            return None

        channel_data = self.cache['channels'][channel_id]

        # 检查是否过期
        cached_time = datetime.fromisoformat(channel_data['timestamp'])
        if datetime.now() - cached_time > timedelta(days=self.cache_expiry_days):
            # 已过期，删除缓存
            del self.cache['channels'][channel_id]
            self.save_cache()
            return None

        return channel_data.get('contact_info')

    def set_channel_contact(
        self,
        channel_id: str,
        contact_info: str,
        channel_name: str = '',
        channel_link: str = '',
        description: str = ''
    ):
        """
        设置频道联系方式到缓存

        Args:
            channel_id: 频道ID
            contact_info: 联系方式
            channel_name: 频道名称（可选）
            channel_link: 频道链接（可选）
            description: 频道描述（可选）
        """
        self.cache['channels'][channel_id] = {
            'contact_info': contact_info,
            'timestamp': datetime.now().isoformat(),
            'channel_name': channel_name,
            'channel_link': channel_link,
            'description': description
        }
        self.save_cache()

    def get_channel_data(self, channel_id: str) -> Optional[Dict]:
        """
        获取完整的频道缓存数据

        Args:
            channel_id: 频道ID

        Returns:
            Optional[Dict]: 频道数据，如果不存在或已过期返回 None
        """
        if channel_id not in self.cache['channels']:
            return None

        channel_data = self.cache['channels'][channel_id]

        # 检查是否过期
        cached_time = datetime.fromisoformat(channel_data['timestamp'])
        if datetime.now() - cached_time > timedelta(days=self.cache_expiry_days):
            # 已过期，删除缓存
            del self.cache['channels'][channel_id]
            self.save_cache()
            return None

        return channel_data

    def clean_expired_cache(self) -> int:
        """
        清理所有过期的缓存

        Returns:
            int: 清理的缓存数量
        """
        expired_channels = []
        now = datetime.now()

        for channel_id, channel_data in self.cache['channels'].items():
            try:
                cached_time = datetime.fromisoformat(channel_data['timestamp'])
                if now - cached_time > timedelta(days=self.cache_expiry_days):
                    expired_channels.append(channel_id)
            except Exception:
                # 时间戳格式错误，也标记为过期
                expired_channels.append(channel_id)

        # 删除过期缓存
        for channel_id in expired_channels:
            del self.cache['channels'][channel_id]

        if expired_channels:
            self.save_cache()

        return len(expired_channels)

    def clear_all_cache(self) -> bool:
        """
        清除所有缓存

        Returns:
            bool: 是否清除成功
        """
        self.cache = {'channels': {}}
        return self.save_cache()

    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            Dict: 统计信息 {"count": 数量, "size_mb": 大小(MB)}
        """
        count = len(self.cache['channels'])

        # 计算文件大小
        size_bytes = 0
        if self.cache_file.exists():
            size_bytes = os.path.getsize(self.cache_file)

        size_mb = size_bytes / (1024 * 1024)

        return {
            'count': count,
            'size_mb': round(size_mb, 2)
        }

    def has_channel(self, channel_id: str) -> bool:
        """
        检查频道是否在缓存中（且未过期）

        Args:
            channel_id: 频道ID

        Returns:
            bool: 是否存在
        """
        return self.get_channel_contact(channel_id) is not None

    def remove_channel(self, channel_id: str) -> bool:
        """
        从缓存中删除指定频道

        Args:
            channel_id: 频道ID

        Returns:
            bool: 是否删除成功
        """
        if channel_id in self.cache['channels']:
            del self.cache['channels'][channel_id]
            self.save_cache()
            return True
        return False

    def export_cache(self, export_path: str) -> bool:
        """
        导出缓存到指定路径

        Args:
            export_path: 导出路径

        Returns:
            bool: 是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出缓存失败: {e}")
            return False

    def import_cache(self, import_path: str, merge: bool = True) -> bool:
        """
        从指定路径导入缓存

        Args:
            import_path: 导入路径
            merge: 是否合并（True）还是覆盖（False）

        Returns:
            bool: 是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_cache = json.load(f)

            if merge:
                # 合并缓存
                self.cache['channels'].update(imported_cache.get('channels', {}))
            else:
                # 覆盖缓存
                self.cache = imported_cache

            self.save_cache()
            return True
        except Exception as e:
            print(f"导入缓存失败: {e}")
            return False
