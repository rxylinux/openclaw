#!/bin/bash

# 科技新闻推送脚本（修复版）
# 修复了 Python 代码中的变量名问题

# 工作目录
cd /root/.openclaw/workspace

# 运行新闻生成脚本
python3 /root/.openclaw/workspace/scripts/tech-news.py

# 检查是否成功生成
if [ ! -f "/root/.openclaw/workspace/temp/latest-news-index.json" ]; then
    echo "新闻生成失败，未找到索引文件"
    exit 1
fi

# 读取拆分索引
INDEX_FILE="/root/.openclaw/workspace/temp/latest-news-index.json"
TOTAL_PARTS=$(python3 -c "import json; d=json.load(open('$INDEX_FILE')); print(d['total_parts'])")

echo "准备发送 $TOTAL_PARTS 条新闻"

# 逐条发送（直接使用 message 命令，避免 Python 代码错误）
for i in $(seq 1 $TOTAL_PARTS); do
    PART_FILE="/root/.openclaw/workspace/temp/latest-news-$i.md"
    if [ -f "$PART_FILE" ]; then
        CONTENT=$(cat "$PART_FILE")
        
        # 计算消息长度
        CONTENT_BYTES=$(echo -n "$CONTENT" | wc -c)
        
        # 如果超过 3000 字节，使用拆分工具
        if [ $CONTENT_BYTES -gt 3000 ]; then
            echo "消息 $i 超过 3000 字节，使用拆分工具"
            
            # 写入临时文件
            echo "$CONTENT" > /tmp/news-part-$i.md
            
            # 调用拆分工具
            python3 /root/.openclaw/workspace/scripts/message-sender.py --file /tmp/news-part-$i.md
            
            # 读取拆分索引
            SPLIT_INDEX="/root/.openclaw/workspace/temp/message-parts-index.json"
            
            # 逐条发送
            python3 << PYTHON_SCRIPT
import json
import subprocess

with open('$SPLIT_INDEX', 'r') as f:
    index = json.load(f)

for j in range(index['total_parts']):
    part_file = f"/root/.openclaw/workspace/temp/message-part-{j+1}.txt"
    with open(part_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = subprocess.run([
        'openclaw', 'message', 'send',
        '--channel', 'feishu',
        '--message', f"（第{j+1}条/共{index['total_parts']}条）\n\n{content}"
    ], capture_output=True, text=True)
    
    print(f"已发送第 {j+1} 部分")

PYTHON_SCRIPT
            
            # 清理临时文件
            rm -f /tmp/news-part-$i.md
        else
            # 直接发送
            echo "消息 $i 不超过 3000 字节，直接发送"
            
            python3 << PYTHON_SCRIPT
import subprocess

content = '''$CONTENT'''

result = subprocess.run([
    'openclaw', 'message', 'send',
    '--channel', 'feishu',
    '--message', f"（第{i}条/共{TOTAL_PARTS}条）\n\n{content}"
], capture_output=True, text=True)

print(result.stdout)
PYTHON_SCRIPT
        fi
        
        # 等待一小段时间，避免被限流
        sleep 3
    done
done

# 更新推送时间
python3 << PYTHON_SCRIPT
import json
from datetime import datetime, timezone

# 读取当前状态
state_file = "/root/.openclaw/workspace/memory/heartbeat-state.json"
with open(state_file, 'r') as f:
    state = json.load(f)

# 更新推送时间
state['last_push_time'] = datetime.now(timezone.utc).isoformat()
state['last_check_time'] = datetime.now(timezone.utc).isoformat()
state['news_sent_count'] = state.get('news_sent_count', 0) + 1
state['status'] = 'completed'

# 保存状态
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"推送完成，已更新状态文件")
PYTHON_SCRIPT

echo "科技新闻推送完成 - $(date)"
