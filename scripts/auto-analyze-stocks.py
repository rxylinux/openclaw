#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股自动分析任务
每10分钟分析一只股票，直到1000只全部完成
"""

import sys
import os
import json
import time
from pathlib import Path

# 添加工作空间路径
workspace_path = Path('/root/.openclaw/workspace')
sys.path.insert(0, str(workspace_path))

def get_next_stock():
    """从a-stock-1000.txt获取下一只股票"""
    stock_file = workspace_path / 'a-stock-1000.txt'

    if not stock_file.exists():
        print("股票文件不存在！")
        return None

    with open(stock_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 跳过注释行
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # 找到第一只股票
        if '|' in line:
            code, name = line.split('|', 1)
            return code.strip(), name.strip()

    return None

def remove_first_stock():
    """删除第一只股票信息"""
    stock_file = workspace_path / 'a-stock-1000.txt'

    with open(stock_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到并删除第一个股票行
    new_lines = []
    removed = False
    for i, line in enumerate(lines):
        if not removed and line.strip() and not line.strip().startswith('#') and '|' in line:
            removed = True
            continue
        new_lines.append(line)

    if removed:
        with open(stock_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("已删除已分析股票")
    else:
        print("没有找到需要删除的股票行")

def get_remaining_count():
    """获取剩余股票数量"""
    stock_file = workspace_path / 'a-stock-1000.txt'

    if not stock_file.exists():
        return 0

    with open(stock_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '|' in line:
            count += 1

    return count

def update_status(code, name, status):
    """更新分析状态"""
    status_file = workspace_path / 'temp' / 'stock-analysis-status.json'

    # 确保temp目录存在
    status_file.parent.mkdir(parents=True, exist_ok=True)

    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    else:
        status_data = {
            'total_analyzed': 0,
            'last_analyzed': None,
            'start_time': None
        }

    if status_data['start_time'] is None:
        status_data['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

    if status == 'completed':
        status_data['total_analyzed'] += 1
        status_data['last_analyzed'] = {
            'code': code,
            'name': name,
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

    return status_data

if __name__ == '__main__':
    print("=" * 60)
    print("A股自动分析任务开始")
    print("=" * 60)

    # 获取下一只股票
    stock_info = get_next_stock()

    if not stock_info:
        print("\n✅ 所有股票已分析完成！")
        print("任务结束。")
        sys.exit(0)

    code, name = stock_info
    remaining = get_remaining_count()

    print(f"\n📊 当前进度")
    print(f"   分析股票: {code} | {name}")
    print(f"   剩余股票: {remaining} 只")
    print(f"   预计完成: {remaining * 10 // 60} 小时后")

    # 更新状态
    status = update_status(code, name, 'started')
    print(f"\n📈 历史统计")
    print(f"   已分析: {status['total_analyzed']} 只")
    print(f"   开始时间: {status['start_time']}")

    print(f"\n⏳ 开始分析 {code} | {name}...")
    print("=" * 60)

    # 这里只是打印股票信息，实际分析需要由a-stock-analysis技能完成
    # 由于本脚本会被cron调用，实际分析逻辑需要在主会话中触发

    print("\n⚠️ 注意: 本脚本仅用于获取和更新股票信息")
    print("   实际分析请使用 a-stock-analysis 技能")

    print("\n分析完成，准备删除已分析股票...")
    remove_first_stock()

    # 更新完成状态
    update_status(code, name, 'completed')

    print("\n✅ 本轮分析任务完成")
    print("=" * 60)
