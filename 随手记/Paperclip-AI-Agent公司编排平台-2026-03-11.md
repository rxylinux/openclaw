# Paperclip - AI Agent公司编排平台研究总结

**研究时间：** 2026-03-11  
**项目地址：** https://github.com/paperclipai/paperclip  
**开发者：** paperclipai  
**Stars：** 18.1k ⭐  
**状态：** 活跃（1小时前更新）  
**许可：** MIT  
**技术栈：** Node.js + React + PostgreSQL  
**官网：** https://paperclip.ing/docs

---

## 🚀 核心理念

### 一句话总结

> **如果 OpenClaw 是员工，Paperclip 就是公司**

### 使命

为零人力公司提供开源编排层

### 愿景

让你管理商业目标，而不是管理 Pull Request

---

## 🎮 核心功能

### 1. BYOA (Bring Your Own Agent)

```
任何Agent，任何运行时，一个组织架构图
只要能接收心跳，就可以被雇佣
```

**支持的Agent类型：**
- OpenClaw
- Claude Code
- Cursor
- Codex
- 任何自定义Agent

### 2. 目标对齐 (Goal Alignment)

```
每个任务都可以追溯到公司使命
Agent知道该做什么，以及为什么做
```

**层级结构：**
```
公司目标
  ↓
项目目标
  ↓
任务
  ↓
Agent执行
```

### 3. 心跳系统 (Heartbeats)

```
Agent按计划唤醒，检查工作，行动
委托在组织架构图中上下流动
```

**工作模式：**
- 调度式（定时任务）
- 事件驱动（任务分配、@mentions）
- 持续式（如OpenClaw）

### 4. 成本控制 (Cost Control)

```
每个Agent每月预算
达到限制时停止
无失控成本
```

**成本监控：**
- Token预算
- API调用统计
- 实时成本追踪
- 超预算自动停止

### 5. 多公司支持 (Multi-Company)

```
一次部署，多个公司
完全数据隔离
一个控制平面管理你的投资组合
```

### 6. 工单系统 (Ticket System)

```
每段对话都有追踪
每个决策都有解释
完整的工具调用追踪和不可变审计日志
```

### 7. 治理系统 (Governance)

```
你是董事会
批准招聘，覆盖策略，暂停或终止任何Agent - 随时
```

**治理权限：**
- Agent招聘/解雇
- 策略批准
- 预算调整
- 紧急暂停
- 配置回滚

### 8. 组织架构图 (Org Chart)

```
层级、角色、汇报线
你的Agent有老板、头衔和职位描述
```

### 9. 移动端支持 (Mobile Ready)

```
从任何地方监控和管理你的自主业务
```

---

## 🔄 工作流示例

### 传统方式

```
你有20个Claude Code标签打开
无法追踪哪个在做什么
重启后丢失所有状态
```

### Paperclip方式

```
Step 1: 定义目标
"构建#1 AI笔记应用，达到$1M MRR"

Step 2: 招聘团队
CEO、CTO、工程师、设计师、营销 - 
任何bot，任何提供商

Step 3: 审批并运行
审查策略。设置预算。点击启动。
从仪表板监控。
```

---

## 🎯 适用场景

✅ **如果你：**

1. 想要构建自主AI公司
2. 协调多个不同Agent（OpenClaw、Codex、Claude、Cursor）实现共同目标
3. 有20个同时运行的Claude Code终端，丢失了每个人在做什么
4. 想要Agent 24/7自主运行，但仍要审计工作并在需要时介入
5. 想要监控成本并执行预算
6. 想要一个感觉像任务管理器的Agent管理流程
7. 想要从手机管理自主业务

---

## 🆚 解决的问题

| 问题 | 无Paperclip | 有Paperclip |
|------|------------|------------|
| 状态混乱 | ❌ 20个Claude Code标签打开，无法追踪 | ✅ 基于任务，会话线程化，重启后持久化 |
| 上下文丢失 | ❌ 手动从多个地方收集上下文 | ✅ 上下文从任务向上流向公司和项目目标 |
| 组织混乱 | ❌ Agent配置文件夹混乱，重复造轮子 | ✅ 组织架构、工单、委托、治理开箱即用 |
| 成本失控 | ❌ 运行循环浪费数百美元token | ✅ 成本跟踪显示token预算，超限节流 |
| 手动触发 | ❌ 定期任务（客服、社交、报告）需要手动启动 | ✅ 心跳处理定期工作，管理监督 |

---

## 💎 为什么Paperclip特殊

### 1. 原子执行

```
任务检出和预算执行是原子的
所以没有双重工作，没有失控消费
```

### 2. 持久Agent状态

```
Agent在心跳间恢复相同的任务上下文
而不是从头重新开始
```

### 3. 运行时技能注入

```
Agent可以在运行时学习Paperclip工作流和项目上下文
无需重新训练
```

### 4. 带回滚的治理

```
审批门被强制执行，配置变更被版本化
不良更改可以安全回滚
```

### 5. 目标感知执行

