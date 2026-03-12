# Gemini Bridge 技能

将 Google Gemini 转换为 REST API + CLI 工具，零 API Key 需求。

## 架构

```
你的终端/脚本 → Chrome AppleScript + JS 注入 → gemini.google.com → 响应提取
```

## 核心功能

### 1. REST API（推荐）

```bash
# 启动服务（Mac 本地）
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py --port 19999

# 发送聊天请求
curl -X POST http://localhost:19999/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好","timeout":120}'

# 创建新会话
curl -X POST http://localhost:19999/new

# 读取当前会话历史
curl http://localhost:19999/history

# 健康检查
curl http://localhost:19999/health
```

### 2. CLI 工具

```bash
# 本地调用
bash /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_chat.sh "你好"

# 指定超时时间
bash gemini_chat.sh "解释量子隧穿" --timeout 90

# 指定会话 ID
bash gemini_chat.sh "继续上一个话题" --session my-session
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/chat` | 发送提示，等待响应 |
| POST | `/new` | 创建新会话（新标签页）|
| GET | `/health` | 健康检查（Chrome URL, Gemini 状态）|
| GET | `/history` | 读取当前页面会话历史 |

## 请求示例

### POST /chat

```bash
curl -X POST http://localhost:19999/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "分析一下英伟达的投资价值",
    "timeout": 120,
    "session_id": "nvidia-analysis"
  }'
```

**响应：**
```json
{
  "status": "ok",
  "response": "英伟达（NVIDIA, NVDA）是AI芯片领域的绝对龙头...",
  "elapsed": 8.5
}
```

### POST /new

创建新的对话会话（打开新标签页）。

**响应：**
```json
{
  "status": "ok"
}
```

### GET /health

检查服务状态。

**响应：**
```json
{
  "status": "ok",
  "url": "https://gemini.google.com",
  "on_gemini": true,
  "version": "v1"
}
```

## 前置条件

1. **macOS 环境**
   - 系统设置 > 隐私与安全性 > 自动化 > 允许 Google Chrome

2. **Chrome 浏览器**
   - 已登录 [gemini.google.com](https://gemini.google.com)
   - 保持 Chrome 运行（或脚本会自动启动）

3. **Python 3**
   - 仅用 stdlib，无需额外依赖

## 技术细节

### 工作原理

1. **输入**：通过 `document.execCommand('insertText')` 插入文本
   - 绕过 React/Vue 受控组件限制
   - 触发真实浏览器输入事件

2. **提交**：通过 JS `button.click()` 点击发送按钮
   - 不依赖 System Events 权限
   - 纯 JavaScript 操作

3. **响应提取**：轮询 `document.body.innerText`
   - 检测 DOM 变化
   - 连续 3 次相同认为稳定

### 多会话管理

- 每个会话对应一个 Chrome 标签页
- 通过 `session_id` 参数区分
- 默认会话：`default`

### 响应清理

自动移除以下 UI 干扰：
- "Enter a prompt" / "Type your message" 提示
- "Share" / "Copy" / "Regenerate" 按钮
- 时间戳（如 "1.3s"）
- 多余空行

## 使用场景

### 1. 批量信息检索

```bash
# 批量分析新闻
for title in $(cat news-titles.txt); do
  curl -X POST http://localhost:19999/chat \
    -d "{\"prompt\":\"从投资角度分析：$title\",\"timeout\":60}"
done
```

### 2. 集成到 OpenClaw 技能

```python
# 在其他技能中调用 Gemini Bridge
import subprocess
import json

def ask_gemini(prompt, timeout=120):
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'http://localhost:19999/chat',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'prompt': prompt, 'timeout': timeout})
    ], capture_output=True, text=True)

    return json.loads(result.stdout)

# 使用
response = ask_gemini("分析一下特斯拉最新财报")
print(response['response'])
```

### 3. 远程调用

通过 SSH 转发端口：

```bash
# 在 Mac 上启动服务
python3 gemini_bridge.py --port 19999 --host 0.0.0.0

# 在远程机器上调用
curl -X POST http://your-mac-ip:19999/chat \
  -d '{"prompt":"你好"}'
```

## 与 Grok Bridge 对比

| 特性 | Grok Bridge | Gemini Bridge |
|------|-------------|---------------|
| 浏览器 | Safari | Chrome |
| 协议 | AppleScript JS | AppleScript JS |
| 多会话 | 否 | 是（通过 session_id）|
| 流式响应 | 否 | 否（计划中）|
| REST API | 是 | 是 |
| CLI 工具 | 是 | 是 |

## 已知限制

1. **需要 macOS**
   - 依赖 Chrome 的 AppleScript 支持
   - Linux/Windows 不支持

2. **需要 Chrome 保持运行**
   - 首次调用会自动启动 Chrome
   - 如果手动关闭，需要重新调用 `/new`

3. **不支持流式响应**
   - 当前版本是等待完整响应
   - 计划未来添加 SSE 支持

## 开发路线图

- [ ] 流式响应（Server-Sent Events）
- [ ] 多会话管理优化（标签页切换）
- [ ] 支持图片/文件上传
- [ ] 会话持久化（保存历史到文件）
- [ ] 错误重试机制

## 故障排查

### Chrome 不响应

检查权限：
```bash
# 系统设置 > 隐私与安全性 > 自动化
# 确保 "Google Chrome" 被允许
```

### 输入框未找到

```bash
# 检查 Chrome 是否在 gemini.google.com
curl http://localhost:19999/health

# 如果不在，手动导航一次：
open -a "Google Chrome" https://gemini.google.com
```

### 响应提取失败

检查 Gemini 页面是否正常加载，尝试手动刷新：
```bash
# 调用 /new 强制重新加载
curl -X POST http://localhost:19999/new
```

## 许可证

MIT
