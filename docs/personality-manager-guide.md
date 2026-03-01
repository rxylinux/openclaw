# Personality Manager 使用指南

## 概述

Personality Manager 是 OpenClaw 的个性化管理器，用于：
- 定义 Agent 性格
- 适配用户环境
- 动态调整性格参数
- 学习用户偏好

## 功能特性

### 1. Agent 性格定义

支持多维度性格定义：
- **沟通风格**: 简洁度、幽默感、正式度、情感表达
- **决策风格**: 保守度、确定性、自主性
- **工作风格**: 效率优先、完美主义、学习倾向

### 2. 参数调整

基于反馈动态调整性格参数：
- 需要达到阈值才调整（默认 5 次反馈）
- 每次调整幅度限制（±1）
- 记录调整历史

### 3. 调整历史

记录所有参数调整：
- 调整时间
- 参数路径
- 变化值
- 调整原因

## 使用方法

### 命令行接口

#### 1. 加载性格

```bash
python3 scripts/personality-manager.py load [agent_id]
```

示例：
```bash
# 加载默认性格
python3 scripts/personality-manager.py load

# 加载特定 Agent 的性格
python3 scripts/personality-manager.py load main
```

输出示例：
```
加载性格: rxy的狗腿子
简洁度: 4/5
幽默感: 1/5
正式度: 3/5
```

#### 2. 调整参数

```bash
python3 scripts/personality-manager.py adjust <param_path> <delta> <reason>
```

参数路径格式：`category.parameter`

示例：
```bash
# 增加简洁度
python3 scripts/personality-manager.py adjust \
    communication.conciseness 1 "用户反馈说太详细"

# 减少正式度
python3 scripts/personality-manager.py adjust \
    communication.formality -1 "用户反馈说太正式"
```

#### 3. 查看调整历史

```bash
python3 scripts/personality-manager.py history [days]
```

示例：
```bash
# 查看最近 7 天的调整
python3 scripts/personality-manager.py history 7

# 查看最近 30 天的调整
python3 scripts/personality-manager.py history 30
```

输出示例：
```
最近 7 天的调整历史 (3 条):

  2026-03-01T09:30:00
    参数: communication.conciseness
    变化: 4 → 5 (+1)
    原因: 用户反馈说太详细

  2026-03-01T08:15:00
    参数: decision.autonomy
    变化: 3 → 4 (+1)
    原因: 用户反馈希望更主动
```

#### 4. 统计信息

```bash
python3 scripts/personality-manager.py stats
```

输出示例：
```json
{
  "total_adjustments": 3,
  "parameter_adjustments": {
    "communication.conciseness": 1,
    "decision.autonomy": 1
  },
  "last_adjustment": {
    "timestamp": "2026-03-01T09:30:00",
    "parameter_path": "communication.conciseness",
    "new_value": 5
  }
}
```

## 文件结构

```
/root/.openclaw/workspace/
├── personality/
│   ├── agents/
│   │   └── main.md  # 主 Agent 性格
│   ├── users/
│   │   └── main.md  # 用户偏好
│   ├── adjustments/
│   │   └── history.json  # 调整历史
│   └── preferences/
│       └── learned.json  # 学习的偏好
├── scripts/
│   └── personality-manager.py
└── config/
    └── personality-config.json
```

## 数据模型

### Personality 对象

```yaml
---
id: agent-personality-main
name: rxy的狗腿子
version: 1.0.0
created_at: 2026-03-01T09:00:00Z
updated_at: 2026-03-01T09:00:00Z

# 沟通风格
communication:
  conciseness: 4        # 简洁度（1-5）
  humor: 1              # 幽默感（1-5）
  formality: 3          # 正式度（1-5）
  emotional: 2          # 情感表达（1-5）

# 决策风格
decision:
  conservative: 2        # 保守度（1-5）
  certainty: 3          # 确定性（1-5）
  autonomy: 4           # 自主性（1-5）

# 工作风格
work:
  efficiency_first: true  # 效率优先
  perfectionism: 3       # 完美主义（1-5）
  learning_style: practice # 学习倾向

# 适配设置
adaptation:
  auto_adjust: true
  adjustment_rate: 0.1
  feedback_threshold: 10
```

## 性格维度说明

### 沟通风格

