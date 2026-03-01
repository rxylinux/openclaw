#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动上下文加载器
在会话开始时自动检测场景并加载相关文件
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


class ContextManager:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / "config" / "context-config.json"
        self.usage_path = self.workspace_path / "memory" / "context-usage.json"
        self.config = self._load_config()
        self.usage = self._load_usage()

    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_usage(self) -> dict:
        """加载使用统计文件"""
        if not self.usage_path.exists():
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
        """根据用户消息检测场景"""
        message_lower = user_message.lower()

        # 投资分析关键词
        investment_keywords = ['股票', '分析', '财报', '投资', '仓位', '买入', '卖出',
                            '估值', '风险', '分红', '股息', '持仓', '板块', '行业',
                            'stock', 'analysis', 'earnings', 'investment', 'portfolio',
                            'valuation', 'dividend', '特斯拉', '特斯拉']

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

        # 心跳检查有最高优先级
        if any(kw in message_lower for kw in heartbeat_keywords):
            return "health_check"

        # 统计关键词匹配数
        scores = {
            "investment_analysis": sum(1 for kw in investment_keywords if kw in message_lower),
            "code_development": sum(1 for kw in code_keywords if kw in message_lower),
            "news_research": sum(1 for kw in news_keywords if kw in message_lower),
            "health_check": sum(1 for kw in health_keywords if kw in message_lower),
        }

        # 找到得分最高的场景
        max_score = max(scores.values())
        if max_score == 0:
            return "daily_conversation"

        return max(scores, key=scores.get)

    def get_files_for_scenario(self, scenario: str) -> tuple:
        """获取场景需要的文件"""
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

        # 处理可选文件
        optional_file_paths = scenario_config.get("optional_files", [])
        optional_file_stats = []

        for file_path in optional_file_paths:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                continue

            stat = self.usage["file_stats"].get(file_path, {})
            frequency_score = stat.get("frequency_score", 0.0)

            optional_file_stats.append({
                "path": str(full_path),
                "score": frequency_score
            })

        # 按频率排序
        optional_file_stats.sort(key=lambda x: x["score"], reverse=True)

        # 压缩机制
        compression_config = self.config.get("compression", {})
        if compression_config.get("enabled", True):
            max_optional = 3
            optional_files = [f["path"] for f in optional_file_stats[:max_optional]]
        else:
            optional_files = [f["path"] for f in optional_file_stats]

        return required_files, optional_files

    def get_skills_for_scenario(self, scenario: str) -> list:
        """获取场景相关的技能"""
        if scenario not in self.config["scenarios"]:
            return []

        return self.config["scenarios"][scenario].get("skills", [])

    def record_file_usage(self, file_path: str, scenario: str):
        """记录文件使用情况"""
        try:
            rel_path = str(Path(file_path).relative_to(self.workspace_path))
        except ValueError:
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

        # 更新频率分数
        decay_factor = self.config["frequency_tracking"].get("decay_factor", 0.95)
        boost_on_use = self.config["frequency_tracking"].get("boost_on_use", 1.0)
        stat["frequency_score"] = stat["frequency_score"] * decay_factor + boost_on_use

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


def load_context_for_message(user_message: str) -> dict:
    """根据用户消息加载上下文"""
    cm = ContextManager()

    # 1. 检测场景
    scenario = cm.detect_scenario(user_message)

    # 2. 获取文件
    required_files, optional_files = cm.get_files_for_scenario(scenario)

    # 3. 获取技能
    skills = cm.get_skills_for_scenario(scenario)

    # 4. 记录使用
    for file_path in required_files + optional_files:
        cm.record_file_usage(file_path, scenario)

    # 5. 计算总大小
    total_size = sum(
        os.path.getsize(f) for f in required_files + optional_files if os.path.exists(f)
    )

    return {
        "scenario": scenario,
        "required_files": required_files,
        "optional_files": optional_files,
        "skills": skills,
        "total_size_kb": round(total_size / 1024, 2),
        "description": cm.config["scenarios"].get(scenario, {}).get("description", "")
    }


def print_load_instructions(context: dict):
    """打印加载指令"""
    print(f"\n=== 上下文自动加载 ===")
    print(f"检测到场景: {context['scenario']}")
    print(f"场景描述: {context['description']}")
    print(f"总大小: {context['total_size_kb']} KB\n")

    if context["required_files"]:
        print("必需文件（必须读取）:")
        for f in context["required_files"]:
            print(f"  - {f}")

    if context["optional_files"]:
        print(f"\n可选文件（按频率排序）:")
        for f in context["optional_files"]:
            print(f"  - {f}")

    if context["skills"]:
        print(f"\n推荐技能:")
        for skill in context["skills"]:
            print(f"  - {skill}")

    print("=" * 50 + "\n")


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python auto-context-loader.py <message>")
        sys.exit(1)

    message = " ".join(sys.argv[1:])

    # 加载上下文
    context = load_context_for_message(message)

    # 打印指令
    print_load_instructions(context)


if __name__ == "__main__":
    main()
