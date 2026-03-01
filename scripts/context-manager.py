#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager for OpenClaw
智能上下文管理器：按场景动态加载文件、统计使用频率、压缩上下文
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class ContextManager:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / "config" / "context-config.json"
        self.usage_path = self.workspace_path / "memory" / "context-usage.json"
        self.config = self._load_config()
        self.usage = self._load_usage()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_usage(self) -> Dict:
        """加载使用统计文件"""
        if not self.usage_path.exists():
            # 创建默认统计
            return {
                "file_stats": {},
                "scenario_stats": {},
                "last_updated": datetime.utcnow().isoformat()
            }
        with open(self.usage_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_usage(self):
        """保存使用统计"""
        self.usage["last_updated"] = datetime.utcnow().isoformat()
        with open(self.usage_path, 'w', encoding='utf-8') as f:
            json.dump(self.usage, f, ensure_ascii=False, indent=2)

    def detect_scenario(self, user_message: str) -> str:
        """
        根据用户消息检测场景
        简单版：基于关键词匹配
        未来可以升级为语义分析
        """
        message_lower = user_message.lower()

        # 投资分析关键词
        investment_keywords = ['股票', '分析', '财报', '投资', '仓位', '买入', '卖出',
                            '估值', '风险', '分红', '股息', '持仓', '板块', '行业',
                            'stock', 'analysis', 'earnings', 'investment', 'portfolio',
                            'valuation', 'dividend']

        # 代码开发关键词
        code_keywords = ['代码', '脚本', '函数', '开发', '调试', '测试', '部署',
                        'skill', 'script', 'function', 'develop', 'debug', 'test']

        # 新闻研究关键词
        news_keywords = ['新闻', '搜索', '查找', '资讯', '最新', '报道',
                        'news', 'search', 'find', 'latest']

        # 健康检查关键词
        health_keywords = ['状态', '检查', '监控', '健康', '系统', '运行',
                          'status', 'check', 'monitor', 'health', 'system']

        # 心跳检查
        heartbeat_keywords = ['heartbeat', '心跳', 'read heartbeat']

        # 统计关键词匹配数
        scores = {
            "investment_analysis": sum(1 for kw in investment_keywords if kw in message_lower),
            "code_development": sum(1 for kw in code_keywords if kw in message_lower),
            "news_research": sum(1 for kw in news_keywords if kw in message_lower),
            "health_check": sum(1 for kw in health_keywords if kw in message_lower),
        }

        # 心跳检查有最高优先级
        if any(kw in message_lower for kw in heartbeat_keywords):
            return "health_check"

        # 找到得分最高的场景
        max_score = max(scores.values())
        if max_score == 0:
            return "daily_conversation"  # 默认场景

        return max(scores, key=scores.get)

    def get_files_for_scenario(self, scenario: str) -> Tuple[List[str], List[str]]:
        """
        获取场景需要的文件
        返回：(必需文件列表, 可选文件列表)
        """
        if scenario not in self.config["scenarios"]:
            return [], []

        scenario_config = self.config["scenarios"][scenario]

        required_files = []
        optional_files = []

        # 处理必需文件
        for file_path in scenario_config.get("required_files", []):
            full_path = self.workspace_path / file_path
            if full_path.exists():
                required_files.append(str(full_path))

        # 处理可选文件（基于使用频率排序）
        optional_file_paths = scenario_config.get("optional_files", [])
        optional_file_stats = []

        for file_path in optional_file_paths:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                continue

            # 获取文件使用频率
            stat = self.usage["file_stats"].get(file_path, {})
            frequency_score = stat.get("frequency_score", 0.0)

            optional_file_stats.append({
                "path": str(full_path),
                "score": frequency_score
            })

        # 按频率排序
        optional_file_stats.sort(key=lambda x: x["score"], reverse=True)

        # 压缩机制：只保留高分文件
        compression_config = self.config.get("compression", {})
        if compression_config.get("enabled", True):
            max_optional = 3  # 最多3个可选文件
            optional_files = [f["path"] for f in optional_file_stats[:max_optional]]
        else:
            optional_files = [f["path"] for f in optional_file_stats]

        return required_files, optional_files

    def get_skills_for_scenario(self, scenario: str) -> List[str]:
        """获取场景相关的技能"""
        if scenario not in self.config["scenarios"]:
            return []

        return self.config["scenarios"][scenario].get("skills", [])

    def record_file_usage(self, file_path: str, scenario: str):
        """记录文件使用情况"""
        # 转换为相对路径
        try:
            rel_path = str(Path(file_path).relative_to(self.workspace_path))
        except ValueError:
            # 不在工作空间内，不记录
            return

        # 更新文件统计
        if rel_path not in self.usage["file_stats"]:
            self.usage["file_stats"][rel_path] = {
                "use_count": 0,
                "last_used": None,
                "frequency_score": 0.0,
                "scenarios": []
            }

        stat = self.usage["file_stats"][rel_path]
        stat["use_count"] += 1
        stat["last_used"] = datetime.utcnow().isoformat()

        # 更新频率分数（带衰减）
        decay_factor = self.config["frequency_tracking"].get("decay_factor", 0.95)
        boost_on_use = self.config["frequency_tracking"].get("boost_on_use", 1.0)
        stat["frequency_score"] = stat["frequency_score"] * decay_factor + boost_on_use

        # 更新场景列表
        if scenario not in stat["scenarios"]:
            stat["scenarios"].append(scenario)

        # 更新场景统计
        if scenario not in self.usage["scenario_stats"]:
            self.usage["scenario_stats"][scenario] = {
                "use_count": 0,
                "last_used": None
            }

        scenario_stat = self.usage["scenario_stats"][scenario]
        scenario_stat["use_count"] += 1
        scenario_stat["last_used"] = datetime.utcnow().isoformat()

        self._save_usage()

    def get_context_summary(self, scenario: str) -> Dict:
        """获取场景的上下文摘要"""
        required_files, optional_files = self.get_files_for_scenario(scenario)
        skills = self.get_skills_for_scenario(scenario)

        total_size = 0
        file_info = []

        for file_path in required_files + optional_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                file_info.append({
                    "path": file_path,
                    "size_bytes": size,
                    "size_kb": round(size / 1024, 2)
                })

        return {
            "scenario": scenario,
            "description": self.config["scenarios"].get(scenario, {}).get("description", ""),
            "required_files_count": len(required_files),
            "optional_files_count": len(optional_files),
            "skills_count": len(skills),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "files": file_info,
            "skills": skills
        }

    def compress_memory_files(self, max_days: int = 7) -> List[str]:
        """
        压缩历史 memory 文件
        返回：被压缩的文件列表
        """
        memory_dir = self.workspace_path / "memory"
        if not memory_dir.exists():
            return []

        # 找到所有 .md 文件
        memory_files = sorted(memory_dir.glob("*.md"))
        compressed_files = []

        # 跳过最近 N 天的文件
        cutoff_date = datetime.utcnow() - timedelta(days=max_days)
        compressed_dir = memory_dir / "archived"

        for memory_file in memory_files:
            # 检查文件日期
            try:
                date_str = memory_file.stem  # 文件名格式: YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            if file_date >= cutoff_date:
                continue

            # 创建归档目录
            compressed_dir.mkdir(exist_ok=True)

            # 移动文件到归档目录
            archived_path = compressed_dir / memory_file.name
            memory_file.rename(archived_path)
            compressed_files.append(str(archived_path))

        return compressed_files

    def get_usage_report(self) -> Dict:
        """获取使用统计报告"""
        total_file_uses = sum(
            stat["use_count"] for stat in self.usage["file_stats"].values()
        )

        top_files = sorted(
            self.usage["file_stats"].items(),
            key=lambda x: x[1]["frequency_score"],
            reverse=True
        )[:10]

        top_scenarios = sorted(
            self.usage["scenario_stats"].items(),
            key=lambda x: x[1]["use_count"],
            reverse=True
        )

        return {
            "total_file_uses": total_file_uses,
            "unique_files": len(self.usage["file_stats"]),
            "top_files": [
                {
                    "path": path,
                    "use_count": stat["use_count"],
                    "frequency_score": round(stat["frequency_score"], 2),
                    "last_used": stat["last_used"]
                }
                for path, stat in top_files
            ],
            "scenario_distribution": [
                {
                    "scenario": scenario,
                    "use_count": stat["use_count"],
                    "last_used": stat["last_used"]
                }
                for scenario, stat in top_scenarios
            ],
            "last_updated": self.usage["last_updated"]
        }


def main():
    """命令行接口"""
    import sys

    cm = ContextManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python context-manager.py detect <message>     # 检测场景")
        print("  python context-manager.py files <scenario>      # 获取文件")
        print("  python context-manager.py summary <scenario>    # 获取摘要")
        print("  python context-manager.py record <file> <scenario>  # 记录使用")
        print("  python context-manager.py compress [days]       # 压缩历史文件")
        print("  python context-manager.py report               # 生成报告")
        sys.exit(1)

    command = sys.argv[1]

    if command == "detect":
        if len(sys.argv) < 3:
            print("错误: 需要提供消息内容")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        scenario = cm.detect_scenario(message)
        print(f"检测到场景: {scenario}")

    elif command == "files":
        if len(sys.argv) < 3:
            print("错误: 需要提供场景名称")
            sys.exit(1)
        scenario = sys.argv[2]
        required, optional = cm.get_files_for_scenario(scenario)
        print(f"必需文件 ({len(required)}):")
        for f in required:
            print(f"  - {f}")
        print(f"\n可选文件 ({len(optional)}):")
        for f in optional:
            print(f"  - {f}")

    elif command == "summary":
        if len(sys.argv) < 3:
            print("错误: 需要提供场景名称")
            sys.exit(1)
        scenario = sys.argv[2]
        summary = cm.get_context_summary(scenario)
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    elif command == "record":
        if len(sys.argv) < 4:
            print("错误: 需要提供文件路径和场景名称")
            sys.exit(1)
        file_path = sys.argv[2]
        scenario = sys.argv[3]
        cm.record_file_usage(file_path, scenario)
        print(f"已记录: {file_path} -> {scenario}")

    elif command == "compress":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        compressed = cm.compress_memory_files(days)
        print(f"已压缩 {len(compressed)} 个文件:")
        for f in compressed:
            print(f"  - {f}")

    elif command == "report":
        report = cm.get_usage_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
