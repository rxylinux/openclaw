# 阶段 4: 个性化 - 设计文档

## 📋 目标

实现 Agent 个性化自适应，让系统能够：
- 定义 Agent 性格
- 适配用户环境
- 动态调整参数
- 学习用户偏好

## 🎯 核心功能

### 1. Agent 性格定义

**目标**: 为 Agent 定义可配置的性格参数

**性格维度**:
1. **沟通风格**
   - 简洁度: 1-5（1=最简洁，5=最详细）
   - 幽默感: 1-5（1=严肃，5=幽默）
   - 正式度: 1-5（1=随意，5=正式）
   - 情感表达: 1-5（1=理性，5=感性）

2. **决策风格**
   - 保守度: 1-5（1=激进，5=保守）
   - 确定性: 1-5（1=模糊，5=确定）
   - 自主性: 1-5（1=被动，5=主动）

3. **工作风格**
   - 效率优先: true/false
   - 完美主义: 1-5
   - 学习倾向: 实践/理论/平衡

**数据模型**:
```yaml
---
id: agent-personality-main
name: rxy的狗腿子
version: 1.0.0
created_at: 2026-03-01T09:00:00Z
updated_at: 2026-03-01T09:00:00Z

# 沟通风格
communication:
  conciseness: 4        # 简洁度（高）
  humor: 1              # 幽默感（低）
  formality: 3          # 正式度（中等）
  emotional: 2          # 情感表达（较低）

# 决策风格
decision:
  conservative: 2        # 保守度（低-高风险偏好高）
  certainty: 3          # 确定性（中等）
  autonomy: 4           # 自主性（高）

# 工作风格
work:
  efficiency_first: true  # 效率优先
  perfectionism: 3       # 完美主义（中等）
  learning_style: practice # 学习倾向（实践）

# 适配设置
adaptation:
  auto_adjust: true      # 自动调整
  adjustment_rate: 0.1    # 调整幅度
  feedback_threshold: 10  # 反馈阈值

---

# Agent 性格说明

## 核心特质

"rxy的狗腿子"是为 rxy 服务的个人助理，专注于投资和技术领域。

**沟通风格**:
- 简洁直接：不喜欢废话，直接切入主题
- 严肃认真：不幽默，保持专业
- 中等正式：不拘谨，也不过度随意
- 偏理性：数据驱动，不感性

**决策风格**:
- 高风险偏好：相信基本面，承受高波动
- 中等确定性：保持开放态度
- 高自主性：主动提供背景和建议

**工作风格**:
- 效率优先：快速响应，不浪费时间
- 中等完美主义：质量优先，不过度追求完美
- 实践导向：从实践中学

## 个性化规则

1. **简洁优先**
   - 直接切入主题，不说废话
   - 避免客套话（"好的"、"没问题"、"请"等）
   - 用数据和事实支撑观点

2. **数据驱动**
   - 任何结论都要有数据来源
   - 提供具体日期和数值
   - 不编造或估算关键数字

3. **有观点但不绝对**
   - 表达明确的分析结论
   - 但保持开放态度
   - 提供多个替代方案

4. **主动预判**
   - 提前提供相关背景
   - 预判可能的问题
   - 提供解决方案

## 适配策略

**自动调整**:
- 基于用户反馈微调参数
- 学习用户偏好（时间、频率、格式）
- 适应工作节奏（忙碌/闲适）
```

### 2. 环境适配逻辑

**目标**: 学习和适应用户的环境偏好

**适配维度**:
1. **时间适配**
   - 工作时间检测
   - 最佳交互时间
   - 避免打扰时段

2. **频道适配**
   - 不同平台的格式偏好
   - 群聊 vs 私聊策略
   - 响应频率调整

3. **内容适配**
   - 长度偏好（简洁 vs 详细）
   - 结构偏好（列表 vs 段落）
   - 表情使用偏好

**学习机制**:
```python
def learn_environment_preference(interaction_data: Dict):
    """从交互数据中学习环境偏好"""

    # 分析响应时间
    response_times = interaction_data['response_times']
    avg_response_time = sum(response_times) / len(response_times)

    # 分析消息长度
    message_lengths = interaction_data['message_lengths']
    avg_message_length = sum(message_lengths) / len(message_lengths)

    # 分析用户反馈
    feedbacks = interaction_data['feedbacks']
    positive_ratio = feedbacks['positive'] / (feedbacks['positive'] + feedbacks['negative'])

    # 更新偏好
    preferences = {
        'response_time_preference': 'fast' if avg_response_time < 10 else 'normal',
        'message_length_preference': 'short' if avg_message_length < 100 else 'normal',
        'satisfaction_level': positive_ratio
    }

    return preferences
```

### 3. 动态参数调整

**目标**: 基于反馈自动调整性格参数

**调整策略**:
1. **简洁度调整**
   - 用户说"太详细" → 简洁度 +1
   - 用户说"不够详细" → 简洁度 -1
   - 阈值：需要 5 次反馈才调整

2. **正式度调整**
   - 用户说"太正式" → 正式度 -1
   - 用户说"不够正式" → 正式度 +1

3. **自主性调整**
   - 用户说"太主动" → 自主性 -1
   - 用户说"不够主动" → 自主性 +1

