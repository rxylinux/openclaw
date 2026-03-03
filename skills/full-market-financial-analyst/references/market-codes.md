# 市场代码手册

## 股票代码识别规则

### 自动识别逻辑

```
用户输入 → 正则匹配 → 市场判断
```

### 识别规则

#### A股 识别

**上海证券交易所 (SSE)**
- 6开头: `600xxx`, `601xxx`, `603xxx`, `605xxx`
- 688开头: `688xxx` (科创板)
- 后缀: `.SH` 或 `.SS`

示例:
- `600519` - 贵州茅台
- `601318` - 中国平安
- `688981` - 中芯国际

**深圳证券交易所 (SZSE)**
- 000xxx: `000xxx` (主板)
- 001xxx: `001xxx` (主板)
- 002xxx: `002xxx` (中小板)
- 300xxx: `300xxx` (创业板)
- 后缀: `.SZ`

示例:
- `000858` - 五粮液
- `002594` - 比亚迪
- `300750` - 宁德时代

#### 美股 识别

**代码格式**
- 1-5个字母
- 无数字
- 无后缀（或 `.O`, `.N`, `.PK`）

示例:
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corporation
- `TSLA` - Tesla, Inc.
- `NVDA` - NVIDIA Corporation

#### 港股 识别

**代码格式**
- 4-5位数字
- 后缀: `.HK`

示例:
- `0001.HK` - 长和
- `0700.HK` - 腾讯控股
- `9988.HK` - 阿里巴巴
- `3690.HK` - 美团

---

## 常用股票代码速查

### A股 蓝筹股

| 代码 | 名称 | 交易所 | 行业 |
|------|------|--------|------|
| 600519.SH | 贵州茅台 | 上交所 | 食品饮料 |
| 601318.SH | 中国平安 | 上交所 | 金融 |
| 600036.SH | 招商银行 | 上交所 | 金融 |
| 000858.SZ | 五粮液 | 深交所 | 食品饮料 |
| 002594.SZ | 比亚迪 | 深交所 | 汽车 |
| 300750.SZ | 宁德时代 | 深交所 | 新能源 |
| 600900.SH | 长江电力 | 上交所 | 公用事业 |
| 601888.SH | 中国中免 | 上交所 | 消费 |
| 600276.SH | 恒瑞医药 | 上交所 | 医药 |

### A股 科技股

| 代码 | 名称 | 交易所 | 行业 |
|------|------|--------|------|
| 688981.SH | 中芯国际 | 科创板 | 半导体 |
| 688111.SH | 金山办公 | 科创板 | 软件 |
| 300059.SZ | 东方财富 | 创业板 | 金融科技 |
| 002415.SZ | 海康威视 | 深交所 | 安防 |
| 002230.SZ | 科大讯飞 | 深交所 | AI |

### 美股 科技巨头

| 代码 | 名称 | 交易所 | 市值 |
|------|------|--------|------|
| AAPL | Apple Inc. | NASDAQ | 大型 |
| MSFT | Microsoft Corporation | NASDAQ | 大型 |
| GOOGL | Alphabet Inc. | NASDAQ | 大型 |
| AMZN | Amazon.com, Inc. | NASDAQ | 大型 |
| META | Meta Platforms, Inc. | NASDAQ | 大型 |
| NVDA | NVIDIA Corporation | NASDAQ | 大型 |
| TSLA | Tesla, Inc. | NASDAQ | 大型 |

### 美股 芯片股

| 代码 | 名称 | 交易所 | 细分 |
|------|------|--------|------|
| NVDA | NVIDIA | NASDAQ | GPU |
| AMD | Advanced Micro Devices | NASDAQ | CPU/GPU |
| INTC | Intel Corporation | NASDAQ | CPU |
| TSM | TSMC | NYSE | 代工 |
| ASML | ASML Holding | NASDAQ | 光刻机 |
| MRVL | Marvell Technology | NASDAQ | 芯片 |

### 美股 云计算

| 代码 | 名称 | 交易所 | 业务 |
|------|------|--------|------|
| AMZN | AWS | NASDAQ | IaaS |
| MSFT | Azure | NASDAQ | IaaS |
| GOOGL | Google Cloud | NASDAQ | IaaS |
| CRM | Salesforce | NYSE | SaaS |
| SNOW | Snowflake | NYSE | 数据云 |
| NET | Cloudflare | NYSE | CDN |

### 美股 金融

| 代码 | 名称 | 交易所 | 类型 |
|------|------|--------|------|
| JPM | JPMorgan Chase | NYSE | 银行 |
| BAC | Bank of America | NYSE | 银行 |
| WFC | Wells Fargo | NYSE | 银行 |
| GS | Goldman Sachs | NYSE | 投行 |
| MS | Morgan Stanley | NYSE | 投行 |
| BLK | BlackRock | NYSE | 资产管理 |
| V | Visa | NYSE | 支付 |

### 港股 蓝筹

