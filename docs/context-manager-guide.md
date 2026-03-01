# Context Manager 使用指南

## 概述

Context Manager 是 OpenClaw 的智能上下文管理器，用于：
- 自动检测用户意图场景
- 按场景动态加载相关文件
- 统计文件使用频率
- 压缩历史上下文

## 功能特性

### 1. 场景检测

支持 5 种场景：
- `investment_analysis` - 股票分析、投资研究
- `code_development` - 代码开发、技能创建
- `daily_conversation` - 日常对话、闲聊
- `news_research` - 新闻研究、信息收集
- `health_check` - 健康检查、系统维护

### 2. 动态文件加载

每个场景定义了：
- **必需文件**：必须加载的文件
- **可选文件**：根据使用频率动态加载
- **推荐技能**：场景相关的技能

### 3. 频率追踪

记录每个文件的使用情况：
- 使用次数
- 最后使用时间
- 频率分数（带衰减）

### 4. 上下文压缩

自动归档旧的 memory 文件，减少上下文大小。

## 使用方法

### 命令行接口

#### 1. 检测场景

```bash
python3 scripts/context-manager.py detect <message>
```

示例：
```bash
python3 scripts/context-manager.py detect "分析一下苹果公司的股票"
# 输出：检测到场景: investment_analysis
```

#### 2. 获取场景文件

```bash
python3 scripts/context-manager.py files <scenario>
```

示例：
```bash
python3 scripts/context-manager.py files investment_analysis
# 输出：必需文件和可选文件列表
```

#### 3. 获取场景摘要

```bash
python3 scripts/context-manager.py summary <scenario>
```

示例：
```bash
python3 scripts/context-manager.py summary investment_analysis
# 输出：JSON 格式的场景摘要
```

#### 4. 记录文件使用

```bash
python3 scripts/context-manager.py record <file_path> <scenario>
```

#### 5. 压缩历史文件

```bash
python3 scripts/context-manager.py compress [days]
```

默认压缩 7 天前的文件：
```bash
python3 scripts/context-manager.py compress 7
```

#### 6. 生成使用报告

```bash
python3 scripts/context-manager.py report
```

### 自动加载器

```bash
python3 scripts/auto-context-loader.py <message>
```

示例：
```bash
python3 scripts/auto-context-loader.py "帮我分析特斯拉的财报"
```

输出：
```
=== 上下文自动加载 ===
检测到场景: investment_analysis
场景描述: 股票分析、投资研究场景
总大小: 9.38 KB

必需文件（必须读取）:
  - /root/.openclaw/workspace/SOUL.md
  - /root/.openclaw/workspace/MEMORY.md
  - /root/.openclaw/workspace/INVESTMENT_PROFILE.md

推荐技能:
  - a-stock-analysis
  - 美股分析/完整股票拆解分析/complete-stock-analysis
  - 美股分析/风险与红旗扫描器/risk-flag-scanner
==================================================
```

## 配置文件

### context-config.json

位置：`/root/.openclaw/workspace/config/context-config.json`

定义场景与文件的映射关系。

#### 示例配置

```json
{
  "scenarios": {
    "investment_analysis": {
      "required_files": [
        "SOUL.md",
        "MEMORY.md",
        "INVESTMENT_PROFILE.md"
      ],
      "optional_files": [
        "memory/investment-notes.md"
      ],
      "skills": [
        "a-stock-analysis",
        "美股分析/完整股票拆解分析/complete-stock-analysis",
        "美股分析/风险与红旗扫描器/risk-flag-scanner"
      ],
      "description": "股票分析、投资研究场景"
    }
  },
  "compression": {
    "enabled": true,
    "max_memory_days": 7,
    "min_memory_size_bytes": 10000,
    "compression_ratio": 0.5
  },
  "frequency_tracking": {
    "enabled": true,
    "decay_factor": 0.95,
    "boost_on_use": 1.0
  }
}
```

#### 配置项说明

- `compression.enabled` - 是否启用压缩
- `compression.max_memory_days` - 保留最近 N 天的文件
- `compression.min_memory_size_bytes` - 最小文件大小（字节）
- `frequency_tracking.decay_factor` - 频率衰减系数（0-1）
- `frequency_tracking.boost_on_use` - 使用时增加的分数

