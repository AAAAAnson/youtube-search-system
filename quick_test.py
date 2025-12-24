"""
快速测试脚本 - 验证YouTube API连接和基本功能
"""

import sys
sys.path.insert(0, '/home/user/youtube-search-system')

from src.core.config_manager import ConfigManager
from src.api.youtube_api import YouTubeAPI
from src.utils.logger import Logger

def test_youtube_api():
    """测试YouTube API基本功能"""
    print("=" * 60)
    print("YouTube API 快速测试")
    print("=" * 60)

    # 初始化
    config = ConfigManager()
    logger = Logger(config.config_dir)

    # 检查API Key
    keys = config.get_youtube_api_keys()
    if not keys:
        print("❌ 错误: 没有配置 YouTube API Key")
        print("   请先运行程序配置 API Key")
        return False

    print(f"\n✅ 找到 {len(keys)} 个 YouTube API Key")

    # 初始化 YouTube API
    try:
        youtube_api = YouTubeAPI(config, logger)
        print("✅ YouTube API 客户端初始化成功")
    except Exception as e:
        print(f"❌ YouTube API 初始化失败: {e}")
        return False

    # 测试搜索
    print("\n正在测试搜索功能 (关键词: test, 最多5条)...")
    try:
        video_ids, next_token = youtube_api.search_videos(
            keyword="test",
            max_results=5,
            order="relevance"
        )

        if video_ids:
            print(f"✅ 搜索成功! 找到 {len(video_ids)} 个视频")
            print(f"   视频ID示例: {video_ids[0]}")
        else:
            print("⚠️ 搜索返回空结果")
            return False

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return False

    # 测试获取视频详情
    print("\n正在测试获取视频详情...")
    try:
        videos = youtube_api.get_video_details([video_ids[0]])

        if videos and len(videos) > 0:
            video = videos[0]
            print(f"✅ 获取详情成功!")
            print(f"   标题: {video['title'][:50]}...")
            print(f"   播放量: {video['view_count']}")
            print(f"   点赞数: {video['like_count']}")
        else:
            print("⚠️ 获取详情返回空结果")
            return False

    except Exception as e:
        print(f"❌ 获取详情失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有测试通过! YouTube API 工作正常!")
    print("=" * 60)
    print("\n👉 现在可以运行主程序: python src/main.py")
    return True

if __name__ == "__main__":
    success = test_youtube_api()
    sys.exit(0 if success else 1)
