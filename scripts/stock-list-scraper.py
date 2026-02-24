#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股上市公司名单抓取脚本
从中国证监会官网批量获取A股上市公司数据
"""

import requests
import time
import json
from bs4 import BeautifulSoup

def scrape_stocks(page_num=1):
    """
    抓取指定页面的上市公司数据
    """
    base_url = "http://eid.csrc.gov.cn/2010/"

    # 构建POST请求数据
    data = {
        'currPage': page_num,
        'pageSize': 15,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            stocks = []

            # 查找表格中的数据
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        stock_code = cols[0].text.strip()
                        stock_name = cols[1].text.strip()
                        company_name = cols[2].text.strip()
                        market = cols[3].text.strip() if len(cols) > 3 else ''

                        stocks.append({
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'company_name': company_name,
                            'market': market
                        })

            return stocks

        return []

    except Exception as e:
        print(f"抓取第 {page_num} 页出错: {e}")
        return []

def save_to_file(stocks, filename):
    """
    保存股票数据到文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for stock in stocks:
            line = f"{stock['stock_code']}\t{stock['stock_name']}\t{stock['company_name']}\t{stock['market']}"
            f.write(line + '\n')

def main():
    """
    主函数
    """
    all_stocks = []
    max_pages = 70  # 获取70页，约1000家左右

    print("开始抓取A股上市公司名单...")

    for page in range(1, max_pages + 1):
        print(f"正在抓取第 {page}/{max_pages} 页...")

        stocks = scrape_stocks(page)

        if stocks:
            all_stocks.extend(stocks)
            print(f"  本页获取 {len(stocks)} 家公司，累计 {len(all_stocks)} 家")
        else:
            print(f"  第 {page} 页无数据，停止抓取")
            break

        # 避免请求过快被封
        time.sleep(1)

    # 保存到文件
    output_file = '/root/.openclaw/workspace/a-stocks-1000.txt'
    save_to_file(all_stocks, output_file)

    print(f"\n抓取完成！")
    print(f"总计获取 {len(all_stocks)} 家上市公司")
    print(f"已保存到: {output_file}")

if __name__ == '__main__':
    main()
