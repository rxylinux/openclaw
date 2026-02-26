# Agent-Reach 投资研究工具

## 📊 工具概览

**名称：** Agent-Reach（AI Agent互联网能力）
**安装时间：** 2026-02-26
**版本：** v1.1.0
**状态：** 已激活（6/11个渠道，55%）

---

## 🎯 核心价值

### 解决的投资研究痛点

**1. 信息聚合困难**
- ❌ 全网搜索不精准
- ❌ 多个信息源切换麻烦
- ❌ RSS订阅源管理复杂

**Agent Reach解决方案：**
- ✅ 统一的网页读取接口
- ✅ AI语义搜索
- ✅ RSS订阅源自动解析
- ✅ 一站式信息聚合

---

## ✅ 已激活功能

### 1. 🔍 全网搜索（AI语义）
- **搜索代码、文档**：高质量AI搜索结果
- **搜索公司信息**：快速获取公司动态
- **搜索行业新闻**：聚合多源信息
- **支持场景：**
  - 行业研究
  - 公司调研
  - 技术趋势分析
  - 竞品动态追踪

**使用方法：**
```bash
# 使用Exa AI搜索
mcporter call 'exa.web_search_exa(query: "AI芯片行业", numResults: 5)'

# 代码搜索（GitHub、StackOverflow、文档）
mcporter call 'exa.get_code_context_exa(query: "pandas dataframe", tokensNum: 3000)'

# 公司研究
mcporter call 'exa.company_research_exa(companyName: "英伟达")'
```

---

### 2. 🌐 网页读取（Jina Reader）
- **功能：** 读取任意网页，返回Markdown或纯文本
- **优势：**
  - 免费，无需API Key
  - 返回结构化内容
  - 自动提取关键信息
  - 支持多语言

**使用方法：**
```bash
# 读取网页
curl -s "https://r.jina.ai/URL" -H "Accept: text/markdown"

# 搜索网页
curl -s "https://s.jina.ai/query" -H "Accept: text/markdown" -d "关键词"
```

**支持场景：**
- 读取研究报告（券商研报、行业白皮书）
- 总结技术文档（API文档、GitHub README）
- 监控公司官网（产品发布、财报预告）
- 分析行业文章（提取关键数据、趋势）

---

### 3. 📦 GitHub搜索（gh CLI）
- **功能：**
  - 搜索仓库（按关键词、语言、星数）
  - 搜索代码（按关键词、语言）
  - 读取仓库信息
  - 查看Issue、PR
  - Fork仓库

**使用方法：**
```bash
# 搜索仓库
gh search repos "LLM framework" --sort stars --limit 10

# 搜索代码
gh search code "pandas dataframe" --language python

# 查看仓库
gh repo view owner/repo

# 搜索issue
gh search repos "owner/repo" --state open --limit 10
```

**支持场景：**
- 研究开源LLM框架
- 查找量化策略代码
- 分析项目技术栈
- 发现新兴工具和库
- 监控热门项目动态

---

### 4. 📺 YouTube/B站视频提取（yt-dlp）
- **功能：**
  - 提取视频信息（时长、分辨率、播放量）
  - 下载字幕（多语言支持）
  - 搜索视频

**使用方法：**
```bash
# 获取视频信息
yt-dlp --dump-json "URL"

# 下载字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# 搜索视频
yt-dlp --dump-json "ytsearch5:query"
```

**支持场景：**
- 学习技术教程（提取字幕做笔记）
- 观看行业会议演讲（提取关键内容）
- 分析产品演示视频（总结功能亮点）
- 研究技术趋势（搜索相关视频）

---

### 5. 📡 RSS订阅（feedparser）
- **功能：**
  - 读取任意RSS/Atom源
  - 解析订阅内容
  - 提取文章标题、链接、发布时间

**使用方法：**
```python
import feedparser
d = feedparser.parse('https://example.com/feed')
for e in d.entries[:5]:
    print(f'{e.title} — {e.link}')
```

