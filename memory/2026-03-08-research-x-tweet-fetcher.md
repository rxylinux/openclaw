# GitHub 项目研究：x-tweet-fetcher

## 基本信息

- **项目名称**: x-tweet-fetcher
- **仓库地址**: https://github.com/ythx-101/x-tweet-fetcher
- **作者**: ythx-101
- **最新版本**: 1.6.1 (2026-03-04)
- **Stars**: 358
- **Forks**: 27
- **主要语言**: Python
- **Open Issues**: 0
- **许可证**: MIT

---

## 项目概述

### 核心价值

**无需登录或 API 密钥即可从 X/Twitter 获取推文、评论、时间线和文章**，专为 AI Agent 设计的 Python 工具包。

### 解决的问题

```
You: fetch that tweet for me
AI: I can't access X/Twitter. Please copy-paste the content manually.

You: ...seriously?
```

X 没有免费 API。爬虫会被封禁。浏览器自动化脆弱。

**x-tweet-fetcher** 解决了这个问题：一条命令 → 结构化 JSON，直接供 Agent 消费。无需 API 密钥、无需登录、无需 Cookie。

---

## 功能矩阵

| 功能 | 零依赖 | 需要 Camofox | 输出 |
|------|--------|-------------|------|
| 单条推文 | ✅ | — | 文本、统计数据、媒体、引用推文 |
| 回复评论 | — | ✅ | 线程化评论树 |
| 用户时间线 | — | ✅ | 分页推文列表（最多 200 条） |
| X 文章（长文） | — | ✅ | 完整文章文本 |
| X Lists | — | ✅ | 分页推文列表 |
| @mentions 监控 | — | ✅ | 增量新提及 |
| 微信文章搜索 | ✅ | — | 标题、URL、作者、日期 |
| 推文发现 | ✅ | 可选 | 关键词搜索结果 |
| Google 搜索 | — | ✅ | 零 API Key 替代方案 |
| 中国平台 | 部分 | ✅ | 微博/B站/CSDN/微信 |
| 用户画像分析 | — | ✅ + LLM | MBTI、大五人格、话题图谱 |

---

## 技术架构

### 架构图

```
                    ┌─────────────┐
 --url              │  FxTwitter  │  ← Public API, no auth
                    │  (free)     │
                    └──────┬──────┘
                           │ JSON
┌──────────┐       ┌──────┴──────┐       ┌──────────┐
│ --replies│       │             │       │  Agent   │
│ --user   │──────▶│  Camofox    │──────▶│  (JSON)  │
│ --monitor│       │  (browser)  │       │          │
│ --list   │       └─────────────┘       └──────────┘
└──────────┘
                    ┌─────────────┐
 --keyword          │ DuckDuckGo  │  ← No API key
 sogou_wechat       │ Sogou       │
                    └─────────────┘
```

### 技术栈

- **基础推文**: FxTwitter public API (无需认证)
- **评论/时间线/Mentions**: Camofox headless Firefox + Nitter 解析
- **Views 补充**: FxTwitter API 自动填充 Nitter 缺失的浏览量
- **微信搜索**: Sogou 搜索（直接 HTTP，无需浏览器）
- **推文发现**: DuckDuckGo + Camofox Google 备选
- **中国平台**: 微信直接 HTTP；其他通过 Camofox

### Camofox 依赖

Camofox 是基于 Camoufox 的反检测浏览器服务（Firefox fork，C++ 级指纹伪装），可以绕过：
- Cloudflare 机器人检测
- 浏览器指纹识别
- JavaScript 挑战

**安装方式**：
```bash
# 方式 1: OpenClaw 插件
openclaw plugins install @askjo/camofox-browser

# 方式 2: 独立安装
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser && npm install && npm start  # Port 9377
```

---

## 文件结构

```
x-tweet-fetcher/
├── SKILL.md                    # OpenClaw Skill 定义
├── README.md                   # 完整文档
├── CHANGELOG.md                # 更新日志
├── VERSION                     # 版本号 (1.6.1)
├── scripts/
│   ├── __init__.py             # 包初始化
│   ├── fetch_tweet.py          # 主获取器（79.2KB）
│   ├── fetch_china.py          # 中国平台获取器（70.6KB）
│   ├── camofox_client.py       # Camofox REST API 客户端（8.5KB）
│   ├── sogou_wechat.py         # 微信文章搜索（14.1KB）
│   ├── x_discover.py           # 推文发现（4.3KB）
│   ├── x_mentions_nitter.py    # Nitter 提及监控（4.2KB）
│   └── version_check.py        # 版本检查（3.3KB）
└── .gitignore
```

---

## 核心功能详解

### 1. 单条推文获取（零依赖）

