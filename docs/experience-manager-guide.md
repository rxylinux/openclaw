# Experience Manager 使用指南

## 概述

Experience Manager 是 OpenClaw 的经验管理器，用于：
- 结构化存储历史经验
- 自动从 daily memory 提取经验
- 管理成功/失败案例库
- 快速检索相关经验
- 生成经验摘要报告

## 功能特性

### 1. 经验提取

自动从 daily memory 文件中提取经验，支持：
- 决策类（关键决策、选择）
- 教训类（错误、失败）
- 偏好类（习惯、喜好）
- 技巧类（技巧、技巧）

### 2. 经验检索

多维度检索经验：
- 按类型：decision, lesson, preference, tip
- 按类别：investment, development, system, general
- 按标签：#股票, #代码, #决策
- 按时间：最近 N 天
- 按重要性：high, medium, low

### 3. 案例管理

管理成功和失败案例：
- 成功案例：记录成功的关键因素和模式
- 失败案例：分析失败原因和教训
- 可复用模式：提炼可复用的模式

### 4. 经验摘要

定期生成经验摘要：
- 本周新经验统计
- 案例分析
- 模式识别
- 数据统计

## 使用方法

### 命令行接口

#### 1. 提取经验

```bash
python3 scripts/experience-manager.py extract <memory_file>
```

示例：
```bash
# 提取今天的经验
python3 scripts/experience-manager.py extract memory/2026-03-01.md

# 提取多天的经验
python3 scripts/experience-manager.py extract memory/2026-03-01.md
python3 scripts/experience-manager.py extract memory/2026-02-28.md
```

#### 2. 查找经验

```bash
python3 scripts/experience-manager.py find [filters]
```

示例：
```bash
# 查找所有决策类经验
python3 scripts/experience-manager.py find type=decision

# 查找投资相关的经验
python3 scripts/experience-manager.py find category=investment

# 查找包含特定标签的经验
python3 scripts/experience-manager.py find tags=股票,风险

# 查找最近 7 天的高重要性经验
python3 scripts/experience-manager.py find importance=high days=7
```

#### 3. 查找案例

```bash
python3 scripts/experience-manager.py cases [filters]
```

示例：
```bash
# 查找所有成功案例
python3 scripts/experience-manager.py cases type=success

# 查找开发相关的案例
python3 scripts/experience-manager.py cases category=development
```

#### 4. 生成摘要

```bash
python3 scripts/experience-manager.py summary [days]
```

示例：
```bash
# 生成最近 7 天的摘要
python3 scripts/experience-manager.py summary 7

# 生成最近 30 天的摘要
python3 scripts/experience-manager.py summary 30
```

#### 5. 统计信息

```bash
python3 scripts/experience-manager.py stats
```

输出示例：
```json
{
  "total_experiences": 3,
  "experience_by_type": {
    "decision": 1,
    "tip": 2
  },
  "total_cases": 1,
  "cases_by_type": {
    "success": 1,
    "failure": 0
  },
  "last_updated": "2026-03-01T07:48:57.251516"
}
```

#### 6. 重新索引

```bash
python3 scripts/experience-manager.py reindex
```

用于重新索引所有案例文件（手动添加案例后使用）。

### 生成经验摘要

```bash
# 生成并显示摘要
python3 scripts/generate-experience-summary.py
```

生成的摘要会：
1. 打印到控制台
2. 保存到 `temp/experience-summary-latest.md`

## 文件结构

```
/root/.openclaw/workspace/
├── experience/
│   ├── experiences/
│   │   ├── decisions/
│   │   ├── lessons/
│   │   ├── preferences/
│   │   └── tips/
│   ├── cases/
│   │   ├── success/
│   │   │   └── case-20260301-001.md
│   │   └── failure/
│   ├── patterns/
│   │   ├── successful-decisions.md
│   │   └── common-pitfalls.md
│   └── index.json
├── scripts/
│   ├── experience-manager.py
│   └── generate-experience-summary.py
└── temp/
    └── experience-summary-latest.md
```

## 数据模型

### Experience 对象

```yaml
---
id: exp-20260301-001
type: decision
category: investment
tags: [股票, 仓位管理]
importance: high
created_at: 2026-03-01T06:00:00Z
related_experiences: [exp-2026-02-28-005]
source: memory/2026-03-01.md
---

# 不习惯止损（相信基本面，承受高波动）

**背景**:
- 用户风险偏好极高
- 投资策略：长期持有优质企业

**结论**:
- 对长期价值投资者，止损不是必须的
- 需要充分的基本面研究
```

