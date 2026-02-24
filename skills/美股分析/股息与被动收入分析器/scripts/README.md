# 股息分析脚本

本目录包含股息与被动收入分析相关的工具脚本。

## 脚本列表

### get_dividend.py

获取股息数据的脚本。

**功能**：
- 获取当前股息
- 计算股息率
- 获取除息日

**使用方式**：
```bash
python3 scripts/get_dividend.py AAPL
```

### dividend_history.py

分析股息历史的脚本。

**功能**：
- 获取历史股息数据
- 计算CAGR
- 识别贵族地位

**使用方式**：
```bash
python3 scripts/dividend_history.py AAPL
```

### drip_calculator.py

股息再投资计算器。

**功能**：
- 计算DRIP复利收益
- 预测5/10/20年收入
- 对比有/无DRIP

**使用方式**：
```bash
python3 scripts/drip_calculator.py AAPL --investment 10000 --years 20
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# Alpha Vantage API Key
ALPHAVANTAGE_API_KEY=your_key_here

# Financial Modeling Prep API Key
FMP_API_KEY=your_key_here
```

## 依赖安装

```bash
pip install yfinance pandas requests python-dotenv
```

## 注意事项

1. 股息数据来源多样
2. 历史数据可能缺失
3. DRIP假设股价不变
