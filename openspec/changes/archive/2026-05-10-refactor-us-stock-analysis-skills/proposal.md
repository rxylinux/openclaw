## Why

美股分析技能集目前存在源码与 `.skill` 包不一致、重复嵌套目录、断链模板、过长 frontmatter description、示例产物混入正式技能目录等问题。这会增加维护成本，也会诱导代理在未读取完整技能正文时按过长摘要执行。

## What Changes

- 清理无效产物：重复嵌套 skill、副本备份、空目录、`.DS_Store`、ABCL 示例数据/报告和不可靠脚本。
- 修订 10 个 `SKILL.md` 的 frontmatter，使 `description` 只描述触发条件并保持简短。
- 补齐估值模型和股息分析缺失的报告模板资产。
- 修正文案与断链：`激ss指标`、`晨光 / EPFR`、`dcfc-methodology.md`、`soty-catalysts.md`。
- 更新根 `README.md` 和 `detail-prompt.md`，让文档反映当前技能集结构。
- 重新生成 10 个 `.skill` 打包文件，确保包内内容与源码目录一致。

## Capabilities

### New Capabilities
- `skill-bundle-quality`: 约束美股分析技能集的源码结构、触发元数据、引用完整性、交付包一致性和数据真实性防护。

### Modified Capabilities

无。当前仓库没有既有 OpenSpec specs，本次为技能集维护质量新增规范。

## Impact

- Affected code: `skills/美股分析` 下 10 个 skill 源目录、根文档和对应 `.skill` 包。
- APIs: 不新增运行时 API；skill name 和 `.skill` 包名保持不变。
- Dependencies: 不新增外部依赖；使用系统 `zip`/`unzip` 完成打包验证。
