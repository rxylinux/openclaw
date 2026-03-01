#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolution Manager - 演化管理器
管理 A/B 测试、反馈收集、参数优化和演化报告
"""

import json
import os
import random
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


@dataclass
class ABTest:
    """A/B 测试对象"""
    id: str
    name: str
    type: str  # loading_strategy, scenario_detection, etc.
    status: str  # planning, active, paused, completed, cancelled
    created_at: str
    ended_at: Optional[str] = None
    duration_days: int = 7

    variant_a: Dict[str, Any] = field(default_factory=dict)
    variant_b: Dict[str, Any] = field(default_factory=dict)
    hypothesis: str = ""

    metrics: Dict[str, Any] = field(default_factory=dict)
    conclusion: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """转换为 YAML 格式"""
        data = self.to_dict()
        content = data.pop('content', '')

        # 构建 YAML
        yaml_str = "---\n"
        yaml_str += f"id: {data['id']}\n"
        yaml_str += f"type: {data['type']}\n"
        yaml_str += f"name: {data['name']}\n"
        yaml_str += f"status: {data['status']}\n"
        yaml_str += f"created_at: {data['created_at']}\n"
        yaml_str += f"ended_at: {data.get('ended_at', 'null')}\n"
        yaml_str += f"duration_days: {data['duration_days']}\n"
        yaml_str += "\nvariant_a:\n"
        for key, value in data['variant_a'].items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\nvariant_b:\n"
        for key, value in data['variant_b'].items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\n"
        yaml_str += "---\n\n"
        yaml_str += self.hypothesis

        return yaml_str

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'ABTest':
        """从 YAML 解析（简化版）"""
        parts = yaml_str.split('---')

        # 解析前置元数据
        metadata = {
            'id': '',
            'name': '',
            'type': 'unknown',
            'status': 'planning',
            'created_at': '',
            'duration_days': 7,
            'variant_a': {},
            'variant_b': {},
            'metrics': {},
            'conclusion': None
        }

        if len(parts) >= 2:
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # 转换类型
                    if key in ['duration_days']:
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    elif key == 'ended_at' and value.lower() == 'null':
                        value = None
                    elif key == 'metrics':
                        value = {}
                    elif key == 'conclusion' and value.lower() == 'null':
                        value = None

                    metadata[key] = value

        hypothesis = parts[2].strip() if len(parts) > 2 else ""

        return cls(
            hypothesis=hypothesis,
            **metadata
        )


@dataclass
class Feedback:
    """反馈对象"""
    id: str
    type: str  # explicit, implicit, performance
    session_id: str
    message_id: str = ""
    variant_id: Optional[str] = None

    # 显式反馈
    rating: Optional[int] = None  # 1-5
    reaction: Optional[str] = None  # 👍, 👎, ❤️, etc.
    text: Optional[str] = None

    # 隐式反馈
    task_completed: Optional[bool] = None
    retry_count: Optional[int] = None
    tool_usage: Optional[Dict[str, int]] = None

    # 性能指标
    latency_ms: Optional[int] = None
    token_consumption: Optional[int] = None
    response_time_ms: Optional[int] = None

    created_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class EvolutionManager:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.evolution_dir = self.workspace_path / "evolution"
        self.tests_dir = self.evolution_dir / "tests"
        self.active_tests_dir = self.tests_dir / "active"
        self.completed_tests_dir = self.tests_dir / "completed"
        self.feedbacks_dir = self.evolution_dir / "feedbacks"
        self.optimizations_dir = self.evolution_dir / "optimizations"
        self.reports_dir = self.evolution_dir / "reports"
        self.metrics_dir = self.evolution_dir / "metrics"
        self.config_path = self.workspace_path / "config" / "evolution-config.json"
        self.index_path = self.evolution_dir / "index.json"

        # 创建目录
        self._ensure_directories()

        # 加载配置
        self.config = self._load_config()

        # 加载索引
        self.index = self._load_index()

    def _ensure_directories(self):
        """确保目录存在"""
        dirs = [
            self.evolution_dir,
            self.tests_dir,
            self.active_tests_dir,
            self.completed_tests_dir,
            self.feedbacks_dir,
            self.optimizations_dir,
            self.reports_dir,
            self.metrics_dir,
            self.reports_dir / "weekly",
            self.reports_dir / "daily"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """加载配置"""
        if not self.config_path.exists():
            return self._default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "ab_testing": {
                "enabled": True,
                "default_duration_days": 7,
                "auto_assign": True,
                "random_seed": 42
            },
            "feedback": {
                "collect_implicit": True,
                "collect_performance": True,
                "retention_days": 30
            },
            "optimization": {
                "enabled": True,
                "auto_optimize": True,
                "optimization_interval_days": 7,
                "min_feedbacks": 10
            }
        }

    def _load_index(self) -> Dict:
        """加载索引"""
        if not self.index_path.exists():
            return {
                "tests": {},
                "feedbacks": {},
                "optimizations": [],
                "last_updated": datetime.now().isoformat()
            }

        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self):
        """保存索引"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _generate_id(self, prefix: str = "test") -> str:
        """生成唯一 ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        count = self.index.get(f"{prefix}_count", 0) + 1
        self.index[f"{prefix}_count"] = count
        return f"{prefix}-{timestamp}-{count:03d}"

    # A/B 测试管理

    def create_test(self, name: str, test_type: str, hypothesis: str,
                   variant_a: Dict, variant_b: Dict, duration_days: int = 7) -> str:
        """创建 A/B 测试"""
        test = ABTest(
            id=self._generate_id("test"),
            name=name,
            type=test_type,
            status="active",
            created_at=datetime.now().isoformat(),
            duration_days=duration_days,
            variant_a=variant_a,
            variant_b=variant_b,
            hypothesis=hypothesis
        )

        # 保存测试
        test_file = self.active_tests_dir / f"{test.id}.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test.to_yaml())

        # 更新索引
        self.index["tests"][test.id] = {
            "name": test.name,
            "type": test.type,
            "status": test.status,
            "created_at": test.created_at,
            "file_path": str(test_file.relative_to(self.workspace_path))
        }

        self._save_index()
        return test.id

    def assign_variant(self, test_id: str, session_id: str) -> Optional[str]:
        """为会话分配变体（A 或 B）"""
        if not self.config["ab_testing"].get("enabled", True):
            return None

        if test_id not in self.index["tests"]:
            return None

        # 使用会话 ID 生成哈希，确保一致性
        hash_input = f"{test_id}_{session_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        variant = "A" if hash_value % 2 == 0 else "B"

        return variant

    def record_test_metric(self, test_id: str, variant: str, metric_name: str, value: Any):
        """记录测试指标"""
        test_id_key = f"{test_id}_{variant}"

        if "metrics" not in self.index["tests"][test_id]:
            self.index["tests"][test_id]["metrics"] = {}

        if test_id_key not in self.index["tests"][test_id]["metrics"]:
            self.index["tests"][test_id]["metrics"][test_id_key] = {}

        self.index["tests"][test_id]["metrics"][test_id_key][metric_name] = value
        self._save_index()

    def conclude_test(self, test_id: str, conclusion: str):
        """结束测试并得出结论"""
        if test_id not in self.index["tests"]:
            return

        # 移动到完成目录
        active_file = self.active_tests_dir / f"{test_id}.md"
        if active_file.exists():
            completed_file = self.completed_tests_dir / f"{test_id}.md"
            active_file.rename(completed_file)

        # 更新索引
        self.index["tests"][test_id]["status"] = "completed"
        self.index["tests"][test_id]["ended_at"] = datetime.now().isoformat()
        self.index["tests"][test_id]["conclusion"] = conclusion

        self._save_index()

    # 反馈收集

    def collect_explicit_feedback(self, session_id: str, message_id: str,
                                rating: Optional[int] = None,
                                reaction: Optional[str] = None,
                                text: Optional[str] = None):
        """收集显式反馈"""
        feedback = Feedback(
            id=self._generate_id("feedback"),
            type="explicit",
            session_id=session_id,
            message_id=message_id,
            rating=rating,
            reaction=reaction,
            text=text,
            created_at=datetime.now().isoformat()
        )

        self._save_feedback(feedback)

    def collect_implicit_feedback(self, session_id: str, task_completed: bool,
                                retry_count: int = 0,
                                tool_usage: Optional[Dict[str, int]] = None):
        """收集隐式反馈"""
        feedback = Feedback(
            id=self._generate_id("feedback"),
            type="implicit",
            session_id=session_id,
            task_completed=task_completed,
            retry_count=retry_count,
            tool_usage=tool_usage,
            created_at=datetime.now().isoformat()
        )

        self._save_feedback(feedback)

    def collect_performance_feedback(self, session_id: str, latency_ms: int,
                                  token_consumption: int, response_time_ms: int):
        """收集性能反馈"""
        feedback = Feedback(
            id=self._generate_id("feedback"),
            type="performance",
            session_id=session_id,
            latency_ms=latency_ms,
            token_consumption=token_consumption,
            response_time_ms=response_time_ms,
            created_at=datetime.now().isoformat()
        )

        self._save_feedback(feedback)

    def _save_feedback(self, feedback: Feedback):
        """保存反馈"""
        # 保存到文件
        feedback_file = self.feedbacks_dir / f"{feedback.type}.json"
        feedbacks = []

        if feedback_file.exists():
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)

        feedbacks.append(feedback.to_dict())

        # 清理旧反馈
        retention_days = self.config["feedback"].get("retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        feedbacks = [
            f for f in feedbacks
            if datetime.fromisoformat(f['created_at']) >= cutoff_date
        ]

        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

        # 更新索引
        self.index["feedbacks"][feedback.id] = {
            "type": feedback.type,
            "session_id": feedback.session_id,
            "created_at": feedback.created_at
        }

        self._save_index()

    # 参数优化

    def optimize_parameters(self):
        """基于反馈优化参数"""
        if not self.config["optimization"].get("enabled", True):
            return

        min_feedbacks = self.config["optimization"].get("min_feedbacks", 10)

        # 收集反馈
        all_feedbacks = self._get_recent_feedbacks(min_count=min_feedbacks)

        if len(all_feedbacks) < min_feedbacks:
            print(f"反馈数量不足（{len(all_feedbacks)}/{min_feedbacks}），跳过优化")
            return

        # 计算平均满意度
        explicit_feedbacks = [f for f in all_feedbacks if f['type'] == 'explicit']
        ratings = [f['rating'] for f in explicit_feedbacks if f.get('rating')]

        if not ratings:
            print("没有评分反馈，跳过优化")
            return

        avg_satisfaction = sum(ratings) / len(ratings)
        print(f"当前平均满意度: {avg_satisfaction:.2f}")

        # 优化参数
        params = self.config["parameters"]
        optimizations = []

        # 如果满意度低，增加可选文件
        if avg_satisfaction < 3.5:
            current_max_optional = params["context_manager"]["max_optional_files"]["current"]
            if current_max_optional < params["context_manager"]["max_optional_files"]["max"]:
                params["context_manager"]["max_optional_files"]["current"] += 1
                optimizations.append({
                    "parameter": "max_optional_files",
                    "old_value": current_max_optional,
                    "new_value": current_max_optional + 1,
                    "reason": "满意度低，增加文件加载"
                })

        # 计算平均响应时间
        performance_feedbacks = [f for f in all_feedbacks if f['type'] == 'performance']
        latencies = [f['response_time_ms'] for f in performance_feedbacks if f.get('response_time_ms')]

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"当前平均响应时间: {avg_latency:.0f}ms")

            threshold = self.config["monitoring"].get("response_time_threshold_ms", 5000)

            if avg_latency > threshold:
                # 减少可选文件
                current_max_optional = params["context_manager"]["max_optional_files"]["current"]
                if current_max_optional > params["context_manager"]["max_optional_files"]["min"]:
                    params["context_manager"]["max_optional_files"]["current"] -= 1
                    optimizations.append({
                        "parameter": "max_optional_files",
                        "old_value": current_max_optional,
                        "new_value": current_max_optional - 1,
                        "reason": f"响应时间慢（{avg_latency:.0f}ms），减少文件"
                    })

                # 增加 decay_factor
                current_decay = params["context_manager"]["decay_factor"]["current"]
                new_decay = min(current_decay * 1.05, params["context_manager"]["decay_factor"]["max"])
                if new_decay != current_decay:
                    params["context_manager"]["decay_factor"]["current"] = new_decay
                    optimizations.append({
                        "parameter": "decay_factor",
                        "old_value": current_decay,
                        "new_value": new_decay,
                        "reason": f"响应时间慢，增加衰减系数"
                    })

        # 保存优化
        if optimizations:
            self._save_optimizations(optimizations)
            self._update_config()
            print(f"应用了 {len(optimizations)} 项优化")
        else:
            print("无需优化")

    def _get_recent_feedbacks(self, min_count: int = 10) -> List[Dict]:
        """获取最近的反馈"""
        all_feedbacks = []

        for feedback_file in self.feedbacks_dir.glob("*.json"):
            if not feedback_file.exists():
                continue

            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
                all_feedbacks.extend(feedbacks)

        # 按时间排序
        all_feedbacks.sort(key=lambda x: x['created_at'], reverse=True)

        return all_feedbacks[:min_count * 2]  # 返回足够多的反馈

    def _save_optimizations(self, optimizations: List[Dict]):
        """保存优化记录"""
        history_file = self.optimizations_dir / "history.json"
        history = []

        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

        optimization_entry = {
            "timestamp": datetime.now().isoformat(),
            "optimizations": optimizations
        }

        history.append(optimization_entry)

        # 保留最近 100 条
        history = history[-100:]

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _update_config(self):
        """更新配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    # 报告生成

    def generate_report(self, days: int = 7) -> str:
        """生成演化报告"""
        # 收集数据
        active_tests = self._get_active_tests()
        completed_tests = self._get_completed_tests(days=days)
        feedbacks = self._get_recent_feedbacks(min_count=10)
        # 只保留最近 N 天的反馈
        cutoff_date = datetime.now() - timedelta(days=days)
        feedbacks = [
            f for f in feedbacks
            if datetime.fromisoformat(f['created_at']) >= cutoff_date
        ]
        optimizations = self._get_recent_optimizations(days=days)

        # 生成报告
        report = f"# 📊 演化报告 - {datetime.now().strftime('%Y年第%W周')}\n\n"

        # A/B 测试
        report += "## 🧪 A/B 测试\n\n"

        if active_tests:
            report += f"### 进行中的测试 ({len(active_tests)} 个)\n\n"
            for test_meta in active_tests:
                test_file = self.workspace_path / test_meta['file_path']
                with open(test_file, 'r', encoding='utf-8') as f:
                    test = ABTest.from_yaml(f.read())
                report += f"- **{test.name}** ({test.type})\n"
                report += f"  - 变体 A: {test.variant_a.get('name', '未知')}\n"
                report += f"  - 变体 B: {test.variant_b.get('name', '未知')}\n"
                report += f"  - 假设: {test.hypothesis[:50]}...\n"
            report += "\n"
        else:
            report += "没有进行中的测试\n\n"

        if completed_tests:
            report += f"### 最近完成的测试 ({len(completed_tests)} 个)\n\n"
            for test_meta in completed_tests:
                test_file = self.workspace_path / test_meta['file_path']
                with open(test_file, 'r', encoding='utf-8') as f:
                    test = ABTest.from_yaml(f.read())
                report += f"- **{test.name}** ({test.type})\n"
                if test.conclusion:
                    report += f"  - 结论: {test.conclusion}\n"
            report += "\n"

        # 反馈统计
        report += "## 😊 用户满意度\n\n"

        explicit_feedbacks = [f for f in feedbacks if f['type'] == 'explicit']
        ratings = [f['rating'] for f in explicit_feedbacks if f.get('rating')]

        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            report += f"- 平均评分: {avg_rating:.2f}/5.0 ({len(ratings)} 条评价)\n"
            report += f"- 评分分布:\n"
            for i in range(1, 6):
                count = ratings.count(i)
                report += f"  - {i} 星: {count} 条\n"
        else:
            report += "暂无评分反馈\n"

        report += "\n"

        # 性能指标
        report += "## ⚡ 性能指标\n\n"

        performance_feedbacks = [f for f in feedbacks if f['type'] == 'performance']

        if performance_feedbacks:
            response_times = [f['response_time_ms'] for f in performance_feedbacks if f.get('response_time_ms')]
            token_consumptions = [f['token_consumption'] for f in performance_feedbacks if f.get('token_consumption')]

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                report += f"- 平均响应时间: {avg_response_time:.0f}ms\n"

            if token_consumptions:
                avg_tokens = sum(token_consumptions) / len(token_consumptions)
                report += f"- 平均 Token 消耗: {avg_tokens:.0f}/会话\n"
        else:
            report += "暂无性能数据\n"

        report += "\n"

        # 参数优化
        report += "## 📈 参数优化\n\n"

        if optimizations:
            for opt in optimizations:
                report += f"- **{opt['parameter']}**\n"
                report += f"  - {opt['old_value']} → {opt['new_value']}\n"
                report += f"  - 原因: {opt['reason']}\n"
        else:
            report += "最近无参数优化\n"

        report += "\n"

        # 改进建议
        report += "## 💡 改进建议\n\n"

        if ratings and len(ratings) >= 5:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating >= 4.5:
                report += "- ✅ 用户满意度高，继续当前策略\n"
            elif avg_rating >= 3.5:
                report += "- 🟡 用户满意度中等，考虑微调\n"
            else:
                report += "- 🔴 用户满意度低，需要改进\n"

        report += "\n"

        report += "---\n\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return report

    def _get_active_tests(self) -> List[Dict]:
        """获取活跃的测试"""
        return [
            meta for meta in self.index["tests"].values()
            if meta.get('status') == 'active'
        ]

    def _get_completed_tests(self, days: int = 7) -> List[Dict]:
        """获取最近完成的测试"""
        cutoff_date = datetime.now() - timedelta(days=days)

        return [
            meta for meta in self.index["tests"].values()
            if meta.get('status') == 'completed' and
            datetime.fromisoformat(meta.get('ended_at', '')) >= cutoff_date
        ]

    def _get_recent_optimizations(self, days: int = 7) -> List[Dict]:
        """获取最近的优化"""
        history_file = self.optimizations_dir / "history.json"
        if not history_file.exists():
            return []

        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        cutoff_date = datetime.now() - timedelta(days=days)

        recent = []
        for entry in history:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time >= cutoff_date:
                recent.extend(entry['optimizations'])

        return recent

    def get_stats(self) -> Dict:
        """获取统计信息"""
        test_stats = {
            'active': 0,
            'completed': 0,
            'total': 0
        }

        for test_meta in self.index["tests"].values():
            test_stats['total'] += 1
            status = test_meta.get('status', '')
            if status == 'active':
                test_stats['active'] += 1
            elif status == 'completed':
                test_stats['completed'] += 1

        # 统计反馈
        feedback_count = 0
        for feedback_file in self.feedbacks_dir.glob("*.json"):
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
                    feedback_count += len(feedbacks)

        return {
            "tests": test_stats,
            "feedbacks_count": feedback_count,
            "last_updated": self.index.get("last_updated", "")
        }


