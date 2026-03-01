#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSSHub 文章获取器
使用 RSSHub 获取各平台的内容（免费、开源）
"""

import requests
import feedparser
from datetime import datetime, timezone
from pathlib import Path
import json
import time


class RSSHubFetcher:
    def __init__(self, rsshub_base="https://rsshub.app"):
        self.rsshub_base = rsshub_base
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSSBot/1.0; +https://example.com)'
        }

    def fetch_wechat_mp(self, account_name: str, limit: int = 5) -> list:
        """
        获取微信公众号文章
        路由: /wechat/mp/{公众号名称}

        注意：需要知道公众号的名称（不是显示名称）
        """
        url = f"{self.rsshub_base}/wechat/mp/{account_name}"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                return []

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': '微信公众号'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取微信公众号失败: {e}")
            return []

    def fetch_zhihu_hot(self, limit: int = 10) -> list:
        """获取知乎热榜"""
        url = f"{self.rsshub_base}/zhihu/hotlist"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': '知乎热榜'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取知乎热榜失败: {e}")
            return []

    def fetch_baidu_news(self, keyword: str, limit: int = 10) -> list:
        """获取百度新闻"""
        url = f"{self.rsshub_base}/baidu/news/{keyword}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': '百度新闻'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取百度新闻失败: {e}")
            return []

    def fetch_github_trending(self, period: str = "daily", limit: int = 10) -> list:
        """
        获取 GitHub 趋势
        period: daily/weekly/monthly
        """
        url = f"{self.rsshub_base}/github/trending/{period}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': 'GitHub趋势'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取 GitHub 趋势失败: {e}")
            return []


def format_articles(articles: list, source_name: str) -> str:
    """格式化文章为 Markdown"""
    if not articles:
        return f"## {source_name}\n\n暂无文章\n\n"

    md_content = f"## {source_name}\n\n"
    md_content += f"文章数量：{len(articles)}\n\n"
    md_content += "---\n\n"

    for i, article in enumerate(articles, 1):
        md_content += f"### {i}. {article['title']}\n\n"
        md_content += f"**来源**：{article['source']}\n"
        md_content += f"**时间**：{article['published']}\n"
        md_content += f"**链接**：{article['link']}\n"

        if article.get('summary'):
            md_content += f"**摘要**：{article['summary']}\n"

        md_content += "\n---\n\n"

    return md_content


def main():
    """测试 RSSHub"""
    fetcher = RSSHubFetcher()

    print("=" * 60)
    print("RSSHub 测试")
    print("=" * 60)

    # 测试 1: 知乎热榜
    print("\n测试 1: 知乎热榜")
    zhihu_articles = fetcher.fetch_zhihu_hot(limit=3)
    print(f"获取到 {len(zhihu_articles)} 篇文章")
    if zhihu_articles:
        print(f"示例: {zhihu_articles[0]['title']}")

    # 测试 2: 百度新闻
    print("\n测试 2: 百度新闻 - 人工智能")
    baidu_articles = fetcher.fetch_baidu_news("人工智能", limit=3)
    print(f"获取到 {len(baidu_articles)} 篇文章")
    if baidu_articles:
        print(f"示例: {baidu_articles[0]['title']}")

    # 测试 3: GitHub 趋势
    print("\n测试 3: GitHub 趋势")
    github_articles = fetcher.fetch_github_trending(period="daily", limit=3)
    print(f"获取到 {len(github_articles)} 篇文章")
    if github_articles:
        print(f"示例: {github_articles[0]['title']}")

    # 测试 4: 微信公众号（可能需要准确的公众号名称）
    print("\n测试 4: 微信公众号（测试极客公园）")
    # 尝试几种可能的名称
    possible_names = ["geekpark", "GeekPark", "极客公园"]
    for name in possible_names:
        wechat_articles = fetcher.fetch_wechat_mp(name, limit=3)
        if wechat_articles:
            print(f"  名称: {name} - 获取到 {len(wechat_articles)} 篇文章")
            break
        else:
            print(f"  名称: {name} - 无结果")

    # 生成汇总
    print("\n" + "=" * 60)
    print("生成汇总报告")
    print("=" * 60)

    all_articles = []

    if zhihu_articles:
        all_articles.extend(zhihu_articles)
    if baidu_articles:
        all_articles.extend(baidu_articles)
    if github_articles:
        all_articles.extend(github_articles)

    if all_articles:
        md_content = "# RSSHub 内容汇总\n\n"
        md_content += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"

        md_content += format_articles(zhihu_articles, "知乎热榜")
        md_content += format_articles(baidu_articles, "百度新闻 - 人工智能")
        md_content += format_articles(github_articles, "GitHub 趋势")

        # 保存文件
        output_dir = Path("/root/.openclaw/workspace/temp/rsshub-articles")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rsshub_summary_{timestamp}.md"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\n✅ 已保存到: {filepath}")
        print(f"总文章数: {len(all_articles)}")
    else:
        print("\n❌ 未能获取到任何文章")


if __name__ == "__main__":
    main()
