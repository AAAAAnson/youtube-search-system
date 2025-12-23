"""
配置管理模块
负责读取、保存和管理应用程序配置
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        """初始化配置管理器"""
        # 配置目录路径（Windows: AppData/Local）
        if os.name == 'nt':  # Windows
            self.config_dir = Path.home() / 'AppData' / 'Local' / 'YouTubeSearchTool'
        else:  # Linux/Mac（用于开发）
            self.config_dir = Path.home() / '.youtube_search_tool'

        self.config_file = self.config_dir / 'config.json'

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 默认配置
        self.default_config = {
            'youtube_api_keys': [],
            'deepseek_api_key': '',
            'last_search_keyword': '',
            'last_max_results': 100,
            'last_sort_order': 'relevance',
            'show_channel_link': False,
            'show_video_description': False,
            'first_run': True
        }

        # 加载配置
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """
        加载配置文件

        Returns:
            Dict: 配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置（处理新增字段）
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()

    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    # ========== YouTube API Keys 管理 ==========

    def add_youtube_api_key(self, api_key: str, name: str = '') -> bool:
        """
        添加 YouTube API Key

        Args:
            api_key: API Key
            name: 备注名称

        Returns:
            bool: 是否添加成功
        """
        # 检查是否已存在
        for key_info in self.config['youtube_api_keys']:
            if key_info['key'] == api_key:
                return False

        key_info = {
            'key': api_key,
            'name': name or f'API Key {len(self.config["youtube_api_keys"]) + 1}',
            'quota_used': 0,
            'quota_total': 10000,
            'last_reset': datetime.utcnow().isoformat(),
            'enabled': True
        }

        self.config['youtube_api_keys'].append(key_info)
        self.save_config()
        return True

    def remove_youtube_api_key(self, api_key: str) -> bool:
        """
        删除 YouTube API Key

        Args:
            api_key: API Key

        Returns:
            bool: 是否删除成功
        """
        original_count = len(self.config['youtube_api_keys'])
        self.config['youtube_api_keys'] = [
            k for k in self.config['youtube_api_keys'] if k['key'] != api_key
        ]

        if len(self.config['youtube_api_keys']) < original_count:
            self.save_config()
            return True
        return False

    def update_youtube_api_key(self, api_key: str, **kwargs) -> bool:
        """
        更新 YouTube API Key 信息

        Args:
            api_key: API Key
            **kwargs: 要更新的字段

        Returns:
            bool: 是否更新成功
        """
        for key_info in self.config['youtube_api_keys']:
            if key_info['key'] == api_key:
                for k, v in kwargs.items():
                    if k in key_info:
                        key_info[k] = v
                self.save_config()
                return True
        return False

    def get_youtube_api_keys(self, enabled_only: bool = True) -> List[Dict]:
        """
        获取所有 YouTube API Keys

        Args:
            enabled_only: 是否只返回启用的 Key

        Returns:
            List[Dict]: API Key 列表
        """
        if enabled_only:
            return [k for k in self.config['youtube_api_keys'] if k.get('enabled', True)]
        return self.config['youtube_api_keys']

    def update_api_quota(self, api_key: str, quota_used: int):
        """
        更新 API 配额使用量

        Args:
            api_key: API Key
            quota_used: 已使用配额
        """
        self.update_youtube_api_key(api_key, quota_used=quota_used)

    def reset_api_quota(self, api_key: Optional[str] = None):
        """
        重置 API 配额（每天UTC 0点调用）

        Args:
            api_key: 指定 API Key，None 则重置所有
        """
        now = datetime.utcnow().isoformat()

        if api_key:
            self.update_youtube_api_key(
                api_key,
                quota_used=0,
                last_reset=now
            )
        else:
            for key_info in self.config['youtube_api_keys']:
                key_info['quota_used'] = 0
                key_info['last_reset'] = now
            self.save_config()

    def batch_import_youtube_keys(self, keys_data: List[Dict]) -> Dict[str, int]:
        """
        批量导入 YouTube API Keys

        Args:
            keys_data: 格式 [{"key": "xxx", "name": "xxx"}, ...]

        Returns:
            Dict: {"success": 成功数量, "failed": 失败数量}
        """
        success = 0
        failed = 0

        for key_data in keys_data:
            api_key = key_data.get('key', '')
            name = key_data.get('name', '')

            if api_key and self.add_youtube_api_key(api_key, name):
                success += 1
            else:
                failed += 1

        return {"success": success, "failed": failed}

    # ========== DeepSeek API Key 管理 ==========

    def set_deepseek_api_key(self, api_key: str):
        """
        设置 DeepSeek API Key

        Args:
            api_key: API Key
        """
        self.config['deepseek_api_key'] = api_key
        self.save_config()

    def get_deepseek_api_key(self) -> str:
        """
        获取 DeepSeek API Key

        Returns:
            str: API Key
        """
        return self.config.get('deepseek_api_key', '')

    # ========== 用户设置管理 ==========

    def set_last_search_keyword(self, keyword: str):
        """保存上次搜索关键词"""
        self.config['last_search_keyword'] = keyword
        self.save_config()

    def get_last_search_keyword(self) -> str:
        """获取上次搜索关键词"""
        return self.config.get('last_search_keyword', '')

    def set_last_max_results(self, max_results: int):
        """保存上次最大结果数"""
        self.config['last_max_results'] = max_results
        self.save_config()

    def get_last_max_results(self) -> int:
        """获取上次最大结果数"""
        return self.config.get('last_max_results', 100)

    def set_last_sort_order(self, sort_order: str):
        """保存上次排序方式"""
        self.config['last_sort_order'] = sort_order
        self.save_config()

    def get_last_sort_order(self) -> str:
        """获取上次排序方式"""
        return self.config.get('last_sort_order', 'relevance')

    def set_show_optional_fields(self, show_channel_link: bool, show_video_description: bool):
        """设置可选字段显示"""
        self.config['show_channel_link'] = show_channel_link
        self.config['show_video_description'] = show_video_description
        self.save_config()

    def get_show_optional_fields(self) -> Dict[str, bool]:
        """获取可选字段显示设置"""
        return {
            'show_channel_link': self.config.get('show_channel_link', False),
            'show_video_description': self.config.get('show_video_description', False)
        }

    def is_first_run(self) -> bool:
        """检查是否首次运行"""
        return self.config.get('first_run', True)

    def set_first_run_completed(self):
        """标记首次运行已完成"""
        self.config['first_run'] = False
        self.save_config()

    def get_config_dir(self) -> Path:
        """获取配置目录路径"""
        return self.config_dir

    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定路径

        Args:
            export_path: 导出路径

        Returns:
            bool: 是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """
        从指定路径导入配置

        Args:
            import_path: 导入路径

        Returns:
            bool: 是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 合并配置
            self.config.update(imported_config)
            self.save_config()
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
