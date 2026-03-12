#!/usr/bin/env python3
"""
OpenClaw Agent 状态监控看板

功能：
1. 模型信息（当前使用的模型、用量统计）
2. 会话统计（活跃会话数、消息统计）
3. 会话关键信息（最近活跃、通道分布）
4. 通道状态（通道类型、消息发送）
5. 系统资源（CPU、内存、磁盘）

使用：
    python3 openclaw-monitor.py              # 启动实时看板
    python3 openclaw-monitor.py --once      # 只显示一次
    python3 openclaw-monitor.py --json       # 输出JSON格式
"""

import os
import json
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加OpenClaw路径
OPENCLAW_ROOT = Path("/root/.openclaw")
WORKSPACE = OPENCLAW_ROOT / "workspace"

# 检查rich库是否安装
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich库未安装，将使用简化输出")
    print("安装: pip install rich")


class OpenClawMonitor:
    """OpenClaw状态监控器"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.workspace = WORKSPACE
        self.memory_dir = self.workspace / "memory"
        self.logs_dir = OPENCLAW_ROOT / "logs"
        self.sessions_dir = OPENCLAW_ROOT / "agents" / "main" / "sessions"

        # 加载配置
        self.config = self._load_config()
        self.cache = {}
        self.cache_ttl = 30  # 缓存30秒

    def _load_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        config_file = OPENCLAW_ROOT / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: 加载配置失败: {e}")
        return {}

    def _parse_timestamp_ms(self, ts_str: str) -> int:
        """解析时间戳字符串为毫秒"""
        try:
            if isinstance(ts_str, (int, float)):
                return int(ts_str)
            # ISO 8601 格式
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except:
            return 0

    def _get_sessions_from_files(self) -> List[Dict[str, Any]]:
        """从jsonl文件读取会话信息"""
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for transcript_file in self.sessions_dir.glob("*.jsonl"):
            try:
                session_id = transcript_file.stem

                # 解析文件
                message_count = 0
                last_timestamp = 0
                total_tokens = 0
                channel = 'unknown'
                model = 'unknown'

                with open(transcript_file, 'r') as f:
                    for line in f:
                        try:
                            msg = json.loads(line)

                            # 统计消息
                            if msg.get('type') == 'message':
                                message_count += 1

                                # 更新最后活跃时间
                                msg_timestamp = msg.get('timestamp', '')
                                if msg_timestamp:
                                    ts_ms = self._parse_timestamp_ms(msg_timestamp)
                                    if ts_ms > last_timestamp:
                                        last_timestamp = ts_ms

                                # 尝试获取通道信息
                                if 'deliveryContext' in msg:
                                    channel = msg['deliveryContext'].get('channel', 'unknown')

                                # 尝试获取模型信息
                                if 'model' in msg:
                                    model = msg['model']

                                # 检查 content 中的 token usage
                                message_data = msg.get('message', {})
                                content = message_data.get('content', [])
                                if isinstance(content, list):
                                    for item in content:
                                        if 'usage' in item:
                                            usage = item['usage']
                                            total_tokens += usage.get('totalTokens', 0)

                        except json.JSONDecodeError:
                            continue
                        except Exception:
                            continue

                # 只有有消息的会话才添加
                if message_count > 0:
                    sessions.append({
                        'session_id': session_id,
                        'message_count': message_count,
                        'last_timestamp': last_timestamp,
                        'total_tokens': total_tokens,
                        'channel': channel,
                        'model': model,
                        'file_size': transcript_file.stat().st_size,
                    })

            except Exception as e:
                continue

        # 按最后活跃时间排序
        sessions.sort(key=lambda x: x['last_timestamp'], reverse=True)
        return sessions

    def _get_heartbeat_state(self) -> Dict[str, Any]:
        """获取心跳状态"""
        heartbeat_file = self.memory_dir / "heartbeat-state.json"
        if heartbeat_file.exists():
            try:
                with open(heartbeat_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: 加载心跳状态失败: {e}")
        return {}

    def _get_system_stats(self) -> Dict[str, Any]:
        """获取系统资源统计"""
        stats = {}

        # CPU使用率
        try:
            result = subprocess.run(['sh', '-c',
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"],
                capture_output=True, text=True)
            stats['cpu_percent'] = float(result.stdout.strip()) if result.stdout.strip() else 0.0
        except:
            stats['cpu_percent'] = 0.0

        # 内存使用
        try:
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                stats['memory_total'] = int(parts[1])
                stats['memory_used'] = int(parts[2])
                stats['memory_percent'] = (stats['memory_used'] / stats['memory_total']) * 100
        except:
            stats['memory_percent'] = 0.0

        # 磁盘使用
        try:
            result = subprocess.run(['df', '-h', OPENCLAW_ROOT], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                stats['disk_used'] = parts[4]  # 百分比
                stats['disk_used_gb'] = parts[2]
                stats['disk_total_gb'] = parts[3]
        except:
            stats['disk_percent'] = 'N/A'

        # 进程状态
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            openclaw_processes = [line for line in result.stdout.split('\n') if 'openclaw' in line.lower()]
            stats['process_count'] = len(openclaw_processes)
        except:
            stats['process_count'] = 0

        return stats

    def _get_channel_stats(self, sessions: List[Dict]) -> Dict[str, int]:
        """统计通道使用情况"""
        channels = {}
        for session in sessions:
            channel = session.get('channel', 'unknown')
            channels[channel] = channels.get(channel, 0) + 1
        return channels

    def _format_timestamp(self, ts_ms: int) -> str:
        """格式化时间戳"""
        if not ts_ms or ts_ms == 0:
            return 'N/A'
        try:
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return 'Invalid'

    def build_dashboard(self) -> Optional[Layout]:
        """构建看板布局"""
        if not RICH_AVAILABLE:
            return None

        layout = Layout()

        # 获取数据
        sessions = self._get_sessions_from_files()
        heartbeat = self._get_heartbeat_state()
        system_stats = self._get_system_stats()
        channel_stats = self._get_channel_stats(sessions)

        # 统计总计
        total_sessions = len(sessions)
        total_messages = sum(s.get('message_count', 0) for s in sessions)
        total_tokens = sum(s.get('total_tokens', 0) for s in sessions)

        # 主布局
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        # 主要区域分为3列，使用5:6:5的比例让中间列更宽
        layout["main"].split_row(
            Layout(name="left", ratio=5),
            Layout(name="center", ratio=6),
            Layout(name="right", ratio=5)
        )

        # === Header ===
        now = datetime.now(timezone.utc)
        header_text = Text.assemble(
            ("🦊 OpenClaw Agent Monitor", "bold cyan"),
            (" | ", "white"),
            (f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC", "dim white"),
        )
        layout["header"].update(Panel(
            Align.center(header_text),
            style="on #1a1a2e"
        ))

        # === Left Column: 模型与系统 ===
        left_layout = Layout()
        left_layout.split_column(
            Layout(name="model_info", size=7),
            Layout(name="system_stats", size=9)
        )

        # 模型信息表格
        model_table = Table(title="🧠 模型信息", box=None, show_header=False)
        model_table.add_column("Metric", style="cyan", width=18, overflow="fold")
        model_table.add_column("Value", style="green", min_width=20, overflow="fold")

        # 从config获取模型信息
        model = self.config.get('model', 'zai/glm-4.7')
        model_table.add_row("Default Model", model)
        model_table.add_row("Total Tokens", f"{total_tokens:,}")
        model_table.add_row("Total Sessions", f"{total_sessions}")

        left_layout["model_info"].update(Panel(model_table, border_style="cyan"))

        # 系统资源表格
        sys_table = Table(title="💻 系统资源", box=None, show_header=False)
        sys_table.add_column("Resource", style="cyan", width=18, overflow="fold")
        sys_table.add_column("Usage", style="green", min_width=20, overflow="fold")

        cpu = system_stats.get('cpu_percent', 0)
        sys_table.add_row("CPU", f"{cpu:.1f}%")

        mem = system_stats.get('memory_percent', 0)
        sys_table.add_row("Memory", f"{mem:.1f}%")

        disk = system_stats.get('disk_used', 'N/A')
        if disk != 'N/A':
            disk_total = system_stats.get('disk_total_gb', '')
            sys_table.add_row("Disk", f"{disk} ({disk_total})")
        else:
            sys_table.add_row("Disk", disk)

        processes = system_stats.get('process_count', 0)
        sys_table.add_row("OpenClaw PIDs", f"{processes}")

        left_layout["system_stats"].update(Panel(sys_table, border_style="cyan"))

        layout["left"].update(left_layout)

        # === Center Column: 会话统计 ===
        center_layout = Layout()
        center_layout.split_column(
            Layout(name="session_stats", size=7),
            Layout(name="session_list", ratio=1)
        )

        # 会话统计表格
        stats_table = Table(title="📊 会话统计", box=None, show_header=False)
        stats_table.add_column("Metric", style="cyan", width=20, overflow="fold")
        stats_table.add_column("Value", style="green", min_width=25, overflow="fold")

        stats_table.add_row("Total Sessions", str(total_sessions))
        stats_table.add_row("Total Messages", f"{total_messages:,}")

        # 最近活跃
        if sessions:
            last_active = self._format_timestamp(sessions[0].get('last_timestamp', 0))
            stats_table.add_row("Last Active", last_active)

        center_layout["session_stats"].update(Panel(stats_table, border_style="yellow"))

        # Top会话列表
        session_table = Table(title="📋 Top Sessions (by messages)", box=None, show_header=True)
        session_table.add_column("Session", style="cyan", width=20, overflow="fold")
        session_table.add_column("Msgs", style="green", justify="right", width=8)
        session_table.add_column("Tokens", style="dim", justify="right", width=12)

        for session in sessions[:5]:
            session_id = session.get('session_id', 'unknown')
            # 截断过长的session id
            if len(session_id) > 20:
                session_id = session_id[:17] + '...'
            session_table.add_row(
                session_id,
                str(session.get('message_count', 0)),
                f"{session.get('total_tokens', 0):,}"
            )

        center_layout["session_list"].update(Panel(session_table, border_style="yellow"))

        layout["center"].update(center_layout)

        # === Right Column: 心跳状态 ===
        right_layout = Layout()
        right_layout.split_column(
            Layout(name="heartbeat_info", size=6),
            Layout(name="channel_info", size=5),
            Layout(name="tasks", size=5)
        )

        # 心跳信息表格
        hb_table = Table(title="💓 心跳状态", box=None, show_header=False)
        hb_table.add_column("Task", style="cyan", width=18, overflow="fold")
        hb_table.add_column("Status", style="green", min_width=20, overflow="fold")

        if heartbeat:
            hb_table.add_row("Use Cron", "✅" if heartbeat.get('use_cron') else "❌")
            hb_table.add_row("News Status", heartbeat.get('status', 'N/A'))
            news_count = heartbeat.get('news_sent_count', 0)
            hb_table.add_row("News Count", str(news_count))
        else:
            hb_table.add_row("Status", "No data")

        right_layout["heartbeat_info"].update(Panel(hb_table, border_style="red"))

        # 通道统计表格
        channel_table = Table(title="📡 通道分布", box=None, show_header=True)
        channel_table.add_column("Channel", style="cyan", width=15, overflow="fold")
        channel_table.add_column("Sessions", style="green", justify="right", width=10)

        for channel, count in sorted(channel_stats.items(), key=lambda x: x[1], reverse=True):
            channel_table.add_row(channel, str(count))

        right_layout["channel_info"].update(Panel(channel_table, border_style="magenta"))

        # 任务列表
        tasks_table = Table(title="⏰ 定时任务", box=None, show_header=False)
        tasks_table.add_column("Task", style="cyan", width=16, overflow="fold")
        tasks_table.add_column("Last", style="dim white", width=25, overflow="fold")

        if heartbeat and 'tasks' in heartbeat:
            for task_name, task_info in heartbeat['tasks'].items():
                last_run = str(task_info.get('last_run', 'N/A'))
                # 截断时间戳
                if len(last_run) > 18:
                    last_run = last_run[:18]
                tasks_table.add_row(task_name, last_run)

        right_layout["tasks"].update(Panel(tasks_table, border_style="magenta"))

        layout["right"].update(right_layout)

        # === Footer ===
        footer_text = Text.assemble(
            ("按 ", "white"),
            ("Ctrl+C", "bold yellow"),
            (" 退出", "white"),
            (" | ", "white"),
            ("刷新间隔: 5s", "dim white"),
        )
        layout["footer"].update(Panel(
            Align.center(footer_text),
            style="on #1a1a2e"
        ))

        return layout

    def print_simple(self):
        """打印简化版本（无rich）"""
        sessions = self._get_sessions_from_files()
        heartbeat = self._get_heartbeat_state()
        system_stats = self._get_system_stats()
        channel_stats = self._get_channel_stats(sessions)

        total_sessions = len(sessions)
        total_messages = sum(s.get('message_count', 0) for s in sessions)
        total_tokens = sum(s.get('total_tokens', 0) for s in sessions)

        print("=" * 60)
        print("🦊 OpenClaw Agent Monitor")
        print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("=" * 60)

        print("\n🧠 模型信息")
        print(f"  Default Model: {self.config.get('model', 'zai/glm-4.7')}")
        print(f"  Total Tokens: {total_tokens:,}")
        print(f"  Total Sessions: {total_sessions}")

        print("\n📊 会话统计")
        print(f"  Total Messages: {total_messages:,}")
        if sessions:
            last_active = self._format_timestamp(sessions[0].get('last_timestamp', 0))
            print(f"  Last Active: {last_active}")

        print("\n📡 通道分布")
        for channel, count in sorted(channel_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {channel}: {count}")

        print("\n📋 Top Sessions")
        for session in sessions[:5]:
            session_id = session.get('session_id', 'unknown')
            if len(session_id) > 25:
                session_id = session_id[:22] + '...'
            print(f"  {session_id}: {session.get('message_count', 0)} msgs, {session.get('total_tokens', 0):,} tokens")

        print("\n💻 系统资源")
        print(f"  CPU: {system_stats.get('cpu_percent', 0):.1f}%")
        print(f"  Memory: {system_stats.get('memory_percent', 0):.1f}%")
        print(f"  Disk: {system_stats.get('disk_used', 'N/A')}")
        print(f"  OpenClaw PIDs: {system_stats.get('process_count', 0)}")

        print("\n💓 心跳状态")
        if heartbeat:
            print(f"  Use Cron: {heartbeat.get('use_cron', False)}")
            print(f"  News Status: {heartbeat.get('status', 'N/A')}")
            print(f"  News Count: {heartbeat.get('news_sent_count', 0)}")
        else:
            print("  No data")

        print("\n" + "=" * 60)

    def run_once(self, json_output: bool = False):
        """运行一次"""
        sessions = self._get_sessions_from_files()
        heartbeat = self._get_heartbeat_state()
        system_stats = self._get_system_stats()
        channel_stats = self._get_channel_stats(sessions)

        total_sessions = len(sessions)
        total_messages = sum(s.get('message_count', 0) for s in sessions)
        total_tokens = sum(s.get('total_tokens', 0) for s in sessions)

        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": {
                "default": self.config.get('model', 'zai/glm-4.7'),
                "total_tokens": total_tokens,
                "total_sessions": total_sessions,
            },
            "sessions": {
                "count": total_sessions,
                "total_messages": total_messages,
                "by_channel": channel_stats,
                "top_sessions": [
                    {
                        "session_id": s.get('session_id'),
                        "message_count": s.get('message_count'),
                        "total_tokens": s.get('total_tokens'),
                        "last_timestamp": s.get('last_timestamp'),
                    }
                    for s in sessions[:10]
                ]
            },
            "system": system_stats,
            "heartbeat": heartbeat,
        }

        if json_output:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            if RICH_AVAILABLE:
                layout = self.build_dashboard()
                if layout:
                    self.console.print(layout)
                else:
                    self.print_simple()
            else:
                self.print_simple()

    def run(self, refresh_interval: int = 5):
        """运行实时看板"""
        if not RICH_AVAILABLE:
            print("Error: rich库未安装，无法启动实时看板")
            print("安装: pip install rich")
            print("或使用: python3 openclaw-monitor.py --once")
            return

        try:
            with Live(self.build_dashboard(), refresh_per_second=1/refresh_interval) as live:
                while True:
                    live.update(self.build_dashboard())
                    time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n\n退出监控")
        except Exception as e:
            print(f"Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='OpenClaw Agent状态监控')
    parser.add_argument('--once', action='store_true', help='只显示一次')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')

    args = parser.parse_args()

    monitor = OpenClawMonitor()

    if args.once:
        monitor.run_once(json_output=args.json)
    else:
        if args.json:
            print("Error: --json 只能和 --one 一起使用")
            sys.exit(1)
        monitor.run(refresh_interval=args.interval)


if __name__ == '__main__':
    main()
