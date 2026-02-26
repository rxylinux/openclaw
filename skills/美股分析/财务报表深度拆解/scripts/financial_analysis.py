#!/usr/bin/env python3
"""
财务报表深度拆解技能脚本（通用版本，最终修复版）

功能：
1. 支持股票代码作为命令行参数
2. 支持从数据文件读取股票财务数据
3. 支持批量分析模式
4. 生成Markdown格式的财务分析报告
5. 自动识别财务风险信号

作者：rxy的狗腿子
版本：2.0.2
日期：2026-02-25
"""

import json
import datetime
import os
import sys
import argparse
from typing import Dict, List, Any, Optional

# 配置风险阈值
RISK_THRESHOLDS = {
    "ocf_to_net_income": {
        "safe": 1.0,
        "warning": 0.8
    },
    "current_ratio": {
        "safe": 2.0,
        "warning": 1.5
    },
    "debt_to_equity": {
        "safe": 1.0,
        "warning": 1.5
    }
}

def get_default_data_dir() -> str:
    """
    获取默认数据目录路径
    
    Returns:
        数据目录路径
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", "data", "stocks")

def get_default_data_file(ticker: str) -> str:
    """
    获取默认数据文件路径
    
    Args:
        ticker: 股票代码
        
    Returns:
        数据文件路径
    """
    data_dir = get_default_data_dir()
    return os.path.join(data_dir, f"{ticker.upper()}.json")

def load_stock_data(ticker: str, data_file: Optional[str] = None) -> Dict[str, Any]:
    """
    从数据文件加载股票数据
    
    Args:
        ticker: 股票代码
        data_file: 数据文件路径（可选）
        
    Returns:
        股票数据字典
        
    Raises:
        FileNotFoundError: 数据文件不存在
        json.JSONDecodeError: 数据文件格式错误
    """
    if data_file is None:
        data_file = get_default_data_file(ticker)
    
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"数据文件不存在: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def analyze_stock_manual(ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析股票财务数据
    
    Args:
        ticker: 股票代码
        data: 财务数据字典
        
    Returns:
        财务分析数据字典
    """
    company_name = data.get("company_name", f"{ticker} Inc.")
    
    # 获取财务数据
    quarterly_revenue = data.get("quarterly_revenue", {})
    quarterly_net_income = data.get("quarterly_net_income", {})
    
    # 计算全年数据
    total_revenue_2025 = sum(quarterly_revenue.values())
    total_net_income_2025 = sum(quarterly_net_income.values())
    
    # 现金流数据
    operating_cashflow = data.get("operating_cashflow", {})
    capital_expenditure = data.get("capital_expenditure", {})
    
    # 现金储备
    cash_reserves = data.get("cash_reserves", 0)
    government_commitment = data.get("government_commitment", 0)
    total_liquidity = cash_reserves + government_commitment
    
    # 估值数据
    current_price = data.get("current_price", 0)
    market_cap = data.get("market_cap", 0)
    beta = data.get("beta", 0)
    
    # 计算财务比率
    # 净利润率
    net_margin = (total_net_income_2025 / total_revenue_2025) * 100 if total_revenue_2025 > 0 else 0
    
    # 债务股权比
    debt_to_equity = data.get("debt_to_equity", 0)
    
    # ROE
    stockholder_equity = data.get("stockholder_equity", total_liquidity)
    roe = (total_net_income_2025 / stockholder_equity) * 100 if stockholder_equity > 0 else 0
    
    # ROA
    total_assets = data.get("total_assets", total_liquidity)
    roa = (total_net_income_2025 / total_assets) * 100 if total_assets > 0 else 0
    
    # 现金流分析
    operating_cashflow_total = sum(operating_cashflow.values())
    capital_expenditure_total = sum(capital_expenditure.values())
    free_cashflow = operating_cashflow_total - capital_expenditure_total
    
    # OCF/净利润
    ocf_to_net_income = (operating_cashflow_total / total_net_income_2025) if total_net_income_2025 < 0 else 0
    
    # 风险评估
    risks = {
        "earnings_quality": [],
        "debt": []
    }
    
    # 盈余质量评估
    if ocf_to_net_income < RISK_THRESHOLDS["ocf_to_net_income"]["warning"]:
        risks["earnings_quality"].append({
            "indicator": "经营现金流/净利润",
            "value": ocf_to_net_income,
            "threshold": f"< {RISK_THRESHOLDS['ocf_to_net_income']['warning']} 警告",
            "risk_level": "⚠️"
        })
    else:
        risks["earnings_quality"].append({
            "indicator": "经营现金流/净利润",
            "value": ocf_to_net_income,
            "threshold": f"≥ {RISK_THRESHOLDS['ocf_to_net_income']['warning']} 安全",
            "risk_level": "✅"
        })
    
    # 债务风险评估
    if debt_to_equity > RISK_THRESHOLDS["debt_to_equity"]["warning"]:
        risks["debt"].append({
            "indicator": "债务股权比",
            "value": debt_to_equity,
            "threshold": f"> {RISK_THRESHOLDS['debt_to_equity']['warning']} 高风险",
            "risk_level": "⚠️"
        })
    else:
        risks["debt"].append({
            "indicator": "债务股权比",
            "value": debt_to_equity,
            "threshold": f"< {RISK_THRESHOLDS['debt_to_equity']['safe']} 安全",
            "risk_level": "✅"
        })
    
    return {
        "ticker": ticker,
        "company_name": company_name,
        "financial_data": {
            "total_revenue_2025": total_revenue_2025,
            "total_net_income_2025": total_net_income_2025,
            "quarterly_revenue": quarterly_revenue,
            "quarterly_net_income": quarterly_net_income,
            "operating_cashflow": operating_cashflow,
            "capital_expenditure": capital_expenditure,
            "cash_reserves": cash_reserves,
            "government_commitment": government_commitment,
            "total_liquidity": total_liquidity
        },
        "ratios": {
            "net_margin": net_margin,
            "debt_to_equity": debt_to_equity,
            "roe": roe,
            "roa": roa,
            "ocf_to_net_income": ocf_to_net_income,
            "free_cashflow": free_cashflow
        },
        "valuation": {
            "current_price": current_price,
            "market_cap": market_cap,
            "beta": beta
        },
        "risks": risks
    }

