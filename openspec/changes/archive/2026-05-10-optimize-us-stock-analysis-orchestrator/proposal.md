# Proposal: 优化美股多技能综合分析总控

## Why

`us-stock-analysis-orchestrator` 已能串联多个美股分析 skill，但仍有三个维护性问题：

- 总控正文包含完整输出模板，占用不必要上下文。
- 子模块之间缺少明确输入输出契约，容易生成松散、重复或冲突的模块发现。
- 校验逻辑目前依赖临时脚本，不能稳定复用。

## What Changes

- 将总控报告模板拆到 `assets/orchestrator-report-template.md`。
- 新增 `references/module-io-contract.md`，定义核心模块、条件模块、字段要求和冲突优先级。
- 更新 `SKILL.md`，保留核心流程，增加条件模块选择规则，并引用模板和契约文件。
- 新增 `scripts/validate-skills.py`，固化 skill frontmatter、链接、包结构和源码/包一致性校验。
- 重新打包 `us-stock-analysis-orchestrator.skill`。

## Impact

- 不新增运行时 API。
- 不重命名已有 skill name 或 `.skill` 包名。
- 影响范围限于 `skills/美股分析` 与 OpenSpec 文档。
- 风险闸门：无接口兼容性、并发、安全、性能敏感路径风险。
