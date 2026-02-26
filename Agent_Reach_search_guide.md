# Agent Reach 搜索功能说明

## ✅ Agent Reach状态

**已安装：** 7/11个渠道可用（64%）
**状态：** 正常，没有死

---

## 🔍 可用的搜索工具

### 1. GitHub搜索（已激活）✅
**功能：**
- 搜索仓库（按关键词、语言、星数）
- 搜索代码（按关键词、语言）
- 读取仓库信息
- 查看Issue、PR

**使用方法：**
```bash
# 搜索LLM框架相关项目
gh search repos "LLM framework" --limit 10

# 搜索pandas dataframe相关代码
gh search code "pandas dataframe" --language python

# 查看仓库详细信息
gh repo view owner/repo

# 列出仓库的Issue
gh issue list -R owner/repo --state open
```

### 2. 网页读取（已激活）✅
**功能：**
- 读取任意网页（返回Markdown或纯文本）
- 提取网页标题
- 搜索网页内容

**使用方法：**
```bash
# 读取网页（Jina Reader）
curl -s "https://r.jina.ai/https://example.com" -H "Accept: text/markdown"

# 搜索网页
curl -s "https://s.jina.ai/query" -H "Accept: text/markdown"
```

### 3. YouTube/B站搜索（已激活）✅
**功能：**
- 搜索视频
- 提取视频信息
- 下载字幕

**使用方法：**
```bash
# 搜索YouTube视频
yt-dlp --dump-json "ytsearch5:query"

# 搜索B站视频
yt-dlp --dump-json "ytsearch5:查询"

# 获取视频信息
yt-dlp --dump-json "URL"
```

---

## ⚠️ 需要配置的搜索工具

### Twitter搜索
**需要：** Cookie
**配置方法：**
```bash
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
```

### Reddit搜索
**需要：** 代理（服务器IP可能被封）
**配置方法：**
```bash
agent-reach configure proxy http://user:pass@ip:port
```

### 小红书搜索
**需要：** Docker + MCP服务
**配置方法：**
```bash
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp
mcporter config add xiaohongshu http://localhost:18060/mcp
```

---

## 💡 对投资研究的价值

### GitHub搜索
- 研究开源LLM框架
- 查看量化策略代码
- 发现新兴技术栈
- 监控项目动态

### 网页读取
- 读取研究报告
- 总结技术文档
- 监控公司官网
- 分析行业文章

### 视频搜索
- 学习技术教程
- 观看行业会议演讲
- 了解产品演示
- 研究技术趋势

---

## 🎯 立即可用的搜索示例

**GitHub搜索示例：**
- "帮我搜一下LLM框架相关项目"
- "看看这个仓库的Issue"
- "搜索pandas dataframe相关代码"

**网页读取示例：**
- "帮我看看这个网页写了什么"
- "总结一下这篇技术文章"
- "读取这个研究报告"

**视频搜索示例：**
- "YouTube上搜一下AI芯片相关视频"
- "B站上搜一下半导体相关视频"

---

## 📊 当前状态总结

### ✅ 已激活（立即可用）
- GitHub搜索
- 网页读取（Jina Reader）
- YouTube/B站视频提取
- RSS订阅
- 全网语义搜索（mcporter）
- Boss直聘职位搜索

### ⚠️ 需要配置（立即可用，但需要Cookie/Docker）
- Twitter（需要Cookie）
- Reddit（可能需要代理）
- 小红书（需要Docker）
- LinkedIn（需要MCP服务）

---

**rxy的狗腿子**
2026-02-26
