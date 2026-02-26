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
import akshare as ak

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

    数据源：腾讯财经API（快且稳定）
    """
    try:
        print(f"获取 {stock_name} ({stock_code}) 的实时价格...")

        # 处理不同市场的股票代码
        if stock_code.endswith('.SH'):
            # 沪市股票
            clean_code = stock_code.replace('.SH', '').lower()
            url = f"http://qt.gtimg.cn/q=sh{clean_code}"
        elif stock_code.endswith('.SZ'):
            # 深市股票
            clean_code = stock_code.replace('.SZ', '').lower()
            url = f"http://qt.gtimg.cn/q=sz{clean_code}"
        elif stock_code.endswith('.HK'):
            # 港股（格式如 0700.HK）
            clean_code = stock_code.replace('.HK', '').lower()
            # 港股需要5位数字，不足补0
            clean_code = clean_code.zfill(5)
            url = f"http://qt.gtimg.cn/q=hk{clean_code}"
        elif stock_code.isupper() and len(stock_code) <= 5:
            # 美股（如NNOX, ABCL）
            url = f"http://qt.gtimg.cn/q=us{stock_code}"
        else:
            print(f"  无法识别的股票代码格式：{stock_code}")
            return None

        # 请求数据
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            print(f"  请求失败，状态码：{response.status_code}")
            return None

        # 解析数据
        data = response.text
        if not data or '=' not in data or '"' not in data:
            print(f"  数据格式错误")
            return None

        # 提取价格数据
        # 腾讯财经返回格式：v_sz000001="51~股票名称~000001~当前价格~昨收~今开~最高~最低~..."
        price_str = data.split('=')[1].strip('"')
        fields = price_str.split('~')

        # 腾讯财经返回字段：
        # 字段0：51（固定值）
        # 字段1：股票名称
        # 字段2：股票代码
        # 字段3：当前价格 ✓
        # 字段4：昨收
        # 字段5：今开
        # 字段6：最高
        # 字段7：最低
        # ...

        if not fields or len(fields) < 4:
            print(f"  数据字段不足（{len(fields)}个字段）")
            return None

        # 提取当前价格（字段3）
        current_price_str = fields[3]
        if not current_price_str:
            print(f"  当前价格为空")
            return None

        try:
            current_price = float(current_price_str)
        except ValueError:
            print(f"  当前价格格式错误：{current_price_str}")
            return None

        if current_price == 0:
            print(f"  当前价格为0")
            return None

        print(f"  当前价格：{current_price}")
        return current_price

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

        # 首次记录价格（不计算涨跌幅）
        if last_price is None:
            stock_info['last_price'] = current_price
            stock_info['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {stock_name}：首次记录价格 {current_price}，不计算涨跌幅")
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

def send_alert_to_feishu(alert_message):
    """发送预警到飞书"""
    if not alert_message:
        return

    # 保存预警消息到文件
    alert_file = '/root/.openclaw/workspace/temp/price-alert.txt'
    with open(alert_file, 'w', encoding='utf-8') as f:
        f.write(alert_message)

    # 注意：这里只保存到文件，实际推送由主会话完成
    # 因为message工具只能在主会话中使用
    print(f"\n  预警消息已保存到 {alert_file}")
    print(f"  请在主会话中读取文件并推送到飞书")

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

        # 发送预警到飞书
        send_alert_to_feishu(alert_message)
    else:
        print("\n✅ 所有持仓股票涨跌幅在±5%以内，无预警")

if __name__ == '__main__':
    main()
