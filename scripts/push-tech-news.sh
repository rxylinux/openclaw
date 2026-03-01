#!/bin/bash

# 科技新闻推送脚本
# 由cron定时调用，确保准时推送

# 工作目录
cd /root/.openclaw/workspace

# 运行新闻生成脚本
python3 /root/.openclaw/workspace/scripts/tech-news.py

# 检查是否成功生成
if [ -f "/root/.openclaw/workspace/temp/latest-news-index.json" ]; then
    # 读取拆分索引
    INDEX_FILE="/root/.openclaw/workspace/temp/latest-news-index.json"
    TOTAL_PARTS=$(python3 -c "import json; d=json.load(open('$INDEX_FILE')); print(d['total_parts'])")

    # 逐条发送
    for i in $(seq 1 $TOTAL_PARTS); do
        PART_FILE="/root/.openclaw/workspace/temp/latest-news-$i.md"
        if [ -f "$PART_FILE" ]; then
            CONTENT=$(cat "$PART_FILE")
            # 使用message工具发送到飞书
            python3 -c "
import subprocess
import json
import sys
content = sys.argv[1]
part_num = $i
total_parts = $TOTAL_PARTS
result = subprocess.run([
    'openclaw', 'message', 'send',
    '--channel', 'feishu',
    '--message', f'（第{part_num}条/共{total_parts}条）\n\n{content}'
], capture_output=True, text=True)
print(result.stdout)
" "$CONTENT"
        fi
    done

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
