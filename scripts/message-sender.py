#!/usr/bin/env python3
"""
消息发送助手 - 自动拆分长消息
"""
import sys
import json
from pathlib import Path

def split_message(message, max_bytes=3000):
    """将消息拆分成多条，适应飞书客户端显示"""
    message_bytes = len(message.encode('utf-8'))
    
    if message_bytes <= max_bytes:
        return [{"content": message, "index": 1, "total": 1}]
    
    # 按段落拆分（以空行或换行为界）
    parts = []
    current_part = ""
    current_bytes = 0
    
    # 按行分割
    lines = message.split('\n')
    
    for line in lines:
        line_bytes = len(line.encode('utf-8'))
        
        # 如果单行就超过限制，强制拆分
        if line_bytes > max_bytes:
            # 保存当前部分
            if current_part.strip():
                parts.append(current_part)
                current_part = ""
                current_bytes = 0
            
            # 拆分长行
            for i in range(0, len(line), max_bytes):
                chunk = line[i:i+max_bytes]
                parts.append(chunk)
            continue
        
        # 检查是否应该开始新的一部分
        if current_bytes + line_bytes > max_bytes:
            if current_part.strip():
                parts.append(current_part)
                current_part = ""
                current_bytes = 0
        
        current_part += line + '\n'
        current_bytes += line_bytes + 1  # +1 for newline
    
    # 添加最后一部分
    if current_part.strip():
        parts.append(current_part)
    
    # 格式化输出
    result = []
    for i, part in enumerate(parts, 1):
        result.append({
            "content": part.strip(),
            "index": i,
            "total": len(parts)
        })
    
    return result

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 message-sender.py '消息内容'")
        print("或者: python3 message-sender.py --file /path/to/message.txt")
        sys.exit(1)
    
    if sys.argv[1] == '--file':
        # 从文件读取
        file_path = Path(sys.argv[2])
        message = file_path.read_text(encoding='utf-8')
    else:
        # 从参数读取
        message = sys.argv[1]
    
    # 拆分消息
    parts = split_message(message)
    
    if len(parts) == 1:
        print("无需拆分")
        print(f"长度: {len(message.encode('utf-8'))} 字节")
    else:
        print(f"已拆分为 {len(parts)} 条消息:")
        for i, part in enumerate(parts, 1):
            print(f"  第 {i} 条: {len(part['content'].encode('utf-8'))} 字节")
    
    # 保存到索引文件
    workspace = Path(__file__).parent.parent / "temp"
    workspace.mkdir(exist_ok=True)
    
    index_file = workspace / "message-parts-index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_parts": len(parts),
            "parts": parts,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    # 保存每条消息到单独文件
    for i, part in enumerate(parts, 1):
        part_file = workspace / f"message-part-{i}.txt"
        with open(part_file, 'w', encoding='utf-8') as f:
            f.write(part['content'])
    
    print(f"\n索引文件: {index_file}")
    print(f"消息文件: {workspace}/message-part-*.txt")

if __name__ == "__main__":
    main()
