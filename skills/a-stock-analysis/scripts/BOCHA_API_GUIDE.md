# 博查API集成指南

## 📋 概述

博查API是一个专为AI应用设计的搜索引擎，可以作为百度搜索API的替代方案用于A股股票分析。

### 博查 vs 百度搜索对比

| 特性 | 博查API | 百度搜索API |
|------|---------|------------|
| **成本** | 免费资源包 + 按需付费 | 需要API密钥 |
| **响应速度** | 0.15秒极速响应 | 较慢 |
| **数据合规** | 国内合规，数据不出海 | 国内合规 |
| **AI友好** | 专为AI设计 | 通用搜索 |
| **返回结果** | 最多50条 | 配置决定 |
| **文本摘要** | 支持 | 支持 |

---

## 🚀 快速开始

### 1. 获取API密钥

1. 访问博查AI开放平台：https://open.bocha.cn
2. 注册账号
3. 获取 API-KEY
4. 免费领取调用资源包

### 2. 安装依赖

```bash
pip3 install requests
```

### 3. 设置环境变量

```bash
export BOCHA_API_KEY=your_api_key_here
```

### 4. 使用脚本

```bash
# 综合搜索（获取所有信息）
python3 bocha_search.py 002472 双环传动

# 仅搜索基本信息
python3 bocha_search.py 002472 双环传动 --basic

# 仅搜索财务数据
python3 bocha_search.py 002472 双环传动 --financial

# 仅搜索最新新闻
python3 bocha_search.py 002472 双环传动 --news
```

---

## 📊 API接口说明

### Web Search API（网页搜索）

**端点**: `https://api.bocha.cn/v1/web-search`

**参数**:
```python
{
    "query": "搜索关键词",
    "count": 10,              # 返回结果数量（最多50条）
    "freshness": "noLimit",   # 时间范围
    "summary": true           # 是否返回摘要
}
```

**freshness 选项**:
- `noLimit`: 不限制
- `day`: 一天内
- `week`: 一周内
- `month`: 一个月内
- `year`: 一年内

**示例**:
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

payload = {
    "query": "双环传动 基本信息",
    "count": 10,
    "freshness": "month",
    "summary": True
}

response = requests.post(
    "https://api.bocha.cn/v1/web-search",
    headers=headers,
    json=payload
)

print(response.json())
```

### AI Search API（AI搜索）

**端点**: `https://api.bocha.cn/v1/ai-search`

**特点**：
- 支持自然语言搜索
- 自动获取垂直领域结构化数据
- 可开启大模型生成答案
- 支持流式输出

**参数**:
```python
{
    "query": "搜索关键词",
    "count": 10,
    "freshness": "noLimit",
    "answer": False,      # 是否返回AI生成答案
    "stream": False       # 是否流式输出
}
```

---

## 🔧 集成到 a-stock-analysis Skill

### 方法1: 替换百度搜索

在 SKILL.md 中，将百度搜索命令替换为博查API：

```markdown
### 1. 股票信息查询

**工具**: 博查API
```bash
python3 skills/a-stock-analysis/scripts/bocha_search.py '{
  "stock_code": "<股票代码>",
  "stock_name": "<股票名称>",
  "option": "--basic"
}'
```
```

### 方法2: 直接在Python中使用

```python
from bocha_search import StockInfoSearcher

# 初始化搜索器
searcher = StockInfoSearcher(api_key="your_api_key")

# 综合搜索
results = searcher.comprehensive_search("002472", "双环传动")

# 查看结果
import json
print(json.dumps(results, indent=2, ensure_ascii=False))
```

---

## 📈 使用示例

### 示例1: 搜索双环传动基本信息

```bash
export BOCHA_API_KEY=your_key
python3 bocha_search.py 002472 双环传动 --basic
```

