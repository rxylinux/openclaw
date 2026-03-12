#!/usr/bin/env python3
"""
科技新闻抓取脚本
抓取科技和AI相关新闻，去重后推送
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加技能路径
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "baidu-search"))

def is_valid_news(item):
    """判断是否是有效的新闻文章（过滤栏目页、首页等）"""
    title = item.get("title", "").strip()
    url = item.get("url", "").strip()
    content = item.get("content", "").strip()

    # 标题太短或太泛泛，可能是栏目页
    if len(title) < 10:
        return False

    # 标题只是"人工智能"、"科技"等泛指词
    if title in ["人工智能", "科技", "AI", "人工智能·AI", "科技频道·央广网",
                 "科技_新华网_让新闻离你更近", "中华人民共和国科学技术部"]:
        return False

    # 标题包含"频道"、"主页"、"首页"、"导航"、"网_"等字样
    if any(x in title for x in ["频道", "主页", "首页", "导航", "网_", "科技快讯"]):
        return False

    # URL 是根路径或栏目首页
    if url.endswith(".cn/") or url.endswith(".com/") or url.endswith(".net/") or \
       url.endswith("/index.htm") or url.endswith("/index.html") or \
       "/szyw/" in url or "/mobile/index.htm" in url or "/kjkx/" in url:
        return False

    # 标题中包含政府机构名称，可能是官网首页
    if "中华人民共和国" in title and "部" in title:
        return False

    # 内容太短，可能是页面框架
    if content and len(content) < 50:
        return False

    # 标题看起来像是一列标题列表（多个标题用顿号分隔）
    if "、" in title and title.count("、") > 3:
        return False

    return True

def search_news(query, days=1, top_k=10):
    """搜索新闻"""
    script_path = Path(__file__).parent.parent / "skills" / "baidu-search" / "scripts" / "search.py"

    search_params = {
        "query": query,
        "search_recency_filter": "week",  # 获取最近一周的新闻
        "resource_type_filter": [
            {"type": "web", "top_k": top_k + 5}  # 多获取一些，因为要过滤
        ]
    }

    import subprocess
    result = subprocess.run(
        [sys.executable, str(script_path), json.dumps(search_params)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"搜索失败: {result.stderr}", file=sys.stderr)
        return []

    # 百度搜索API返回格式: 先输出成功消息+请求参数，然后是JSON数组
    try:
        stdout = result.stdout
        # 查找包含 "id": 的 [ 位置，这是真正的数据开始位置
        # 因为输出格式是: success parse request body: [...]\n[\n  {\n    "id": ...
        # 所以需要找到第二个 [
        first_bracket = stdout.find('[')
        if first_bracket != -1:
            # 找第二个 [
            second_bracket = stdout.find('[\n', first_bracket + 1)
            if second_bracket == -1:
                second_bracket = stdout.find('[', first_bracket + 1)

            if second_bracket != -1:
                # 从第二个 [ 开始解析
                json_str = stdout[second_bracket:]

                # 移除可能存在的尾部注释或非JSON内容
                # 找到最后一个 ] 的位置
                bracket_end = json_str.rfind(']')
                if bracket_end != -1:
                    json_str = json_str[:bracket_end + 1]

                data = json.loads(json_str)
                # 过滤掉无效的新闻（栏目页、首页等）
                valid_news = [item for item in data if is_valid_news(item)]
                print(f"  过滤: {len(data)} → {len(valid_news)}", file=sys.stderr)
                return valid_news

        # 如果没找到，尝试直接解析（备用方案）
        data = json.loads(stdout)
        if isinstance(data, list):
            return [item for item in data if is_valid_news(item)]
        if isinstance(data, dict):
            return [item for item in data.get("results", []) if is_valid_news(item)]
        return []
    except json.JSONDecodeError as e:
        print(f"解析结果失败: {e}", file=sys.stderr)
        # 只打印前1000字符避免太长
        print(f"输出前1000字符: {stdout[:1000]}", file=sys.stderr)
        return []

def dedupe_news(news_items, history_file):
    """去重"""
    # 读取历史记录
    history = set()
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = set(json.load(f))
        except:
            pass

    # 过滤已推送的新闻
    new_items = []
    for item in news_items:
        # 使用URL作为唯一标识
        url = item.get("url", "")
        title = item.get("title", "")

        # 简单的去重策略：URL或标题相似
        is_duplicate = False
        for history_url in history:
            if url in history_url or history_url in url:
                is_duplicate = True
                break
            # 标题相似度检查（简单版）
            if title and len(title) > 5:
                history_title = history_url.split("|||")[0] if "|||" in history_url else ""
                if history_title and (title in history_title or history_title in title):
                    is_duplicate = True
                    break

        if not is_duplicate:
            new_items.append(item)

    # 更新历史记录
    new_history = history.copy()
    for item in new_items:
        url = item.get("url", "")
        title = item.get("title", "")
        new_history.add(f"{title}|||{url}")

    # 保存历史记录（只保留最近100条）
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(list(new_history)[-100:], f, ensure_ascii=False, indent=2)

    return new_items

def generate_analysis(title, content):
    """使用 AI 生成新闻分析（重点投资机会，更紧凑）"""
    import subprocess

    prompt = f"""请从投资角度分析以下科技新闻（80-120字，紧凑格式）：