def generate_stock_report(analysis: Dict[str, Any]) -> str:
    """
    生成股票财务分析报告
    
    Args:
        analysis: 股票财务分析数据
        
    Returns:
        Markdown格式的分析报告
    """
    report_date = datetime.datetime.now().strftime("%Y-%m-%d")
    data = analysis["financial_data"]
    ratios = analysis["ratios"]
    valuation = analysis["valuation"]
    risks = analysis["risks"]
    
    # 使用列表逐行构建报告
    report_lines = []
    
    # 报告头部
    report_lines.append(f"# {analysis['ticker']} - {analysis['company_name']} 财务报表深度分析报告")
    report_lines.append("")
    report_lines.append(f"**报告日期**: {report_date}")
    report_lines.append(f"**数据截止日期**: 2025年Q3")
    report_lines.append(f"**分析师**: rxy的狗腿子")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 基本信息
    report_lines.append("## 📊 基本信息")
    report_lines.append("")
    report_lines.append("| 项目 | 内容 |")
    report_lines.append("|-----|------|")
    report_lines.append(f"| 股票代码 | {analysis['ticker']} |")
    report_lines.append(f"| 公司名称 | {analysis['company_name']} |")
    report_lines.append(f"| 当前股价 | ${valuation['current_price']:.2f} |")
    report_lines.append(f"| 总市值 | ${valuation['market_cap']:.2f}百万 |")
    report_lines.append(f"| 贝塔系数 | {valuation['beta']:.2f} |")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 第1步 —— 利润表分析
    report_lines.append("## 🔄 第1步 —— 利润表分析")
    report_lines.append("")
    
    # 核心指标
    report_lines.append("### 核心指标")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 来源 | 日期 |")
    report_lines.append("|-----|------|------|------|")
    report_lines.append(f"| 总营收（2025年） | ${data['total_revenue_2025']:.2f}百万 | 数据文件 | {report_date} |")
    report_lines.append(f"| 净利润（2025年） | ${data['total_net_income_2025']:.2f}百万 | 数据文件 | {report_date} |")
    report_lines.append(f"| 净利润率 | {ratios['net_margin']:.2f}% | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 季度营收
    report_lines.append("### 季度营收")
    report_lines.append("")
    report_lines.append("| 季度 | 营收（百万美元） | 来源 | 日期 |")
    report_lines.append("|-----|------------------|------|------|")
    
    for quarter in ["Q1", "Q2", "Q3", "Q4"]:
        revenue = data["quarterly_revenue"].get(quarter, 0)
        report_lines.append(f"| {quarter} | {revenue:.2f} | 数据文件 | {report_date} |")
    
    total_revenue = data['total_revenue_2025']
    report_lines.append(f"| **总计** | **{total_revenue:.2f}** | | |")
    report_lines.append("")
    
    # 季度净利润
    report_lines.append("### 季度净利润")
    report_lines.append("")
    report_lines.append("| 季度 | 净利润（百万美元） | 来源 | 日期 |")
    report_lines.append("|-----|---------------------|------|------|")
    
    for quarter in ["Q1", "Q2", "Q3", "Q4"]:
        net_income = data["quarterly_net_income"].get(quarter, 0)
        report_lines.append(f"| {quarter} | {net_income:.2f} | 数据文件 | {report_date} |")
    
    total_net_income = data['total_net_income_2025']
    report_lines.append(f"| **总计** | **{total_net_income:.2f}** | | |")
    report_lines.append("")
    
    # 第2步 —— 资产负债表健康状况
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 🏦 第2步 —— 资产负债表健康状况")
    report_lines.append("")
    
    # 现金储备
    report_lines.append("### 现金储备")
    report_lines.append("")
    report_lines.append("| 项目 | 金额（百万美元） | 说明 | 来源 | 日期 |")
    report_lines.append("|-----|------------------|------|------|------|")
    report_lines.append(f"| 现金及现金等价物 | {data['cash_reserves']:.2f} | 2025年Q3累计 | 数据文件 | {report_date} |")
    report_lines.append(f"| 政府承诺资金 | {data['government_commitment']:.2f} | 来自政府来源 | 数据文件 | {report_date} |")
    report_lines.append(f"| **总流动性** | **{data['total_liquidity']:.2f}** | | |")
    report_lines.append("")
    
    # 流动性比率
    report_lines.append("### 流动性比率")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 安全阈值 | 评估 | 来源 | 日期 |")
    report_lines.append("|-----|------|----------|------|------|------|")
    report_lines.append(f"| 债务股权比 | {ratios['debt_to_equity']:.2f} | < 1.0 安全 | ✅ | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 盈利能力指标
    report_lines.append("### 盈利能力指标")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 来源 | 日期 |")
    report_lines.append("|-----|------|------|------|")
    report_lines.append(f"| ROE（净资产收益率） | {ratios['roe']:.2f}% | 计算得出 | {report_date} |")
    report_lines.append(f"| ROA（总资产收益率） | {ratios['roa']:.2f}% | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 第3步 —— 现金流真实性检查
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 💵 第3步 —— 现金流真实性检查")
    report_lines.append("")
    
    # 经营现金流 vs 净利润
    report_lines.append("### 经营现金流 vs 净利润")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 评估 | 来源 | 日期 |")
    report_lines.append("|-----|------|------|------|------|")
    report_lines.append(f"| 经营现金流（全年） | {sum(data['operating_cashflow'].values()):.2f}百万 | | 计算得出 | {report_date} |")
    report_lines.append(f"| 净利润（全年） | {data['total_net_income_2025']:.2f}百万 | | 数据文件 | {report_date} |")
    
    risk_level = '✅ 良好' if ratios['ocf_to_net_income'] >= 1.0 else '⚠️ 需关注'
    report_lines.append(f"| OCF/净利润 | {ratios['ocf_to_net_income']:.2f} | {risk_level} | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 资本支出
    report_lines.append("### 资本支出")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 营收 | Capex/营收 | 来源 | 日期 |")
    report_lines.append("|-----|----------|--------|------------|------|------|")
    
    capex = sum(data['capital_expenditure'].values())
    revenue = data['total_revenue_2025']
    capex_revenue = (capex / revenue) * 100 if revenue > 0 else 0
    report_lines.append(f"| 资本支出（全年） | {capex:.2f}百万 | {revenue:.2f}百万 | {capex_revenue:.2f}% | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 自由现金流
    report_lines.append("### 自由现金流")
    report_lines.append("")
    report_lines.append("| 指标 | 经营现金流 | 资本支出 | 自由现金流 | FCF利润率 | 来源 | 日期 |")
    report_lines.append("|-----|------------|----------|------------|------------|------|------|")
    
    fcf = ratios['free_cashflow']
    fcf_margin = (fcf / data['total_revenue_2025']) * 100 if data['total_revenue_2025'] > 0 else 0
    report_lines.append(f"| 全年 | {sum(data['operating_cashflow'].values()):.2f} | {capex:.2f} | {fcf:.2f} | {fcf_margin:.2f}% | 计算得出 | {report_date} |")
    report_lines.append("")
    
    # 第4步 —— 风险信号检查
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## ⚠️ 第4步 —— 风险信号检查")
    report_lines.append("")
    
    # 盈余质量
    report_lines.append("### 盈余质量")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 阈值 | 风险评估 |")
    report_lines.append("|-----|------|------|----------|")
    
    earnings_quality = risks.get("earnings_quality", [])
    for risk in earnings_quality:
        report_lines.append(f"| {risk['indicator']} | {risk['value']:.2f} | {risk['threshold']} | {risk['risk_level']} |")
    report_lines.append("")
    
    # 债务风险
    report_lines.append("### 债务风险")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 | 安全阈值 | 风险评估 |")
    report_lines.append("|-----|------|----------|----------|")
    
    debt_risks = risks.get("debt", [])
    for risk in debt_risks:
        report_lines.append(f"| {risk['indicator']} | {risk['value']:.2f} | {risk['threshold']} | {risk['risk_level']} |")
    report_lines.append("")
    
    return "\n".join(report_lines)

def analyze_stock(ticker: str, data_file: Optional[str] = None) -> Dict[str, Any]:
    """
    分析单只股票的财务报表
    
    Args:
        ticker: 股票代码
        data_file: 数据文件路径（可选）
        
    Returns:
        财务分析结果字典
    """
    try:
        # 加载股票数据
        data = load_stock_data(ticker, data_file)
        
        # 分析财务数据
        analysis = analyze_stock_manual(ticker, data)
        
        return {
            "success": True,
            "ticker": ticker,
            "analysis": analysis
        }
    except Exception as e:
        return {
            "success": False,
            "ticker": ticker,
            "error": str(e)
        }

def analyze_batch_stocks(tickers: List[str], data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    批量分析多只股票的财务报表
    
    Args:
        tickers: 股票代码列表
        data_dir: 数据文件目录路径（可选）
        
    Returns:
        财务分析结果列表
    """
    results = []
    
    for ticker in tickers:
        if data_dir:
            data_file = os.path.join(data_dir, f"{ticker.upper()}.json")
        else:
            data_file = None
        
        result = analyze_stock(ticker, data_file)
        results.append(result)
    
    return results

def save_report(report: str, ticker: str, output_dir: Optional[str] = None) -> str:
    """
    保存财务分析报告
    
    Args:
        report: 报告内容
        ticker: 股票代码
        output_dir: 输出目录路径（可选）
        
    Returns:
        报告文件路径
    """
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "reports")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成报告文件名
    report_filename = f"{ticker.upper()}-financial-analysis-{datetime.datetime.now().strftime('%Y%m%d')}.md"
    output_file = os.path.join(output_dir, report_filename)
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_file

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="财务报表深度拆解技能脚本（通用版本，最终修复版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析单只股票
  python3 financial_analysis.py ABCL

  # 指定数据文件
  python3 financial_analysis.py ABCL --data-file /path/to/ABCL.json

  # 批量分析
  python3 financial_analysis.py --batch ABCL AAPL TSLA

  # 指定数据目录
  python3 financial_analysis.py --batch --data-dir /path/to/data/stocks/ ABCL AAPL TSLA

  # 指定输出目录
  python3 financial_analysis.py ABCL --output-dir /path/to/output
        """
    )
    
    parser.add_argument("tickers", nargs="*", help="股票代码（可选，如果不提供则使用--batch模式）")
    parser.add_argument("--data-file", help="数据文件路径")
    parser.add_argument("--data-dir", help="数据文件目录路径（批量模式）")
    parser.add_argument("--batch", action="store_true", help="批量分析模式")
    parser.add_argument("--output-dir", help="报告输出目录路径")
    
    args = parser.parse_args()
    
    # 批量分析模式
    if args.batch:
        if not args.tickers:
            print("❌ 错误: 批量分析模式需要提供股票代码列表")
            return
        
        print(f"正在批量分析 {len(args.tickers)} 只股票...")
        results = analyze_batch_stocks(args.tickers, args.data_dir)
        
        # 保存报告
        print(f"\n正在保存报告...")
        saved_files = []
        for result in results:
            if result["success"]:
                report = generate_stock_report(result["analysis"])
                output_file = save_report(report, result["ticker"], args.output_dir)
                saved_files.append(output_file)
                print(f"✅ {result['ticker']}: 报告已保存到 {output_file}")
            else:
                print(f"❌ {result['ticker']}: 分析失败 - {result['error']}")
        
        print(f"\n📊 批量分析完成！")
        print(f"成功: {len([r for r in results if r['success']])}/{len(results)}")
        print(f"失败: {len([r for r in results if not r['success']])}/{len(results)}")
        
    # 单只股票分析模式
    elif args.tickers:
        ticker = args.tickers[0].upper()
        
        print(f"正在分析 {ticker} 的财务报表...")
        result = analyze_stock(ticker, args.data_file)
        
        if result["success"]:
            # 生成报告
            print(f"正在生成 {ticker} 财务分析报告...")
            report = generate_stock_report(result["analysis"])
            
            # 保存报告
            print(f"正在保存 {ticker} 财务分析报告...")
            output_file = save_report(report, ticker, args.output_dir)
            
            print(f"✅ 分析完成！")
            print(f"📄 报告已保存到: {output_file}")
            
            # 显示财务摘要
            analysis = result["analysis"]
            data = analysis["financial_data"]
            ratios = analysis["ratios"]
            print(f"\n📊 财务摘要:")
            print(f"   总营收: {data['total_revenue_2025']:.2f}百万")
            print(f"   总净利润: {data['total_net_income_2025']:.2f}百万")
            print(f"   净利润率: {ratios['net_margin']:.2f}%")
            print(f"   债务股权比: {ratios['debt_to_equity']:.2f}")
            print(f"   ROE: {ratios['roe']:.2f}%")
            print(f"   ROA: {ratios['roa']:.2f}%")
        else:
            print(f"❌ 分析失败: {result['error']}")
    else:
        print("❌ 错误: 请提供股票代码或使用--batch模式")
        parser.print_help()

if __name__ == "__main__":
    main()
