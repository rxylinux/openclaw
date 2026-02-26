# Agent-Reach 项目总结

## 📊 项目信息

**项目名称：** Agent-Reach
**GitHub地址：** https://github.com/Panniantong/Agent-Reach
**定位：** 给AI Agent一键装上互联网能力

---

## 🎯 核心价值

### 解决的问题

AI Agent已经能帮你写代码、改文档、管项目——但你让它去网上找点东西，它就抓瞎了：

1. **YouTube字幕提取** → 看不了，拿不到字幕
2. **Twitter/X搜索** → 搜不了，Twitter API要付费
3. **Reddit访问** → 403被封，服务器IP被拒
4. **小红书访问** → 打不开，必须登录才能看
5. **B站视频** → 连不上，海外/服务器IP被屏蔽
6. **全网搜索** → 没有好用的搜索，要么付费要么质量差
7. **网页读取** → 抓回来一堆HTML标签，根本没法读
8. **GitHub访问** → 能用，但认证配置很麻烦

### Agent Reach的方案

**一句话安装：**
```
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md
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
- ……任何能跑命令行的Agent都能用

### 5. 自带诊断
- `agent-reach doctor` 一条命令告诉你哪个通、哪个不通、怎么修

---

## 🌐 支持的平台

| 平台 | 装好即用 | 配置后解锁 | 怎么配 |
|-----|---------|-----------|-------|
| 🌐 网页 | 阅读任意网页 | — | 无需配置 |
| 📺 YouTube | 字幕提取+视频搜索 | — | 无需配置 |
| 📡 RSS | 阅读任意RSS/Atom源 | — | 无需配置 |
| 🔍 全网搜索 | — | 全网语义搜索 | 自动配置（MCP接入，免费无需Key） |
| 📦 GitHub | 读公开仓库+搜索 | 私有仓库、提Issue/PR、Fork | 告诉Agent「帮我登录GitHub」 |
| 🐦 Twitter/X | 读单条推文 | 搜索推文、浏览时间线、发推 | 告诉Agent「帮我配Twitter」 |
| 📺 B站 | 本地：字幕提取+搜索 | 服务器也能用 | 告诉Agent「帮我配代理」 |
| 📖 Reddit | 搜索（通过Exa免费） | 读帖子和评论 | 告诉Agent「帮我配代理」 |
| 📕 小红书 | — | 阅读、搜索、发帖、评论、点赞 | 告诉Agent「帮我配小红书」 |
| 💼 LinkedIn | Jina Reader读公开页面 | Profile详情、公司页面、职位搜索 | 告诉Agent「帮我配LinkedIn」 |
| 🏢 Boss直聘 | Jina Reader读职位页 | 搜索职位、向HR打招呼 | 告诉Agent「帮我配Boss直聘」 |

---

## 🚀 快速上手

### 一键全自动（推荐）

```bash
pip install https://github.com/Panniantong/Agent-Reach/archive/main.zip
agent-reach install --env=auto
```

这个命令会自动：
- 安装CLI工具 — `pip install` 装好`agent-reach`命令行
- 安装系统依赖 — 自动检测并安装Node.js、gh CLI、mcporter、bird等
- 配置搜索引擎 — 通过MCP接入Exa（免费，无需API Key）
- 检测环境 — 判断是本地电脑还是服务器，给出对应的配置建议
- 注册SKILL.md — 在Agent的skills目录安装使用指南，以后Agent遇到"搜推特"、"看视频"这类需求，会自动知道该调哪个上游工具

安装完之后，`agent-reach doctor` 一条命令告诉你每个渠道的状态。

### 安全模式

如果担心安全，可以使用安全模式——不会自动装系统包，只告诉你需要什么：

```bash
pip install https://github.com/Panniantong/Agent-Reach/archive/main.zip
agent-reach install --env=auto --safe
```

它会做什么？（点击展开）
- 安装CLI工具 — `pip install` 装好`agent-reach`命令行
- 安装系统依赖 — 自动检测并安装Node.js、gh CLI、mcporter、bird等
- 配置搜索引擎 — 通过MCP接入Exa（免费，无需API Key）
- 检测环境 — 判断是本地电脑还是服务器，给出对应的配置建议
- 注册SKILL.md — 在Agent的skills目录安装使用指南，以后Agent遇到"搜推特"、"看视频"这类需求，会自动知道该调哪个上游工具

### 仅预览

```bash
pip install https://github.com/Panniantong/Agent-Reach/archive/main.zip
agent-reach install --env=auto --dry-run
```

显示什么会做，不做任何改动。

---

## 💡 使用示例

### 网页读取

```bash
# 读取任意网页（Jina Reader）
curl -s "https://r.jina.ai/URL" -H "Accept: text/markdown"

# 搜索网页
curl -s "https://s.jina.ai/query" -H "Accept: text/markdown"
```

### YouTube

```bash
# 获取视频metadata
yt-dlp --dump-json "https://www.youtube.com/watch?v=xxx"

