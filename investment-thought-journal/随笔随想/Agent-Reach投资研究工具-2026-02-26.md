# 随笔：Agent-Reach投资研究工具

## 📊 工具概况

**安装时间：** 2026-02-26
**项目名称：** Agent-Reach
**项目地址：** https://github.com/Panniantong/Agent-Reach
**版本：** v1.1.0

---

## 🎯 核心价值

### 给AI Agent装上互联网能力

**解决的投资研究痛点：**
1. **信息聚合困难** - 搜不了全网新闻、读不了网页、订阅不了RSS
2. **内容分析限制** - 提取不了YouTube字幕、B站视频总结困难
3. **实时追踪缺失** - 监控不了GitHub项目动态、行业KOL观点
4. **社交媒体访问受限** - 搜不了推特、读不了小红书口碑

**Agent Reach的解决方案：**
- ✅ 一句话安装，几分钟搞定
- ✅ 完全免费，所有API零成本
- ✅ 隐私安全，Cookie只存本地
- ✅ 持续更新，平台封了作者修
- ✅ 兼容所有Agent，OpenClaw、Claude Code、Cursor、Windsurf都可用

---

## ✅ 已激活功能（6/11个渠道）

### 1. GitHub搜索 🔍
**功能：**
- 搜索仓库（按关键词、语言、星数）
- 搜索代码（按关键词、语言）
- 读取仓库信息
- 查看Issue、PR
- Fork仓库

**投资研究价值：**
- 研究开源LLM框架
- 查看量化策略代码
- 发现新兴技术栈
- 监控项目动态（Issue讨论、PR更新）
- 分析竞争对手技术选型

**使用方法：**
```bash
gh search repos "LLM framework" --limit 10
gh search code "pandas dataframe" --language python
gh repo view owner/repo
gh issue list -R owner/repo --state open
```

---

### 2. 网页读取 🌐
**功能：**
- 读取任意网页（返回Markdown或纯文本）
- 提取网页标题
- 搜索网页内容

**投资研究价值：**
- 读取研究报告、技术文档
- 总结文章要点、提取关键数据
- 监控公司官网动态、研报发布
- 分析行业新闻、政策文件

**使用方法：**
```bash
curl -s "https://r.jina.ai/https://example.com" -H "Accept: text/markdown"
curl -s "https://s.jina.ai/query" -H "Accept: text/markdown"
```

---

### 3. YouTube/B站视频提取 📺
**功能：**
- 提取视频信息（时长、分辨率、播放量）
- 下载字幕（多语言支持）
- 搜索视频

**投资研究价值：**
- 学习技术教程、行业会议演讲
- 观看产品演示、功能介绍
- 提取字幕进行深度内容分析
- 搜索行业相关视频进行技术趋势分析

**使用方法：**
```bash
# 获取视频信息
yt-dlp --dump-json "URL"

# 下载字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# 搜索视频
yt-dlp --dump-json "ytsearch5:query"
```

---

### 4. RSS订阅 📡
**功能：**
- 读取任意RSS/Atom源
- 解析订阅内容

**投资研究价值：**
- 订阅新闻网站、行业博客
- 监控研报发布
- 获取公司公告、财报预告
- 追踪行业动态

**使用方法：**
```python
import feedparser
d = feedparser.parse('https://example.com/feed')
for e in d.entries[:5]:
    print(f'{e.title} — {e.link}')
```

---

### 5. 全网搜索（AI语义）🔍
**功能：**
- AI语义搜索
- 代码搜索（GitHub、StackOverflow、docs）
- 公司研究
- 高质量、相关性强的结果

**投资研究价值：**
- 搜索行业新闻、技术趋势
- 查找竞争对手动态
- 研究市场舆情、用户反馈
- 搜寻产业链相关信息

**使用方法：**
```bash
mcporter call 'exa.web_search_exa(query: "AI芯片行业", numResults: 5)'
mcporter call 'exa.get_code_context_exa(query: "pandas dataframe", tokensNum: 3000)'
mcporter call 'exa.company_research_exa(companyName: "OpenAI")'
```

---

### 6. Boss直聘职位搜索 💼
**功能：**
- 浏览推荐职位
- 搜索职位
- 向HR打招呼

**投资研究价值：**
- 分析人才市场趋势
- 了解薪资水平、技能需求
- 识别行业热招岗位
- 监控重点公司招聘动态

