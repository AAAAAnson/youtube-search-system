#!/usr/bin/env python3
"""
资源导入脚本
帮助导入鸿蒙字体和图标到项目中
"""

import os
import shutil
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"


def extract_fonts(font_source: Path):
    """
    提取字体文件

    Args:
        font_source: 字体文件或目录路径
    """
    print(f"\n📦 处理字体: {font_source}")

    if font_source.is_file():
        # 单个字体文件
        if font_source.suffix.lower() in ['.ttf', '.otf']:
            dest = FONTS_DIR / font_source.name
            shutil.copy2(font_source, dest)
            print(f"  ✓ 复制字体: {font_source.name}")

        # 压缩包
        elif font_source.suffix.lower() == '.zip':
            with zipfile.ZipFile(font_source, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.lower().endswith(('.ttf', '.otf')):
                        zip_ref.extract(file, FONTS_DIR)
                        print(f"  ✓ 解压字体: {file}")

    elif font_source.is_dir():
        # 目录：复制所有字体文件
        for font_file in font_source.glob('**/*'):
            if font_file.suffix.lower() in ['.ttf', '.otf']:
                dest = FONTS_DIR / font_file.name
                shutil.copy2(font_file, dest)
                print(f"  ✓ 复制字体: {font_file.name}")


def extract_icons(icon_source: Path):
    """
    提取图标文件

    Args:
        icon_source: 图标文件或目录路径
    """
    print(f"\n📦 处理图标: {icon_source}")

    if icon_source.is_file():
        # 压缩包
        if icon_source.suffix.lower() == '.zip':
            with zipfile.ZipFile(icon_source, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.lower().endswith(('.png', '.svg', '.jpg', '.jpeg')):
                        # 保持目录结构
                        zip_ref.extract(file, ICONS_DIR)
                        print(f"  ✓ 解压图标: {file}")

    elif icon_source.is_dir():
        # 目录：复制所有图标文件
        for icon_file in icon_source.glob('**/*'):
            if icon_file.suffix.lower() in ['.png', '.svg', '.jpg', '.jpeg']:
                # 保持相对路径
                relative_path = icon_file.relative_to(icon_source)
                dest = ICONS_DIR / relative_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(icon_file, dest)
                print(f"  ✓ 复制图标: {relative_path}")


def setup_resources():
    """设置资源"""
    print("="*60)
    print("鸿蒙资源导入工具")
    print("="*60)

    # 创建目录
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ 资源目录已创建")
    print(f"  - 字体: {FONTS_DIR}")
    print(f"  - 图标: {ICONS_DIR}")

    # 扫描根目录查找资源
    print(f"\n🔍 扫描根目录: {PROJECT_ROOT}")

    found_resources = []

    # 查找可能的资源文件/目录
    for item in PROJECT_ROOT.iterdir():
        item_lower = item.name.lower()

        # 字体相关
        if any(keyword in item_lower for keyword in ['font', '字体', 'harmonyos', '鸿蒙']):
            if item.suffix.lower() in ['.ttf', '.otf', '.zip'] or item.is_dir():
                found_resources.append(('font', item))

        # 图标相关
        elif any(keyword in item_lower for keyword in ['icon', '图标', 'ic_', 'img', 'image']):
            if item.suffix.lower() == '.zip' or item.is_dir():
                found_resources.append(('icon', item))

    if not found_resources:
        print("\n⚠ 未在根目录找到资源文件")
        print("\n请手动操作：")
        print(f"  1. 将鸿蒙字体文件（.ttf/.otf）放到: {FONTS_DIR}")
        print(f"  2. 将鸿蒙图标文件（.png/.svg）放到: {ICONS_DIR}")
        print(f"\n或者将资源文件/压缩包放到项目根目录，重新运行本脚本")
        return

    # 处理找到的资源
    print(f"\n✓ 找到 {len(found_resources)} 个资源")

    for resource_type, resource_path in found_resources:
        print(f"\n  • {resource_path.name} ({resource_type})")
        confirm = input(f"    导入此资源? (y/n) [y]: ").strip().lower()

        if confirm in ['', 'y', 'yes']:
            try:
                if resource_type == 'font':
                    extract_fonts(resource_path)
                elif resource_type == 'icon':
                    extract_icons(resource_path)
            except Exception as e:
                print(f"  ✗ 导入失败: {e}")

    # 统计结果
    print("\n" + "="*60)
    print("导入完成")
    print("="*60)

    font_files = list(FONTS_DIR.glob('**/*.ttf')) + list(FONTS_DIR.glob('**/*.otf'))
    icon_files = list(ICONS_DIR.glob('**/*.png')) + list(ICONS_DIR.glob('**/*.svg'))

    print(f"\n📊 资源统计:")
    print(f"  - 字体文件: {len(font_files)} 个")
    for font in font_files:
        print(f"    • {font.name}")

    print(f"\n  - 图标文件: {len(icon_files)} 个")
    if len(icon_files) <= 20:
        for icon in icon_files:
            print(f"    • {icon.relative_to(ICONS_DIR)}")
    else:
        for icon in icon_files[:10]:
            print(f"    • {icon.relative_to(ICONS_DIR)}")
        print(f"    ... 还有 {len(icon_files) - 10} 个图标")

    print("\n✓ 资源已准备就绪！")
    print("\n下一步: 运行程序查看鸿蒙风格界面")
    print("  python src/main.py")


if __name__ == "__main__":
    setup_resources()
