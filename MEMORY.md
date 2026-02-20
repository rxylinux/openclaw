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
