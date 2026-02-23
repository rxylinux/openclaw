# A股数据获取脚本使用指南

## 概述

`fetch_stock_data.py` 是一个无需百度 API Key 的多数据源股票数据获取脚本，使用 AkShare 和 Web Reader 作为数据源。

## 依赖安装

### 1. 安装 AkShare

```bash
pip3 install akshare
```

或者使用国内镜像：

```bash
pip3 install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 验证安装

```bash
python3 -c "import akshare as ak; print(ak.__version__)"
```

## 使用方法

### 基本用法

```bash
# 进入脚本目录
cd skills/a-stock-analysis/scripts

# 获取所有数据
python3 fetch_stock_data.py 002156

# 仅获取基本信息
python3 fetch_stock_data.py 002156 --basic

# 仅获取实时行情
python3 fetch_stock_data.py 002156 --quote

# 仅获取财务数据
python3 fetch_stock_data.py 002156 --financial

# 仅获取雪球数据
python3 fetch_stock_data.py 002156 --xueqiu
```

### 数据源说明

| 数据源 | 接口 | 数据类型 | 状态 |
|--------|------|----------|------|
| **AkShare** | stock_individual_info_em | 基本信息 | ✅ 免费 |
| **AkShare** | stock_zh_a_spot | 实时行情 | ✅ 免费 |
| **AkShare** | stock_financial_analysis | 财务分析 | ✅ 免费 |
| **AkShare** | stock_profit_sheet_by_reportly | 利润表 | ✅ 免费 |
| **AkShare** | stock_zh_a_hist | 历史行情 | ✅ 免费 |
| **Web Reader** | xueqiu.com | 社区观点 | ✅ 免费 |

## 输出示例

```json
{
  "stock_code": "002156",
  "basic_info": {
    "source": "AkShare",
    "data": {
      "股票简称": "通富微电",
      "公司名称": "通富微电子股份有限公司",
      ...
    }
  },
  "realtime_quote": {
    "source": "AkShare",
    "data": {
      "代码": "002156",
      "名称": "通富微电",
      "最新价": 22.58,
      "涨跌幅": -1.83,
      ...
    }
  },
  "financial_data": {
    "source": "AkShare",
    "data": {
      "financial_analysis": {...},
      "profit_sheet": {...}
    }
  },
  "xueqiu_data": {
    "source": "Xueqiu",
    "url": "https://xueqiu.com/S/SZ002156",
    "data": "..."
  }
}
```

## 与百度搜索的对比

| 特性 | 百度搜索 | AkShare方案 |
|------|----------|-------------|
| **成本** | 需要API密钥 | 完全免费 |
| **稳定性** | 依赖百度服务 | 依赖开源库 |
| **数据源** | 15个网站 | 东财、新浪等 |
| **实时性** | 高 | 中（延迟15-20秒） |
| **覆盖范围** | 新闻、研报、行情 | 行情、财务为主 |
| **配置难度** | 需要申请密钥 | pip安装即用 |

## 最佳实践

### 1. 组合使用

```bash
# 使用 AkShare 获取结构化数据
python3 fetch_stock_data.py 002156 --quote

# 使用 Web Reader 获取社区观点
python3 fetch_stock_data.py 002156 --xueqiu
```

### 2. 定时更新

```bash
# 每天收盘后获取数据
0 15:30 * * 1-5 python3 /path/to/fetch_stock_data.py 002156
```

### 3. 批量获取

```bash
# 获取多只股票数据
for code in 002156 600584 002185; do
    python3 fetch_stock_data.py $code --quote
done
```

## 故障排除

### 问题1：未安装 AkShare

**错误信息**: `未安装 AkShare`

**解决方案**:
```bash
pip3 install akshare
```

### 问题2：网络连接问题

**错误信息**: `Connection timeout` 或 `网络错误`

**解决方案**:
- 检查网络连接
- 尝试使用代理
- 多次重试

### 问题3：数据为空

**错误信息**: `未找到该股票数据`

**解决方案**:
- 确认股票代码正确（6位数字）
- 检查是否为A股代码
- 尝试使用其他数据源

## 扩展功能

脚本可以轻松扩展以支持更多数据源：

```python
def get_tushare_data(self):
    """使用 Tushare 获取数据"""
    import tushare as ts
    ts.set_token('your_token')
    pro = ts.pro_api()
    return pro.stock_basic(ts_code=self.stock_code)

def get_baostock_data(self):
    """使用 Baostock 获取数据"""
    import baostock as bs
    lg = bs.login()
    # ... 获取数据
    bs.logout()
```

## 更新日志

- 2025-02-23: 初始版本，支持 AkShare 和 Web Reader
- 待定: 添加更多数据源支持
