# Agent-Reach 项目总结

## 📊 项目概况

**GitHub地址：** https://github.com/Panniantong/Agent-Reach
**项目定位：** 给AI Agent一键装上互联网能力
**开源协议：** MIT License
**Python版本：** Python 3.8+

---

## 🎯 核心价值

### 解决的问题

AI Agent已经能帮你写代码、改文档、管项目——但你让它去网上找点东西，它就抓瞎了：

1. **YouTube字幕提取** → 看不了，拿不到字幕
2. **Twitter/X搜索** → 搜不了，Twitter API要付费
3. **Reddit访问** → 403被封，服务器IP被拒
4. **小红书访问** → 打不开，必须登录才能看
5. **B站访问** → 连不上，海外/服务器IP被屏蔽
6. **全网搜索** → 没有好用的搜索，要么付费要么质量差
7. **网页读取** → 抓回来一堆HTML标签，根本没法读
8. **GitHub访问** → 能用，但认证配置很麻烦
9. **RSS订阅** → 要自己装库写代码

### Agent Reach的方案

**一句话安装：**
```
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

复制给你的Agent，几分钟后它就能读推特、搜Reddit、看YouTube、刷小红书了。

**Star这个项目**，我们会持续追踪各平台的变化、接入新的渠道。你不用自己盯——平台封了我们修，有新渠道我们加。

---

## ✅ 特性

### 1. 完全免费
- 所有工具开源
- 所有API免费
- 唯一可能花钱的是服务器代理（$1/月），本地电脑不需要

### 2. 隐私安全
- Cookie只存在你本地，不上传不外传
- 代码完全开源，随时可审查

### 3. 持续更新
- 底层工具（yt-dlp、bird、Jina Reader等）定期追踪更新到最新版
- 你不用自己盯

### 4. 兼容所有Agent
- Claude Code
- OpenClaw
- Cursor
- Windsurf
- 任何能跑命令行的Agent都能用

### 5. 自带诊断
- `agent-reach doctor`一条命令告诉你哪个通、哪个不通、怎么修

---

## 🌐 支持的平台

### 装好即用

| 平台 | 能力 | 配置 |
|-----|------|------|
| 🌐 网页 | 阅读任意网页 | 无需配置 |
| 📺 YouTube | 字幕提取+视频搜索 | 无需配置 |
| 📡 RSS | 阅读任意RSS/Atom源 | 无需配置 |
| 🔍 全网搜索 | — | 全网语义搜索 | 自动配置（MCP接入，免费无需Key） |
| 📦 GitHub | 读公开仓库+搜索 | 私有仓库、提Issue/PR、Fork | 告诉Agent「帮我登录GitHub」 |

### 配置后解锁

| 平台 | 能力 | 怎么配 |
|-----|------|--------|
| 🐦 Twitter/X | 读单条推文 | 搜索推文、浏览时间线、发推 | 告诉Agent「帮我配Twitter」 |
| 📺 B站 | 本地：字幕提取+搜索 | 服务器也能用 | 告诉Agent「帮我配代理」 |
| 📖 Reddit | 搜索（通过Exa免费） | 读帖子和评论 | 告诉Agent「帮我配代理」 |
| 📕 小红书 | — | 阅读、搜索、发帖、评论、点赞 | 告诉Agent「帮我配小红书」 |
| 💼 LinkedIn | Jina Reader读公开页面 | Profile详情、公司页面、职位搜索 | 告诉Agent「帮我配LinkedIn」 |
| 🏢 Boss直聘 | Jina Reader读职位页 | 搜索职位、向HR打招呼 | 告诉Agent「帮我配Boss直聘」 |

### Cookie安全建议

需要Cookie的平台（Twitter、小红书等）建议使用Chrome插件[Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)一键导出。

服务器用户没有浏览器界面，请在自己的电脑上登录对应网站后导出Cookie，再发给Agent配置即可。

**注意：** Cookie只存在你本地，不上传不外传。代码完全开源，随时可审查。

---

## 🚀 快速上手

### 默认安装（全自动）

```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

这个命令会自动：
1. 安装CLI工具 - `pip install`装好`agent-reach`命令行
2. 安装系统依赖 - 自动检测并安装Node.js、gh CLI、mcporter、bird等
3. 配置搜索引擎 - 通过MCP接入Exa（免费，无需API Key）
4. 检测环境 - 判断是本地电脑还是服务器，给出对应的配置建议
5. 注册SKILL.md - 在Agent的skills目录安装使用指南，以后Agent遇到"搜推特"、"看视频"这类需求，会自动知道该调哪个上游工具

### 安全模式

如果担心安全，可以用安全模式——不会自动装系统包，只告诉你需要什么：

```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto --safe
```

它会做什么？（点击展开）
- 安装CLI工具
- 安装系统依赖
- 配置搜索引擎
- 检测环境
- 注册SKILL.md

