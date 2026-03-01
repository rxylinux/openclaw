# 阶段 2: 经验沉淀 - 设计文档

## 📋 目标

建立知识图谱和经验库，让系统能够：
- 结构化存储历史经验
- 快速检索相关经验
- 自动提取经验摘要
- 管理成功/失败案例

## 🎯 核心功能

### 1. 经验库结构化

**目标**: 将 MEMORY.md 和 daily memory 转换为结构化数据

**方案**:
- 使用 YAML 前置元数据（Front Matter）
- 分类存储：决策、教训、偏好、技巧
- 时间索引和标签系统

**数据模型**:
```yaml
---
id: exp-2026-03-01-001
type: decision
category: investment
tags: [股票, 仓位管理, 风险控制]
importance: high
created_at: 2026-03-01T06:00:00Z
related_experiences: [exp-2026-02-28-005]
---

# 不习惯止损（相信基本面，承受高波动）

**背景**:
- 用户风险偏好极高
- 投资策略：长期持有优质企业
- 交易习惯：到目标价后止盈，不喜欢止损

**分析**:
- 基本面驱动投资 vs 技术面止损
- 长期持有 vs 波动承受能力
- 信念成本 vs 止损纪律

**结论**:
- 对长期价值投资者，止损不是必须的
- 需要充分的基本面研究和心理承受能力
- 适合高波动但高成长的优质标的

**适用场景**:
- 基本面深入研究
- 长期投资周期（>3年）
- 高成长赛道
```

### 2. 成功/失败案例库

**目标**: 记录并分类历史上的成功和失败案例

**目录结构**:
```
experience/
├── cases/
│   ├── success/
│   │   ├── 2026-03-stock-analysis.md
│   │   └── 2026-03-context-manager.md
│   └── failure/
│       ├── 2026-02-tool-error.md
│       └── 2026-02-data-loss.md
└── patterns/
    ├── successful-decisions.md
    └── common-pitfalls.md
```

**案例模板**:
```yaml
---
id: case-2026-03-001
type: success
category: development
project: Context Manager
date: 2026-03-01
outcome: completed_successfully
lessons:
  - 渐进式开发，先核心再完善
  - 文档先行，测试驱动
  - 数据驱动优化
metrics:
  performance: 50% faster
  context_size: 40-60% reduced
---

# 成功案例：Context Manager 智能上下文

**问题**:
- 每次会话加载所有文件，上下文窗口压力大
- 无法智能判断需要哪些文件
- 文件使用频率无法追踪

**解决方案**:
1. 场景自动检测（基于关键词）
2. 按场景动态加载文件
3. 频率追踪和压缩机制

**关键决策**:
- 选择关键词匹配而非语义分析（快速、可依赖）
- 使用带衰减的频率分数（自适应优化）
- 归档旧文件而非删除（保留历史）

**结果**:
- 上下文大小减少 40-60%
- 加载时间减少 50%+
- 用户体验显著提升

**可复用模式**:
- 渐进式功能开发
- 数据驱动的优化策略
- 文档与代码同步更新
```

### 3. 自动经验提取

**目标**: 从 daily memory 中自动提取经验

**提取规则**:
1. **标记段落**: 以 `## 💡`、`## 📝`、`## 关键决策` 开头
2. **识别模式**: "学习到"、"发现"、"结论是"、"记住"
3. **时间戳**: 自动记录提取时间
4. **重要性评分**: 基于关键词（"必须"、"关键"、"重要"）

**提取脚本**:
```python
# scripts/extract-experience.py
from experience_manager import ExperienceManager

em = ExperienceManager()

# 从 daily memory 提取
experiences = em.extract_from_memory("memory/2026-03-01.md")

# 保存到经验库
for exp in experiences:
    em.save_experience(exp)
```

### 4. 经验检索机制

**目标**: 快速找到相关经验

**检索维度**:
- **按场景**: 投资分析、代码开发
- **按类型**: 决策、教训、技巧、偏好
- **按标签**: #股票、#止损、#仓位
- **按时间**: 最近7天、最近30天
- **按重要性**: 高、中、低

**检索命令**:
```bash
# 按场景检索
python3 scripts/experience-manager.py find scenario=investment_analysis

# 按标签检索
python3 scripts/experience-manager.py find tags=股票,风险

# 按类型检索
python3 scripts/experience-manager.py find type=lesson

# 按时间检索
python3 scripts/experience-manager.py find days=7
```

### 5. 经验摘要生成

**目标**: 定期生成经验摘要

**摘要内容**:
- 本周新经验
- 重要决策回顾
- 失败案例分析
- 模式识别

