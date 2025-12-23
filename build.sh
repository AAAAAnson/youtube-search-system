#!/bin/bash
# YouTube 数据采集工具 - Linux/Mac 打包脚本
# 注意：此脚本生成的可执行文件仅能在对应系统运行

echo "=========================================="
echo " YouTube 数据采集工具 - 打包程序"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装"
    exit 1
fi

echo "[1/4] 检查依赖..."
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "[提示] PyInstaller 未安装，正在安装..."
    python3 -m pip install pyinstaller
fi

echo ""
echo "[2/4] 安装项目依赖..."
python3 -m pip install -r requirements.txt

echo ""
echo "[3/4] 清理旧的打包文件..."
rm -rf build dist

echo ""
echo "[4/4] 开始打包（这可能需要 2-5 分钟）..."
python3 -m PyInstaller --clean youtube_tool.spec

echo ""
if [ -d "dist/YouTube数据采集工具" ]; then
    echo "=========================================="
    echo " 打包完成！"
    echo "=========================================="
    echo ""
    echo "可执行文件位置："
    echo "dist/YouTube数据采集工具/YouTube数据采集工具"
    echo ""
    echo "您可以："
    echo "1. 将整个 \"YouTube数据采集工具\" 文件夹复制到其他电脑使用"
    echo "2. 运行 ./dist/YouTube数据采集工具/YouTube数据采集工具"
    echo ""
    echo "注意：请不要删除文件夹中的其他文件，它们是程序运行所必需的"
    echo ""
else
    echo ""
    echo "[错误] 打包失败，请检查错误信息"
    exit 1
fi
