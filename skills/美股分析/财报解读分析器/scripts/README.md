# 财报解读分析脚本

本目录包含财报解读分析相关的工具脚本。

## 脚本列表

### fetch_earnings.py

获取财报数据和预期对比的脚本。

**功能**：
- 获取最新财报数据
- 获取分析师预期
- 计算超预期/不及预期

**使用方式**：
```bash
python3 scripts/fetch_earnings.py AAPL
```

### get_transcript.py

获取财报会议记录的脚本。

**功能**：
- 获取会议文字记录
- 提取CEO/CFO发言
- 分析关键词变化

**使用方式**：
```bash
python3 scripts/get_transcript.py AAPL
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
pip install yfinance requests beautifulsoup4 python-dotenv
```

## 注意事项

1. 会议记录可能有延迟（1-2天）
2. 如未发布，使用新闻稿替代
3. 免费API有请求限制
