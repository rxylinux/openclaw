# A股财务数据获取指南

## 📊 现状总结

### ✅ 可获取的数据（通过 AkShare）

| 数据类型 | 接口 | 状态 | 示例 |
|----------|------|------|------|
| 基本信息 | `stock_individual_info_em` | ✅ 可用 | 股票代码、名称、行业 |
| 实时行情 | `stock_zh_a_spot_em` | ✅ 可用 | 股价、涨跌幅、成交量 |
| 历史行情 | `stock_zh_a_hist` | ✅ 可用 | 历史K线数据 |
| 估值指标 | 动态计算 | ✅ 可用 | PE、PB、市值 |

### ❌ 暂时无法获取的数据

| 数据类型 | 接口 | 状态 | 原因 |
|----------|------|------|------|
| 利润表 | `stock_profit_sheet_by_report_em` | ❌ 失败 | 接口报错 |
| 资产负债表 | `stock_balance_sheet_by_reportly` | ❌ 不存在 | 接口名称错误 |
| 现金流量表 | `stock_cash_flow_sheet_by_reportly` | ❌ 不存在 | 接口名称错误 |
| 财务指标 | `stock_financial_analysis_indicator_em` | ❌ 失败 | 返回None |

**特别注意**：科创板（688开头）的财务数据在AkShare中支持不完善。

---

## 🔧 解决方案

### 方案1：使用新脚本 `get_financial_data.py`

```bash
# 查看财务数据获取指南
python3 get_financial_data.py 688981 --guide

# 使用新浪财经（HTML解析）
python3 get_financial_data.py 688981 --sina

# 使用Tushare（需要API Token）
python3 get_financial_data.py 688981 --tushare YOUR_TOKEN
```

### 方案2：手动获取财务数据

#### 方法1：巨潮资讯（官方推荐）

**网址**：http://www.cninfo.com.cn/

**步骤**：
1. 搜索股票代码（如 688981）
2. 点击"公告"查看财报
3. 下载PDF财报
4. 查看财务数据

**优点**：
- ✅ 官方数据，最准确
- ✅ 数据完整（三大报表）
- ✅ 免费访问

**缺点**：
- ❌ PDF格式，不便解析
- ❌ 需要手动查看

#### 方法2：东方财富

**网址**：http://data.eastmoney.com/

**步骤**：
1. 输入股票代码
2. 点击"财务分析"
3. 查看各项指标

**优点**：
- ✅ 数据详细
- ✅ 可视化图表
- ✅ 多年对比

**缺点**：
- ❌ 需要网页访问
- ❌ 难以批量获取

#### 方法3：同花顺

**网址**：http://basic.10jqka.com.cn/

**优点**：
- ✅ 财务指标齐全
- ✅ 有同行对比
- ✅ 图表直观

### 方案3：使用 Tushare（推荐用于程序化获取）

**安装**：
```bash
pip3 install tushare
```

**注册**：
1. 访问 https://tushare.pro/register
2. 注册账号
3. 获取 API Token

**使用示例**：
```python
import tushare as ts

# 设置Token
ts.set_token('YOUR_TOKEN_HERE')
pro = ts.pro_api()

# 获取财务指标
df = pro.fina_indicator(ts_code='688981.SH', limit=4)

# 获取利润表
df = pro.income(ts_code='688981.SH', limit=4)

# 获取资产负债表
df = pro.balancesheet(ts_code='688981.SH', limit=4)

# 获取现金流量表
df = pro.cashflow(ts_code='688981.SH', limit=4)
```

**优点**：
- ✅ 数据完整
- ✅ 接口稳定
- ✅ 支持科创板
- ✅ 结构化数据

**缺点**：
- ❌ 需要注册
- ❌ 有积分限制（免费120分/天）

---

## 📝 财务数据获取清单

### 对于中芯国际 (688981)

**已获取** ✅：
- 基本信息（股票代码、名称、行业）
- 实时行情（股价116.93元，PE 185.59倍）
- 市值数据（总市值9355亿元）
- 历史价格（最近10天）

**缺失数据** ❌：
- 营收金额及增速
- 净利润及增速
- 毛利率、净利率
- ROE、ROA
- 资产负债率
- 现金流数据
- 研发投入

**获取建议**：

1. **快速查看**：访问东方财富 http://data.eastmoney.com/bbsj/688981.html

2. **详细分析**：下载巨潮资讯财报PDF

3. **程序化获取**：注册Tushare，使用API获取

---

## 🎯 推荐方案总结

| 使用场景 | 推荐方案 | 成本 | 难度 |
|----------|----------|------|------|
| **偶尔查看** | 东方财富网页 | 免费 | ⭐ 简单 |
| **详细分析** | 巨潮资讯PDF | 免费 | ⭐⭐ 中等 |
| **批量获取** | Tushare API | 免费(有限制) | ⭐⭐⭐ 较难 |
| **高频监控** | Tushare + 付费 | 付费 | ⭐⭐⭐ 较难 |

---

## 📚 相关脚本

1. **fetch_stock_data.py** - 获取基本行情数据
2. **get_financial_data.py** - 获取详细财务数据
3. **calculate_ratios.py** - 计算财务指标

---

## 🔗 快速链接

- **AkShare文档**: https://akshare.akfamily.xyz/
- **Tushare官网**: https://tushare.pro/
- **巨潮资讯**: http://www.cninfo.com.cn/
- **东方财富数据**: http://data.eastmoney.com/

---

**最后更新**: 2026-02-23
**维护者**: Claude Sonnet 4.6
