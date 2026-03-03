# Apify + Claude Code 实时网页数据抓取

**研究日期**: 2026-03-02
**文章来源**: 恶人笔记（微信公众号）
**原文链接**: https://mp.weixin.qq.com/s/lopU0A1nVdlpECU_t9iuTQ
**视频来源**: @svpino (X/Twitter) - 7分13秒实战演示

---

## 核心理念：职责分离

### 传统 AI 网页能力的问题

当让 Claude/GPT "帮我查查XX网站最新数据"时，通常遇到：

1. **靠搜索引擎拼概率**
   - 结果不全
   - 数据过时
   - 无法验证准确性

2. **硬啃原始 HTML**
   - 规模一大就幻觉连篇
   - 根本无法校验
   - 数据错误无法察觉

> **svpino 原话**：
>
> "At 10 pages, you won't notice. At 100 pages, your agent will start making decisions based on data that's wrong in ways you can't even detect."
>
> 10页的时候，你不会注意到。到了100页，你的Agent就会开始根据那些你甚至都无法察觉其错误之处的数据来做决定。

### 根本原因

使用架构错了：把"确定性抓取"和"智能分析"全扔给 LLM。

### 正确做法：职责彻底分离

| 职责 | 工具 | 优势 |
|------|------|------|
| 确定性抓取 | Apify | 20年经验，海量稳定 Actor |
| 智能分析 | LLM | 理解、决策、输出洞见 |

两者通过 **Apify Agent Skills** 无缝集成到 Claude Code（或 Cursor）里，一行自然语言指令就能跑通全流程。

---

## 技术方案

### 工具组合

1. **Apify**
   - 20年网页抓取经验
   - 积累海量 Actor（Serverless 云程序）
   - 只负责一件事：用确定性工具读取网页、结构化提取数据

2. **Apify Agent Skills**
   - 12个预构建技能包
   - 开箱即用，零配置

3. **Claude Code/Cursor**
   - 通过自然语言调用 Apify 技能
   - AI 自动编排工作流
   - 无需手动写爬虫代码

---

## 安装步骤

### 1. 安装 Agent Skills

```bash
npm install -g apify-agent-skills
```

安装时全选12个技能：
- ✅ lead generation（潜客获取）
- ✅ competitor analysis（竞品分析）
- ✅ ecommerce（电商）
- ✅ ultimate scraper（终极爬虫）
- ✅ actor development（Actor 开发）
- ✅ 等12个技能

### 2. 获取 Apify API Token

- 访问: https://console.apify.com/account/integrations
- 创建免费账号
- 复制 API Token

### 3. 配置项目

在项目目录创建 `.env` 文件：

```bash
APIFY_TOKEN=你的token
```

### 4. 在 Claude Code 中使用

**列出所有技能**：
```
list all the agent skills you have access to
```

**执行抓取**：
```
run lead generation skill for AI startups in San Francisco
```

**链式提取**：
```
extract emails from the previous results
```

---

## 实战演示

svpio 的真实演示超级直观：

### 步骤 1: 自然语言指令

在 Claude Code/Cursor 中说：

> "帮我抓取旧金山AI初创公司的Google Maps数据"

### 步骤 2: AI 自动调用

- AI 自动调用 Apify 的 Google Places Actor
- 输出结构化 CSV
- 包含：公司名、网站、地址、评分等

### 步骤 3: 链式提取

> "从这些网站里提取邮箱地址"

### 步骤 4: 继续自动处理

- AI 继续调用 Contact Info Scraper
- 遍历所有网站
- 自动抓取 email
- 追加到 CSV

### 结果

**整个过程在 IDE 中完成**：
- ✅ 不用切到 Apify 控制台
- ✅ 不用手动写爬虫
- ✅ 数据真实、可验证
- ✅ 自动保存为 CSV/JSON
- ✅ Apify 控制台实时监控消耗

---

## 为什么实用性提升10倍？

### 1. 零幻觉 ✅

- 数据来自 Apify 真实 HTTP 请求
- 20年积累的解析规则
- **不是 LLM "编"的**

