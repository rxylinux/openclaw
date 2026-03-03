#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狗微信文章获取器
基于 WechatSogou 开源项目，免费获取微信公众号文章
"""

import sys
import json
from datetime import datetime
from pathlib import Path

try:
    from wechatsogou import WechatSogouAPI
    WECHAT_SOUGOU_AVAILABLE = True
except ImportError:
    WECHAT_SOUGOU_AVAILABLE = False


class SogouWechatFetcher:
    """搜狗微信文章获取器"""

    def __init__(self):
        self.available = WECHAT_SOUGOU_AVAILABLE

        if self.available:
            self.api = WechatSogouAPI()
        else:
            print("警告: wechatsogou 库未安装")
            print("安装命令: pip install wechatsogou --upgrade")

    def search_account(self, keyword: str) -> list:
        """
        搜索公众号

        返回:
        [
            {
                'name': 公众号名称,
                'wechat_id': 公众号ID,
                'head_img': 头像,
                'verified': 是否认证
            }
        ]
        """
        if not self.available:
            return []

        try:
            result = self.api.search_gzh(keyword)
            accounts = []

            for account in result.get('wechats', [])[:5]:
                accounts.append({
                    'name': account.get('name', ''),
                    'wechat_id': account.get('wechatid', ''),
                    'head_img': account.get('headimg', ''),
                    'verified': account.get('verified', False)
                })

            return accounts

        except Exception as e:
            print(f"搜索公众号失败: {e}")
            return []

    def get_account_articles(self, wechat_id: str, limit: int = 10) -> list:
        """
        获取公众号文章

        参数:
            wechat_id: 公众号ID
            limit: 文章数量

        返回:
        [
            {
                'title': 文章标题,
                'url': 文章链接,
                'time': 发布时间,
                'summary': 摘要,
                'source': 搜狗微信
            }
        ]
        """
        if not self.available:
            return []

        try:
            # 通过公众号ID获取文章
            # 注意：这个方法可能需要公众号名称而不是ID
            result = self.api.search_article(wechat_id)
            articles = []

            for article in result.get('items', [])[:limit]:
                articles.append({
                    'title': article.get('title', '无标题'),
                    'url': article.get('url', ''),
                    'time': article.get('time', ''),
                    'summary': article.get('content', '')[:200],
                    'source': '搜狗微信'
                })

            return articles

        except Exception as e:
            print(f"获取文章失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_hot_articles(self, category: str = '科技', limit: int = 10) -> list:
        """
        获取热门文章

        参数:
            category: 分类（科技、财经、生活等）
            limit: 文章数量

        返回:
        [文章列表]
        """
        if not self.available:
            return []

        try:
            result = self.api.get_gzh_article_by_hot(category)
            articles = []

            for article in result.get('items', [])[:limit]:
                articles.append({
                    'title': article.get('title', '无标题'),
                    'url': article.get('url', ''),
                    'time': article.get('time', ''),
                    'account': article.get('account', {}).get('name', ''),
                    'source': f'搜狗微信 - {category}热榜'
                })

            return articles

        except Exception as e:
            print(f"获取热门文章失败: {e}")
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

        if article.get('time'):
            md_content += f"**发布时间**: {article['time']}\n"

        if article.get('url'):
            md_content += f"**链接**: {article['url']}\n"

        if article.get('account'):
            md_content += f"**公众号**: {article['account']}\n"

        if article.get('summary'):
            md_content += f"\n**摘要**:\n{article['summary']}\n"

        md_content += "\n---\n\n"

    return md_content


def main():
    """测试搜狗微信获取"""
    print("=" * 60)
    print("搜狗微信文章获取器测试")
    print("=" * 60)

    # 检查依赖
    if not WECHAT_SOUGOU_AVAILABLE:
        print("\n❌ wechatsogou 库未安装")
        print("\n安装命令:")
        print("  pip install wechatsogou --upgrade")
        print("\n或者:")
        print("  pip install git+https://github.com/Chyroc/wechat_sogou.git")
        return

    fetcher = SogouWechatFetcher()

    # 测试 1: 搜索公众号
    print("\n测试 1: 搜索公众号")
    print("-" * 60)

    test_accounts = ["极客公园", "量子位", "虎嗅"]
    all_results = []

    for account_name in test_accounts:
        print(f"\n搜索: {account_name}")
        accounts = fetcher.search_account(account_name)

        if accounts:
            print(f"  找到 {len(accounts)} 个公众号")

            for acc in accounts[:1]:  # 只取第一个
                print(f"  名称: {acc['name']}")
                print(f"  ID: {acc['wechat_id']}")

                # 尝试获取文章
                print(f"  正在获取文章...")
                articles = fetcher.get_account_articles(acc['wechat_id'], limit=3)

                if articles:
                    print(f"  文章数: {len(articles)}")
                    print(f"  最新: {articles[0]['title']}")

                    all_results.append({
                        'name': acc['name'],
                        'articles': articles
                    })
                    break
        else:
            print(f"  未找到公众号")

        import time
        time.sleep(2)

    # 生成汇总报告
    print("\n" + "=" * 60)
    print("生成汇总报告")
    print("=" * 60)

    md_content = "# 搜狗微信文章汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"

    total_articles = 0

    for result in all_results:
        account_name = result['name']
        articles = result['articles']

        md_content += format_articles(articles, account_name)
        total_articles += len(articles)

    # 保存文件
    output_dir = Path("/root/.openclaw/workspace/temp/sogou-wechat-articles")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sogou_summary_{timestamp}.md"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✅ 已保存到: {filepath}")
    print(f"总文章数: {total_articles}")
    print(f"公众号数: {len(all_results)}")


if __name__ == "__main__":
    main()