### Case 对象

```yaml
---
id: case-20260301-001
type: success
category: development
project: Context Manager
date: 2026-03-01
outcome: completed_successfully
lessons:
  - 渐进式开发
  - 文档先行
  - 数据驱动
metrics:
  performance: 50% faster
  context_size: 40-60% reduced
---

# 成功案例：Context Manager 智能上下文

## 问题描述
每次会话加载所有文件，上下文窗口压力大

## 解决方案
场景自动检测 + 按场景动态加载

## 关键决策
选择关键词匹配而非语义分析

## 可复用模式
渐进式开发，先核心再完善
```

## 工作流程

### 1. 提取流程

```
daily memory
    ↓ extract
经验库（YAML 格式）
    ↓ index
索引文件
```

### 2. 检索流程

```
用户查询
    ↓ find
索引匹配
    ↓ load YAML
返回结果
```

### 3. 摘要流程

```
触发（每周日 20:00）
    ↓ generate
读取本周经验
    ↓ analyze
生成 Markdown
    ↓ save & display
文件 + 控制台
```

## 最佳实践

### 1. 经验提取

**标记经验段落**：
- 使用 `## 💡` 标记决策
- 使用 `## 📝` 标记教训
- 使用 `## 关键决策` 标记重要决策

**示例**：
```markdown
## 💡 关键设计决策

不习惯止损，相信基本面，承受高波动。

**原因**：
- 风险偏好极高
- 长期持有策略
```

### 2. 案例管理

**成功案例**：
- 记录关键决策
- 提炼可复用模式
- 提供具体指标

**失败案例**：
- 分析失败原因
- 提取教训
- 提供改进建议

### 3. 标签使用

**推荐标签**：
- #股票 - 股票投资相关
- #代码 - 代码开发相关
- #决策 - 决策类经验
- #教训 - 教训类经验
- #技巧 - 技巧类经验

### 4. 定期维护

**每周**：
- 提取 daily memory 中的经验
- 生成经验摘要

**每月**：
- 审核经验内容
- 清理过时经验
- 更新案例库

**每季度**：
- 分析经验模式
- 生成总结报告
- 优化检索策略

## 集成到会话

### Python 集成示例

```python
from scripts.experience_manager import ExperienceManager

# 创建管理器
em = ExperienceManager()

# 查找相关经验
experiences = em.find_experiences(
    type='decision',
    category='investment'
)

# 应用经验到决策
for exp in experiences:
    print(f"经验: {exp.content}")
```

### Shell 集成示例

```bash
#!/bin/bash

# 在会话开始前提取经验
python3 /root/.openclaw/workspace/scripts/experience-manager.py \
    extract memory/2026-03-01.md

# 查找相关经验
python3 /root/.openclaw/workspace/scripts/experience-manager.py \
    find type=lesson category=investment
```

## 故障排查

### 问题：提取的经验不准确

**原因**：
- daily memory 中的经验标记不清晰
- 提取规则需要调整

**解决方法**：
1. 检查 daily memory 格式
2. 使用清晰的标记（## 💡, ## 📝）
3. 手动编辑提取的经验

### 问题：检索结果太多

**原因**：
- 过滤条件不够具体

**解决方法**：
1. 添加更多过滤条件
2. 使用标签过滤
3. 限制时间范围

### 问题：案例没有索引

**原因**：
- 手动添加案例后没有重新索引

**解决方法**：
```bash
python3 scripts/experience-manager.py reindex
```

## 性能优化

### 1. 索引优化

- 索引文件增量更新
- 避免全量扫描

### 2. 检索优化

- 缓存常用查询结果
- 限制返回数量

### 3. 存储优化

- 定期清理过时经验
- 压缩历史案例

## 未来改进

- [ ] 向量化索引（语义搜索）
- [ ] 实时提取（自动监控）
- [ ] 机器学习分类
- [ ] 用户反馈循环
- [ ] 多语言支持

## 相关文档

- [阶段 2 设计文档](phase2-knowledge-graph-design.md)
- [阶段 1 总结](phase1-context-manager-summary.md)
- [Context Manager 指南](context-manager-guide.md)

## 支持

如有问题或建议，请创建 Issue 或联系维护者。
