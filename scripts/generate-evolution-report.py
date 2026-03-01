#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成演化报告并通过飞书推送
"""

import sys
import json
import subprocess
from pathlib import Path


def generate_evolution_report(days: int = 7) -> str:
    """获取演化报告（通过调用 evolution-manager.py）"""
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/scripts/evolution-manager.py', 'report', str(days)],
        capture_output=True,
        text=True
    )
    return result.stdout


def send_report(message: str):
    """发送报告"""
    # 检查消息长度
    message_bytes = len(message.encode('utf-8'))

    if message_bytes > 3000:
        # 保存到文件
        backup_path = Path("/root/.openclaw/workspace/temp/evolution-report.md")
        backup_path.parent.mkdir(exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"报告较长（{message_bytes} 字节），已保存到文件")
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

    print(f"生成演化报告（最近 {days} 天）...")

    # 生成报告
    report = generate_evolution_report(days)

    # 发送报告
    send_report(report)

    # 保存报告到文件
    report_path = Path("/root/.openclaw/workspace/temp/evolution-report-latest.md")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存到: {report_path}")


if __name__ == "__main__":
    main()
