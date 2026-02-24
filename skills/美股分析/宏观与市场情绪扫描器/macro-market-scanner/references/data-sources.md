# 宏观数据源说明

## 官方经济数据源

### 美联储（Federal Reserve）

**网址：** federalreserve.gov

**提供数据：**
- 联邦基金利率
- FOMC 会议决议
- 会议纪要
- 经济预测（SEP）
- 点阵图

**更新频率：**
- FOMC 决议：约 6 周 1 次
- 会议纪要：决议后 3 周
- 经济预测：季度

**重要性：** ⭐⭐⭐⭐⭐

### BLS（劳工统计局）

**网址：** bls.gov

**提供数据：**
- CPI（消费者价格指数）
- 非农就业报告
- 失业率
- 平均时薪
- 劳动参与率

**更新频率：**
- CPI：每月
- 就业报告：每月（第一个周五）
- 失业率：每月

**重要性：** ⭐⭐⭐⭐⭐

### BEA（经济分析局）

**网址：** bea.gov

**提供数据：**
- GDP（国内生产总值）
- PCE（个人消费支出价格指数）
| 个人收入和支出

**更新频率：**
- GDP：每季度（首估、修正、终值）
- PCE：每月

**重要性：** ⭐⭐⭐⭐⭐

---

## 市场数据源

### Yahoo Finance

**网址：** finance.yahoo.com

**提供数据：**
- 主要指数（标普 500、纳斯达克、道琼斯）
- VIX
- 期权数据
- ETF 数据
| 个股数据

**更新频率：** 实时（延迟 15 分钟）

**可靠性：** ⭐⭐⭐⭐

**优点：** 免费，数据全面

### CBOE（芝加哥期权交易所）

**网址：** cboe.com

**提供数据：**
- VIX 指数
- Put/Call Ratio
| 期权成交量

**更新频率：** 每日

### CME FedWatch Tool

**网址：** cmegroup.com

**提供数据：**
- 美联储利率预期概率
- 基于联邦基金期货

**更新频率：** 实时

**⚠️ 注意：** 这是市场预期，不是美联储官方预测

---

## 消费者与商业调查

### 密歇根大学

**网址：** uma.soe.umich.edu

**提供数据：**
- 消费者信心指数
- 消费者预期指数

**更新频率：** 每月（两次：初值和终值）

### Conference Board

**网址：** conference-board.org

**提供数据：**
- 消费者信心指数
- 领先经济指数（LEI）

**更新频率：** 每月

### ISM（供应管理协会）

**网址：** ism.com

**提供数据：**
- 制造业 PMI
- 服务业 PMI

**更新频率：** 每月

---

## 债券与利率数据

### FRED（美联储经济数据）

**网址：** fred.stlouisfed.org

**提供数据：**
- 国债收益率（各期限）
- 收益率曲线
- 经济指标

**更新频率：** 每日

**可靠性：** ⭐⭐⭐⭐⭐

### 美国财政部

**网址：** treasury.gov

**提供数据：**
- 国债收益率曲线
| 利率数据

**更新频率：** 每日

---

## ETF 与资金流向

### ETF 发行人网站

**Vanguard：** vanguard.com
**iShares：** ishares.com
**SPDR：** ssga.com
**Invesco：** invesco.com

**提供数据：**
- ETF 资金流向
- 持仓明细
- 费用率

### Morningstar

**网址：** morningstar.com

**提供数据：**
- 基金评级
| 资金流向
- 持仓分析

---

## 机构数据

### SEC EDGAR

**网址：** sec.gov/edgar

**提供数据：**
- 13F 持仓报告
- 10-K/10-Q 财报
| 8-K 重大事件

**更新频率：**
- 13F：季度（45 天延迟）
- 财报：季度/年度

### Bloomberg / FactSet / Reuters

**提供数据：**
- 分析师评级
- 机构资金流向
- 市场广度数据

**可靠性：** ⭐⭐⭐⭐⭐