**支持场景：**
- 订阅券商研报
- 关注行业博客RSS
- 监控新闻网站更新
- 跟踪公司公告发布

---

### 6. 💼 Boss直聘职位搜索
- **功能：**
  - 浏览推荐职位
  - 搜索职位（按关键词、城市、薪资）
  - 向HR打招呼

**使用方法：**
```bash
# 浏览推荐职位
mcporter call 'bosszhipin.get_recommend_jobs_tool(page: 1)'

# 搜索职位
mcporter call 'bosszhipin.search_jobs_tool(keyword: "AI工程师", city: "北京", page: 1)'

# 向HR打招呼
mcporter call 'bosszhipin.greet_hr(job_url: "...", message: "...")'
```

**支持场景：**
- 分析AI人才市场
- 了解薪资水平
- 识别热门技能需求
- 监控重点公司招聘动态

---

## 🔍 需要配置的渠道（可选）

### 1. 🐦 Twitter/X搜索（需要Cookie）
**功能：**
- 搜索推文
- 读取单条推文
- 浏览时间线
- 发推

**配置方法：**
```bash
# 配置Cookie
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"

# 搜索推文
bird search "关键词" --json -n 10

# 读取推文
bird read https://x.com/user/status/123 --json
```

**投资研究价值：**
- 搜索行业KOL观点
- 追踪公司高管动态
- 监控市场情绪和话题
- 分析用户反馈和评论

---

### 2. 📖 Reddit搜索（可能需要代理）
**功能：**
- 搜索帖子
- 读取帖子和评论

**配置方法：**
```bash
# 配置代理（服务器需要）
agent-reach configure proxy http://user:pass@ip:port

# 搜索subreddit
curl -s "https://www.reddit.com/r/python/hot.json?limit=10" -H "User-Agent: agent-reach/1.0"
```

**投资研究价值：**
- 了解社区讨论
- 获取真实用户反馈
- 发现问题和痛点
- 分析行业趋势和话题

---

### 3. 📕 小红书笔记（需要Docker）
**功能：**
- 搜索笔记
- 读取笔记详情
- 获取评论
- 发帖、评论、点赞

**配置方法：**
```bash
# 启动Docker服务
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp

# 配置MCP
mcporter config add xiaohongshu http://localhost:18060/mcp

# 搜索笔记
mcporter call 'xiaohongshu.search_feeds(keyword: "关键词")'

# 读取笔记
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy")'
```

**投资研究价值：**
- 研究产品口碑
- 分析C端用户反馈
- 了解市场趋势和偏好
- 发现新品牌和产品

---

### 4. 💼 LinkedIn搜索（需要MCP服务）
**功能：**
- 查看Profile
- 搜索职位
- 查看公司页面

**配置方法：**
```bash
# 安装MCP服务
pip install linkedin-scraper-mcp
mcporter config add linkedin http://localhost:3000/mcp

# 搜索职位
mcporter call 'linkedin.search_people(keyword: "AI工程师", limit: 10)'

# 查看profile
mcporter call 'linkedin.get_person_profile(linkedin_url: "https://linkedin.com/in/username")'
```

**投资研究价值：**
- 分析人才市场
- 了解职业网络
- 识别行业专家和KOL
- 监控重点公司人事动态

---

## 💡 对rxy的投资研究价值

### 1. 信息聚合能力增强
- **全网搜索**：AI语义搜索，快速获取高质量信息
- **网页读取**：一键读取任意网页，自动提取关键信息
- **RSS订阅**：自动跟踪多个信息源
- **GitHub搜索**：快速查找开源项目和代码

### 2. 项目研究能力
- **开源LLM框架研究**：通过GitHub搜索发现新框架
- **量化策略分析**：搜索相关代码，研究策略实现
- **技术栈分析**：通过代码搜索了解项目技术选型
- **竞争分析**：监控热门项目动态

