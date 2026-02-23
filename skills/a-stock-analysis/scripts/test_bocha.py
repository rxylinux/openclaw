#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博查API测试脚本
测试API密钥是否有效，并演示基本用法
"""

import os
import sys


def test_bocha_api():
    """测试博查API"""

    # 检查API密钥
    api_key = os.getenv('BOCHA_API_KEY')
    if not api_key:
        print("="*60)
        print(" 博查API测试")
        print("="*60)
        print("\n❌ 未设置博查API密钥")
        print("\n获取步骤:")
        print("1. 访问: https://open.bocha.cn")
        print("2. 注册账号")
        print("3. 获取API-KEY")
        print("4. 设置环境变量:")
        print("   export BOCHA_API_KEY=your_api_key")
        print("\n然后重新运行此脚本")
        print("="*60)
        return False

    print("="*60)
    print(" 博查API测试")
    print("="*60)
    print(f"\n✅ 检测到API密钥: {api_key[:10]}...{api_key[-4:]}")
    print("\n开始测试...")

    try:
        from bocha_search import BochaSearchClient

        # 初始化客户端
        client = BochaSearchClient(api_key)

        # 测试搜索
        print("\n[测试1] 网页搜索测试")
        result = client.web_search(
            query="双环传动 基本信息",
            count=3,
            freshness="month",
            summary=True
        )

        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            return False

        print("✅ 网页搜索成功!")
        print(f"   返回结果数: {len(result.get('web_results', []))}")

        # 显示前3个结果
        if 'web_results' in result:
            for i, item in enumerate(result['web_results'][:3], 1):
                print(f"\n   结果 {i}:")
                print(f"   标题: {item.get('title', 'N/A')}")
                print(f"   URL: {item.get('url', 'N/A')}")
                if 'snippet' in item:
                    snippet = item['snippet'][:100]
                    print(f"   摘要: {snippet}...")

        print("\n" + "="*60)
        print("✅ 博查API测试成功！")
        print("="*60)
        print("\n下一步:")
        print("1. 搜索股票信息:")
        print("   python3 bocha_search.py 002472 双环传动")
        print("\n2. 搜索最新新闻:")
        print("   python3 bocha_search.py 002472 双环传动 --news")
        print("\n3. 查看完整指南:")
        print("   cat BOCHA_API_GUIDE.md")
        print("="*60)

        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装 requests: pip3 install requests")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = test_bocha_api()
    sys.exit(0 if success else 1)
