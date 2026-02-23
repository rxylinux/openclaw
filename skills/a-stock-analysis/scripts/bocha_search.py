#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博查API集成脚本 - A股股票搜索
使用博查AI开放平台的搜索API进行股票信息查询
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class BochaSearchClient:
    """博查搜索API客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化博查客户端

        Args:
            api_key: 博查API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('BOCHA_API_KEY')
        if not self.api_key:
            raise ValueError("请设置博查API密钥：\n"
                           "1. 设置环境变量: export BOCHA_API_KEY=your_key\n"
                           "2. 或者直接传入: BochaSearchClient(api_key='your_key')")

        self.base_url = "https://api.bocha.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def web_search(
        self,
        query: str,
        count: int = 10,
        freshness: str = "noLimit",
        summary: bool = True
    ) -> Dict[str, Any]:
        """
        网页搜索（通搜）

        Args:
            query: 搜索关键词
            count: 返回结果数量（最多50条）
            freshness: 时间范围
                - "noLimit": 不限制
                - "day": 一天内
                - "week": 一周内
                - "month": 一个月内
                - "year": 一年内
            summary: 是否返回摘要

        Returns:
            搜索结果字典
        """
        url = f"{self.base_url}/web-search"

        payload = {
            "query": query,
            "count": count,
            "freshness": freshness,
            "summary": summary
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}

    def ai_search(
        self,
        query: str,
        count: int = 10,
        freshness: str = "noLimit",
        answer: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        AI搜索（混合搜索）

        Args:
            query: 搜索关键词
            count: 返回结果数量（最多50条）
            freshness: 时间范围
            answer: 是否返回AI生成的答案
            stream: 是否使用流式输出

        Returns:
            搜索结果字典
        """
        url = f"{self.base_url}/ai-search"

        payload = {
            "query": query,
            "count": count,
            "freshness": freshness,
            "answer": answer,
            "stream": stream
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}


