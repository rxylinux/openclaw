#!/usr/bin/env python3
"""
批量发送股票分析到飞书
"""
import json
import time
from pathlib import Path

def send_all_batches():
    """发送所有批次到飞书"""
    target_id = "on_8c7eaa61db2cfd8a28d81931b7c3f7d0"
    workspace = Path("/root/.openclaw/workspace")

    # 查找所有批次文件
    batch_files = sorted(workspace.glob("stock-batch-*.md"))

    print(f"找到 {len(batch_files)} 个批次文件")

    # 生成发送命令
    send_commands = []
    for i, batch_file in enumerate(batch_files, 1):
        content = batch_file.read_text(encoding='utf-8')

        # 检查消息长度
        message_bytes = len(content.encode('utf-8'))

        send_commands.append({
            "batch": i,
            "file": str(batch_file),
            "size": message_bytes,
            "content": content
        })

    print(f"\n前10批已经手动发送，继续发送第11-{len(send_commands)}批")

    # 只发送第11批及以后的
    for cmd in send_commands[10:]:
        print(f"\n发送第{cmd['batch']}批...")
        print(f"  文件: {cmd['file']}")
        print(f"  大小: {cmd['size']}字节")

        # 保存到临时文件
        temp_file = Path(f"/tmp/batch-{cmd['batch']}.txt")
        temp_file.write_text(cmd['content'], encoding='utf-8')

        print(f"  ✓ 准备完成")

        # 添加延迟避免频率限制
        time.sleep(1)

    print(f"\n✓ 所有批次准备完成")
    print(f"  总计: {len(send_commands)}批")
    print(f"  已发送: 10批")
    print(f"  待发送: {len(send_commands)-10}批")

if __name__ == "__main__":
    send_all_batches()