### 2. 无限边界 ✅

支持上千平台：
- Google Maps
- YouTube
- Instagram
- TikTok
- Amazon
- Booking
- 任意网站都能自定义 Actor

### 3. 链式自动化 ✅

```
抓取 → 清洗 → 分析 → 生成报告
```
全程 AI 自主完成，无需人工干预。

### 4. 低门槛 ✅

- 一行命令集成
- 免费额度上手
- 适合个人/小团队

### 5. 可扩展 ✅

- 不仅抓数据
- 还能开发自己的 Actor（视频里提到 actor-development skill）
- 把任意工具包装成 AI 可调用技能

---

## 实战使用场景

### 场景 1: 市场研究/竞品分析

**指令示例**：
```
用lead generation skill抓取'AI Agent工具'赛道最近30天融资的初创公司，
再提取创始人LinkedIn和邮箱，生成竞品矩阵
```

**效果**：半小时出完整报告，比手动 Google 快10倍。

### 场景 2: 内容创作/趋势追踪

**指令示例**：
```
用ultimate scraper抓取过去7天TikTok上#AIAgent话题的Top10视频，
转录文本，做情绪分析和热点总结
```

**效果**：直接喂给 Claude 生成爆款短视频脚本。

### 场景 3: 个人/商业情报引擎

**指令示例**：
```
监控我关注的10个竞品官网价格变动 + 新闻
```

**效果**：变成你的专属商业哨兵。

### 场景 4: 电商研究

**指令示例**：
```
抓取Amazon上"AI工具"相关的Top100产品，
分析价格分布、评分趋势、评论关键词
```

**效果**：快速完成电商竞品分析。

---

## 进阶 Tips

### 1. 先玩熟免费额度

**推荐优先体验**：
- Google Maps - 本地商家数据
- Ultimate Scraper - 通用网页爬虫

**免费额度**：
- 足够玩很久
- 付费也超便宜（按结果计费）

### 2. 开发自定义 Actor

使用 `apify-actor-development` skill：
```
用actor development skill帮我写一个爬虫，抓取XX网站的数据
```

让 Claude 帮你写代码，把任意工具包装成 AI 可调用技能。

### 3. 注意合规 ⚠️

- ✅ 只抓公开数据
- ✅ 商业用途注意平台条款
- ✅ 遵守 robots.txt
- ❌ 不要抓取私有数据
- ❌ 不要绕过反爬虫限制

### 4. 搭配工具

- **Claude Projects** - 更好的上下文管理
- **Cursor Rules** - 技能调用更稳定
- **Apify Dashboard** - 实时监控消耗和日志

---

## 核心洞察

### 本质变化

- **从**："概率搜索时代"
- **到**："结构化知识管道时代"

### 信息形态转变

- **以前**：碎片化的网页
- **现在**：你私人情报引擎的结构化输入

### AI Agent 进化

| 维度 | 以前 | 现在 |
|------|------|------|
| 能力 | 会聊天 | 会干活 |
| 定位 | 玩具 | 武器 |
| 数据 | 概率性猜测 | 确定性抓取 |
| 可靠性 | 有幻觉 | 零幻觉 |

### 以前 vs 现在

**以前**：
- 知道的很多但干不了实事
- 靠搜索引擎拼概率
- 大规模数据时会幻觉

**现在**：
- 有了确定性数据管道
- 实事真能干
- 而且干得又快又准

---

## 技术细节

### Apify Agent Skills 包含的12个技能

1. **Lead Generation** - 潜客获取（Google Maps、LinkedIn）
2. **Competitor Analysis** - 竞品分析（价格、评论、关键词）
3. **Ecommerce Scraper** - 电商数据（Amazon、eBay、Shopify）
4. **Ultimate Scraper** - 通用网页爬虫（任意网站）
5. **Instagram Scraper** - Instagram 数据（帖子、评论、用户信息）
6. **YouTube Scraper** - YouTube 数据（视频、评论、元数据）
7. **TikTok Scraper** - TikTok 数据（视频、标签、用户信息）
8. **Google Search Scraper** - Google 搜索结果（SERP）
9. **Contact Info Scraper** - 联系信息提取（邮箱、电话、社交账号）
10. **Actor Development** - Actor 开发（自定义爬虫）
11. **Data Cleaning** - 数据清洗（去重、格式化、验证）
12. **Report Generation** - 报告生成（PDF、Excel、图表）

