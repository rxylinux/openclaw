---
name: us-stock-analysis-orchestrator
description: Use when the user asks for multi-skill comprehensive US stock analysis, integrated company research, combined financial statement, earnings, peer, valuation, risk, and macro analysis, or wants several stock-analysis skills applied to one company in one final report.
---

# 美股多技能综合分析总控

## Core Rule

Use this as the controller when one company needs a single integrated investment view across multiple analysis skills. Do not output separate module reports. Coordinate module findings, resolve conflicts, and produce one final conclusion.

## When To Use

Use for requests like:

- "对 NVDA 做多技能综合分析"
- "用多个 skill 分析 TSLA"
- "方案3分析微软"
- "综合判断这家公司能不能买"
- "整合财务、估值、风险和宏观，给我一份结论"

If the user asks for a formal investment memo or full due-diligence report, use `comprehensive-due-diligence` as the final report style while still following this orchestration flow.

## Required References

Load these files when this skill triggers:

- [references/module-io-contract.md](references/module-io-contract.md) - module selection, required outputs, source rules, and conflict priority.
- [assets/orchestrator-report-template.md](assets/orchestrator-report-template.md) - default final report skeleton.

## Orchestration Flow

Apply the core modules in this order unless the user narrows the request:

1. `complete-stock-analysis` - business model, revenue structure, core financials, price performance, analyst consensus, institutional ownership.
2. `earnings-call-analyzer` - latest earnings release, call transcript, management guidance, tone, market reaction.
3. `financial-statement-deep-dive` - income statement, balance sheet, cash flow, accounting quality, financial trend checks.
4. `industry-comparison-analyzer` - peer comparison, industry position, moat, market share, relative strengths and weaknesses.
5. `valuation-model-builder` - DCF, WACC, comparable valuation, historical multiples, Bull/Base/Bear scenarios.
6. `risk-flag-scanner` - financial risk, accounting risk, regulatory/legal risk, insider activity, short interest, concentration risk.
7. `macro-market-scanner` - rates, inflation, economic data, market sentiment, sector rotation, event calendar.

## Conditional Modules

Add these modules only when relevant:

- `dividend-income-analyzer`: user asks about dividends, passive income, yield, payout safety, DRIP, income suitability, or dividend growth.
- `etf-portfolio-analyzer`: target is an ETF, fund, basket, or portfolio rather than a single operating company.
- `comprehensive-due-diligence`: user asks for a formal due diligence report, investment memo, first coverage report, or investment committee style output.

If a conditional module conflicts with the core flow, explain the scope decision before the final report. Example: for an ETF request, use `etf-portfolio-analyzer` as the primary module and skip operating-company modules that do not apply.

## Data Integrity Requirements

- Every factual data point must include source and date.
- If a source is unavailable, write `未获取` or `未公开披露`; do not estimate or fill gaps.
- Management quotes must be real transcript or filing quotes; never fabricate them.
- Forward-looking statements, target prices, scenario probabilities, growth rates, WACC assumptions, and catalysts must be labeled `[ASSUMPTION]`.
- Separate confirmed facts from forecasts and market expectations.
- Prefer SEC/company filings for reported financials when sources conflict, and explain the conflict.
- Include a short disclaimer that the output is research and education, not investment advice.

## Integration Rules

- Produce one integrated report, not a concatenation of module outputs.
- Each module should contribute only its highest-signal findings to the final report.
- Keep duplicated facts in the key data table once; reference them from modules as needed.
- If valuation says "cheap" but risk scanning finds severe red flags, downgrade the final judgment and explain why risk dominates.
- If earnings are strong but cash flow quality is weak, treat the quarter as mixed unless filings clearly explain cash-flow timing.
- If macro is unfavorable but company fundamentals are strong, separate tactical timing risk from long-term quality.
- If key data is missing, reduce confidence rather than filling the gap.

## Quick Prompt

Users can invoke this skill with:

```text
对 [Ticker/公司] 做多技能综合分析。
输出一页结论、关键数据表、模块发现、估值区间、最大风险、未来 90 天催化剂和最终买入/持有/回避判断。
所有事实数据标注来源和日期，未获取数据不要编造，所有假设标注 [ASSUMPTION]。
```
