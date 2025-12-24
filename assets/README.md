# 资源文件目录

## 📁 目录说明

此目录用于存放程序所需的资源文件，包括鸿蒙字体、图标等。

## 🎯 目录结构

```
assets/
├── fonts/          ← 鸿蒙字体文件（需手动放置）
├── icons/          ← 鸿蒙图标文件（需手动放置）
├── tutorial/       ← 教程图片
└── README.md       ← 本文件
```

---

## 🔤 鸿蒙字体（fonts/）

### 必需字体文件

放置以下字体文件到 `assets/fonts/` 目录：

1. **HarmonyOS_Sans_SC_Regular.ttf**
   - 用途：正文、辅助文字
   - 字重：Regular (400)

2. **HarmonyOS_Sans_SC_Medium.ttf**
   - 用途：小标题、按钮
   - 字重：Medium (500)

3. **HarmonyOS_Sans_SC_Bold.ttf**
   - 用途：大标题、重点强调
   - 字重：Bold (700)

### 获取方式

- **官方渠道**：华为开发者官网
- **许可协议**：遵循 HarmonyOS 字体许可协议
- **备用方案**：如果无法获取，程序会自动降级到系统字体（Microsoft YaHei UI）

### 导入方法

```bash
# 方式1：直接复制
cp HarmonyOS_Sans_SC_*.ttf /home/user/youtube-search-system/assets/fonts/

# 方式2：使用导入脚本
python setup_resources.py
```

---

## 🎨 鸿蒙图标（icons/）

### 必需图标列表

放置以下图标文件到 `assets/icons/` 目录：

| 图标名称 | 文件名 | 用途 | 尺寸 |
|---------|--------|------|------|
| 设置 | `ic_public_settings.png` | API管理按钮 | 20x20 |
| 日志 | `ic_public_log.png` | 查看日志按钮 | 20x20 |
| 删除 | `ic_public_delete.png` | 清除缓存按钮 | 20x20 |
| 搜索 | `ic_public_search_filled.png` | 开始搜索按钮 | 24x24 |
| 导出 | `ic_public_export.png` | 导出Excel按钮 | 24x24 |
| 取消 | `ic_public_cancel.png` | 取消按钮 | 20x20 |

### 可选图标

扩展功能预留：
- `ic_public_ok.png` - 成功提示
- `ic_public_fail.png` - 错误提示
- `ic_public_warn.png` - 警告提示
- `ic_public_info.png` - 信息提示
- `ic_public_refresh.png` - 刷新
- `ic_public_download.png` - 下载
- `ic_public_folder.png` - 文件夹
- `ic_public_files.png` - 文件

### 获取方式

- **官方渠道**：HarmonyOS 图标库
- **格式要求**：PNG 格式，透明背景，单色图标
- **备用方案**：如果没有图标，程序会使用 emoji 替代 (⚙️ 📋 🗑️ 🚀 📊)

---

## 📥 资源导入

### 使用导入脚本（推荐）

```bash
# 1. 将字体包/图标压缩包放到项目根目录
# 2. 运行导入脚本
python setup_resources.py
# 3. 按照提示选择导入资源
```

### 手动放置

```bash
# 字体
cp HarmonyOS_Sans_SC_*.ttf assets/fonts/

# 图标
cp ic_public_*.png assets/icons/
```

### 检查资源

```bash
python -m src.gui.harmony_resources
```

---

## 🔄 自动降级机制

**即使没有鸿蒙资源，程序也能正常运行：**

| 资源 | 有资源 | 无资源（自动降级） |
|------|--------|-------------------|
| 字体 | ✓ HarmonyOS Sans SC | → Microsoft YaHei UI |
| 图标 | ✓ PNG 图标 | → emoji (⚙️ 📋 🗑️ 🚀 📊) |

---

## 🎨 图标文件（icon.ico）

### 添加自定义图标

如果您想为打包后的程序添加自定义图标：

1. **准备图标文件**
   - 格式：`.ico` 格式
   - 推荐尺寸：256x256 像素
   - 文件名：`icon.ico`

2. **放置位置**
   - 将 `icon.ico` 文件放在此目录（`assets/`）下

3. **图标生成工具**
   - 在线工具：[ConvertICO](https://www.convertico.com/)
   - 本地工具：[IcoFX](https://icofx.ro/)

4. **从 PNG 转换为 ICO**
   - 准备一张 PNG 图片（推荐 256x256）
   - 使用上述工具转换为 .ico 格式

### 当前状态

目前项目中**未包含**图标文件。

如果不添加图标：
- 打包后的程序将使用 Python 默认图标
- 功能不受影响，仅影响外观

### 推荐图标设计

建议图标包含以下元素：
- YouTube 相关视觉（红色、播放按钮等）
- 数据/表格相关（Excel 绿色等）
- 简洁明了，易于识别

**注意**：请确保使用的图标符合版权要求，避免侵权。

---

## 📚 教程图片（tutorial/）

此子目录可用于存放：
- API Key 获取教程的截图
- 使用说明图片
- 帮助文档配图

目前为空，可根据需要添加。
