#!/usr/bin/env python3
"""
Markdown转HTML转换工具

功能：
1. 读取Markdown文件
2. 将Markdown转换为HTML格式
3. 保存为HTML文件

作者：rxy的狗腿子
版本：1.0.0
日期：2026-02-25
"""

import markdown
import os
import sys

def markdown_to_html(markdown_file: str, html_file: str) -> str:
    """
    将Markdown文件转换为HTML文件
    
    Args:
        markdown_file: Markdown文件路径
        html_file: HTML文件路径
        
    Returns:
        HTML内容
    """
    # 读取Markdown文件
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 配置markdown扩展
    extensions = [
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ]
    
    # 转换Markdown为HTML
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(markdown_content)
    
    # 创建完整的HTML文档
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABCL财务分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        
        h3 {{
            color: #3498db;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        th {{
            background-color: #3498db;
            color: #fff;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        tr:hover {{
            background-color: #e8f4f8;
        }}
        
        .positive {{
            color: #28a745;
            font-weight: 600;
        }}
        
        .negative {{
            color: #dc3545;
            font-weight: 600;
        }}
        
        .warning {{
            color: #ffc107;
            font-weight: 600;
        }}
        
        .info {{
            color: #17a2b8;
            font-weight: 600;
        }}
        
        .success {{
            color: #28a745;
        }}
        
        .danger {{
            color: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""
    
    # 保存HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    return html_content

def main():
    """主函数"""
    # 默认文件路径
    markdown_file = "/root/.openclaw/workspace/skills/美股分析/财务报表深度拆解/scripts/reports/ABCL-financial-analysis-20260225.md"
    html_file = "/root/.openclaw/workspace/skills/美股分析/财务报表深度拆解/scripts/reports/ABCL-financial-analysis-20260225.html"
    
    # 如果提供了参数
    if len(sys.argv) > 1:
        markdown_file = sys.argv[1]
        html_file = markdown_file.replace('.md', '.html')
    
    print(f"正在转换 {markdown_file} 为HTML...")
    
    try:
        html_content = markdown_to_html(markdown_file, html_file)
        print(f"✅ 转换完成！")
        print(f"📄 HTML文件已保存到: {html_file}")
        print(f"📊 HTML内容长度: {len(html_content)} 字节")
    except Exception as e:
        print(f"❌ 转换失败: {e}")

if __name__ == "__main__":
    main()