**缺点：** 昂贵，专业级

---

## 市场广度数据

### NYSE / Nasdaq

**网址：**
- nyse.com
- nasdaq.com

**提供数据：**
- 涨跌家数
- 新高新低
| 市场广度指标

### StockCharts.com

**网址：** stockcharts.com

**提供数据：**
- 高于均线股票比例
- 涨跌线
| 市场广度图表

---

## 地缘政治数据

### Eurasia Group

**网址：** eurasigroupgroup.com

**提供数据：**
- 全球政治风险指数
| 国家风险评级

### 各种新闻机构

**来源：**
- 路透社（Reuters）
- 彭博社（Bloomberg）
- 华尔街日报（WSJ）
| 金融时报（FT）

---

## 经济日历

### 经济数据日历网站

**网址：**
- investing.com/economic-calendar
- tradingeconomics.com/calendar

**提供：**
- 即将发布的经济数据
| 市场预期
| 历史数据

---

## 数据类型对应关系

| 数据类型 | 首选数据源 | 备选数据源 |
|----------|------------|------------|
| 美联储利率 | federalreserve.gov | Bloomberg |
| CPI | bls.gov | Trading Economics |
| 就业数据 | bls.gov | Yahoo Finance |
| GDP | bea.gov | FRED |
| PCE | bea.gov | Bloomberg |
| 消费者信心 | 密歇根大学, Conference Board | Bloomberg |
| PMI | ism.com | Trading Economics |
| 股票指数 | Yahoo Finance | Bloomberg |
| VIX | cboe.com | Yahoo Finance |
| Put/Call Ratio | cboe.com | 各大交易平台 |
| ETF 资金流 | ETF 发行人 | Morningstar |
| 机构持仓 | SEC EDGAR | Bloomberg |
| 市场广度 | NYSE/Nasdaq | StockCharts |
| 国债收益率 | FRED | treasury.gov |
| 地缘政治 | 新闻机构 | Eurasia Group |

---

## 数据新鲜度

| 数据类型 | 更新频率 | 延迟 |
|----------|----------|------|
| 指数价格 | 实时 | 15 分钟 |
| VIX | 实时 | 实时 |
| FedWatch 概率 | 实时 | 实时 |
| 债券收益率 | 每日 | 当日 |
| PMI | 每月 | 当月 |
| CPI | 每月 | 当月 |
| 就业报告 | 每月 | 当月 |
| GDP | 每季度 | 当季 |
| 13F 持仓 | 每季度 | 45 天 |

---

## 免费数据源

| 数据源 | 覆盖范围 |
|--------|----------|
| Yahoo Finance | 股票、指数、期权 |
| FRED | 宏观经济、债券 |
| Investing.com | 经济日历、市场数据 |
| Trading Economics | 全球经济数据 |
| ETF 发行人网站 | ETF 专属数据 |
| SEC EDGAR | 官方公司文件 |

---

## 付费数据源

| 数据源 | 特点 |
|--------|------|
| Bloomberg Terminal | 专业级，全球覆盖 |
| FactSet | 机构级数据 |
| Refinitiv (路透) | 全球新闻和数据 |
| S&P Capital IQ | 深度公司数据 |

---

## 数据验证

### 交叉验证原则

1. **关键数据验证：** 从多个来源验证
2. **官方数据优先：** 优先使用政府/央行数据
3. **检查时间戳：** 确认数据发布日期
4. **注意修订：** 经济数据可能后续修订

### 常见数据差异

**原因：**
- 季节性调整方法不同
- 计算方法略有差异
- 发布时间不同（日终 vs 实时）

---

## 注意事项

1. **数据来源标注：** 每个数据点必须注明来源和日期
2. **预期 vs 实际：** 明确区分市场预期和实际数据
3. **数据修订：** 经济数据可能修订，注明版本
4. **时效性：** 宏观数据通常有 1 个月延迟
5. **预测标识：** 明确标识哪些是预测，哪些是已确认数据
