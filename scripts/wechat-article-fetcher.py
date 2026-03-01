#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号文章获取器
使用 agent-browser 获取指定公众号的文章
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


# 目标公众号
TARGET_ACCOUNTS = [
    {
        "name": "极客公园",
        "description": "科技资讯、产品创新",
        "category": "科技"
    },
    {
        "name": "美股投资网",
        "description": "美股市场分析、投资策略",
        "category": "投资"
    },
    {
        "name": "程序员的那些事",
        "description": "程序员职场、技术话题",
        "category": "职场"
    }
]


class WechatArticleFetcher:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.output_dir = self.workspace_path / "temp" / "wechat-articles"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_articles(self, account_name: str, limit: int = 5) -> list:
        """获取公众号文章"""
        # 使用 agent-browser 搜索
        search_query = f"{account_name} 公众号 文章"

        # 调用 agent-browser
        result = subprocess.run([
            'python3',
            '/root/.openclaw/workspace/skills/agent-browser/tool.py',
            'search',
            'wechat',
            f"{account_name}"
        ], capture_output=True, text=True, timeout=120)

        output = result.stdout

        # 解析结果（简化版，假设返回 JSON 格式）
        articles = self._parse_articles(output, account_name, limit)

        return articles

    def _parse_articles(self, content: str, account_name: str, limit: int) -> list:
        """解析文章内容（简化版）"""
        articles = []

        # 这里需要根据实际的 agent-browser 输出格式来调整
        # 暂时返回模拟数据
        for i in range(min(limit, 5)):
            article = {
                "title": f"{account_name} - 示例文章标题 {i+1}",
                "url": f"https://mp.weixin.qq.com/s/xxxxxxxx",
                "author": account_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "summary": f"这是 {account_name} 的第 {i+1} 篇示例文章的摘要内容..."
            }
            articles.append(article)

        return articles

    def format_articles(self, articles: list) -> str:
        """格式化文章为 Markdown"""
        if not articles:
            return "暂无文章"

        md_content = f"# {articles[0]['author']} - 最新文章\n\n"
        md_content += f"获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"

        for i, article in enumerate(articles, 1):
            md_content += f"## {i}. {article['title']}\n\n"
            md_content += f"**时间**：{article['time']}\n\n"
            md_content += f"**链接**：{article['url']}\n\n"
            md_content += f"**摘要**：{article['summary']}\n\n"
            md_content += "---\n\n"

        return md_content

    def save_articles(self, account_name: str, content: str):
        """保存文章到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{account_name}_{timestamp}.md"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def get_daily_summary(self) -> str:
        """获取每日摘要"""
        today = datetime.now().strftime("%Y-%m-%d")

        md_content = f"# 公众号文章汇总 - {today}\n\n"
        md_content += f"获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"

        for account in TARGET_ACCOUNTS:
            md_content += f"## {account['name']}\n\n"
            md_content += f"**分类**：{account['category']}\n"
            md_content += f"**描述**：{account['description']}\n\n"

        return md_content


def main():
    """主函数"""
    fetcher = WechatArticleFetcher()

    # 获取每日摘要
    summary = fetcher.get_daily_summary()

    # 保存摘要
    summary_file = fetcher.save_articles("每日汇总", summary)

    # 为每个公众号获取文章
    for account in TARGET_ACCOUNTS:
        account_name = account['name']
        print(f"正在获取 {account_name} 的文章...")

        # 获取文章
        articles = fetcher.fetch_articles(account_name, limit=3)

        # 格式化
        content = fetcher.format_articles(articles)

        # 保存
        filepath = fetcher.save_articles(account_name, content)

        print(f"已保存到：{filepath}")

    # 发送飞书消息
    print("\n正在发送到飞书...")

    # 读取摘要文件
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary_content = f.read()

    # 发送消息
    try:
        result = subprocess.run([
            'python3', '-c',
            """
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from message_sender import send_to_feishu

content = '''%s'''

result = send_to_feishu(content)
print(result.stdout)
""" % summary_content
        ], capture_output=True, text=True, timeout=30)

        print(f"发送结果：{result.stdout}")
    except Exception as e:
        print(f"发送失败：{e}")


if __name__ == "__main__":
    main()
