#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费 RSS 聚合器获取器
测试各种免费的 RSS 源
"""

import requests
import feedparser
from datetime import datetime
from pathlib import Path
import time


class FreeRSSAggregator:
    """免费 RSS 聚合器"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSSBot/1.0; +https://example.com)'
        }

        # 免费RSS源列表
        self.free_rss_sources = [
            {
                'name': '微信热榜',
                'url': 'https://rss.aishort.top/?type=wasi',
                'category': '微信',
                'description': '微信文章热门聚合'
            },
            {
                'name': '百度热点',
                'url': 'https://rss.aishort.top/?type=baidu',
                'category': '热点',
                'description': '百度新闻热点'
            },
            {
                'name': 'AI 热搜',
                'url': 'https://rss.aishort.top/?type=ai',
                'category': 'AI',
                'description': 'AI 相关热点'
            },
            {
                'name': '36氪',
                'url': 'https://36kr.com/feed',
                'category': '科技',
                'description': '36氪科技新闻'
            },
            {
                'name': '虎嗅',
                'url': 'https://www.huxiu.com/rss/0.xml',
                'category': '科技',
                'description': '虎嗅商业科技'
            },
            {
                'name': '少数派',
                'url': 'https://sspai.com/feed',
                'category': '生产力',
                'description': '少数派效率工具'
            }
        ]

    def fetch_rss(self, rss_config: dict, limit: int = 5) -> dict:
        """
        获取单个 RSS 源

        返回:
        {
            'name': RSS 名称,
            'success': True/False,
            'articles': [文章列表],
            'error': 错误信息
        }
        """
        result = {
            'name': rss_config['name'],
            'category': rss_config['category'],
            'description': rss_config['description'],
            'success': False,
            'articles': [],
            'error': ''
        }

        try:
            response = requests.get(
                rss_config['url'],
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                result['error'] = f"HTTP {response.status_code}"
                return result

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:limit]:
                # 提取并清理摘要
                summary = entry.get('summary', '')
                if summary:
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = ' '.join(summary.split())
                    summary = summary[:300] if len(summary) > 300 else summary

                article = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'summary': summary
                }
                articles.append(article)

            result['success'] = True
            result['articles'] = articles

        except Exception as e:
            result['error'] = str(e)

        return result

    def fetch_all(self, limit: int = 5) -> list:
        """获取所有 RSS 源"""
        all_results = []

        for rss_config in self.free_rss_sources:
            print(f"正在获取: {rss_config['name']}")

            result = self.fetch_rss(rss_config, limit)

            if result['success']:
                print(f"  ✅ 成功 - {len(result['articles'])} 篇文章")
            else:
                print(f"  ❌ 失败 - {result['error']}")

            all_results.append(result)

            # 避免请求过快
            time.sleep(2)

        return all_results


def format_articles(result: dict) -> str:
    """格式化文章为 Markdown"""
    md_content = f"## {result['name']}\n\n"
    md_content += f"**分类**: {result['category']}\n"
    md_content += f"**描述**: {result['description']}\n\n"

    if not result['success']:
        md_content += f"❌ 获取失败: {result['error']}\n\n"
        return md_content

    articles = result['articles']

    if not articles:
        md_content += "暂无文章\n\n"
        return md_content

    md_content += f"**文章数量**: {len(articles)}\n\n"
    md_content += "---\n\n"

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


def save_report(results: list, output_path: str):
    """保存汇总报告"""
    md_content = "# 免费 RSS 聚合内容汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += f"数据源数量: {len(results)}\n\n"

    total_articles = sum(len(r['articles']) for r in results)
    successful_sources = sum(1 for r in results if r['success'])

    md_content += f"总文章数: {total_articles}\n"
    md_content += f"成功获取: {successful_sources}/{len(results)}\n\n"
    md_content += "---\n\n"

    # 按分类分组
    categories = {}
    for result in results:
        category = result['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(result)

    # 按分类输出
    for category, category_results in categories.items():
        md_content += f"# {category}\n\n"

        for result in category_results:
            md_content += format_articles(result)

    # 保存文件
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"free_rss_summary_{timestamp}.md"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return str(filepath), total_articles, successful_sources


def main():
    """主函数"""
    print("=" * 70)
    print("免费 RSS 聚合器测试")
    print("=" * 70)

    aggregator = FreeRSSAggregator()

    # 获取所有 RSS 源
    print("\n开始获取 RSS 内容...\n")
    results = aggregator.fetch_all(limit=5)

    # 保存报告
    print("\n" + "=" * 70)
    print("生成汇总报告")
    print("=" * 70)

    output_dir = "/root/.openclaw/workspace/temp/free-rss-articles"
    filepath, total_articles, successful_sources = save_report(results, output_dir)

    print(f"\n✅ 已保存到: {filepath}")
    print(f"总文章数: {total_articles}")
    print(f"成功率: {successful_sources}/{len(results)}")


if __name__ == "__main__":
    main()