1. **简洁度（Conciseness）**
   - 1: 非常详细，提供所有细节
   - 3: 平衡，适中
   - 5: 非常简洁，只说核心信息

2. **幽默感（Humor）**
   - 1: 严肃，不幽默
   - 3: 偶尔幽默
   - 5: 很幽默，经常开玩笑

3. **正式度（Formality）**
   - 1: 随意，像朋友聊天
   - 3: 中等，专业但不拘谨
   - 5: 非常正式，像商务沟通

4. **情感表达（Emotional）**
   - 1: 非常理性，纯逻辑
   - 3: 适度，有情感但不过度
   - 5: 非常感性，情感丰富

### 决策风格

1. **保守度（Conservative）**
   - 1: 非常激进，高风险高回报
   - 3: 中等，平衡
   - 5: 非常保守，低风险低回报

2. **确定性（Certainty）**
   - 1: 模糊，经常说"可能"
   - 3: 中等，有一定把握
   - 5: 非常确定，说"肯定"

3. **自主性（Autonomy）**
   - 1: 被动，只回答问题
   - 3: 中等，偶尔主动
   - 5: 非常主动，主动提供背景和建议

## 工作流程

### 1. 性格加载流程

```
会话开始
    ↓ load_personality()
加载性格配置
    ↓ apply_to_responses()
应用到响应
```

### 2. 参数调整流程

```
收到反馈
    ↓ analyze_feedback()
分析反馈类型和方向
    ↓ check_threshold()
检查是否达到阈值
    ↓ adjust_parameter()
调整参数
    ↓ log_adjustment()
记录调整
```

### 3. 历史查询流程

```
用户请求
    ↓ get_adjustment_history()
获取调整历史
    ↓ filter_by_time()
按时间过滤
    ↓ return_filtered()
返回过滤结果
```

## 最佳实践

### 1. 性格定义

**保持一致性**:
- 调整不要改变核心性格
- 保留"rxy的狗腿子"的核心特质
- 调整要渐进，不要突变

**基于真实反馈**:
- 只在有足够多反馈时调整
- 区分真实反馈和临时情绪
- 记录调整原因

### 2. 参数调整

**渐进式调整**:
- 每次只调整 ±1
- 需要达到阈值（默认 5 次）才调整
- 不要同时调整多个参数

**记录完整信息**:
- 记录调整原因
- 记录调整时间和数值
- 便于后续分析和回滚

### 3. 调整管理

**定期回顾**:
- 每周回顾调整历史
- 分析哪些参数调整最多
- 评估调整效果

**提供回滚**:
- 保留历史版本
- 提供恢复默认选项
- 提供手动覆盖选项

## 故障排查

### 问题：性格文件不存在

**原因**：
- 首次使用，还没有创建性格文件

**解决方法**：
- 自动创建默认性格
- 或手动创建 `personality/agents/main.md`

### 问题：参数调整无效

**原因**：
- 参数路径格式错误
- 没有达到调整阈值

**解决方法**：
1. 检查参数路径格式（category.parameter）
2. 确认调整次数 >= 阈值（默认 5）
3. 检查配置中的 `adjustment_threshold`

### 问题：历史记录为空

**原因**：
- 还没有进行过参数调整
- 历史文件损坏

**解决方法**：
1. 进行一次参数调整
2. 或检查 `personality/adjustments/history.json`
3. 重新生成历史文件

## 性能优化

### 1. 缓存机制

- 缓存加载的性格
- 定期刷新缓存
- 避免频繁文件 I/O

### 2. 历史管理

- 限制历史记录数量（默认 100 条）
- 定期清理过期记录
- 按时间索引加速查询

### 3. 配置优化

- 延迟加载配置
- 按需加载用户偏好
- 减少不必要的计算

## 未来改进

- [ ] 多 Agent 支持
- [ ] 上下文感知的性格调整
- [ ] 情感识别和响应
- [ ] 个性化学术语生成
- [ ] 跨场景性格迁移

## 相关文档

- [阶段 4 设计文档](phase4-personalization-design.md)
- [Context Manager 指南](context-manager-guide.md)
- [Experience Manager 指南](experience-manager-guide.md)

## 支持

如有问题或建议，请创建 Issue 或联系维护者。