标题：{title}
内容摘要：{content[:200] if content else '暂无'}

重点分析方向：
1. 投资机会（具体标的）
2. 市场空间（数据预测）
3. 投资逻辑（核心驱动）
4. 风险提示（关键风险）

要求：
- 紧凑格式，避免过多分段
- 用 | 分隔不同维度
- 简洁专业

分析："""

    try:
        # 调用 zai/GLM API
        import os

        # 使用 curl 调用 API
        curl_cmd = [
            "curl", "-s", "-X", "POST",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer f7e03893f91c4bdb970e8aea9859f422.bxVdixIhlImG3KoK",
            "-d", json.dumps({
                "model": "glm-4-flash",  # 使用 flash 模型更快
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            })
        ]

        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "choices" in response and len(response["choices"]) > 0:
                analysis = response["choices"][0]["message"]["content"].strip()
                return analysis
    except Exception as e:
        print(f"AI 分析失败: {e}", file=sys.stderr)

    return "⚠️ AI 分析生成失败"

def format_news(news_items, offset=0):
    """格式化新闻（包含 AI 分析）"""
    output = []
    for idx, item in enumerate(news_items, 1):
        i = offset + idx
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        content = item.get("content", "").strip()

        if title:
            news_line = f"{i}. {title}"
            if url:
                news_line += f"\n   {url}"

            # 生成 AI 分析
            analysis = generate_analysis(title, content)
            if analysis and "⚠️" not in analysis:
                news_line += f"\n   💡 {analysis}"

            # 添加内容摘要
            if content and len(content) > 50:
                news_line += f"\n   📝 {content[:150]}..."

            output.append(news_line)

    return "\n\n".join(output)

def format_news_simple(news_items, offset=0):
    """格式化新闻（不含 AI 分析）"""
    output = []
    for idx, item in enumerate(news_items, 1):
        i = offset + idx
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        content = item.get("content", "").strip()

        if title:
            news_line = f"{i}. {title}"
            if url:
                news_line += f"\n   {url}"

            # 添加内容摘要
            if content and len(content) > 50:
                news_line += f"\n   📝 {content[:150]}..."

            output.append(news_line)

    return "\n\n".join(output)

def split_message(output, max_bytes=3000):
    """将消息按合理位置拆分成多条（最多在新闻条目之间拆分）"""
    # 使用字节长度判断（中文占多字节）
    total_bytes = len(output.encode('utf-8'))
    if total_bytes <= max_bytes:
        return [output]

    # 找到所有新闻条目的分割点（"数字. 标题" 格式）
    import re
    pattern = r'\n(\d+)\. '
    matches = list(re.finditer(pattern, output))

    # 提取标题和时间
    header_match = re.search(r'^(.+)📱 【科技新闻】(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', output, re.MULTILINE | re.DOTALL)
    if header_match:
        header = header_match.group(0) + "\n\n"
        time_str = header_match.group(2)
    else:
        header = ""
        time_str = ""

    # 提取每个新闻条目（包括其前面的数字标题）
    news_items = []
    for i, match in enumerate(matches):
        start_pos = match.start()
        # 下一条新闻的开始位置
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(output)
        news_content = output[start_pos:end_pos]
        news_items.append(news_content)

    # 如果没有找到新闻条目，按字节强制拆分
    if not news_items:
        return split_by_bytes(output, max_bytes)

    # 将新闻条目分组，每组不超过max_bytes
    parts = []
    current_part = header
    current_bytes = len(header.encode('utf-8'))

    for i, news in enumerate(news_items):
        news_bytes = len(news.encode('utf-8'))

        # 如果加上这条新闻会超过限制，并且当前部分已经有内容了
        if current_bytes + news_bytes > max_bytes and current_part != header:
            parts.append(current_part)
            # 新的部分从标题开始
            part_num = len(parts) + 1
            current_part = f"📱 【科技新闻（续）{part_num}】{time_str}\n\n"
            current_bytes = len(current_part.encode('utf-8'))

        current_part += news
        current_bytes += news_bytes

    # 添加最后一部分
    if current_part.strip():
        parts.append(current_part)

    return parts

def split_by_bytes(text, max_bytes):
    """按字节长度强制拆分文本（小心处理多字节字符）"""
    parts = []
    current_part = ""
    current_bytes = 0

    for char in text:
        char_bytes = len(char.encode('utf-8'))
        if current_bytes + char_bytes > max_bytes and current_part:
            parts.append(current_part)
            current_part = ""
            current_bytes = 0
        current_part += char
        current_bytes += char_bytes

    if current_part:
        parts.append(current_part)

    return parts

def main():
    # 历史记录文件
    workspace = Path(__file__).parent.parent
    history_file = workspace / "memory" / "news-history.json"
    history_file.parent.mkdir(exist_ok=True)

    # 搜索查询（扩大范围，覆盖更多科技细分领域）
    queries = [
        "人工智能 AI 最新新闻",
        "科技新闻 最新动态",
        "AI 大模型 科技",
        "人工智能 行业资讯",
        "芯片半导体 最新动态",
        "新能源汽车 科技",
        "人形机器人 产业",
        "液冷服务器 散热",
        "智能制造 工业互联网",
        "量子计算 突破",
        "生物科技 医药",
        "5G 6G 通信技术",
        "云计算 数据中心"
    ]

    all_news = []
    seen_titles = set()

    # 搜索每个查询
    for query in queries:
        print(f"搜索: {query}")
        news = search_news(query, days=1, top_k=8)

        for item in news:
            title = item.get("title", "").strip()
            # 按标题去重
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_news.append(item)

        # 防止请求过多
        import time
        time.sleep(0.5)

    if not all_news:
        print("没有找到新闻")
        # 删除旧的索引文件，避免推送旧新闻
        index_file = workspace / "temp" / "latest-news-index.json"
        if index_file.exists():
            index_file.unlink()
            print("已删除旧索引文件")
        return

    print(f"共找到 {len(all_news)} 条新闻")

    # 去重
    deduped_news = dedupe_news(all_news, str(history_file))
    print(f"去重后: {len(deduped_news)} 条")

    if not deduped_news:
        print("没有新内容")
        return

    # 只取前10条
    top_news = deduped_news[:10]

    print(f"正在为前5条新闻生成AI分析...")
    # 只为前5条生成 AI 分析，其他只显示摘要
    news_with_analysis = top_news[:5]
    news_without_analysis = top_news[5:]

    # 格式化输出
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"📱 【科技新闻】{now}"
    footer = f"\n\n---\n抓取: {len(all_news)} → 去重: {len(deduped_news)} → 精选: {len(top_news)} (含AI分析: {len(news_with_analysis)})"

    formatted_with = format_news(news_with_analysis, offset=0)
    formatted_without = format_news_simple(news_without_analysis, offset=len(news_with_analysis))

    output = f"{header}\n\n{formatted_with}\n\n{formatted_without}{footer}"

    print(f"\n消息总长度: {len(output)} 字符 ({len(output.encode('utf-8'))} 字节)")

    # 检查是否需要拆分（使用字节长度判断，因为中文占多字节）
    max_bytes = 3000  # 3000字节，适应飞书客户端显示
    message_bytes = len(output.encode('utf-8'))
    if message_bytes > max_bytes:
        print(f"消息超过 {max_bytes} 字节，正在拆分成多条...")
        message_parts = split_message(output, max_bytes)
        print(f"已拆分为 {len(message_parts)} 条消息")

        # 保存每条消息到单独文件
        temp_dir = workspace / "temp"
        temp_dir.mkdir(exist_ok=True)

        message_files = []
        for i, part in enumerate(message_parts, 1):
            part_file = temp_dir / f"latest-news-{i}.md"
            with open(part_file, 'w', encoding='utf-8') as f:
                f.write(part)
            message_files.append(part_file.name)
            print(f"  保存: {part_file} ({len(part)} 字符)")

        # 保存索引文件
        index_file = temp_dir / "latest-news-index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_parts": len(message_parts),
                "files": message_files,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print(f"\n索引文件已保存: {index_file}")
    else:
        # 保存到单个文件
        temp_file = workspace / "temp" / "latest-news.md"
        temp_file.parent.mkdir(exist_ok=True)
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(output)

        # 保存索引文件（单条消息）
        index_file = workspace / "temp" / "latest-news-index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_parts": 1,
                "files": ["latest-news.md"],
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(output)
        print("=" * 60)
        print(f"\n已保存到: {temp_file}")

if __name__ == "__main__":
    main()
