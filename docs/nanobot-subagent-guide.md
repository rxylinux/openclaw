# Nanobot 子 Agent 使用指南

## 什么是 Nanobot？

Nanobot 是一个轻量级的个人 AI 助手框架（约 4000 行代码），受 OpenClaw 启发但更加精简。

## 安装状态

✅ 已安装到虚拟环境：`/root/.nanobot-env`
✅ 版本：v0.1.4.post2
✅ 配置文件：`/root/.nanobot/config.json`
✅ 工作空间：`/root/.nanobot/workspace`
✅ 启动脚本：`/root/.openclaw/workspace/scripts/nanobot-runner.sh`

## 当前配置

- **模型**: zai/glm-4.7
- **提供商**: custom (自定义 API)
- **工作空间**: ~/.nanobot/workspace
- **最大令牌**: 8192
- **温度**: 0.1

## 如何使用

### 1. 直接命令行调用

```bash
# 发送单条消息
/root/.openclaw/workspace/scripts/nanobot-runner.sh -m "你好，介绍一下你自己"

# 使用启动脚本
bash /root/.openclaw/workspace/scripts/nanobot-runner.sh -m "帮我分析一下最近的科技新闻"
```

### 2. 交互式对话

```bash
# 进入交互模式
/root/.nanobot-env/bin/nanobot

# 然后可以直接输入对话内容
```

### 3. 作为子 Agent 调用（推荐）

你可以让主 agent 调用 nanobot 来处理特定任务：

```python
# 在 OpenClaw 中使用 sessions_spawn 调用
sessions_spawn(
    task="使用 nanobot 分析：[具体任务]",
    agentId="nanobot",
    label="nanobot-subagent"
)
```

## API 密钥配置

当前 nanobot 配置使用的是自定义 API 端点，需要配置正确的 API 密钥才能使用。

### 方法 1：使用 OpenRouter（推荐）

OpenRouter 支持多个模型提供商，一个 API key 就可以访问多个模型。

1. 获取 API Key: https://openrouter.ai/keys
2. 编辑配置文件：
   ```bash
   nano /root/.nanobot/config.json
   ```
3. 修改 providers 部分：
   ```json
   {
     "providers": {
       "openrouter": {
         "apiKey": "your-openrouter-api-key"
       }
     },
     "agents": {
       "defaults": {
         "model": "anthropic/claude-sonnet",
         "provider": "openrouter"
       }
     }
   }
   ```

### 方法 2：使用本地 vLLM

如果你有本地部署的 LLM 模型，可以配置 nanobot 使用它：

```json
{
  "providers": {
    "vllm": {
      "apiBase": "http://localhost:8000/v1",
      "apiKey": "dummy"
    }
  },
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct",
      "provider": "vllm"
    }
  }
}
```

## 支持的任务类型

Nanobot 支持以下类型的功能：

1. **对话交互** - 自然语言对话
2. **Web 搜索** - 联网搜索（需要配置 API key）
3. **文件操作** - 读取、写入文件
4. **代码执行** - 执行 shell 命令
5. **记忆管理** - 记住上下文信息

## 与 OpenClaw 的区别

| 特性 | OpenClaw | Nanobot |
|------|----------|---------|
| 代码量 | ~数十万行 | ~4000 行 |
| 复杂度 | 高（企业级） | 低（个人级） |
| 功能 | 全功能 | 核心功能 |
| 资源占用 | 较高 | 较低 |
| 适用场景 | 生产环境、企业部署 | 个人使用、快速开发 |

## 使用建议

### 适合使用 Nanobot 的场景：

1. 快速原型开发
2. 学习 AI 智能体原理
3. 资源受限的环境
4. 需要"轻量级"助手进行特定任务

### 适合使用 OpenClaw 的场景：

1. 生产环境部署
2. 需要完整功能
3. 复杂的多步骤任务
4. 企业级应用

## 故障排除

### 问题：连接错误

**原因**: API 密钥未配置或无效

**解决**: 检查 `~/.nanobot/config.json` 中的 API 密钥配置

### 问题：模型不可用

**原因**: 模型名称或提供商配置错误

**解决**: 检查配置文件中的 `model` 和 `provider` 字段

### 问题：权限错误

**原因**: 虚拟环境未激活或脚本权限不足

**解决**:
```bash
chmod +x /root/.openclaw/workspace/scripts/nanobot-runner.sh
source /root/.nanobot-env/bin/activate
```

## 更多资源

- Nanobot GitHub: https://github.com/HKUDS/nanobot
- Nanobot 文档: https://github.com/HKUDS/nanobot#readme
- OpenRouter: https://openrouter.ai

## 更新记录

- 2026-03-05: 初始安装和配置完成
