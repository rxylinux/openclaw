# Evolution Manager 使用指南

## 概述

Evolution Manager 是 OpenClaw 的演化管理器，用于：
- 创建和管理 A/B 测试
- 收集用户反馈（显式和隐式）
- 基于反馈自动优化参数
- 生成演化报告

## 功能特性

### 1. A/B 测试

支持创建和管理 A/B 测试：
- 定义测试变体（A 和 B）
- 为会话分配变体
- 记录测试指标
- 分析测试结果
- 得出结论

### 2. 反馈收集

收集多种类型的反馈：
- **显式反馈**: 评分（1-5）、反应（👍/👎）、文字反馈
- **隐式反馈**: 任务完成率、重试次数、工具使用
- **性能指标**: 响应时间、Token 消耗、API 延迟

### 3. 参数优化

基于反馈自动优化参数：
- Context Manager 参数（decay_factor, max_optional_files）
- Experience Manager 参数
- 自动调整幅度限制

### 4. 演化报告

定期生成演化报告：
- A/B 测试结果
- 用户满意度统计
- 性能指标
- 参数优化历史
- 改进建议

## 使用方法

### 命令行接口

#### 1. 创建 A/B 测试

```bash
python3 scripts/evolution-manager.py create-test <name> <type> <hypothesis>
```

示例：
```bash
# 创建文件加载策略对比测试
python3 scripts/evolution-manager.py create-test \
    "文件加载策略对比" \
    "loading_strategy" \
    "按场景加载相比全部加载能减少上下文大小 50%+"
```

#### 2. 分配变体

```bash
python3 scripts/evolution-manager.py assign <test_id> <session_id>
```

示例：
```bash
# 为会话分配变体
python3 scripts/evolution-manager.py assign test-20260301-001 session-12345
# 输出: 分配变体: A
```

#### 3. 记录测试指标

```bash
python3 scripts/evolution-manager.py record-metric <test_id> <variant> <name> <value>
```

#### 4. 结束测试

```bash
python3 scripts/evolution-manager.py conclude <test_id> <conclusion>
```

#### 5. 收集反馈

```bash
python3 scripts/evolution-manager.py feedback <type> <session_id> [args]
```

#### 6. 优化参数

```bash
python3 scripts/evolution-manager.py optimize
```

#### 7. 生成报告

```bash
python3 scripts/evolution-manager.py report [days]
```

#### 8. 统计信息

```bash
python3 scripts/evolution-manager.py stats
```

输出示例：
```json
{
  "tests": {
    "active": 1,
    "completed": 0,
    "total": 1
  },
  "feedbacks_count": 0,
  "last_updated": "2026-03-01T08:25:33.140839"
}
```

### 生成演化报告

```bash
python3 scripts/generate-evolution-report.py
```

生成的报告会：
1. 打印到控制台
2. 保存到 `temp/evolution-report-latest.md`

## 文件结构

```
/root/.openclaw/workspace/
├── evolution/
│   ├── tests/
│   │   ├── active/
│   │   │   └── test-20260301-001.md
│   │   └── completed/
│   ├── feedbacks/
│   │   ├── explicit.json
│   │   ├── implicit.json
│   │   └── performance.json
│   ├── optimizations/
│   │   └── history.json
│   ├── reports/
│   │   ├── weekly/
│   │   └── daily/
│   ├── metrics/
│   └── index.json
├── scripts/
│   ├── evolution-manager.py
│   └── generate-evolution-report.py
└── config/
    └── evolution-config.json
```

## 数据模型

### ABTest 对象

```yaml
---
id: test-20260301-001
type: loading_strategy
name: 文件加载策略对比
status: active
created_at: 2026-03-01T08:00:00Z
ended_at: null
duration_days: 7

variant_a:
  name: 按场景加载
  description: 使用 Context Manager

variant_b:
  name: 全部加载
  description: 加载所有文件

hypothesis: 按场景加载相比全部加载能减少上下文大小 50%+

metrics:
  test-20260301-001_A:
    context_size_avg: 9.5
    load_time_avg: 0.05
    user_satisfaction: 4.5
  test-20260301-001_B:
    context_size_avg: 25.3
    load_time_avg: 0.12
    user_satisfaction: 3.2

conclusion: 变体 A 胜出，应采纳
```

