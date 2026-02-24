# 行业对比分析脚本

本目录包含行业对比分析相关的工具脚本。

## 脚本列表

### compare_companies.py

对比多家公司财务数据的脚本。

**功能**：
- 获取多家公司财务数据
- 建立对比表格
- 计算关键比率

**使用方式**：
```bash
python3 scripts/compare_companies.py AAPL MSFT GOOGL
```

### market_share.py

获取市场份额数据的脚本。

**功能**：
- 获取行业市场份额
- 对比份额变化
- 识别领导者

**使用方式**：
```bash
python3 scripts/market_share.py cloud
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

1. 对比需用同一时间段数据
2. 市场份额数据来源不一
3. 部分数据可能不可得
