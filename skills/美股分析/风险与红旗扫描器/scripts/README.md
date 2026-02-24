# 风险扫描脚本

本目录包含风险扫描相关的工具脚本。

## 脚本列表

### financial_health.py

财务健康风险检查脚本。

**功能**：
- 债务增速 vs 营收增速
- FCF趋势分析
- 现金续航计算
- 债务到期分析

**使用方式**：
```bash
python3 scripts/financial_health.py AAPL
```

### insider_trading.py

内部人交易监控脚本。

**功能**：
- 获取Form 4数据
- 计算净买入/卖出
- 追踪6个月趋势

**使用方式**：
```bash
python3 scripts/insider_trading.py AAPL
```

### institutional_flow.py

机构持仓分析脚本。

**功能**：
- 获取13F数据
- 机构流入/流出
- 做空比例追踪

**使用方式**：
```bash
python3 scripts/institutional_flow.py AAPL
```

## 配置文件

### .env.example

环境变量配置示例。

```bash
# SEC API Key (用于获取Form 4、13F)
SEC_API_KEY=your_key_here

# Bloomberg API Key (可选)
BLOOMBERG_API_KEY=your_key_here

# Yahoo Finance API
YAHOO_FINANCE_KEY=your_key_here
```

## 依赖安装

```bash
pip install requests pandas python-dotenv sec-edgar
```

## 注意事项

1. SEC数据有延迟（Form 4：2天，13F：45天）
2. 做空数据来源多样
3. 监管新闻需人工验证