| 代码 | 名称 | 行业 |
|------|------|------|
| 0001.HK | 长和 | 综合企业 |
| 0005.HK | 汇丰控股 | 银行 |
| 0700.HK | 腾讯控股 | 科技 |
| 9988.HK | 阿里巴巴 | 电商 |
| 0941.HK | 中国移动 | 电信 |
| 1299.HK | 友邦保险 | 保险 |
| 2318.HK | 中国平安 | 保险 |
| 1398.HK | 工商银行 | 银行 |

### 港股 科技

| 代码 | 名称 | 业务 |
|------|------|------|
| 0700.HK | 腾讯控股 | 社交/游戏 |
| 9988.HK | 阿里巴巴 | 电商/云 |
| 9618.HK | 京东集团 | 电商 |
| 3690.HK | 美团 | 本地服务 |
| 1024.HK | 快手 | 短视频 |
| 9866.HK | 小米集团 | 智能手机 |
| 2010.HK | SMIC | 半导体 |

---

## 指数代码

### A股 指数

| 代码 | 名称 | 说明 |
|------|------|------|
| 000001.SH | 上证指数 | 沪市大盘 |
| 399001.SZ | 深证成指 | 深市大盘 |
| 399006.SZ | 创业板指 | 创业板龙头 |
| 000688.SH | 科创50 | 科创板龙头 |
| 000300.SH | 沪深300 | A股核心 |
| 000905.SH | 中证500 | 中盘股 |
| 000852.SH | 中证1000 | 小盘股 |

### 美股 指数

| 代码 | 名称 | 说明 |
|------|------|------|
| ^GSPC | S&P 500 | 标普500 |
| ^IXIC | NASDAQ | 纳斯达克 |
| ^DJI | Dow Jones | 道琼斯 |
| ^RUT | Russell 2000 | 小盘股 |
| ^VIX | VIX | 恐慌指数 |

### 港股 指数

| 代码 | 名称 | 说明 |
|------|------|------|
| ^HSI | 恒生指数 | 港股大盘 |
| ^HSCE | 恒生国企 | H股指数 |
| ^HSTECH | 恒生科技 | 科技股 |
| ^HSCCI | 恒生中国 | 中资股 |

---

## ETF 代码

### A股 ETF

| 代码 | 名称 | 跟踪标的 |
|------|------|----------|
| 510050.SH | 50ETF | 上证50 |
| 510300.SH | 300ETF | 沪深300 |
| 159915.SZ | 创业板ETF | 创业板指 |
| 512760.SH | 芯片ETF | 芯片指数 |
| 515880.SH | 通信ETF | 通信指数 |

### 美股 ETF

| 代码 | 名称 | 跟踪标的 |
|------|------|----------|
| SPY | SPDR S&P 500 | S&P 500 |
| QQQ | Invesco QQQ | NASDAQ-100 |
| VOO | Vanguard S&P 500 | S&P 500 |
| VTI | Vanguard Total Stock Market | 全市场 |
| IWM | iShares Russell 2000 | 小盘股 |
| XLK | Technology Select Sector SPDR | 科技板块 |
| XLV | Health Care Select Sector SPDR | 医疗板块 |
| XLF | Financial Select Sector SPDR | 金融板块 |

---

## 代码格式转换

### 后缀标准化

| 市场 | Yahoo Finance | Tushare | 通用 |
|------|--------------|----------|------|
| A股 | 600519.SS | 600519.SH | 600519 |
| 美股 | AAPL | - | AAPL |
| 港股 | 0700.HK | - | 0700.HK |

### 转换规则

```python
def normalize_symbol(symbol):
    # 去除空格
    symbol = symbol.strip().upper()

    # A股 - 统一为 .SH 或 .SZ
    if re.match(r'^60\d{4}$', symbol):
        return f"{symbol}.SH"  # 上交所
    elif re.match(r'^(00|30)\d{4}$', symbol):
        return f"{symbol}.SZ"  # 深交所

    # 美股 - 直接返回
    elif re.match(r'^[A-Z]{1,5}$', symbol):
        return symbol

    # 港股 - 添加 .HK
    elif re.match(r'^\d{4,5}$', symbol):
        return f"{symbol}.HK"

    # 已有后缀 - 保持不变
    elif '.' in symbol:
        return symbol

    else:
        return symbol
```

---

## 代码验证

### 合法性检查

**A股:**
- 上交所: `6\d{5}`
- 科创板: `688\d{3}`
- 深主板: `00\d{4}` 或 `001\d{3}`
- 中小板: `002\d{4}`
- 创业板: `300\d{4}`

**美股:**
- 格式: `[A-Z]{1,5}`
- 不能全是数字

**港股:**
- 格式: `\d{4,5}`

---

## 代码查询

### 在线查询

- A股: 同花顺 (10jqka.com.cn), 东方财富
- 美股: Yahoo Finance, NASDAQ, NYSE
- 港股: 港交所, AAStocks

### API 查询

- A股: Tushare, AkShare
- 美股: yfinance, alpha_vantage
- 港股: yfinance
