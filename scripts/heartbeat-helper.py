#!/usr/bin/env python3
"""
心跳处理助手 - 自动检查并推送新闻，支持消息拆分
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def split_message_automatically(message, max_bytes=3000):
    """自动拆分长消息"""
    message_bytes = len(message.encode('utf-8'))
    
    if message_bytes <= max_bytes:
        return [message]
    
    # 简单的拆分策略：在换行处拆分
    lines = message.split('\n')
    parts = []
    current_part = ""
    current_bytes = 0
    
    for line in lines:
        line_bytes = len(line.encode('utf-8')) + 1  # +1 for newline
        
        if current_bytes + line_bytes > max_bytes:
            if current_part.strip():
                parts.append(current_part)
                current_part = ""
                current_bytes = 0
        
        current_part += line + '\n'
        current_bytes += line_bytes
    
    if current_part.strip():
        parts.append(current_part)
    
    return [p.strip() for p in parts]

def check_and_send_news():
    """检查是否需要推送新闻并发送"""
    workspace = Path('/root/.openclaw/workspace')
    index_file = workspace / 'temp' / 'latest-news-index.json'
    
    if not index_file.exists():
        print("没有找到新闻索引文件")
        return
    
    # 读取索引
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    total_parts = index.get('total_parts', 0)
    files = index.get('files', [])
    
    if not files:
        print("没有新闻文件")
        return
    
    # 读取所有消息
    all_messages = []
    for file_name in files:
        file_path = workspace / 'temp' / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                all_messages.append(content)
    
    if not all_messages:
        print("没有消息内容")
        return
    
    # 合并所有消息
    full_message = '\n'.join(all_messages)
    
    # 拆分消息
    parts = split_message_automatically(full_message)
    
    print(f"消息拆分: {len(parts)} 条")
    for i, part in enumerate(parts, 1):
        print(f"  第 {i} 条: {len(part.encode('utf-8'))} 字节")
    
    # 保存拆分后的消息
    output_dir = workspace / 'temp'
    split_files = []
    for i, part in enumerate(parts, 1):
        file_path = output_dir / f'news-split-{i}.txt'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(part)
        split_files.append(file_path.name)
    
    # 更新索引
    split_index_file = output_dir / 'news-split-index.json'
    with open(split_index_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_parts": len(parts),
            "files": split_files,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n拆分索引文件: {split_index_file}")
    return split_index_file

if __name__ == "__main__":
    check_and_send_news()