```bash
# JSON 输出
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# 仅文本输出
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# 美化 JSON
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

**支持的内容类型**：
- ✅ 常规推文（完整文本 + 统计数据）
- ✅ 长推文（Twitter Blue）
- ✅ X 文章（长文完整文本）
- ✅ 引用推文（自动包含）
- ✅ 统计数据（点赞/转发/浏览）
- ✅ 媒体 URL（图片 + 视频）

### 2. 回复线程（需要 Camofox）

```bash
# 获取推文 + 所有回复（包括嵌套回复）
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies

# 纯文本模式
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies --text-only
```

### 3. 用户时间线（需要 Camofox）

```bash
# 获取用户最新推文（支持分页，MAX_PAGES=20）
python3 scripts/fetch_tweet.py --user <username> --limit 300
```

### 4. X Lists（需要 Camofox）

```bash
# 获取 X Lists 推文
python3 scripts/fetch_tweet.py --list "https://x.com/i/lists/123456"

# 或直接使用 ID
python3 scripts/fetch_tweet.py --list "123456"
```

**特性**：
- 支持纯数字 ID 和完整 URL
- 零 API Key（通过 Camofox + Nitter）
- 支持翻页（MAX_PAGES=10）和去重
- 支持 `--text-only` 纯文本和 JSON 输出

### 5. @mentions 监控（需要 Camofox）

```bash
# 监控 @username 的新提及（cron 友好）
python3 scripts/fetch_tweet.py --monitor @username
```

**特性**：
- 基于 Google 搜索（通过 Camofox），零 API key
- 增量检测 — 首次建基线，后续只报新内容
- 支持 cron 集成（退出码 0=无新 / 1=有新 / 2=错误）
- 本地缓存去重（~/.x-tweet-fetcher/）

**Cron 集成示例**：
```bash
# 每 30 分钟检查提及
*/30 * * * * python3 fetch_tweet.py --monitor @username || notify-send "New mentions!"

