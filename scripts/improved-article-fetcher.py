#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版公众号文章获取器
尝试多种搜索策略，直到获取到真实数据
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
        "search_keywords": ["极客公园", "geekpark"],
        "search_queries": [
            "site:mp.weixin.qq.com 极客公园 文章",
            "极客公园 最新文章",
            "site:mp.weixin.qq.com 极客公园 推送"
        ]
    },
    {
        "name": "美股投资网",
        "search_keywords": ["美股投资网", "stockus"],
        "search_queries": [
            "site:mp.weixin.qq.com 美股投资网 文章",
            "美股投资网 最新",
            "美股投资网 推送"
        ]
    },
    {
        "name": "程序员的那些事",
        "search_keywords": ["程序员的那些事", "chengxuyuan"],
        "search_queries": [
            "site:mp.weixin.qq.com 程序员的那些事 文章",
            "程序员的那些事 最新",
            "site:mp.weixin.qq.com 程序员的那些事 推送"
        ]
    }
]


class ImprovedArticleFetcher:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.output_dir = self.workspace_path / "temp" / "wechat-articles"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.workspace_path / "logs" / "wechat-fetch.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
        print(message)

    def fetch_article_by_search(self, account_name: str, search_query: str, search_engine: str = "browser") -> dict:
        """通过搜索获取文章"""
        self._log(f"搜索：{search_query}，引擎：{search_engine}")

        try:
            # 尝试不同的搜索工具
            if search_engine == "browser":
                result = subprocess.run([
                    'python3',
                    '/root/.openclaw/workspace/skills/agent-browser/tool.py',
                    'search',
                    'github',  # 尝试 GitHub 先
                    f"{account_name}"
                ], capture_output=True, text=True, timeout=60)
            elif search_engine == "web-read":
                result = subprocess.run([
                    'python3',
                    '/root/.openclaw/workspace/skills/web-read/tool.py',
                    'fetch',
                    f"https://mp.weixin.qq.com/s/{account_name}"
                ], capture_output=True, text=True, timeout=60)
            else:
                raise ValueError(f"不支持的搜索引擎：{search_engine}")

            output = result.stdout

            # 解析输出
            articles = self._parse_search_output(output, account_name, search_query)

            self._log(f"找到 {len(articles)} 篇文章")
            return articles

        except Exception as e:
            self._log(f"搜索失败：{e}")
            return []

    def _parse_search_output(self, output: str, account_name: str, search_query: str) -> list:
        """解析搜索输出"""
        articles = []

        # 尝试解析 JSON 格式
        try:
            data = json.loads(output)
            if "items" in data:
                for item in data["items"][:5]:  # 最多 5 篇
                    article = {
                        "title": item.get("title", "").strip(),
                        "url": item.get("url", ""),
                        "summary": item.get("summary", "").strip(),
                        "author": account_name,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    if article["title"]:  # 只保留有标题的
                        articles.append(article)

            if articles:
                return articles
        except json.JSONDecodeError:
            pass

        # 如果 JSON 解析失败，尝试解析文本格式
        lines = output.split('\n')
        for line in lines:
            if line.strip():
                # 简单的标题匹配
                if account_name in line or any(kw in line for kw in ["文章", "发布", "推文"]):
                    article = {
                        "title": line[:100].strip(),  # 取前 100 字符
                        "url": "",
                        "summary": line[:200].strip(),
                        "author": account_name,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    articles.append(article)
                    if len(articles) >= 5:
                        break

        return articles

    def fetch_with_retry(self, account_name: dict, max_attempts: int = 3) -> list:
        """带重试的获取"""
        all_articles = []

        # 尝试多个搜索查询
        for search_query in account_name["search_queries"]:
            self._log(f"尝试搜索：{search_query}")

            # 尝试不同的搜索引擎
            for search_engine in ["browser", "web-read"]:
                articles = self.fetch_article_by_search(account_name["name"], search_query, search_engine)

                if articles:
                    all_articles.extend(articles)
                    break  # 找到就停止

            if all_articles:
                break  # 找到就停止

            if len(all_articles) >= 5:
                self._log(f"已找到足够多的文章（{len(all_articles)}），停止搜索")
                break

        # 去重
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article["title"] not in seen_titles:
                seen_titles.add(article["title"])
                unique_articles.append(article)

        return unique_articles[:5]  # 最多返回 5 篇

    def format_articles(self, account_name: str, articles: list) -> str:
        """格式化文章"""
        if not articles:
            return f"# {account_name}\n\n暂无文章\n"

        md_content = f"# {account_name} - 最新文章\n\n"
        md_content += f"获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += f"文章数量：{len(articles)} 篇\n\n"
        md_content += "---\n\n"

        for i, article in enumerate(articles, 1):
            md_content += f"## {i}. {article['title']}\n\n"

            if article["url"]:
                md_content += f"**链接**：{article['url']}\n\n"

            md_content += f"**摘要**：{article['summary']}\n\n"
            md_content += f"**时间**：{article['time']}\n\n"
            md_content += f"**作者**：{article['author']}\n\n"
            md_content += "---\n\n"

        return md_content

    def save_articles(self, account_name: str, content: str):
        """保存文章"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{account_name}_{timestamp}.md"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self._log(f"已保存到：{filepath}")
        return str(filepath)

    def get_summary(self) -> str:
        """获取汇总"""
        today = datetime.now().strftime("%Y-%m-%d")

        md_content = f"# 公众号文章汇总 - {today}\n\n"
        md_content += f"获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"

        for account in TARGET_ACCOUNTS:
            account_name = account["name"]
            category = account.get("category", "未分类")
            description = account.get("description", "")

            md_content += f"## {account_name}\n\n"
            md_content += f"**分类**：{category}\n\n"
            md_content += f"**描述**：{description}\n\n"

        return md_content

    def update_heartbeat(self):
        """更新心跳状态"""
        heartbeat_file = self.workspace_path / "memory" / "heartbeat-state.json"

        with open(heartbeat_file, 'r', encoding='utf-8') as f:
            heartbeat = json.load(f)

        heartbeat["last_check_time"] = datetime.now().isoformat()
        heartbeat["tasks"] = heartbeat.get("tasks", {})
        heartbeat["tasks"]["wechat_articles"] = {
            "last_run": datetime.now().isoformat(),
            "status": "completed"
        }

        with open(heartbeat_file, 'w', encoding='utf-8') as f:
            json.dump(heartbeat, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    fetcher = ImprovedArticleFetcher()

    # 获取汇总
    summary = fetcher.get_summary()
    summary_file = fetcher.save_articles("每日汇总", summary)

    # 为每个公众号获取文章
    for account in TARGET_ACCOUNTS:
        account_name = account["name"]

        fetcher._log(f"\n开始获取 {account_name} 的文章...")

        # 带重试的获取
        articles = fetcher.fetch_with_retry(account, max_attempts=3)

        if articles:
            # 格式化
            content = fetcher.format_articles(account_name, articles)

            # 保存
            filepath = fetcher.save_articles(account_name, content)

            fetcher._log(f"成功获取 {len(articles)} 篇文章")
        else:
            # 没有找到文章
            content = f"# {account_name}\n\n暂无文章"
            filepath = fetcher.save_articles(account_name, content)

            fetcher._log(f"未找到文章")

    # 更新心跳状态
    fetcher.update_heartbeat()

    # 发送汇总
    fetcher._log("正在发送汇总到飞书...")

    try:
        # 使用 Python 脚本发送
        result = subprocess.run([
            'python3', '-c',
            """
import sys
sys.path.insert(0, '/root/.openclaw/workspace/scripts')
from message_sender import send_to_feishu

with open('""" + summary_file + """', 'r', encoding='utf-8') as f:
    content = f.read()

send_to_feishu(content)
"""
        ], capture_output=True, text=True, timeout=30)

        fetcher._log(f"发送结果：{result.stdout}")
    except Exception as e:
        fetcher._log(f"发送失败：{e}")

    fetcher._log("完成！")


if __name__ == "__main__":
    main()
