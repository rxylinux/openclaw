# 阶段 3: 演化机制 - 设计文档

## 📋 目标

实现 A/B 测试和自动优化，让系统能够：
- 运行 A/B 测试
- 收集用户反馈
- 自动优化决策策略
- 识别性能瓶颈
- 生成演化报告

## 🎯 核心功能

### 1. A/B 测试框架

**目标**: 支持多种策略的并行测试

**测试场景**:
- 文件加载策略：按场景加载 vs 全部加载
- 场景检测：关键词匹配 vs 语义分析
- 检索排序：频率分数 vs 时间顺序
- 响应风格：简洁 vs 详细

**数据模型**:
```yaml
---
id: test-2026-03-01-001
type: ab_test
name: 文件加载策略对比
status: active
created_at: 2026-03-01T08:00:00Z
ended_at: null
duration_days: 7
variant_a:
  name: 按场景加载
  description: 使用 Context Manager 按场景动态加载
  config:
    use_context_manager: true
  metrics:
    context_size_avg: 9.5
    load_time_avg: 0.05
    user_satisfaction: 4.5
variant_b:
  name: 全部加载
  description: 加载所有文件
  config:
    use_context_manager: false
  metrics:
    context_size_avg: 25.3
    load_time_avg: 0.12
    user_satisfaction: 3.2
hypothesis: 按场景加载能减少上下文大小 50%+，提高满意度
---

# 文件加载策略对比测试

## 测试目的
对比 Context Manager 的按场景加载和传统的全部加载方式。

## 变体设计

### 变体 A（实验组）
- 使用 Context Manager
- 按场景动态加载文件
- 压缩可选文件

### 变体 B（对照组）
- 不使用 Context Manager
- 加载所有文件（SOUL.md、USER.md、MEMORY.md）

## 测量指标
- 上下文大小（KB）
- 加载时间（秒）
- 用户满意度（1-5 分）
- 任务完成率

## 预期结果
- 上下文大小减少 50%+
- 加载时间减少 40%+
- 用户满意度提升 1 分+
```

### 2. 反馈收集管道

**目标**: 收集多种反馈数据

**反馈类型**:
1. **显式反馈**（用户主动提供）
   - 好评/差评（👍/👎）
   - 星级评分（1-5 星）
   - 文字反馈

2. **隐式反馈**（从行为推断）
   - 任务完成率
   - 重试次数
   - 工具使用频率
   - 会话时长

3. **性能指标**
   - API 延迟
   - Token 消耗
   - 响应时间

**数据模型**:
```python
@dataclass
class Feedback:
    id: str
    type: str  # explicit, implicit, performance
    session_id: str
    message_id: str
    variant_id: str  # 关联到 A/B 测试变体

    # 显式反馈
    rating: Optional[int]  # 1-5
    reaction: Optional[str]  # 👍, 👎, ❤️, etc.
    text: Optional[str]

    # 隐式反馈
    task_completed: Optional[bool]
    retry_count: Optional[int]
    tool_usage: Optional[Dict[str, int]]

    # 性能指标
    latency_ms: Optional[int]
    token_consumption: Optional[int]
    response_time_ms: Optional[int]

    created_at: str
```

### 3. 自动优化脚本

**目标**: 基于反馈自动调整参数

**优化维度**:
1. **Context Manager 参数**
   - decay_factor: 从 0.95 调整到最优值
   - boost_on_use: 调整频率提升幅度
   - max_optional_files: 调整可选文件数量

2. **Experience Manager 参数**
   - 提取规则权重
   - 分类阈值

3. **场景检测参数**
   - 关键词权重
   - 场景映射

