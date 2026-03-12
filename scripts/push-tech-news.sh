#!/bin/bash

# 科技新闻推送脚本
# 由cron定时调用，确保准时推送

# 工作目录
cd /root/.openclaw/workspace

# 运行新闻生成脚本
python3 /root/.openclaw/workspace/scripts/tech-news.py

# 检查是否成功生成
INDEX_FILE="/root/.openclaw/workspace/temp/latest-news-index.json"
if [ -f "$INDEX_FILE" ]; then
    # 检查文件时间戳，如果太旧（超过25小时）就不推送
    FILE_AGE=$(( ($(date +%s) - $(stat -c %Y "$INDEX_FILE")) / 3600 ))
    if [ $FILE_AGE -gt 25 ]; then
        echo "索引文件已过期（${FILE_AGE}小时前），跳过推送"
        exit 0
    fi

    # 读取拆分索引
    TOTAL_PARTS=$(python3 -c "import json; d=json.load(open('$INDEX_FILE')); print(d['total_parts'])")
    
    echo "开始推送，共 ${TOTAL_PARTS} 条消息"

    # 逐条发送
    SUCCESS_COUNT=0
    for i in $(seq 1 $TOTAL_PARTS); do
        PART_FILE="/root/.openclaw/workspace/temp/latest-news-$i.md"
        if [ ! -f "$PART_FILE" ]; then
            echo "警告：文件 $PART_FILE 不存在，跳过"
            continue
        fi
        
        echo "正在发送第 ${i}/${TOTAL_PARTS} 条..."
        
        # 使用message工具发送到飞书（必须指定target）
        python3 << PYTHON_CODE
import subprocess
import sys
import os

content = sys.argv[1]
part_num = int(sys.argv[2])
total_parts = int(sys.argv[3])
message = f"（第{part_num}条/共{total_parts}条）\n\n{content}"

result = subprocess.run([
    "openclaw", "message", "send",
    "--channel", "feishu",
    "--target", "oc_4d7341948c64c9b83d05bd45b8980a38",
    "--message", message
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"ERROR: 发送失败，返回码: {result.returncode}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    sys.exit(1)
else:
    print(f"Successfully sent part {part_num}/{total_parts}")
    sys.exit(0)
PYTHON_CODE
        
        SEND_RESULT=$?
        if [ $SEND_RESULT -eq 0 ]; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            echo "✓ 第 ${i} 条发送成功"
        else
            echo "✗ 第 ${i} 条发送失败（返回码: $SEND_RESULT）"
        fi
    done
    
    echo "推送完成：成功 ${SUCCESS_COUNT}/${TOTAL_PARTS} 条"

    # 更新推送时间
    python3 << 'PYTHON_SCRIPT'
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

# 保存状态
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"推送完成，已更新状态文件")
PYTHON_SCRIPT

    echo "科技新闻推送完成 - $(date)"
else
    echo "新闻生成失败，未找到索引文件"
    exit 1
fi
