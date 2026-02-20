#!/usr/bin/env python3
import json
import subprocess
import sys
import os

# 读取索引文件
index_file = "/root/.openclaw/workspace/temp/message-parts-index.json"
with open(index_file, 'r') as f:
    data = json.load(f)

total_parts = data['total_parts']
parts = data['parts']

# 逐条发送
for part in parts:
    content = part['content']
    index = part['index']
    total = part['total']

    # 添加前缀
    prefix = f"（第{index}条/共{total}条）\n\n"
    message = prefix + content

    # 写入临时文件
    tmp_file = f"/tmp/feishu_msg_{index}.txt"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(message)

    print(f"准备发送第{index}/{total}条消息，长度：{len(message.encode('utf-8'))}字节")
    print(f"消息已保存到：{tmp_file}")
