@echo off
REM YouTube 数据采集工具 - Windows 打包脚本
REM 使用方法：在 Windows 命令提示符中运行此脚本

echo ==========================================
echo  YouTube 数据采集工具 - 打包程序
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [提示] PyInstaller 未安装，正在安装...
    pip install pyinstaller
)

echo.
echo [2/4] 安装项目依赖...
pip install -r requirements.txt

echo.
echo [3/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [4/4] 开始打包（这可能需要 2-5 分钟）...
pyinstaller --clean youtube_tool.spec

echo.
if exist "dist\YouTube数据采集工具" (
    echo ==========================================
    echo  打包完成！
    echo ==========================================
    echo.
    echo 可执行文件位置：
    echo dist\YouTube数据采集工具\YouTube数据采集工具.exe
    echo.
    echo 您可以：
    echo 1. 将整个 "YouTube数据采集工具" 文件夹复制到其他电脑使用
    echo 2. 双击 YouTube数据采集工具.exe 运行程序
    echo.
    echo 注意：请不要删除文件夹中的其他文件，它们是程序运行所必需的
    echo.

    REM 询问是否打开文件夹
    choice /c YN /m "是否打开输出文件夹？"
    if errorlevel 2 goto end
    if errorlevel 1 explorer "dist\YouTube数据采集工具"
) else (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

:end
pause