### 仅预览

```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto --dry-run
```

显示什么会做，不做任何改动。

---

## 🔧 管理命令

### 状态检查

```bash
agent-reach doctor        # channel status overview
agent-reach watch         # quick health + update check
agent-reach check-update  # check for new versions
```

### 配置命令

```bash
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
agent-reach configure proxy http://user:pass@ip:port
agent-reach configure --from-browser chrome    # auto-extract cookies from local browser
```

---

## 🎯 使用上游工具

安装完成后，Agent直接调用上游工具（bird CLI、yt-dlp、mcporter、gh CLI等），不需要经过Agent Reach的包装层。

### Twitter/X (bird CLI)

```bash
# 搜索推文
bird search "query" --json -n 10

# 读单条推文
bird read https://x.com/user/status/123 --json

# 读用户时间线
bird timeline @username --json -n 20
```

### YouTube (yt-dlp)

```bash
# 获取视频metadata
yt-dlp --dump-json "https://www.youtube.com/watch?v=xxx"

# 仅下载字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"
# 然后读取.vtt文件

# 搜索（yt-dlp ytsearch）
yt-dlp --dump-json "ytsearch5:query"
```

### B站 (yt-dlp)

```bash
# 获取视频metadata
yt-dlp --dump-json "https://www.bilibili.com/video/BVxxx"

# 下载字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --convert-subs vtt --skip-download -o "/tmp/%(id)s" "URL"
```

### Reddit (JSON API)

```bash
# 读取subreddit
curl -s "https://www.reddit.com/r/python/hot.json?limit=10" -H "User-Agent: agent-reach/1.0"

# 读取带评论的帖子
curl -s "https://www.reddit.com/r/python/comments/POST_ID.json" -H "User-Agent: agent-reach/1.0"

# 搜索
curl -s "https://www.reddit.com/search.json?q=query&limit=10" -H "User-Agent: agent-reach/1.0"
```

注意：在服务器上，Reddit可能会封锁你的IP。使用代理或者通过Exa搜索。

### 小红书 / XiaoHongShu (mcporter + xiaohongshu-mcp)

```bash
# 搜索笔记
mcporter call 'xiaohongshu.search_feeds(keyword: "query")'

# 读取笔记
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy")'

# 获取评论
mcporter call 'xiaohongshu.get_feed_comments(feed_id: "xxx", xsec_token: "yyy")'

# 发帖
mcporter call 'xiaohongshu.create_image_feed(title: "标题", desc: "内容", image_paths: ["/path/to/img.jpg"])'
```

### GitHub (gh CLI)

```bash
# 搜索仓库
gh search repos "query" --sort stars --limit 10

# 查看仓库
gh repo view owner/repo

# 搜索代码
gh search code "query" --language python

# 列出Issue
gh issue list -R owner/repo --state open

# 查看特定issue/PR
gh issue view 123 -R owner/repo
```

### Web — Any URL (Jina Reader)

```bash
# 读取任意网页为markdown
curl -s "https://r.jina.ai/URL" -H "Accept: text/markdown"

# 搜索网页
curl -s "https://s.jina.ai/query" -H "Accept: text/markdown"
```

### Exa Search (mcporter + exa MCP)

```bash
# Web搜索
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# 代码搜索（GitHub, StackOverflow, docs）
mcporter call 'exa.get_code_context_exa(query: "how to parse JSON in Python", tokensNum: 3000)'

# 公司研究
mcporter call 'exa.company_research_exa(companyName: "OpenAI")'
```

---

## 🏗️ 架构设计

### 脚手架（Scaffolding）理念

Agent Reach是一个脚手架，不是框架。

你给一个新Agent装环境的时候，总要花时间去找工具、装依赖、调配置——Twitter用什么读？Reddit怎么绕封？YouTube字幕怎么提取？每次都要重新踩一遍。

Agent Reach做的事情很简单：帮你把这些选型和配置的活儿做完了。

安装完成后，Agent直接调用上游工具（bird CLI、yt-dlp、mcporter、gh CLI等），不需要经过Agent Reach的包装层。

### 可插拔架构

每个平台背后是一个独立的上游工具。不满意？换掉就行。

```
channels/
├── web.py → Jina Reader ← 可以换成Firecrawl、Crawl4AI……
├── twitter.py → bird ← 可以换成Nitter、官方API……
├── youtube.py → yt-dlp ← 可以换成YouTube API、Whisper……
├── github.py → gh CLI ← 可以换成REST API、PyGithub……
├── bilibili.py → yt-dlp ← 可以换成bilibili-api……
├── reddit.py → JSON API + Exa ← 可以换成PRAW、Pushshift……
├── xiaohongshu.py → mcporter MCP ← 可以换成其他XHS工具……
├── linkedin.py → linkedin-mcp ← 可以换成LinkedIn API……
├── bosszhipin.py → mcp-bosszp ← 可以换成其他招聘工具……
└── rss.py → feedparser ← 可以换成atoma……
```

