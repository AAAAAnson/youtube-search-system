"""
搜索历史管理模块
管理搜索历史、去重和断点续传
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class SearchHistoryManager:
    """搜索历史管理器"""

    def __init__(self, config_dir: Path):
        """
        初始化搜索历史管理器

        Args:
            config_dir: 配置目录
        """
        self.config_dir = Path(config_dir)
        self.history_file = self.config_dir / "search_history.json"
        self.history_data = self._load_history()

    def _load_history(self) -> Dict:
        """加载搜索历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"searches": {}}
        return {"searches": {}}

    def _save_history(self):
        """保存搜索历史"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存搜索历史失败: {e}")

    def _generate_search_key(self, keyword: str, year_from: Optional[int], year_to: Optional[int],
                            exact_match: bool, order: str) -> str:
        """生成搜索唯一键"""
        year_range = f"{year_from or 'all'}-{year_to or 'all'}"
        match_type = "exact" if exact_match else "fuzzy"
        return f"{keyword}_{year_range}_{match_type}_{order}"

    def get_search_progress(self, keyword: str, year_from: Optional[int], year_to: Optional[int],
                           exact_match: bool, order: str) -> Optional[Dict]:
        """
        获取搜索进度

        Returns:
            搜索进度信息，如果不存在则返回 None
        """
        search_key = self._generate_search_key(keyword, year_from, year_to, exact_match, order)
        return self.history_data["searches"].get(search_key)

    def update_search_progress(self, keyword: str, year_from: Optional[int], year_to: Optional[int],
                              exact_match: bool, order: str, video_ids: List[str],
                              next_page_token: Optional[str], is_complete: bool = False):
        """
        更新搜索进度

        Args:
            keyword: 搜索关键词
            year_from: 起始年份
            year_to: 结束年份
            exact_match: 是否精确匹配
            order: 排序方式
            video_ids: 已获取的视频ID列表
            next_page_token: 下一页token
            is_complete: 是否搜索完成
        """
        search_key = self._generate_search_key(keyword, year_from, year_to, exact_match, order)

        # 去重
        existing_ids = set(self.history_data["searches"].get(search_key, {}).get("video_ids", []))
        new_ids = list(existing_ids | set(video_ids))

        self.history_data["searches"][search_key] = {
            "keyword": keyword,
            "year_from": year_from,
            "year_to": year_to,
            "exact_match": exact_match,
            "order": order,
            "video_ids": new_ids,
            "total_videos": len(new_ids),
            "next_page_token": next_page_token,
            "is_complete": is_complete,
            "last_updated": datetime.now().isoformat()
        }

        self._save_history()

    def clear_search_history(self, keyword: str, year_from: Optional[int], year_to: Optional[int],
                            exact_match: bool, order: str):
        """清除特定搜索的历史"""
        search_key = self._generate_search_key(keyword, year_from, year_to, exact_match, order)
        if search_key in self.history_data["searches"]:
            del self.history_data["searches"][search_key]
            self._save_history()

    def get_all_history(self) -> Dict:
        """获取所有搜索历史"""
        return self.history_data["searches"]

    def clear_all_history(self):
        """清除所有搜索历史"""
        self.history_data = {"searches": {}}
        self._save_history()
