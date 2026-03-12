# ask-search - 零成本多源搜索引擎研究总结

**研究时间：** 2026-03-11  
**项目地址：** https://github.com/ythx-101/ask-search  
**开发者：** ythx-101  
**Stars：** 175 ⭐  
**状态：** 活跃（2天前更新）  
**许可：** MIT

---

## 🎯 核心价值

### 解决的问题

| 方案 | 成本 | 限制 | 隐私 |
|------|------|------|------|
| Brave Search API | $3/1000次查询 | 速率限制 | ❌ 查询上传 |
| Google Custom Search | $5/1000次查询 | 每日配额 | ❌ 查询上传 |
| Bing API | 付费 | 复杂设置 | ❌ 查询上传 |
| 内置搜索 | 免费 | 第三方服务器 | ❌ 查询上传 |
| **ask-search** | **免费** | **无限制** | ✅ **本地隐私** |

### 核心优势

- 零API费用
- 完全隐私保护（本地查询）
- 无速率限制
- 70+搜索源聚合

---

## 🔧 技术架构

```
ask-search
    ↓
SearxNG（元搜索引擎）
    ↓
聚合 70+ 搜索源
- Google
- Bing
- DuckDuckGo
- Brave
- Wikipedia
- YouTube
- Reddit
- ...等
```

### 技术栈

- 后端：Python
- 搜索引擎：SearxNG（Docker部署）
- 协议：HTTP + JSON
- 集成：MCP Server / CLI Skill

---

## 📦 兼容性矩阵

| 环境 | 集成方式 | 状态 |
|------|---------|------|
| OpenClaw | CLI Skill (SKILL.md) | ✅ 完全支持 |
| Claude Code | CLI命令 | ✅ 完全支持 |
| Antigravity | MCP Server | ✅ 完全支持 |
| 任意Shell | ask-search CLI | ✅ 完全支持 |

---

## 🎮 使用示例

```bash
# 基础搜索（返回Top 10结果）
ask-search "Claude Code vs Cursor 2026"

# 限制结果数量
ask-search "React Server Components" --num 5

# 只搜索新闻
ask-search "AI breakthrough" --categories news

# 语言过滤
ask-search "人工智能" --lang zh-CN

# 只返回URL（可pipe到web_fetch）
ask-search "OpenAI最新动态" --urls-only | web_fetch

# 原始JSON输出
ask-search "GPT-5" --json

# 指定搜索引擎
ask-search "机器学习" -e google,brave
```

---

## 🛠️ 快速部署

### 30秒版本（已有SearxNG）

```bash
git clone https://github.com/ythx-101/ask-search
cd ask-search
bash install.sh
ask-search "hello world"
```

### 完整部署（SearxNG + ask-search）

```bash
# 步骤1：部署SearxNG（Docker）
docker run -d --name searxng \
  -p 127.0.0.1:8080:8080 \
  -e SEARXNG_SECRET_KEY=your-secret-key \
  searxng/searxng

# 步骤2：启用JSON输出（编辑settings.yml）
search:
  formats:
    - html
    - json

# 步骤3：安装ask-search
bash install.sh

# 步骤4：使用
ask-search "your query"
```

---

## 🤖 Agent 工作流

```python
# 1. 搜索
ask-search "React Server Components 2026" --num 10

# 2. 发现有价值URL？深度获取
ask-search "query" --urls-only | web_fetch

# 3. 新闻模式
ask-search "GPT-5 release" --categories news --lang en
```

---

## 📋 高级配置

### 环境变量

```bash
export SEARXNG_URL="http://localhost:8080"
```

### MCP集成配置（Claude Code / Antigravity）

```json
{
  "mcpServers": {
    "ask-search": {
      "command": "python3",
      "args": ["/path/to/ask-search/mcp/server.py"],
      "env": {
        "SEARXNG_URL": "http://localhost:8080"
      }
    }
  }
}
```

---

## ⚠️ 深度获取限制与解决方案

### 问题场景

| 站点 | 搜索 | 深度获取 | 原因 |
|------|------|---------|------|
| 大部分站点 | ✅ | ✅ | 无反爬 |
| Reddit | ✅ | ❌ | VPS IP被封锁 |
| 知乎 | ✅ | ❌ | 登录墙+指纹 |
| Medium | ✅ | ⚠️ | 付费墙 |

### 解决方案1：住宅IP的SOCKS代理

```bash
# 在VPS上创建SSH SOCKS隧道
ssh -f -N -D 127.0.0.1:1082 user@your-home-machine

# 通过代理获取
curl -x socks5h://127.0.0.1:1082 "https://reddit.com/r/example/comments/xxx.json"

# Reddit特殊技巧：添加.json获取结构化数据
curl -x socks5h://127.0.0.1:1082 \
  "https://www.reddit.com/r/LocalLLaMA/comments/xxxxx/post_title.json"
```

