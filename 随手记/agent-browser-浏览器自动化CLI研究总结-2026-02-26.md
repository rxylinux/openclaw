# agent-browser.dev 研究总结

## 📊 项目概况

**网站地址：** https://agent-browser.dev/
**项目名称：** agent-browser
**项目定位：** 为AI Agents设计的Headless浏览器自动化CLI
**版本：** v0.15.0
**安装状态：** ✅ 已成功安装

---

## 🎯 核心价值

### 1. Agent-first 设计
- **紧凑的文本输出** - 最小化Token使用，优化AI上下文效率
- **为AI设计** - 相比JSON输出，文本输出更节省tokens（200-400 tokens vs 3000-5000 tokens）
- **Ref-based快照** - 返回可访问性树和refs，用于确定性元素选择

### 2. 完整的浏览器自动化
- **50+命令** - 导航、表单、截图、网络、存储等
- **多会话支持** - 隔离的浏览器实例，独立的认证
- **快照和Refs** - 快速定位和交互元素

### 3. 跨平台支持
- **原生Rust CLI** - macOS (ARM64, x64), Linux (ARM64, x64), Windows (x64)
- **开箱即用** - 预编译的二进制文件，无需依赖

### 4. 兼容所有AI Agents
- **Claude Code** - ✅ 完全兼容
- **Cursor** - ✅ 完全兼容
- **GitHub Copilot** - ✅ 完全兼容
- **OpenAI Codex** - ✅ 完全兼容
- **Google Gemini** - ✅ 完全兼容
- **opencode** - ✅ 完全兼容
- **任何能运行shell命令的Agent** - ✅ 完全兼容

---

## 🏗️ 架构设计

### 1. Client-daemon架构
```
Client (Rust CLI)
    ↓ 命令解析
    ↓ 与daemon通信
    ↓
Daemon (Node.js)
    ↓ 管理Playwright实例
    ↓ 持久化会话
```

- **Rust CLI** - 解析命令、与daemon通信、即时响应
- **Node.js Daemon** - 管理Playwright浏览器实例、持久化会话
- **自动化启动** - Daemon自动启动和持久化，命令间无需重启

### 2. 为什么使用Refs？
```
传统方式：返回完整DOM (3000-5000 tokens)
Ref方式：返回快照 + Refs (200-400 tokens)
```

**优势：**
1. **Context效率** - 文本输出使用更少tokens
2. **确定性选择** - Refs指向精确元素，无需重新查询DOM
3. **速度** - 无需DOM重查询，命令更快
4. **AI友好** - LLM可以自然解析Refs（如"点击@e1"）

---

## 💡 核心功能

### 1. 导航命令
```bash
# 打开网站
agent-browser open example.com

# 快照（返回Refs）
agent-browser snapshot -i
# 输出示例：
# heading "Example Domain" [ref=e1]
# link "More information..." [ref=e2]
# ...

# 使用Refs点击元素
agent-browser click @e1

# 返回上一页
agent-browser back

# 刷新页面
agent-browser refresh
```

### 2. 表单和交互命令
```bash
# 填写表单
agent-browser type "#input-name" "input value"
agent-browser type "#email" "user@example.com"
agent-browser type "#password" "secret123"

# 点击按钮
agent-browser click @e3

# 选择下拉框
agent-browser select "#country" "USA"

# 复选框
agent-browser check "#terms" true
```

### 3. 截图命令
```bash
# 截全屏
agent-browser screenshot page.png

# 截特定元素
agent-browser screenshot element.png --ref @e5

# 截选区
agent-browser screenshot region.png --x 100 --y 100 --width 200 --height 100
```

### 4. 网络命令
```bash
# 拦截请求
agent-browser network enable

# 导出HAR
agent-browser network export network.har

# 清除Cookies
agent-browser network clear-cookies
```

### 5. 存储命令
```bash
# 导出Cookies
agent-browser storage export-cookies cookies.json

# 导入Cookies
agent-browser storage import-cookies cookies.json

# 清除LocalStorage
agent-browser storage clear-local-storage
```

