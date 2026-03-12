# 法拍数据采集系统 - 使用指南

## 系统架构

```
auction-data-collector/
├── SKILL.md                      # 技能说明
├── init_database.py               # 数据库初始化
├── collect_ali_auction.py        # 阿里拍卖采集
├── analyze_data.py                # 数据分析
└── dashboard.py                   # Web看板

auction-data/
├── auction.db                     # SQLite 数据库
└── dashboard.html                 # 可视化看板
```

---

## 快速开始

### 第 1 步：初始化数据库

```bash
# 创建数据库表结构
python3 /root/.openclaw/workspace/skills/auction-data-collector/init_database.py
```

**预期输出：**
```
✓ 目录创建完成
✓ 数据库已备份
✓ 数据库连接成功
✓ 数据表创建完成
  - ali_auctions
  - jd_auctions
  - judicial_auctions
  - property_listings
  - price_analysis
  - collection_logs
✓ 示例数据插入完成
```

---

### 第 2 步：采集数据

#### 采集阿里拍卖数据

```bash
# 采集最近 7 天的阿里拍卖数据（默认）
python3 /root/.openclaw/workspace/skills/auction-data-collector/collect_ali_auction.py

# 采集特定关键词的拍卖数据
python3 /root/.openclaw/workspace/skills/auction-data-collector/collect_ali_auction.py --keyword "法拍房"

# 采集最近 30 天的数据
python3 /root/.openclaw/workspace/skills/auction-data-collector/collect_ali_auction.py --days 30

# 限制采集数量
python3 /root/.openclaw/workspace/skills/auction-data-collector/collect_ali_auction.py --limit 50
```

**采集的数据字段：**
- title: 标题
- price: 当前价格
- reserve_price: 起拍价
- current_price: 当前出价（拍卖中）
- auction_status: 拍卖状态（拍卖中、已成交、流拍等）
- auction_type: 拍卖类型（法拍房、司法拍卖、资产拍卖等）
- start_time: 开始时间
- end_time: 结束时间
- location: 拍卖地点
- court: 委托法院
- url: 拍卖链接
- source: 数据源（ali）

---

### 第 3 步：分析数据

```bash
# 分析阿里拍卖数据
python3 /root/.openclaw/workspace/skills/auction-data-collector/analyze_data.py --table ali_auctions

# 导出数据到 CSV
python3 /root/.openclaw/workspace/skills/auction-data-collector/analyze_data.py --export

# 分析所有数据源
python3 /root/.openclaw/workspace/skills/auction-data-collector/analyze_data.py --all

# 生成完整分析报告
python3 /root/.openclaw/workspace/skills/auction-data-collector/analyze_data.py --report
```

**分析内容包括：**
1. 某本统计（总数、成交数、流拍数）
2. 价格分析（均价、最低价、最高价）
3. 类别分析（法拍房、车辆、资产等）
4. 地区热力图（各城市/区域的数据量）
5. 时间趋势分析（最近7天的数据变化）
6. 成交率分析（各类别的成交率）

---

### 第 4 步：查看数据看板

```bash
# 生成 Web 看板（默认）
python3 /root/.openclaw/workspace/skills/auction-data-collector/dashboard.py

# 仅导出 JSON 数据（供其他程序使用）
python3 /root/.openclaw/workspace/skills/auction-data-collector/dashboard.py --json

# 指定 Web 服务器端口
python3 /root/.openclaw/workspace/skills/auction-data-collector/dashboard.py --port 9000
```

**看板功能：**
- 📊 数据概览（总记录数、各数据源统计）
- 📈 状态分布（拍卖中、已成交、流拍、预展中）
- 📋 类别分析（各拍卖类型的统计和价格）
- 🗺️ 地区热力图（各城市/区域的数据量）
- 📝 最新采集记录
- ⏱️ 自动刷新（每5分钟）

**访问看板：**
```bash
# 在浏览器中打开
firefox /root/.openclaw/workspace/auction-data/dashboard.html

# 或者使用简单的 HTTP 服务器
cd /root/.openclaw/workspace/auction-data
python3 -m http.server 8888

# 然后在浏览器访问
# http://localhost:8888/dashboard.html
```

---

## 数据库操作

### 查询数据库

