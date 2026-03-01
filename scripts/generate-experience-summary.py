#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成经验摘要并通过飞书推送
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


def get_experience_summary(days: int = 7) -> str:
    """获取经验摘要（通过调用 experience-manager.py）"""
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/scripts/experience-manager.py', 'summary', str(days)],
        capture_output=True,
        text=True
    )
    return result.stdout


def send_to_feishu(message: str):
    """发送消息到飞书"""
    # 检查消息长度
    message_bytes = len(message.encode('utf-8'))

    if message_bytes > 3000:
        # 保存到文件
        backup_path = Path("/root/.openclaw/workspace/temp/experience-summary.md")
        backup_path.parent.mkdir(exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"消息较长（{message_bytes} 字节），已保存到文件")
        print(f"使用: cat {backup_path}")
        return False
    else:
        # 直接打印，让用户看到
        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")
        return True


def main():
    days = 7  # 最近 7 天

    print(f"生成经验摘要（最近 {days} 天）...")

    # 生成摘要
    summary = get_experience_summary(days)

    # 发送到飞书
    send_to_feishu(summary)

    # 保存摘要到文件
    summary_path = Path("/root/.openclaw/workspace/temp/experience-summary-latest.md")
    summary_path.parent.mkdir(exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"摘要已保存到: {summary_path}")


if __name__ == "__main__":
    main()
