# YouTube 数据采集工具

一个功能强大的 YouTube 视频数据采集工具，支持批量搜索、数据提取、联系方式智能分析和 Excel 导出。

## ✨ 主要功能

- 🔍 **关键词搜索**：根据关键词批量搜索 YouTube 视频（最多1000条）
- 📊 **数据提取**：自动获取播放量、点赞数、评论数等详细数据
- 🤖 **智能分析**：使用 AI 自动提取 KOL 联系方式（邮箱、微信、官网等）
- 🔑 **多 API Key 管理**：支持批量导入和智能轮换，突破配额限制
- 📈 **进度追踪**：实时显示采集进度和预计剩余时间
- 📁 **Excel 导出**：一键导出为格式化的 Excel 表格

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python src/main.py
```

### 首次使用

1. 启动程序后会自动打开配置向导
2. 按照提示配置 YouTube API Key 和 DeepSeek API Key
3. 完成配置后即可开始使用

## 📋 数据字段

导出的 Excel 表格包含以下字段：

| 字段 | 说明 |
|------|------|
| keyword | 搜索关键词 |
| KOL名称 | 频道名称 |
| 视频链接 | 完整视频URL |
| 播放数量 | 播放次数 |
| 互动率 | (点赞+评论)/播放量 |
| 联系方式 | AI提取的联系方式 |
| 点赞数量 | 点赞次数 |
| 评论数量 | 评论次数 |
| 视频标题 | 视频标题 |
| 发布日期 | 发布日期 |
| 视频时长 | 视频时长 |
| 频道订阅数 | 频道订阅人数 |
| 视频语言 | 视频语言 |

## 🔑 API Key 获取

### YouTube Data API v3

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 "YouTube Data API v3"
4. 创建凭据（API 密钥）
5. 复制 API Key 到工具中

### DeepSeek API

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册并登录账号
3. 在 API Keys 页面创建新密钥
4. 复制 API Key 到工具中

## 📊 配额说明

- **YouTube API**：每个 Key 每天有 10,000 配额单位
- **采集1000个视频**：约消耗 3,500 配额单位（35%）
- **建议配置**：3个以上 API Key 以满足大量采集需求

## 🛠 技术栈

- **语言**：Python 3.8+
- **UI**：CustomTkinter
- **API**：YouTube Data API v3, DeepSeek API
- **数据处理**：pandas, openpyxl

## 📖 详细文档

详细的技术规格和实现细节请参考 [CLAUDE.md](CLAUDE.md)

## ⚠️ 注意事项

- 请遵守 YouTube API 使用条款
- 合理控制请求频率，避免被封禁
- API Key 请妥善保管，不要泄露
- 定期清理缓存以释放存储空间

## 📝 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看 [CLAUDE.md](CLAUDE.md) 中的技术文档或提交 Issue。
