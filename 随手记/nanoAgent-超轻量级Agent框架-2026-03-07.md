# nanoAgent 项目研究总结

**项目地址:** https://github.com/sanbuphy/nanoAgent
**研究日期:** 2026-03-07
**作者:** sanbuphy

---

## 📋 项目概述

### Slogan
> "The question is not what you look at, but what you see." — Henry David Thoreau

### 定位
使用 OpenAI function calling 实现的最小化 AI Agent。

---

## 🎯 核心理念

**设计目标:** "If you can read 100 lines of Python, you understand agents."

- **极简主义**: 代码量约 100 行
- **易理解**: 核心逻辑简单直观
- **可扩展**: 基础功能完整，易于扩展

---

## 🔧 技术架构

### 技术栈
- **编程语言:** Python
- **核心依赖:** OpenAI API
- **功能调用:** OpenAI Function Calling
- **模型:** gpt-4o-mini（默认，可配置）

### 核心工具

| 工具名 | 功能 | 说明 |
|-------|------|------|
| execute_bash | 执行bash命令 | 运行任何shell命令 |
| read_file | 读取文件 | 获取文件内容 |
| write_file | 写入文件 | 创建或修改文件 |

---

## 🔄 工作原理

### Agent 主循环

```python
# 定义工具
tools = [{"type": "function", "function": {...}}]

# Agent循环
for _ in range(max_iterations):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools
    )
    
    if not response.choices[0].message.tool_calls:
        return response.choices[0].message.content
    
    # 执行工具调用
    for tool_call in response.choices[0].message.tool_calls:
        result = available_functions[tool_call.function.name](**args)
        messages.append({"role": "tool", "content": result})
```

### 执行流程

1. **接收任务** - 用户提出需求
2. **决策工具** - Agent选择使用哪个工具
3. **执行工具** - 运行bash/read/write
4. **返回结果** - 将结果反馈给模型
5. **重复循环** - 直到任务完成

**核心:** 简单的循环：`call model → execute tools → repeat`

---

## 💡 关键特性

### 1. 错误处理
- 容错机制：即使工具调用参数错误或引用未知工具，也不会崩溃
- 错误返回：将错误信息明确返回给模型
- 持续运行：确保Agent能继续执行

### 2. 自动迭代
- 最大迭代次数限制
- 自动判断任务完成
- 工具链式调用

### 3. 环境配置
支持多平台环境变量配置：

**macOS/Linux:**
```bash
export OPENAI_API_KEY='your-key-here'
export OPENAI_BASE_URL='https://api.openai.com/v1'  # optional
export OPENAI_MODEL='gpt-4o-mini'  # optional
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='your-key-here'
$env:OPENAI_BASE_URL='https://api.openai.com/v1'
$env:OPENAI_MODEL='gpt-4o-mini'
```

---

## 🚀 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 使用示例

**列出当前目录的Python文件:**
```bash
python agent.py "list all python files in current directory"
```

**创建文件:**
```bash
python agent.py "create a file called hello.txt with 'Hello World'"
```

**读取文件:**
```bash
python agent.py "read contents of README.md"
```

---

## 📊 能力展示

### 系统操作
- 查看当前目录和文件
- 列出文件信息
- 执行系统命令

### 文件操作
- 创建Python脚本
- 读取文件内容
- 写入数据到文件

### 组合任务
- 查找所有.py文件并统计代码行数
- 批量处理文件
- 多步骤自动化任务

---

## 🎨 项目亮点

### 1. 极简设计
- 代码量约100行，极易阅读
- 核心逻辑清晰：模型调用 → 工具执行 → 循环迭代
- 没有复杂的抽象层

### 2. 功能完整
- 虽然代码少，但功能不弱
- 支持三大核心工具（bash/read/write）
- 能完成多步骤复杂任务

### 3. 教育意义
- 适合学习Agent基本原理
- 理解Function Calling机制
- 快速上手Agent开发

### 4. 实用性强
- 可以直接用于文件操作自动化
- 系统管理任务
- 批量文件处理

---

## 🎯 应用场景

### 适用场景
1. **学习和教学**
   - 理解Agent工作原理
   - 学习Function Calling
   - 快速原型开发

2. **自动化脚本**
   - 批量文件操作
   - 系统管理任务
   - 简单的数据处理

3. **集成开发**
   - 作为其他项目的Agent基础
   - 嵌入到现有系统
   - 自定义工具扩展

