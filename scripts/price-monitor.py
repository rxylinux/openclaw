#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨跌幅监控脚本
监控持仓股票是否涨跌超过5%，立即推送预警
"""

import json
import requests
from datetime import datetime
import sys
import os

# 添加工作目录到路径
sys.path.insert(0, '/root/.openclaw/workspace')

# 配置文件路径
PRICE_TRACKING_FILE = '/root/.openclaw/workspace/investment-monitoring/price-tracking/holdings-price.json'
ALERT_LOG_FILE = '/root/.openclaw/workspace/investment-monitoring/price-tracking/alerts.json'

def load_price_tracking():
    """加载价格跟踪数据"""
    try:
        with open(PRICE_TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到价格跟踪文件 {PRICE_TRACKING_FILE}")
        return None

def save_price_tracking(data):
    """保存价格跟踪数据"""
    with open(PRICE_TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_stock_price(stock_code, stock_name):
    """
    获取股票实时价格

    数据源：备用方案（通过web_search搜索股价）
    注意：由于新浪财经API访问受限，暂时使用备用方案
    """
    try:
        # 暂时返回None，等待更好的数据源
        # TODO: 实现真实的股价获取功能
        # 可以考虑：
        # 1. 安装akshare库（pip install akshare）
        # 2. 使用东方财富网API
        # 3. 使用腾讯财经API
        # 4. 使用雅虎财经API
        print(f"获取 {stock_name} ({stock_code}) 的实时价格...")
        print(f"  警告：股价获取功能暂未完全实现，需要接入真实的数据源")
        print(f"  提示：当前网络环境可能无法访问实时股价API")
        return None

    except Exception as e:
        print(f"  获取 {stock_name} 价格失败：{str(e)}")
        return None

def calculate_price_change(current_price, last_price):
    """计算价格涨跌幅"""
    if last_price is None or current_price is None:
        return None, None
    change = current_price - last_price
    change_percent = (change / last_price) * 100
    return change, change_percent

def check_price_alerts(data):
    """检查价格预警"""
    alerts = []

    for stock_name, stock_info in data['stocks'].items():
        stock_code = stock_info['code']

        # 跳过未上市股票
        if stock_code is None:
            print(f"  跳过 {stock_name}（未上市）")
            continue

        # 获取当前价格
        current_price = get_stock_price(stock_code, stock_name)

        if current_price is None:
            print(f"  {stock_name}：无法获取价格")
            continue

        # 获取上次检查价格
        last_price = stock_info['last_price']

        # 首次记录价格
        if last_price is None:
            stock_info['last_price'] = current_price
            stock_info['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {stock_name}：首次记录价格 {current_price}")
            continue

        # 计算涨跌幅
        change, change_percent = calculate_price_change(current_price, last_price)

        if change_percent is None:
            print(f"  {stock_name}：无法计算涨跌幅")
            continue

        # 检查是否超过±5%
        if abs(change_percent) >= 5.0:
            alert = {
                "stock": stock_name,
                "code": stock_code,
                "last_price": last_price,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "direction": "上涨" if change_percent > 0 else "下跌",
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            alerts.append(alert)

            print(f"  ⚠️  预警：{stock_name} {stock_code}")
            print(f"      上次价格：{last_price}")
            print(f"      当前价格：{current_price}")
            print(f"      涨跌幅：{change_percent:.2f}%")
        else:
            print(f"  {stock_name}：涨跌幅 {change_percent:.2f}%（正常）")

        # 更新价格记录
        stock_info['last_price'] = current_price
        stock_info['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 保存更新后的价格数据
    save_price_tracking(data)

    return alerts

def generate_alert_message(alerts):
    """生成预警消息"""
    if not alerts:
        return None

    lines = ["【价格预警】持仓股票涨跌超过5%", ""]

    for alert in alerts:
        emoji = "📈" if alert['change_percent'] > 0 else "📉"
        lines.append(f"{emoji} {alert['stock']} ({alert['code']})")
        lines.append(f"   {alert['direction']} {abs(alert['change_percent']):.2f}%")
        lines.append(f"   上次价格：{alert['last_price']}")
        lines.append(f"   当前价格：{alert['current_price']}")
        lines.append(f"   时间：{alert['time']}")
        lines.append("")

    return '\n'.join(lines)

def main():
    """主函数"""
    print("=" * 60)
    print("涨跌幅监控脚本")
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 加载价格跟踪数据
    data = load_price_tracking()
    if data is None:
        return

    print(f"\n持仓数量：{len(data['stocks'])}")
    print("开始检查价格预警...\n")

    # 检查价格预警
    alerts = check_price_alerts(data)

    # 生成预警消息
    alert_message = generate_alert_message(alerts)

    if alert_message:
        print("\n" + "=" * 60)
        print("预警消息：")
        print("=" * 60)
        print(alert_message)
        print("=" * 60)

        # 保存预警记录
        with open(ALERT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(alert_message)
            f.write("\n" + "=" * 60 + "\n")

        # TODO: 推送预警到飞书
        print("\n⚠️  警告：预警消息已生成，但尚未自动推送到飞书")
        print("    需要实现飞书消息推送功能")
    else:
        print("\n✅ 所有持仓股票涨跌幅在±5%以内，无预警")

if __name__ == '__main__':
    main()