**优化算法**:
```python
def optimize_parameters(feedbacks: List[Feedback], current_params: Dict) -> Dict:
    """基于反馈优化参数"""

    # 1. 分析反馈
    positive_ratio = calculate_positive_ratio(feedbacks)
    avg_satisfaction = calculate_avg_satisfaction(feedbacks)

    # 2. 如果满意度低，调整参数
    if avg_satisfaction < 3.5:
        # 增加可选文件数量
        current_params['max_optional_files'] += 1

    # 3. 如果性能差，减少文件
    if get_avg_latency(feedbacks) > 500:
        current_params['max_optional_files'] -= 1
        current_params['decay_factor'] *= 1.05

    return current_params
```

### 4. 性能监控

**目标**: 识别性能瓶颈

**监控指标**:
- 响应时间（P50, P90, P99）
- API 调用次数
- Token 消耗
- 错误率
- 内存使用

**告警阈值**:
- 响应时间 > 5s: 警告
- 响应时间 > 10s: 严重
- 错误率 > 5%: 警告
- Token 消耗 > 100K/小时: 警告

**自动报告**:
- 每小时生成性能摘要
- 检测到异常时立即告警
- 每日生成性能趋势

### 5. 演化报告

**目标**: 定期生成演化报告

**报告内容**:
- 运行中的 A/B 测试
- 测试结果分析
- 参数优化历史
- 性能趋势
- 用户满意度变化
- 建议的改进

**报告格式**:
```markdown
# 📊 演化报告 - 2026年第9周

## 🧪 A/B 测试结果

### 测试 1: 文件加载策略
- **状态**: ✅ 完成
- **变体 A（按场景）**:
  - 上下文大小: 9.5 KB (-62%)
  - 加载时间: 0.05s (-58%)
  - 用户满意度: 4.5/5.0 (+41%)
- **变体 B（全部加载）**:
  - 上下文大小: 25.3 KB
  - 加载时间: 0.12s
  - 用户满意度: 3.2/5.0
- **结论**: ✅ 变体 A 胜出，应采纳

## 📈 参数优化

### Context Manager 参数
- `decay_factor`: 0.95 → 0.96 (满意度提升 3%)
- `max_optional_files`: 3 → 4 (任务完成率提升 5%)

### 场景检测参数
- 新增关键词: "特斯拉"、"财报"

## ⚡ 性能趋势

### 响应时间
- 本周平均: 1.2s
- 上周平均: 1.5s
- **改善**: 20%

### Token 消耗
- 本周平均: 15K/会话
- 上周平均: 20K/会话
- **改善**: 25%

## 😊 用户满意度

- 本周平均: 4.2/5.0
- 上周平均: 3.8/5.0
- **改善**: 0.4 分

## 💡 改进建议

1. 继续使用按场景加载策略
2. 考虑增加更多场景
3. 优化场景检测关键词
4. 实现语义分析（未来）
```

## 🏗️ 架构设计

### 组件关系

```
Evolution Manager (scripts/evolution-manager.py)
    ├── AB Test Runner
    │   ├── 创建测试
    │   ├── 分配变体
    │   └── 收集指标
    ├── Feedback Collector
    │   ├── 显式反馈
    │   ├── 隐式反馈
    │   └── 性能指标
    ├── Optimizer
    │   ├── 参数优化
    │   ├── 策略调整
    │   └── 配置更新
    ├── Performance Monitor
    │   ├── 响应时间
    │   ├── Token 消耗
    │   └── 错误率
    └── Report Generator
        └── 生成演化报告
```

### 文件结构

```
/root/.openclaw/workspace/
├── evolution/
│   ├── tests/
│   │   ├── active/
│   │   │   └── test-20260301-001.md
│   │   └── completed/
│   │       └── test-20260228-001.md
│   ├── feedbacks/
│   │   ├── explicit.json
│   │   ├── implicit.json
│   │   └── performance.json
│   ├── optimizations/
│   │   └── history.json
│   ├── reports/
│   │   ├── weekly/
│   │   └── daily/
│   └── metrics/
│       ├── response_time.json
│       ├── token_consumption.json
│       └── error_rate.json
├── scripts/
│   ├── evolution-manager.py
│   ├── ab-test-runner.py
│   ├── feedback-collector.py
│   ├── optimizer.py
│   └── generate-evolution-report.py
└── config/
    └── evolution-config.json
```