```bash
# 连接数据库
sqlite3 /root/.openclaw/workspace/auction-data/auction.db

# 查看所有表
.tables

# 查看表结构
.schema ali_auctions

# 查询阿里拍卖数据（前 10 条）
SELECT * FROM ali_auctions ORDER BY created_at DESC LIMIT 10;

# 查询已成交的拍卖（按价格降序）
SELECT * FROM ali_auctions 
WHERE auction_status = '已成交' 
ORDER BY price DESC 
LIMIT 10;

# 查询特定地区的拍卖
SELECT * FROM ali_auctions 
WHERE location LIKE '%北京%';

# 统计各类别的成交率
SELECT 
    auction_type,
    COUNT(*) as total,
    SUM(CASE WHEN auction_status = '已成交' THEN 1 ELSE 0 END) as completed,
    ROUND(SUM(CASE WHEN auction_status = '已成交' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM ali_auctions
GROUP BY auction_type;
```

### 导出数据

```bash
# 导出为 CSV（SQLite 自带）
sqlite3 /root/.openclaw/workspace/auction-data/auction.db
.headers on
.mode csv
.output ali_auctions.csv
SELECT * FROM ali_auctions;
.quit
```

---

## 定时采集配置

### 使用 Crontab

```bash
# 编辑 crontab
crontab -e

# 添加定时任务
# 每天早上 8 点采集阿里拍卖数据
0 8 * * * python3 /root/.openclaw/workspace/skills/auction-data-collector/collect_ali_auction.py >> /root/.openclaw/workspace/auction-data/logs/collection.log 2>&1

# 每天中午 12 点分析数据
0 12 * * * python3 /root/.openclaw/workspace/skills/auction-data-collector/analyze_data.py --all >> /root/.openclaw/workspace/auction-data/logs/analysis.log 2>&1

# 每天晚上 8 点更新看板
0 20 * * * python3 /root/.openclaw/workspace/skills/auction-data-collector/dashboard.py >> /root/.openclaw/workspace/auction-data/logs/dashboard.log 2>&1
```

---

## 数据源说明

### 1. 阿里拍卖
- **URL**: https://paimai.taobao.com
- **数据类型**: 法拍、司法拍卖、资产拍卖
- **更新频率**: 实时
- **采集限制**: 公开数据，完全合法
- **建议采集频率**: 每天 1-2 次

### 2. 京东拍卖
- **URL**: https://auction.jd.com
- **数据类型**: 司法拍卖、资产处置
- **更新频率**: 实时
- **采集限制**: 公开数据，完全合法
- **建议采集频率**: 每天 1 次

### 3. 司法拍卖平台
- **人民法院诉讼资产网**: https://www.rmfysszc.gov.cn
- **中国拍卖行业协会**: https://www.caa123.org.cn
- **数据类型**: 司法拍卖公告
- **更新频率**: 每周
- **采集限制**: 公开数据，完全合法
- **建议采集频率**: 每周 1-2 次

### 4. 房产交易平台
- **链家**: https://www.lianjia.com
- **我爱我家**: https://www.5i5j.com
- **安居客**: https://www.anjuke.com
- **数据类型**: 二手房、法拍房
- **更新频率**: 实时
- **采集限制**: 公开数据，完全合法
- **建议采集频率**: 每天 1 次

---

## 高级功能

### 1. 价格监控告警

```python
# 在 OpenClaw 中使用
import sqlite3

def check_price_alerts():
    conn = sqlite3.connect('/root/.openclaw/workspace/auction-data/auction.db')
    cursor = conn.cursor()
    
    # 查找价格低于设定阈值的新拍卖
    cursor.execute("""
        SELECT title, price, url, location
        FROM ali_auctions
        WHERE price < 500000  # 50 万以下
          AND auction_status = '拍卖中'
          AND created_at >= datetime('now', '-1 day')
        ORDER BY price ASC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return results
```

### 2. 区域筛选分析

```python
# 按城市/区域筛选数据
def analyze_by_region(region):
    conn = sqlite3.connect('/root/.openclaw/workspace/auction-data/auction.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                COUNT(*) as count,
                SUM(CASE WHEN auction_status = '已成交' THEN 1 ELSE 0 END) as completed
        FROM ali_auctions
        WHERE location LIKE ?
        GROUP BY location
    """, (f'%{region}%',))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
```

### 3. 成交率趋势分析

```python
# 分析最近的成交率趋势
def analyze_success_rate_trend(days=30):
    conn = sqlite3.connect('/root/.openclaw/workspace/auction-data/auction.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN auction_status = '已成交' THEN 1 ELSE 0 END) as completed
        FROM ali_auctions
        WHERE created_at >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """, (days,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
```

---

## 常见问题

### Q1: 采集不到数据？