# 下载字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"
# 然后读取.vtt文件
```

### Twitter/X (bird CLI)

```bash
# 搜索tweets
bird search "query" --json -n 10

# 读单条tweet
bird read https://x.com/user/status/123 --json

# 读用户timeline
bird timeline @username --json -n 20
```

### GitHub (gh CLI)

```bash
# 搜索repos
gh search repos "query" --sort stars --limit 10

# 查看repo
gh repo view owner/repo

# 搜索代码
gh search code "query" --language python

# 列出issues
gh issue list -R owner/repo --state open

# 查看特定issue/PR
gh issue view 123 -R owner/repo
```

---

## 🔧 管理命令

```bash
agent-reach doctor        # channel status overview
agent-reach watch         # quick health + update check
agent-reach check-update  # check for new versions
agent-reach configure twitter-cookies "..."  # unlock Twitter search + posting
agent-reach configure proxy URL  # unlock Reddit + Bilibili on servers
```

---

## 📋 检查状态

运行`agent-reach doctor`查看每个渠道的状态：

```
✅ 装好即用：
  ⚠️ GitHub 仓库和代码 — gh CLI 未安装。安装：https://cli.github.com
  ✅ YouTube 视频和字幕 — 可提取视频信息和字幕
  ✅ RSS/Atom 订阅源 — 可读取 RSS/Atom 源
  ✅ 全网语义搜索 — 全网语义搜索可用（免费，无需 API Key）
  ✅ 任意网页 — 通过 Jina Reader 读取任意网页（curl https://r.jina.ai/URL）

🔍 搜索（mcporter 即可解锁）：
  ⬜ Twitter/X 推文 — bird CLI 已安装但未配置 Cookie。运行：
  agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
  ⬜ Reddit 帖子和评论 — 无代理。服务器 IP 可能被 Reddit 封锁。配置代理：
  agent-reach configure proxy http://user:pass@ip:port
  ✅ B站视频和字幕 — 可提取视频信息和字幕（本地环境）。服务器可能需要代理

🔧 配置后可用：
  ⬜ 小红书笔记 — mcporter 已装但小红书 MCP 未配置。运行：
  docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp
  mcporter config add xiaohongshu http://localhost:18060/mcp
  ⬜ LinkedIn 职业社交 — mcporter 已装但 LinkedIn MCP 未配置。运行：
  pip install linkedin-scraper-mcp
  mcporter config add linkedin http://localhost:3000/mcp
  ✅ Boss直聘职位搜索 — 可搜索职位、向 HR 打招呼
```

---

## 🎯 对rxy的投资研究价值

### 1. 信息聚合
- **全网搜索**：行业新闻、技术趋势
- **网页读取**：研究报告、技术文档
- **RSS订阅**：新闻网站、行业博客

### 2. 内容分析
- **YouTube字幕提取**：学习教程、行业会议演讲
- **B站视频总结**：技术解读、行业观点分析
- **Twitter搜索**：行业KOL观点、公司动态追踪

### 3. 实时追踪
- **RSS订阅源**：新闻网站、行业博客
- **GitHub监控**：开源项目动态、Issue讨论、PR更新

---

## 💡 对rxy的投资建议

### 短期方案（立即可用）

**组合：网页读取 + 全网搜索 + RSS订阅**
- 成本：0
- 数据延迟：实时/低延迟
- 稳定性：高

### 长期方案（推荐）

**组合：Twitter搜索 + GitHub监控 + 小红书笔记**
- 成本：0（Twitter用Cookie，其他都免费）
- 数据延迟：实时
- 稳定性：高

---

## 📊 当前状态总结

**已激活（立即可用）：**
1. 🌐 网页读取 - Jina Reader
2. 📺 YouTube - yt-dlp
3. 📡 RSS订阅 - feedparser
4. 🔍 全网搜索 - Exa (MCP)
5. 📦 GitHub - gh CLI

**需配置（可选）：**
1. 🐦 Twitter - 需要Cookie
2. 📖 Reddit - 需要代理（服务器）
3. 📕 小红书 - 需要Docker
4. 💼 LinkedIn - 需要MCP服务

---

## 🔒 安全性

### 安全措施

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

## 💡 总结

**推荐理由：**

1. **极简安装**：一句话搞定
2. **完全免费**：零API成本
3. **隐私安全**：Cookie本地存储
4. **持续更新**：作者自己维护
5. **兼容所有Agent**：任何能跑命令行的都能用

**适用场景：**
- 投资研究（信息聚合、内容分析）
- 市场调研（全网搜索、网页读取）
- 技术学习（YouTube字幕、B站视频）
- 项目监控（GitHub动态、Issue追踪）

---

## 📁 详细文档

**项目主页：** https://github.com/Panniantong/Agent-Reach
**安装指南：** https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md
**英文文档：** https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md

---

**需要我帮你安装这个项目吗？**

或者先看看立即可用的功能（网页读取、YouTube字幕、RSS订阅、全网搜索、GitHub搜索）？

---

rxy的狗腿子
2026-02-26
