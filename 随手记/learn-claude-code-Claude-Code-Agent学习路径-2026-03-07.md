# learn-claude-code 项目研究总结

**项目地址:** https://github.com/shareAI-lab/learn-claude-code
**研究日期:** 2026-03-07
**作者:** shareAI-lab
**定位:** 从0到1的Claude Code Agent学习项目

---

## 🎯 项目概述

### Slogan
> "Bash is all you need - A nano Claude Code–like agent, built from 0 to 1"

### 核心目标
通过12个渐进式session，从零开始构建一个类似Claude Code的AI Agent。

**设计理念:**
- Mental-Model-First文档（问题-方案-图表-最简代码）
- 每个session添加一个机制，但保持主循环不变
- 从简单循环到自主执行，渐进式演进

---

## 🔄 核心模式：Agent循环

### 最小Agent模式
```python
def agent_loop(messages):
    while True:
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS,
        )
        messages.append({
            "role": "assistant",
            "content": response.content
        })
        
        if response.stop_reason != "tool_use":
            return
        
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = TOOL_HANDLERS[block.name](**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({
            "role": "user", 
            "content": results
        })
```

**核心:** 每个session在这个循环上叠加一层机制，不改变循环本身。

---

## 📚 12个Session学习路径

### Phase 1: THE LOOP & 基础工具
**目标:** 理解Agent最基础的运行机制

#### S01: The Agent Loop
**Motto:** "One loop & Bash is all you need"
- 一个工具 + 一个循环 = Agent
- 停止条件：`stop_reason != "tool_use"`
- 工具结果追加到messages

#### S02: Tool Use
**Motto:** "Adding a tool means adding one handler"
- 保持循环不变
- 新工具注册到dispatch map
- 动态工具分发

#### S03: TodoWrite
**Motto:** "An agent without a plan drifts"
- 添加TodoManager工具
- while循环 + 定时提醒
- 防止Agent漂移

#### S04: Subagents
**Motto:** "Break big tasks down; each subtask gets a clean context"
- 为每个子任务创建fresh messages[]
- dispatch map: name->handler
- 独立上下文，主对话保持清晰

#### S05: Skills
**Motto:** "Load knowledge when you need it, not upfront"
- 通过tool_result注入SKILL.md
- 不在system prompt中加载所有知识
- 按需获取，节省上下文

#### S06: Context Compact
**Motto:** "Context will fill up; you need a way to make room"
- 3层压缩策略：
  1. 压缩工具调用结果
  2. 合并相似消息
  3. 移除已完成任务上下文
- 适配无限session

---

### Phase 2: PLANNING & KNOWLEDGE
**目标:** 添加规划能力和知识管理

#### S07: Task System
**Motto:** "Break big goals into small tasks, order them, persist to disk"
- 基于文件的任务CRUD
- 依赖图管理
- 为多Agent协作打基础

#### S08: Background Tasks
**Motto:** "Run slow operations in background; agent keeps thinking"
- daemon线程执行命令
- 完成后注入通知到queue
- Agent继续思考，不阻塞

---

### Phase 3: PERSISTENCE & TEAMS
**目标:** 持久化存储和多Agent协作

#### S09: Agent Teams
**Motto:** "When a task is too big for one, delegate to teammates"
- persistent teammates + async mailboxes
- 任务过载时委托
- 独立工作目录

#### S10: Team Protocols
**Motto:** "Teammates need shared communication rules"
- 一个请求-响应模式驱动所有协商
- 统一的任务声明协议
- 避免混乱的Agent间通信

#### S11: Autonomous Agents
**Motto:** "Teammates scan board and claim tasks themselves"
- idle cycle + auto-claim
- 不需要lead分配每个任务
- 自主任务分配机制

#### S12: Worktree Task Isolation
**Motto:** "Each works in its own directory, no interference"
- 任务协调 + 可选的独立执行通道
- worktree管理目录
- 通过ID绑定

---

## 🏗️ 项目架构

```
learn-claude-code/
├── agents/              # Python参考实现 (s01-s12 + s_full)
│   ├── s01_agent_loop.py
│   ├── s02_tool_use.py
│   ├── s03_todo_write.py
│   ├── s04_subagents.py
│   ├── s05_skills.py
│   ├── s06_context_compact.py
│   ├── s07_task_system.py
│   ├── s08_background_tasks.py
│   ├── s09_agent_teams.py
│   ├── s10_team_protocols.py
│   ├── s11_autonomous_agents.py
│   ├── s12_worktree_task_isolation.py
│   └── s_full.py          # Capstone: 所有机制合并
├── docs/                # Mental-model-first文档
│   ├── en/             # 英文
│   ├── zh/             # 中文
│   └── ja/             # 日语
├── skills/              # S05的技能文件
├── web/                 # 交互式学习平台 (Next.js)
│   ├── 交互式可视化
│   ├── 逐步图表
│   ├── 源码查看器
│   └── 在线文档
└── .github/workflows/   # CI配置
```

---

## 🌐 Web平台

