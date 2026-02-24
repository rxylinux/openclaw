# 利润表分析方法

## 营收分析

### 最近4季度营收表

| 季度 | 营收（百万美元） | 同比增长 | 环比增长 |
|------|----------------|---------|---------|
| Q1 YYYY | $X,XXX | +X.X% | +X.X% |
| Q2 YYYY | $X,XXX | +X.X% | +X.X% |
| Q3 YYYY | $X,XXX | +X.X% | +X.X% |
| Q4 YYYY | $X,XXX | +X.X% | +X.X% |

*数据来源：10-Q/10-K，报告日期：YYYY-MM-DD*

### 计算方法

**同比增长率**：
```
同比增长率 = (本期营收 - 去年同期营收) / 去年同期营收 × 100%
```

**环比增长率**：
```
环比增长率 = (本期营收 - 上期营收) / 上期营收 × 100%
```

## 利润率分析

### 三大利润率

| 季度 | 毛利率 | 营业利润率 | 净利率 |
|------|--------|-----------|--------|
| Q1 | XX.X% | XX.X% | XX.X% |
| Q2 | XX.X% | XX.X% | XX.X% |
| Q3 | XX.X% | XX.X% | XX.X% |
| Q4 | XX.X% | XX.X% | XX.X% |
| **趋势** | ↗️/→/↘️ | ↗️/→/↘️ | ↗️/→/↘️ |

*数据来源：10-Q/10-K，报告日期：YYYY-MM-DD*

### 利润率定义

**毛利率**：
```
毛利率 = (营收 - 销售成本) / 营收 × 100%
```

**营业利润率**：
```
营业利润率 = 营业利润 / 营收 × 100%
```

**净利率**：
```
净利率 = 净利润 / 营收 × 100%
```

### 趋势判断

| 变化幅度 | 判断 |
|---------|------|
| > +1.0% | 显著扩张 ↗️ |
| +0.5% ~ +1.0% | 温和扩张 ↗️ |
| -0.5% ~ +0.5% | 稳定 → |
| -1.0% ~ -0.5% | 温和收缩 ↘️ |
| < -1.0% | 显著收缩 ↘️ |

## 研发支出分析

### 研发强度表

| 季度 | 研发支出（百万美元） | 占营收比例 | 同比变化 |
|------|-------------------|-----------|---------|
| Q1 | $XXX | XX.X% | +X.X% |
| Q2 | $XXX | XX.X% | +X.X% |
| Q3 | $XXX | XX.X% | +X.X% |
| Q4 | $XXX | XX.X% | +X.X% |

*数据来源：10-Q/10-K，报告日期：YYYY-MM-DD*

### 研发强度评估

| 占比 | 评估 |
|------|------|
| > 15% | 高度研发密集型 |
| 8-15% | 中度研发密集型 |
| 3-8% | 低度研发密集型 |
| < 3% | 非研发密集型 |

## 数据来源

### SEC 文件

- **10-K**：年度报告（包含完整年度利润表）
- **10-Q**：季度报告（包含季度利润表）
- **8-K**：当前报告（重大事项）

### 公司财报

- 季度财报（Earnings Release）
- 年度报告（Annual Report）
- 投资者演示材料（Investor Presentation）

### 金融数据平台

- Bloomberg
- FactSet
- Yahoo Finance
- Seeking Alpha

## 获取方法

### SEC EDGAR

```python
import requests

# 获取10-Q文件
def get_10q(cik, year, quarter):
    url = f"https://www.sec.gov/files/qa/{cik}10q{year}{quarter}.htm"
    return requests.get(url).text
```

### Yahoo Finance API

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
income_stmt = ticker.financials
quarterly_stmt = ticker.quarterly_financials
```
