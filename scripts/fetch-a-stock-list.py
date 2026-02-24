#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从东方财富网获取A股上市公司列表
"""

import requests
import json
import time

def fetch_stock_list():
    """获取A股上市公司列表"""

    seen_codes = set()
    all_stocks = []

    # 东方财富网A股列表API
    url = "http://92.push2.eastmoney.com/api/qt/clist/get"

    # 分页获取，每页200条，获取10页达到2000家
    for page in range(1, 11):
        params = {
            'pn': str(page),  # 页码
            'pz': '200',  # 每页数量
            'po': '1',  # 排序方式
            'np': '1',
            'fltt': '2',
            'invt': '2',
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # 沪深A股
            'fields': 'f12,f13,f14',  # 股票代码,市场,股票名称
            '_': str(int(time.time() * 1000))
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['data'] and 'diff' in data['data']:
                stocks = data['data']['diff']

                for stock in stocks:
                    code = str(stock['f12'])  # 股票代码
                    market = stock['f13']  # 市场 0=沪市 1=深市
                    name = stock['f14']  # 股票名称

                    # 格式化股票代码为6位数字
                    full_code = code.zfill(6)

                    # 避免重复
                    if full_code not in seen_codes:
                        seen_codes.add(full_code)
                        all_stocks.append({
                            'code': full_code,
                            'name': name
                        })

                print(f"第{page}页: 获取到{len(stocks)}只股票，累计{len(all_stocks)}只")

                if len(all_stocks) >= 1000:
                    break

        except Exception as e:
            print(f"第{page}页抓取失败: {e}")
            continue

        time.sleep(0.3)  # 避免请求过快

    return all_stocks[:1000]  # 只返回前1000家

if __name__ == '__main__':
    stocks = fetch_stock_list()

    if stocks:
        # 保存到文件
        output_file = '/root/.openclaw/workspace/a-stock-1000.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# A股上市公司列表（前1000家）\n")
            f.write("# 格式：股票代码|股票名称\n")
            f.write("# 生成时间：2026-02-22\n\n")

            for i, stock in enumerate(stocks, 1):
                f.write(f"{stock['code']}|{stock['name']}\n")

        print(f"成功获取 {len(stocks)} 家上市公司信息")
        print(f"已保存到: {output_file}")

        # 显示前10家
        print("\n前10家股票:")
        for stock in stocks[:10]:
            print(f"  {stock['code']}|{stock['name']}")
    else:
        print("未能获取到股票数据")
