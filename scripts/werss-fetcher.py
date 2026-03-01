#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeRss 公众号文章获取器
使用 WeRss (werss.app) 获取微信公众号文章（免费）
"""

import requests
import feedparser
from datetime import datetime, timezone
from pathlib import Path
import json
import time
import re


class WeRssFetcher:
    """
    WeRss 获取器

    文档: https://werss.app
    免费使用，无需注册
    """

    def __init__(self, base_url="https://werss.app"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSSBot/1.0; +https://example.com)'
        }

    def search_account(self, keyword: str) -> dict:
        """
        搜索公众号

        返回格式：
        {
            'name': 公众号名称,
            'account_id': 公众号ID (用于生成RSS),
            'description': 描述,
            'found': True/False
        }
        """
        url = f"{self.base_url}/api/search"

        try:
            response = requests.get(url, params={'keyword': keyword}, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return {'found': False, 'error': f"HTTP {response.status_code}"}

            data = response.json()

            if not data.get('data'):
                return {'found': False, 'error': '未找到公众号'}

            # 返回第一个结果
            account = data['data'][0]
            return {
                'found': True,
                'name': account.get('name', ''),
                'account_id': account.get('account_id', ''),
                'description': account.get('description', ''),
                'avatar': account.get('avatar', '')
            }

        except Exception as e:
            return {'found': False, 'error': str(e)}

    def get_rss_url(self, account_id: str) -> str:
        """
        生成 RSS 订阅地址

        格式: https://werss.app/feed/{account_id}
        """
        return f"{self.base_url}/feed/{account_id}"

    def fetch_articles(self, rss_url: str, limit: int = 10) -> list:
        """
        从 RSS 地址获取文章
        """
        try:
            response = requests.get(rss_url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                return []

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'summary': self._clean_summary(entry.get('summary', '')),
                    'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取文章失败: {e}")
            return []

    def _clean_summary(self, summary: str) -> str:
        """清理摘要文本"""
        if not summary:
            return ''

        # 移除 HTML 标签
        summary = re.sub(r'<[^>]+>', '', summary)
        # 移除多余空格
        summary = ' '.join(summary.split())
        # 限制长度
        return summary[:300] if len(summary) > 300 else summary

    def fetch_by_name(self, account_name: str, limit: int = 10) -> dict:
        """
        通过公众号名称获取文章（一步到位）

        返回格式：
        {
            'success': True/False,
            'account': {公众号信息},
            'articles': [文章列表],
            'rss_url': RSS地址,
            'error': 错误信息（如果失败）
        }
        """
        result = {
            'success': False,
            'account': None,
            'articles': [],
            'rss_url': '',
            'error': ''
        }

        # 1. 搜索公众号
        search_result = self.search_account(account_name)

        if not search_result['found']:
            result['error'] = f"未找到公众号: {search_result.get('error', '未知错误')}"
            return result

        # 2. 生成 RSS 地址
        account_id = search_result['account_id']
        rss_url = self.get_rss_url(account_id)

        # 3. 获取文章
        articles = self.fetch_articles(rss_url, limit)

        result['success'] = True
        result['account'] = search_result
        result['articles'] = articles
        result['rss_url'] = rss_url

        return result


def format_articles(result: dict) -> str:
    """格式化文章为 Markdown"""
    if not result['success']:
        return f"## {result.get('account_name', '未知公众号')}\n\n❌ 获取失败: {result['error']}\n\n"

    account = result['account']
    articles = result['articles']

    md_content = f"## {account['name']}\n\n"
    md_content += f"**描述**: {account.get('description', '无')}\n"
    md_content += f"**RSS地址**: {result['rss_url']}\n"
    md_content += f"**文章数量**: {len(articles)}\n"
    md_content += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"

    if not articles:
        md_content += "暂无文章\n\n"
        return md_content

    for i, article in enumerate(articles, 1):
        md_content += f"### {i}. {article['title']}\n\n"

        if article['author']:
            md_content += f"**作者**: {article['author']}\n"

        if article['published']:
            md_content += f"**发布时间**: {article['published']}\n"

        md_content += f"**链接**: {article['link']}\n"

        if article.get('summary'):
            md_content += f"\n**摘要**:\n{article['summary']}\n"

        md_content += "\n---\n\n"

    return md_content


def main():
    """测试 WeRss"""
    fetcher = WeRssFetcher()

    print("=" * 60)
    print("WeRss 测试")
    print("=" * 60)

    # 测试账号列表
    test_accounts = [
        "极客公园",
        "量子位",
        "机器之心"
    ]

    all_results = []

    for account_name in test_accounts:
        print(f"\n测试: {account_name}")
        print("-" * 60)

        result = fetcher.fetch_by_name(account_name, limit=3)

        if result['success']:
            account = result['account']
            print(f"  ✅ 找到: {account['name']}")
            print(f"  ID: {account['account_id']}")
            print(f"  文章数: {len(result['articles'])}")

            if result['articles']:
                print(f"  最新: {result['articles'][0]['title']}")
        else:
            print(f"  ❌ 失败: {result['error']}")

        all_results.append(result)

        # 避免请求过快
        time.sleep(2)

    # 生成汇总报告
    print("\n" + "=" * 60)
    print("生成汇总报告")
    print("=" * 60)

    md_content = "# WeRss 公众号文章汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"

    total_articles = 0

    for result in all_results:
        if result['success']:
            md_content += format_articles(result)
            total_articles += len(result['articles'])

    # 保存文件
    output_dir = Path("/root/.openclaw/workspace/temp/werss-articles")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"werss_summary_{timestamp}.md"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✅ 已保存到: {filepath}")
    print(f"总文章数: {total_articles}")
    print(f"成功率: {sum(1 for r in all_results if r['success'])}/{len(all_results)}")


if __name__ == "__main__":
    main()