**可能原因：**
1. 网站改版，HTML 结构变化
2. 请求过于频繁，被限制
3. 需要登录才能访问

**解决方法：**
1. 检查日志，查看错误信息
2. 降低采集频率，增加延迟
3. 使用代理 IP 池

### Q2: 数据库被锁定？

**错误信息：**
```
sqlite3.OperationalError: database is locked
```

**解决方法：**
1. 确保没有其他进程正在访问数据库
2. 关闭所有数据库连接后重新执行
3. 使用 `timeout` 命令避免长时间锁定

### Q3: Web 看板无法刷新？

**可能原因：**
1. 浏览器缓存
2. 数据库权限问题

**解决方法：**
1. 强制刷新浏览器（Ctrl+Shift+R）
2. 检查数据库文件权限
3. 查看浏览器控制台错误信息

---

## 数据安全与备份

### 备份数据库

```bash
# 手动备份
cp /root/.openclaw/workspace/auction-data/auction.db /root/.openclaw/workspace/auction-data/backups/auction_backup_$(date +%Y%m%d_%H%M%S).db

# 自动备份（添加到 crontab）
0 2 * * * /root/.openclaw/workspace/auction-data/scripts/backup_database.sh
```

### 数据权限控制

```bash
# 设置数据库文件权限（仅 root 可写）
chmod 640 /root/.openclaw/workspace/auction-data/auction.db
chown root:root /root/.openclaw/workspace/auction-data/auction.db
```

---

## 性能优化

### 1. 批量插入优化

```python
# 使用事务批量插入
def batch_insert_auctions(auctions):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        for auction in auctions:
            cursor.execute("""
                INSERT OR IGNORE INTO ali_auctions
                (title, price, reserve_price, auction_status, auction_type,
                 start_time, end_time, location, court, url, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                auction['title'], auction['price'], auction['reserve_price'],
                auction['auction_status'], auction['auction_type'],
                auction['start_time'], auction['end_time'],
                auction['location'], auction['court'],
                auction['url'], auction['source']
            ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

### 2. 查询优化

```sql
-- 使用索引优化查询
CREATE INDEX idx_ali_price_status ON ali_auctions(price, auction_status);
CREATE INDEX idx_ali_created ON ali_auctions(created_at);

-- 分页查询
SELECT * FROM ali_auctions
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

---

## 法律合规

### ✅ 本系统的优点

1. **完全合法**
   - 只采集公开数据
   - 不涉及任何私密信息
   - 遵守《反不正当竞争法》

2. **道德使用**
   - 控制采集频率
   - 不对服务器造成压力
   - 尊重网站的服务条款

3. **数据价值**
   - 公开透明的拍卖数据
   - 辅助投资决策
   - 促进市场信息透明

### ⚠️ 使用注意事项

1. **不要爬取淘宝**
   - 淘宝明确禁止自动爬取
   - 可能导致法律诉讼
   - 可能面临封号风险

2. **不要绕过登录**
   - 不要尝试破解登录系统
   - 不要使用任何黑客手段
   - 不要泄露任何账号信息

3. **遵守法律法规**
   - 遵守《网络安全法》
   - 遵守《电子商务法》
   - 遵守网站的服务条款

---

## 技术支持

如果遇到问题：

1. 查看日志文件
   - 采集日志：`/root/.openclaw/workspace/auction-data/logs/collection.log`
   - 分析日志：`/root/.openclaw/workspace/auction-data/logs/analysis.log`
   - 看板日志：`/root/.openclaw/workspace/auction-data/logs/dashboard.log`

2. 查看错误信息
   - Python 错误信息会显示在终端
   - SQLite 错误会显示在数据库操作中

3. 检查数据库
   - 使用 SQLite 命令行工具检查数据
   - 验证表结构和数据完整性

---

## 下一步扩展

### 可以添加的功能

1. **更多数据源**
   - 阿里资产拍卖
   - 拍卖行拍卖
   - 其他司法拍卖平台

2. **高级分析**
   - 机器学习价格预测
   - 投资回报率计算
   - 风险评估模型

3. **可视化增强**
   - 交互式图表（Chart.js、D3.js）
   - 地图可视化（百度地图 API）
   - 实时数据推送（WebSocket）

4. **告警系统**
   - 价格低于阈值告警
   - 新增拍卖通知
   - 成交结果通知

5. **数据导出**
   - Excel 格式
   - PDF 报告
   - API 接口

---

**最后更新**: 2026-03-06
**版本**: v1.0.0
**维护**: AI Agent
