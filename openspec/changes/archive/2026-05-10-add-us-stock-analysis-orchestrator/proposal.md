## Why

用户希望把“多技能综合分析同一家公司”的方案 3 固化为一个可直接触发的总控 skill，避免每次手动粘贴多个 skill 的调用路径和输出要求。

## What Changes

- 新增 `us-stock-analysis-orchestrator` skill，作为美股多技能综合分析总控。
- 总控 skill 固化 7 个子技能的调用路径：公司概览、财报解读、财务报表、行业对比、估值、风险、宏观。
- 总控 skill 规定统一输出结构：一页结论、关键数据表、模块发现、估值区间、最大风险、90 天催化剂和买/持有/回避结论。
- 更新美股分析 README 和历史提示词索引。
- 生成对应 `.skill` 包。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `skill-bundle-quality`: 增加对总控编排型 skill 的维护要求。

## Impact

- Affected code: `skills/美股分析/多技能综合分析总控/us-stock-analysis-orchestrator`、`skills/美股分析/README.md`、`skills/美股分析/detail-prompt.md`、对应 `.skill` 包。
- APIs: 新增 skill name `us-stock-analysis-orchestrator`；不修改既有 skill name。
- Dependencies: 不新增外部依赖。
