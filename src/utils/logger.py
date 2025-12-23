"""
日志系统模块
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class Logger:
    """日志管理器"""

    def __init__(self, config_dir: Path, log_retention_days: int = 30):
        """
        初始化日志管理器

        Args:
            config_dir: 配置目录路径
            log_retention_days: 日志保留天数
        """
        self.log_dir = config_dir / 'logs'
        self.log_retention_days = log_retention_days

        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 创建logger
        self.logger = logging.getLogger('YouTubeSearchTool')
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的处理器（避免重复）
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 创建文件处理器（每天一个文件）
        log_file = self.log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 启动时清理旧日志
        self.clean_old_logs()

    def info(self, message: str):
        """记录信息级别日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告级别日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """记录错误级别日志"""
        self.logger.error(message)

    def debug(self, message: str):
        """记录调试级别日志"""
        self.logger.debug(message)

    def clean_old_logs(self) -> int:
        """
        清理超过保留天数的旧日志

        Returns:
            int: 清理的日志文件数量
        """
        if not self.log_dir.exists():
            return 0

        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)

        for log_file in self.log_dir.glob('*.log'):
            try:
                # 从文件名解析日期
                file_date_str = log_file.stem  # 文件名（不含扩展名）
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                # 无法解析的文件跳过
                self.warning(f"无法处理日志文件 {log_file}: {e}")

        if cleaned_count > 0:
            self.info(f"清理了 {cleaned_count} 个旧日志文件")

        return cleaned_count

    def get_today_log_path(self) -> Path:
        """
        获取今天的日志文件路径

        Returns:
            Path: 日志文件路径
        """
        return self.log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'

    def get_log_content(self, date: Optional[str] = None) -> str:
        """
        获取指定日期的日志内容

        Args:
            date: 日期字符串（YYYY-MM-DD），None 则返回今天的

        Returns:
            str: 日志内容
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        log_file = self.log_dir / f'{date}.log'

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"读取日志文件失败: {e}"
        else:
            return f"日志文件不存在: {log_file}"

    def get_available_log_dates(self) -> list:
        """
        获取所有可用的日志日期

        Returns:
            list: 日期列表（YYYY-MM-DD）
        """
        if not self.log_dir.exists():
            return []

        dates = []
        for log_file in self.log_dir.glob('*.log'):
            dates.append(log_file.stem)

        return sorted(dates, reverse=True)  # 降序排列（最新的在前）

    def clear_all_logs(self) -> bool:
        """
        清除所有日志文件

        Returns:
            bool: 是否清除成功
        """
        try:
            for log_file in self.log_dir.glob('*.log'):
                log_file.unlink()
            self.info("所有日志文件已清除")
            return True
        except Exception as e:
            self.error(f"清除日志文件失败: {e}")
            return False


# 创建全局logger实例（在应用启动时初始化）
_global_logger: Optional[Logger] = None


def init_logger(config_dir: Path) -> Logger:
    """
    初始化全局日志器

    Args:
        config_dir: 配置目录路径

    Returns:
        Logger: 日志器实例
    """
    global _global_logger
    _global_logger = Logger(config_dir)
    return _global_logger


def get_logger() -> Logger:
    """
    获取全局日志器

    Returns:
        Logger: 日志器实例
    """
    if _global_logger is None:
        raise RuntimeError("Logger 未初始化，请先调用 init_logger()")
    return _global_logger