```
任务携带完整的目标祖先
所以Agent始终看到"为什么"，而不仅仅是标题
```

### 6. 可移植公司模板

```
导出/导入组织、Agent和技能
支持密钥清理和冲突处理
```

### 7. 真正的多公司隔离

```
每个实体都是公司范围的
所以一次部署可以运行多个公司
具有单独的数据和审计轨迹
```

---

## 🚫 Paperclip不是什么

| 不是 | 原因 |
|------|------|
| 聊天机器人 | Agent有工作，不是聊天窗口 |
| Agent框架 | 不告诉你如何构建Agent，告诉你如何运行由它们组成的公司 |
| 工作流构建器 | 没有拖放管道，Paperclip建模公司 - 组织架构、目标、预算、治理 |
| 提示词管理器 | Agent带来自己的提示词、模型和运行时 |
| 单Agent工具 | 这是为团队设计的。如果你有一个Agent，可能不需要Paperclip。如果你有二十个 - 绝对需要 |
| 代码审查工具 | Paperclip编排工作，不是Pull Request。带来自己的审查过程 |

---

## 🚀 快速开始

```bash
# 方法1：一键安装
npx paperclipai onboard --yes

# 方法2：手动安装
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev
```

**启动后：**
- API服务器：http://localhost:3100
- 自动创建嵌入式PostgreSQL数据库 - 无需设置

**要求：**
- Node.js 20+
- pnpm 9.15+

---

## 🛠️ 开发命令

```bash
pnpm dev              # 完整开发（API + UI，监听模式）
pnpm dev:once         # 完整开发，无文件监听
pnpm dev:server       # 仅服务器
pnpm build            # 构建所有
pnpm typecheck        # 类型检查
pnpm test:run         # 运行测试
pnpm db:generate      # 生成数据库迁移
pnpm db:migrate       # 应用迁移
```

---

## 📋 路线图

### 即将推出

- ⚪ 让OpenClaw接入更容易
- ⚪ 让云Agent工作（如Cursor / e2b agents）
- ⚪ ClipMart - 一键购买和运行整个Agent公司
- ⚪ 简化Agent配置 / 更易理解
- ⚪ 更好的工具工程支持
- ⚪ 插件系统（知识库、自定义追踪、队列等）
- ⚪ 更好的文档

---

## 🌟 ClipMart (即将推出)

### 下载并一键运行整个公司

浏览预构建的公司模板 - 完整的组织架构、Agent配置和技能 - 并在几秒钟内导入到你的Paperclip实例。

---

## 💡 典型设置

### 本地

单个Node.js进程管理嵌入式Postgres和本地文件存储。

### 生产

指向你自己的Postgres，以任何方式部署（Vercel、Railway等）

### 对于独立创业者

使用Tailscale在移动时访问Paperclip，需要时部署到Vercel。

---

## 🎓 技术架构

```
┌─────────────────────────────────────┐
│         Paperclip                  │
│   (Node.js + React)               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     PostgreSQL (Embedded)          │
│   - 公司                         │
│   - 项目                         │
│   - 任务                         │
│   - Agent                         │
│   - 工单                           │
│   - 治理记录                       │
│   - 成本追踪                       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Agent运行时                     │
│   - OpenClaw                      │
│   - Claude Code                   │
│   - Cursor                        │
│   - 自定义Agent                    │
└─────────────────────────────────────┘
```

---

## 🎯 对你的价值

### 作为OpenClaw用户

#### 1. 完美互补

```
OpenClaw = 员工（执行工作）
Paperclip = 公司（管理工作）
```

#### 2. 解决痛点

- ✅ 多Agent协调混乱 → 有序的组织架构
- ✅ 成本失控 → 预算控制和实时监控
- ✅ 任务追踪丢失 → 完整的工单系统
- ✅ 上下文传递困难 → 目标对齐和上下文流
- ✅ 手动管理 → 自动心跳和委托

#### 3. 投资组合管理

```
一个Paperclip实例
  ↓
多个"公司"（项目）
  ↓
每个公司有自己的：
- 组织架构
- Agent团队
- 预算
- 目标
```

---

## 📊 与其他方案对比

| 特性 | Paperclip | 直接使用OpenClaw | 任务管理器（Asana/Trello） |
|------|----------|----------------|---------------------------|
| Agent编排 | ✅ 原生 | ❌ 需要手动 | ❌ 无Agent概念 |
| 组织架构 | ✅ 原生 | ❌ 无 | ✅ 但无Agent |
| 成本控制 | ✅ 原生 | ❌ 基础 | ❌ 无 |
| 目标对齐 | ✅ 原生 | ❌ 无 | ✅ 但无上下文流 |
| 会话持久化 | ✅ 原生 | ✅ 有限 | ❌ 无 |
| 治理系统 | ✅ 原生 | ❌ 无 | ❌ 无 |
| 审计日志 | ✅ 原生 | ❌ 有限 | ❌ 无 |
| 多公司 | ✅ 原生 | ❌ 无 | ✅ 多工作区 |

---

## 💼 使用场景示例

### 场景1：AI笔记应用开发公司

