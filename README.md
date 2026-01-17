# SocialScraper

这是一个通用的社交媒体数据抓取工具，目前支持 Twitter (通过 Nitter)。

## 功能特性

- **多平台架构**：设计为可扩展支持多个社交平台。
- **Twitter 抓取**：
  - 基于 Playwright 的浏览器自动化，绕过 JS 反爬验证。
  - 自动轮询多个 Nitter 实例，提高成功率。
  - 提取推文内容、时间、媒体链接等详细信息。

## 目录结构

```
SocialScraper/
├── app/
│   ├── api/             # API 路由
│   ├── core/            # 核心配置与日志
│   ├── models/          # 数据模型
│   └── services/        # 业务逻辑与爬虫
├── config.yml           # 配置文件
├── main.py              # 启动入口
├── requirements.txt     # 依赖列表
└── README.md
```

## 安装

1. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 安装 Playwright 浏览器：
   ```bash
   playwright install chromium
   ```

## 使用方法

### 启动 API 服务

```bash
# 启动服务（默认监听 127.0.0.1:8000）
python main.py

# 指定主机和端口
python main.py --host 0.0.0.0 --port 8080
```

服务启动后，可以通过 REST API 进行抓取。

### API 文档

访问 `http://127.0.0.1:8000/docs` 查看完整的 API 文档和测试接口。

### 调用示例

**抓取 Twitter 用户推文**：

```bash
curl http://127.0.0.1:8000/twitter/NASA?limit=5
```

响应示例：
```json
{
  "data": [ ... ],
  "count": 5,
  "platform": "twitter",
  "username": "NASA"
}
```

## 注意事项

- 请确保网络环境可以访问 Nitter 实例。
- 爬虫可能会因为目标网站的反爬策略更新而失效。
