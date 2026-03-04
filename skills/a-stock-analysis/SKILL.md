---
name: a-stock-analysis
description: A股股票分析技能。使用博查API和秘塔搜索获取股票信息、财务数据、最新新闻，进行基本面分析和技术分析。支持个股查询、行业分析、财务指标解读。当用户询问A股股票、上市公司分析、投资研究时使用此技能。
---

# A股股票分析

## 概述

本技能提供A股上市公司**14维度综合分析**能力：
- **基础数据**（维度1-4）：股票信息查询、财务数据分析、新闻追踪、行业对比
- **商业理解**（维度5-6）：商业理解、收入分解
- **行业与竞争**（维度7-8）：行业背景、竞争格局
- **财务与风险**（维度9-10）：财务质量、风险与下行提示
- **管理层与情景**（维度11-12）：管理层与执行、牛熊情景
- **估值与论点**（维度13-14）：估值思考、长期论点

**数据源**：博查AI开放平台 + 秘塔AI搜索

**核心特色**：
- 严格遵循reference文档标准（每个维度都有详细的分析框架、评分标准、输出模板）
- 大白话风格（避免金融术语，让小学生都能听懂）
- 综合评分体系（收入结构0-50分、财务质量0-100分、风险0-100分、管理层0-100分、竞争力0-50分）

## 快速开始

### 单股分析
当用户询问"帮我看下拓普集团"时：
1. **获取基本信息**：优先使用博查API，失败时使用秘塔搜索
2. **财务数据**：优先使用博查API，失败时使用秘塔搜索
3. **最新新闻**：优先使用博查API，失败时使用秘塔搜索
4. **综合分析**：整合多个来源的数据生成分析报告

### 行业分析
当用户询问"半导体行业如何"时：
1. 优先使用博查API搜索行业关键词
2. 如果博查API返回空数据或失败，使用秘塔搜索
3. 汇总多家公司信息
4. 生成行业对比分析

## 数据搜索策略

**规则：博查API优先，秘塔搜索备选。博查API返回空数据或报错时，自动使用秘塔搜索。**

| 搜索类型 | 博查API命令 | 秘塔搜索关键词 |
|---------|------------|--------------|
| 基本信息 | `python3 scripts/bocha_search.py <代码> <名称> --basic` | `<代码> <名称> 基本信息 主营业务` |
| 财务数据 | `python3 scripts/bocha_search.py <代码> <名称> --financial` | `<代码> 财报 业绩 ROE 市盈率` |
| 最新新闻 | `python3 scripts/bocha_search.py <代码> <名称> --news` | `<代码> 最新新闻 动态` |
| 行业信息 | `python3 scripts/bocha_search.py <代码> <名称> --industry` | `<行业> 龙头 对比 市场份额` |
| 综合搜索 | `python3 scripts/bocha_search.py <代码> <名称>` | 多次搜索组合 |
| 机构调研 | `python3 scripts/bocha_search.py <代码> <名称> --news` | `<代码> 机构调研 券商评级` |

详细搜索指南见：[references/bocha-api-guide.md](references/bocha-api-guide.md)、[references/metaso-mcp-guide.md](references/metaso-mcp-guide.md)

## 14维度分析框架

### 维度1-4：基础数据获取

**1. 股票信息查询** — 获取股票基本信息、主营业务、客户资源、竞争优势。
**2. 财务数据分析** — 查询营收、净利润、市盈率、ROE等关键财务指标。
**3. 新闻追踪** — 搜索最新新闻、重大事件、机构调研、政策影响。
**4. 行业对比分析** — 同一行业多家公司对比，分析竞争优势、市场格局。

### 维度5：商业理解

用大白话讲清楚公司的生意，让小学生都能听懂。
- 必须回答：这家公司解决什么问题？谁为此付费？为什么客户选它？
- 禁用金融术语，用日常语言（"护城河"→"别人抄不来的本事"）
- 详细指南：[references/business-explanation.md](references/business-explanation.md)

### 维度6：收入分解

把公司的收入拆开来看，找出哪块业务赚钱、哪块拖后腿、客户/产品是否过度集中。
- 输出收入结构健康度评分（0-50分）
- 详细指南：[references/revenue-breakdown.md](references/revenue-breakdown.md)

### 维度7：行业背景

判断公司所在行业的环境和趋势，行业是顺风还是逆风。
- 判断行业生命周期（导入期/成长期/成熟期/衰退期）
- 识别长期趋势（顺风/逆风）
- 详细指南：[references/industry-background.md](references/industry-background.md)

### 维度8：竞争格局

找出行业主要玩家，对比定价权、产品实力、规模、竞争壁垒。
- 列出3-5家竞争对手并排名
- 输出综合竞争力评分（0-50分）
- 详细指南：[references/competition-pattern.md](references/competition-pattern.md)

### 维度9：财务质量

分析近年财务质量，识别健康度和风险点。
- 五维分析：收入一致性、利润率稳定、债务安全、现金流质量、资本配置
- 识别财务陷阱（利润虚高、并购增长、高杠杆推ROE等）
- 输出财务质量评分（0-100分）
- 详细指南：[references/financial-quality.md](references/financial-quality.md)

### 维度10：风险与下行提示

识别最大风险点——"硬伤"（能死人的）和"软肋"（拖后腿的）。
- 四维分析：业务风险、财务风险、监管风险、永久伤害因素
- 输出综合风险评分（0-100分，越高越危险）
- 详细指南：[references/risk-downside.md](references/risk-downside.md)

### 维度11：管理层团队与执行

看班底靠不靠谱，过去战略对不对，投资是瞎投还是精算。
- 六维分析：战略执行、决策质量、风险控制、长期业绩、治理结构、股东回报
- 识别红旗警示信号
- 输出管理层评分（0-100分）
- 详细指南：[references/management-execution.md](references/management-execution.md)

