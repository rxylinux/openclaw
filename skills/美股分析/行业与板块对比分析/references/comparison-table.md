# 对比表格模板

## 基础指标对比表

### 市值与营收

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| 股票代码 | XXX | XXX | XXX |
| 市值（十亿美元） | $XXX | $XXX | $XXX |
| TTM营收（十亿美元） | $XXX | $XXX | $XXX |
| 营收同比增长率 | X.X% | X.X% | X.X% |

*数据来源：各公司最新财报/ Yahoo Finance，日期：YYYY-MM-DD*

### 利润率对比

| 指标 | 公司A | 公司B | 公司C | 最佳 |
|------|------|------|------|------|
| 毛利率 | XX.X% | XX.X% | XX.X% | XX.X% |
| 营业利润率 | XX.X% | XX.X% | XX.X% | XX.X% |
| 净利率 | XX.X% | XX.X% | XX.X% | XX.X% |

*数据来源：各公司最新财报，日期：YYYY-MM-DD*

**利润率排名**：
- **毛利率**：[最高] > [中等] > [最低]
- **营业利润率**：[最高] > [中等] > [最低]
- **净利率**：[最高] > [中等] > [最低]

## 估值指标对比表

### 市场倍数

| 指标 | 公司A | 公司B | 公司C | 行业平均 |
|------|------|------|------|---------|
| 市盈率（P/E） | XX.X | XX.X | XX.X | XX.X |
| 预期市盈率（Forward P/E） | XX.X | XX.X | XX.X | XX.X |
| 市销率（P/S） | X.X | X.X | X.X | X.X |
| EV/EBITDA | XX.X | XX.X | XX.X | XX.X |
| PEG比率 | X.XX | X.XX | X.XX | X.XX |

*数据来源：Yahoo Finance / Bloomberg，日期：YYYY-MM-DD*

### 估值分析

**相对估值评估**：
- **P/E最低**：[公司名称]（最便宜）
- **P/E最高**：[公司名称]（最贵）
- **PEG最低**：[公司名称]（增长相对估值最便宜）

## 财务健康度对比表

### 资产负债表指标

| 指标 | 公司A | 公司B | 公司C | 最健康 |
|------|------|------|------|--------|
| 资产负债率 | XX% | XX% | XX% | XX% |
| 债务股权比 | X.XX | X.XX | X.XX | X.XX |
| 净负债（十亿美元） | $XXX | $XXX | $XXX | $XXX |
| 现金（十亿美元） | $XXX | $XXX | $XXX | $XXX |

*数据来源：各公司最新资产负债表，日期：YYYY-MM-DD*

### 现金流指标

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| 自由现金流（十亿美元） | $XXX | $XXX | $XXX |
| FCF收益率 | X.X% | X.X% | X.X% |
| FCF利润率 | X.X% | X.X% | X.X% |

*数据来源：各公司现金流量表，日期：YYYY-MM-DD*

**财务健康度排名**：
- **资产负债表最健康**：[公司名称]
- **现金最充裕**：[公司名称]
- **FCF收益率最高**：[公司名称]

## 行业关键指标对比表

### SaaS行业指标

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| ARR（十亿美元） | $XXX | $XXX | $XXX |
| 同比增长率 | X.X% | X.X% | X.X% |
| 客户数量 | XXX | XXX | XXX |
| 流失率 | X.X% | X.X% | X.X% |
| NDR | XXX% | XXX% | XXX% |

*数据来源：各公司财报/投资者演示，日期：YYYY-MM-DD*

### 电商行业指标

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| GMV（十亿美元） | $XXX | $XXX | $XXX |
| 活跃买家（百万） | XXX | XXX | XXX |
| 订单量（百万） | XXX | XXX | XXX |
| AOV（平均订单价值） | $XXX | $XXX | $XXX |

*数据来源：各公司财报，日期：YYYY-MM-DD*

### 社交媒体指标

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| MAU（百万） | XXX | XXX | XXX |
| DAU（百万） | XXX | XXX | XXX |
| 用户时长（分钟/日） | XXX | XXX | XXX |
| ARPU（美元） | $X.XX | $X.XX | $X.XX |

*数据来源：各公司财报，日期：YYYY-MM-DD*

### 云计算指标

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| 云服务收入（十亿美元） | $XXX | $XXX | $XXX |
| 同比增长率 | X.X% | X.X% | X.X% |
| 客户数量 | XXX | XXX | XXX |
| 基础设施数量 | XXX | XXX | XXX |

*数据来源：各公司财报，日期：YYYY-MM-DD*

## 数据来源说明

### 主要数据源

1. **市值数据**：
   - Yahoo Finance
   - Google Finance
   - Nasdaq.com

2. **财务数据**：
   - 10-K/10-Q（SEC文件）
   - 季度财报
   - 投资者演示材料

3. **估值倍数**：
   - Yahoo Finance
   - Bloomberg
   - FactSet

4. **行业特定数据**：
   - 公司财报
   - 行业报告
   - 投资者演示

### 数据获取方法

#### Yahoo Finance API

```python
import yfinance as yf

def get_company_data(ticker):
    ticker_obj = yf.Ticker(ticker)

    # 基础数据
    info = ticker_obj.info

    # 财务数据
    financials = ticker_obj.financials
    quarterly_financials = ticker_obj.quarterly_financials

    return info
```

#### 财报数据

```python
import requests

# 获取SEC 10-Q文件
def get_10q(cik, year, quarter):
    url = f"https://www.sec.gov/files/edgar/data/{cik}10q{year}{quarter}.htm"
    return requests.get(url).text
```

## 数据时效性标记

### 时效性标准

- **实时**：当日数据（股票价格、市值）
- **近期**：最近1个月
- **季度**：最新季度财报
- **过期警告**：超过30天需标记

### 标记格式

```
数值（来源：XXX，日期：YYYY-MM-DD）⚠️ 数据可能已过期
```

## 缺失数据处理

### 处理原则

1. **明确标注**：使用 'N/A 未公开披露'
2. **不得估算**：不插值或计算缺失数据
3. **说明原因**：简要说明为何不可获取

### 示例

| 指标 | 公司A | 公司B | 公司C |
|------|------|------|------|
| 某指标 | XX.X | N/A 未公开披露 | XX.X |

*注：公司B未披露该数据*
