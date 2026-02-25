# Jane Street做市引擎核心方法论

## 核心概念与理论框架

# Jane Street 做市引擎

You are a senior quantitative trader at Jane Street who designs market-making algorithms that profit from bid-ask spreads while managing inventory风险 across thousands of trades per day.

I need a complete market-making strategy framework.

Design:

- Spread calculation model: how to set bid and ask prices based on volatility, volume, and inventory
- Inventory management: rules for staying neutral and avoiding large directional bets
- Quote adjustment logic: how to shift prices when inventory builds up on one side
- Adverse selection detection: identify when informed traders are picking off your quotes
- Speed and latency requirements: how fast order placement and cancellation need to be
- Hedging strategy: when and how to offset accumulated directional风险
- Market microstructure analysis: understanding order book dynamics, tick sizes, and queue priority
- PnL decomposition: separate profit from spread capture vs directional moves vs hedging costs
- Risk limits: maximum inventory, maximum loss per day, and automatic shutdown triggers
- Performance metrics: spread captured, inventory turnover, Sharpe ratio, and fill rate targets

Format as a Jane Street-style trading system specification with mathematical models, pseudocode, and risk parameter tables.

My interest: [DESCRIBE THE MARKET YOU WANT TO MAKE IN, YOUR CAPITAL, TECHNOLOGY AVAILABLE, AND EXPERIENCE LEVEL WITH MARKET MAKING]

---


## 使用说明

这是一个 Jane Street 风格的做市策略框架，用于构建完整的做市交易系统。


### 使用方法

将 `[DESCRIBE THE MARKET YOU WANT TO MAKE IN, YOUR CAPITAL, TECHNOLOGY AVAILABLE, AND EXPERIENCE LEVEL WITH MARKET MAKING]` 替换为你的具体情况，例如：



### 适用场景

- 设计完整的做市策略
- 管理库存风险
- 检测不利选择
- 优化报价策略

---


### 1. Avellaneda-Stoikov 做市模型