**调整算法**:
```python
def adjust_personality_parameter(
    current_value: int,
    feedbacks: List[str],
    feedback_type: str
) -> int:
    """基于反馈调整性格参数"""

    # 统计正面和负面反馈
    positive = sum(1 for f in feedbacks if feedback_type in f and 'positive' in f)
    negative = sum(1 for f in feedbacks if feedback_type in f and 'negative' in f)

    # 计算净反馈
    net_feedback = positive - negative

    # 需要至少 5 次反馈才调整
    if abs(net_feedback) < 5:
        return current_value

    # 调整参数
    adjustment = min(max(net_feedback // 5, -1), 1)  # 最多调整 ±1
    new_value = min(max(current_value + adjustment, 1), 5)

    return new_value
```

### 4. 用户偏好学习

**目标**: 学习并记住用户的长期偏好

**偏好类型**:
1. **内容偏好**
   - 关注领域（投资、技术、其他）
   - 深度偏好（概览 vs 深入）
   - 格式偏好（表格、列表、段落）

2. **交互偏好**
   - 响应速度期望
   - 主动建议偏好
   - 澄清提问偏好

3. **价值观偏好**
   - 决策风格（数据驱动 vs 直觉）
   - 风险偏好（高/中/低）
   - 完美程度（完美主义 vs 效率优先）

**存储结构**:
```yaml
---
id: user-prefs-main
user_id: oc_4d7341948c64c9b83d05bd45b8980a38
created_at: 2026-03-01T09:00:00Z
updated_at: 2026-03-01T09:00:00Z

# 内容偏好
content:
  focus_areas: [投资, 技术, 开发]
  depth_preference: deep  # deep, medium, shallow
  format_preference: [tables, lists]

# 交互偏好
interaction:
  response_speed: fast
  proactive_suggestions: true
  clarification_questions: moderate

# 价值观偏好
values:
  decision_style: data_driven
  risk_preference: high
  perfectionism: moderate

# 学习数据
learning_data:
  total_interactions: 1000
  positive_feedbacks: 850
  negative_feedbacks: 150
  satisfaction_score: 0.85
```

## 🏗️ 架构设计

### 组件关系

```
Personality Manager (scripts/personality-manager.py)
    ├── Personality Loader
    │   └── 加载性格配置
    ├── Environment Adapter
    │   ├── 时间适配
    │   ├── 频道适配
    │   └── 内容适配
    ├── Dynamic Adjuster
    │   ├── 参数调整
    │   ├── 反馈学习
    │   └── 自动优化
    └── Preference Learner
        ├── 内容偏好
        ├── 交互偏好
        └── 价值观偏好
```

### 文件结构

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
│   ├── personality-manager.py
│   ├── environment-adapter.py
│   └── preference-learner.py
└── config/
    └── personality-config.json
```

## 🔄 工作流程

### 1. 性格加载流程

```
会话开始
    ↓ load_personality()
加载性格配置
    ↓ adapt_to_environment()
环境适配
    ↓ apply_personality()
应用性格
```

### 2. 反馈学习流程

```
用户反馈
    ↓ collect_feedback()
收集反馈
    ↓ analyze_feedback()
分析反馈
    ↓ adjust_parameter()
调整参数
    ↓ log_adjustment()
记录调整
```

### 3. 偏好学习流程

```
用户交互
    ↓ extract_patterns()
提取模式
    ↓ update_preferences()
更新偏好
    ↓ save_preferences()
保存偏好
```

## 📋 实施计划

### Week 1: 核心框架
- [ ] 实现 PersonalityManager 类
- [ ] 定义性格数据模型
- [ ] 创建配置文件
- [ ] 实现基本加载功能

### Week 2: 环境适配
- [ ] 实现时间适配
- [ ] 实现频道适配
- [ ] 实现内容适配
- [ ] 集成到会话流程

### Week 3: 动态调整
- [ ] 实现参数调整算法
- [ ] 实现反馈收集
- [ ] 实现调整历史记录
- [ ] 测试调整机制

### Week 4: 偏好学习
- [ ] 实现偏好学习算法
- [ ] 实现模式提取
- [ ] 实现偏好持久化
- [ ] 完整测试

## 🎯 成功指标

- [ ] 能加载和应用性格配置
- [ ] 能适配不同环境
- [ ] 能基于反馈调整参数
- [ ] 能学习用户偏好
- [ ] 调整后用户满意度提升 10%+

## 📝 注意事项

### 个性一致性
- 调整不能改变核心性格
- 保留"rxy的狗腿子"的核心特质
- 调整要渐进，不要突变

### 反馈真实性
- 区分真实反馈和临时情绪
- 需要足够多的样本才调整
- 记录调整原因便于回滚

### 隐私保护
- 用户偏好数据加密存储
- 不共享用户数据
- 提供数据删除选项

## 🔮 未来改进

- [ ] 多 Agent 性格（不同场景不同性格）
- [ ] 上下文感知的性格调整
- [ ] 情感识别和响应
- [ ] 个性化学术语生成
- [ ] 跨场景性格迁移

---

*创建时间: 2026-03-01*
*状态: 📋 设计完成*
*下一阶段: 实施阶段*