## 使用统计

### context-usage.json

位置：`/root/.openclaw/workspace/memory/context-usage.json`

记录文件和场景的使用情况。

#### 数据结构

```json
{
  "file_stats": {
    "SOUL.md": {
      "use_count": 100,
      "last_used": "2026-03-01T06:27:00Z",
      "frequency_score": 100.0,
      "scenarios": ["investment_analysis", "code_development"]
    }
  },
  "scenario_stats": {
    "investment_analysis": {
      "use_count": 45,
      "last_used": "2026-03-01T06:27:00Z"
    }
  },
  "last_updated": "2026-03-01T06:27:00Z"
}
```

## 集成到会话

### Python 集成示例

```python
from scripts.auto_context_loader import load_context_for_message

# 在会话开始时
user_message = "帮我分析一下苹果公司的股票"
context = load_context_for_message(user_message)

# 读取必需文件
for file_path in context['required_files']:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 处理文件内容

# 使用推荐技能
for skill in context['skills']:
    # 加载技能 SKILL.md
    pass
```

### Shell 集成示例

```bash
#!/bin/bash

USER_MESSAGE="$1"
CONTEXT=$(python3 /root/.openclaw/workspace/scripts/auto-context-loader.py "$USER_MESSAGE")

# 解析 JSON 并加载文件
echo "$CONTEXT" | jq -r '.required_files[]' | while read file; do
    echo "加载文件: $file"
    # 加载文件逻辑
done
```

## 工作流程

### 会话开始时的流程

1. **用户发送消息**
2. **自动加载器检测场景**
   - 基于关键词匹配
   - 选择最高分场景
3. **获取场景文件**
   - 必需文件：全部加载
   - 可选文件：按频率排序，加载前 3 个
4. **记录使用情况**
   - 更新文件统计
   - 更新场景统计
5. **加载推荐技能**
   - 读取 SKILL.md
   - 按技能指导执行

### 定期维护

**每天：**
- 检查文件使用频率
- 清理冗余统计

**每周：**
- 压缩历史 memory 文件
- 生成使用报告
- 优化场景配置

## 最佳实践

### 1. 场景定义

- 保持场景简单、明确
- 避免重叠的职责
- 定期评估场景效果

### 2. 文件组织

- 必需文件：最小化，只保留核心
- 可选文件：按优先级排序
- 避免循环依赖

### 3. 频率追踪

- 定期清理低频文件
- 调整衰减参数
- 关注异常使用模式

### 4. 压缩策略

- 保留最近 7 天的文件
- 归档重要历史数据
- 定期清理归档目录

## 故障排查

### 问题：场景检测不准确

**解决方法：**
1. 检查关键词配置
2. 增加更多关键词
3. 考虑使用语义分析（未来版本）

### 问题：文件加载失败

**解决方法：**
1. 检查文件路径是否正确
2. 确认文件是否存在
3. 检查文件权限

### 问题：压缩导致数据丢失

**解决方法：**
1. 备份归档文件
2. 调整压缩参数
3. 关闭自动压缩

## 性能优化

### 1. 缓存机制

缓存频繁使用的场景配置：
```python
# 在 ContextManager 中添加
self._scenario_cache = {}
```

### 2. 延迟加载

只在需要时加载文件：
```python
# 使用生成器
def lazy_load_files(file_list):
    for file_path in file_list:
        yield read_file(file_path)
```

### 3. 异步记录

异步更新使用统计：
```python
import asyncio

async def async_record_usage(file_path, scenario):
    # 异步保存
    pass
```

## 未来改进

- [ ] 语义分析场景检测（使用向量相似度）
- [ ] 上下文预加载（基于历史预测）
- [ ] 智能文件分块（大文件按章节加载）
- [ ] 自动场景学习（基于用户反馈）
- [ ] 多级缓存（内存、磁盘、远程）

## 相关文档

- [AGENTS.md](../AGENTS.md) - 工作空间管理
- [MEMORY.md](../MEMORY.md) - 长期记忆
- [HEARTBEAT.md](../HEARTBEAT.md) - 定时任务

## 支持

如有问题或建议，请创建 Issue 或联系维护者。
