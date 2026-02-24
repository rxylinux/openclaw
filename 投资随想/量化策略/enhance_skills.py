#!/usr/bin/env python3
"""
为14个量化策略技能添加详细的参考文档和Python代码实现
"""
import os
import re
import shutil
from pathlib import Path

# 技能映射
SKILL_MAPPING = {
    'bridgewatermacrotrader': 'Bridgewater宏观交易策略师',
    'citadelalphasignallab': 'Citadel阿尔法信号研究实验室',
    'deshawstatisticalarb': 'D.E. Shaw统计套利系统',
    'janestreetmarketmaker': 'Jane Street做市引擎',
    'mangroupportfoliooptimizer': 'Man Group投资组合优化引擎',
    'millenniumlivesystem': 'Millennium Management实时交易系统',
    'point72mlresearcher': 'Point72机器学习阿尔法研究员',
    'twosigariskmanager': 'Two Sigma风险管理系统',
    'virtuexecutionalgorithms': 'Virtu Financial执行算法设计师',
    'bloombergdatapipeline': '彭博终端数据管道构建器',
    'renaissancetechbacktester': '文艺复兴技术公司回测引擎',
    'dimensionalfactorbacktester': '美国维度基金公司因子回测器',
    'goldmancomplianceframework': '高盛算法交易合规框架',
    'goldmanquantarchitect': '高盛量化策略架构师'
}

BASE_DIR = Path('/Volumes/solid hard disk/github/rxylinux/openclaw/投资随想/量化策略')
SKILLS_DIR = BASE_DIR / 'skills'


def extract_python_code(content: str) -> list:
    """从markdown中提取Python代码块"""
    pattern = r'```python\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches


def create_core_methodology(content: str, skill_name: str, skill_cn: str) -> str:
    """创建核心方法论文档"""
    # 提取主要章节
    sections = []
    lines = content.split('\n')
    current_section = []
    in_code_block = False
    section_count = 0

    for line in lines:
        # 跳过代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 收集主要章节
        if line.startswith('##') or line.startswith('#'):
            if current_section and len(current_section) > 2:
                sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        sections.append('\n'.join(current_section))

    # 构建方法论文档
    doc = f"# {skill_cn}核心方法论\n\n"
    doc += "## 核心概念与理论框架\n\n"

    # 添加提取的非代码内容
    for section in sections[:5]:  # 取前5个主要章节
        doc += section + "\n\n"

    return doc


def create_python_implementation_guide(content: str, skill_name: str, skill_cn: str) -> str:
    """创建Python实现指南"""
    doc = f"# {skill_cn}Python实现指南\n\n"
    doc += "## 完整实现架构\n\n"

    # 提取代码块
    code_blocks = extract_python_code(content)

    if code_blocks:
        doc += "### 主要组件\n\n"
        for i, code in enumerate(code_blocks[:3], 1):
            # 提取类名或函数名
            class_match = re.search(r'class\s+(\w+)', code)
            func_match = re.search(r'def\s+(\w+)', code)
            if class_match:
                doc += f"{i}. **{class_match.group(1)}** - 主要类\n"
            elif func_match:
                doc += f"{i}. **{func_match.group(1)}** - 主要函数\n"

        doc += "\n## 代码实现\n\n"
        for i, code in enumerate(code_blocks, 1):
            doc += f"### 代码块 {i}\n\n```python\n{code}\n```\n\n"

    return doc


def create_implementation_py(content: str, skill_name: str) -> str:
    """创建Python实现文件"""
    code_blocks = extract_python_code(content)

    header = f'"""'
    header += f'{skill_name.upper()} - 量化策略实现\n'
    header += f'自动从原始文档提取的Python代码\n'
    header += f'"""\n\n'
    header += 'import numpy as np\n'
    header += 'import pandas as pd\n'
    header += 'from typing import Dict, List, Optional, Tuple\n'
    header += 'from dataclasses import dataclass\n\n\n'

    implementations = []
    for code in code_blocks:
        implementations.append(code.strip())

    return header + '\n\n'.join(implementations)


def process_skill(skill_id: str, skill_cn: str):
    """处理单个技能"""
    print(f"处理 {skill_id} ({skill_cn})...")

    # 路径
    original_md = BASE_DIR / f'{skill_cn}.md'
    skill_dir = SKILLS_DIR / skill_id
    refs_dir = skill_dir / 'references'
    assets_dir = skill_dir / 'assets'

    # 检查原始文件
    if not original_md.exists():
        print(f"  警告: 原始MD文件不存在: {original_md}")
        return

    # 读取原始内容
    with open(original_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 创建目录
    refs_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 创建references/README.md
    refs_readme = refs_dir / 'README.md'
    if not refs_readme.exists():
        refs_readme.write_text("""# 参考文档

此目录存放该技能的详细参考文档，包括：
- core-methodology.md: 核心方法论和理论框架
- python-implementation.md: Python代码实现指南
- terminology.md: 专业术语解释

这些文档从原始 Markdown 文件中提取相关内容创建。
""", encoding='utf-8')

    # 创建references/core-methodology.md
    core_methodology = create_core_methodology(content, skill_id, skill_cn)
    (refs_dir / 'core-methodology.md').write_text(core_methodology, encoding='utf-8')

    # 创建references/python-implementation.md
    py_guide = create_python_implementation_guide(content, skill_id, skill_cn)
    (refs_dir / 'python-implementation.md').write_text(py_guide, encoding='utf-8')

    # 创建assets/README.md
    assets_readme = assets_dir / 'README.md'
    if not assets_readme.exists():
        assets_readme.write_text("""# 资产文件

此目录存放该技能的资产文件，包括：
- Python实现代码 (.py)
- 配置文件 (.yaml, .json)
- 模板文件
- 其他静态资源

这些文件可以被 Claude Code 读取并复制到输出中，但不会自动加载到上下文。
""", encoding='utf-8')

    # 创建assets/implementation.py
    py_code = create_implementation_py(content, skill_id)
    (assets_dir / 'implementation.py').write_text(py_code, encoding='utf-8')

    # 统计信息
    code_blocks = extract_python_code(content)
    lines = len(py_code.split('\n'))

    print(f"  完成:")
    print(f"    - references/core-methodology.md: {len(core_methodology)} 字符")
    print(f"    - references/python-implementation.md: {len(py_guide)} 字符")
    print(f"    - assets/implementation.py: {lines} 行, {len(code_blocks)} 个代码块")


def main():
    """主函数"""
    print("=" * 60)
    print("开始为14个量化策略技能添加详细文档")
    print("=" * 60)

    results = []

    for skill_id, skill_cn in SKILL_MAPPING.items():
        try:
            process_skill(skill_id, skill_cn)
            results.append((skill_id, '成功'))
        except Exception as e:
            print(f"  错误: {e}")
            results.append((skill_id, f'失败: {e}'))

    # 输出总结
    print("\n" + "=" * 60)
    print("处理完成总结")
    print("=" * 60)
    for skill_id, status in results:
        print(f"  {skill_id}: {status}")


if __name__ == '__main__':
    main()
