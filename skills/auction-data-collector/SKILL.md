---
name: auction-data-collector
description: 合法采集法拍、司法拍卖、房产交易数据的智能系统
metadata: { "openclaw": { "emoji": "🏛️", "requires": { "bins": ["python3"], "env": [] }, "primaryEnv": "" } }
---

# 法拍数据采集器

## 功能

1. **公开数据源采集**
   - 阿里拍卖
   - 京东拍卖
   - 人民法院诉讼资产网
   - 中国拍卖行业协会
   - 链家房产数据

2. **智能数据处理**
   - 自动去重
   - 价格分析
   - 成交率统计
   - 区域热力图

3. **数据可视化**
   - 实时数据看板
   - 价格趋势图
   - 成交分布图

## 使用方法

```bash
# 初始化数据库
python3 init_database.py

# 采集阿里拍卖数据
python3 collect_ali_auction.py --days 7

# 采集京东拍卖数据
python3 collect_jd_auction.py --days 7

# 采集司法拍卖数据
python3 collect_judicial_auction.py --days 7

# 分析数据
python3 analyze_data.py

# 启动Web看板
python3 dashboard.py
```

## 技术特点

✅ 完全合法 - 只采集公开数据
✅ 数据去重 - 自动去除重复项目
✅ 实时更新 - 支持增量采集
✅ 智能分析 - 价格趋势、成交率等
✅ 可视化展示 - Web看板、图表

## 数据源

1. **阿里拍卖**
   - URL: https://paimai.taobao.com
   - 内容: 法拍、司法拍卖、资产拍卖
   - 更新频率: 实时

2. **京东拍卖**
   - URL: https://auction.jd.com
   - 内容: 司法拍卖、资产处置
   - 更新频率: 实时

3. **人民法院诉讼资产网**
   - URL: https://www.rmfysszc.gov.cn
   - 内容: 司法拍卖公告
   - 更新频率: 每日

4. **中国拍卖行业协会**
   - URL: https://www.caa123.org.cn
   - 内容: 行业拍卖信息
   - 更新频率: 每周

5. **链家房产数据**
   - URL: https://www.lianjia.com
   - 内容: 二手房、法拍房
   - 更新频率: 实时