## 📊 数据模型

### ABTest 对象

```python
@dataclass
class ABTest:
    id: str
    name: str
    type: str
    status: str  # planning, active, paused, completed, cancelled
    created_at: str
    ended_at: Optional[str]
    duration_days: int

    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    hypothesis: str

    metrics: Dict[str, Any]
    conclusion: Optional[str]
```

### Feedback 对象

```python
@dataclass
class Feedback:
    id: str
    type: str
    session_id: str
    message_id: str
    variant_id: Optional[str]

    # 显式反馈
    rating: Optional[int]
    reaction: Optional[str]
    text: Optional[str]

    # 隐式反馈
    task_completed: Optional[bool]
    retry_count: Optional[int]
    tool_usage: Optional[Dict[str, int]]

    # 性能指标
    latency_ms: Optional[int]
    token_consumption: Optional[int]
    response_time_ms: Optional[int]

    created_at: str
```

## 🔄 工作流程

### 1. A/B 测试流程

```
创建测试
    ↓ assign_variants()
分配变体给会话
    ↓ collect_metrics()
收集指标
    ↓ analyze_results()
分析结果
    ↓ conclude_test()
得出结论
```

### 2. 反馈收集流程

```
用户交互
    ↓ collect_explicit_feedback()
收集显式反馈
    ↓ collect_implicit_feedback()
收集隐式反馈
    ↓ collect_performance_metrics()
收集性能指标
    ↓ save_feedback()
保存到存储
```

### 3. 优化流程

```
定期触发（每周日 20:00）
    ↓ analyze_feedbacks()
分析反馈
    ↓ calculate_optimal_params()
计算最优参数
    ↓ update_config()
更新配置
    ↓ log_optimization()
记录优化
```

### 4. 报告生成流程

```
定期触发（每周日 21:00）
    ↓ collect_metrics()
收集指标
    ↓ analyze_trends()
分析趋势
    ↓ generate_report()
生成报告
    ↓ send_report()
发送报告
```

## 📋 实施计划

### Week 1: 核心框架
- [ ] 实现 EvolutionManager 类
- [ ] 设计数据模型
- [ ] 创建目录结构
- [ ] 实现配置系统

### Week 2: A/B 测试
- [ ] 实现 ABTest 数据模型
- [ ] 实现变体分配
- [ ] 实现指标收集
- [ ] 实现结果分析

### Week 3: 反馈和优化
- [ ] 实现反馈收集
- [ ] 实现性能监控
- [ ] 实现优化算法
- [ ] 实现配置更新

### Week 4: 报告和集成
- [ ] 实现报告生成
- [ ] 实现自动化（Cron）
- [ ] 集成到工作流
- [ ] 性能测试

## 🎯 成功指标

- [ ] 能创建和管理 A/B 测试
- [ ] 能收集多种类型的反馈
- [ ] 能自动优化参数
- [ ] 能生成演化报告
- [ ] 优化后满意度提升 10%+
- [ ] 性能提升 15%+

## 📝 注意事项

### 数据隐私
- 不记录敏感信息
- 提供反馈 opt-out 选项
- 定期清理旧数据

### A/B 测试伦理
- 不影响用户体验
- 提前告知用户（可选）
- 快速回滚机制

### 优化谨慎性
- 参数调整要有幅度限制
- 记录所有优化历史
- 提供手动覆盖选项

## 🔮 未来改进

- [ ] 机器学习优化（贝叶斯优化）
- [ ] 多变量测试（A/B/C/D）
- [ ] 自动测试生成
- [ ] 实时参数调整
- [ ] 用户分群测试

---

*创建时间: 2026-03-01*
*状态: 📋 设计完成*
*下一阶段: 实施阶段*
