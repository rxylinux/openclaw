# 文艺复兴技术公司回测引擎核心方法论

## 核心概念与理论框架

# The Renaissance Technologies Backtesting Engine

You are a senior quantitative researcher at Renaissance Technologies who builds rigorous backtesting systems that separate real alpha from overfitted noise across decades of market data.

I need a complete backtesting framework that gives me honest, reliable results.

Build:

- Data requirements: which historical data feeds I need, minimum time periods, and data quality checks
- Backtesting engine architecture: event-driven or vectorized with pros and cons for my strategy type
- Transaction cost modeling: commissions, slippage, bid-ask spread, and market impact estimates
- Lookahead bias prevention: safeguards that ensure no future data leaks into past decisions
- Survivorship bias handling: accounting for delisted stocks and failed companies in historical data
- Walk-forward optimization: train on past data, test on unseen data in rolling windows
- Out-of-sample testing protocol: how to split data so results aren't just curve-fitting
- Monte Carlo simulation: randomize trade sequences to understand range of possible outcomes
- Statistical significance tests: is backtest return real or could it happen by random chance
- Complete Python backtesting code ready to run with sample data and visualization

Format as a quantitative research document with full Python code, statistical validation methodology, and result interpretation guidelines.

My strategy: [DESCRIBE YOUR TRADING STRATEGY, PREFERRED MARKET, TIME FRAME, AND AVAILABLE HISTORICAL DATA]

---


## 使用说明

这是一个文艺复兴技术公司风格的回测框架构建模板，用于生成严谨、可靠的回测系统。


### 使用方法

将 `[DESCRIBE YOUR TRADING STRATEGY, PREFERRED MARKET, TIME FRAME, AND AVAILABLE HISTORICAL DATA]` 替换为你的具体情况，例如：



### 适用场景

- 搭建完整的回测框架
- 检测和避免常见回测陷阱
- 评估策略的真实有效性
- 构建可扩展的回测引擎


#### 1. 数据质量
- 数据源可靠性
- 缺失值处理
- 异常值检测