### 功能特性
- **交互式可视化** - 实时展示Agent执行过程
- **逐步图表** - ASCII架构图，理解Agent流程
- **源码查看器** - 内置代码浏览器
- **在线文档** - 实时查阅文档

### 启动方式
```bash
cd web
npm install
npm run dev
# http://localhost:3000
```

---

## 🎯 关键设计理念

### 1. Mental-Model-First文档
**格式:** 问题 → 解决方案 → ASCII图表 → 最小代码

**优势:**
- 先理解问题本质
- 图形化展示架构
- 代码只实现核心逻辑
- 降低认知负担

### 2. 渐进式增强
**原则:** 每个session添加一个机制，保持核心循环不变

**实现:**
- S01: 基础循环
- S02: 添加工具
- S03: 添加Todo
- S04: 添加Subagents
- S05: 添加Skills
- S06: 添加Context Compact
- ...

### 3. 生产级简化
**简化但保留核心:**
- ✅ 12个progressive sessions
- ❌ 完整事件/钩子总线（只保留最小append-only生命周期）
- ❌ 基于规则的权限治理
- ❌ Session生命周期控制
- ❌ 完整MCP运行时

---

## 📊 Session对比

| Session | 主题 | 机制数量 | 难度 |
|---------|------|---------|------|
| S01 | Agent Loop | 1 | ⭐ |
| S02 | Tool Use | 1 | ⭐ |
| S03 | TodoWrite | 2 | ⭐⭐ |
| S04 | Subagents | 2 | ⭐⭐ |
| S05 | Skills | 2 | ⭐⭐ |
| S06 | Context Compact | 3 | ⭐⭐⭐ |
| S07 | Task System | 3 | ⭐⭐⭐ |
| S08 | Background Tasks | 3 | ⭐⭐⭐ |
| S09 | Agent Teams | 3 | ⭐⭐⭐⭐ |
| S10 | Team Protocols | 4 | ⭐⭐⭐⭐ |
| S11 | Autonomous Agents | 4 | ⭐⭐⭐⭐⭐ |
| S12 | Worktree Isolation | 4 | ⭐⭐⭐⭐⭐ |

---

## 🚀 技术特性

### 核心技术栈
- **语言:** Python
- **API:** Anthropic Messages API
- **模型:** Claude Code-like agent
- **Web框架:** Next.js

### 关键机制

1. **工具分发**
```python
dispatch_map = {
    "bash": execute_bash,
    "read_file": read_file,
    "write_file": write_file,
    # ... 更多工具
}
```

2. **Subagent独立上下文**
```python
# 每个subagent有独立的messages[]
subagent_messages = []
response = client.messages.create(messages=subagent_messages)
```

3. **后台任务队列**
```python
# daemon线程执行
queue = Queue()
daemon_thread = Thread(target=worker, args=(queue,))
daemon_thread.start()

# Agent继续思考
# 完成后通知
queue.put({"type": "notification", "content": result})
```

4. **任务依赖图**
```python
tasks = {
    "task1": {"deps": [], "status": "pending"},
    "task2": {"deps": ["task1"], "status": "pending"},
    "task3": {"deps": ["task1", "task2"], "status": "pending"},
}
```

---

## 💡 学习价值

### 为什么这个项目有价值？

1. **完整的学习路径**
   - 从最简单的循环开始
   - 逐步添加机制
   - 理解每个决策点

2. **生产级代码简化**
   - 保留核心架构
   - 简化复杂特性
   - 适合教学和学习

3. **多语言文档**
   - 英文、中文、日语
   - Mental-Model-First
   - 图形化理解

4. **交互式Web平台**
   - 可视化Agent执行
   - 逐步学习
   - 源码对比

---

## 🔍 与OpenClaw的关联

### OpenClaw的心跳和Cron机制
**claw0姐妹项目:** https://github.com/shareAI-lab/claw0

**OpenClaw = Agent核心 + Heartbeat + Cron + IM + Memory + Soul**

```python
claw0 = agent核心 + heartbeat + cron + IM聊天 + memory + soul个性
```

**关键机制:**
- **Heartbeat:** 每30秒检查是否有工作
  - 无事 → 回到sleep
  - 有事 → 立即执行
  
- **Cron:** Agent可以调度自己的未来任务
  - 时间到了自动执行
  - 不需要外部触发

**学习价值:**
- 从"use-and-discard"（用完即弃）到"always-on assistant"
- 添加多通道IM路由（WhatsApp/Telegram/Slack/Discord等）
- 持久化上下文记忆
- Soul个性系统

---

## 🎓 学习路径建议

### 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/shareAI-lab/learn-claude-code
cd learn-claude-code

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑.env，添加ANTHROPIC_API_KEY

# 4. 启动Web平台
cd web && npm install && npm run dev

