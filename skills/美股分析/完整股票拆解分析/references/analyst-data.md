# 分析师数据获取方法

## 分析师评级数据

### 评级分布表

| 评级类型 | 数量 | 占比 |
|---------|------|------|
| 买入（Buy） | XX  | XX%  |
| 持有（Hold）| XX  | XX%  |
| 卖出（Sell）| XX  | XX%  |
| **总计**   | **XX** | **100%** |

*注：不同机构使用的评级术语可能不同（如 Outperform、Neutral、Underperform）*

### 目标价汇总

| 指标     | 金额       |
|---------|-----------|
| 平均目标价 | $XXX.XX   |
| 最高目标价 | $XXX.XX   |
| 最低目标价 | $XXX.XX   |
| 当前价格   | $XXX.XX   |
| 上涨空间   | +X.X%     |

### 上涨空间计算

上涨空间 = (平均目标价 - 当前价格) / 当前价格 × 100%

## 最近评级变动

### 评级变动追踪

| 日期 | 机构 | 原评级 | 新评级 | 目标价调整 |
|------|------|--------|--------|-----------|
| YYYY-MM-DD | XXXX | 持有 | 买入 | $XXX |
| YYYY-MM-DD | XXXX | 买入 | 持有 | $XXX |

### 重点关注

- **近期上调**：可能预示利好消息
- **近期下调**：可能预示风险因素
- **首次覆盖**：新投行开始关注

## 数据来源

### 专业数据平台
- Bloomberg Terminal
- FactSet
- Refinitiv (formerly Thomson Reuters)
- I/B/E/S (Institutional Brokers' Estimate System)

### 免费数据来源
- Yahoo Finance（Analyst Ratings）
- TipRanks
- MarketBeat
- Seeking Alpha
- Nasdaq.com

### 公司披露
- 公司财报演示材料中的分析师数据
- 投资者关系网站

## 数据获取方法

### API 获取
```python
# Yahoo Finance 示例
import yfinance as yf

ticker = yf.Ticker("AAPL")
analyst_info = ticker.info

# 获取目标价
target_price = analyst_info.get('targetMeanPrice')
# 获取评级分布
recommendations = ticker.recommendations
```

### 网页抓取
- 注意遵守网站 robots.txt
- 检查数据使用条款

## 数据时效性

- **分析师数据**：通常每周更新
- **目标价**：随财报发布频繁调整
- **评级变动**：实时更新
- **数据标注**：注明数据获取日期

## 注意事项

1. **评级术语不统一**：
   - Buy = Strong Buy = Overweight = Outperform
   - Hold = Neutral = Equal Weight = Market Perform
   - Sell = Underweight = Underperform

2. **利益冲突**：
   - 投行可能与公司有投行业务关系
   - 评级可能偏乐观

3. **准确度**：
   - 分析师预测历史准确度有限
   - 应作为参考而非投资依据