### 解决方案2：无头浏览器（JS重站点）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        proxy={"server": "socks5://127.0.0.1:1082"}
    )
    page = browser.new_page()
    page.goto("https://example.com/article")
    content = page.inner_text("article")
```

### 解决方案3：利用归档缓存

```bash
# Archive.org（对Reddit效果很好）
curl "https://web.archive.org/web/2026/https://reddit.com/r/example/comments/xxx"

# Google Cache
curl "https://webcache.googleusercontent.com/search?q=cache:example.com/page"
```

### 解决方案4：多节点Agent架构（最稳健）

```
VPS Agent: ask-search "query" → 获取URL + 摘要
           ↓
    Local Agent: web_fetch(url) → 完整内容（住宅IP，无封锁）
           ↓
VPS Agent: 接收完整文本，分析，响应
```

---

## 💡 核心洞察

### 为什么搜索总能工作

- SearxNG查询搜索引擎（Google、Brave等），不直接查询目标站点
- 搜索引擎已经索引了内容

### 深度获取的问题

- 只在Agent尝试获取完整页面时出现
- 反爬措施针对直接访问

### 最佳实践

- ✅ 搜索阶段：VPS（成本低，速度快）
- ✅ 深度获取：本地机器（住宅IP，无封锁）
- ✅ 回环：VPS接收内容，进行分析

---

## 📊 与竞品对比

| 特性 | ask-search | Perplexica | LLocalSearch |
|------|-----------|------------|--------------|
| 搜索源 | 70+ | Google/Bing | 本地索引 |
| 成本 | 免费 | API费用 | 本地计算 |
| 隐私 | ✅ 本地 | ❌ 第三方 | ✅ 本地 |
| 设置难度 | 简单 | 中等 | 复杂 |
| 实时性 | ✅ 实时 | ✅ 实时 | ❌ 静态 |
| Agent兼容 | ✅ MCP/CLI | ❌ 专有 | ✅ Python |

---

## 🚦 部署建议

### 快速测试

```bash
# 使用公共SearxNG实例
export SEARXNG_URL="https://searx.work"
git clone https://github.com/ythx-101/ask-search
cd ask-search
bash install.sh
ask-search "test query"
```

### 生产环境

```bash
# 自托管SearxNG
docker run -d --name searxng \
  -p 127.0.0.1:8080:8080 \
  -e SEARXNG_SECRET_KEY=$(openssl rand -hex 16) \
  searxng/searxng
```

---

## 🎯 对你的价值

### 作为OpenClaw用户

1. **完全免费**
   - 无API费用
   - 无查询限制

2. **隐私保护**
   - 本地查询
   - 不上传到第三方

3. **无缝集成**
   - 直接作为Skill使用
   - 兼容现有工作流

4. **灵活性**
   - 70+搜索源
   - 自定义搜索引擎
   - 新闻/通用/图像分类

### 推荐部署场景

- ✅ VPS运行SearxNG + ask-search（搜索）
- ✅ 本地机器运行web_fetch（深度获取）
- ✅ 回环到VPS进行分析

---

## 🎓 适合场景

✅ **适合：**
- AI Agent的网络搜索需求
- 需要隐私保护的应用
- 高频查询场景（无API限制）
- 多源聚合搜索需求
- 本地部署环境

❌ **不适合：**
- 需要登录的站点（知乎等）
- 复杂的JS重站点（除非用Playwright）
- 对VPS IP极度敏感的站点（Reddit等）

---

## 🎯 实施建议

### 立即可用

```bash
# 使用公共SearxNG实例测试
export SEARXNG_URL="https://searx.work"
ask-search "your query"
```

### 生产部署

```bash
# 1. 部署SearxNG
docker run -d --name searxng \
  -p 127.0.0.1:8080:8080 \
  -e SEARXNG_SECRET_KEY=$(openssl rand -hex 16) \
  searxng/searxng

# 2. 安装ask-search
git clone https://github.com/ythx-101/ask-search
cd ask-search
bash install.sh

# 3. 配置为OpenClaw Skill
cp SKILL.md ~/.openclaw/extensions/skills/ask-search/SKILL.md
```

---

## 📝 总结

**核心优势：**
- 零成本 + 零限制 + 零隐私泄漏
- 70+搜索源聚合
- 完美适配OpenClaw

**关键洞察：**
- 搜索：用SearxNG（VPS，快）
- 深度获取：用本地机器（住宅IP，稳）
- 回环：VPS接收分析

**推荐行动：**
1. 立即测试（公共实例）
2. 生产部署（自托管SearxNG）
3. 集成到OpenClaw工作流

---

**研究完成时间：** 2026-03-11  
**下一步：** 部署测试 + OpenClaw集成
