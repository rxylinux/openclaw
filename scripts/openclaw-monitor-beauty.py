#!/usr/bin/env python3
"""
OpenClaw Agent 状态监控看板（美化版）

功能：
1. 模型信息（当前使用的模型、用量统计）
2. 会话统计（活跃会话数、消息统计）
3. 会话关键信息（最近活跃、通道分布）
4. 通道状态（通道类型、消息发送）
5. 系统资源（CPU、内存、磁盘）

使用：
    python3 openclaw-monitor-beauty.py         # 启动实时看板
    python3 openclaw-monitor-beauty.py --once  # 只显示一次
"""

import os
import json
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# 检查rich库是否安装
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    from rich.progress import BarColumn, Progress, TextColumn
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich库未安装，将使用简化输出")
    print("安装: pip install rich")


class OpenClawMonitorBeauty:
    """OpenClaw状态监控器（美化版）"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.sessions_dir = Path("/root/.openclaw/agents/main/sessions")
        self.memory_dir = Path("/root/.openclaw/workspace/memory")

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        config_file = Path("/root/.openclaw/config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _parse_timestamp_ms(self, ts_str: str) -> int:
        """解析时间戳字符串为毫秒"""
        try:
            if isinstance(ts_str, (int, float)):
                return int(ts_str)
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except:
            return 0

    def _get_sessions_info(self) -> List[Dict[str, Any]]:
        """获取会话信息"""
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for transcript_file in self.sessions_dir.glob("*.jsonl"):
            try:
                session_id = transcript_file.stem
                message_count = 0
                last_timestamp = 0

                with open(transcript_file, 'r') as f:
                    for line in f:
                        try:
                            msg = json.loads(line)
                            if msg.get('type') == 'message':
                                message_count += 1
                                msg_timestamp = msg.get('timestamp', '')
                                if msg_timestamp:
                                    ts_ms = self._parse_timestamp_ms(msg_timestamp)
                                    if ts_ms > last_timestamp:
                                        last_timestamp = ts_ms
                        except:
                            pass

                if message_count > 0:
                    sessions.append({
                        'session_id': session_id,
                        'message_count': message_count,
                        'last_timestamp': last_timestamp,
                    })
            except:
                pass

        # 按消息数排序
        sessions.sort(key=lambda x: x['message_count'], reverse=True)
        return sessions

    def _get_heartbeat_state(self) -> Dict[str, Any]:
        """获取心跳状态"""
        heartbeat_file = self.memory_dir / "heartbeat-state.json"
        if heartbeat_file.exists():
            try:
                with open(heartbeat_file, 'r') as f:
                    return json.load(f)
            except:
                pass
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
            result = subprocess.run(['df', '-h', "/root/.openclaw"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                stats['disk_used'] = parts[4]
                stats['disk_used_gb'] = parts[2]
                stats['disk_total_gb'] = parts[3]
        except:
            stats['disk_used'] = 'N/A'

        return stats

    def _format_timestamp(self, ts_ms: int) -> str:
        """格式化时间戳"""
        if not ts_ms or ts_ms == 0:
            return 'N/A'
        try:
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            return dt.strftime('%m-%d %H:%M')
        except:
            return 'Invalid'

    def _get_progress_bar(self, value: float, max_value: float = 100) -> str:
        """生成进度条"""
        try:
            bar = BarColumn(bar_width=20)
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                bar,
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            )
            progress.add_task("", completed=value, total=max_value)
            return progress
        except:
            return f"{value:.1f}%"

    def _get_emoji_for_value(self, value: float, thresholds: List[float], emojis: List[str]) -> str:
        """根据值获取对应的emoji"""
        for i, threshold in enumerate(thresholds):
            if value < threshold:
                return emojis[i]
        return emojis[-1]

    def build_dashboard(self):
        """构建看板"""
        # 获取数据
        sessions = self._get_sessions_info()
        heartbeat = self._get_heartbeat_state()
        system_stats = self._get_system_stats()

        total_sessions = len(sessions)
        total_messages = sum(s['message_count'] for s in sessions)

        # 创建标题
        now = datetime.now(timezone.utc)
        title = Text.assemble(
            ("🦊 ", "bold white"),
            ("OpenClaw", "bold cyan"),
            (" Agent", "bold white"),
            (" Monitor", "bold magenta"),
            (" | ", "dim"),
            (f"{now.strftime('%Y-%m-%d')}", "dim"),
            (" ", "dim"),
            (f"{now.strftime('%H:%M:%S')}", "bright_cyan"),
            (" UTC", "dim"),
        )

        # === 系统状态卡片 ===
        sys_table = Table(show_header=False, box=None, padding=(0, 1))
        sys_table.add_column("", style="cyan", width=16)
        sys_table.add_column("", style="bright_green", width=16)

        # CPU
        cpu = system_stats.get('cpu_percent', 0)
        cpu_emoji = self._get_emoji_for_value(cpu, [30, 70, 90], ['🟢', '🟡', '🟠', '🔴'])
        cpu_color = "green" if cpu < 50 else "yellow" if cpu < 80 else "red"
        sys_table.add_row(f"{cpu_emoji} CPU", f"[{cpu_color}]{cpu:.1f}%[/]")

        # 内存
        mem = system_stats.get('memory_percent', 0)
        mem_emoji = self._get_emoji_for_value(mem, [50, 80, 90], ['🟢', '🟡', '🟠', '🔴'])
        mem_color = "green" if mem < 50 else "yellow" if mem < 80 else "red"
        sys_table.add_row(f"{mem_emoji} 内存", f"[{mem_color}]{mem:.1f}%[/]")

        # 磁盘
        disk = system_stats.get('disk_used', 'N/A')
        if disk != 'N/A':
            disk_val = float(disk.rstrip('%'))
            disk_emoji = self._get_emoji_for_value(disk_val, [50, 80, 90], ['🟢', '🟡', '🟠', '🔴'])
            disk_color = "green" if disk_val < 50 else "yellow" if disk_val < 80 else "red"
            sys_table.add_row(f"{disk_emoji} 磁盘", f"[{disk_color}]{disk}[/]")

        # 分隔线
        sys_table.add_row("", "")

        # 会话统计
        sys_table.add_row("📊 会话总数", f"[bold cyan]{total_sessions:,}[/]")
        sys_table.add_row("💬 消息总数", f"[bold cyan]{total_messages:,}[/]")

        sys_panel = Panel(sys_table, title="📈 系统概览", border_style="cyan", padding=(1, 1))

        # === Top会话卡片 ===
        top_table = Table(show_header=True, box=None)
        top_table.add_column("排名", style="bright_yellow", width=4)
        top_table.add_column("会话ID", style="cyan", width=28)
        top_table.add_column("消息", style="green", justify="right", width=10)
        top_table.add_column("最后活跃", style="dim", width=14)

        for i, s in enumerate(sessions[:5], 1):
            session_id = s['session_id'][:28]
            rank_emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i-1]
            top_table.add_row(rank_emoji, session_id, f"{s['message_count']:,}", self._format_timestamp(s['last_timestamp']))

        top_panel = Panel(top_table, title="🏆 活跃会话 Top 5", border_style="yellow", padding=(1, 1))

        # === 心跳状态卡片 ===
        hb_table = Table(show_header=False, box=None, padding=(0, 1))
        hb_table.add_column("", style="cyan", width=16)
        hb_table.add_column("", style="yellow", width=30)

        if heartbeat:
            cron_status = "[green]✅ 已启用[/]" if heartbeat.get('use_cron') else "[red]❌ 未启用[/]"
            hb_table.add_row("⚙️ Cron状态", cron_status)

            news_status = heartbeat.get('status', 'N/A')
            status_emoji = "✅" if news_status == "completed" else "⏳"
            status_color = "green" if news_status == "completed" else "yellow"
            hb_table.add_row(f"{status_emoji} 新闻推送", f"[{status_color}]{news_status}[/]")

            news_count = heartbeat.get('news_sent_count', 0)
            hb_table.add_row("📰 推送次数", f"[bold cyan]{news_count:,}[/]")

            hb_table.add_row("", "")

            # 定时任务
            if 'tasks' in heartbeat:
                hb_table.add_row("⏰ 定时任务", "")
                for task_name, task_info in list(heartbeat['tasks'].items())[:2]:
                    last_run = str(task_info.get('last_run', 'N/A'))
                    # 提取日期时间
                    if 'T' in last_run:
                        dt = last_run.split('T')[0]
                        tm = last_run.split('T')[1].split('+')[0].split('.')[0][:5]
                        last_run = f"[dim]{dt}[/] [white]{tm}[/]"
                    task_emoji = "✅" if task_info.get('status') == 'completed' else "⏳"
                    # 格式化任务名称，避免太长
                    if len(task_name) > 14:
                        task_name = task_name[:14]
                    hb_table.add_row(f"  {task_emoji} {task_name}", last_run)
        else:
            hb_table.add_row("⚠️ 状态", "[dim]无数据[/]")

        hb_panel = Panel(hb_table, title="💓 心跳监控", border_style="red", padding=(1, 1))

        # === 底部状态栏 ===
        uptime = datetime.now(timezone.utc) - datetime(2026, 2, 23, 13, 31, 30, tzinfo=timezone.utc)
        days = uptime.days
        hours = uptime.seconds // 3600

        footer_text = Text.assemble(
            ("⚡ ", "green"),
            (f"运行时间: {days}天{hours}小时", "white"),
            ("  |  ", "dim"),
            ("🔄 ", "blue"),
            ("自动刷新: 5秒", "white"),
            ("  |  ", "dim"),
            ("⌨️  ", "yellow"),
            ("Ctrl+C 退出", "white"),
        )
        footer_panel = Panel(Align.center(footer_text), style="on #1a1a2e", padding=(0, 1))

        # 组合布局
        layout = [
            Panel(Align.center(title), style="on #1a1a2e", padding=(0, 1)),
            Rule(style="bright_blue"),
            Columns([sys_panel, top_panel, hb_panel], equal=True),
            Rule(style="bright_blue"),
            footer_panel,
        ]

        return layout

    def run_once(self):
        """运行一次"""
        panels = self.build_dashboard()

        if RICH_AVAILABLE:
            for panel in panels:
                self.console.print(panel)
        else:
            print("=" * 80)
            print(f"🦊 OpenClaw Agent Monitor - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("=" * 80)
            sessions = self._get_sessions_info()
            system_stats = self._get_system_stats()
            total_sessions = len(sessions)
            total_messages = sum(s['message_count'] for s in sessions)
            print(f"\n会话数: {total_sessions}")
            print(f"总消息数: {total_messages:,}")
            print(f"CPU: {system_stats.get('cpu_percent', 0):.1f}%")
            print(f"内存: {system_stats.get('memory_percent', 0):.1f}%")
            print(f"磁盘: {system_stats.get('disk_used', 'N/A')}")

    def run(self, refresh_interval: int = 5):
        """运行实时看板"""
        if not RICH_AVAILABLE:
            print("Error: rich库未安装")
            return

        try:
            with Live(self.build_dashboard(), refresh_per_second=1/refresh_interval) as live:
                while True:
                    live.update(self.build_dashboard())
                    time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n\n✨ 退出监控")
        except Exception as e:
            print(f"Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='OpenClaw Agent状态监控（美化版）')
    parser.add_argument('--once', action='store_true', help='只显示一次')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')

    args = parser.parse_args()

    monitor = OpenClawMonitorBeauty()

    if args.once:
        monitor.run_once()
    else:
        monitor.run(refresh_interval=args.interval)


if __name__ == '__main__':
    main()
