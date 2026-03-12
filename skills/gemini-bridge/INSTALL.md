# Gemini Bridge 安装指南

## 前置条件

1. **macOS**（10.15+）
2. **Google Chrome**（最新版本）
3. **Python 3.8+**

## 安装步骤

### 1. 设置 Chrome 权限

**重要：必须完成此步骤，否则无法运行**

```bash
# 打开系统设置
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"

# 或者手动操作：
# 1. 打开 "系统设置" > "隐私与安全性" > "自动化"
# 2. 找到 "Google Chrome"
# 3. 勾选允许
```

### 2. 登录 Gemini

```bash
# 在 Chrome 中打开 Gemini
open -a "Google Chrome" https://gemini.google.com

# 登录你的 Google 账户
```

### 3. 测试服务

```bash
# 启动服务
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py

# 在另一个终端测试
curl http://localhost:19999/health
```

预期输出：
```json
{
  "status": "ok",
  "url": "https://gemini.google.com",
  "on_gemini": true,
  "version": "v1"
}
```

### 4. 发送第一条消息

```bash
curl -X POST http://localhost:19999/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好","timeout":60}'
```

## 启动服务

### 前台运行（测试）

```bash
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py
```

### 后台运行（生产）

```bash
# 使用 nohup
nohup python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py \
  > /var/log/gemini-bridge.log 2>&1 &

# 或使用 tmux
tmux new -s gemini-bridge
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py
# Ctrl+B, D 分离会话
```

### 指定端口

```bash
python3 gemini_bridge.py --port 19999
python3 gemini_bridge.py --port 8080 --host 0.0.0.0  # 允许外部访问
```

## 验证安装

### 健康检查

```bash
curl http://localhost:19999/health
```

### 发送测试消息

```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"1+1等于几？"}'
```

### 使用 CLI 工具

```bash
bash /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_chat.sh "你好 Gemini"
```

## 故障排查

### 问题 1：权限被拒绝

**错误信息：**
```
osascript: execution error: Google Chrome got an error: not allowed to send events
```

**解决方案：**
1. 打开 "系统设置" > "隐私与安全性" > "自动化"
2. 确保 "Google Chrome" 被勾选
3. 如果仍未生效，重启 Chrome

### 问题 2：Chrome 未响应

**错误信息：**
```
{'status': 'error', 'error': 'chrome not reachable'}
```

**解决方案：**
```bash
# 手动启动 Chrome
open -a "Google Chrome"

# 导航到 Gemini
open -a "Google Chrome" https://gemini.google.com

# 重试
curl http://localhost:19999/health
```

### 问题 3：输入框未找到

**错误信息：**
```
{'status': 'error', 'error': 'input not found'}
```

**解决方案：**
```bash
# 重新加载 Gemini 页面
curl -X POST http://localhost:19999/new

# 或手动刷新 Chrome 中的 Gemini 页面
```

### 问题 4：响应提取失败

**现象：** 响应为空或包含 UI 元素

**解决方案：**
1. 检查 Gemini 页面是否正常加载
2. 手动在浏览器中发送一条消息，确保功能正常
3. 如果问题持续，尝试清理 Chrome 缓存

### 问题 5：端口被占用

**错误信息：**
```
OSError: [Errno 48] Address already in use
```

**解决方案：**
```bash
# 查找占用端口的进程
lsof -i :19999

# 杀死进程
kill -9 <PID>

# 或使用其他端口
python3 gemini_bridge.py --port 19998
```

## 高级配置

### 修改端口

```bash
python3 gemini_bridge.py --port 8080
```

### 允许外部访问

```bash
python3 gemini_bridge.py --host 0.0.0.0 --port 19999
```

注意：允许外部访问时，请确保：
1. 使用防火墙限制访问
2. 在局域网内使用
3. 不要暴露到公网

### 配置开机自启动

创建 `~/Library/LaunchAgents/com.geminibridge.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.geminibridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py</string>
        <string>--port</string>
        <string>19999</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/gemini-bridge.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/gemini-bridge.error.log</string>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.geminibridge.plist
```

## 卸载

### 停止服务

```bash
# 查找进程
ps aux | grep gemini_bridge

# 杀死进程
kill <PID>

# 如果使用 launchctl
launchctl unload ~/Library/LaunchAgents/com.geminibridge.plist
```

### 移除文件

```bash
# 移除服务文件
rm ~/Library/LaunchAgents/com.geminibridge.plist

# 移除日志
rm /var/log/gemini-bridge.log /var/log/gemini-bridge.error.log
```

## 下一步

安装完成后，查看使用示例：

```bash
cat /root/.openclaw/workspace/skills/gemini-bridge/EXAMPLES.md
```

或查看 API 文档：

```bash
cat /root/.openclaw/workspace/skills/gemini-bridge/SKILL.md
```
