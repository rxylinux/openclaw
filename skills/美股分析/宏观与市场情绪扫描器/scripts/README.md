# 宏观分析脚本

本目录包含宏观与市场情绪分析相关的工具脚本。

## 脚本列表

### get_cpi.py

获取CPI通胀数据的脚本。

**功能**：
- 获取最新CPI报告
- 对比整体CPI和核心CPI
- 分析通胀趋势

**使用方式**：
```bash
python3 scripts/get_cpi.py
```

### fed_watch.py

从CME获取美联储降息概率的脚本。

**功能**：
- 获取下次FOMC会议的降息概率
- 获取未来12个月的利率预期
- 对比历史概率变化

**使用方式**：
```bash
python3 scripts/fed_watch.py
```

### get_pmi.py

获取PMI数据的脚本。

**功能**：
- 获取制造业PMI
- 获取服务业PMI
- 判断扩张/收缩状态

**使用方式**：
```bash
python3 scripts/get_pmi.py
```

### market_breadth.py

计算市场广度指标的脚本。

**功能**：
- 涨跌家数比率
- 创新高/新低统计
- 超过200日均线比例

**使用方式**：
```bash
python3 scripts/market_breadth.py
```

### sector_rotation.py

分析板块轮动的脚本。

**功能**：
- 各板块表现对比
- 资金流向分析
- 领涨/领跌板块识别

**使用方式**：
```bash
python3 scripts/sector_rotation.py --period week
```

### vix_analysis.py

分析VIX恐慌指数的脚本。

**功能**：
- VIX当前水平
- VIX历史分位数
- 隐含波动率vs实际波动率

**使用方式**：
```bash
python3 scripts/vix_analysis.py
```

### put_call_ratio.py

获取Put/Call比率的脚本。

**功能**：
- 整体P/C比率
- 权益P/C比率
- 历史分位数

**使用方式**：
```bash
python3 scripts/put_call_ratio.py
```

### fund_flows.py

获取ETF资金流向的脚本。

**功能**：
- 主要ETF资金流入/流出
- 板块ETF资金流向
- 周度/月度资金流

**使用方式**：
```bash
python3 scripts/fund_flows.py --period week
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# FRED API Key (用于获取经济数据)
FRED_API_KEY=your_key_here

# CME API Key (用于获取FedWatch数据)
CME_API_KEY=your_key_here

# Bloomberg API Key (用于获取市场数据)
BLOOMBERG_API_KEY=your_key_here

# Reuters API Key (用于获取新闻)
REUTERS_API_KEY=your_key_here
```

## 依赖安装

```bash
pip install yfinance pandas numpy requests python-dotenv fredapi
```

## 注意事项

1. 经济数据发布时间不同，注意更新频率
2. 市场数据需要实时更新
3. 预期数据来自调查，存在误差
4. 地缘政治事件变化迅速，需要及时跟踪
