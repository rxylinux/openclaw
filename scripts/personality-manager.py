#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personality Manager - 个性化管理器
管理 Agent 性格定义、环境适配、参数调整和偏好学习
"""

import json
import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Personality:
    """Agent 性格对象"""
    id: str
    name: str
    version: str
    created_at: str
    updated_at: str

    # 沟通风格
    communication: Dict[str, Any] = field(default_factory=dict)

    # 决策风格
    decision: Dict[str, Any] = field(default_factory=dict)

    # 工作风格
    work: Dict[str, Any] = field(default_factory=dict)

    # 适配设置
    adaptation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """转换为 YAML 格式"""
        data = self.to_dict()
        content = data.pop('content', '')

        # 构建 YAML
        yaml_str = "---\n"
        yaml_str += f"id: {data['id']}\n"
        yaml_str += f"name: {data['name']}\n"
        yaml_str += f"version: {data['version']}\n"
        yaml_str += f"created_at: {data['created_at']}\n"
        yaml_str += f"updated_at: {data['updated_at']}\n\n"

        # 沟通风格
        yaml_str += "# 沟通风格\n"
        yaml_str += "communication:\n"
        for key, value in data.get('communication', {}).items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\n"

        # 决策风格
        yaml_str += "# 决策风格\n"
        yaml_str += "decision:\n"
        for key, value in data.get('decision', {}).items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\n"

        # 工作风格
        yaml_str += "# 工作风格\n"
        yaml_str += "work:\n"
        for key, value in data.get('work', {}).items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\n"

        # 适配设置
        yaml_str += "# 适配设置\n"
        yaml_str += "adaptation:\n"
        for key, value in data.get('adaptation', {}).items():
            yaml_str += f"  {key}: {value}\n"
        yaml_str += "\n"

        yaml_str += "---\n\n"

        if hasattr(self, '_content'):
            yaml_str += self._content

        return yaml_str

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'Personality':
        """从 YAML 解析"""
        lines = yaml_str.split('\n')

        # 基础数据
        data = {
            'id': '',
            'name': '',
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'communication': {},
            'decision': {},
            'work': {},
            'adaptation': {}
        }

        # 解析前置元数据
        for i, line in enumerate(lines):
            if line.startswith('---'):
                break

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key in data:
                    data[key] = value

        # 解析各个部分
        current_section = None
        for line in lines:
            if line.startswith('---'):
                break

            if line.strip().startswith('#'):
                current_section = line.strip('#').strip().lower()
                continue

            if current_section and ':' in line and line.strip().startswith('  '):
                key, value = line.strip().split(':', 1)
                key = key.strip()
                value = value.strip()

                # 转换类型
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)

                # 映射到对应的部分
                section_map = {
                    '沟通风格': 'communication',
                    '决策风格': 'decision',
                    '工作风格': 'work',
                    '适配设置': 'adaptation'
                }

                if current_section in section_map:
                    section_name = section_map[current_section]
                    if section_name in data:
                        data[section_name][key] = value

        return cls(**data)


@dataclass
class UserPreferences:
    """用户偏好对象"""
    id: str
    user_id: str
    created_at: str
    updated_at: str

    # 内容偏好
    content: Dict[str, Any] = field(default_factory=dict)

    # 交互偏好
    interaction: Dict[str, Any] = field(default_factory=dict)

    # 价值观偏好
    values: Dict[str, Any] = field(default_factory=dict)

    # 学习数据
    learning_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


class PersonalityManager:
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.personality_dir = self.workspace_path / "personality"
        self.agents_dir = self.personality_dir / "agents"
        self.users_dir = self.personality_dir / "users"
        self.adjustments_dir = self.personality_dir / "adjustments"
        self.preferences_dir = self.personality_dir / "preferences"
        self.config_path = self.workspace_path / "config" / "personality-config.json"

        # 创建目录
        self._ensure_directories()

        # 加载配置
        self.config = self._load_config()

    def _ensure_directories(self):
        """确保目录存在"""
        dirs = [
            self.personality_dir,
            self.agents_dir,
            self.users_dir,
            self.adjustments_dir,
            self.preferences_dir
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """加载配置"""
        if not self.config_path.exists():
            return {
                "personality": {
                    "default_agent": "main",
                    "auto_adjust": True,
                    "adjustment_threshold": 5
                }
            }

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_personality(self, agent_id: str = "main") -> Optional[Personality]:
        """加载 Agent 性格"""
        personality_file = self.agents_dir / f"{agent_id}.md"

        if not personality_file.exists():
            # 返回默认性格
            return self._default_personality()

        with open(personality_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return Personality.from_yaml(content)

    def _default_personality(self) -> Personality:
        """默认性格（rxy的狗腿子）"""
        return Personality(
            id="agent-personality-main",
            name="rxy的狗腿子",
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            communication={
                "conciseness": 4,  # 简洁度（高）
                "humor": 1,      # 幽默感（低）
                "formality": 3,    # 正式度（中等）
                "emotional": 2     # 情感表达（较低）
            },
            decision={
                "conservative": 2,   # 保守度（低-高风险偏好高）
                "certainty": 3,      # 确定性（中等）
                "autonomy": 4         # 自主性（高）
            },
            work={
                "efficiency_first": True,  # 效率优先
                "perfectionism": 3,        # 完美主义（中等）
                "learning_style": "practice"  # 学习倾向（实践）
            },
            adaptation={
                "auto_adjust": True,
                "adjustment_rate": 0.1,
                "feedback_threshold": 10
            }
        )

    def save_personality(self, personality: Personality):
        """保存 Agent 性格"""
        personality_file = self.agents_dir / f"{personality.id}.md"

        with open(personality_file, 'w', encoding='utf-8') as f:
            f.write(personality.to_yaml())

        personality.updated_at = datetime.now().isoformat()

    def adjust_parameter(self, parameter_path: str, delta: int, reason: str):
        """调整性格参数"""
        # 解析参数路径，例如 "communication.conciseness"
        parts = parameter_path.split('.')

        personality = self.load_personality()
        if not personality:
            return

        # 当前值
        current_value = personality
        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                if part == parts[-1]:
                    current_value = current_value[part]
                else:
                    current_value = current_value[part]
            else:
                return

        # 新值（限制在 1-5）
        new_value = min(max(int(current_value) + delta, 1), 5)

        # 应用调整
        target = personality
        for part in parts[:-1]:
            target = getattr(target, part, {})

        setattr(target, parts[-1], new_value)

        # 保存调整后的性格
        self.save_personality(personality)

        # 记录调整历史
        self._log_adjustment(parameter_path, current_value, new_value, reason)

    def _log_adjustment(self, parameter_path: str, old_value: int, new_value: int, reason: str):
        """记录调整历史"""
        history_file = self.adjustments_dir / "history.json"
        history = []

        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

        adjustment = {
            "timestamp": datetime.now().isoformat(),
            "parameter_path": parameter_path,
            "old_value": old_value,
            "new_value": new_value,
            "delta": new_value - old_value,
            "reason": reason
        }

        history.append(adjustment)

        # 保留最近 100 条
        history = history[-100:]

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """加载用户偏好"""
        pref_file = self.users_dir / f"{user_id}.md"

        if not pref_file.exists():
            return None

        with open(pref_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简化解析（不使用 YAML，直接 JSON）
        try:
            data = json.loads(content.split('---')[-1])
            return UserPreferences(**data)
        except:
            return None

    def save_user_preferences(self, preferences: UserPreferences):
        """保存用户偏好"""
        pref_file = self.users_dir / f"{preferences.id}.md"

        data = preferences.to_dict()

        with open(pref_file, 'w', encoding='utf-8') as f:
            f.write("---\n\n")
            f.write(f"# 用户偏好\n\n")
            f.write(json.dumps(data, ensure_ascii=False, indent=2))

    def get_adjustment_history(self, days: int = 30) -> List[Dict]:
        """获取调整历史"""
        history_file = self.adjustments_dir / "history.json"
        if not history_file.exists():
            return []

        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        # 过滤时间
        cutoff_date = datetime.now() - timedelta(days=days)

        return [
            adj for adj in history
            if datetime.fromisoformat(adj['timestamp']) >= cutoff_date
        ]

    def get_stats(self) -> Dict:
        """获取统计信息"""
        # 统计调整次数
        adjustments = self.get_adjustment_history(days=30)

        # 统计各参数的调整次数
        param_adjustments = {}
        for adj in adjustments:
            param = adj['parameter_path']
            if param not in param_adjustments:
                param_adjustments[param] = 0
            param_adjustments[param] += 1

        return {
            "total_adjustments": len(adjustments),
            "parameter_adjustments": param_adjustments,
            "last_adjustment": adjustments[-1] if adjustments else None,
            "config": self.config
        }


def main():
    """命令行接口"""
    pm = PersonalityManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python personality-manager.py load [agent_id]               # 加载性格")
        print("  python personality-manager.py adjust <param> <delta> <reason>  # 调整参数")
        print("  python personality-manager.py history [days]                   # 调整历史")
        print("  python personality-manager.py stats                             # 统计信息")
        sys.exit(1)

    command = sys.argv[1]

    if command == "load":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else "main"
        personality = pm.load_personality(agent_id)
        if personality:
            print(f"加载性格: {personality.name}")
            print(f"简洁度: {personality.communication.get('conciseness', 0)}/5")
            print(f"幽默感: {personality.communication.get('humor', 0)}/5")
            print(f"正式度: {personality.communication.get('formality', 0)}/5")
        else:
            print("未找到性格配置")

    elif command == "adjust":
        if len(sys.argv) < 5:
            print("错误: 需要提供参数路径、调整值和原因")
            sys.exit(1)

        param_path = sys.argv[2]
        delta = int(sys.argv[3])
        reason = " ".join(sys.argv[4:])

        pm.adjust_parameter(param_path, delta, reason)
        print(f"调整参数: {param_path} ({delta:+d})")
        print(f"原因: {reason}")

    elif command == "history":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        history = pm.get_adjustment_history(days)
        print(f"最近 {days} 天的调整历史 ({len(history)} 条):\n")

        for adj in history[-10:]:
            print(f"  {adj['timestamp']}")
            print(f"    参数: {adj['parameter_path']}")
            print(f"    变化: {adj['old_value']} → {adj['new_value']} ({adj['delta']:+d})")
            print(f"    原因: {adj['reason']}")
            print()

    elif command == "stats":
        stats = pm.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