```yaml
公司目标：构建#1 AI笔记应用，达到$1M MRR

组织架构：
  CEO (Claude Code)
  CTO (OpenClaw)
  前端工程师 (Cursor)
  后端工程师 (OpenClaw)
  UI设计师 (DALL-E + Claude Code)
  
预算：
  CEO: $500/月
  CTO: $800/月
  工程师团队: $2000/月
  设计师: $300/月
  
心跳频率：
  CEO: 每日
  CTO: 每日
  工程师: 连续（开发中）
  设计师: 事件驱动
```

### 场景2：自动化内容营销公司

```yaml
公司目标：每月生产100篇高质量技术内容

组织架构：
  内容总监 (OpenClaw)
  研究员 (OpenClaw + ask-search)
  写作团队 (3个Claude Code实例)
  SEO专家 (OpenClaw)
  社交媒体经理 (OpenClaw)
  
预算：
  总计: $3000/月
  
心跳频率：
  每日批量生产
```

### 场景3：投资组合管理

```yaml
Paperclip实例
  ↓
公司1：AI笔记应用（开发中）
公司2：内容营销（运行中）
公司3：客服机器人（生产环境）
公司4：数据分析（研究阶段）
  ↓
每个公司独立运营
独立预算
独立审计
```

---

## 🎓 学习成本

### 初学者

**1-2天上手**
- 基本概念
- 创建第一个公司
- 配置Agent

### 进阶

**1周掌握**
- 组织架构设计
- 治理策略
- 成本优化

### 专家

**1个月精通**
- 插件开发
- 自定义工作流
- ClipMart模板创建

---

## 🚦 部署建议

### 开发环境

```bash
# 本地一键安装
npx paperclipai onboard --yes

# 或者Docker
docker build -t paperclip-local .
docker run -p 3100:3100 paperclip-local
```

### 生产环境

- Vercel（推荐）
- Railway
- AWS EC2
- 自有服务器

### 数据存储

- 开发：嵌入式PostgreSQL
- 生产：外部PostgreSQL（Supabase、Neon等）

---

## 🎯 是否适合你？

### ✅ 强烈推荐，如果：

- 你同时使用多个Agent（OpenClaw + Claude Code + Cursor等）
- 你想构建"零人力"公司
- 你需要监控成本
- 你想24/7自主运行但保留控制权
- 你有多个独立项目需要管理

### ❌ 可能不需要，如果：

- 你只使用一个Agent
- 你只是偶尔使用AI工具
- 你不需要自动化工作流
- 你不需要成本追踪

---

## 🗺️ 社区与资源

- **Discord：** https://discord.gg/m4HZY7xNG3
- **文档：** https://paperclip.ing/docs
- **问题：** GitHub Issues
- **讨论：** GitHub Discussions
- **贡献指南：** CONTRIBUTING.md

---

## 📝 总结

### Paperclip是：

- Agent编排层
- 零人力公司操作系统
- 成本控制和治理平台
- 多Agent协调工具

### Paperclip不是：

- Agent本身
- 聊天机器人
- 工作流构建器
- 代码审查工具

### 核心价值

```
让AI团队像真实公司一样运作
组织架构 + 目标对齐 + 治理 + 成本控制
```

---

## 🚀 下一步

### 立即尝试

```bash
npx paperclipai onboard --yes
```

### 学习资源

- 官方文档：https://paperclip.ing/docs
- Discord社区：https://discord.gg/m4HZY7xNG3
- GitHub：https://github.com/paperclipai/paperclip

### 期待功能

- ClipMart（一键公司模板）
- 更好的OpenClaw集成
- 插件系统

---

## 💡 我的建议

### 对于你

1. **立即尝试本地部署**
   - 一条命令启动
   - 无需数据库设置
   - 零成本试用

2. **结合OpenClaw使用**
   - OpenClaw作为"员工"
   - Paperclip作为"公司管理层"
   - 完美互补

3. **从小项目开始**
   - 创建一个测试公司
   - 配置2-3个Agent
   - 理解工作流

4. **扩展到投资组合**
   - 多个"公司"代表不同项目
   - 统一管理
   - 独立预算

---

## 🎯 与其他项目的协同效应

### ask-search + Paperclip

```
ask-search：零成本搜索（员工工具）
Paperclip：公司编排（管理层）
  ↓
完整解决方案：
- 搜索Agent（使用ask-search）
- 内容生产Agent（使用Paperclip协调）
- 成本控制（Paperclip预算管理）
- 目标对齐（Paperclip组织架构）
```

### 实施建议

```yaml
公司目标：AI驱动的市场研究

组织架构：
  CEO (OpenClaw + ask-search)
  研究总监 (Claude Code)
  数据分析师 (OpenClaw)
  报告生成器 (OpenClaw)
  
工具集成：
  搜索：ask-search（零成本）
  编排：Paperclip（目标对齐）
  成本：Paperclip（预算控制）
```

---

**研究完成时间：** 2026-03-11  
**下一步：** 本地部署测试 + 与OpenClaw集成
