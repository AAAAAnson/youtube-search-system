# YouTube 数据采集工具 - 打包说明文档

## 📦 打包概述

本文档介绍如何将 YouTube 数据采集工具打包成 Windows 可执行文件（.exe）。

## 🖥️ 系统要求

### Windows 打包环境
- Windows 10/11（64位）
- Python 3.8 或更高版本
- 至少 2GB 可用磁盘空间
- 管理员权限（用于安装依赖）

### 其他系统
- Linux / macOS 也可以打包，但生成的可执行文件仅能在对应系统运行
- Windows 可执行文件只能在 Windows 系统上打包

## 🚀 快速打包（Windows）

### 方法一：使用批处理脚本（推荐）

1. **下载项目代码**
   ```bash
   git clone https://github.com/你的仓库/youtube-search-system.git
   cd youtube-search-system
   ```

2. **双击运行打包脚本**
   - 找到项目根目录的 `build.bat` 文件
   - 双击运行
   - 按照提示完成打包

3. **打包完成**
   - 可执行文件位于：`dist\YouTube数据采集工具\`
   - 主程序：`YouTube数据采集工具.exe`

### 方法二：手动打包

1. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **执行打包命令**
   ```bash
   pyinstaller --clean youtube_tool.spec
   ```

3. **等待打包完成**
   - 时间：约 2-5 分钟
   - 输出目录：`dist\YouTube数据采集工具\`

## 📁 打包输出结构

```
dist/
└── YouTube数据采集工具/
    ├── YouTube数据采集工具.exe  ← 主程序（双击运行）
    ├── _internal/                  ← 依赖文件（不可删除）
    │   ├── customtkinter/
    │   ├── google/
    │   ├── pandas/
    │   └── ... (其他依赖库)
    └── ... (其他运行时文件)
```

**重要提示**：
- ✅ 可以将整个 `YouTube数据采集工具` 文件夹复制到其他 Windows 电脑使用
- ❌ 不要删除文件夹中的任何文件
- ❌ 不要单独复制 .exe 文件，必须保持文件夹完整

## 🎨 自定义图标（可选）

如果您想更换程序图标：

1. **准备图标文件**
   - 格式：`.ico` 文件
   - 尺寸：256x256 或更小
   - 命名：`icon.ico`

2. **放置图标**
   ```
   youtube-search-system/
   └── assets/
       └── icon.ico  ← 放在这里
   ```

3. **重新打包**
   - 再次运行 `build.bat` 或打包命令

## 🔧 打包配置说明

### spec 文件（youtube_tool.spec）

关键配置项：

```python
# 是否显示控制台窗口
console=False  # False = 不显示（推荐）, True = 显示

# 打包模式
exclude_binaries=True   # 文件夹模式（推荐）
# exclude_binaries=False  # 单文件模式（不推荐，启动慢）

# UPX 压缩
upx=True  # 压缩可执行文件（减小体积）
```

### 文件夹模式 vs 单文件模式

| 模式 | 体积 | 启动速度 | 推荐 |
|------|------|----------|------|
| **文件夹模式** | ~100MB | 快（2-3秒） | ✅ 推荐 |
| 单文件模式 | ~80MB | 慢（5-10秒） | ❌ 不推荐 |

**我们使用文件夹模式**，因为：
- 启动速度更快
- 更容易调试
- 杀毒软件误报率更低

## 🐛 常见问题

### 1. 打包失败：ModuleNotFoundError

**问题**：提示找不到某个模块

**解决方案**：
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清理缓存后重新打包
rmdir /s /q build dist
pyinstaller --clean youtube_tool.spec
```

### 2. 杀毒软件误报

**问题**：Windows Defender 或其他杀毒软件报毒

**原因**：PyInstaller 打包的程序容易被误报

**解决方案**：
- 将程序添加到杀毒软件白名单
- 或使用代码签名（需要证书，成本较高）

### 3. 程序无法启动

**问题**：双击 .exe 没有反应

**调试方法**：
1. 修改 `youtube_tool.spec`：
   ```python
   console=True  # 改为 True，显示控制台窗口
   ```

2. 重新打包

3. 再次运行，查看控制台错误信息

### 4. 打包体积过大

**当前体积**：约 100-150 MB（正常）

**如果超过 300 MB**，检查是否包含了不必要的库：
```bash
# 排除不需要的库
pip uninstall matplotlib scipy
```

### 5. 缺少 DLL 文件

**问题**：提示缺少 `vcruntime140.dll` 等

**解决方案**：
安装 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## 📊 打包性能优化

### 减小体积

1. **排除不需要的模块**
   ```python
   # 在 youtube_tool.spec 中添加
   excludes=[
       'matplotlib',
       'scipy',
       'numpy.random._examples',
       'test',
       'unittest',
   ]
   ```

2. **启用 UPX 压缩**
   ```python
   upx=True
   ```

### 提升启动速度

- 使用文件夹模式（已配置）
- 减少 `hiddenimports`（只保留必需的）

## 🔐 代码签名（可选）

如果您想避免杀毒软件误报：

1. **购买代码签名证书**
   - 价格：约 $100-300/年
   - 推荐：DigiCert、Sectigo

2. **使用 SignTool 签名**
   ```bash
   signtool sign /f "证书.pfx" /p "密码" /t "http://timestamp.digicert.com" "YouTube数据采集工具.exe"
   ```

## 📦 分发建议

### 压缩发布

```bash
# 将打包好的文件夹压缩为 ZIP
cd dist
tar -a -c -f YouTube数据采集工具_v1.0.0.zip "YouTube数据采集工具"
```

### 云盘分发

推荐上传到：
- 百度网盘
- 阿里云盘
- GitHub Releases

### 安装说明

为用户提供 `安装说明.txt`：
```
YouTube 数据采集工具 v1.0.0

安装步骤：
1. 解压 ZIP 文件到任意目录
2. 双击运行 "YouTube数据采集工具.exe"
3. 首次运行会要求配置 API Key

注意事项：
- 需要联网使用
- Windows 10/11 系统
- 如遇杀毒软件拦截，请添加到白名单
```

## 🧪 测试清单

打包完成后，请测试以下功能：

- [ ] 程序能正常启动
- [ ] 首次启动向导显示正常
- [ ] 能添加 YouTube API Key
- [ ] 能添加 DeepSeek API Key
- [ ] 搜索功能正常
- [ ] 进度显示正常
- [ ] 数据预览正常
- [ ] Excel 导出正常
- [ ] 日志功能正常
- [ ] 缓存功能正常

## 📞 技术支持

如果打包过程中遇到问题：

1. 检查 Python 版本：`python --version`
2. 检查依赖安装：`pip list`
3. 查看打包日志：`build\youtube_tool\warn-youtube_tool.txt`
4. 提交 Issue：附上错误信息和系统环境

## 📚 参考资料

- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)
- [CustomTkinter 打包指南](https://customtkinter.tomschimansky.com/documentation/packaging)
- [Python 打包最佳实践](https://packaging.python.org/)

---

**最后更新**: 2025-01-23
**版本**: 1.0.0
