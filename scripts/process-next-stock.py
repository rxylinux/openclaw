#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理下一只股票分析
"""

import json
from pathlib import Path

workspace_path = Path('/root/.openclaw/workspace')

def get_next_stock():
    """从a-stock-1000.txt获取下一只股票"""
    stock_file = workspace_path / 'a-stock-1000.txt'

    if not stock_file.exists():
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
    for line in lines:
        if not removed and line.strip() and not line.strip().startswith('#') and '|' in line:
            removed = True
            continue
        new_lines.append(line)

    if removed:
        with open(stock_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

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

if __name__ == '__main__':
    # 获取下一只股票
    stock_info = get_next_stock()

    if not stock_info:
        print("ALL_DONE")  # 所有股票已完成
        sys.exit(0)

    code, name = stock_info
    remaining = get_remaining_count()

    # 输出JSON格式供主程序读取
    result = {
        'code': code,
        'name': name,
        'remaining': remaining,
        'status': 'pending'
    }

    print(json.dumps(result, ensure_ascii=False))
