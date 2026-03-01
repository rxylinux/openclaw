#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Experience Manager - 经验管理器
管理结构化的经验库、案例库，支持提取、检索、摘要生成
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml


@dataclass
class Experience:
    """经验对象"""
    id: str
    type: str  # decision, lesson, preference, tip
    category: str  # investment, development, etc.
    tags: List[str] = field(default_factory=list)
    importance: str = "medium"  # high, medium, low
    created_at: str = ""
    related_experiences: List[str] = field(default_factory=list)
    content: str = ""
    source: str = ""  # memory file path

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """转换为 YAML 格式"""
        data = self.to_dict()
        content = data.pop('content', '')

        yaml_str = "---\n"
        yaml_str += yaml.dump(data, allow_unicode=True, default_flow_style=False)
        yaml_str += "---\n\n"
        yaml_str += content

        return yaml_str

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'Experience':
        """从 YAML 字符串解析"""
        # 分离前置元数据和内容
        parts = yaml_str.split('---')
        if len(parts) < 3:
            # 没有完整的前置元数据，返回空对象
            return cls(id="", type="tip", category="general")

        metadata = yaml.safe_load(parts[1])
        content = '---'.join(parts[2:]).strip()

        return cls(content=content, **metadata)


@dataclass
class Case:
    """案例对象"""
    id: str
    type: str  # success, failure
    category: str
    project: str
    date: str
    outcome: str
    lessons: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """转换为 YAML 格式"""
        data = self.to_dict()
        content = data.pop('content', '')

        yaml_str = "---\n"
        yaml_str += yaml.dump(data, allow_unicode=True, default_flow_style=False)
        yaml_str += "---\n\n"
        yaml_str += content

        return yaml_str

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'Case':
        """从 YAML 字符串解析"""
        parts = yaml_str.split('---')
        if len(parts) < 3:
            return cls(id="", type="success", category="general", project="", date="", outcome="")

        metadata = yaml.safe_load(parts[1])
        content = '---'.join(parts[2:]).strip()

        return cls(content=content, **metadata)


