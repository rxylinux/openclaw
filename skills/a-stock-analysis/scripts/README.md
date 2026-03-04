# A股分析脚本工具集

## 依赖安装

```bash
pip3 install requests akshare pandas numpy
```

## 环境配置

```bash
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

或设置环境变量：
```bash
export BOCHA_API_KEY=your_api_key_here
```

## 脚本列表

| 脚本 | 功能 | 用法 |
|------|------|------|
| `bocha_search.py` | 博查API搜索（基本信息、财务、新闻、行业） | `python3 bocha_search.py <代码> <名称> [--basic/--financial/--news/--industry]` |
| `fetch_stock_data.py` | AkShare数据获取（行情、财务报表、历史数据） | `python3 fetch_stock_data.py <代码> [选项]` |
| `get_financial_data.py` | 财务报表数据获取（利润表、资产负债表、现金流） | `python3 get_financial_data.py <代码>` |
| `calculate_ratios.py` | 财务比率计算（ROE、毛利率、PE等） | `python3 calculate_ratios.py <代码>` |
| `setup_bocha_key.sh` | 博查API密钥配置 | `bash setup_bocha_key.sh` |

## 详细指南

- 博查API使用指南：[references/bocha-api-guide.md](../references/bocha-api-guide.md)
- 秘塔MCP集成指南：[references/metaso-mcp-guide.md](../references/metaso-mcp-guide.md)
- 数据源使用指南：[references/data-sources-guide.md](../references/data-sources-guide.md)
