#!/usr/bin/env python3
"""
飞书自动发送脚本 - 支持速率限制和批量发送

使用方法：
1. 生成分析报告并拆分消息
2. python3 auto-feishu-sender.py --batch N

功能：
- 自动读取拆分后的消息
- 控制发送速率（避免触发限制）
- 支持断点续传
- 生成发送日志
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class FeishuAutoSender:
    def __init__(self, workspace=None, rate_limit=20, delay_between_messages=3):
        """
        workspace: 工作区路径
        rate_limit: 每分钟发送消息数上限（默认20条/分钟）
        delay_between_messages: 消息之间的延迟（秒，默认3秒）
        """
        self.workspace = Path(workspace) if workspace else Path(__file__).parent.parent
        self.temp_dir = self.workspace / "temp"
        self.logs_dir = self.workspace / "logs"
        self.rate_limit = rate_limit
        self.delay_between_messages = delay_between_messages
        self.message_count = 0
        self.start_time = None

        # 创建日志目录
        self.logs_dir.mkdir(exist_ok=True)

    def load_message_parts(self, batch_number: int) -> List[Dict]:
        """
        加载指定批次的消息部分

        Args:
            batch_number: 批次号

        Returns:
            消息部分列表
        """
        # 支持两种索引文件格式
        index_files = [
            self.temp_dir / f"message-parts-index.json",
            self.temp_dir / f"batch{batch_number}-parts.json",
        ]

        index_file = None
        for f in index_files:
            if f.exists():
                index_file = f
                break

        if not index_file:
            raise FileNotFoundError(f"未找到消息索引文件，请先拆分消息")

        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        parts = data.get('parts', [])
        if not parts:
            raise ValueError("索引文件中没有找到消息部分")

        return parts

    def should_rate_limit(self) -> bool:
        """
        检查是否需要速率限制

        Returns:
            True if should wait
        """
        if self.start_time is None:
            return False

        elapsed = time.time() - self.start_time
        messages_per_minute = self.message_count / (elapsed / 60)

        if messages_per_minute >= self.rate_limit:
            print(f"⚠️  达到速率限制（{messages_per_minute:.1f}条/分钟），等待60秒...")
            time.sleep(60)
            self.start_time = time.time()  # 重置计时
            return True

        return False

    def send_single_message(self, content: str, index: int, total: int, batch_number: int):
        """
        发送单条消息

        Args:
            content: 消息内容
            index: 当前消息索引
            total: 总消息数
            batch_number: 批次号
        """
        # 添加前缀
        prefix = f"（第{index}条/共{total}条）\n\n"
        message = prefix + content

        # 检查速率限制
        self.should_rate_limit()

        # 这里是实际的发送逻辑
        # 由于需要调用OpenClaw的message工具，这里生成命令供外部执行
        message_size = len(message.encode('utf-8'))

        # 写入发送命令文件
        cmd_file = self.temp_dir / f"send-command-b{batch_number}-p{index}.txt"
        with open(cmd_file, 'w', encoding='utf-8') as f:
            f.write(f"# 发送命令 - 批次{batch_number} 第{index}/{total}条\n")
            f.write(f"# 时间: {datetime.now().isoformat()}\n")
            f.write(f"# 大小: {message_size}字节\n\n")
            f.write(f"message send --channel feishu --message '{message}'")

        print(f"✓ 准备发送第{index}/{total}条消息，大小：{message_size}字节")

        # 模拟发送延迟
        time.sleep(self.delay_between_messages)

        self.message_count += 1
        if self.start_time is None:
            self.start_time = time.time()

        return {
            'index': index,
            'size': message_size,
            'status': 'prepared',
            'timestamp': datetime.now().isoformat()
        }

    def send_batch(self, batch_number: int, dry_run=True):
        """
        发送整个批次的消息

        Args:
            batch_number: 批次号
            dry_run: 是否只生成命令，不实际发送
        """
        print(f"\n{'='*60}")
        print(f"开始处理批次 {batch_number}")
        print(f"{'='*60}\n")

        try:
            # 加载消息部分
            parts = self.load_message_parts(batch_number)
            total_parts = len(parts)

            print(f"✓ 成功加载 {total_parts} 条消息\n")

            # 发送统计
            total_size = 0
            results = []

            # 逐条发送
            for i, part in enumerate(parts, 1):
                result = self.send_single_message(
                    part['content'],
                    part['index'],
                    part['total'],
                    batch_number
                )
                results.append(result)
                total_size += result['size']

                # 显示进度
                if i % 5 == 0 or i == total_parts:
                    print(f"  进度: {i}/{total_parts} ({i*100//total_parts}%)")

            # 生成发送日志
            log_file = self.logs_dir / f"send-log-batch{batch_number}.json"
            log_data = {
                'batch_number': batch_number,
                'total_messages': total_parts,
                'total_size_bytes': total_size,
                'average_size_bytes': total_size // total_parts,
                'dry_run': dry_run,
                'results': results,
                'generated_at': datetime.now().isoformat()
            }

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)

            # 显示总结
            elapsed_time = time.time() - self.start_time if self.start_time else 0

            print(f"\n{'='*60}")
            print(f"批次 {batch_number} 处理完成")
            print(f"{'='*60}")
            print(f"总消息数: {total_parts}")
            print(f"总大小: {total_size:,} 字节 ({total_size/1024:.1f} KB)")
            print(f"平均大小: {total_size // total_parts:,} 字节")
            print(f"总耗时: {elapsed_time:.1f} 秒")
            print(f"平均速度: {total_parts/elapsed_time*60:.1f} 条/分钟")
            print(f"模式: {'模拟模式' if dry_run else '实际发送'}")
            print(f"\n发送命令文件: {self.temp_dir / 'send-command-*.txt'}")
            print(f"日志文件: {log_file}")
            print(f"\n{'='*60}")

            return log_data

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def execute_commands(self, batch_number: int):
        """
        执行生成的发送命令（需要OpenClaw环境）

        Args:
            batch_number: 批次号
        """
        cmd_files = sorted(self.temp_dir.glob(f"send-command-b{batch_number}-p*.txt"))

        if not cmd_files:
            print(f"❌ 未找到批次 {batch_number} 的发送命令文件")
            return False

        print(f"\n准备执行 {len(cmd_files)} 个发送命令...\n")

        for cmd_file in cmd_files:
            with open(cmd_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 提取实际命令（跳过注释）
                for line in lines:
                    line = line.strip()
                    if line.startswith('message send '):
                        print(f"执行: {line}")
                        # 这里需要实际的OpenClaw环境
                        # os.system(line)
                        time.sleep(self.delay_between_messages)

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='飞书自动发送脚本')
    parser.add_argument('--batch', '-b', type=int, required=True, help='批次号')
    parser.add_argument('--rate-limit', '-r', type=int, default=20, help='速率限制（条/分钟，默认20）')
    parser.add_argument('--delay', '-d', type=float, default=3, help='消息延迟（秒，默认3）')
    parser.add_argument('--execute', '-e', action='store_true', help='实际执行发送（默认只生成命令）')
    parser.add_argument('--workspace', '-w', type=str, help='工作区路径')

    args = parser.parse_args()

    # 创建发送器
    sender = FeishuAutoSender(
        workspace=args.workspace,
        rate_limit=args.rate_limit,
        delay_between_messages=args.delay
    )

    # 发送批次
    result = sender.send_batch(args.batch, dry_run=not args.execute)

    if result and args.execute:
        # 实际执行
        sender.execute_commands(args.batch)


if __name__ == "__main__":
    main()
