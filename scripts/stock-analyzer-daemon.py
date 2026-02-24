#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票分析守护进程
循环读取股票、分析、发送、删除
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

# 添加工作空间路径
workspace_path = Path('/root/.openclaw/workspace')
sys.path.insert(0, str(workspace_path))

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
    for i, line in enumerate(lines):
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

def save_analyzed_stock(code, name):
    """保存已分析的股票记录"""
    log_file = workspace_path / 'temp' / 'analyzed-stocks.log'

    # 确保目录存在
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{timestamp}|{code}|{name}\n")

def main():
    """主循环"""
    print("=" * 60)
    print("🚀 A股自动分析守护进程启动")
    print("=" * 60)

    analyzed_count = 0
    start_time = time.time()

    while True:
        try:
            # 获取下一只股票
            stock_info = get_next_stock()

            if not stock_info:
                print("\n" + "=" * 60)
                print("✅ 所有股票已分析完成！")
                print(f"总计分析: {analyzed_count} 只股票")
                print(f"总耗时: {(time.time() - start_time) / 60:.1f} 分钟")
                print("=" * 60)
                break

            code, name = stock_info
            remaining = get_remaining_count()

            print("\n" + "=" * 60)
            print(f"📊 第 {analyzed_count + 1} 只股票")
            print(f"   股票: {code} | {name}")
            print(f"   剩余: {remaining} 只")
            print(f"   预计剩余时间: {remaining * 10 // 60} 小时 {remaining * 10 % 60} 分钟")
            print("=" * 60)

            # 生成分析命令
            # 这里我们生成一个待分析列表文件，供主会话读取
            next_stock_file = workspace_path / 'temp' / 'next-stock-to-analyze.json'

            with open(next_stock_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'code': code,
                    'name': name,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, ensure_ascii=False, indent=2)

            print(f"\n⏳ 已将股票信息写入: {next_stock_file}")
            print("   等待主会话分析...")

            # 等待分析完成（通过检查状态文件）
            status_file = workspace_path / 'temp' / 'analysis-complete.flag'

            max_wait = 600  # 最多等待10分钟
            wait_time = 0
            while wait_time < max_wait and not status_file.exists():
                time.sleep(30)  # 每30秒检查一次
                wait_time += 30

            if status_file.exists():
                print("\n✅ 分析完成")
                # 删除标志文件
                status_file.unlink()

                # 保存分析记录
                save_analyzed_stock(code, name)

                # 删除已分析的股票
                if remove_first_stock():
                    print("✅ 已更新股票列表")
                else:
                    print("⚠️  更新股票列表失败")

                analyzed_count += 1

                # 显示统计信息
                elapsed = time.time() - start_time
                avg_time = elapsed / analyzed_count
                print(f"\n📈 进度统计")
                print(f"   已分析: {analyzed_count} 只")
                print(f"   平均耗时: {avg_time / 60:.1f} 分钟/只")
                print(f"   总耗时: {elapsed / 60:.1f} 分钟")
            else:
                print("\n⚠️  等待超时，跳过这只股票")

            print("\n⏸️  等待10分钟后继续...")

            # 等待10分钟
            time.sleep(600)

        except KeyboardInterrupt:
            print("\n\n🛑 用户中断，停止分析")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)  # 出错后等待1分钟再继续

    print("\n守护进程结束")

if __name__ == '__main__':
    main()
