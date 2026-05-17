# 美股分析技能集

这是一个面向美股研究、估值、财报解读、风险扫描、ETF/组合分析和宏观判断的 Codex skill 集合。每个技能目录包含一个必需的 `SKILL.md`，可选的 `references/` 和 `assets/`，并在同级保留对应 `.skill` 打包文件。

## 技能目录

| 技能 | 源目录 | 用途 |
|------|--------|------|
| 完整股票拆解分析 | `完整股票拆解分析/complete-stock-analysis` | 个股完整概览、财务、股价、分析师预期和机构持仓 |
| 财务报表深度拆解 | `财务报表深度拆解/financial-statement-deep-dive` | 利润表、资产负债表、现金流和会计质量分析 |
| 财报解读分析器 | `财报解读分析器/earnings-call-analyzer` | 最新财报、电话会议、管理层指引和市场反应 |
| 行业与板块对比分析 | `行业与板块对比分析/industry-comparison-analyzer` | 2-5 家公司同行对比、竞争壁垒和综合排名 |
| 估值模型构建器 | `估值模型构建器/valuation-model-builder` | DCF、WACC、可比公司估值、历史估值和情景分析 |
| 股息与被动收入分析器 | `股息与被动收入分析器/dividend-income-analyzer` | 股息率、增长记录、派息安全性和收入预测 |
| 风险与红旗扫描器 | `风险与红旗扫描器/risk-flag-scanner` | 财务、会计、监管、做空、内部人和宏观敏感度风险 |
| ETF 与投资组合分析器 | `ETF与投资组合分析器/etf-portfolio-analyzer` | ETF/组合配置、重叠、风险、费用、收益和压力测试 |
| 宏观与市场情绪扫描器 | `宏观与市场情绪扫描器/macro-market-scanner` | 利率、通胀、经济数据、市场情绪、板块轮动和事件日历 |
| 完整尽职调查报告 | `完整尽职调查报告/comprehensive-due-diligence` | 整合多项分析生成完整投资研究报告 |
| 多技能综合分析总控 | `多技能综合分析总控/us-stock-analysis-orchestrator` | 编排多个分析 skill，对同一家公司输出一份综合投资判断 |

## 维护规则

- `SKILL.md` frontmatter 只保留触发元数据：`name` 和简短 `description`。
- `description` 必须以 `Use when` 开头，只描述何时触发，不总结完整流程。
- 每个事实数据要求来源和日期；不可得数据必须明确标注，不得编造。
- 前瞻性陈述、目标价、概率、增长率、折现率等假设必须标注 `[ASSUMPTION]` 并说明依据。
- 长解释放在 `references/`；可复用输出骨架放在 `assets/`；不要把示例报告、临时数据或备份文件混入技能源目录。
- 修改源码目录后，同步重新生成同级 `.skill` 包。
- 修改后运行 `python3 scripts/validate-skills.py`，确认源码、链接和 `.skill` 包一致。

## 打包约定

每个 `.skill` 包只包含对应的英文 skill 源目录，例如：

```bash
cd 完整股票拆解分析
zip -r complete-stock-analysis.skill complete-stock-analysis -x '*/.DS_Store'
```

包名保持不变，避免已有安装引用失效。

## 免责声明

这些技能用于研究和教育，不构成投资建议。输出中的评级、目标价和情景分析必须基于可追溯数据和显式假设，最终投资决策由使用者自行承担。
