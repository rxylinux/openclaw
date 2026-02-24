# 美股数据源指南

## 概述

本文档介绍美股分析中可用的主要数据源及其特点。

## 免费数据源

### Yahoo Finance

**网址**：https://finance.yahoo.com/

**数据类型**：
- ✅ 实时股价（延迟15分钟）
- ✅ 财务报表（利润表、资产负债表、现金流量表）
- ✅ 估值指标（PE、PB、PS、PEG等）
- ✅ 历史价格
- ✅ 财务比率（ROE、ROA、毛利率等）
- ✅ 股票基本信息
- ✅ 持股机构信息

**优点**：
- 完全免费
- 数据全面
- 界面友好
- API可用（yfinance）

**缺点**：
- 实时数据延迟15分钟
- 某些高级指标缺失
- 历史数据可能有限

**使用方式**：
```python
import yfinance as yf
stock = yf.Ticker("AAPL")
info = stock.info
financials = stock.financials
```

### SEC EDGAR

**网址**：https://www.sec.gov/edgar/

**数据类型**：
- ✅ 10-K（年报）
- ✅ 10-Q（季报）
- ✅ 8-K（重大事件）
- ✅ 13F（机构持仓）
- ✅ DEF 14A（委托书）
- ✅ S-1（招股说明书）

**优点**：
- 官方权威数据
- 最完整
- 完全免费

**缺点**：
- 格式复杂，需解析
- 查找较慢
- 无API（需爬虫）

**使用方式**：
- 直接访问SEC官网搜索
- 使用SEC API（有限）
- 使用第三方解析工具

### Finviz

**网址**：https://finviz.com/

**数据类型**：
- ✅ 实时股价
- ✅ 财务数据
- ✅ 估值指标
- ✅ 技术指标
- ✅ 新闻标题
- ✅ 内部交易

**优点**：
- 免费版功能齐全
- 筛选器强大
- 数据可视化好

**缺点**：
- 免费版有广告
- 高级功能需付费
- 实时数据延迟

**使用方式**：
- 网页直接查询
- 使用finviz库（非官方）

### Morningstar

**网址**：https://www.morningstar.com/

**数据类型**：
- ✅ 财务数据
- ✅ 估值指标
- ✅ 财务比率
- ✅ 星级评级
- ✅ 公允价值估算

**优点**：
- 数据质量高
- 分析工具专业
- 评级有参考价值

**缺点**：
- 高级功能需付费
- 免费版数据有限
- 无API

### Alpha Vantage

**网址**：https://www.alphavantage.co/

**数据类型**：
- ✅ 实时股价
- ✅ 历史价格
- ✅ 财务数据
- ✅ 技术指标

**优点**：
- 免费API可用
- 数据更新及时
- 支持技术指标

**缺点**：
- 免费版有请求限制
- 某些数据需付费

**使用方式**：
```python
import requests
url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=AAPL&apikey=YOUR_KEY"
response = requests.get(url)
data = response.json()
```

## 付费数据源

### Bloomberg Terminal

**数据类型**：
- 所有金融数据
- 实时新闻
- 分析师评级
- 机构持仓

**价格**：~$24,000/年

### FactSet

**数据类型**：
- 财务数据
- 分析师预期
- 机构持仓
- 公司事件

**价格**：~$12,000/年

### Refinitiv (formerly Thomson Reuters)

**数据类型**：
- 实时股价
- 新闻
- 分析师评级
- 财务数据

**价格**：~$15,000/年

## 分析师评级数据源

### TipRanks

**网址**：https://www.tipranks.com/

**数据类型**：
- ✅ 分析师评级
- ✅ 目标价
- ✅ 分析师排名
- ✅ 内部交易

**优点**：
- 免费版可用
- 分析师透明度高
- 有排名系统

**缺点**：
- 高级功能需付费
- 数据可能有延迟

### MarketBeat

**网址**：https://www.marketbeat.com/