### 输出格式

支持多种格式：
- CSV（结构化数据）
- JSON（程序化处理）
- Excel（表格分析）
- PDF（报告生成）

### 成本估算

**免费额度**：
- 每月一定量的免费执行
- 足够个人使用和测试

**付费**：
- 按结果计费
- 通常非常便宜（每次抓取几美分）
- 大批量还有折扣

---

## 个人评价

### 优势 ✅

1. **确定性数据**
   - 真实HTTP请求
   - 20年积累的解析规则
   - 零幻觉

2. **覆盖广**
   - 支持上千平台
   - 自定义Actor扩展性极强

3. **零门槛**
   - 自然语言调用
   - 无需编程
   - 安装即可用

4. **低成本**
   - 免费额度充足
   - 按结果付费
   - 性价比高

5. **可扩展**
   - 开发自定义Actor
   - 集成任意工具
   - 打造专属情报引擎

### 限制 ⚠️

1. **依赖外部服务**
   - 需要注册 Apify 账号
   - 依赖 Apify API 可用性
   - 网络连接必需

2. **合规性**
   - 必须遵守各平台条款
   - 不能抓取私有数据
   - 注意反爬虫限制

3. **学习曲线**
   - 需要了解12个技能的用法
   - 复杂任务需要多次迭代
   - 最佳实践需要摸索

### 适用人群

**强烈推荐**：
- ✅ 市场研究员
- ✅ 竞品分析师
- ✅ 内容创作者
- ✅ 商业情报工作者
- ✅ 电商运营
- ✅ 投资分析师
- ✅ 任何需要大规模获取公开数据的人

**不太适合**：
- ❌ 只需要偶尔查一两篇文章的人
- ❌ 不懂技术、不愿意学习的用户
- ❌ 需要爬取私有数据的场景

---

## 总结

### 关键要点

1. **职责分离是关键**
   - Apify 负责确定性抓取
   - LLM 负责智能分析
   - 两者结合，威力无穷

2. **零幻觉是核心价值**
   - 数据来自真实HTTP请求
   - 不是LLM编造的
   - 可验证、可追溯

3. **自然语言调用降低门槛**
   - 不用写爬虫代码
   - 不用学 Apify API
   - 一行指令搞定

4. **从玩具到武器的进化**
   - AI 不再只会聊天
   - 真正能干活、能创造价值
   - 实用性提升10倍

### 与其他工具对比

| 工具 | 幻觉率 | 覆盖平台 | 易用性 | 成本 |
|------|--------|---------|--------|------|
| Claude/GPT 直接抓取 | 高 | 广 | 高 | 低 |
| 手动爬虫 | 低 | 低 | 低 | 高（时间） |
| Apify + Claude | **零** | **极广** | **高** | **低** |

### 最终评价

**svpio 这套方案，真正把 AI Agent 从玩具变成了武器。**

以前我们抱怨 AI "知道的很多但干不了实事"，现在有了确定性数据管道，实事它真能干，而且干得又快又准。

如果你正在卷 AI Agent，强烈建议试试这套方案。

---

## 快速开始

**1. 注册 Apify**
https://console.apify.com/account/integrations

**2. 安装 Agent Skills**
```bash
npm install -g apify-agent-skills
```

**3. 配置 Token**
在项目目录创建 `.env` 文件：
```bash
APIFY_TOKEN=你的token
```

**4. 开始使用**
打开 Claude Code/Cursor，输入：
```
list all the agent skills you have access to
```

就这么简单！🚀

---

*研究完成时间: 2026-03-02*
*研究状态: ✅ 完成*
