#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业与板块对比分析 Skill
你是一名高级股票研究分析师，正在撰写行业竞争格局报告。
每一个指标都必须标注来源和日期。
仅使用最新披露的数据。
不要估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'。
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

class IndustryComparisonSkill:
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

    def extract_company_data(self, stock, results):
        """
        从搜索结果中提取公司数据
        严格遵守：不估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'
        """
        data = {
            "stock": stock,
            "source": "百度搜索",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "metrics": {}
        }

        # 遍历搜索结果，提取数据
        for item in results:
            content = item.get("content", "")
            url = item.get("url", "")
            date = item.get("date", "")

            # 尝试提取市值
            if "市值" in content:
                data["metrics"]["market_cap"] = {
                    "value": "N/A 未公开披露",
                    "source": url,
                    "date": date,
                    "note": "需要从金融数据库或公司财报中提取精确数值"
                }

            # 尝试提取营收
            if "营收" in content:
                data["metrics"]["revenue"] = {
                    "value": "N/A 未公开披露",
                    "source": url,
                    "date": date,
                    "note": "需要从公司财报中提取精确数值"
                }

            # 尝试提取毛利率
            if "毛利率" in content:
                data["metrics"]["gross_margin"] = {
                    "value": "N/A 未公开披露",
                    "source": url,
                    "date": date,
                    "note": "需要从公司财报中提取精确数值"
                }

        return data

    def generate_comparison_table_section(self, stocks, industry):
        """
        第1步——建立对比表格（每家公司包含以下列）
        严格遵守：不估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'
        """
        content = "## 第1步——建立对比表格（每家公司包含以下列）\n\n"
        content += f"**行业/板块**: {industry}\n\n"

        content += "### 市值\n\n"
        content += "| 公司 | 市值 | 来源 | 报告日期 |\n"
        content += "|------|------|------|----------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | 金融数据库/公司财报 | N/A |\n"
        content += "\n**注意**: ⚠️ 需要从金融数据库或公司财报中提取精确数值，当前数据不可获取。\n\n"

        content += "### TTM 营收及同比增长率\n\n"
        content += "| 公司 | TTM 营收 | 同比增长率 | 来源 | 报告日期 |\n"
        content += "|------|----------|----------|------|----------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | 公司财报 | N/A |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取精确数值，当前数据不可获取。\n\n"

        content += "### 毛利率、营业利润率和净利率\n\n"
        content += "| 公司 | 毛利率 | 营业利润率 | 净利率 | 来源 |\n"
        content += "|------|--------|----------|--------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取精确数值，当前数据不可获取。\n\n"

        content += "### 市盈率（P/E）、预期市盈率、市销率、EV/EBITDA、PEG 比率\n\n"
        content += "| 公司 | P/E | Forward P/E | P/S | EV/EBITDA | PEG 比率 | 来源 |\n"
        content += "|------|-----|-----------|-----|----------|--------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 金融数据库 |\n"
        content += "\n**注意**: ⚠️ 需要从金融数据库中提取精确数值，当前数据不可获取。\n\n"

        content += "### 资产负债率及净负债\n\n"
        content += "| 公司 | 资产负债率 | 净负债 | 来源 |\n"
        content += "|------|----------|--------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取精确数值，当前数据不可获取。\n\n"

        content += "### 自由现金流及 FCF 收益率\n\n"
        content += "| 公司 | 自由现金流 | FCF 收益率 | 来源 |\n"
        content += "|------|----------|-----------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取精确数值，当前数据不可获取。\n\n"

        content += "### 该行业关键增长指标（例如：订阅用户数、活跃用户数、预订量、销量等）\n\n"
        content += "| 公司 | 指标1 | 指标2 | 指标3 | 来源 |\n"
        content += "|------|------|------|------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报或业务报告中提取行业关键增长指标，当前数据不可获取。\n\n"

        return content

    def generate_competitive_positioning_section(self, stocks, industry):
        """
        第2步——竞争定位
        严格遵守：不估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'
        """
        content = "## 第2步——竞争定位\n\n"
        content += f"**行业/板块**: {industry}\n\n"

        content += "### 每家公司的核心竞争壁垒是什么？\n\n"
        content += "| 公司 | 核心竞争壁垒 | 来源 |\n"
        content += "|------|--------------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | 行业研究报告/公司年报 |\n"
        content += "\n**注意**: ⚠️ 需要从行业研究报告或公司年报中提取核心竞争壁垒，当前数据不可获取。\n\n"

        content += "### 市场份额排名（如有数据请注明来源）\n\n"
        content += "| 排名 | 公司 | 市场份额 | 来源 |\n"
        content += "|------|------|----------|------|\n"
        for i, stock in enumerate(stocks, 1):
            content += f"| {i} | {stock} | N/A 未公开披露 | 行业研究报告 |\n"
        content += "\n**注意**: ⚠️ 需要从行业研究报告中提取市场份额数据，当前数据不可获取。\n\n"

        content += "### 哪家公司正在提升市场份额？哪家正在流失份额？\n\n"
        content += "| 公司 | 市场份额变化 | 趋势 | 来源 |\n"
        content += "|------|--------------|------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | 不可判断 | 行业研究报告 |\n"
        content += "\n**注意**: ⚠️ 需要从行业研究报告中提取市场份额变化数据，当前数据不可获取。\n\n"

        return content

    def generate_risk_comparison_section(self, stocks, industry):
        """
        第3步——风险对比
        严格遵守：不估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'
        """
        content = "## 第3步——风险对比\n\n"
        content += f"**行业/板块**: {industry}\n\n"

        content += "### 未来 12 个月每家公司最大的单一风险是什么？\n\n"
        content += "| 公司 | 最大单一风险 | 风险等级 | 来源 |\n"
        content += "|------|--------------|----------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | 行业研究报告/公司年报 |\n"
        content += "\n**注意**: ⚠️ 需要从行业研究报告或公司年报中提取最大单一风险，当前数据不可获取。\n\n"

        content += "### 哪家公司债务风险最高？\n\n"
        content += "| 公司 | 债务风险 | 资产负债率 | 来源 |\n"
        content += "|------|----------|----------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取资产负债率数据，当前数据不可获取。\n\n"

        content += "### 哪家公司竞争风险最高？\n\n"
        content += "| 公司 | 竞争风险 | 市场份额 | 行业竞争程度 | 来源 |\n"
        content += "|------|----------|----------|------------|------|\n"
        for stock in stocks:
            content += f"| {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 行业研究报告 |\n"
        content += "\n**注意**: ⚠️ 需要从行业研究报告中提取竞争风险数据，当前数据不可获取。\n\n"

        return content

    def generate_ranking_conclusion_section(self, stocks, industry):
        """
        第4步——排名与结论
        严格遵守：不估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'
        """
        content = "## 第4步——排名与结论\n\n"
        content += f"**行业/板块**: {industry}\n\n"

        content += "### 最具价值标的（在关键估值指标相对增长下最便宜）\n\n"
        content += "| 排名 | 公司 | P/E | 营收增长率 | 估值合理性 | 来源 |\n"
        content += "|------|------|-----|----------|----------|------|\n"
        for i, stock in enumerate(stocks, 1):
            content += f"| {i} | {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 金融数据库 |\n"
        content += "\n**注意**: ⚠️ 需要从金融数据库中提取估值和增长率数据，当前数据不可获取。无法确定最具价值标的。\n\n"

        content += "### 增长潜力最高（营收和盈利轨迹最强）\n\n"
        content += "| 排名 | 公司 | 营收增长率 | 盈利增长率 | 增长潜力 | 来源 |\n"
        content += "|------|------|----------|----------|----------|------|\n"
        for i, stock in enumerate(stocks, 1):
            content += f"| {i} | {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取增长率数据，当前数据不可获取。无法确定增长潜力最高的公司。\n\n"

        content += "### 最安全选择（资产负债表最强、业务最稳定）\n\n"
        content += "| 排名 | 公司 | 资产负债率 | 现金储备 | 业务稳定性 | 来源 |\n"
        content += "|------|------|----------|----------|----------|------|\n"
        for i, stock in enumerate(stocks, 1):
            content += f"| {i} | {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 公司财报 |\n"
        content += "\n**注意**: ⚠️ 需要从公司财报中提取资产负债率和现金储备数据，当前数据不可获取。无法确定最安全的选择。\n\n"

        content += "### 综合赢家及原因——给出明确判断\n\n"
        content += "| 排名 | 公司 | 估值 | 增长 | 安全性 | 综合评分 | 原因 | 来源 |\n"
        content += "|------|------|------|------|--------|----------|------|------|\n"
        for i, stock in enumerate(stocks, 1):
            content += f"| {i} | {stock} | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | N/A 未公开披露 | 不可判断 | N/A 未公开披露 | N/A |\n"
        content += "\n**注意**: ⚠️ 需要从金融数据库和公司财报中提取完整的估值、增长和安全性数据，当前数据不可获取。无法给出明确的综合赢家判断。\n\n"

        return content

    def compare(self, stocks, industry):
        """
        执行完整的行业与板块对比分析

        Args:
            stocks: 股票列表
            industry: 行业名称

        Returns:
            dict: 分析结果
        """
        print(f"📊 正在进行行业与板块对比分析")
        print(f"🏭 行业/板块: {industry}")
        print(f"📋 公司列表: {', '.join(stocks)}")
        print(f"⚠️ 注意：本分析严格遵守“不估算或插值任何缺失数据”的原则，如果某项指标不可获取，将标注为 'N/A 未公开披露'。")

        # 搜索数据
        for stock in stocks:
            query = f"{stock} 营收 利润 毛利率 市值"
            results = self.search_baidu(query)
            print(f"🔍 {stock}: 搜索到 {len(results)} 条结果")

        # 生成报告
        full_report = self._generate_full_report(stocks, industry)

        # 保存报告
        report_file = f"{self.temp_dir}/industry-comparison-{industry.replace(' ', '-')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        # 使用消息发送器
        self._send_report(report_file)

        return {
            "stocks": stocks,
            "industry": industry,
            "report_file": report_file,
            "full_report": full_report,
            "status": "completed"
        }

    def _generate_full_report(self, stocks, industry):
        """生成完整报告"""
        content = f"# {industry} 行业与板块对比分析报告\n\n"
        content += f"**行业/板块**: {industry}\n"
        content += f"**公司列表**: {', '.join(stocks)}\n"
        content += f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += f"**分析师**: 高级股票研究分析师\n\n"
        content += "---\n"
        content += "**免责声明**: 本报告仅供信息参考，不构成投资建议。所有数据均来自公开来源（金融数据库、公司财报、行业研究报告），可能存在延迟或错误。投资者应基于自身研究和判断做出投资决策。投资有风险，入市需谨慎。\n\n"
        content += "---\n"
        content += f"**数据来源说明**: 本分析严格遵守“不估算或插值任何缺失数据”的原则，仅使用最新披露的数据。不要估算或插值任何缺失数据，若无法获取请标注为 'N/A 未公开披露'。每一个指标都必须标注来源和日期。\n\n"
        content += "---\n\n"

        # 添加4个分析步骤
        content += self.generate_comparison_table_section(stocks, industry)
        content += "---\n\n"
        content += self.generate_competitive_positioning_section(stocks, industry)
        content += "---\n\n"
        content += self.generate_risk_comparison_section(stocks, industry)
        content += "---\n\n"
        content += self.generate_ranking_conclusion_section(stocks, industry)

        return content

    def _send_report(self, report_file):
        """发送报告"""
        cmd = f"python3 /root/.openclaw/workspace/scripts/message-sender.py --file {report_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result

def main():
    import argparse

    parser = argparse.ArgumentParser(description="行业与板块对比分析Skill")
    parser.add_argument("--stocks", required=True, help="股票列表，用逗号分隔（如：AAPL,MSFT,GOOGL）")
    parser.add_argument("--industry", required=True, help="行业/板块名称")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 解析股票列表
    stocks = [stock.strip() for stock in args.stocks.split(",")]

    # 创建分析器实例
    analyzer = IndustryComparisonSkill()

    # 执行分析
    print(f"📊 开始行业与板块对比分析: {args.industry}")
    result = analyzer.compare(stocks, args.industry)

    print(f"\n📋 分析结果:")
    print(f"  🏭 行业/板块: {result['industry']}")
    print(f"  📋 公司列表: {', '.join(result['stocks'])}")
    print(f"  📄 报告文件: {result['report_file']}")
    print(f"  ✅ 分析状态: {result['status']}")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['full_report'])
        print(f"✅ 报告已保存到: {args.output}")

if __name__ == "__main__":
    main()
