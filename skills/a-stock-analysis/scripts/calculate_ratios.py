#!/usr/bin/env python3
"""
财务指标计算工具
"""
import sys
import json
import argparse

def calculate_cagr(start_value, end_value, years):
    """计算复合年增长率 (CAGR)"""
    if years <= 0 or start_value <= 0:
        return None
    cagr = (end_value / start_value) ** (1/years) - 1
    return round(cagr * 100, 2)

def calculate_roe(net_income, avg_equity):
    """计算净资产收益率 (ROE)"""
    if avg_equity == 0:
        return None
    return round(net_income / avg_equity * 100, 2)

def calculate_pe(price, eps):
    """计算市盈率 (PE)"""
    if eps == 0:
        return None
    return round(price / eps, 2)

def calculate_pb(price, book_value_per_share):
    """计算市净率 (PB)"""
    if book_value_per_share == 0:
        return None
    return round(price / book_value_per_share, 2)

def calculate_peg(pe, growth_rate):
    """计算PEG（市盈增长比）"""
    if growth_rate == 0:
        return None
    return round(pe / growth_rate, 2)

def calculate_debt_ratio(total_debt, total_assets):
    """计算资产负债率"""
    if total_assets == 0:
        return None
    return round(total_debt / total_assets * 100, 2)

def calculate_current_ratio(current_assets, current_liabilities):
    """计算流动比率"""
    if current_liabilities == 0:
        return None
    return round(current_assets / current_liabilities, 2)

def calculate_inventory_days(cogs, avg_inventory):
    """计算存货周转天数"""
    if avg_inventory == 0 or cogs == 0:
        return None
    days = 365 / (cogs / avg_inventory)
    return round(days, 2)

def calculate_receivable_days(revenue, avg_receivables):
    """计算应收账款周转天数"""
    if avg_receivables == 0 or revenue == 0:
        return None
    days = 365 / (revenue / avg_receivables)
    return round(days, 2)

def calculate_turnover_days(cogs_or_revenue, avg_value):
    """通用周转天数计算"""
    if avg_value == 0 or cogs_or_revenue == 0:
        return None
    return round(365 / (cogs_or_revenue / avg_value), 2)

def main():
    parser = argparse.ArgumentParser(description='财务指标计算工具')
    parser.add_argument('--json', help='JSON格式的财务数据')
    parser.add_argument('--calc', choices=['cagr', 'roe', 'pe', 'pb', 'peg', 'debt', 'current', 'inventory', 'receivable'],
                   help='要计算的指标类型')

    # CAGR参数
    parser.add_argument('--start', type=float, help='起始值')
    parser.add_argument('--end', type=float, help='期末值')
    parser.add_argument('--years', type=float, help='年数')

    # ROE参数
    parser.add_argument('--net-income', type=float, help='净利润')
    parser.add_argument('--avg-equity', type=float, help='平均净资产')

    # PE参数
    parser.add_argument('--price', type=float, help='股价')
    parser.add_argument('--eps', type=float, help='每股收益')

    # PB参数
    parser.add_argument('--book-value', type=float, help='每股净资产')

    # PEG参数
    parser.add_argument('--growth-rate', type=float, help='增长率（小数形式，如0.2表示20%）')

    # 资产负债率参数
    parser.add_argument('--total-debt', type=float, help='总负债')
    parser.add_argument('--total-assets', type=float, help='总资产')

    # 流动比率参数
    parser.add_argument('--current-assets', type=float, help='流动资产')
    parser.add_argument('--current-liabilities', type=float, help='流动负债')

    # 周转天数参数
    parser.add_argument('--cogs', type=float, help='营业成本')
    parser.add_argument('--avg-inventory', type=float, help='平均存货')
    parser.add_argument('--avg-receivables', type=float, help='平均应收账款')

    args = parser.parse_args()

    result = None

    if args.calc == 'cagr':
        result = calculate_cagr(args.start, args.end, args.years)
    elif args.calc == 'roe':
        result = calculate_roe(args.net_income, args.avg_equity)
    elif args.calc == 'pe':
        result = calculate_pe(args.price, args.eps)
    elif args.calc == 'pb':
        result = calculate_pb(args.price, args.book_value)
    elif args.calc == 'peg':
        result = calculate_peg(args.pe, args.growth_rate)
    elif args.calc == 'debt':
        result = calculate_debt_ratio(args.total_debt, args.total_assets)
    elif args.calc == 'current':
        result = calculate_current_ratio(args.current_assets, args.current_liabilities)
    elif args.calc == 'inventory':
        result = calculate_inventory_days(args.cogs, args.avg_inventory)
    elif args.calc == 'receivable':
        result = calculate_receivable_days(args.revenue or args.cogs, args.avg_receivables)

    if result is not None:
        print(f"{result}%")
    else:
        print("无法计算：参数无效或除零")

if __name__ == '__main__':
    main()