**输出**:
```json
{
  "query_type": "basic_info",
  "stock_code": "002472",
  "search_time": "2026-02-23 16:30:00",
  "data": {
    "web_results": [
      {
        "title": "双环传动(002472)股票基本信息",
        "url": "http://basic.10jqka.com.cn/002472/",
        "snippet": "公司名称：双环传动...",
        "publish_date": "2025-12-01"
      }
    ]
  }
}
```

### 示例2: 搜索最新新闻

```bash
python3 bocha_search.py 002472 双环传动 --news
```

### 示例3: 搜索行业信息

```bash
python3 bocha_search.py --industry 汽车零部件
```

---

## 💡 最佳实践

### 1. 搜索关键词优化

```python
# 好的搜索词
query = "002472 双环传动 主营业务"
query = "002472 ROE 市盈率 财务指标"
query = "002472 最新新闻 重大事项"

# 避免过于宽泛的搜索词
# ❌ query = "股票"
# ✅ query = "002472 股票基本信息"
```

### 2. 时间范围选择

```python
# 最新资讯
freshness = "week"

# 财务数据（通常不需要太新）
freshness = "month"

# 基本信息（可以放宽）
freshness = "year"
```

### 3. 结果数量控制

```python
# 快速浏览
count = 5

# 详细分析
count = 20

# 深度研究
count = 50
```

---

## ⚠️ 注意事项

### 1. API密钥安全

```bash
# ❌ 不要在代码中硬编码
api_key = "sk-xxxxxxxx"

# ✅ 使用环境变量
api_key = os.getenv('BOCHA_API_KEY')
```

### 2. 请求频率控制

```python
import time

# 添加延迟，避免频繁请求
def search_with_delay(query):
    result = searcher.client.web_search(query=query)
    time.sleep(1)  # 每次请求间隔1秒
    return result
```

### 3. 错误处理

```python
try:
    result = searcher.client.web_search(query=query)
    if "error" in result:
        print(f"搜索失败: {result['error']}")
except Exception as e:
    print(f"发生错误: {e}")
```

---

## 📊 费用说明

### 免费资源包

- 新用户注册赠送免费资源包
- 包含一定次数的免费调用

### 付费标准

- Web Search API: 按调用次数计费
- AI Search API: 按调用次数 + token使用量计费
- Semantic Reranker: 0.005元/次

详细价格请参考：https://open.bocha.cn

---

## 🆚 从百度搜索迁移

### 迁移步骤

#### 1. 注册博查账号

```bash
# 访问
https://open.bocha.cn

# 注册并获取API密钥
export BOCHA_API_KEY=your_new_key
```

#### 2. 更新搜索脚本

将 `baidu-search/scripts/search.py` 替换为 `bocha_search.py`

#### 3. 更新 SKILL.md

```markdown
## 使用博查API搜索股票信息

```bash
python3 skills/a-stock-analysis/scripts/bocha_search.py '{
  "stock_code": "002472",
  "stock_name": "双环传动",
  "option": "--basic"
}'
```
```

### 优势对比

| 特性 | 博查API | 百度搜索 |
|------|---------|----------|
| **获取难度** | 简单，直接注册 | 复杂，需要企业认证 |
| **响应速度** | 0.15秒 | 较慢 |
| **AI友好** | 专为AI设计 | 通用搜索 |
| **数据质量** | 高质量，结构化 | 需要清洗 |
| **成本** | 免费+付费 | 需要企业认证 |

---

## 🔗 相关链接

- **博查官网**: https://bocha.cn
- **开放平台**: https://open.bocha.cn
- **API文档**: https://bocha-ai.feishu.cn/wiki/HmtOw1z6vik14Fkdu5uc9VaInBb
- **注册地址**: https://open.bocha.cn

---

## 📝 更新日志

- **2026-02-23**: 初始版本，集成博查Web Search和AI Search API
- **待定**: 添加Semantic Reranker支持
- **待定**: 添加流式输出支持

---

**最后更新**: 2026-02-23
**维护者**: Claude Sonnet 4.6
