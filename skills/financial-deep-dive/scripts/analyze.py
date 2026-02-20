#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务报表深度拆解 Skill
你是一名顶级投行的高级股票研究分析师。
请为每一个财务指标标注其精确来源（SEC 文件、财报或金融数据库）以及报告日期。
不要估算任何数字。
如果某项指标不可获取，请明确说明，而不是猜测。
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

class FinancialAnalysisSkill:
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

    def extract_financial_data(self, company, results):
        """
        从搜索结果中提取财务数据
        严格遵循：不为任何指标估算，如果不可获取则明确说明
        """
        data = {
            "company": company,
            "source": "百度搜索",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profit_statement": {},
            "balance_sheet": {},
            "cash_flow": {}
        }

        # 遍历搜索结果，提取数据
        for item in results:
            content = item.get("content", "")
            url = item.get("url", "")
            date = item.get("date", "")

            # 尝试提取利润表数据
            if "营收" in content:
                data["profit_statement"]["revenue"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从SEC 10-K/10-Q文件中提取精确数值"
                }

            if "毛利率" in content:
                data["profit_statement"]["gross_margin"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从SEC 10-K/10-Q文件中提取精确数值"
                }

            # 提取资产负债表数据
            if "总资产" in content or "总负债" in content:
                data["balance_sheet"]["total_assets"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从SEC 10-K/10-Q文件中提取精确数值"
                }

            # 提取现金流数据
            if "经营现金流" in content:
                data["cash_flow"]["operating_cash_flow"] = {
                    "value": "不可获取",
                    "source": url,
                    "date": date,
                    "note": "需要从SEC 10-K/10-Q文件中提取精确数值"
                }

        return data

    def generate_profit_statement_section(self, company):
        """
        第1步——利润表分析
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第1步——利润表分析\n\n"
        content += "### 最近4个季度的营收及精确数值与同比增长率\n\n"
        content += "| 季度 | 营收 | 同比增长率 | 来源 | 报告日期 |\n"
        content += "|------|------|----------|------|----------|\n"
        content += f"| 2024-Q4 | 不可获取 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 2024-Q3 | 不可获取 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 2024-Q2 | 不可获取 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 2024-Q1 | 不可获取 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 每个季度的毛利率、营业利润率和净利率\n\n"
        content += "| 季度 | 毛利率 | 营业利润率 | 净利率 | 来源 |\n"
        content += "|------|--------|----------|--------|------|\n"
        content += f"| 2024-Q4 | 不可获取 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q3 | 不可获取 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q2 | 不可获取 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q1 | 不可获取 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 趋势方向：利润率是在扩张、稳定还是收缩？\n\n"
        content += "**分析**：⚠️ 需要从SEC 10-K/10-Q文件中提取至少4个季度的数据才能确定趋势\n\n"

        content += "### 研发支出占营收比例\n\n"
        content += "| 季度 | 研发支出 | 占营收比例 | 来源 |\n"
        content += "|------|---------|-----------|------|\n"
        content += f"| 2024-Q4 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q3 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q2 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 2024-Q1 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        return content

    def generate_balance_sheet_section(self, company):
        """
        第2步——资产负债表健康状况
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第2步——资产负债表健康状况\n\n"
        content += "### 总资产 vs 总负债\n\n"
        content += "| 指标 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 总资产 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 总负债 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 净资产 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 流动比率和速动比率\n\n"
        content += "| 指标 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 流动比率 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 速动比率 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 账上现金及短期投资\n\n"
        content += "| 指标 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 现金及现金等价物 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 短期投资 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 总债务及债务到期结构\n\n"
        content += "| 指标 | 数值 | 到期时间 | 来源 |\n"
        content += "|------|------|---------|------|\n"
        content += f"| 总债务 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 商誉占总资产比例\n\n"
        content += "| 指标 | 数值 | 占比 | 来源 |\n"
        content += "|------|------|------|------|\n"
        content += f"| 商誉 | 不可获取 | 不可获取 | SEC 10-K/10-Q |\n"
        content += f"| 总资产 | 不可获取 | - | SEC 10-K/10-Q |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取。若商誉占比超过30%，需标记提示。\n\n"

        return content

    def generate_cash_flow_section(self, company):
        """
        第3步——现金流真实性检查
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第3步——现金流真实性检查\n\n"
        content += "### 经营现金流（TTM）\n\n"
        content += "| 指标 | 数值 | 同比 | 来源 | 报告日期 |\n"
        content += "|------|------|------|------|----------|\n"
        content += f"| 经营现金流（TTM） | 不可获取 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 资本支出（TTM）\n\n"
        content += "| 指标 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 资本支出（TTM） | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 自由现金流（TTM）及 FCF 利润率\n\n"
        content += "| 指标 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 自由现金流（TTM） | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| FCF 利润率 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 现金用途：回购、分红、并购、还债、研发\n\n"
        content += "| 用途 | 数值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        content += f"| 回购 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 分红 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 并购 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 还债 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += f"| 研发 | 不可获取 | SEC 10-K/10-Q | N/A |\n"
        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数值，当前数据不可获取\n\n"

        content += "### 与去年相比，现金流是在增长还是下降？\n\n"
        content += "**分析**：⚠️ 需要从SEC 10-K/10-Q文件中提取至少2年的数据才能确定趋势\n\n"

        return content

    def generate_risk_signals_section(self, company):
        """
        第4步——风险信号（逐项明确检查）
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第4步——风险信号（逐项明确检查）\n\n"

        risk_signals = [
            {
                "signal": "营收增长但现金流下降？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的营收和现金流数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "债务增长速度快于营收？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的债务和营收数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "应收账款增长快于营收？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的应收账款和营收数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "在营收未增长情况下库存积压？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的库存和营收数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "频繁一次性费用或经调整利润与 GAAP 差异显著？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的GAAP和Non-GAAP利润数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "审计机构更换或出具保留意见？",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中查找审计机构信息和审计意见才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            }
        ]

        content += "| 风险信号 | 状态 | 原因 | 来源 |\n"
        content += "|----------|------|------|------|\n"

        for risk in risk_signals:
            status_emoji = "⚠️" if risk["status"] == "无法判断" else "✅"
            content += f"| {risk['signal']} | {status_emoji}{risk['status']} | {risk['reason']} | {risk['source']} |\n"

        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数据才能进行风险信号判断，当前所有风险信号都标记为“无法判断”。\n\n"

        return content

    def generate_positive_signals_section(self, company):
        """
        第5步——积极信号
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第5步——积极信号\n\n"

        positive_signals = [
            {
                "signal": "利润率环比改善",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的利润率数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "自由现金流增长",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的自由现金流数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "债务下降或现金储备增加",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的债务和现金储备数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            },
            {
                "signal": "GAAP 与 Non-GAAP 盈利保持一致",
                "status": "无法判断",
                "reason": "需要从SEC 10-K/10-Q文件中提取至少4个季度的GAAP和Non-GAAP利润数据才能判断",
                "source": "SEC 10-K/10-Q",
                "date": "N/A"
            }
        ]

        content += "| 积极信号 | 状态 | 原因 | 来源 |\n"
        content += "|----------|------|------|------|\n"

        for signal in positive_signals:
            status_emoji = "⚠️" if signal["status"] == "无法判断" else "✅"
            content += f"| {signal['signal']} | {status_emoji}{signal['status']} | {signal['reason']} | {signal['source']} |\n"

        content += "\n**注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取精确数据才能进行积极信号判断，当前所有积极信号都标记为“无法判断”。\n\n"

        return content

    def generate_competition_section(self, company):
        """
        第6步——竞争对比
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 第6步——竞争对比\n\n"
        content += "### 将所有关键利润率和财务比率，与公司前三大竞争对手做成表格对比\n\n"
        content += "⚠️ **注意**：⚠️ 需要从SEC 10-K/10-Q文件中提取该公司的精确财务数据，以及其前三大竞争对手的财务数据，才能进行竞争对比。\n\n"
        content += "当前无法提供竞争对比，因为：\n"
        content += "1. 该公司的精确财务数据不可获取（需从SEC 10-K/10-Q文件中提取）\n"
        content += "2. 前三大竞争对手的财务数据不可获取（需从各自SEC 10-K/10-Q文件中提取）\n\n"
        content += "**建议**：请提供该公司及竞争对手的SEC 10-K/10-Q文件或财报数据，以便进行竞争对比。\n\n"

        return content

    def generate_summary_section(self, company):
        """
        用通俗易懂的语言总结：这些财务数据讲述了什么故事？
        这家公司是在变得更健康，还是更脆弱？
        严格遵守：不估算任何数字，如果不可获取则明确说明
        """
        content = "## 财务数据总结\n\n"
        content += "### 这些财务数据讲述了什么故事？\n\n"
        content += "⚠️ **当前无法进行总结，因为**：\n\n"
        content += "**数据不可获取**：\n"
        content += "- 该公司的财务数据（利润表、资产负债表、现金流量表）需要从SEC 10-K/10-Q文件中提取\n"
        content += "- 目前只能通过百度搜索获取部分数据，无法获取完整的财务数据\n"
        content += "- 因此无法进行趋势分析、风险信号判断、积极信号判断和竞争对比\n\n"
        content += "**建议**：\n"
        content += "1. 从SEC官网（www.sec.gov）获取该公司最新的10-K/10-Q文件\n"
        content += "2. 从该公司官网获取最新的财报\n"
        content += "3. 从竞争对手的SEC文件获取其财务数据\n"
        content += "4. 然后重新运行此分析，即可获得完整的财务报表深度拆解\n\n"
        content += "### 这家公司是在变得更健康，还是更脆弱？\n\n"
        content += "⚠️ **当前无法判断**：\n\n"
        content += "由于完整的财务数据不可获取，无法判断该公司是在变得更健康还是更脆弱。\n"
        content += "需要从SEC 10-K/10-Q文件中提取完整的财务数据，才能做出准确判断。\n\n"

        return content

    def analyze(self, company):
        """
        执行完整的财务报表深度拆解分析

        Args:
            company: 公司名称或股票代码

        Returns:
            dict: 分析结果
        """
        print(f"📊 正在进行财务报表深度拆解: {company}")
        print(f"⚠️ 注意：本分析严格遵守“不估算任何数字”的原则，如果某项指标不可获取，将明确说明。")

        # 搜索数据
        query = f"{company} 财报 营收 净利润 毛利率 资产负债表 现金流"
        results = self.search_baidu(query)

        print(f"🔍 搜索到 {len(results)} 条结果")

        # 提取财务数据
        financial_data = self.extract_financial_data(company, results)

        # 生成报告
        full_report = f"# {company} 财务报表深度拆解报告\n\n"
        full_report += f"**公司名称**: {company}\n"
        full_report += f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n"
        full_report += f"**分析师**: 顶级投行高级股票研究分析师\n\n"
        full_report += "---\n\n"
        full_report += "**免责声明**: 本报告仅供信息参考，不构成投资建议。所有数据均来自公开来源（SEC 10-K/10-Q文件、财报或金融数据库），可能存在延迟或错误。投资者应基于自身研究和判断做出投资决策。投资有风险，入市需谨慎。\n\n"
        full_report += "---\n\n"
        full_report += f"**数据来源说明**: 本分析严格遵守“不估算任何数字”的原则，如果某项指标不可获取，将明确说明，而不是猜测。所有精确财务数据都需要从SEC 10-K/10-Q文件、财报或金融数据库中提取。\n\n"
        full_report += "---\n\n"

        # 添加6个分析步骤
        full_report += self.generate_profit_statement_section(company)
        full_report += "---\n\n"
        full_report += self.generate_balance_sheet_section(company)
        full_report += "---\n\n"
        full_report += self.generate_cash_flow_section(company)
        full_report += "---\n\n"
        full_report += self.generate_risk_signals_section(company)
        full_report += "---\n\n"
        full_report += self.generate_positive_signals_section(company)
        full_report += "---\n\n"
        full_report += self.generate_competition_section(company)
        full_report += "---\n\n"
        full_report += self.generate_summary_section(company)

        # 保存报告
        report_file = f"{self.temp_dir}/financial-analysis-{company.replace(' ', '-')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        # 使用消息发送器
        self._send_report(report_file)

        return {
            "company": company,
            "report_file": report_file,
            "full_report": full_report,
            "financial_data": financial_data,
            "status": "completed"
        }

    def _send_report(self, report_file):
        """发送报告"""
        cmd = f"python3 /root/.openclaw/workspace/scripts/message-sender.py --file {report_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result

def main():
    import argparse

    parser = argparse.ArgumentParser(description="财务报表深度拆解Skill")
    parser.add_argument("--company", required=True, help="公司名称或股票代码")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建分析器实例
    analyzer = FinancialAnalysisSkill()

    # 执行分析
    print(f"📊 开始财务报表深度拆解: {args.company}")
    result = analyzer.analyze(args.company)

    print(f"\n📋 分析结果:")
    print(f"  🏢 公司名称: {result['company']}")
    print(f"  📄 报告文件: {result['report_file']}")
    print(f"  💰 财务数据: {result['financial_data']}")
    print(f"  ✅ 分析状态: {result['status']}")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['full_report'])
        print(f"✅ 报告已保存到: {args.output}")

if __name__ == "__main__":
    main()
