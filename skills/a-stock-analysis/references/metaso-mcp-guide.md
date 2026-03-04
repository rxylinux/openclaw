# 秘塔AI搜索 MCP 服务器配置指南

## 📋 概述

秘塔AI搜索（Metaso）是一款基于AI的智能搜索引擎，提供无广告、高质量的搜索体验。通过MCP（Model Context Protocol）集成，可以让AI助手拥有强大的联网搜索能力。

### 秘塔AI搜索特性

| 特性 | 说明 |
|------|------|
| **无广告** | 干净的搜索体验 |
| **AI整理** | 自动整理结构化结果 |
| **多种模式** | 简洁、深入、研究三种搜索模式 |
| **多模态输出** | 思维导图、大纲、表格 |
| **信息溯源** | 所有信息来源均标注 |

---

## 🚀 配置步骤

### 方法1：通过 ModelScope MCP 广场配置（推荐）

1. **访问 ModelScope MCP 广场**
   - 网址：https://www.modelscope.cn/mcp
   - 搜索：metaso 或 秘塔

2. **找到秘塔AI搜索服务器**
   - 服务器名称：metaso-search
   - 或者直接访问：https://www.modelscope.cn/mcp/servers/metasota/metaso-search

3. **获取配置信息**
   - 查看「使用指南」或「配置说明」
   - 复制 MCP 配置 JSON

4. **添加到 Claude Desktop 配置**
   ```bash
   # macOS 配置路径
   ~/Library/Application Support/Claude/claude_desktop_config.json

   # Windows 配置路径
   %APPDATA%\Claude\claude_desktop_config.json
   ```

---

### 方法2：手动配置 MCP 服务器

#### Claude Desktop 配置

编辑配置文件：
```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

添加以下配置：

```json
{
  "mcpServers": {
    "metaso-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelscope/mcp-server-metaso-search"
      ],
      "env": {
        "METASO_API_KEY": "your_metaso_api_key_here"
      }
    }
  }
}
```

#### Cursor/Windsurf 配置

在设置中添加 MCP 服务器：

```json
{
  "mcpServers": {
    "metaso-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelscope/mcp-server-metaso-search"
      ],
      "env": {
        "METASO_API_KEY": "your_metaso_api_key_here"
      }
    }
  }
}
```

---

## 🔑 获取秘塔API密钥

### 步骤1：注册账号

1. 访问秘塔AI搜索官网：https://metaso.cn
2. 注册账号并登录

### 步骤2：申请API密钥

1. 进入「开发者中心」或「API管理」
2. 申请API密钥
3. 复制密钥备用

### 步骤3：配置环境变量（可选）

```bash
# 添加到 ~/.zshrc (Oh My Zsh)
echo 'export METASO_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc

# 或添加到 ~/.bash_profile (Bash)
echo 'export METASO_API_KEY=your_api_key_here' >> ~/.bash_profile
source ~/.bash_profile
```

---

## 📖 使用示例

### 在 Claude Desktop 中使用

配置完成后，重启 Claude Desktop，然后可以直接对话：

```
用户：帮我搜索一下双环传动(002472)的最新新闻

Claude：[调用 metaso-search 工具]
搜索到以下最新新闻：
1. 双环传动发布2024年业绩预告...
2. 双环传动子公司上市申请获受理...
3. ...
```

### 在代码中使用（Python示例）

```python
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 秘塔搜索 MCP 服务器参数
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelscope/mcp-server-metaso-search"],
    env={
        "METASO_API_KEY": os.getenv("METASO_API_KEY")
    }
)

async def search_with_metaso(query):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 调用搜索工具
            result = await session.call_tool("metaso_search", {
                "query": query,
                "search_mode": "comprehensive"  # 简洁/深入/研究
            })

            return result

