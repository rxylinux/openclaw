#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台内容获取器
从多个平台获取科技、投资相关内容
包括：知乎、今日头条、CSDN 等
"""

import requests
import feedparser
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import time


class MultiPlatformFetcher:
    """
    多平台内容获取器

    支持的平台：
    - 知乎热榜
    - 知乎专栏（科技、投资相关）
    - CSDN 博客
    - InfoQ
    - 36氪
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSSBot/1.0; +https://example.com)'
        }

    def fetch_zhihu_hot(self, limit: int = 10) -> list:
        """获取知乎热榜"""
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()
            articles = []

            for item in data.get('data', [])[:limit]:
                target = item.get('target', {})
                article = {
                    'title': target.get('title', '无标题'),
                    'url': f"https://www.zhihu.com/question/{target.get('id', '')}",
                    'excerpt': target.get('excerpt', '')[:200],
                    'created': datetime.fromtimestamp(target.get('created', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'source': '知乎热榜'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取知乎热榜失败: {e}")
            return []

    def fetch_csdn_recommend(self, limit: int = 10) -> list:
        """获取 CSDN 推荐博客"""
        url = "https://blog.csdn.net/api/articles?type=more&category=home&shown_offset=0"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()
            articles = []

            for item in data.get('list', {})[:limit]:
                article = {
                    'title': item.get('title', '无标题'),
                    'url': item.get('url', ''),
                    'description': item.get('description', '')[:200],
                    'views': item.get('views', 0),
                    'source': 'CSDN'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取 CSDN 推荐失败: {e}")
            return []

    def fetch_36kr_hot(self, limit: int = 10) -> list:
        """获取 36氪热门文章"""
        url = "https://36kr.com/api/search-column/manuscripts"

        try:
            # 36氪的热门文章
            response = requests.get(
                "https://36kr.com/api/newsflash/newsflash-list",
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                return []

            data = response.json()
            articles = []

            # 尝试解析数据
            if isinstance(data, dict):
                items = data.get('data', {}).get('itemList', [])
            elif isinstance(data, list):
                items = data
            else:
                return []

            for item in items[:limit]:
                article = {
                    'title': item.get('title', '无标题'),
                    'url': f"https://36kr.com/p/{item.get('itemId', '')}",
                    'summary': item.get('description', '')[:200],
                    'source': '36氪'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取 36氪失败: {e}")
            return []

    def fetch_infoq_rss(self, limit: int = 10) -> list:
        """获取 InfoQ RSS"""
        url = "https://www.infoq.cn/feed"

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
                    'summary': re.sub(r'<[^>]+>', '', entry.get('summary', ''))[:200],
                    'source': 'InfoQ'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"获取 InfoQ 失败: {e}")
            return []

    def fetch_rsshub_zhihu(self, limit: int = 10) -> list:
        """尝试通过 RSSHub 获取知乎内容"""
        url = "https://rsshub.app/zhihu/hotlist"

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
                    'source': '知乎（RSSHub）'
                }
                articles.append(article)

            return articles

        except Exception as e:
            print(f"通过 RSSHub 获取知乎失败: {e}")
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

        if article.get('source'):
            md_content += f"**来源**: {article['source']}\n"

        if article.get('published'):
            md_content += f"**发布时间**: {article['published']}\n"

        if article.get('url'):
            md_content += f"**链接**: {article['url']}\n"
        elif article.get('link'):
            md_content += f"**链接**: {article['link']}\n"

        if article.get('summary'):
            md_content += f"\n**摘要**:\n{article['summary']}\n"
        elif article.get('description'):
            md_content += f"\n**摘要**:\n{article['description']}\n"
        elif article.get('excerpt'):
            md_content += f"\n**摘要**:\n{article['excerpt']}\n"

        md_content += "\n---\n\n"

    return md_content


def main():
    """测试多平台获取"""
    fetcher = MultiPlatformFetcher()

    print("=" * 60)
    print("多平台内容获取测试")
    print("=" * 60)

    all_sources = []

    # 测试 1: RSSHub 知乎
    print("\n测试 1: RSSHub - 知乎热榜")
    zhihu_articles = fetcher.fetch_rsshub_zhihu(limit=5)
    print(f"  获取到 {len(zhihu_articles)} 篇文章")
    if zhihu_articles:
        print(f"  示例: {zhihu_articles[0]['title']}")
    all_sources.append(('知乎热榜', zhihu_articles))

    time.sleep(2)

    # 测试 2: InfoQ
    print("\n测试 2: InfoQ RSS")
    infoq_articles = fetcher.fetch_infoq_rss(limit=5)
    print(f"  获取到 {len(infoq_articles)} 篇文章")
    if infoq_articles:
        print(f"  示例: {infoq_articles[0]['title']}")
    all_sources.append(('InfoQ', infoq_articles))

    time.sleep(2)

    # 测试 3: 36氪
    print("\n测试 3: 36氪热门")
    kr_articles = fetcher.fetch_36kr_hot(limit=5)
    print(f"  获取到 {len(kr_articles)} 篇文章")
    if kr_articles:
        print(f"  示例: {kr_articles[0]['title']}")
    all_sources.append(('36氪', kr_articles))

    time.sleep(2)

    # 测试 4: CSDN
    print("\n测试 4: CSDN 推荐")
    csdn_articles = fetcher.fetch_csdn_recommend(limit=5)
    print(f"  获取到 {len(csdn_articles)} 篇文章")
    if csdn_articles:
        print(f"  示例: {csdn_articles[0]['title']}")
    all_sources.append(('CSDN', csdn_articles))

    # 生成汇总报告
    print("\n" + "=" * 60)
    print("生成汇总报告")
    print("=" * 60)

    md_content = "# 多平台内容汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"

    total_articles = 0

    for source_name, articles in all_sources:
        md_content += format_articles(articles, source_name)
        total_articles += len(articles)

    # 保存文件
    output_dir = Path("/root/.openclaw/workspace/temp/multi-platform-articles")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"multi_platform_summary_{timestamp}.md"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✅ 已保存到: {filepath}")
    print(f"总文章数: {total_articles}")
    print(f"数据源数: {len(all_sources)}")


if __name__ == "__main__":
    main()
