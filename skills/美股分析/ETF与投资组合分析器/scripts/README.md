# 投资组合分析脚本

本目录包含ETF和投资组合分析相关的工具脚本。

## 脚本列表

### get_holdings.py

获取ETF持仓数据的脚本。

**功能**：
- 获取前10大持仓
- 分析行业配置
- 计算权重占比

**使用方式**：
```bash
python3 scripts/get_holdings.py VOO
```

### analyze_risk.py

风险指标计算脚本。

**功能**：
- 计算组合Beta
- 计算波动率
- 分析持仓相关性
- 计算最大回撤

**使用5-式**：
```bash
python3 scripts/analyze_risk.py VOO
```

### cost_calculator.py

成本分析脚本。

**功能**：
- 计算加权费用率
- 对比不同投资规模
- 寻找低成本替代品

**使用方式**：
```bash
python3 scripts/cost_calculator.py VOO --investment 10000
```

### stress_test.py

历史压力测试脚本。

**功能**：
- 2008金融危机表现
- 2020疫情暴跌
- 2022熊市表现
- 计算恢复时间

**使用方式**：
```bash
python3 scripts/stress_test.py VOO
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# Alpha Vantage API Key
ALPHAVANTAGE_API_KEY=your_key_here

# Financial Modeling Prep API Key
FMP_API_KEY=your_key_here

# Morningstar API Key (用于获取历史数据)
MORNINGSTAR_API_KEY=your_key_here
```

## 依赖安装

```bash
pip install yfinance pandas numpy requests python-dotenv
```

## 注意事项

1. 历史数据可能不完整
2. 费用数据来源于招募书
3. Beta计算需要基准数据
4. 压力测试基于历史，不预示未来
