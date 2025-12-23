"""
辅助函数模块
提供通用的工具函数
"""

import csv
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


def parse_duration(duration_str: str) -> str:
    """
    解析 YouTube API 返回的时长格式 (ISO 8601)

    Args:
        duration_str: ISO 8601 格式的时长字符串 (如 "PT1H23M45S")

    Returns:
        str: 格式化的时长 (如 "1:23:45" 或 "23:45")
    """
    if not duration_str:
        return "0:00"

    # 使用正则表达式解析
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return "0:00"

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def format_number(num: int) -> str:
    """
    格式化数字（添加千分位）

    Args:
        num: 数字

    Returns:
        str: 格式化后的字符串
    """
    return f"{num:,}"


def calculate_engagement_rate(likes: int, comments: int, views: int) -> float:
    """
    计算互动率

    Args:
        likes: 点赞数
        comments: 评论数
        views: 播放数

    Returns:
        float: 互动率（百分比）
    """
    if views == 0:
        return 0.0

    engagement = (likes + comments) / views * 100
    return round(engagement, 2)


def format_date(date_str: str) -> str:
    """
    格式化日期字符串

    Args:
        date_str: ISO 8601 格式的日期字符串

    Returns:
        str: YYYY-MM-DD 格式
    """
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return date_str


def parse_csv_keys(file_path: str) -> List[Dict]:
    """
    从 CSV 文件解析 API Keys

    Args:
        file_path: CSV 文件路径

    Returns:
        List[Dict]: [{"key": "xxx", "name": "xxx"}, ...]
    """
    keys_data = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 尝试使用 CSV 读取器
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 1:
                    key = row[0].strip()
                    name = row[1].strip() if len(row) >= 2 else ''
                    if key:
                        keys_data.append({"key": key, "name": name})
    except Exception as e:
        print(f"解析 CSV 文件失败: {e}")

    return keys_data


def parse_txt_keys(file_path: str) -> List[Dict]:
    """
    从 TXT 文件解析 API Keys（每行一个）

    Args:
        file_path: TXT 文件路径

    Returns:
        List[Dict]: [{"key": "xxx", "name": ""}, ...]
    """
    keys_data = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                key = line.strip()
                if key:
                    keys_data.append({"key": key, "name": ""})
    except Exception as e:
        print(f"解析 TXT 文件失败: {e}")

    return keys_data


def parse_json_keys(file_path: str) -> List[Dict]:
    """
    从 JSON 文件解析 API Keys

    Args:
        file_path: JSON 文件路径

    Returns:
        List[Dict]: [{"key": "xxx", "name": "xxx"}, ...]
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 支持两种格式
            # 格式1: [{"key": "xxx", "name": "xxx"}, ...]
            # 格式2: ["key1", "key2", ...]

            if isinstance(data, list):
                keys_data = []
                for item in data:
                    if isinstance(item, dict):
                        keys_data.append(item)
                    elif isinstance(item, str):
                        keys_data.append({"key": item, "name": ""})
                return keys_data
            else:
                return []
    except Exception as e:
        print(f"解析 JSON 文件失败: {e}")
        return []


def import_api_keys(file_path: str) -> List[Dict]:
    """
    从文件导入 API Keys（自动识别格式）

    Args:
        file_path: 文件路径

    Returns:
        List[Dict]: [{"key": "xxx", "name": "xxx"}, ...]
    """
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.csv':
        return parse_csv_keys(file_path)
    elif file_ext == '.txt':
        return parse_txt_keys(file_path)
    elif file_ext == '.json':
        return parse_json_keys(file_path)
    else:
        # 尝试按 TXT 格式解析
        return parse_txt_keys(file_path)


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    截断文本到指定长度

    Args:
        text: 文本
        max_length: 最大长度

    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def is_valid_api_key(key: str) -> bool:
    """
    简单验证 API Key 格式

    Args:
        key: API Key

    Returns:
        bool: 是否有效
    """
    # YouTube API Key 通常以 AIza 开头，长度约 39 字符
    if key.startswith('AIza') and len(key) >= 30:
        return True

    # DeepSeek API Key 通常以 sk- 开头
    if key.startswith('sk-') and len(key) >= 20:
        return True

    return False


def estimate_time_remaining(processed: int, total: int, elapsed_seconds: float) -> str:
    """
    估算剩余时间

    Args:
        processed: 已处理数量
        total: 总数量
        elapsed_seconds: 已用时间（秒）

    Returns:
        str: 剩余时间描述 (如 "5分钟" 或 "1小时30分钟")
    """
    if processed == 0 or processed >= total:
        return "0秒"

    # 计算平均速度
    avg_time_per_item = elapsed_seconds / processed
    remaining_items = total - processed
    remaining_seconds = avg_time_per_item * remaining_items

    # 格式化时间
    if remaining_seconds < 60:
        return f"{int(remaining_seconds)}秒"
    elif remaining_seconds < 3600:
        minutes = int(remaining_seconds / 60)
        return f"{minutes}分钟"
    else:
        hours = int(remaining_seconds / 3600)
        minutes = int((remaining_seconds % 3600) / 60)
        return f"{hours}小时{minutes}分钟"
