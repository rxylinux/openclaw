# Gemini Bridge 使用示例

## 1. 快速测试

### 基础聊天
```bash
# 启动服务（另一个终端）
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py

# 发送请求
curl -X POST http://localhost:19999/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好","timeout":60}'
```

### CLI 工具
```bash
bash /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_chat.sh "解释量子计算"
```

## 2. 投资分析场景

### 批量分析股票
```bash
#!/bin/bash
STOCKS=("AAPL" "NVDA" "TSLA" "MSFT")

for stock in "${STOCKS[@]}"; do
  echo "Analyzing $stock..."

  curl -s -X POST http://localhost:19999/chat \
    -H "Content-Type: application/json" \
    -d "{\"prompt\":\"从投资角度分析 $stock 的基本面，包括：1. 核心业务 2. 财务状况 3. 竞争优势 4. 投资风险\",\"timeout\":120}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"

  echo "---"
  sleep 2
done
```

### 多会话对比分析
```bash
# 创建科技股会话
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"开始分析科技股","session_id":"tech-stocks"}'

# 添加个股
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"分析英伟达的护城河","session_id":"tech-stocks"}'

curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"对比英伟达和AMD","session_id":"tech-stocks"}'

# 创建医药股会话
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"开始分析医药股","session_id":"healthcare"}'
```

## 3. 新闻分析

### 批量新闻摘要
```bash
#!/bin/bash
# news-titles.txt:
# 英伟达发布新一代AI芯片
# 特斯拉在中国推出新车型
# 美联储宣布降息

while IFS= read -r title; do
  echo "=== $title ==="

  curl -s -X POST http://localhost:19999/chat \
    -H "Content-Type: application/json" \
    -d "{\"prompt\":\"从投资角度分析这条新闻：$title。给出：1. 影响的标的 2. 影响程度（高/中/低）3. 投资建议\",\"timeout\":90}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"

  echo ""
  sleep 2
done < news-titles.txt
```

## 4. 集成到 Python 脚本

```python
#!/usr/bin/env python3
import requests
import json

GEMINI_API = "http://localhost:19999"

def ask_gemini(prompt, timeout=120, session_id=None):
    """调用 Gemini Bridge API"""
    payload = {"prompt": prompt, "timeout": timeout}
    if session_id:
        payload["session_id"] = session_id

    response = requests.post(f"{GEMINI_API}/chat", json=payload)
    return response.json()

def analyze_stock(symbol):
    """分析单只股票"""
    prompt = f"""
    分析 {symbol} 的投资价值。
    从以下维度：
    1. 业务模式
    2. 财务指标
    3. 竞争优势
    4. 投资风险
    5. 当前估值

    给出明确结论：强烈买入/买入/持有/卖出
    """

    result = ask_gemini(prompt, timeout=150, session_id=symbol)

    if result["status"] == "ok":
        print(f"=== {symbol} 分析结果 ===")
        print(result["response"])
        print(f"耗时: {result['elapsed']}秒")
    else:
        print(f"错误: {result.get('error', 'Unknown error')}")

# 使用
if __name__ == "__main__":
    analyze_stock("NVDA")
```

## 5. 定期复盘

```python
#!/usr/bin/env python3
"""
每周投资复盘
"""
import requests
from datetime import datetime

def weekly_review():
    prompt = f"""
    今天是 {datetime.now().strftime('%Y-%m-%d')}。
    帮我进行每周投资复盘：

    1. 回顾本周重要市场事件
    2. 分析持仓股票的表现
    3. 总结本周的交易操作
    4. 提出下周关注的重点

    请以投资经理的口吻，专业、客观地分析。
    """

    response = requests.post(
        "http://localhost:19999/chat",
        json={"prompt": prompt, "timeout": 180, "session_id": "weekly-review"}
    )

    result = response.json()

    if result["status"] == "ok":
        print(result["response"])

        # 保存到文件
        with open(f"review_{datetime.now().strftime('%Y%m%d')}.md", "w") as f:
            f.write(f"# 投资复盘 {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(result["response"])
    else:
        print(f"复盘失败: {result.get('error')}")

if __name__ == "__main__":
    weekly_review()
```

## 6. 健康检查脚本

```bash
#!/bin/bash
# 检查 Gemini Bridge 服务状态

echo "检查 Gemini Bridge 服务..."

# 1. 检查服务是否运行
if curl -s http://localhost:19999/health > /dev/null 2>&1; then
    echo "✓ 服务运行中"
else
    echo "✗ 服务未运行"
    exit 1
fi

# 2. 检查 Chrome 连接
HEALTH=$(curl -s http://localhost:19999/health)
echo "健康状态: $HEALTH" | python3 -m json.tool

# 3. 测试简单请求
echo ""
echo "测试请求..."
TEST=$(curl -s -X POST http://localhost:19999/chat \
  -d '{"prompt":"1+1=","timeout":30}')

echo "$TEST" | python3 -m json.tool

echo ""
echo "✓ 所有检查完成"
```

## 7. 批量文档分析

```python
#!/usr/bin/env python3
"""
批量分析文档（PDF/Word/Txt）
"""
import os
import requests
import subprocess

def read_document(file_path):
    """读取文档内容"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        # 使用 pdftotext
        result = subprocess.run(
            ["pdftotext", file_path, "-"],
            capture_output=True,
            text=True
        )
        return result.stdout
    else:
        raise ValueError(f"Unsupported format: {ext}")

def analyze_document(file_path, question):
    """分析文档"""
    content = read_document(file_path)

    prompt = f"""
    以下是一份文档内容：

    {content[:10000]}  # 限制长度

    问题：{question}

    请基于文档内容回答。
    """

    response = requests.post(
        "http://localhost:19999/chat",
        json={"prompt": prompt, "timeout": 180}
    )

    result = response.json()

    if result["status"] == "ok":
        return result["response"]
    else:
        return f"分析失败: {result.get('error')}"

# 使用
if __name__ == "__main__":
    doc_path = "财报.pdf"
    question = "营收增长了多少？净利润率是多少？"

    answer = analyze_document(doc_path, question)
    print(answer)
```

## 8. 定时任务集成

```bash
# 添加到 crontab
# crontab -e

# 每天早上 8 点分析新闻
0 8 * * * bash /path/to/news-analysis.sh >> /var/log/gemini-news.log 2>&1

# 每周五晚上 8 点复盘
0 20 * * 5 /usr/bin/python3 /path/to/weekly-review.py >> /var/log/gemini-review.log 2>&1
```

## 调试技巧

### 查看完整响应
```bash
curl -v -X POST http://localhost:19999/chat \
  -d '{"prompt":"测试"}' | python3 -m json.tool
```

### 测试响应时间
```bash
time curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"快速测试","timeout":30}'
```

### 清理会话
```bash
# 新建会话会自动清理旧会话
curl -X POST http://localhost:19999/new
```
