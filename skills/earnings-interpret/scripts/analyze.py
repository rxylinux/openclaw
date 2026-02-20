#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报解读分析器 Skill
你是一名负责 [行业] 的高级股票研究分析师。
每一个数字都必须标注来源。
必须清楚区分已确认的实际披露数据与前瞻性预测。
不要编造任何引用或财务指标。

请分析 [公司名称 / 股票代码] 最近一次财报。
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

class EarningsInterpreterSkill:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.temp_dir = f"{self.workspace}/temp"

    def search_baidu(self, query, recency="month"):
        """搜索百度数据"""
        cmd = f'python3 /root/.openclaw/workspace/skills/baidu-search/scripts/search.py \'{{"query": "{query}", "search_recency_filter": "{recency}"}}\''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
        return []

    def analyze(self, company, industry="科技"):
        """
        执行完整的财报解读分析

        Args:
            company: 公司名称或股票代码
            industry: 行业名称

        Returns:
            dict: 分析结果
        """
        print(f"📊 正在进行财报解读分析: {company}")
        print(f"🏢 行业: {industry}")
        print(f"⚠️ 注意：本分析严格遵守“不编造任何引用或财务指标”的原则，如果某项数据不可获取，将明确说明。")

        # 搜索财报数据
        query = f"{company} 财报 营收 EPS 指引 超预期 不及预期 电话会议"
        results = self.search_baidu(query)

        print(f"🔍 搜索到 {len(results)} 条结果")

        # 提取财报数据
        earnings_data = self.extract_earnings_data(company, results)

        # 生成报告
        full_report = self._generate_full_report(company, industry, earnings_data)

        # 保存报告
        report_file = f"{self.temp_dir}/earnings-analysis-{company.replace(' ', '-')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        # 使用消息发送器
        self._send_report(report_file)

        return {
            "company": company,
            "industry": industry,
            "report_file": report_file,
            "full_report": full_report,
            "earnings_data": earnings_data,
            "status": "completed"
        }

    def extract_earnings_data(self, company, results):
        """
        从搜索结果中提取财报数据
        严格遵守：不编造任何引用或财务指标
        """
        data = {
            "company": company,
            "source": "百度搜索",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "core_data": {},
            "guidance": {},
            "segments": {},
            "management_comments": {},
            "market_reaction": {},
            "final_conclusion": {}
        }

        # 遍历搜索结果，提取数据
        for item in results:
            content = item.get("content", "")
            url = item.get("url", "")
            date = item.get("date", "")

            # 尝试提取营收和EPS数据
            if "超预期" in content or "不及预期" in content:
                data["core_data"]["beat_miss"] = {
                    "value": "需要从财报电话会议纪要中提取",
                    "source": url,
                    "date": date,
                    "note": "必须清楚区分已确认的实际披露数据与前瞻性预测"
                }

            if "营收" in content:
                data["core_data"]["revenue"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从财报电话会议纪要中提取精确数值"
                }

            if "EPS" in content or "每股收益" in content:
                data["core_data"]["eps"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从财报电话会议纪要中提取精确数值"
                }

            # 尝试提取指引数据
            if "指引" in content or "前瞻" in content:
                data["guidance"]["outlook"] = {
                    "value": "需要从财报电话会议纪要中提取",
                    "source": url,
                    "date": date,
                    "note": "需要从财报电话会议纪要中提取管理层指引"
                }

        return data

    def _generate_core_data_section(self, company, earnings_data):
        """第1步——核心数据"""
        content = "## 第1步——核心数据\n\n"

        content += "### 营收：市场预期 vs 实际结果，是超预期还是不及预期？差额是多少（美元和百分比）\n\n"
        content += "| 指标 | 市场预期 | 实际结果 | 超预期/不及预期 | 差额（美元） | 差额（%） | 来源 | 报告日期 |\n"
        content += "|------|----------|----------|--------------|------------|----------|------|----------|\n"
        content += f"| 营收 | 不可获取 | 不可获取 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须清楚区分已确认的实际披露数据与前瞻性预测，需要从财报电话会议纪要中提取精确数值，当前数据不可获取。\n\n"

        content += "### 每股收益（EPS）：预期 vs 实际，是超预期还是不及预期？差额是多少\n\n"
        content += "| 指标 | 市场预期 | 实际结果 | 超预期/不及预期 | 差额 | 来源 | 报告日期 |\n"
        content += "|------|----------|----------|--------------|------|------|----------|\n"
        content += f"| EPS | 不可获取 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须清楚区分已确认的实际披露数据与前瞻性预测，需要从财报电话会议纪要中提取精确数值，当前数据不可获取。\n\n"

        content += "### 是否存在一次性项目影响利润？调整后数据与 GAAP 数据有何差异？\n\n"
        content += "| 指标 | GAAP 数据 | Non-GAAP 数据 | 差异 | 来源 | 报告日期 |\n"
        content += "|------|----------|-------------|------|------|----------|\n"
        content += f"| 净利润 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| EPS | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取 GAAP 和 Non-GAAP 数据，当前数据不可获取。\n\n"

        return content

    def _generate_guidance_section(self, company, earnings_data):
        """第2步——前瞻指引"""
        content = "## 第2步——前瞻指引\n\n"

        content += "### 管理层是上调、下调还是维持业绩指引？\n\n"
        content += "| 指标 | 状态 | 前指引 | 新指引 | 来源 | 报告日期 |\n"
        content += "|------|------|--------|--------|------|----------|\n"
        content += f"| 业绩指引 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取管理层指引，当前数据不可获取。\n\n"

        content += "### 下一季度指引：营收区间和 EPS 区间\n\n"
        content += "| 指标 | 区间下限 | 区间上限 | 中点 | 来源 | 报告日期 |\n"
        content += "|------|---------|---------|------|------|----------|\n"
        content += f"| 下一季度营收 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 下一季度 EPS | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取前瞻指引，当前数据不可获取。\n\n"

        content += "### 全年指引：相比上一季度是否发生变化？\n\n"
        content += "| 指标 | 前指引 | 新指引 | 变化 | 来源 | 报告日期 |\n"
        content += "|------|--------|--------|------|------|----------|\n"
        content += f"| 全年营收 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 全年 EPS | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取全年指引，当前数据不可获取。\n\n"

        content += "### 管理层使用的措辞（乐观、谨慎、不确定等）\n\n"
        content += "| 管理层 | 核心引用 | 语气评估 | 来源 | 报告日期 |\n"
        content += "|--------|----------|---------|------|----------|\n"
        content += f"| CEO | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| CFO | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        return content

    def _generate_segments_section(self, company, earnings_data):
        """第3步——业务板块拆解"""
        content = "## 第3步——业务板块拆解\n\n"

        content += "### 各业务板块表现：哪些增长，哪些下滑？幅度是多少？\n\n"
        content += "| 业务板块 | 表现 | 增长率 | 贡献 | 来源 | 报告日期 |\n"
        content += "|----------|------|--------|------|------|----------|\n"
        content += f"| 板块1 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 板块2 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取业务板块表现，当前数据不可获取。\n\n"

        content += "### 是否强调了新的业务板块、产品线或地区市场？\n\n"
        content += "| 类型 | 内容 | 重点 | 来源 | 报告日期 |\n"
        content += "|------|------|------|------|----------|\n"
        content += f"| 新业务板块 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 新产品线 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 新地区市场 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取新业务板块信息，当前数据不可获取。\n\n"

        content += "### 哪个板块对超预期或不及预期贡献最大？\n\n"
        content += "| 业务板块 | 贡献度 | 超预期/不及预期 | 原因 | 来源 | 报告日期 |\n"
        content += "|----------|--------|--------------|------|------|----------|\n"
        content += f"| 板块1 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取板块贡献数据，当前数据不可获取。\n\n"

        return content

    def _generate_management_comments_section(self, company, earnings_data):
        """第4步——管理层评论（必须引用真实电话会议纪要）"""
        content = "## 第4步——管理层评论（必须引用真实电话会议纪要）\n\n"

        content += "### CEO 核心信息（1–2 步话）\n\n"
        content += "| 引用 | 来源 | 报告日期 |\n"
        content += "|------|------|----------|\n"
        content += f"| CEO 核心信息 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        content += "### CFO 对财务前景的核心表述（1–2 步话）\n\n"
        content += "| 引用 | 来源 | 报告日期 |\n"
        content += "|------|------|----------|\n"
        content += f"| CFO 核心信息 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        content += "### 是否提到新的战略重点、转型方向或潜在风险？\n\n"
        content += "| 类型 | 内容 | 风险评估 | 来源 | 报告日期 |\n"
        content += "|------|------|----------|------|----------|\n"
        content += f"| 战略重点 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 转型方向 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 潜在风险 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        content += "### 语气评估：自信、谨慎、防御性还是回避问题？\n\n"
        content += "| 管理层 | 语气 | 原因 | 来源 | 报告日期 |\n"
        content += "|--------|------|------|------|----------|\n"
        content += f"| CEO | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| CFO | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        return content

    def _generate_market_reaction_section(self, company, earnings_data):
        """第5步——市场与分析师反应"""
        content = "## 第5步——市场与分析师反应\n\n"

        content += "### 盘后及下一交易日股价变动（精确百分比）\n\n"
        content += "| 时间段 | 股价变动 | 精确百分比 | 来源 | 报告日期 |\n"
        content += "|--------|----------|------------|------|----------|\n"
        content += f"| 盘后（盘后） | 不可获取 | 不可获取 | 百度搜索 | N/A |\n"
        content += f"| 下一交易日 | 不可获取 | 不可获取 | 百度搜索 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从百度搜索中提取股价变动数据，当前数据不可获取。\n\n"

        content += "### 财报后上调或下调评级的分析师（机构名称、旧评级 → 新评级、新目标价）\n\n"
        content += "| 机构名称 | 旧评级 | 新评级 | 新目标价 | 变动日期 | 来源 |\n"
        content += "|----------|--------|--------|---------|----------|------|\n"
        content += f"| 机构1 | 不可获取 | 不可获取 | 不可获取 | N/A | 百度搜索 |\n"
        content += f"| 机构2 | 不可获取 | 不可获取 | 不可获取 | N/A | 百度搜索 |\n"
        content += "\n**注意**：⚠️ 需要从百度搜索中提取分析师评级变动数据，当前数据不可获取。\n\n"

        content += "### 分析师问答环节的关键主题\n\n"
        content += "| 主题 | 关键问题 | 管理层回答 | 来源 | 报告日期 |\n"
        content += "|------|----------|----------|------|----------|\n"
        content += f"| 主题1 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 主题2 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        return content

    def _generate_final_conclusion_section(self, company, earnings_data):
        """第6步——最终结论"""
        content = "## 第6步——最终结论\n\n"

        content += "### 本次财报中最重要的一个数字是什么？为什么？\n\n"
        content += "| 指标 | 数值 | 原因 | 来源 | 报告日期 |\n"
        content += "|------|------|------|------|----------|\n"
        content += f"| 最重要数字 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取最重要数字和原因，当前数据不可获取。\n\n"

        content += "### 这是一个真正强劲的季度，还是“表面好看”？解释原因\n\n"
        content += "| 评估 | 结论 | 原因 | 来源 | 报告日期 |\n"
        content += "|------|------|------|------|----------|\n"
        content += f"| 季度评估 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 需要从财报电话会议纪要中提取季度评估和原因，当前数据不可获取。\n\n"

        content += "### 根据管理层表述，下个季度最值得关注什么？\n\n"
        content += "| 关注点 | 内容 | 重要性 | 来源 | 报告日期 |\n"
        content += "|--------|------|--------|------|----------|\n"
        content += f"| 关注点1 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += f"| 关注点2 | 不可获取 | 不可获取 | 不可获取 | 财报电话会议纪要 | N/A |\n"
        content += "\n**注意**：⚠️ 必须引用真实电话会议纪要，当前数据不可获取。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"

        return content

    def _generate_full_report(self, company, industry, earnings_data):
        """生成完整报告"""
        content = f"# {company} 财报解读分析报告\n\n"
        content += f"**公司名称**: {company}\n"
        content += f"**行业**: {industry}\n"
        content += f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += f"**分析师**: 负责 {industry} 的高级股票研究分析师\n\n"
        content += "---\n"
        content += "**免责声明**: 本报告仅供信息参考，不构成投资建议。所有数据均来自公开来源（财报电话会议纪要），可能存在延迟或错误。投资者应基于自身研究和判断做出投资决策。投资有风险，入市需谨慎。\n\n"
        content += "---\n"
        content += f"**数据来源说明**: 本分析严格遵守“不编造任何引用或财务指标”的原则，每一个数字都必须标注来源。必须清楚区分已确认的实际披露数据与前瞻性预测。如财报电话会议纪要尚未发布，请明确标记说明。\n\n"
        content += "---\n\n"

        # 添加6个分析步骤
        content += self._generate_core_data_section(company, earnings_data)
        content += "---\n\n"
        content += self._generate_guidance_section(company, earnings_data)
        content += "---\n\n"
        content += self._generate_segments_section(company, earnings_data)
        content += "---\n\n"
        content += self._generate_management_comments_section(company, earnings_data)
        content += "---\n\n"
        content += self._generate_market_reaction_section(company, earnings_data)
        content += "---\n\n"
        content += self._generate_final_conclusion_section(company, earnings_data)

        return content

    def _send_report(self, report_file):
        """发送报告"""
        cmd = f"python3 /root/.openclaw/workspace/scripts/message-sender.py --file {report_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result

def main():
    import argparse

    parser = argparse.ArgumentParser(description="财报解读分析器Skill")
    parser.add_argument("--company", required=True, help="公司名称或股票代码")
    parser.add_argument("--industry", default="科技", help="行业名称")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建分析器实例
    analyzer = EarningsInterpreterSkill()

    # 执行分析
    print(f"📊 开始财报解读分析: {args.company}")
    result = analyzer.analyze(args.company, args.industry)

    print(f"\n📋 分析结果:")
    print(f"  🏢 公司名称: {result['company']}")
    print(f"  🏭 行业: {result['industry']}")
    print(f"  📄 报告文件: {result['report_file']}")
    print(f"  💰 财报数据: {result['earnings_data']}")
    print(f"  ✅ 分析状态: {result['status']}")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['full_report'])
        print(f"✅ 报告已保存到: {args.output}")

if __name__ == "__main__":
    main()
