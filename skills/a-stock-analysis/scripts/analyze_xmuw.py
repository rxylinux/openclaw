#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
厦门钨业分析脚本
"""

import json
import sys
from bocha_search import StockInfoSearcher

def analyze_stock():
    """分析厦门钨业"""
    searcher = StockInfoSearcher()

    print("=" * 80)
    print("厦门钨业 (600549) 深度分析报告")
    print("=" * 80)
    print()

    # 1. 基本信息
    print("【一、基本信息】")
    print("-" * 80)
    basic_result = searcher.search_stock_basic_info("600549", "厦门钨业")

    if "webPages" in basic_result["data"]["data"]:
        webpages = basic_result["data"]["data"]["webPages"]["value"]
        print(f"✓ 找到 {len(webpages)} 条相关信息")

        # 提取关键信息
        for i, page in enumerate(webpages[:5], 1):
            print(f"\n{i}. {page['name']}")
            print(f"   来源: {page['displayUrl']}")
            snippet = page.get('snippet', '')
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            print(f"   摘要: {snippet}")
    else:
        print("✗ 未找到基本信息")

    print("\n" + "=" * 80)

    # 2. 财务数据
    print("\n【二、财务数据】")
    print("-" * 80)
    financial_result = searcher.search_stock_financial("600549", "厦门钨业")

    if "webPages" in financial_result["data"]["data"]:
        webpages = financial_result["data"]["data"]["webPages"]["value"]
        print(f"✓ 找到 {len(webpages)} 条财务相关信息")

        for i, page in enumerate(webpages[:5], 1):
            print(f"\n{i}. {page['name']}")
            print(f"   来源: {page['displayUrl']}")
            snippet = page.get('snippet', '')
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            print(f"   摘要: {snippet}")
    else:
        print("✗ 未找到财务数据")

    print("\n" + "=" * 80)

    # 3. 最新新闻
    print("\n【三、最新新闻】")
    print("-" * 80)
    news_result = searcher.search_stock_news("600549", "厦门钨业")

    if "webPages" in news_result["data"]["data"]:
        webpages = news_result["data"]["data"]["webPages"]["value"]
        print(f"✓ 找到 {len(webpages)} 条最新新闻")

        for i, page in enumerate(webpages[:8], 1):
            print(f"\n{i}. {page['name']}")
            print(f"   来源: {page['displayUrl']}")
            snippet = page.get('snippet', '')
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            print(f"   摘要: {snippet}")
    else:
        print("✗ 未找到最新新闻")

    print("\n" + "=" * 80)

    # 4. 行业分析
    print("\n【四、行业分析】")
    print("-" * 80)
    industry_result = searcher.search_industry("钨产业 稀土")

    if "webPages" in industry_result["data"]["data"]:
        webpages = industry_result["data"]["data"]["webPages"]["value"]
        print(f"✓ 找到 {len(webpages)} 条行业分析")

        for i, page in enumerate(webpages[:5], 1):
            print(f"\n{i}. {page['name']}")
            print(f"   来源: {page['displayUrl']}")
            snippet = page.get('snippet', '')
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            print(f"   摘要: {snippet}")
    else:
        print("✗ 未找到行业分析")

    print("\n" + "=" * 80)
    print("\n报告生成完成")
    print("数据来源: 博查AI开放平台")

if __name__ == "__main__":
    analyze_stock()