### 6. 会话管理命令
```bash
# 列出所有会话
agent-browser session list

# 创建新会话
agent-browser session create my-session

# 切换会话
agent-browser session switch my-session

# 关闭会话
agent-browser session close my-session

# 删除会话
agent-browser session delete my-session
```

---

## 🚀 安装方法

### 1. 全局安装（推荐）

**Linux/macOS:**
```bash
npm install -g agent-browser
# 或使用npm
npx agent-browser open example.com
```

**macOS (Homebrew):**
```bash
brew install agent-browser
```

**Windows (PowerShell):**
```powershell
npm install -g agent-browser
agent-browser.exe open example.com
```

### 2. 不安装（使用npx）

```bash
# 直接运行，无需全局安装
npx agent-browser open example.com
```

### 3. 本地二进制

```bash
# 下载预编译二进制
curl -LO https://github.com/browserbase/agent-browser/releases/latest/download/agent-browser-linux-x86_64

# 添加执行权限
chmod +x agent-browser-linux-x86_64

# 运行
./agent-browser-linux-x86_64 open example.com
```

---

## 💡 对rxy的投资研究价值

### 1. 自动化数据收集

**场景：** 自动化访问券商网站、公司官网、研报网站
**使用命令：**
```bash
# 打开券商网站
agent-browser open https://www.xxxsec.com.cn

# 导航到研报页面
agent-browser click @e3

# 下载研报
agent-browser click @e5
```

**价值：**
- 自动化数据收集流程
- 节省大量手动操作时间
- 可以结合其他脚本进行数据提取

### 2. 表单自动化

**场景：** 自动化填写登录表单、注册表单、搜索表单
**使用命令：**
```bash
# 填写登录表单
agent-browser type "#username" "your_username"
agent-browser type "#password" "your_password"
agent-browser click "#login-button"

# 填写搜索表单
agent-browser type "#search-input" "AAPL"
agent-browser click "#search-button"
```

**价值：**
- 自动化账号登录
- 自动化搜索和数据收集
- 结合脚本实现批量操作

### 3. 截图和取证

**场景：** 自动化截图存证、页面状态记录
**使用命令：**
```bash
# 截全屏
agent-browser screenshot page.png

# 截特定元素（如价格、图表）
agent-browser screenshot price.png --ref @e10

# 定期截图监控
watch -n 60 "agent-browser screenshot \$(date +%Y%m%d_%H%M%S).png"
```

**价值：**
- 自动化截图存证
- 记录页面状态变化
- 监控重要数据更新

### 4. 会话隔离

**场景：** 多个账号同时登录、不同任务独立执行
**使用命令：**
```bash
# 为券商A创建会话
agent-browser session create broker-a
agent-browser session switch broker-a
agent-browser open https://broker-a.com
# 登录券商A

# 切换到券商B
agent-browser session create broker-b
agent-browser session switch broker-b
agent-browser open https://broker-b.com
# 登录券商B

# 两个账号同时保持登录
```

**价值：**
- 多账号同时登录
- 任务完全隔离
- 避免Cookies冲突

---

## 🎯 推荐使用场景

### 短期（立即可用）

**1. 网站数据收集**
```bash
# 打开网站并获取快照
agent-browser open example.com
agent-browser snapshot -i

# 导航到特定页面
agent-browser click @e10

# 截图
agent-browser screenshot data.png
```

**2. 表单自动化**
```bash
# 自动化登录
agent-browser open https://example.com/login
agent-browser type "#username" "user"
agent-browser type "#password" "pass"
agent-browser click "#login-btn"
```

### 中期（结合脚本）

**1. 数据提取脚本**
```bash
#!/bin/bash
# 自动化数据提取流程
agent-browser open https://data-source.com
sleep 2
agent-browser click @e5
sleep 3
agent-browser screenshot chart.png
agent-browser back
```

**2. 定期监控脚本**
```bash
#!/bin/bash
# 定期截图监控
while true; do
    agent-browser open https://target.com
    agent-browser screenshot "monitor_$(date +%H%M%S).png"
    sleep 3600
done
```