### 不适用场景
- 复杂多Agent协作
- 需要长期记忆和状态管理
- 大规模生产环境

---

## 📝 代码结构

```
nanoAgent/
├── agent.py           # 主Agent程序
├── requirements.txt   # 依赖列表
├── README.md         # 英文文档
└── README_CN.md      # 中文文档
```

**核心文件:** `agent.py` (约100行）

---

## 🔍 与其他框架对比

| 特性 | nanoAgent | LangChain | AutoGPT |
|------|-----------|-----------|---------|
| 代码量 | ~100行 | 数千行 | 数千行 |
| 学习曲线 | 平 | 陡 | 陡 |
| 功能完整性 | 基础 | 完整 | 完整 |
| 可定制性 | 高 | 中 | 低 |
| 适合学习 | ✅ | ❌ | ❌ |
| 生产就绪 | ❌ | ✅ | ✅ |

---

## 💡 启发与思考

### 设计哲学
1. **简单即是美**
   - 100行代码实现核心功能
   - 没有过度设计
   - 清晰的职责分离

2. **渐进增强**
   - 从简单开始，逐步扩展
   - 先实现核心，再优化细节
   - 保持代码可维护性

3. **Function Calling的威力**
   - OpenAI的Function Calling简化了工具调用
   - 模型自动选择合适的工具
   - 减少大量手动编码

### 对OpenClaw的启发
1. **模块化设计**
   - 工具定义清晰
   - 易于添加新工具
   - 工具可独立测试

2. **错误处理机制**
   - Agent不应因为单个工具失败而崩溃
   - 错误信息应该反馈给模型，让它自我修正
   - 需要最大迭代次数限制防止无限循环

3. **状态管理**
   - 当前nanoAgent是无状态的（每次重新开始）
   - 长期应用可能需要持久化状态
   - 考虑添加记忆机制

---

## 🚀 改进建议

### 短期改进
1. **增强工具集**
   - 添加网络请求工具（http_get）
   - 添加文件搜索工具（search_files）
   - 添加Git操作工具

2. **日志记录**
   - 详细记录每次工具调用
   - 记录模型决策过程
   - 便于调试和分析

3. **配置文件**
   - 使用配置文件管理API密钥
   - 支持多环境配置
   - 更灵活的工具定义

### 中期改进
1. **持久化记忆**
   - 添加向量数据库存储上下文
   - 支持RAG检索
   - 记住用户偏好和历史

2. **多模态支持**
   - 图像处理工具
   - 文档解析工具
   - 音视频处理

3. **任务规划**
   - 添加任务分解能力
   - 支持子任务管理
   - 任务进度跟踪

### 长期改进
1. **Agent协作**
   - 多Agent通信机制
   - 任务分发和协调
   - 共享上下文和状态

2. **插件系统**
   - 动态加载工具
   - 第三方工具市场
   - 社区贡献工具库

---

## 📚 参考价值

### 学习Agent开发
- **理解核心概念**: Function Calling、工具调用、循环执行
- **实践最小原型**: 亲手实现一个简单Agent
- **扩展到复杂系统**: 基于nanoAgent理解LangChain等框架

### 项目借鉴
- **代码组织**: 工具定义、Agent循环、错误处理
- **架构设计**: 模块化、可扩展、易测试
- **文档撰写**: 清晰的README、丰富的示例

---

## ⭐ 总结

### 优点
✅ 代码极简（~100行）
✅ 易于理解和学习
✅ 功能完整（bash/read/write）
✅ 错误处理健壮
✅ 适合作为教学案例

### 不足
❌ 功能相对基础
❌ 缺少记忆机制
❌ 无持久化状态
❌ 不适合复杂生产环境

### 适用人群
- ✅ Agent开发初学者
- ✅ 想理解Agent原理的开发者
- ✅ 需要快速原型的项目
- ✅ 教育/培训场景

---

## 📖 核心代码片段

```python
# 工具定义
tools = [{
    "type": "function",
    "function": {
        "name": "execute_bash",
        "description": "Run any bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    }
}]

# Agent主循环
for _ in range(max_iterations):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools
    )
    
    if not response.choices[0].message.tool_calls:
        return response.choices[0].message.content
    
    # 执行工具调用
    for tool_call in response.choices[0].message.tool_calls:
        result = available_functions[tool_call.function.name](**args)
        messages.append({"role": "tool", "content": result})
```

---

**研究完成时间:** 2026-03-07 16:30 (GMT+8)
**文档版本:** v1.0
