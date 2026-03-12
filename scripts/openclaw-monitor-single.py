#!/usr/bin/env python3
"""
OpenClaw Agent 状态监控看板（单列版）

功能：
1. 模型信息（当前使用的模型、用量统计）
2. 会话统计（活跃会话数、消息统计）
3. 会话关键信息（最近活跃、通道分布）
4. 通道状态（通道类型、消息发送）
5. 系统资源（CPU、内存、磁盘）

使用：
    python3 openclaw-monitor-single.py         # 启动实时看板
    python3 openclaw-monitor-single.py --once  # 只显示一次
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
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich库未安装，将使用简化输出")
    print("安装: pip install rich")


class OpenClawMonitorSingle:
    """OpenClaw状态监控器（单列版）"""

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

    def build_dashboard(self):
        """构建看板"""
        # 获取数据
        sessions = self._get_sessions_info()
        heartbeat = self._get_heartbeat_state()
        system_stats = self._get_system_stats()

        total_sessions = len(sessions)
        total_messages = sum(s['message_count'] for s in sessions)

        # 创建所有Panel
        panels = []

        # 标题
        now = datetime.now(timezone.utc)
        header = Text.assemble(
            ("🦊 OpenClaw Monitor", "bold cyan"),
            (" | ", "white"),
            (f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC", "dim white"),
        )
        panels.append(Panel(Align.center(header), style="on #1a1a2e"))

        # 系统状态表格
        sys_table = Table(show_header=True, box=None, padding=(0, 1))
        sys_table.add_column("指标", style="cyan", width=12)
        sys_table.add_column("值", style="green")

        sys_table.add_row("会话数", str(total_sessions))
        sys_table.add_row("总消息数", f"{total_messages:,}")
        sys_table.add_row("CPU", f"{system_stats.get('cpu_percent', 0):.1f}%")
        sys_table.add_row("内存", f"{system_stats.get('memory_percent', 0):.1f}%")
        sys_table.add_row("磁盘", f"{system_stats.get('disk_used', 'N/A')}")

        panels.append(Panel(sys_table, title="📊 系统状态", border_style="cyan"))

        # Top会话表格
        top_table = Table(show_header=True, box=None, padding=(0, 1))
        top_table.add_column("会话ID", style="cyan", width=24)
        top_table.add_column("消息数", style="green", justify="right", width=8)
        top_table.add_column("最后活跃", style="dim", width=12)

        for s in sessions[:5]:
            session_id = s['session_id'][:24]
            top_table.add_row(session_id, str(s['message_count']), self._format_timestamp(s['last_timestamp']))

        panels.append(Panel(top_table, title="📋 Top会话", border_style="yellow"))

        # 心跳状态表格
        hb_table = Table(show_header=False, box=None, padding=(0, 1))
        hb_table.add_column("任务", style="cyan", width=16)
        hb_table.add_column("状态", style="yellow", width=30)

        if heartbeat:
            hb_table.add_row("Cron状态", "✅ 已启用" if heartbeat.get('use_cron') else "❌ 未启用")
            hb_table.add_row("新闻推送", heartbeat.get('status', 'N/A'))
            hb_table.add_row("推送次数", str(heartbeat.get('news_sent_count', 0)))
            if 'tasks' in heartbeat:
                for task_name, task_info in list(heartbeat['tasks'].items())[:2]:
                    last_run = str(task_info.get('last_run', 'N/A'))
                    if len(last_run) > 25:
                        last_run = last_run[:25]
                    hb_table.add_row(task_name, last_run)
        else:
            hb_table.add_row("状态", "无数据")

        panels.append(Panel(hb_table, title="💓 心跳状态", border_style="red"))

        # 底部
        footer = Panel(Text("按 Ctrl+C 退出 | 刷新间隔: 5s", justify="center"), style="on #1a1a2e")
        panels.append(footer)

        return panels

    def run_once(self):
        """运行一次"""
        panels = self.build_dashboard()

        if RICH_AVAILABLE:
            for panel in panels:
                self.console.print(panel)
        else:
            print("=" * 70)
            print(f"🦊 OpenClaw Agent Monitor - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("=" * 70)
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
            print("\n\n退出监控")
        except Exception as e:
            print(f"Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='OpenClaw Agent状态监控（单列版）')
    parser.add_argument('--once', action='store_true', help='只显示一次')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')

    args = parser.parse_args()

    monitor = OpenClawMonitorSingle()

    if args.once:
        monitor.run_once()
    else:
        monitor.run(refresh_interval=args.interval)


if __name__ == '__main__':
    main()