### 维度12：牛熊情景

推演未来3-5年的牛市和熊市情景，关注基本面而非价格预测。
- 判断长期盈利驱动类型
- 推演三种情景及概率
- 详细指南：[references/bull-bear-scenarios.md](references/bull-bear-scenarios.md)

### 维度13：估值思考

评估内在价值，关键假设的敏感性比估值结果本身更重要。
- 选择合适的估值方法（PE/PB/DCF/PEG）
- 计算估值中枢和安全边际
- 识别估值陷阱
- 详细指南：[references/valuation-thinking.md](references/valuation-thinking.md)

### 维度14：长期论点

总结为什么这可能是好投资，什么必须成功，什么信号表明我错了。
- 确定投资逻辑类型（价值/成长/质量/反转/平台）
- 列出关键成功因素和危险信号
- 设置止损和加仓条件
- 计算预期年化收益率
- 详细指南：[references/long-term-thesis.md](references/long-term-thesis.md)

## 分析规则

### 核心原则

1. **Reference-First**：每个维度分析前，**必须先阅读对应的reference文档**，严格按照文档中的分析框架、评分标准和输出模板执行
2. **数据驱动**：所有分析必须基于搜索获得的数据，不编造数据
3. **大白话输出**：避免金融术语，使用日常语言
4. **评分量化**：每个维度都必须给出量化评分

### 分析执行步骤

对每个维度：
1. Read：阅读对应的 reference 文档
2. Search：使用博查API/秘塔搜索获取数据
3. Analyze：按照 reference 中的框架分析
4. Score：按照 reference 中的评分标准打分
5. Output：按照 reference 中的模板输出

### 基本面分析要素

| 维度 | 关键指标 | 参考文档 |
|------|----------|----------|
| 盈利能力 | ROE、毛利率、净利率 | financial-quality.md |
| 成长性 | 营收增速、净利润增速 | financial-quality.md |
| 财务健康 | 资产负债率、流动比率 | financial-quality.md |
| 现金流 | 经营现金流/净利润 | financial-quality.md |
| 估值 | PE、PB、PEG | valuation-thinking.md |
| 风险 | 业务/财务/监管风险 | risk-downside.md |

## 产出格式

### 14维度完整报告结构

```
# [股票代码] [股票名称] 综合分析报告

## 1. 📋 基本信息
## 2. 💰 财务数据概览
## 3. 📰 最新动态
## 4. 🏭 行业对比
## 5. 🏪 商业理解（大白话版）
## 6. 💰 收入分解 — 健康度评分: _/50
## 7. 🌍 行业背景
## 8. ⚔️ 竞争格局 — 竞争力评分: _/50
## 9. 💵 财务质量 — 质量评分: _/100
## 10. ⚠️ 风险与下行提示 — 风险评分: _/100
## 11. 👥 管理层与执行 — 管理评分: _/100
## 12. 🐂 牛熊情景
## 13. 💎 估值思考
## 14. 📊 长期论点

## 综合评分汇总
| 维度 | 评分 | 评级 |
|------|------|------|
| 收入结构健康度 | _/50 | |
| 竞争力 | _/50 | |
| 财务质量 | _/100 | |
| 风险程度 | _/100 | |
| 管理层质量 | _/100 | |

## 投资建议
```

## 长消息拆分规则

当分析内容超过一条消息的限制时，按维度拆分为多条消息发送。每条消息涵盖2-3个维度。

## 参考资源

### 分析维度参考文档

| 文档 | 对应维度 | 内容 |
|------|----------|------|
| [analysis-framework.md](references/analysis-framework.md) | 总体框架 | A股基本面分析框架 |
| [financial-ratios.md](references/financial-ratios.md) | 维度2 | 财务指标速查手册 |
| [business-explanation.md](references/business-explanation.md) | 维度5 | 大白话商业理解指南 |
| [revenue-breakdown.md](references/revenue-breakdown.md) | 维度6 | 收入分解分析指南 |
| [industry-background.md](references/industry-background.md) | 维度7 | 行业背景分析指南 |
| [competition-pattern.md](references/competition-pattern.md) | 维度8 | 竞争格局分析指南 |
| [financial-quality.md](references/financial-quality.md) | 维度9 | 财务质量分析指南 |
| [risk-downside.md](references/risk-downside.md) | 维度10 | 风险与下行提示指南 |
| [management-execution.md](references/management-execution.md) | 维度11 | 管理层分析指南 |
| [bull-bear-scenarios.md](references/bull-bear-scenarios.md) | 维度12 | 牛熊情景分析指南 |
| [valuation-thinking.md](references/valuation-thinking.md) | 维度13 | 估值思考指南 |
| [long-term-thesis.md](references/long-term-thesis.md) | 维度14 | 长期论点构建指南 |

### 工具使用指南

| 文档 | 内容 |
|------|------|
| [bocha-api-guide.md](references/bocha-api-guide.md) | 博查API配置和使用详细指南 |
| [metaso-mcp-guide.md](references/metaso-mcp-guide.md) | 秘塔MCP集成和使用指南 |
| [data-sources-guide.md](references/data-sources-guide.md) | 数据源使用和财务数据获取指南 |

## 注意事项

1. **搜索优先级**：始终先尝试博查API，失败时使用秘塔搜索
2. **数据时效**：使用最近1个月内的数据，财务数据可放宽至1年
3. **合规要求**：不做投资建议承诺，仅提供分析框架参考
4. **API密钥**：通过环境变量配置，不在代码中硬编码。详见 `scripts/.env.example`
5. **分析完整性**：每次分析至少覆盖14个维度中的关键维度，给出量化评分
