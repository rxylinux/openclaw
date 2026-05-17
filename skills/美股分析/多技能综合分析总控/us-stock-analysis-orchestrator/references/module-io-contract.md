# Module IO Contract

Use this contract to coordinate module outputs for one integrated company analysis. Do not expose this as a separate report unless the user asks for process details.

## Inputs

Collect these inputs before or during module execution:

| Field | Required | Notes |
|-------|----------|-------|
| Company or ticker | Yes | Resolve ticker, exchange, and company name when possible. |
| Analysis date | Yes | Use current date for report timestamp. |
| User objective | Yes | Buy/hold/sell, watchlist, income, valuation, risk, or full DD. |
| Time horizon | Preferred | If absent, use 6-18 months and label as `[ASSUMPTION]`. |
| Risk tolerance | Preferred | If absent, avoid portfolio-size recommendations. |
| Existing position | Optional | Use only if user provides it. |

## Core Module Outputs

| Module | Required Output | Required Source Discipline |
|--------|-----------------|----------------------------|
| `complete-stock-analysis` | Business summary, revenue mix, recent price context, analyst/institutional snapshot | Source/date for company facts, price, consensus, ownership. |
| `earnings-call-analyzer` | Latest quarter result, guidance, management tone, important quote, market reaction | Use actual release/transcript quotes only; mark missing transcript as `未获取`. |
| `financial-statement-deep-dive` | Revenue/profit/cash-flow trend, balance-sheet strength, accounting-quality notes | Prefer SEC filings and company reports for reported figures. |
| `industry-comparison-analyzer` | Peer set, relative growth, margin, valuation, moat, winner/laggard view | Explain peer selection and source/date for peer metrics. |
| `valuation-model-builder` | Bull/Base/Bear fair value range, key assumptions, sensitivity, current valuation context | Mark growth, WACC, multiples, probabilities, and target prices as `[ASSUMPTION]`. |
| `risk-flag-scanner` | Top risks, red flags, severity, evidence, monitoring indicators | Separate confirmed risk evidence from hypothesis. |
| `macro-market-scanner` | Macro backdrop, rates/inflation/liquidity, sector sentiment, 90-day event risks | Date macro releases and distinguish current data from forecasts. |

## Conditional Module Outputs

| Module | Trigger | Required Output |
|--------|---------|-----------------|
| `dividend-income-analyzer` | Dividends, income, yield, payout safety, DRIP | Dividend safety, payout coverage, income projection, dividend peer comparison. |
| `etf-portfolio-analyzer` | ETF, fund, basket, portfolio | Exposure, holdings, overlap, fees, tracking, risk metrics, portfolio actions. |
| `comprehensive-due-diligence` | Formal memo, full DD, investment committee output | Use as final formatting layer; keep orchestrator evidence and conflict rules. |

## Conflict Priority

Use this priority order when facts conflict:

1. SEC filings and company filings for reported historical financials.
2. Company investor relations releases and presentations for company-disclosed operating metrics.
3. Earnings call transcripts for management wording and guidance tone.
4. Exchange, official macro agencies, and index providers for market/macro data.
5. Reputable financial data vendors for derived metrics, estimates, and consensus.

When estimates conflict with reported data, keep reported data as fact and describe estimates separately as market expectations.

## Final Synthesis Requirements

- Final recommendation must cite the dominant evidence from at least valuation, risk, and business/fundamental modules.
- Confidence must be reduced when key current data is unavailable.
- Use `买入`, `持有`, or `回避` unless the user requests a different rating scale.
- Never create exact target prices without showing the assumption basis.
- Do not turn every module into a long section; keep only decision-useful findings.
