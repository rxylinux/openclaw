# Gemini Bridge - 跨平台版本

通过浏览器自动化与 Google Gemini 对话的 HTTP API 桥接器。

## 两个版本

### macOS 版本: `gemini_bridge.py`
- **使用**: AppleScript + Apple Events
- **系统要求**: macOS + Chrome 浏览器
- **特点**:
  - 利用 macOS 原生自动化能力
  - 无需额外依赖
  - 直接控制已打开的 Chrome 窗口

### Linux 版本: `gemini_bridge_linux.py` ✨ 新增
- **使用**: Playwright + Chromium
- **系统要求**: Linux/Windows + Python 3.8+
- **特点**:
  - 跨平台兼容（Linux/Windows/macOS）
  - 支持无头模式（后台运行）
  - 自动管理浏览器上下文
  - 独立运行，不影响现有浏览器

---

## 快速开始

### macOS 用户

```bash
# 1. 允许 Chrome 自动化（系统设置 > 隐私与安全性 > 自动化）
# 2. 在 Chrome 中登录 gemini.google.com
# 3. 运行
python3 gemini_bridge.py --port 19999
```

### Linux 用户

```bash
# 1. 安装依赖（首次）
pip install playwright
playwright install chromium

# 2. 测试环境
bash test_gemini_bridge_linux.sh

# 3. 启动服务器
python3 gemini_bridge_linux.py --port 19999
```

首次运行时，浏览器会自动打开 gemini.google.com，请手动登录 Google 账号。

---

## API 端点

### POST `/chat`
发送聊天请求

```bash
curl -X POST http://localhost:19999/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "你好",
    "timeout": 120,
    "session_id": "optional"
  }'
```

**参数:**
- `prompt` (必需): 发送给 Gemini 的文本
- `timeout` (可选): 超时时间，默认 120 秒
- `session_id` (可选): 会话 ID，不提供则使用默认会话

**响应:**
```json
{
  "status": "ok",
  "response": "Gemini 的回复",
  "elapsed": 15.3
}
```

### GET `/health`
健康检查

```bash
curl http://localhost:19999/health
```

**响应:**
```json
{
  "status": "ok",
  "url": "https://gemini.google.com/...",
  "on_gemini": true,
  "version": "v1-linux",
  "browser": "chromium"
}
```

### GET `/history`
获取当前会话历史

```bash
curl http://localhost:19999/history
```

**响应:**
```json
{
  "status": "ok",
  "content": "对话内容...",
  "raw_length": 1234
}
```

### POST `/new`
创建新会话

```bash
curl -X POST http://localhost:19999/new
```

**响应:**
```json
{
  "status": "ok",
  "session_id": "abc12345"
}
```

---

## 命令行参数

```bash
python3 gemini_bridge_linux.py [选项]

选项:
  --port PORT      HTTP 服务端口 (默认: 19999)
  --host HOST      监听地址 (默认: 127.0.0.1)
  --headless       无头模式，不显示浏览器窗口
```

---

## Linux 版本高级用法

### 无头模式（后台运行）

```bash
python3 gemini_bridge_linux.py --headless &
```

适合服务器环境，无需图形界面。

### 会话管理

```bash
# 使用指定会话 ID
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"问题1", "session_id":"work"}'

curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"问题2", "session_id":"work"}'
```

不同 `session_id` 会保持独立的对话上下文。

---

## 故障排查

### Linux 版本

**Q: 提示 "chromium not found"**
```bash
python3 -m playwright install chromium
```

**Q: 浏览器启动失败**
```bash
# 检查系统依赖
# Ubuntu/Debian
sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

**Q: 无法保持登录状态**
- 首次运行使用有头模式（不加 `--headless`）
- 手动登录 Google 账号
- 后续会话会自动使用已保存的 cookies

### macOS 版本

**Q: 提示 "chrome not reachable"**
- 检查系统设置 > 隐私与安全性 > 自动化
- 确保 "Google Chrome" 已被勾选

---

## 版本对比

| 特性 | macOS 版本 | Linux 版本 |
|------|-----------|-----------|
| 系统要求 | macOS | Linux/Windows/macOS |
| 依赖 | 无 | Playwright |
| 无头模式 | ❌ | ✅ |
| 多会话 | ✅ | ✅ |
| 资源占用 | 低 | 中 |
| 稳定性 | 依赖系统 | 独立运行 |
| 安装难度 | 简单 | 需要安装依赖 |

---

## 技术细节

### macOS 版本原理
- 使用 AppleScript 的 `do JavaScript` 命令
- 直接在 Chrome 当前标签页注入 JS
- 通过 DOM 操作实现自动化

### Linux 版本原理
- 使用 Playwright 启动独立 Chromium 实例
- 通过 Playwright API 进行 DOM 操作和事件模拟
- 自动等待元素就绪，更稳定可靠

---

## 许可

MIT License