class StockInfoSearcher:
    """股票信息搜索器（使用博查API）"""

    # A股专业网站列表
    STOCK_WEBSITES = [
        {"name": "财联社", "domain": "caifinance.com"},
        {"name": "雪球", "domain": "xueqiu.com"},
        {"name": "巨潮资讯", "domain": "cninfo.com.cn"},
        {"name": "东方财富", "domain": "eastmoney.com"},
        {"name": "同花顺", "domain": "10jqka.com.cn"},
        {"name": "萝卜投资", "domain": "luobotou.com"},
        {"name": "证券时报", "domain": "stcn.com"},
        {"name": "中国基金报", "domain": "chinatimes.net"},
        {"name": "全景网", "domain": "p5w.net"},
        {"name": "金融界", "domain": "jrj.com.cn"},
        {"name": "和讯网", "domain": "hexun.com"},
        {"name": "第一财经", "domain": "yicai.com"},
        {"name": "新浪财经", "domain": "finance.sina.com.cn"},
        {"name": "搜狐财经", "domain": "business.sohu.com"},
        {"name": "网易财经", "domain": "money.163.com"}
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化

        Args:
            api_key: 博查API密钥
        """
        self.client = BochaSearchClient(api_key)

    def search_stock_basic_info(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """
        搜索股票基本信息

        Args:
            stock_code: 股票代码（如 002472）
            stock_name: 股票名称（如 双环传动）

        Returns:
            搜索结果
        """
        # 构建搜索关键词
        query = f"{stock_code} {stock_name} 基本信息 股票代码 主营业务"
        if stock_name:
            query = f"{stock_code} {stock_name} 基本信息 主营业务"
        else:
            query = f"{stock_code} 基本信息 主营业务"

        print(f"[博查] 搜索: {query}")
        result = self.client.web_search(query=query, count=10, freshness="month")

        return {
            "query_type": "basic_info",
            "stock_code": stock_code,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": result
        }

    def search_stock_financial(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """
        搜索财务数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            搜索结果
        """
        query = f"{stock_code} {stock_name} 财报 业绩 ROE 市盈率"
        if stock_name:
            query = f"{stock_code} {stock_name} 财报 业绩 ROE 市盈率"
        else:
            query = f"{stock_code} 财报 业绩 ROE 市盈率"

        print(f"[博查] 搜索: {query}")
        result = self.client.web_search(query=query, count=10, freshness="month")

        return {
            "query_type": "financial",
            "stock_code": stock_code,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": result
        }

    def search_stock_news(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """
        搜索最新新闻

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            搜索结果
        """
        query = f"{stock_code} {stock_name} 最新新闻 动态 公告"
        if stock_name:
            query = f"{stock_code} {stock_name} 最新新闻 动态 公告"
        else:
            query = f"{stock_code} 最新新闻 动态 公告"

        print(f"[博查] 搜索: {query}")
        result = self.client.web_search(query=query, count=15, freshness="week")

        return {
            "query_type": "news",
            "stock_code": stock_code,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": result
        }

    def search_industry(self, industry_name: str) -> Dict[str, Any]:
        """
        搜索行业信息

        Args:
            industry_name: 行业名称

        Returns:
            搜索结果
        """
        query = f"{industry_name} 行业分析 发展趋势 市场规模 龙头公司"

        print(f"[博查] 搜索: {query}")
        result = self.client.web_search(query=query, count=15, freshness="month")

        return {
            "query_type": "industry",
            "industry": industry_name,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": result
        }

    def comprehensive_search(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """
        综合搜索（获取所有信息）

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            所有搜索结果
        """
        print(f"\n{'='*60}")
        print(f"使用博查API搜索 {stock_code} {stock_name} 的完整信息")
        print(f"{'='*60}\n")

        results = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "博查AI开放平台 (https://open.bocha.cn)"
        }

        # 1. 基本信息
        print("[1/4] 搜索基本信息...")
        results["basic_info"] = self.search_stock_basic_info(stock_code, stock_name)

        # 2. 财务数据
        print("[2/4] 搜索财务数据...")
        results["financial"] = self.search_stock_financial(stock_code, stock_name)

        # 3. 最新新闻
        print("[3/4] 搜索最新新闻...")
        results["news"] = self.search_stock_news(stock_code, stock_name)

        # 4. 行业信息
        print("[4/4] 搜索行业信息...")
        # 从基本信息中提取行业名称
        # 这里简化处理，实际可以从搜索结果中解析
        results["industry"] = self.search_industry("股票所属行业")

        return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("="*60)
        print(" 博查API股票搜索工具")
        print("="*60)
        print("\n用法: python3 bocha_search.py <股票代码> [股票名称] [选项]")
        print("\n示例:")
        print("  python3 bocha_search.py 002472 双环传动")
        print("  python3 bocha_search.py 002472 双环传动 --basic")
        print("  python3 bocha_search.py 002472 双环传动 --financial")
        print("  python3 bocha_search.py 002472 双环传动 --news")
        print("\n选项:")
        print("  --basic      仅搜索基本信息")
        print("  --financial  仅搜索财务数据")
        print("  --news       仅搜索最新新闻")
        print("  --industry   仅搜索行业信息")
        print("  --all        搜索所有信息（默认）")
        print("\n环境变量:")
        print("  BOCHA_API_KEY  博查API密钥（必填）")
        print("\n获取API密钥:")
        print("  1. 访问 https://open.bocha.cn")
        print("  2. 注册账号并获取API-KEY")
        print("  3. 免费领取调用资源包")
        print("="*60)
        sys.exit(1)

    stock_code = sys.argv[1]
    stock_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else ""

    try:
        searcher = StockInfoSearcher()

        # 根据参数执行相应操作
        if '--basic' in sys.argv:
            result = searcher.search_stock_basic_info(stock_code, stock_name)
        elif '--financial' in sys.argv:
            result = searcher.search_stock_financial(stock_code, stock_name)
        elif '--news' in sys.argv:
            result = searcher.search_stock_news(stock_code, stock_name)
        elif '--industry' in sys.argv:
            # 行业搜索需要单独的参数
            industry_name = stock_name or "汽车零部件"
            result = searcher.search_industry(industry_name)
        else:
            # 默认：综合搜索
            result = searcher.comprehensive_search(stock_code, stock_name)

        # 输出结果
        print(f"\n{'='*60}")
        print("搜索完成，结果如下：")
        print(f"{'='*60}\n")
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"搜索失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