每个渠道文件只负责检测对应上游工具是否可用（check()方法），给`agent-reach doctor`提供状态信息。实际的读取和搜索由Agent直接调用上游工具完成。

### 当前选型

| 场景 | 选型 | 为什么选它 |
|-----|------|----------|
| 读网页 | [Jina Reader](https://github.com/jina-ai/reader) | 9.8K Star，免费，不需要API Key |
| 读推特 | [bird](https://www.npmjs.com/package/@steipete/bird) | Cookie登录，免费。官方API按量付费（读一条$0.005） |
| 视频字幕+搜索 | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 148K Star，YouTube+B站+1800站通吃 |
| 搜全网 | [Exa](https://exa.ai) via [mcporter](https://github.com/steipete/mcporter) | AI语义搜索，MCP接入免Key |
| GitHub | [gh CLI](https://cli.github.com) | 官方工具，认证后完整API能力 |
| 读RSS | [feedparser](https://github.com/kurtmckee/feedparser) | Python生态标准选择，2.3K Star |
| 小红书 | [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | ⭐9K+，Go语言，Docker一键部署 |
| LinkedIn | [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) | ⭐900+，MCP服务，浏览器自动化 |
| Boss直聘 | [mcp-bosszp](https://github.com/mucsbr/mcp-bosszp) | MCP服务，支持职位搜索和打招呼 |

📌 这些都是「当前选型」。不满意？换掉对应文件就行。这正是脚手架的意义。

---

## 🔒 安全性

### 措施

| 措施 | 说明 |
|-----|------|
| 🔒 数据本地存储 | Cookie、Token只存在你本机`~/.agent-reach/config.yaml`，文件权限600（仅所有者可读写），不上传不外传 |
| 🛡️ 安全模式 | `agent-reach install --safe`不会自动修改系统，只列出需要什么，由你决定装不装 |
| 👀 完全开源 | 代码透明，随时可审查。所有依赖工具也是开源项目 |
| 🔍 Dry Run | `agent-reach install --dry-run`预览所有操作，不做任何改动 |
| 🧩 可插拔架构 | 不信任某个组件？换掉对应的channel文件即可，不影响其他 |

### Cookie安全建议

需要Cookie的平台（Twitter、小红书等）建议使用**专用小号**，不要用主账号。Cookie等同于完整登录权限，用小号可以在凭据泄露时限制影响范围。

---

## 📊 项目统计

- ⭐ Stars: 持续增长中
- 📦 Commits: 持续更新
- 🔄 Releases: 稳定更新
- 🐛 Issues: 快速响应

---

## 🤔 常见问题

### AI Agent怎么搜索Twitter / X？不想付API费用

Agent Reach使用[bird CLI](https://www.npmjs.com/package/@steipete/bird)通过Cookie认证访问Twitter，完全免费。安装Agent Reach后，用Cookie-Editor导出你的Twitter Cookie，运行`agent-reach configure twitter-cookies "your_cookies"`即可。之后Agent就可以用`bird search "关键词" --json`搜索推文了。

### Reddit返回403 / 服务器IP被封锁怎么办？

Reddit封锁数据中心IP。配置一个住宅代理即可解决：`agent-reach configure proxy http://user:pass@ip:port`。推荐Webshare（$1/月）。本地电脑一般不会遇到这个问题。

### 怎么获取YouTube视频转录？

```bash
yt-dlp --dump-json "https://www.youtube.com/watch?v=xxx"  # 提取视频metadata
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"  # 下载字幕
# 然后读取.vtt文件
```

使用yt-dlp，支持多种语言，免费。支持YouTube、B站等1800个网站。

### 怎么让AI Agent读小红书？

小红书需要通过Docker运行一个MCP服务。安装Docker后，运行`agent-reach install`会自动配置。之后Agent就可以用`mcporter call 'xiaohongshu.search_feeds(keyword: "关键词")'`读取笔记或`mcporter call 'xiaohongshu.get_feed_detail(...)'`搜索了。

---

## 💡 为什么值得Star

这个项目我自己每天在用，所以我会一直维护它。

- 有新需求或者大家提了想要的渠道，我会陆续加上
- 每个渠道我会尽量保证能用、好用、免费
- 平台改了反爬或者API变了，我会想办法解决

为Web 4.0基建贡献一份自己的力量。

Star一下，下次需要的时候能找到。⭐

---

## 📞 致谢

- [Jina Reader](https://github.com/jina-ai/reader)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [bird](https://www.npmjs.com/package/@steipete/bird)
- [Exa](https://exa.ai)
- [mcporter](https://github.com/steipete/mcporter)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)
- [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server)
- [mcp-bosszp](https://github.com/mucsbr/mcp-bosszp)

---

## 📄 License

[MIT](LICENSE)