### 3. 内容分析能力
- **YouTube字幕提取**：学习技术教程、行业会议演讲
- **技术文档总结**：快速理解复杂文档
- **行业文章分析**：提取关键数据和趋势

### 4. 市场研究能力
- **Boss直聘搜索**：分析AI人才市场、薪资水平
- **LinkedIn搜索**：了解职业网络、行业专家分布
- **小红书笔记**：研究产品口碑、用户反馈
- **Twitter搜索**：追踪行业KOL观点、公司动态

### 5. 实时追踪能力
- **GitHub监控**：跟踪项目更新、Issue讨论
- **RSS订阅**：自动获取公司公告、研报发布
- **网页读取**：监控公司官网动态

---

## 🎯 推荐使用方式

### 短期（立即可用）
**信息聚合：**
- 全网搜索 + 网页读取 + RSS订阅
- 用于：行业研究、公司调研、技术趋势分析

**项目研究：**
- GitHub搜索 + 代码分析
- 用于：开源LLM框架研究、量化策略分析

**内容学习：**
- YouTube字幕提取
- 用于：学习教程、会议演讲分析

---

### 中期（配置后可用）
**社交媒体分析：**
- Twitter搜索（需要Cookie）
- 小红书笔记（需要Docker）

**职业网络分析：**
- LinkedIn搜索（需要MCP）
- Boss直聘职位搜索

**市场舆情分析：**
- Reddit搜索（可能需要代理）
- Twitter KOL观点追踪

---

## 🚀 下一步

### 推荐配置
1. **Twitter搜索**（低优先级） - 需要Cookie，可以搜索行业KOL观点
2. **小红书笔记**（中优先级） - 需要Docker，可以研究产品口碑
3. **LinkedIn搜索**（中优先级） - 需要MCP，可以分析人才市场

### 推荐测试
1. **全网搜索** - "帮我搜一下最新的AI芯片新闻"
2. **GitHub搜索** - "搜一下LLM框架相关项目"
3. **网页读取** - "帮我看看这个网页写了什么"

---

## 📋 总结

**Agent-Reach核心价值：** 给AI Agent一键装上互联网能力

**对rxy的投资研究价值：**
1. **信息聚合效率提升** - 全网搜索、网页读取、RSS订阅
2. **项目研究能力增强** - GitHub搜索、代码分析、技术栈研究
3. **内容分析能力** - YouTube字幕、技术文档总结
4. **市场研究能力** - Boss直聘、LinkedIn、小红书、Twitter
5. **实时追踪能力** - 项目动态、公司公告、行业新闻

**立即可用（无需配置）：**
- 全网搜索
- 网页读取
- YouTube/B站视频提取
- GitHub搜索
- RSS订阅
- Boss直聘职位搜索

**配置后可用：**
- Twitter搜索
- 小红书笔记
- Reddit搜索
- LinkedIn搜索

**成本：**
- 立即可用功能：完全免费
- 配置后功能：需要Cookie/Docker/MCP（也都是免费的）
- 唯一可选成本：Reddit/B站可能需要住宅代理（$1/月）

---

## 💡 建议的搜索组合

### 行业研究组合
- **全网搜索 + GitHub搜索** - 研究行业技术栈、开源项目
- **全网搜索 + 网页读取** - 获取行业报告、公司动态
- **RSS订阅 + 网页读取** - 自动跟踪多源信息

### 公司调研组合
- **全网搜索 + 网页读取** - 搜索公司新闻、官网信息
- **Boss直聘 + LinkedIn** - 分析公司人才结构、招聘动态
- **GitHub搜索** - 查看公司开源项目

### 产品调研组合
- **全网搜索 + 小红书笔记** - 搜索产品信息、用户反馈
- **网页读取** - 读取产品官网、技术文档
- **YouTube字幕提取** - 研究产品演示视频

---

**rxy的狗腿子**
2026-02-26