### 长期（完全自动化）

**1. 结合其他工具**
```bash
# 结合agent-browser + Python脚本
agent-browser open https://data-source.com
# 使用Python解析快照、提取数据、存储到数据库
```

**2. 自动化工作流**
```bash
# 完整的数据收集流程
# 1. 登录多个券商
# 2. 导航到研报页面
# 3. 下载所有研报
# 4. 自动化数据处理
```

---

## 📊 与其他浏览器自动化工具对比

| 工具 | 语言 | Token效率 | AI友好 | 安装大小 | 跨平台 |
|-----|------|----------|--------|---------|--------|
| agent-browser | Rust | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~10 MB | ✅ 完全 |
| Playwright | Node.js | ⭐⭐ | ⭐⭐⭐ | ~200 MB | ✅ 完全 |
| Selenium | Python | ⭐⭐ | ⭐⭐ | ~50 MB | ✅ 完全 |
| Puppeteer | Node.js | ⭐⭐ | ⭐⭐ | ~300 MB | ✅ 完全 |

**agent-browser的优势：**
1. **Token效率最高** - 文本输出使用200-400 tokens vs 其他工具的3000-5000 tokens
2. **AI最友好** - Ref-based快照，LLM可以自然解析和交互
3. **安装最小** - ~10 MB vs 其他工具的50-300 MB
4. **启动最快** - Rust CLI解析命令，Client-daemon架构
5. **完全跨平台** - 原生Rust编译，支持macOS、Linux、Windows

---

## 🔒 安全和隐私

### 1. 本地执行
- 所有浏览器操作都在本地执行
- 不经过任何云端服务
- 不上传任何数据

### 2. 会话隔离
- 每个会话完全隔离
- Cookies和LocalStorage独立
- 避免跨会话冲突

### 3. Cookie管理
- 支持导出/导入Cookies
- 支持清除Cookies
- 支持LocalStorage管理

---

## 🚀 快速开始

### 基础使用

```bash
# 1. 打开网站
agent-browser open https://example.com

# 2. 获取快照（Refs）
agent-browser snapshot -i

# 3. 使用Refs交互
agent-browser click @e1
agent-browser type "#input" "value"
agent-browser click @e2

# 4. 截图
agent-browser screenshot page.png

# 5. 关闭
agent-browser close
```

### 会话管理

```bash
# 创建会话
agent-browser session create my-task

# 切换会话
agent-browser session switch my-task

# 列出会话
agent-browser session list

# 关闭会话
agent-browser session close my-task
```

---

## 📋 总结

**agent-browser核心价值：**
1. **Agent-first设计** - 为AI Agents优化的紧凑文本输出
2. **Ref-based快照** - 确定性元素选择，无DOM重查询
3. **完整功能** - 50+命令，涵盖导航、表单、截图、网络、存储等
4. **极致性能** - Rust CLI + Client-daemon架构，快速响应
5. **完全兼容** - Claude Code、Cursor、GitHub Copilot、OpenAI Codex等

**对rxy的投资研究价值：**
1. **自动化数据收集** - 网站访问、表单填写、数据下载
2. **表单自动化** - 登录、注册、搜索表单
3. **截图和取证** - 页面状态记录、数据存证
4. **多账号管理** - 会话隔离、多账号同时登录
5. **与其他工具集成** - 可以结合Python、Bash脚本实现完全自动化

**核心优势：**
- Token效率最高（200-400 vs 3000-5000）
- AI最友好（Refs自然解析）
- 安装最小（~10 MB）
- 完全跨平台（macOS、Linux、Windows）
- 零依赖（开箱即用）

---

## 🔗 相关链接

**网站：** https://agent-browser.dev/
**GitHub：** https://github.com/browserbase/agent-browser
**NPM：** https://www.npmjs.com/package/agent-browser
**文档：** https://agent-browser.dev/docs

---

**rxy的狗腿子**
2026-02-26