### Feedback 对象

```json
{
  "id": "feedback-20260301-001",
  "type": "explicit",
  "session_id": "session-12345",
  "message_id": "om_x123",
  "rating": 5,
  "reaction": "👍",
  "text": "非常好用！",
  "created_at": "2026-03-01T08:00:00Z"
}
```

## 最佳实践

### 1. A/B 测试设计

**明确假设**:
- 测试前明确假设
- 量化预期结果
- 定义成功标准

**控制变量**:
- 只改变一个变量
- 其他条件保持一致
- 样本量足够大

**测试时长**:
- 建议测试 7-14 天
- 确保统计显著性
- 可以提前停止（如果趋势明显）

### 2. 反馈收集

**显式反馈**:
- 在回复后主动询问评分
- 提供简单的评分选项（1-5 星）
- 收集具体建议

**隐式反馈**:
- 记录任务完成率
- 统计重试次数
- 追踪工具使用频率

**性能指标**:
- 持续监控响应时间
- 追踪 Token 消耗
- 监控错误率

### 3. 参数优化

**谨慎调整**:
- 每次只调整一个参数
- 调整幅度要小（10-20%）
- 观察效果后再继续

**记录历史**:
- 所有优化都要记录
- 包括原因和效果
- 便于回滚

**手动覆盖**:
- 提供手动调整选项
- 自动优化不满意时可以干预
- 保留"恢复默认"功能

## 工作流程

### 1. A/B 测试流程

```
创建测试
    ↓ assign_variant()
为会话分配变体
    ↓ record_metric()
收集指标
    ↓ conclude_test()
结束测试
```

### 2. 反馈收集流程

```
用户交互
    ↓ collect_explicit_feedback()
收集显式反馈
    ↓ collect_implicit_feedback()
收集隐式反馈
    ↓ collect_performance_feedback()
收集性能指标
    ↓ save_feedback()
保存到存储
```

### 3. 优化流程

```
定期触发（每周日 20:00）
    ↓ analyze_feedbacks()
分析反馈
    ↓ optimize_parameters()
优化参数
    ↓ update_config()
更新配置
```

## 故障排查

### 问题：测试指标无法记录

**原因**：
- test_id 或 variant 格式错误
- 测试状态不是 active

**解决方法**：
1. 检查 test_id 是否存在
2. 确认测试状态为 active
3. variant 格式为 "A" 或 "B"

### 问题：优化不生效

**原因**：
- 反馈数量不足
- 配置中自动优化关闭

**解决方法**：
1. 等待收集足够的反馈（>=10 条）
2. 检查 config 中的 `optimization.enabled`
3. 手动运行 `optimize` 命令

### 问题：报告内容为空

**原因**：
- 没有测试、反馈或优化数据
- 索引文件损坏

**解决方法**：
1. 检查 `evolution/index.json`
2. 确认有相关数据
3. 重新生成索引

## 性能优化

### 1. 反馈清理

- 定期清理过期反馈（默认 30 天）
- 使用 `retention_days` 配置
- 自动压缩历史数据

### 2. 测试管理

- 定期归档完成的测试
- 清理测试指标数据
- 保留关键测试结果

### 3. 索引优化

- 索引文件增量更新
- 避免全量扫描
- 定期重建索引

## 未来改进

- [ ] 机器学习优化（贝叶斯优化）
- [ ] 多变量测试（A/B/C/D）
- [ ] 自动测试生成
- [ ] 实时参数调整
- [ ] 用户分群测试

## 相关文档

- [阶段 3 设计文档](phase3-evolution-mechanism-design.md)
- [Context Manager 指南](context-manager-guide.md)
- [Experience Manager 指南](experience-manager-guide.md)

## 支持

如有问题或建议，请创建 Issue 或联系维护者。
