#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
from datetime import datetime, timezone

def send_message_via_cli(content, part_num, total_parts):
    """
    通过命令行发送消息到飞书
    """
    message = f"（第{part_num}条/共{total_parts}条）\n\n{content}"

    # 使用 openclaw message send 命令
    result = subprocess.run([
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", "oc_4d7341948c64c9b83d05bd45b8980a38",
        "--message", message
    ], capture_output=True, text=True, cwd="/root/.openclaw/workspace")

    if result.returncode != 0:
        print(f"ERROR: 发送失败（返回码: {result.returncode}）")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return False

    print(f"✓ 第 {part_num}/{total_parts} 条发送成功")
    return True

def main():
    # 读取索引文件
    index_file = "/root/.openclaw/workspace/temp/latest-news-index.json"
    if not os.path.exists(index_file):
        print("ERROR: 索引文件不存在")
        return 1

    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)

    total_parts = index.get('total_parts', 0)
    print(f"开始推送，共 {total_parts} 条消息")

    # 逐条发送
    success_count = 0
    for i in range(1, total_parts + 1):
        part_file = f"/root/.openclaw/workspace/temp/latest-news-{i}.md"

        if not os.path.exists(part_file):
            print(f"警告：文件 {part_file} 不存在，跳过")
            continue

        with open(part_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if send_message_via_cli(content, i, total_parts):
            success_count += 1
        else:
            print(f"✗ 第 {i} 条发送失败")

    print(f"推送完成：成功 {success_count}/{total_parts} 条")

    # 更新推送状态
    state_file = "/root/.openclaw/workspace/memory/heartbeat-state.json"
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        state['last_push_time'] = datetime.now(timezone.utc).isoformat()
        state['last_check_time'] = datetime.now(timezone.utc).isoformat()
        state['news_sent_count'] = state.get('news_sent_count', 0) + 1
        state['status'] = 'completed'

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print("推送状态已更新")

    # 如果全部成功，返回0；否则返回1
    return 0 if success_count == total_parts else 1

if __name__ == '__main__':
    exit(main())