**使用方法：**
```bash
mcporter call 'bosszhipin.get_recommend_jobs_tool(page: 1)'
mcporter call 'bosszhipin.search_jobs_tool(keyword: "AI工程师", city: "北京", page: 1)'
mcporter call 'bosszhipin.get_job_detail_tool(job_url: "https://www.zhipin.com/job_detail/xxx")'
```

---

## 🎯 对rxy的投资策略支持

### 信息聚合能力增强
**全网搜索 + 网页读取 + RSS订阅**
- 自动收集行业新闻、技术趋势
- 监控公司动态、研报发布
- 分析市场情绪、行业观点

### 项目研究能力
**GitHub搜索 + 代码分析**
- 研究开源LLM框架、量化策略
- 查看技术栈、依赖关系
- 分析项目活跃度、社区讨论

### 内容分析能力
**YouTube字幕提取 + 网页读取**
- 学习技术教程、行业会议演讲
- 总结研究报告、技术文档要点
- 提取关键数据、趋势信息

### 人才市场分析
**Boss直聘职位搜索**
- 了解AI工程师市场供需
- 分析薪资水平、技能需求
- 识别行业招聘热点

---

## 🚀 配置后可解锁更多功能

### Twitter/X搜索 🐦
**需要：** Cookie登录
**功能：**
- 搜索推文
- 读取单条推文
- 浏览时间线
- 发推（如果需要）

**投资研究价值：**
- 搜索行业KOL观点
- 追踪公司动态、产品反馈
- 监控市场舆情、用户讨论
- 分析热门话题、趋势判断

---

### 小红书笔记 📕
**需要：** Docker + MCP服务
**功能：**
- 搜索笔记
- 读取笔记详情
- 获取评论
- 发帖、评论、点赞

**投资研究价值：**
- 研究产品口碑、用户反馈
- 分析市场趋势、消费偏好
- 监控竞品动态、用户讨论
- 了解C端用户真实使用场景

---

### LinkedIn职业社交 💼
**需要：** MCP服务
**功能：**
- Profile详情
- 公司页面
- 职位搜索

**投资研究价值：**
- 分析人才市场
- 了解行业人脉分布
- 监控重点公司人事动态
- 识别高管变动、组织架构

---

## 💡 使用建议

### 立即可用（无需配置）
1. **GitHub搜索** - 研究开源项目、量化策略
2. **网页读取** - 读取研究报告、技术文档
3. **视频提取** - 学习教程、行业会议演讲
4. **全网搜索** - 搜索行业新闻、技术趋势
5. **RSS订阅** - 监控研报发布、公司动态
6. **Boss直聘** - 分析人才市场

### 配置后可用（可选）
1. **Twitter搜索** - 行业KOL观点、市场舆情
2. **小红书笔记** - 产品口碑、用户反馈
3. **LinkedIn搜索** - 人才市场、高管动态

---

## 📋 常见使用场景

### 投资调研
- "帮我搜一下LLM框架相关项目"
- "GitHub上有什么AI工具？"
- "搜一下最新的AI芯片新闻"
- "看看这个仓库的Issue"

### 价值投资
- "帮我搜一下英伟达的最新动态"
- "全网搜索英伟达供应链情况"
- "Boss直聘搜一下AI工程师薪资"

### 技术学习
- "YouTube上搜一下AI芯片相关视频"
- "这个视频讲了什么？"
- "B站上搜一下半导体相关视频"

### 市场分析
- "全网搜索行业KOL对英伟达的评价"
- "小红书搜一下英伟达产品的用户反馈"

---

## 🔒 安全性

### 数据安全
- **本地存储：** 所有Cookie、Token只存在`~/.agent-reach/config.yaml`
- **文件权限：** 600（仅所有者可读写）
- **不上传不外传：** 完全本地化，不上云、不外传

### 代码透明
- **完全开源：** 代码透明，随时可审查
- **可插拔架构：** 不满意某个组件？换掉对应channel文件即可
- **依赖开源：** 所有上游工具都是开源项目

---

## 📊 总结

**核心价值：** 给AI Agent一键装上互联网能力

**投资研究价值：**
1. ✅ 信息聚合（全网搜索、网页读取、RSS订阅）
2. ✅ 内容分析（视频字幕提取、网页解析）
3. ✅ 项目研究（GitHub搜索、代码分析、Issue追踪）
4. ✅ 市场分析（Boss直聘职位搜索、人才市场）
5. ✅ 社交媒体舆情（配置后：Twitter、小红书、LinkedIn）

**立即可用：** 6个渠道（无需任何配置）

**成本：** 完全免费，零API成本

**稳定性：** 持续更新，作者自己维护

---

**rxy的狗腿子**
2026-02-26
