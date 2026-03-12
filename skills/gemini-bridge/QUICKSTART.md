# Gemini Bridge - 5 分钟上手指南

## 什么是 Gemini Bridge？

把 Google Gemini 变成你的本地 API 服务，零成本、无限用。

## 为什么使用？

| 场景 | 传统方式 | Gemini Bridge |
|------|---------|---------------|
| 批量分析 | $5-20/月 API 费 | $0 |
| 深度推理 | API 限流 | 无限制 |
| 长上下文 | API 超配额 | 不受限 |
| 隐私保护 | 数据上传 | 本地运行 |

## 快速开始（3 步）

### 1️⃣ 设置权限（1 分钟）

```bash
# 打开自动化权限设置
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"

# 勾选 "Google Chrome"
```

### 2️⃣ 启动服务（10 秒）

```bash
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py
```

### 3️⃣ 发送请求（5 秒）

```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"你好"}'
```

## 常用命令

### 基础对话
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"解释量子计算"}'
```

### 指定超时
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"分析英伟达","timeout":120}'
```

### 多会话
```bash
# 会话 1：股票分析
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"分析 AAPL","session_id":"stocks"}'

# 会话 2：新闻摘要
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"总结今天的新闻","session_id":"news"}'
```

### CLI 工具
```bash
bash /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_chat.sh "你好"
```

## 实战示例

### 📈 股票分析
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"分析英伟达的投资价值，从业务、财务、竞争三个维度"}'
```

### 📰 新闻分析
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"从投资角度分析：美联储宣布降息。给出影响和投资建议"}'
```

### 📊 财报解读
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"解读特斯拉最新财报：营收增长 25%，净利润率 8%，如何评价？"}'
```

### 🔄 定期复盘
```python
import requests

def weekly_review():
    prompt = """
    进行每周投资复盘：
    1. 回顾本周市场事件
    2. 分析持仓表现
    3. 总结交易操作
    4. 提出下周关注点
    """

    response = requests.post(
        "http://localhost:19999/chat",
        json={"prompt": prompt, "timeout": 180, "session_id": "weekly-review"}
    )

    print(response.json()['response'])

weekly_review()
```

## API 参考

### POST /chat
```json
{
  "prompt": "你的问题",
  "timeout": 120,
  "session_id": "optional-session-id"
}
```

### POST /new
创建新会话（新标签页）

### GET /health
健康检查

### GET /history
读取当前会话历史

## 故障排查

### ❌ 权限错误
```
解决方案：系统设置 > 隐私与安全性 > 自动化 > 勾选 "Google Chrome"
```

### ❌ Chrome 未响应
```bash
# 启动 Chrome
open -a "Google Chrome"

# 导航到 Gemini
open -a "Google Chrome" https://gemini.google.com
```

### ❌ 输入框未找到
```bash
# 重新加载
curl -X POST http://localhost:19999/new
```

## 进阶使用

查看更多示例：
```bash
cat /root/.openclaw/workspace/skills/gemini-bridge/EXAMPLES.md
```

查看详细文档：
```bash
cat /root/.openclaw/workspace/skills/gemini-bridge/SKILL.md
```

## 下一步

1. ✅ 运行测试脚本
   ```bash
   bash /root/.openclaw/workspace/skills/gemini-bridge/test.sh
   ```

2. ✅ 尝试示例代码
   ```bash
   cat EXAMPLES.md
   ```

3. ✅ 集成到你的工具链
   - Python 脚本
   - 定时任务
   - Web 服务

## 常见问题

**Q: 会消耗 API 配额吗？**
A: 不会。这是复用 Gemini Web 界面，零额外费用。

**Q: 支持流式输出吗？**
A: 当前版本不支持，计划在 v2.0 添加。

**Q: 可以远程访问吗？**
A: 可以。启动时指定 `--host 0.0.0.0`，注意防火墙设置。

**Q: 需要保持 Chrome 打开吗？**
A: 建议。首次调用会自动启动，但手动关闭后需要重新调用 `/new`。

---

**有问题？** 查看 [INSTALL.md](./INSTALL.md) 或 [SKILL.md](./SKILL.md)
