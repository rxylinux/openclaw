# 估值模型构建脚本

本目录包含估值模型构建相关的工具脚本。

## 脚本列表

### build_dcf.py

构建DCF模型的脚本。

**功能**：
- 获取历史FCF数据
- 计算WACC
- 运行DCF模型
- 生成敏感性分析

**使用方式**：
```bash
python3 scripts/build_dcf.py AAPL
```

### comparables.py

可比公司估值对比脚本。

**功能**：
- 获取同行数据
- 计算估值倍数
- 对比分析

**使用方式**：
```bash
python3 scripts/comparables.py AAPL
```

### analyst_targets.py

获取分析师目标价脚本。

**功能**：
- 汇总华尔街目标价
- 计算平均/中位数
- 追踪近期更新

**使用方式**：
```bash
python3 scripts/analyst_targets.py AAPL
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
pip install yfinance numpy pandas requests python-dotenv
```

## 注意事项

1. DCF假设需有数据支撑
2. 敏感性分析展示关键变量
3. 多种方法交叉验证
