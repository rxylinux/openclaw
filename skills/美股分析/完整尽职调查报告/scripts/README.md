# 尽职调查脚本

本目录包含尽职调查分析相关的工具脚本。

## 脚本列表

### fetch_sec_filings.py

获取SEC文件的脚本。

**功能**：
- 下载最新10-K/10-Q
- 解析财务数据
- 提取关键指标

**使用方式**：
```bash
python3 scripts/fetch_sec_filings.py AAPL
```

### calculate_wacc.py

计算WACC（加权平均资本成本）的脚本。

**功能**：
- 获取无风险利率
- 计算股权成本（CAPM模型）
- 计算债务成本
- 输出WACC

**使用方式**：
```bash
python3 scripts/calculate_wacc.py AAPL
```

### dcf_model.py

DCF估值模型脚本。

**功能**：
- 构建现金流预测
- 计算企业价值
- 输出目标价

**使用方式**：
```bash
python3 scripts/dcf_model.py AAPL --growth_rate 10 --terminal_growth 2.5
```

### comparable_analysis.py

可比公司分析脚本。

**功能**：
- 获取同行公司数据
- 计算估值倍数
- 生成估值表

**使用方式**：
```bash
python3 scripts/comparable_analysis.py AAPL --peers MSFT GOOGL META
```

### short_interest.py

获取做空比例的脚本。

**功能**：
- 获取当前做空比例
- 获取空头利息天数
- 历史趋势分析

**使用方式**：
```bash
python3 scripts/short_interest.py AAPL
```

### insider_trading.py

获取内部人交易数据的脚本。

**功能**：
- 获取最新Form 4文件
- 分析内部人买卖趋势
- 生成交易汇总表

**使用方式**：
```bash
python3 scripts/insider_trading.py AAPL --months 6
```

### analyst_expectations.py

获取分析师预期的脚本。

**功能**：
- 获取一致预期EPS/收入
- 获取评级分布
- 对比管理层指引

**使用方式**：
```bash
python3 scripts/analyst_expectations.py AAPL
```

### estimate_report.py

生成完整报告的辅助脚本。

**功能**：
- 整合所有分析模块
- 生成结构化报告
- 导出为Markdown/PDF

**使用方式**：
```bash
python3 scripts/generate_report.py AAPL --output report.md
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# SEC API Key (用于获取SEC文件)
SEC_API_KEY=your_key_here

# Bloomberg API Key (用于获取市场数据)
BLOOMBERG_API_KEY=your_key_here

# FactSet API Key (用于获取分析师预期)
FACTSET_API_KEY=your_key_here

# Alpha Vantage API Key (用于获取基础数据)
ALPHAVANTAGE_API_KEY=your_key_here

# Financial Modeling Prep API Key
FMP_API_KEY=your_key_here
```

## 依赖安装

```bash
pip install yfinance pandas numpy requests python-dotenv sec-edgar-downloader
```

## 注意事项

1. SEC文件可能非常大，需要时间下载和解析
2. 分析师预期数据可能需要付费API
3. DCF模型对假设敏感，需谨慎使用
4. 可比公司选择需要行业知识
5. 内部人交易数据有延迟（通常2天）
6. 做空比例数据更新频率因交易所而异
