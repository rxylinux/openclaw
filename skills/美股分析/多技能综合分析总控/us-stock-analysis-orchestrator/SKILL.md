---
name: us-stock-analysis-orchestrator
description: Use when the user asks for multi-skill comprehensive US stock analysis, integrated company research, combined financial statement, earnings, peer, valuation, risk, and macro analysis, or wants several stock-analysis skills applied to one company in one final report.
---

# 美股多技能综合分析总控

## Core Rule

Use this as the controller when one company needs a single integrated investment view across multiple analysis skills. Do not output seven disconnected reports. Gather the relevant facts from each module, resolve conflicts, and produce one coherent conclusion.

## Trigger Examples

Use this skill for requests like:

- "对 NVDA 做多技能综合分析"
- "用多个 skill 分析 TSLA"
- "给我一份整合财务、估值、风险和宏观的 AAPL 报告"
- "方案3分析微软"
- "综合判断这家公司能不能买"

If the user asks for a full due-diligence report with formal investment-bank style sections, you may use `comprehensive-due-diligence` as the base format, but still apply the orchestration flow below.

## Orchestration Flow

Apply these skills in order. If a module is not relevant or data is unavailable, mark it explicitly rather than inventing content.

1. `complete-stock-analysis` - company business, revenue structure, core financials, price performance, analyst consensus, institutional ownership.
2. `earnings-call-analyzer` - latest earnings release, call transcript, management guidance, tone, market reaction.
3. `financial-statement-deep-dive` - income statement, balance sheet, cash flow, accounting quality, financial trend checks.
4. `industry-comparison-analyzer` - peer comparison, industry position, moat, market share, relative strengths and weaknesses.
5. `valuation-model-builder` - DCF, WACC, comparable valuation, historical multiples, Bull/Base/Bear scenarios.
6. `risk-flag-scanner` - financial risk, accounting risk, regulatory/legal risk, insider activity, short interest, concentration risk.
7. `macro-market-scanner` - rates, inflation, economic data, market sentiment, sector rotation, event calendar.

## Data Integrity Requirements

- Every factual data point must include source and date.
- If a source is unavailable, write `未获取` or `未公开披露`; do not estimate or fill gaps.
- Management quotes must be real transcript or filing quotes; never fabricate them.
- Forward-looking statements, target prices, scenario probabilities, growth rates, WACC assumptions, and catalysts must be labeled `[ASSUMPTION]`.
- Separate confirmed facts from forecasts and market expectations.
- If sources conflict, prefer SEC/company filings for reported financials and explain the conflict.
- Include a short disclaimer that the output is research and education, not investment advice.

## Output Contract

Use this structure by default:

```markdown
# [Ticker] 多技能综合分析

## 1. 一页结论

| 项目 | 结论 | 依据 |
|------|------|------|
| 综合判断 | 买入 / 持有 / 回避 | |
| 核心逻辑 | | |
| 估值区间 | $ - $ | [ASSUMPTION] |
| 最大上行因素 | | |
| 最大下行风险 | | |
| 信心等级 | 高 / 中 / 低 | |

## 2. 关键数据表

| 类别 | 指标 | 数值 | 来源 | 日期 |
|------|------|------|------|------|
| 股价与市值 | 当前股价 | | | |
| 财务 | TTM 营收 | | | |
| 财务 | TTM 自由现金流 | | | |
| 估值 | P/E 或 EV/EBITDA | | | |
| 风险 | 做空比例 / 债务风险 | | | |

## 3. 模块发现

### 公司与核心财务
[来自 complete-stock-analysis 的关键发现]

### 最新财报与管理层指引
[来自 earnings-call-analyzer 的关键发现]

### 财务报表与会计质量
[来自 financial-statement-deep-dive 的关键发现]

### 行业与竞争位置
[来自 industry-comparison-analyzer 的关键发现]

### 估值与情景分析
[来自 valuation-model-builder 的关键发现]

### 风险与红旗
[来自 risk-flag-scanner 的关键发现]

### 宏观与市场环境
[来自 macro-market-scanner 的关键发现]

## 4. 估值区间

| 情景 | 合理价值 | 关键假设 | 概率 |
|------|----------|----------|------|
| Bull | $ | [ASSUMPTION] | [ASSUMPTION] |
| Base | $ | [ASSUMPTION] | [ASSUMPTION] |
| Bear | $ | [ASSUMPTION] | [ASSUMPTION] |

## 5. 最大风险

1. [风险 1：证据、来源、监控指标]
2. [风险 2：证据、来源、监控指标]
3. [风险 3：证据、来源、监控指标]

## 6. 未来 90 天催化剂

| 日期/窗口 | 催化剂 | 可能影响 | 来源 |
|-----------|--------|----------|------|
| | | | |

## 7. 最终投资判断

[用 3-5 句话合并所有模块的证据，给出买入 / 持有 / 回避判断。]

## 数据来源与免责声明

- 数据来源汇总：[列出使用过的 filings、IR、行情、宏观和第三方来源]
- 免责声明：本分析仅用于研究和教育，不构成投资建议。
```

## Conflict Handling

- If valuation says "cheap" but risk scanner finds severe red flags, downgrade the final judgment and explain why risk dominates.
- If earnings are strong but cash flow quality is weak, treat the quarter as "mixed" unless cash-flow timing is clearly explained by filings.
- If macro is unfavorable but company fundamentals are strong, separate tactical timing risk from long-term quality.
- If key data is missing, reduce confidence rather than filling the gap.

## Quick Prompt

Users can invoke this skill with:

```text
对 [Ticker/公司] 做多技能综合分析。
输出一页结论、关键数据表、模块发现、估值区间、最大风险、未来 90 天催化剂和最终买入/持有/回避判断。
所有事实数据标注来源和日期，未获取数据不要编造，所有假设标注 [ASSUMPTION]。
```
