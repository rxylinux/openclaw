# 财务报表分析脚本

本目录包含财务报表深度分析相关的工具脚本。

## 脚本列表

### fetch_financials.py

获取公司财务报表数据的脚本。

**功能**：
- 获取利润表数据
- 获取资产负债表数据
- 获取现金流量表数据
- 计算财务比率

**使用方式**：
```bash
python3 scripts/fetch_financials.py AAPL
```

### analyze_cashflow.py

分析现金流质量的脚本。

**功能**：
- 计算自由现金流
- 计算FCF利润率
- 检查现金流与利润匹配度

**使用方式**：
```bash
python3 scripts/analyze_cashflow.py AAPL
```

### risk_signals.py

检查财务风险信号的脚本。

**功能**：
- 检查6项风险信号
- 生成风险评估报告

**使用方式**：
```bash
python3 scripts/risk_signals.py AAPL
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

1. 免费API有请求限制
2. 财报数据有45-60天延迟
3. 建议多个数据源交叉验证
