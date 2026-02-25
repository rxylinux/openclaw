#!/usr/bin/env python3
"""
网站有效性检查工具

功能：
1. 检查网站是否可访问
2. 验证网站状态码
3. 检查网站响应时间

作者：rxy的狗腿子
版本：1.0.0
日期：2026-02-25
"""

import requests
import time
from typing import Dict, List, Any

# 要检查的网站列表
WEBSITES = [
    {"name": "n1n", "url": "https://n1n.com"},
    {"name": "dmaxapi", "url": "https://dmaxapi.com"},
    {"name": "AIHubmix", "url": "https://aihubmix.com"},
    {"name": "zenmux", "url": "https://zenmux.com"},
    {"name": "OhMyGPT", "url": "https://ohmygpt.com"},
    {"name": "aigc2d", "url": "https://aigc2d.com"}
]

def check_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    检查网站是否可访问
    
    Args:
        url: 网站URL
        timeout: 超时时间（秒）
        
    Returns:
        检查结果字典
    """
    result = {
        "url": url,
        "status_code": None,
        "accessible": False,
        "response_time": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = time.time()
        
        result["status_code"] = response.status_code
        result["response_time"] = round((end_time - start_time) * 1000, 2)  # 毫秒
        result["accessible"] = (response.status_code == 200)
        
        if response.status_code == 200:
            result["status"] = "✅ 正常"
        elif response.status_code == 404:
            result["status"] = "❌ 404 Not Found"
        elif response.status_code == 500:
            result["status"] = "⚠️ 500 Server Error"
        else:
            result["status"] = f"⚠️ {response.status_code}"
            
    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
        result["status"] = "⏰ 超时"
    except requests.exceptions.ConnectionError:
        result["error"] = "ConnectionError"
        result["status"] = "🔌 连接失败"
    except requests.exceptions.TooManyRedirects:
        result["error"] = "TooManyRedirects"
        result["status"] = "🔄 重定向过多"
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
        result["status"] = "❌ 访问失败"
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "❌ 未知错误"
    
    return result

def check_websites(websites: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    检查多个网站
    
    Args:
        websites: 网站列表
        
    Returns:
        检查结果列表
    """
    results = []
    
    for site in websites:
        print(f"正在检查 {site['name']} ({site['url']})...")
        result = check_website(site["url"])
        result["name"] = site["name"]
        results.append(result)
        print(f"  结果：{result['status']}")
        if result["response_time"]:
            print(f"  响应时间：{result['response_time']}ms")
        time.sleep(1)  # 避免请求过快
    
    return results

def generate_report(results: List[Dict[str, Any]]) -> str:
    """
    生成检查报告
    
    Args:
        results: 检查结果列表
        
    Returns:
        Markdown格式的报告
    """
    report = [
        "# AI模型聚合平台网站有效性检查报告",
        "",
        f"**检查时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## 📊 检查结果",
        "",
        "| 平台 | 网站 | 状态码 | 响应时间 | 可访问性 | 状态 |",
        "|-----|------|-------|---------|---------|------|"
    ]
    
    for result in results:
        accessible = "✅ 是" if result["accessible"] else "❌ 否"
        response_time = f"{result['response_time']}ms" if result["response_time"] else "-"
        
        report.append(f"| {result['name']} | {result['url']} | {result['status_code'] if result['status_code'] else '-'} | {response_time} | {accessible} | {result['status']} |")
    
    report.extend([
        "",
        "---",
        "",
        "## 📋 总结",
        "",
        f"- **总网站数**：{len(results)}",
        f"- **可访问网站数**：{len([r for r in results if r['accessible']])}",
        f"- **不可访问网站数**：{len([r for r in results if not r['accessible']])}",
        "",
        "## ❌ 不可访问网站列表",
        "",
    ])
    
    for result in results:
        if not result["accessible"]:
            report.append(f"- **{result['name']}**：{result['url']} - {result['status']} - 错误：{result['error']}")
    
    report.extend([
        "",
        "---",
        "",
        "## 💡 建议",
        "",
        "对于不可访问的网站：",
        "1. 检查网站URL是否正确",
        "2. 检查网站是否已关闭或更换域名",
        "3. 检查网络连接是否正常",
        "4. 尝试使用浏览器直接访问验证",
        ""
        "_检查人：rxy的狗腿子_",
        "_检查日期：2026-02-25_"
    ])
    
    return "\n".join(report)

def main():
    """主函数"""
    print("开始检查AI模型聚合平台网站有效性...")
    print()
    
    # 检查所有网站
    results = check_websites(WEBSITES)
    
    # 生成报告
    print()
    print("生成检查报告...")
    report = generate_report(results)
    
    # 保存报告
    report_file = "/root/.openclaw/workspace/随手记/ai模型聚合平台网站有效性检查.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 检查完成！")
    print(f"📄 报告已保存到：{report_file}")
    print()
    print("📊 检查摘要：")
    print(f"   总网站数：{len(results)}")
    print(f"   可访问网站数：{len([r for r in results if r['accessible']])}")
    print(f"   不可访问网站数：{len([r for r in results if not r['accessible']])}")

if __name__ == "__main__":
    main()