# 5. 依次学习sessions
python agents/s01_agent_loop.py
python agents/s02_tool_use.py
# ...
python agents/s12_worktree_task_isolation.py
```

### 学习顺序建议

**初学者:**
1. 阅读S01-S03的文档
2. 运行示例代码
3. 理解基本循环和工具

**进阶者:**
4. 学习S04-S06（Subagents/Skills/Context）
5. 理解上下文管理和任务分解

**高级者:**
6. 学习S07-S12（Teams/Background/Autonomous）
7. 理解多Agent协作和持久化

---

## 🌟 项目亮点

### 1. 教学设计优秀
- Mental-Model-First文档
- 渐进式学习路径
- 每个session有明确目标
- 12个阶段，从0到1完整路径

### 2. 代码质量高
- 清晰的代码结构
- 详细的注释
- 可独立运行的每个session
- capstone项目（s_full.py）整合所有机制

### 3. 实用性强
- 12个session覆盖Agent开发核心话题
- Web平台提供交互式学习
- 多语言文档
- 生产级简化但核心完整

### 4. 生态系统完整
- 姐妹项目：claw0
- CLI工具：Kode Agent CLI
- SDK：Kode Agent SDK
- 从学习到生产的完整路径

---

## 🎯 适用人群

### 适合
- ✅ Agent开发初学者
- ✅ 想理解Claude Code原理的开发者
- ✅ 需要学习Agent架构的工程师
- ✅ 教育和培训场景
- ✅ 快速原型开发

### 不适合
- ❌ 需要开箱即用生产系统
- ❌ 复杂权限管理需求
- ❌ 大规模企业部署

---

## 📖 相关项目

### 1. Kode Agent CLI
**地址:** https://github.com/shareAI-lab/Kode
**定位:** 开源Coding Agent CLI
**特性:**
- Skill & LSP支持
- Windows就绪
- 可插拔（GLM/MiniMax/DeepSeek等）

### 2. Kode Agent SDK
**地址:** https://github.com/shareAI-lab/Kode-agent-sdk
**定位:** 在应用中嵌入Agent能力
**特性:**
- 独立库，无per-user进程开销
- 可嵌入到后端、浏览器扩展、嵌入式设备

### 3. OpenClaw
**地址:** https://github.com/openclaw/openclaw
**定位:** Always-on个人AI助手
**特性:**
- 心跳机制
- Cron调度
- 多通道IM路由
- 持久化记忆
- Soul个性系统

---

## 🚀 进阶建议

### 短期改进
1. **添加更多工具**
   - HTTP请求工具
   - Git操作工具
   - 文件搜索工具

2. **增强Web平台**
   - 在线代码执行
   - 实时日志查看
   - Session对比功能

3. **改进文档**
   - 添加视频教程
   - 更多实战案例
   - 交互式练习

### 中期改进
1. **性能优化**
   - 上下文压缩算法优化
   - Subagent池化
   - 后台任务调度优化

2. **功能增强**
   - 添加向量数据库支持
   - RAG检索集成
   - 长期记忆系统

3. **多模态支持**
   - 图像处理工具
   - 文档解析工具
   - 语音处理能力

### 长期改进
1. **分布式Agent**
   - 多机协作
   - 任务分发优化
   - 故障恢复机制

2. **插件系统**
   - 动态工具加载
   - 第三方工具市场
   - 社区贡献机制

---

## 📊 总结

### 项目优势
✅ 完整的学习路径（0到1）
✅ Mental-Model-First文档
✅ 渐进式教学设计
✅ 12个session覆盖核心话题
✅ 交互式Web平台
✅ 多语言支持（英/中/日）
✅ 生产级简化但核心完整

### 项目局限
❌ 不适合直接用于生产
❌ 缺少完整的权限管理
❌ 无复杂的生命周期控制

### 最佳用途
- 🎓 Agent开发教学
- 📚 理解Agent原理
- 🚀 快速原型开发
- 💡 架构设计和学习

---

## 🔍 对OpenClaw的启示

### 可以借鉴的设计
1. **Heartbeat机制**
   - 定期检查是否有工作
   - 无事时休眠，有事时立即执行
   - 避免"poke it to make it move"的低效

2. **Cron集成**
   - Agent可以自主调度任务
   - 准时执行预定义任务
   - 减少外部依赖

3. **多通道路由**
   - 支持WhatsApp/Telegram/Slack/Discord等13+平台
   - 统一的消息格式
   - 灵活的通道配置

4. **持久化记忆**
   - 长期知识存储
   - 用户偏好记录
   - 历史对话管理

### 实现建议
1. **在现有系统上叠加**
   - 保持核心Agent循环
   - 逐步添加Heartbeat/Cron/IM/Memory/Soul
   - 每个机制独立，易于测试

2. **模块化设计**
   - Heartbeat模块
   - Cron调度器
   - IM路由器
   - Memory存储
   - Soul个性引擎

3. **渐进增强**
   - 先实现Heartbeat（最重要的）
   - 再添加Cron调度
   - 最后添加持久化记忆

---

**研究完成时间:** 2026-03-07 16:45 (GMT+8)
**文档版本:** v1.0
**推荐度:** ⭐⭐⭐⭐⭐ (五星推荐)
