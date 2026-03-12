# Gemini Bridge 项目总结

## 项目结构

```
gemini-bridge/
├── scripts/
│   ├── gemini_bridge.py  # 核心服务（REST API）
│   ├── gemini_chat.sh    # CLI 工具
│   └── test.sh          # 测试脚本
├── SKILL.md             # OpenClaw 技能定义
├── README.md            # 项目说明
├── INSTALL.md           # 安装指南
├── EXAMPLES.md          # 使用示例
└── PROJECT_SUMMARY.md   # 本文件
```

## 核心功能

### 1. REST API 服务

**文件：** `scripts/gemini_bridge.py`

**特性：**
- ✅ 多线程处理（支持并发请求）
- ✅ 多会话管理（通过 session_id）
- ✅ 零依赖（仅用 Python stdlib）
- ✅ AppleScript + JS 注入（零额外权限）
- ✅ 响应稳定性检测（轮询 DOM 直到稳定）

**API 端点：**
- `POST /chat` - 发送聊天请求
- `POST /new` - 创建新会话
- `GET /health` - 健康检查
- `GET /history` - 读取历史

### 2. CLI 工具

**文件：** `scripts/gemini_chat.sh`

**用法：**
```bash
bash gemini_chat.sh "你的问题" [--timeout 60] [--session default]
```

### 3. 测试脚本

**文件：** `test.sh`

**功能：**
- 检查前置条件
- 启动服务
- 测试所有 API 端点
- 生成测试报告

## 技术方案

### AppleScript + JS 注入

```python
# 执行 JavaScript
def _js(self, js, timeout=30):
    esc = js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return self._osa(
        f'tell application "Google Chrome" to do JavaScript "{esc}" in current tab of front window',
        timeout
    )
```

### 输入文本

```python
# 绕过 React 受控组件
document.execCommand('insertText', false, 'your text')
```

### 提交请求

```python
# JS 点击发送按钮
document.querySelector('button[aria-label*="send"]').click()
```

### 响应提取

```python
# 轮询 DOM 直到稳定
if body != body_before and body == last:
    stable += 1
    if stable >= 3:
        return response
```

## 与 Grok Bridge 对比

| 特性 | Grok Bridge | Gemini Bridge |
|------|-------------|---------------|
| 浏览器 | Safari | Chrome |
| 多会话 | ❌ | ✅（通过 session_id）|
| 流式响应 | ❌ | ❌（计划中）|
| 多线程 | ✅ | ✅ |
| 零依赖 | ✅ | ✅ |
| AppleScript | ✅ | ✅ |
| 文档 | 简洁 | 详细（示例多）|

## 使用场景

### 1. 投资分析
- 批量分析股票
- 新闻摘要
- 定期复盘

### 2. 信息检索
- 批量查询
- 文档分析
- 知识库问答

### 3. 自动化集成
- OpenClaw 技能
- 定时任务
- Web 服务

## 文档体系

1. **README.md** - 项目概述、快速开始
2. **SKILL.md** - 详细 API 文档、技术细节
3. **INSTALL.md** - 安装指南、故障排查
4. **EXAMPLES.md** - 丰富的使用示例
5. **PROJECT_SUMMARY.md** - 项目总结（本文件）

## 快速开始

### 1. 设置权限
```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"
# 勾选 "Google Chrome"
```

### 2. 启动服务
```bash
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py
```

### 3. 测试
```bash
bash /root/.openclaw/workspace/skills/gemini-bridge/test.sh
```

### 4. 使用
```bash
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"你好"}'
```

## 已知限制

1. **仅支持 macOS**
   - 依赖 Chrome 的 AppleScript 支持
   - Linux/Windows 不支持

2. **需要 Chrome 保持运行**
   - 首次调用会自动启动
   - 如果手动关闭，需要重新调用 `/new`

3. **不支持流式响应**
   - 当前版本等待完整响应
   - 计划未来添加 SSE

4. **依赖网络**
   - 需要 Google 账户登录
   - 需要稳定的网络连接

## 开发路线图

### v1.1（短期）
- [ ] 添加错误重试机制
- [ ] 优化响应清理逻辑
- [ ] 支持更多 Gemini 功能

### v2.0（中期）
- [ ] 流式响应（SSE）
- [ ] 多标签页管理
- [ ] 会话持久化

### v3.0（长期）
- [ ] 支持 Linux（通过 Chrome Remote Debugging）
- [ ] 支持图片/文件上传
- [ ] WebSocket 双向通信

## 贡献指南

### 代码风格
- 遵循 PEP 8
- 使用类型注解
- 添加文档字符串

### 测试
- 新功能必须添加测试
- 测试覆盖率 > 80%
- 手动测试所有 API

### 文档
- 更新 README.md
- 添加 EXAMPLES.md 示例
- 更新版本号

## 许可证

MIT License

## 致谢

- Grok Bridge - 架构灵感来源
- Chrome DevTools Protocol - 技术基础
- AppleScript - macOS 自动化支持

---

**版本：** v1.0
**创建日期：** 2026-03-10
**作者：** rxy的狗腿子
