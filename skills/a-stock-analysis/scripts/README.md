# A股数据获取脚本使用指南（优化版）

## 概述

`fetch_stock_data.py` 是一个无需百度 API Key 的多数据源股票数据获取脚本，使用 AkShare 作为主要数据源。

### 🆕 优化版特性

- ✅ **自动重试机制** - 网络请求失败时自动重试（最多3次）
- ✅ **智能缓存** - 5分钟内重复查询直接返回缓存，避免频繁请求
- ✅ **列名自动检测** - 自动识别 AkShare 返回的列名，提高兼容性
- ✅ **增强错误处理** - 详细的错误信息和调试日志
- ✅ **更多财务数据** - 新增资产负债表、现金流量表
- ✅ **类型提示** - 完整的类型注解，提高代码质量
- ✅ **灵活配置** - 支持命令行参数和配置常量

## 依赖安装

### 1. 安装 AkShare

```bash
pip3 install akshare
```

或者使用国内镜像：

```bash
pip3 install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装可选依赖

如果需要获取雪球数据（非 MCP 环境）：

```bash
pip3 install requests beautifulsoup4
```

### 3. 验证安装

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

# 获取历史行情
python3 fetch_stock_data.py 002156 --history

# 禁用缓存
python3 fetch_stock_data.py 002156 --no-cache
```

### 高级用法

```bash
# 获取指定时间段的历史行情
python3 fetch_stock_data.py 002156 --history --start 20240101 --end 20241231

# 获取周线数据
python3 fetch_stock_data.py 002156 --history --period weekly

# 获取月线数据
python3 fetch_stock_data.py 002156 --history --period monthly

# 获取行业数据
python3 fetch_stock_data.py --industry

# 获取指定行业数据
python3 fetch_stock_data.py --industry --industry-name 半导体

# 获取排名数据
python3 fetch_stock_data.py --rank

# 获取成交额排名
python3 fetch_stock_data.py --rank --rank-type 成交额

# 不包含雪球数据（加快速度）
python3 fetch_stock_data.py 002156 --no-xueqiu
```

## 数据源说明

| 数据源 | 接口 | 数据类型 | 状态 |
|--------|------|----------|------|
| **AkShare** | stock_individual_info_em | 基本信息 | ✅ 免费 |
| **AkShare** | stock_zh_a_spot | 实时行情 | ✅ 免费 |
| **AkShare** | stock_financial_analysis | 财务分析 | ✅ 免费 |
| **AkShare** | stock_profit_sheet_by_reportly | 利润表 | ✅ 免费 |
| **AkShare** | stock_balance_sheet_by_reportly | 资产负债表 | ✅ 免费 |
| **AkShare** | stock_cash_flow_sheet_by_reportly | 现金流量表 | ✅ 免费 |
| **AkShare** | stock_zh_a_hist | 历史行情 | ✅ 免费 |
| **AkShare** | stock_board_industry_name_em | 行业板块 | ✅ 免费 |
| **雪球网** | Web scraping | 社区观点 | ⚠️ 需要额外依赖 |

## 输出格式

### 基本信息

```json
{
  "source": "AkShare",
  "fetch_time": "2026-02-23 10:30:00",
  "data": {
    "股票简称": "通富微电",
    "公司名称": "通富微电子股份有限公司",
    ...
  }
}
```

### 实时行情

```json
{
  "source": "AkShare",
  "fetch_time": "2026-02-23 10:30:00",
  "data": {
    "代码": "002156",
    "名称": "通富微电",
    "最新价": 22.58,
    "涨跌幅": -1.83,
    ...
  }
}
```

### 财务数据

```json
{
  "source": "AkShare",
  "fetch_time": "2026-02-23 10:30:00",
  "data": {
    "financial_analysis": {...},
    "profit_sheet": {...},
    "balance_sheet": {...},
    "cash_flow_sheet": {...}
  }
}
```

### 历史行情

```json
{
  "source": "AkShare",
  "fetch_time": "2026-02-23 10:30:00",
  "period": "daily",
  "adjust": "qfq",
  "count": 10,
  "data": [
    {
      "日期": "2026-02-22",
      "开盘": 22.50,
      "收盘": 22.58,
      ...
    }
  ]
}
```

