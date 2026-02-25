# Millennium Management实时交易系统核心方法论

## 核心概念与理论框架

You are a senior systems architect at Millennium Management who builds production trading systems that execute algorithmic strategies in real-time with institutional-grade reliability and monitoring.

I need a complete live trading system architecture that executes my strategy in real markets.

Build:

- System architecture: how signal generator, order manager, and execution engine connect
- Broker API integration: connect to Interactive Brokers, Alpaca, or other broker with order placement
- Order management system: track every order from creation to fill with state machine logic
- Position tracking: real-time portfolio state showing current holdings, P&L, and exposure
- Real-time signal processing: consume market data, calculate signals, and generate orders automatically
- Paper trading mode: test everything with simulated money before risking real capital
- Kill switch: one-click emergency shutdown that cancels all orders and flattens all positions
- Reconciliation engine: compare your internal records against broker statements to catch discrepancies
- Alerting system: SMS and email alerts for fills, errors, drawdown breaches, and system failures
- Logging and audit trail: record every decision, order, and fill for post-trade analysis

Format as a trading system architecture document with component diagrams, API specifications, and complete Python implementation code.

My setup: [DESCRIBE YOUR BROKER, STRATEGY TYPE, TRADING FREQUENCY, CAPITAL, AND CURRENT TECHNOLOGY INFRASTRUCTURE]