**数据类型**：
- ✅ 分析师评级
- ✅ 目标价
- ✅ 评级变化
- ✅ 股息信息

**优点**：
- 免费版功能全
- 更新及时
- 有邮件提醒

**缺点**：
- 界面较简陋
- 无API

### Seeking Alpha

**网址**：https://seekingalpha.com/

**数据类型**：
- ✅ 分析师文章
- ✅ 评级
- ✅ 财务数据
- ✅ 讨论区

**优点**：
- 内容深度好
- 社区活跃
- 有原创分析

**缺点**：
- 高级功能需付费
- 质量参差不齐

## 机构持仓数据源

### SEC 13F Files

**网址**：https://www.sec.gov/edgar/search/

**数据类型**：
- ✅ 机构持仓详情
- ✅ 持仓变化
- ✅ 新建仓/清仓

**更新频率**：季度（45天后提交）

**优点**：
- 官方权威
- 完整详细
- 免费获取

**缺点**：
- 格式复杂
- 更新慢（季度）
- 需手动解析

### WhaleWisdom

**网址**：https://whalewisdom.com/

**数据类型**：
- ✅ 机构持仓聚合
- ✅ 持仓变化跟踪
- ✅ 聪明钱流向

**优点**：
- 数据整理好
- 有可视化
- 可追踪变化

**缺点**：
- 高级功能需付费
- 免费版限制多

## 新闻数据源

### Yahoo Finance News

**网址**：https://finance.yahoo.com/news/

**优点**：
- 免费
- 更新及时
- 来源广泛

### Bloomberg News

**网址**：https://www.bloomberg.com/news

**优点**：
- 权威性高
- 质量好
- 更新快

**缺点**：
- 高级文章需付费

### Reuters

**网址**：https://www.reuters.com/finance

**优点**：
- 权威性高
- 全球覆盖

## API工具

### yfinance (Python)

**安装**：
```bash
pip install yfinance
```

**使用示例**：
```python
import yfinance as yf

# 获取股票信息
ticker = yf.Ticker("AAPL")

# 基本信息
info = ticker.info

# 财务报表
financials = ticker.financials
balance_sheet = ticker.balance_sheet
cashflow = ticker.cashflow

# 历史价格
hist = ticker.history(period="1y")
```

### pandas_datareader (Python)

**安装**：
```bash
pip install pandas_datareader
```

**使用示例**：
```python
import pandas_datareader.data as web

# 获取股价数据
df = web.DataReader('AAPL', 'yahoo', start, end)
```

## MCP工具

本项目已配置的MCP工具：

### mcp__web-search-prime__webSearchPrime

**用途**：搜索最新美股新闻和财务数据

**使用场景**：
- 获取最新股价
- 搜索公司新闻
- 获取分析师评级

### mcp__web-reader__webReader

**用途**：读取网页内容，获取详细信息

**使用场景**：
- 读取SEC文件
- 读取公司财报
- 读取分析师报告

## 数据时效性

| 数据类型 | 更新频率 | 滞后时间 |
|---------|---------|---------|
| 股价 | 实时 | 0-15分钟 |
| 新闻 | 实时 | 0-1小时 |
| 财报 | 季度 | 45-60天 |
| 机构持仓（13F） | 季度 | 45天 |
| 分析师评级 | 不定期 | 0-7天 |

## 数据质量检查

使用任何数据源时，请注意：

1. **交叉验证**：多个来源对比关键数据
2. **时效性检查**：注意数据发布时间
3. **异常值检测**：明显异常的数据需验证
4. **数据完整性**：缺失数据标注明确
5. **来源标注**：每个数据标注来源和日期

## 推荐数据组合

### 免费方案
- Yahoo Finance（主要数据源）
- SEC EDGAR（财报）
- TipRanks（分析师评级）
- MarketBeat（补充）

### 付费方案
- Bloomberg Terminal（专业机构）
- FactSet（财务数据）
- Refinitiv（新闻和评级）