# 每日发现推文
0 9 * * * python3 x_discover.py --keywords "AI Agent" --cache ~/.cache/discover.json --json >> ~/discoveries.jsonl
```

### 6. 中国平台支持

#### 微信文章（无需 Camofox）
```bash
python3 scripts/sogou_wechat.py --keyword "AI Agent" --limit 10 --json
```

#### 其他平台（需要 Camofox）
```bash
# 自动从 URL 识别平台
python3 scripts/fetch_china.py --url "https://weibo.com/..."      # 微博
python3 scripts/fetch_china.py --url "https://bilibili.com/..."   # B站
python3 scripts/fetch_china.py --url "https://csdn.net/..."       # CSDN
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/..." # 微信（无需 Camofox！）
```

**平台状态**：
| 平台 | 状态 | 说明 |
|------|------|------|
| 微信文章 | ✅ | 直接使用 web_fetch，无需 Camofox |
| 微博 | ✅ | Camofox 渲染 JS |
| B站 | ✅ | 视频信息 + 统计数据 |
| CSDN | ✅ | 文章 + 代码块 |
| 小红书 | ✅ | 支持 `--proxy` 和 `--cookies` |
| 知乎/小红书 | ⚠️ | 需要导入 cookie 登录 |

### 7. Google 搜索（零 API Key）

```python
from scripts.camofox_client import camofox_search
results = camofox_search("your search query")
# Returns: [{"title": "...", "url": "...", "snippet": "..."}, ...]
```

```bash
# CLI
python3 scripts/camofox_client.py "your search query"
```

**特点**：
- 使用 Camofox 浏览器直接搜索 Google
- 无需 Brave API key，零成本
- 绕过 Cloudflare 和反爬虫检测

---

## 输出格式

### JSON 输出示例

```json
{
  "url": "https://x.com/user/status/123",
  "username": "user",
  "tweet_id": "123",
  "tweet": {
    "text": "Tweet content...",
    "author": "Display Name",
    "screen_name": "username",
    "likes": 100,
    "retweets": 50,
    "bookmarks": 25,
    "views": 10000,
    "replies_count": 30,
    "created_at": "Mon Jan 01 12:00:00 +0000 2026",
    "is_note_tweet": false,
    "is_article": true,
    "article": {
      "title": "Article Title",
      "full_text": "Complete article content...",
      "word_count": 4847
    }
  },
  "replies": [
    {
      "author": "@someone",
      "text": "Reply text...",
      "likes": 5,
      "links": ["https://github.com/..."],
      "thread_replies": [{"text": "Nested reply..."}]
    }
  ]
}
```

---

## 依赖要求

| | 必需 | 可选 |
|--|------|------|
| **运行时** | Python 3.7+ | — |
| **基础推文** | 无其他依赖 | — |
| **高级功能** | Camofox | `duckduckgo-search` (pip) |
| **画像分析** | Camofox + LLM API key | — |

---

## 版本历史

### [1.6.1] - 2026-03-04
**修复**：
- 转推/引用推文分离：新增 `retweeted_by` 和 `quoted_tweet` 字段
- Stats 提取修复：icon 字符正则支持逗号分隔数字
- 内容识别修复：避免误判 TOC link
- 正则容错：stats 末尾允许非数字字符

### [1.6.0] - 2026-03-04
**新增**：
- X Lists 抓取：`--list <id_or_url>`

### [1.5.0] - 2026-02-25
**新增**：
- Nitter Mentions 监控
- version_check.py 自动版本检查工具

### [1.4.0] - 2026-02-24
**新增**：
- 小红书支持
- 搜狗微信搜索 `--resolve` 和 `--via-ssh`
- 路由器代理 `--via-router`

### [1.3.0] - 2026-02-23
**新增**：
- Mentions 监控：`--monitor @username`

### [1.2.0] - 2026-02-20
**新增**：
- 国内平台支持：微博、B站、CSDN、微信公众号
- 共享模块：camofox_client.py
- 多输出格式：JSON/Markdown/纯文本
- 自动平台识别
- 双语 README

### [1.1.0] - 2026-02-20
**修复**：
- 评论区链接提取
- 嵌套评论支持

### [1.0.0] - 2026-02-14
**初始发布**：
- 单条推文、评论区、用户时间线、X 文章、引用推文、双语支持

---

## 技术亮点

### 1. 零依赖推文获取
使用 FxTwitter 公共 API，无需任何认证或第三方库，直接获取推文内容和统计数据。

### 2. 反爬虫设计
通过 Camofox（基于 Camoufox）实现 C++ 级指纹伪装，有效绕过 Cloudflare、浏览器指纹识别和 JavaScript 挑战。

### 3. 增量监控机制
mentions 监控使用本地缓存和基线比较，首次运行建立基线，后续只报告新增内容，节省资源。

### 4. Cron 友好设计
退出码标准化：
- `0` = 无新内容
- `1` = 发现新内容
- `2` = 错误

便于集成到自动化工作流。

### 5. 多语言支持
内置中英文双语消息系统，根据 `--lang` 参数动态切换。

### 6. 策略模式架构
中国平台支持采用 Strategy Pattern，每个平台独立 Parser，社区可轻松扩展。

---

## 适用场景

### 适合使用的情况

1. **AI Agent 需要访问 Twitter 数据**：无需 API key，直接获取结构化数据
2. **社交媒体监控**：监控关键词、@mentions、用户时间线
3. **内容聚合**：从多个平台抓取内容（Twitter + 微博 + B站 + CSDN + 微信）
4. **数据分析**：批量获取推文、评论进行情感分析、趋势分析
5. **自动化工作流**：Cron 集成，定期监控和报告

### 不适合的情况

1. **需要实时数据**：有延迟（Nitter 同步、Google 索引）
2. **大规模爬取**：可能触发 Nitter 频率限制
3. **需要完整历史数据**：无法获取超过一定时间范围的数据
4. **需要登录私有账户**：只能获取公开内容

---

## 与现有工具的对比

### 与官方 Twitter API 对比

| 维度 | x-tweet-fetcher | Twitter API |
|------|----------------|-------------|
| 成本 | 免费 | 付费（$100+/月）|
| 认证 | 无需 | 需要密钥 |
| 速率限制 | 较宽松（Nitter）| 严格 |
| 实时性 | 有延迟 | 实时 |
| 数据完整性 | 公开内容 | 完整权限 |

### 与其他爬虫工具对比

| 维度 | x-tweet-fetcher | 传统爬虫 |
|------|----------------|----------|
| 反检测能力 | 高（Camofox） | 低 |
| 易用性 | 高（CLI + Python API） | 需要编程 |
| 维护成本 | 低 | 高（频繁失效）|
| 稳定性 | 较高 | 低 |

---

## 潜在改进方向

1. **性能优化**：并行处理多个请求
2. **错误恢复**：失败重试机制
3. **数据缓存**：避免重复抓取
4. **更多平台**：支持 Threads、Mastodon 等
5. **实时推送**：WebSocket 支持
6. **分布式抓取**：支持多节点协作

---

## 总结

**x-tweet-fetcher** 是一个设计精良、功能强大的 Twitter 数据获取工具，特别适合 AI Agent 使用。

**优势**：
- ✅ 零依赖、零 API key
- ✅ 反爬虫能力强（Camofox）
- ✅ 输出结构化 JSON，易于集成
- ✅ 支持多平台（Twitter + 中国平台）
- ✅ Cron 友好，适合自动化
- ✅ 活跃维护（最近更新：2026-03-04）

**劣势**：
- ⚠️ Camofox 需要额外部署
- ⚠️ 高级功能需要 Camofox
- ⚠️ 实时性不如官方 API

**推荐使用场景**：
- AI Agent 需要访问 Twitter 数据
- 社交媒体监控和内容聚合
- 数据分析和研究
- 自动化工作流集成

---

## 研究时间

- **研究日期**: 2026-03-08
- **研究者**: rxy的狗腿子
- **研究方法**: GitHub API + 文档分析 + 代码审查
