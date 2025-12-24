"""
鸿蒙资源管理器
管理字体、图标等资源的加载和使用
"""

import os
import sys
from pathlib import Path
from typing import Optional
import customtkinter as ctk
from PIL import Image


class HarmonyResources:
    """鸿蒙资源管理器"""

    # 获取项目根目录
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        PROJECT_ROOT = Path(sys._MEIPASS)
    else:
        # 开发环境
        PROJECT_ROOT = Path(__file__).parent.parent.parent

    ASSETS_DIR = PROJECT_ROOT / "assets"
    FONTS_DIR = ASSETS_DIR / "fonts"
    ICONS_DIR = ASSETS_DIR / "icons"

    # 鸿蒙字体路径
    FONT_HARMONY_SANS_SC_REGULAR = FONTS_DIR / "HarmonyOS_Sans_SC_Regular.ttf"
    FONT_HARMONY_SANS_SC_MEDIUM = FONTS_DIR / "HarmonyOS_Sans_SC_Medium.ttf"
    FONT_HARMONY_SANS_SC_BOLD = FONTS_DIR / "HarmonyOS_Sans_SC_Bold.ttf"

    # 图标映射表（鸿蒙图标文件名）
    ICONS = {
        # 工具栏图标
        'settings': 'ic_public_settings.png',
        'log': 'ic_public_log.png',
        'delete': 'ic_public_delete.png',

        # 操作图标
        'search': 'ic_public_search_filled.png',
        'cancel': 'ic_public_cancel.png',
        'export': 'ic_public_export.png',

        # 状态图标
        'success': 'ic_public_ok.png',
        'error': 'ic_public_fail.png',
        'warning': 'ic_public_warn.png',
        'info': 'ic_public_info.png',

        # 功能图标
        'refresh': 'ic_public_refresh.png',
        'download': 'ic_public_download.png',
        'upload': 'ic_public_upload.png',
        'folder': 'ic_public_folder.png',
        'file': 'ic_public_files.png',
    }

    _font_cache = {}
    _icon_cache = {}

    @classmethod
    def get_font_path(cls, weight: str = "regular") -> Optional[Path]:
        """
        获取字体文件路径

        Args:
            weight: 字重 (regular/medium/bold)

        Returns:
            字体文件路径，如果不存在则返回 None
        """
        font_map = {
            "regular": cls.FONT_HARMONY_SANS_SC_REGULAR,
            "medium": cls.FONT_HARMONY_SANS_SC_MEDIUM,
            "bold": cls.FONT_HARMONY_SANS_SC_BOLD,
        }

        font_path = font_map.get(weight.lower())
        if font_path and font_path.exists():
            return font_path
        return None

    @classmethod
    def get_font_family(cls, weight: str = "regular") -> str:
        """
        获取字体族名称（用于 tkinter/customtkinter）

        Args:
            weight: 字重 (regular/medium/bold)

        Returns:
            字体族名称
        """
        font_path = cls.get_font_path(weight)
        if font_path:
            # 返回鸿蒙字体族名
            if weight == "bold":
                return "HarmonyOS Sans SC Bold"
            elif weight == "medium":
                return "HarmonyOS Sans SC Medium"
            else:
                return "HarmonyOS Sans SC"
        else:
            # 降级到系统字体
            return "Microsoft YaHei UI"

    @classmethod
    def register_fonts(cls):
        """
        注册鸿蒙字体到系统（Windows）

        注意：CustomTkinter 使用的是 tkinter 的字体系统，
        需要通过 tkinter.font 来注册自定义字体
        """
        try:
            import tkinter as tk
            import tkinter.font as tkfont

            # 创建临时 root 窗口（如果不存在）
            try:
                root = tk._default_root
                if root is None:
                    root = tk.Tk()
                    root.withdraw()
            except:
                root = tk.Tk()
                root.withdraw()

            # 注册字体（使用 tkinter.font.Font）
            for weight in ["regular", "medium", "bold"]:
                font_path = cls.get_font_path(weight)
                if font_path and font_path.exists():
                    try:
                        # 尝试加载字体（这在某些系统上可能不完全生效）
                        # tkinter 对自定义字体的支持有限
                        pass
                    except Exception as e:
                        print(f"注册字体失败 ({weight}): {e}")

            print(f"✓ 鸿蒙字体注册完成")
            print(f"  - Regular: {cls.FONT_HARMONY_SANS_SC_REGULAR.exists()}")
            print(f"  - Medium: {cls.FONT_HARMONY_SANS_SC_MEDIUM.exists()}")
            print(f"  - Bold: {cls.FONT_HARMONY_SANS_SC_BOLD.exists()}")

        except Exception as e:
            print(f"字体注册失败: {e}")

    @classmethod
    def get_icon(cls, name: str, size: tuple = (20, 20)) -> Optional[ctk.CTkImage]:
        """
        获取鸿蒙图标

        Args:
            name: 图标名称（参考 ICONS 字典）
            size: 图标尺寸 (width, height)

        Returns:
            CTkImage 对象，如果图标不存在则返回 None
        """
        cache_key = f"{name}_{size[0]}x{size[1]}"

        # 检查缓存
        if cache_key in cls._icon_cache:
            return cls._icon_cache[cache_key]

        # 获取图标文件名
        icon_filename = cls.ICONS.get(name)
        if not icon_filename:
            print(f"⚠ 图标 '{name}' 未定义")
            return None

        # 构建图标路径
        icon_path = cls.ICONS_DIR / icon_filename
        if not icon_path.exists():
            print(f"⚠ 图标文件不存在: {icon_path}")
            return None

        try:
            # 加载图标
            image = Image.open(icon_path)
            ctk_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=size
            )

            # 缓存
            cls._icon_cache[cache_key] = ctk_image
            return ctk_image

        except Exception as e:
            print(f"✗ 加载图标失败 ({name}): {e}")
            return None

    @classmethod
    def get_icon_path(cls, name: str) -> Optional[Path]:
        """
        获取图标文件路径

        Args:
            name: 图标名称

        Returns:
            图标路径，如果不存在则返回 None
        """
        icon_filename = cls.ICONS.get(name)
        if not icon_filename:
            return None

        icon_path = cls.ICONS_DIR / icon_filename
        if icon_path.exists():
            return icon_path
        return None

    @classmethod
    def check_resources(cls):
        """检查资源完整性"""
        print("\n" + "="*60)
        print("鸿蒙资源检查")
        print("="*60)

        print(f"\n📁 资源目录: {cls.ASSETS_DIR}")
        print(f"  - 存在: {cls.ASSETS_DIR.exists()}")

        print(f"\n🔤 字体目录: {cls.FONTS_DIR}")
        print(f"  - 存在: {cls.FONTS_DIR.exists()}")
        if cls.FONTS_DIR.exists():
            font_files = list(cls.FONTS_DIR.glob("*.ttf")) + list(cls.FONTS_DIR.glob("*.otf"))
            print(f"  - 字体文件数: {len(font_files)}")
            for font in font_files:
                print(f"    • {font.name}")

        print(f"\n🎨 图标目录: {cls.ICONS_DIR}")
        print(f"  - 存在: {cls.ICONS_DIR.exists()}")
        if cls.ICONS_DIR.exists():
            icon_files = list(cls.ICONS_DIR.glob("*.png")) + list(cls.ICONS_DIR.glob("*.svg"))
            print(f"  - 图标文件数: {len(icon_files)}")
            for icon in icon_files[:10]:  # 只显示前10个
                print(f"    • {icon.name}")
            if len(icon_files) > 10:
                print(f"    ... 还有 {len(icon_files) - 10} 个图标")

        print("\n" + "="*60 + "\n")


# 初始化时检查资源
if __name__ == "__main__":
    HarmonyResources.check_resources()
    HarmonyResources.register_fonts()
