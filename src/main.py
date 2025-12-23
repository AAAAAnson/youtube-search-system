"""
YouTube 数据采集工具 - 程序入口
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import ConfigManager
from src.core.cache_manager import CacheManager
from src.utils.logger import init_logger
from src.gui.main_window import MainWindow
from src.gui.setup_wizard import SetupWizard


def main():
    """程序入口函数"""
    # 初始化配置管理器
    config_manager = ConfigManager()

    # 初始化日志系统
    logger = init_logger(config_manager.get_config_dir())
    logger.info("=" * 60)
    logger.info("YouTube 数据采集工具启动")
    logger.info("=" * 60)

    # 初始化缓存管理器
    cache_manager = CacheManager(config_manager.get_config_dir())

    # 检查是否首次运行
    if config_manager.is_first_run():
        logger.info("检测到首次运行，启动配置向导")

        # 显示首次启动向导
        wizard = SetupWizard(config_manager, logger)
        wizard.mainloop()

        # 如果向导未完成配置，退出程序
        if config_manager.is_first_run():
            logger.info("用户取消配置，程序退出")
            return

    # 启动主窗口
    logger.info("启动主窗口")
    app = MainWindow(config_manager, cache_manager, logger)
    app.mainloop()

    logger.info("程序正常退出")


if __name__ == "__main__":
    main()
