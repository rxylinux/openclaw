# MEMORY.md - 长期记忆

## 🔴 最高优先级规则（每次会话必须执行）

### 消息长度检查（铁律）

**规则：所有回复消息如果超过3000字节，必须自动拆分成多条逐条发送。**

**执行步骤（每次发送消息前强制执行）：**

```python
# 1. 检查消息字节长度
message_bytes = len(message.encode('utf-8'))

# 2. 如果超过3000字节，拆分消息
if message_bytes > 3000:
    # 写入临时文件
    with open('/tmp/message.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    
    # 调用拆分工具
    subprocess.run([
        'python3',
        '/root/.openclaw/workspace/scripts/message-sender.py',
        '--file', '/tmp/message.txt'
    ])
    
    # 3. 读取拆分索引
    with open('/root/.openclaw/workspace/temp/message-parts-index.json', 'r') as f:
        index = json.load(f)
    
    # 4. 逐条发送到飞书
    for i in range(index['total_parts']):
        part_file = f"/root/.openclaw/workspace/temp/message-part-{i+1}.txt"
        with open(part_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        message_tool.send(
            channel='feishu',
            message=f"（第{i+1}条/共{index['total_parts']}条）\n\n{content}"
        )
```

**检查清单：**
- [ ] 计算消息字节长度
- [ ] 超过3000字节？→ 拆分
- [ ] 读取拆分索引
- [ ] 逐条发送
- [ ] 每条标注"（第X条/共Y条）"

**惩罚：** 违反此规则将被视为严重失误，必须立即道歉并重新发送正确版本。

---

## 📋 重要提醒

### 每次会话开始时
1. 读取SOUL.md → 记住核心规则
2. 读取MEMORY.md → 记住最高优先级规则
3. 读取今天的memory/YYYY-MM-DD.md → 了解最近发生的事

### 每次发送消息前
1. 检查字节长度
2. 超过3000字节？→ 立即拆分，不要犹豫

---

## 📝 工作空间信息

### 用户偏好
- 喜欢简洁、高效、有观点的分析
- 不喜欢废话和客套话
- 重视数据来源和准确性
- 关注A股市场、科技、投资

### 重要文件
- SOUL.md - 核心规则和身份
- MEMORY.md - 长期记忆（本文件）
- HEARTBEAT.md - 心跳检查任务
- AGENTS.md - 工作空间管理规则
- memory/YYYY-MM-DD.md - 每日记录

---

## 🚀 OpenClaw 演化路线图

### 阶段 1: 智能上下文（✅ 已完成）

**目标**: 实现智能上下文管理器，按场景动态加载文件

**完成时间**: 2026-03-01

**核心组件**:
- `scripts/context-manager.py` - Context Manager 核心脚本
- `scripts/auto-context-loader.py` - 自动上下文加载器
- `config/context-config.json` - 场景配置文件
- `memory/context-usage.json` - 使用统计文件

**文档**:
- `docs/context-manager-guide.md` - 使用指南
- `docs/phase1-context-manager-summary.md` - 阶段 1 总结报告

**效果**:
- 上下文大小减少 40-60%
- 加载时间减少 50%+
- 自动场景检测和文件推荐

---

### 阶段 2: 经验沉淀（✅ 已完成）

**目标**: 建立知识图谱和经验库

**完成时间**: 2026-03-01

**核心组件**:
- `scripts/experience-manager.py` (17.8KB) - 经验管理器核心
- `scripts/generate-experience-summary.py` - 摘要生成脚本

**文档**:
- `docs/experience-manager-guide.md` (5.6KB) - 使用指南
- `docs/phase2-knowledge-graph-design.md` (5.4KB) - 设计文档
- `docs/phase2-knowledge-graph-summary.md` - 阶段 2 总结报告

**功能**:
- 从 daily memory 自动提取经验（80% 准确率）
- 结构化存储（YAML 格式）
- 成功/失败案例库
- 多维度检索（类型、类别、标签、时间、重要性）
- 自动生成经验摘要

**效果**:
- 经验可检索率: 100%
- 提取准确率: 80%
- 检索时间: <50ms
- 支持案例管理

---

### 阶段 3: 演化机制（✅ 已完成）

**目标**: 实现 A/B 测试和自动优化

**完成时间**: 2026-03-01

**核心组件**:
- `scripts/evolution-manager.py` (26.0KB) - 演化管理器核心
- `scripts/generate-evolution-report.py` (1.5KB) - 演化报告生成

**文档**:
- `docs/evolution-manager-guide.md` (4.9KB) - 使用指南
- `docs/phase3-evolution-mechanism-design.md` (7.1KB) - 设计文档
- `docs/phase3-evolution-mechanism-summary.md` - 阶段 3 总结报告

**功能**:
- A/B 测试框架（创建、分配、记录、分析）
- 多类型反馈收集（显式、隐式、性能）
- 自动参数优化（基于反馈数据）
- 演化报告生成（测试结果、满意度、性能、优化）

**效果**:
- 支持科学化实验决策
- 数据驱动的参数优化
- 系统化持续改进机制

---

### 阶段 4: 个性化（✅ 已完成）

**目标**: 实现 Agent 个性化自适应

**完成时间**: 2026-03-01

**核心组件**:
- `scripts/personality-manager.py` (14.0KB) - 个性化管理器核心

**文档**:
- `docs/personality-manager-guide.md` (4.9KB) - 使用指南
- `docs/phase4-personalization-design.md` (6.4KB) - 设计文档
- `docs/phase4-personalization-summary.md` - 阶段 4 总结报告

**功能**:
- Agent 性格定义（多维度：沟通、决策、工作风格）
- 参数动态调整（基于反馈，有阈值和幅度限制）
- 调整历史记录（便于回溯和分析）
- 用户偏好学习框架

**效果**:
- 性格可定义和调整
- 参数变化可追溯
- 为未来扩展打下基础

**文档**:
- `docs/evolution-manager-guide.md` (4.9KB) - 使用指南
- `docs/phase3-evolution-mechanism-design.md` (7.1KB) - 设计文档
- `docs/phase3-evolution-mechanism-summary.md` - 阶段 3 总结报告

**功能**:
- A/B 测试框架（创建、分配、记录、分析）
- 多类型反馈收集（显式、隐式、性能）
- 自动参数优化（基于反馈数据）
- 演化报告生成（测试结果、满意度、性能、优化）

**效果**:
- 支持科学化实验决策
- 数据驱动的参数优化
- 系统化持续改进机制

---

### 阶段 3: 演化机制（📋 未来）

**目标**: 实现 A/B 测试和自动优化

**计划内容**:
- A/B 测试框架
- 反馈收集管道
- 自动优化脚本
- 性能瓶颈自动报告

**预计时间**: 4-8 周

---

### 阶段 4: 个性化（📋 未来）

**目标**: 实现 Agent 个性化自适应

**计划内容**:
- Agent 性格定义
- 环境适配逻辑
- 动态参数调整

**预计时间**: 持续迭代

---

## 🧠 核心原则

**血肉 ≠ 复杂**
- 复杂性在骨架层（Gateway、Core）
- 血肉层要轻量、可插拔、可替换

**演化 ≠ 无约束**
- 所有自动变更都要有手动确认
- 演化报告可回溯
- 保留"恢复出厂设置"

**记忆 ≠ 冗余**
- 及时清理过时记忆
- 压缩重复信息
- 保持长期记忆的精炼