## 配置选项

脚本中的 `Config` 类包含可配置的常量：

```python
class Config:
    # 网络请求配置
    MAX_RETRIES = 3           # 最大重试次数
    RETRY_DELAY = 2           # 重试延迟（秒）
    REQUEST_TIMEOUT = 30      # 请求超时（秒）

    # 数据缓存配置
    CACHE_TTL = 300           # 缓存有效期（秒）- 5分钟
    ENABLE_CACHE = True       # 是否启用缓存

    # 数据输出配置
    MAX_HISTORY_DAYS = 10     # 历史数据最多返回天数
    JSON_INDENT = 2           # JSON 缩进
```

可根据需要修改这些值。

## 性能优化

### 1. 缓存机制

脚本内置了智能缓存，相同数据在 5 分钟内直接返回缓存，避免重复请求：

```bash
# 第一次请求：从网络获取
python3 fetch_stock_data.py 002156 --quote

# 5分钟内再次请求：从缓存返回（速度快）
python3 fetch_stock_data.py 002156 --quote

# 禁用缓存：每次都从网络获取
python3 fetch_stock_data.py 002156 --quote --no-cache
```

### 2. 选择性获取

只获取需要的数据类型，减少不必要的请求：

```bash
# ❌ 不推荐：获取所有数据（慢）
python3 fetch_stock_data.py 002156

# ✅ 推荐：只获取需要的（快）
python3 fetch_stock_data.py 002156 --quote
```

### 3. 并行获取

如果需要获取多只股票，可以使用并行处理：

```bash
# 使用 GNU Parallel
parallel python3 fetch_stock_data.py {} --quote ::: 002156 600584 002185
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
- 脚本会自动重试 3 次
- 耐心等待重试完成

### 问题3：数据为空

**错误信息**: `未找到该股票数据`

**解决方案**:
- 确认股票代码正确（6位数字）
- 检查是否为A股代码
- 查看调试信息中的列名

### 问题4：列名不匹配

**错误信息**: `[调试] 实时行情列名: [...]`

**解决方案**:
- 脚本会自动检测列名
- 查看调试输出中的实际列名
- 如果仍有问题，可能是 AkShare 接口变化

### 问题5：雪球数据获取失败

**错误信息**: `雪球数据获取失败` 或 `请在 MCP 环境中运行`

**解决方案**:
- 安装可选依赖：`pip3 install requests beautifulsoup4`
- 或者在 MCP 环境中运行脚本
- 或者使用 `--no-xueqiu` 跳过雪球数据

## 最佳实践

### 1. 定时更新

```bash
# 每天收盘后获取数据
0 15:30 * * 1-5 python3 /path/to/fetch_stock_data.py 002156
```

### 2. 批量获取

```bash
# 获取多只股票数据
for code in 002156 600584 002185; do
    python3 fetch_stock_data.py $code --quote
done
```

### 3. 数据存储

```bash
# 保存到文件
python3 fetch_stock_data.py 002156 > data_002156.json
```

### 4. 组合使用

```bash
# 获取行情后，获取历史数据
python3 fetch_stock_data.py 002156 --quote --history
```

## 扩展功能

脚本采用模块化设计，可以轻松扩展以支持更多数据源：

```python
def get_tushare_data(self):
    """使用 Tushare 获取数据"""
    import tushare as ts
    ts.set_token('your_token')
    pro = ts.pro_api()
    return pro.stock_basic(ts_code=self.standard_code)

def get_baostock_data(self):
    """使用 Baostock 获取数据"""
    import baostock as bs
    lg = bs.login()
    # ... 获取数据
    bs.logout()
```

## 更新日志

- **2026-02-23 v2.0**: 优化版
  - 添加自动重试机制
  - 添加智能缓存
  - 添加列名自动检测
  - 添加更多财务数据
  - 改进错误处理
  - 添加类型提示
- **2026-02-23 v1.0**: 初始版本，支持 AkShare 和 Web Reader

## 技术支持

如遇问题，请检查：
1. AkShare 版本是否最新
2. 网络连接是否正常
3. 股票代码是否正确
4. 查看调试信息