class ExperienceManager:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.experience_dir = self.workspace_path / "experience"
        self.experiences_dir = self.experience_dir / "experiences"
        self.cases_dir = self.experience_dir / "cases"
        self.success_dir = self.cases_dir / "success"
        self.failure_dir = self.cases_dir / "failure"
        self.patterns_dir = self.experience_dir / "patterns"
        self.index_path = self.experience_dir / "index.json"
        self.config_path = self.workspace_path / "config" / "experience-config.json"

        # 创建目录
        self._ensure_directories()

        # 加载索引
        self.index = self._load_index()

    def _ensure_directories(self):
        """确保目录存在"""
        dirs = [
            self.experience_dir,
            self.experiences_dir,
            self.cases_dir,
            self.success_dir,
            self.failure_dir,
            self.patterns_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> Dict:
        """加载索引"""
        if not self.index_path.exists():
            return {
                "experiences": {},
                "cases": {},
                "last_updated": datetime.now().isoformat()
            }

        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self):
        """保存索引"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _generate_id(self, prefix: str = "exp") -> str:
        """生成唯一 ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        count = self.index.get(f"{prefix}_count", 0) + 1
        self.index[f"{prefix}_count"] = count
        return f"{prefix}-{timestamp}-{count:03d}"

    def save_experience(self, experience: Experience) -> str:
        """保存经验"""
        if not experience.id:
            experience.id = self._generate_id("exp")

        if not experience.created_at:
            experience.created_at = datetime.now().isoformat()

        # 确定文件路径
        type_dir = self.experiences_dir / f"{experience.type}s"
        type_dir.mkdir(exist_ok=True)

        file_path = type_dir / f"{experience.id}.md"

        # 保存 YAML 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(experience.to_yaml())

        # 更新索引
        self.index["experiences"][experience.id] = {
            "type": experience.type,
            "category": experience.category,
            "tags": experience.tags,
            "importance": experience.importance,
            "created_at": experience.created_at,
            "file_path": str(file_path.relative_to(self.workspace_path)),
            "source": experience.source
        }

        self._save_index()
        return experience.id

    def save_case(self, case: Case) -> str:
        """保存案例"""
        if not case.id:
            case.id = self._generate_id("case")

        if not case.date:
            case.date = datetime.now().strftime("%Y-%m-%d")

        # 确定文件路径
        case_dir = self.success_dir if case.type == "success" else self.failure_dir
        file_path = case_dir / f"{case.id}.md"

        # 保存 YAML 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(case.to_yaml())

        # 更新索引
        self.index["cases"][case.id] = {
            "type": case.type,
            "category": case.category,
            "project": case.project,
            "date": case.date,
            "outcome": case.outcome,
            "file_path": str(file_path.relative_to(self.workspace_path)),
            "lessons_count": len(case.lessons)
        }

        self._save_index()
        return case.id

    def extract_from_memory(self, memory_file: str) -> List[Experience]:
        """从 memory 文件提取经验"""
        memory_path = Path(memory_file)
        if not memory_path.is_absolute():
            memory_path = self.workspace_path / memory_path

        if not memory_path.exists():
            return []

        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()

        experiences = []
        sections = re.split(r'\n##+\s+', content)

        for section in sections:
            if not section.strip():
                continue

            # 检测经验标记
            is_experience = (
                '💡' in section or
                '📝' in section or
                '关键决策' in section or
                '学习要点' in section or
                '重要笔记' in section
            )

            if not is_experience:
                continue

            # 分析类型
            exp_type = self._detect_experience_type(section)

            # 分析重要性
            importance = self._detect_importance(section)

            # 提取标签
            tags = self._extract_tags(section)

            # 创建经验对象
            exp = Experience(
                id="",
                type=exp_type,
                category=self._detect_category(section),
                tags=tags,
                importance=importance,
                created_at=datetime.now().isoformat(),
                content=section.strip(),
                source=str(memory_path.relative_to(self.workspace_path))
            )

            experiences.append(exp)

        return experiences

    def _detect_experience_type(self, content: str) -> str:
        """检测经验类型"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ['决策', '决定', '选择']):
            return "decision"
        elif any(kw in content_lower for kw in ['教训', '错误', '失败', '注意']):
            return "lesson"
        elif any(kw in content_lower for kw in ['偏好', '习惯', '喜欢']):
            return "preference"
        else:
            return "tip"

    def _detect_importance(self, content: str) -> str:
        """检测重要性"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ['必须', '关键', '重要', '核心', '最高优先级']):
            return "high"
        elif any(kw in content_lower for kw in ['建议', '推荐', '可以']):
            return "medium"
        else:
            return "low"

    def _detect_category(self, content: str) -> str:
        """检测类别"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ['股票', '投资', '财报', '估值', '风险']):
            return "investment"
        elif any(kw in content_lower for kw in ['代码', '开发', '脚本', '函数']):
            return "development"
        elif any(kw in content_lower for kw in ['系统', '服务', '部署']):
            return "system"
        else:
            return "general"

    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []

        # 提取 # 标签
        hashtag_matches = re.findall(r'#([^\s#]+)', content)
        tags.extend(hashtag_matches)

        # 提取关键词（从常见主题）
        keywords = [
            '股票', '投资', '代码', '开发', '系统', '安全',
            '决策', '教训', '偏好', '技巧',
            '止损', '仓位', '基本面', '技术',
            '测试', '部署', '文档'
        ]

        for kw in keywords:
            if kw in content and kw not in tags:
                tags.append(kw)

        return tags

    def find_experiences(self, **filters) -> List[Experience]:
        """查找经验"""
        results = []

        for exp_id, exp_meta in self.index["experiences"].items():
            # 应用过滤条件
            match = True

            if 'type' in filters and filters['type'] != exp_meta['type']:
                match = False

            if 'category' in filters and filters['category'] != exp_meta['category']:
                match = False

            if 'importance' in filters and filters['importance'] != exp_meta['importance']:
                match = False

            if 'tags' in filters:
                filter_tags = set(filters['tags'])
                exp_tags = set(exp_meta.get('tags', []))
                if not filter_tags.issubset(exp_tags):
                    match = False

            if 'days' in filters:
                exp_date = datetime.fromisoformat(exp_meta['created_at'])
                cutoff_date = datetime.now() - timedelta(days=filters['days'])
                if exp_date < cutoff_date:
                    match = False

            if match:
                # 加载完整经验
                exp_path = self.workspace_path / exp_meta['file_path']
                if exp_path.exists():
                    with open(exp_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    exp = Experience.from_yaml(content)
                    results.append(exp)

        return results

    def find_cases(self, **filters) -> List[Case]:
        """查找案例"""
        results = []

        for case_id, case_meta in self.index["cases"].items():
            # 应用过滤条件
            match = True

            if 'type' in filters and filters['type'] != case_meta['type']:
                match = False

            if 'category' in filters and filters['category'] != case_meta['category']:
                match = False

            if match:
                # 加载完整案例
                case_path = self.workspace_path / case_meta['file_path']
                if case_path.exists():
                    with open(case_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    case = Case.from_yaml(content)
                    results.append(case)

        return results

    def generate_summary(self, days: int = 7) -> str:
        """生成经验摘要"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # 获取新经验
        new_experiences = []
        for exp_id, exp_meta in self.index["experiences"].items():
            exp_date = datetime.fromisoformat(exp_meta['created_at'])
            if exp_date >= cutoff_date:
                new_experiences.append(exp_meta)

        # 获取新案例
        new_cases = []
        for case_id, case_meta in self.index["cases"].items():
            case_date = datetime.strptime(case_meta['date'], "%Y-%m-%d")
            if case_date >= cutoff_date:
                new_cases.append(case_meta)

        # 生成摘要
        summary = f"# 📊 经验周报 - {datetime.now().strftime('%Y年第%W周')}\n\n"

        # 按类型分组
        exp_by_type = {}
        for exp in new_experiences:
            exp_type = exp['type']
            if exp_type not in exp_by_type:
                exp_by_type[exp_type] = []
            exp_by_type[exp_type].append(exp)

        summary += "## 🆕 本周新经验\n\n"
        for exp_type, exps in exp_by_type.items():
            type_name = {
                'decision': '决策类',
                'lesson': '教训类',
                'preference': '偏好类',
                'tip': '技巧类'
            }.get(exp_type, exp_type)

            summary += f"### {type_name} ({len(exps)} 条)\n\n"
            for exp in exps[:5]:  # 最多显示 5 条
                summary += f"- **{exp.get('category', 'general')}**: {exp.get('tags', [])}\n"
            summary += "\n"

        # 案例统计
        success_cases = [c for c in new_cases if c['type'] == 'success']
        failure_cases = [c for c in new_cases if c['type'] == 'failure']

        summary += "## 📈 案例统计\n\n"
        summary += f"- 成功案例: {len(success_cases)} 个\n"
        summary += f"- 失败案例: {len(failure_cases)} 个\n\n"

        if success_cases:
            summary += "### 成功案例\n\n"
            for case in success_cases[:3]:
                summary += f"- **{case.get('project', 'Unknown')}**: {case.get('outcome', 'completed')}\n"
            summary += "\n"

        if failure_cases:
            summary += "### 失败案例\n\n"
            for case in failure_cases[:3]:
                summary += f"- **{case.get('project', 'Unknown')}**: {case.get('outcome', 'failed')}\n"
            summary += "\n"

        summary += "---\n\n"
        summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return summary

    def get_stats(self) -> Dict:
        """获取统计信息"""
        exp_stats = {}
        for exp_meta in self.index["experiences"].values():
            exp_type = exp_meta['type']
            if exp_type not in exp_stats:
                exp_stats[exp_type] = 0
            exp_stats[exp_type] += 1

        case_stats = {
            'success': 0,
            'failure': 0
        }
        for case_meta in self.index["cases"].values():
            case_type = case_meta['type']
            if case_type in case_stats:
                case_stats[case_type] += 1

        return {
            "total_experiences": len(self.index["experiences"]),
            "experience_by_type": exp_stats,
            "total_cases": len(self.index["cases"]),
            "cases_by_type": case_stats,
            "last_updated": self.index.get("last_updated", "")
        }

    def reindex_cases(self):
        """重新索引所有案例文件"""
        # 清空案例索引
        self.index["cases"] = {}

        # 扫描成功案例
        for case_file in self.success_dir.glob("*.md"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                case = Case.from_yaml(content)
                if case.id:
                    self.index["cases"][case.id] = {
                        "type": case.type,
                        "category": case.category,
                        "project": case.project,
                        "date": case.date,
                        "outcome": case.outcome,
                        "file_path": str(case_file.relative_to(self.workspace_path)),
                        "lessons_count": len(case.lessons)
                    }
            except Exception as e:
                print(f"错误: 无法索引 {case_file}: {e}")

        # 扫描失败案例
        for case_file in self.failure_dir.glob("*.md"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                case = Case.from_yaml(content)
                if case.id:
                    self.index["cases"][case.id] = {
                        "type": case.type,
                        "category": case.category,
                        "project": case.project,
                        "date": case.date,
                        "outcome": case.outcome,
                        "file_path": str(case_file.relative_to(self.workspace_path)),
                        "lessons_count": len(case.lessons)
                    }
            except Exception as e:
                print(f"错误: 无法索引 {case_file}: {e}")

        self._save_index()
        print(f"重新索引完成: {len(self.index['cases'])} 个案例")


def main():
    """命令行接口"""
    em = ExperienceManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python experience-manager.py extract <memory_file>  # 提取经验")
        print("  python experience-manager.py find [filters]          # 查找经验")
        print("  python experience-manager.py cases [filters]           # 查找案例")
        print("  python experience-manager.py summary [days]           # 生成摘要")
        print("  python experience-manager.py stats                   # 统计信息")
        print("  python experience-manager.py reindex                 # 重新索引案例")
        sys.exit(1)

    command = sys.argv[1]

    if command == "extract":
        if len(sys.argv) < 3:
            print("错误: 需要提供 memory 文件路径")
            sys.exit(1)
        memory_file = sys.argv[2]
        experiences = em.extract_from_memory(memory_file)
        print(f"从 {memory_file} 提取到 {len(experiences)} 条经验")

        for exp in experiences:
            exp_id = em.save_experience(exp)
            print(f"  保存: {exp_id} ({exp.type} - {exp.importance})")

    elif command == "find":
        filters = {}
        for arg in sys.argv[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                if key == 'tags':
                    value = value.split(',')
                filters[key] = value

        results = em.find_experiences(**filters)
        print(f"找到 {len(results)} 条经验:\n")
        for exp in results:
            print(f"  [{exp.id}] {exp.type} - {exp.category}")
            print(f"    标签: {', '.join(exp.tags)}")
            print(f"    重要性: {exp.importance}")
            print()

    elif command == "cases":
        filters = {}
        for arg in sys.argv[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                filters[key] = value

        results = em.find_cases(**filters)
        print(f"找到 {len(results)} 个案例:\n")
        for case in results:
            print(f"  [{case.id}] {case.type} - {case.project}")
            print(f"    结果: {case.outcome}")
            print()

    elif command == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        summary = em.generate_summary(days)
        print(summary)

    elif command == "stats":
        stats = em.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif command == "reindex":
        em.reindex_cases()

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