**生成频率**:
- 每周日晚上 8 点
- 通过飞书推送

**摘要模板**:
```markdown
# 📊 经验周报 - 2026年第9周

## 🆕 本周新经验

### 决策类
- 不习惯止损（高风险偏好，相信基本面）

### 教训类
- 代码开发：文档先行，测试驱动

## 🎯 重要决策回顾

### Context Manager 实现
- **决策**: 选择关键词匹配而非语义分析
- **原因**: 快速、可依赖、不依赖外部服务
- **结果**: 上下文大小减少 40-60%

## 📉 失败案例分析

本周无失败案例 ✅

## 🔍 模式识别

### 成功模式
- 渐进式开发 → 更好的质量
- 文档先行 → 更易维护

### 需要改进
- 频率统计 → 需要定期清理
- 场景检测 → 需要定期更新关键词

## 📈 数据统计

- 新增经验: 2 条
- 成功案例: 1 个
- 失败案例: 0 个
- 模式识别: 2 个
```

## 🏗️ 架构设计

### 组件关系

```
Experience Manager (scripts/experience-manager.py)
    ├── Experience Extractor
    │   └── 从 daily memory 提取经验
    ├── Experience Store
    │   ├── YAML 文件存储
    │   └── 索引文件
    ├── Experience Indexer
    │   ├── 按场景索引
    │   ├── 按标签索引
    │   └── 全文搜索
    └── Experience Summarizer
        └── 生成经验摘要
```

### 文件结构

```
/root/.openclaw/workspace/
├── experience/
│   ├── cases/
│   │   ├── success/
│   │   └── failure/
│   ├── patterns/
│   ├── experiences/
│   │   ├── decisions/
│   │   ├── lessons/
│   │   ├── preferences/
│   │   └── tips/
│   └── index.json
├── scripts/
│   ├── experience-manager.py
│   ├── extract-experience.py
│   └── generate-experience-summary.py
└── config/
    └── experience-config.json
```

## 📊 数据模型

### Experience 对象

```python
@dataclass
class Experience:
    id: str
    type: str  # decision, lesson, preference, tip
    category: str  # investment, development, etc.
    tags: List[str]
    importance: str  # high, medium, low
    created_at: str
    related_experiences: List[str]
    content: str
    source: str  # memory file path
```

### Case 对象

```python
@dataclass
class Case:
    id: str
    type: str  # success, failure
    category: str
    project: str
    date: str
    outcome: str
    lessons: List[str]
    metrics: Dict[str, Any]
    content: str
```

## 🔄 工作流程

### 1. 提取流程

```
daily memory
    ↓ extract-experience.py
经验库（YAML 格式）
    ↓ experience-manager.py index
索引文件
```

### 2. 检索流程

```
用户查询
    ↓ experience-manager.py find
索引匹配
    ↓ 加载 YAML
返回结果
```

### 3. 摘要流程

```
触发（每周日 20:00）
    ↓ generate-experience-summary.py
读取本周经验
    ↓ 分析和统计
生成 Markdown 摘要
    ↓ 推送到飞书
```

## 📋 实施计划

### Week 1: 核心框架
- [ ] 实现 ExperienceManager 类
- [ ] 设计 YAML 模板
- [ ] 创建目录结构
- [ ] 实现基本存储功能

### Week 2: 提取和索引
- [ ] 实现自动提取脚本
- [ ] 构建索引机制
- [ ] 实现全文搜索
- [ ] 测试提取流程

### Week 3: 检索和摘要
- [ ] 实现多维度检索
- [ ] 生成摘要脚本
- [ ] 集成到 cron
- [ ] 测试完整流程

### Week 4: 优化和完善
- [ ] 优化索引性能
- [ ] 改进提取准确性
- [ ] 编写使用文档
- [ ] 性能测试

## 🎯 成功指标

- [ ] 能够自动提取 80% 以上的重要经验
- [ ] 检索响应时间 < 100ms
- [ ] 索引文件大小 < 1MB
- [ ] 摘要生成时间 < 5s
- [ ] 用户体验满意度 > 4.0/5.0

## 📝 注意事项

### 数据质量
- 确保提取的准确性
- 定期审核经验内容
- 处理重复经验

### 性能考虑
- 索引要增量更新
- 检索结果要缓存
- 大文件要分页

### 可扩展性
- 支持向量化索引（未来）
- 支持分布式存储（未来）
- 支持实时更新（未来）

---

*创建时间: 2026-03-01*
*状态: 📋 设计完成*
*下一阶段: 实施阶段*
