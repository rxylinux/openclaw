# 美股分析脚本

本目录包含美股分析相关的工具脚本。

## 脚本列表

### fetch_us_stock_data.py

获取美股股票数据的脚本。

**功能**：
- 获取实时股价
- 获取财务数据
- 获取估值指标
- 获取历史价格

**使用方式**：
```bash
python3 scripts/fetch_us_stock_data.py AAPL
```

### get_analyst_ratings.py

获取分析师评级和目标价的脚本。

**功能**：
- 获取分析师评级分布
- 获取目标价数据
- 获取最新评级调整

**使用方式**：
```bash
python3 scripts/get_analyst_ratings.py AAPL
```

### get_institutional_holdings.py

获取机构持仓数据的脚本。

**功能**：
- 获取前5大机构持仓
- 获取持仓变化
- 获取对冲基金动向

**使用方式**：
```bash
python3 scripts/get_institutional_holdings.py AAPL
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# Alpha Vantage API Key (可选)
ALPHAVANTAGE_API_KEY=your_key_here

# Polygon.io API Key (可选)
POLYGON_API_KEY=your_key_here
```

## 依赖安装

```bash
pip install yfinance pandas requests python-dotenv
```

## 注意事项

1. 某些API需要申请密钥
2. 免费API有请求限制
3. 数据可能延迟15-20分钟
4. 建议多个数据源交叉验证