def main():
    """命令行接口"""
    em = EvolutionManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution-manager.py create-test <name> <type> <hypothesis>  # 创建测试")
        print("  python evolution-manager.py assign <test_id> <session_id>        # 分配变体")
        print("  python evolution-manager.py record-metric <test_id> <variant> <name> <value>")
        print("  python evolution-manager.py conclude <test_id> <conclusion>     # 结束测试")
        print("  python evolution-manager.py feedback <type> <session_id> [args]  # 收集反馈")
        print("  python evolution-manager.py optimize                               # 优化参数")
        print("  python evolution-manager.py report [days]                           # 生成报告")
        print("  python evolution-manager.py stats                                  # 统计信息")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-test":
        if len(sys.argv) < 5:
            print("错误: 需要提供名称、类型和假设")
            sys.exit(1)

        name = sys.argv[2]
        test_type = sys.argv[3]
        hypothesis = sys.argv[4]

        # 简单的默认变体
        variant_a = {"name": "变体 A", "description": "实验组"}
        variant_b = {"name": "变体 B", "description": "对照组"}

        test_id = em.create_test(name, test_type, hypothesis, variant_a, variant_b)
        print(f"创建测试: {test_id}")

    elif command == "assign":
        if len(sys.argv) < 4:
            print("错误: 需要提供测试 ID 和会话 ID")
            sys.exit(1)

        test_id = sys.argv[2]
        session_id = sys.argv[3]
        variant = em.assign_variant(test_id, session_id)
        print(f"分配变体: {variant}")

    elif command == "optimize":
        em.optimize_parameters()

    elif command == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        report = em.generate_report(days)
        print(report)

    elif command == "stats":
        stats = em.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