# 使用
import asyncio
results = asyncio.run(search_with_metaso("双环传动 最新财报"))
```

---

## 🛠️ 可用工具

### metaso_search

执行AI驱动的网络搜索。

**参数：**
- `query` (string, 必需): 搜索关键词
- `search_mode` (string, 可选): 搜索模式
  - `simple`: 简洁模式 - 快速获取核心信息
  - `deep`: 深入模式 - 详细分析和更多结果
  - `research`: 研究模式 - 全面深入的研究报告
- `result_type` (string, 可选): 结果类型
  - `text`: 文字结果
  - `mindmap`: 思维导图
  - `outline`: 大纲
  - `table`: 信息表格

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "query": "双环传动 基本信息",
    "summary": "浙江双环传动机械股份有限公司是一家...",
    "sources": [
      {
        "title": "双环传动公司简介",
        "url": "https://...",
        "snippet": "..."
      }
    ],
    "mindmap": "...",
    "outline": "..."
  }
}
```

---

## ⚙️ 高级配置

### 自定义搜索参数

```json
{
  "mcpServers": {
    "metaso-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelscope/mcp-server-metaso-search"
      ],
      "env": {
        "METASO_API_KEY": "your_api_key",
        "METASO_SEARCH_MODE": "deep",
        "METASO_MAX_RESULTS": "20"
      }
    }
  }
}
```

### 使用代理（可选）

```bash
# 设置代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

---

## 🔧 故障排除

### 问题1：MCP服务器启动失败

**解决方案：**
```bash
# 检查 Node.js 版本
node --version  # 需要 v16 或更高

# 手动测试MCP服务器
npx -y @modelscope/mcp-server-metaso-search

# 检查API密钥
echo $METASO_API_KEY
```

### 问题2：搜索返回错误

**解决方案：**
1. 确认API密钥有效
2. 检查网络连接
3. 查看秘塔AI官网获取最新API文档

### 问题3：配置文件不生效

**解决方案：**
```bash
# macOS: 检查配置文件路径
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 验证JSON格式
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python3 -m json.tool

# 重启 Claude Desktop
killall Claude && open -a Claude
```

---

## 📊 与其他搜索引擎对比

| 特性 | 秘塔AI搜索 | 博查API | 百度搜索 |
|------|-----------|---------|----------|
| **AI整合** | ✅ 强 | ✅ 强 | ❌ 弱 |
| **无广告** | ✅ | ✅ | ❌ |
| **多模态输出** | ✅ | ❌ | ❌ |
| **思维导图** | ✅ | ❌ | ❌ |
| **信息溯源** | ✅ | ✅ | ✅ |
| **API价格** | 待确认 | 免费+付费 | 企业认证 |
| **中文支持** | ✅ 优秀 | ✅ 优秀 | ✅ 优秀 |

---

## 💡 最佳实践

### 1. 选择合适的搜索模式

```javascript
// 快速获取信息
search_mode: "simple"  // 用于简单问答

// 深度分析
search_mode: "deep"    // 用于股票分析、行业研究

// 全面研究
search_mode: "research" // 用于投资决策、深度报告
```

### 2. 结合其他工具

```javascript
// 秘塔搜索 + AkShare
metaso_search("双环传动 最新财报")  // 获取新闻和解读
+ akshare_stock_financial("002472")  // 获取财务数据
= 完整的股票分析报告
```

### 3. 定期更新API密钥

```bash
# 检查密钥有效期
curl -H "Authorization: Bearer $METASO_API_KEY" \
     https://api.metaso.cn/v1/status
```

---

## 📚 相关资源

- **秘塔AI搜索官网**: https://metaso.cn
- **ModelScope MCP广场**: https://www.modelscope.cn/mcp
- **MCP官方文档**: https://modelcontextprotocol.io
- **Claude Desktop文档**: https://docs.anthropic.com/claude/docs/mcp

---

## 📝 更新日志

- **2026-02-23**: 初始版本，创建秘塔AI搜索MCP配置指南

---

**最后更新**: 2026-02-23
**维护者**: Claude Sonnet 4.6

## MCP配置示例

### 秘塔搜索配置
```json
{
  "mcpServers": {
    "metaso-search": {
      "command": "npx",
      "args": ["-y", "@modelscope/mcp-server-metaso-search"],
      "env": {
        "METASO_API_KEY": "your_metaso_api_key_here"
      }
    }
  }
}
```
