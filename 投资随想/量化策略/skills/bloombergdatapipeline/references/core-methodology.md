# 彭博终端数据管道构建器核心方法论

## 核心概念与理论框架

# 彭博终端数据管道构建器

You are a senior quantitative data engineer at Bloomberg who builds real-time and historical data pipelines feeding algorithmic trading systems at the world's largest hedge funds.

I need a complete market data pipeline for my trading system.

Build:

- Data source architecture: free and paid sources for price, fundamental, sentiment and alternative data
- Real-time data feed: WebSocket connections to live market data with reconnection handling
- Historical data storage: database design for efficiently storing years of tick, minute and daily data
- Data cleaning pipeline: handle missing values, stock splits, dividends and delistings automatically
- Corporate action adjustment: automatically adjust historical prices for splits, mergers and spinoffs
- Feature store: pre-computed technical indicators and fundamental ratios ready for signal generation
- Data validation rules: automated checks that catch bad data before it triggers false trades
- API layer: clean endpoints your trading strategy can query for any data point instantly
- Scheduling system: automated daily updates, weekly fundamental refreshes and monthly recalculations
- Complete Python data pipeline code with database setup, data ingestion and API serving

Format as a data engineering specification with pipeline diagrams, database schemas and production-ready Python code.

My needs: [DESCRIBE YOUR TRADING ASSETS, DATA SOURCES YOU HAVE ACCESS TO, UPDATE FREQUENCY NEEDED, AND STORAGE PREFERENCES]

---


## 使用说明

这是一个 Bloomberg 风格的实时和历史数据管道构建框架。


### 使用方法

将 `[DESCRIBE YOUR TRADING ASSETS, DATA SOURCES YOU HAVE ACCESS TO, UPDATE FREQUENCY NEEDED, AND STORAGE PREFERENCES]` 替换为你的具体情况，例如：



### 适用场景

- 构建实时交易数据管道
- 历史数据存储和管理
- 多数据源整合
- 数据质量保证
- 企业行动自动处理

---


### 1. 数据源分类


---


