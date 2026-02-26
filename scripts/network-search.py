#!/usr/bin/env python3
"""
网络搜索工具

功能：
1. 搜索指定的关键词
2. 获取搜索结果
3. 生成搜索报告

作者：rxy的狗腿子
版本：1.0.0
日期：2026-02-25
"""

import sys
import json
import os
import requests
import time
from typing import Dict, List, Any

def baidu_search(api_key: str, query: str) -> List[Dict[str, Any]]:
    """
    百度搜索
    
    Args:
        api_key: API密钥
        query: 搜索关键词
        
    Returns:
        搜索结果列表
    """
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }

    request_body = {
        "messages": [
            {
                "content": query,
                "role": "user"
            }
        ],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": 20}]
    }

    response = requests.post(url, json=request_body, headers=headers)
    response.raise_for_status()
    results = response.json()
    
    if "code" in results and results["code"] != 0:
        raise Exception(f"搜索错误：{results['message']}")
    
    if "references" not in results:
        return []
    
    references = results["references"]
    
    # 移除不需要的字段
    keys_to_remove = {"snippet"}
    for item in references:
        for key in keys_to_remove:
            if key in item:
                del item[key]
    
    return references

def generate_search_report(query: str, results: List[Dict[str, Any]]) -> str:
    """
    生成搜索报告
    
    Args:
        query: 搜索关键词
        results: 搜索结果列表
        
    Returns:
        Markdown格式的报告
    """
    report = [
        f"# 网络搜索报告",
        "",
        f"**搜索关键词**：{query}",
        f"**搜索时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**结果数量**：{len(results)}",
        "",
        "---",
        "",
        "## 📊 搜索结果",
        "",
    ]
    
    for i, result in enumerate(results, 1):
        title = result.get('title', '无标题')
        report.append(f"### {i}. {title}")
        report.append(f"**链接**：{result.get('url', '无链接')}")
        report.append(f"**域名**：{result.get('domain', '无域名')}")
        report.append("")
    
    report.extend([
        "---",
        "",
        "_搜索人：rxy的狗腿子_",
        f"_搜索时间：{time.strftime('%Y-%m-%d %H:%M:%S')}_"
    ])
    
    return "\n".join(report)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python3 network-search.py <搜索关键词>")
        print()
        print("示例：")
        print("  python3 network-search.py n1n 官网 最新状态")
        print("  python3 network-search.py zenmux 网站 无法访问")
        print()
        sys.exit(1)
    
    query = sys.argv[1]
    api_key = os.getenv("BAIDU_API_KEY")
    
    if not api_key:
        print("❌ 错误：BAIDU_API_KEY 环境变量未设置")
        print()
        print("请设置环境变量：")
        print("  export BAIDU_API_KEY='your_api_key_here'")
        print()
        sys.exit(1)
    
    print(f"正在搜索：{query}...")
    
    try:
        results = baidu_search(api_key, query)
        print(f"✅ 搜索完成！找到 {len(results)} 条结果")
        
        # 生成报告
        report = generate_search_report(query, results)
        
        # 保存报告
        report_file = f"/root/.openclaw/workspace/temp/search-report-{int(time.time())}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 报告已保存到：{report_file}")
        
        # 显示前3条结果
        print()
        print("前3条搜索结果：")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.get('title', '无标题')}")
            print(f"     链接：{result.get('url', '无链接')}")
        
    except Exception as e:
        print(f"❌ 搜索失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
