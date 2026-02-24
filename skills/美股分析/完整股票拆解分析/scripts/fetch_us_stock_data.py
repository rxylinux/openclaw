#!/usr/bin/env python3
"""
美股股票数据获取脚本

功能：
- 获取实时股价
- 获取财务数据
- 获取估值指标
- 获取历史价格

使用方式：
    python3 scripts/fetch_us_stock_data.py AAPL
"""

import yfinance as yf
import sys
import json
from datetime import datetime

def fetch_stock_data(symbol):
    """
    获取美股股票数据

    Args:
        symbol: 股票代码，如 AAPL

    Returns:
        dict: 包含股票数据的字典
    """
    try:
        # 创建股票对象
        stock = yf.Ticker(symbol)

        # 获取基本信息
        info = stock.info

        # 获取财务数据
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow

        # 获取历史价格（1年）
        hist = stock.history(period="1y")

        # 计算价格变动
        current_price = hist['Close'].iloc[-1] if len(hist) > 0 else 0
        price_1m_ago = hist['Close'].iloc[-21] if len(hist) >= 21 else current_price
        price_3m_ago = hist['Close'].iloc[-63] if len(hist) >= 63 else current_price
        price_6m_ago = hist['Close'].iloc[-126] if len(hist) >= 126 else current_price
        price_1y_ago = hist['Close'].iloc[-252] if len(hist) >= 252 else current_price
        price_ytd_start = hist['Close'].iloc[0] if len(hist) > 0 else current_price

        # 计算涨跌幅
        change_1m = ((current_price - price_1m_ago) / price_1m_ago * 100) if price_1m_ago > 0 else 0
        change_3m = ((current_price - price_3m_ago) / price_3m_ago * 100) if price_3m_ago > 0 else 0
        change_6m = ((current_price - price_6m_ago) / price_6m_ago * 100) if price_6m_ago > 0 else 0
        change_1y = ((current_price - price_1y_ago) / price_1y_ago * 100) if price_1y_ago > 0 else 0
        change_ytd = ((current_price - price_ytd_start) / price_ytd_start * 100) if price_ytd_start > 0 else 0

        # 52周高低点
        high_52w = hist['High'].max() if len(hist) > 0 else 0
        low_52w = hist['Low'].min() if len(hist) > 0 else 0

        # 构建结果
        result = {
            "symbol": symbol,
            "company_name": info.get('longName', ''),
            "sector": info.get('sector', ''),
            "industry": info.get('industry', ''),
            "current_price": current_price,
            "currency": info.get('currency', 'USD'),
            "market_cap": info.get('marketCap', 0),
            "price_changes": {
                "1m": round(change_1m, 2),
                "3m": round(change_3m, 2),
                "6m": round(change_6m, 2),
                "1y": round(change_1y, 2),
                "ytd": round(change_ytd, 2)
            },
            "52w_range": {
                "high": round(high_52w, 2),
                "low": round(low_52w, 2)
            },
            "valuation": {
                "pe_ratio": info.get('trailingPE', None),
                "forward_pe": info.get('forwardPE', None),
                "pb_ratio": info.get('priceToBook', None),
                "ps_ratio": info.get('priceToSalesTrailing12Months', None),
                "peg_ratio": info.get('pegRatio', None)
            },
            "financials": {
                "total_revenue": info.get('totalRevenue', None),
                "revenue_per_share": info.get('revenuePerShare', None),
                "profit_margin": info.get('profitMargins', None),
                "operating_margin": info.get('operatingMargins', None),
                "roe": info.get('returnOnEquity', None),
                "debt_to_equity": info.get('debtToEquity', None),
                "total_cash": info.get('totalCash', None),
                "total_debt": info.get('totalDebt', None),
                "free_cash_flow": info.get('freeCashflow', None)
            },
            "trading": {
                "52_week_change": info.get('52WeekChange', None),
                "avg_volume": info.get('averageVolume', None),
                "beta": info.get('beta', None)
            },
            "dividend": {
                "dividend_yield": info.get('dividendYield', None),
                "dividend_rate": info.get('dividendRate', None),
                "payout_ratio": info.get('payoutRatio', None)
            },
            "data_source": "Yahoo Finance (yfinance)",
            "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return result

    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol
        }


def print_stock_data(data):
    """打印股票数据"""
    if "error" in data:
        print(f"错误: {data['error']}")
        return

    print(f"\n# {data['company_name']} ({data['symbol']})")
    print(f"行业: {data['sector']} / {data['industry']}")
    print(f"当前价格: ${data['current_price']:.2f}")
    print(f"市值: ${data['market_cap'] / 1e9:.2f}B")

    print("\n## 价格变动")
    print(f"1个月: {data['price_changes']['1m']:+.2f}%")
    print(f"3个月: {data['price_changes']['3m']:+.2f}%")
    print(f"6个月: {data['price_changes']['6m']:+.2f}%")
    print(f"1年: {data['price_changes']['1y']:+.2f}%")
    print(f"年初至今: {data['price_changes']['ytd']:+.2f}%")

    print("\n## 52周区间")
    print(f"最高: ${data['52w_range']['high']:.2f}")
    print(f"最低: ${data['52w_range']['low']:.2f}")

    print("\n## 估值指标")
    valuation = data['valuation']
    if valuation['pe_ratio']:
        print(f"市盈率 (P/E): {valuation['pe_ratio']:.2f}")
    if valuation['forward_pe']:
        print(f"预期市盈率 (Forward P/E): {valuation['forward_pe']:.2f}")
    if valuation['pb_ratio']:
        print(f"市净率 (P/B): {valuation['pb_ratio']:.2f}")
    if valuation['ps_ratio']:
        print(f"市销率 (P/S): {valuation['ps_ratio']:.2f}")
    if valuation['peg_ratio']:
        print(f"PEG比率: {valuation['peg_ratio']:.2f}")

    print("\n## 财务数据")
    financials = data['financials']
    if financials['total_revenue']:
        print(f"营收: ${financials['total_revenue'] / 1e9:.2f}B")
    if financials['profit_margin']:
        print(f"净利润率: {financials['profit_margin'] * 100:.2f}%")
    if financials['roe']:
        print(f"ROE: {financials['roe'] * 100:.2f}%")
    if financials['debt_to_equity']:
        print(f"资产负债率: {financials['debt_to_equity']:.2f}%")
    if financials['free_cash_flow']:
        print(f"自由现金流: ${financials['free_cash_flow'] / 1e9:.2f}B")

    print(f"\n数据来源: {data['data_source']}")
    print(f"获取时间: {data['fetch_date']}")


def main():
    if len(sys.argv) < 2:
        print("使用方式: python3 scripts/fetch_us_stock_data.py <股票代码>")
        print("示例: python3 scripts/fetch_us_stock_data.py AAPL")
        sys.exit(1)

    symbol = sys.argv[1].upper()

    print(f"正在获取 {symbol} 的数据...")
    data = fetch_stock_data(symbol)

    print_stock_data(data)


if __name__ == "__main__":
    main()
