# SEC 文件解读指南

## SEC 文件概述

### 常用文件类型

| 文件类型 | 全称 | 用途 | 更新频率 |
|---------|------|------|----------|
| 10-K | Annual Report | 年度财报 | 每年一次 |
| 10-Q | Quarterly Report | 季度财报 | 每季度一次 |
| 8-K | Current Report | 重大事件披露 | 不定期 |
| Form 4 | Statement of Changes in Beneficial Ownership | 内部人买卖 | 交易后 2 日内 |
| 13F | Information Required of Institutional Investment Managers | 机构持仓 | 每季度 |
| S-1 | Registration Statement | 上市申请 | 上市时 |
| 20-F | Registration of Foreign Private Issuer | 外国公司年度报告 | 每年一次 |

### 查询平台

- **SEC EDGAR**: https://www.sec.gov/edgar/search/
- **Bloomberg**: 专业数据库
- **FactSet**: 专业数据库
- **Morningstar**: 投资研究平台

---

## 10-K 年度财报

### 文件结构

```
Part I - 基本信息与风险
Item 1. Business（业务描述）
Item 1A. Risk Factors（风险因素）
Item 1B. Unresolved Staff Comments（员工意见）
Item 1C. Cybersecurity（网络安全）
Item 2. Properties（物业）
Item 3. Legal Proceedings（法律诉讼）
Item 4. Mine Safety Disclosures（矿山安全披露）

Part II - 市场数据与财务报表
Item 5. Market for Registrant's Common Equity（股票市场数据）
Item 6. Selected Financial Data（精选财务数据）
Item 7. Management's Discussion and Analysis (MD&A)（管理层讨论与分析）
Item 7A. Quantitative and Qualitative Disclosures About Market Risk（市场风险披露）
Item 8. Financial Statements and Supplementary Data（财务报表）
Item 9. Changes in and Disagreements With Accountants（会计师变更）

Part III - 公司治理
Item 10. Directors and Executive Officers（董事和高管）
Item 11. Executive Compensation（高管薪酬）
Item 12. Security Ownership of Certain Beneficial Owners（股权结构）
Item 13. Certain Relationships and Related Transactions（关联交易）
Item 14. Principal Accountant Fees and Services（审计师费用）

Part IV - 其他
Item 15. Exhibits, Financial Statement Schedules（附件）
```

### 关键部分解读

#### Item 1. Business（业务描述）

**内容：**
- 公司主要业务
- 产品和服务
- 主要市场
- 竞争环境
- 季节性因素

**关键信息：**
- 产品/服务组合
- 客户集中度（如披露）
- 地域分布
- 竞争对手

**风险分析用途：**
- 业务集中度风险
- 竞争威胁分析

---

#### Item 1A. Risk Factors（风险因素）

**内容：**
- 公司面临的主要风险
- 行业风险
- 监管风险
- 财务风险

**关键风险类型：**
- 市场风险
- 信贷风险
- 流动性风险
- 操作风险
- 合规风险
- 竞争风险
- 监管风险

**风险分析用途：**
- 识别公司自身披露的风险
- 与实际数据对比验证
- 发现潜在隐性风险

---

#### Item 3. Legal Proceedings（法律诉讼）

**内容：**
- 正在进行的主要诉讼
- 诉讼类型（民事、刑事、监管）
- 诉讼金额（如有披露）
- 诉讼状态

**关键信息：**
- 重大诉讼列表
- 潜在赔偿金额
- 诉讼进展

**风险分析用途：**
- 法律风险评估
- 潜在赔偿风险

---

#### Item 7. MD&A（管理层讨论与分析）

**内容：**
- 经营业绩分析
- 财务状况分析
- 流动性和资本资源
- 表外安排
- 合同义务
- 关键会计政策

**关键部分：**

**Results of Operations（经营业绩）**
- 收入分析
- 毛利率分析
- 营业费用分析
- 税收分析
- 每股收益分析

**Liquidity and Capital Resources（流动性和资本资源）**
- 现金来源
- 资本支出
- 债务情况
- 合同义务

**Contractual Obligations（合同义务）**
- 未来付款义务时间表
- 长期债务到期时间表

**Off-Balance Sheet Arrangements（表外安排）**
- 特殊目的实体
- 担保义务

**Critical Accounting Estimates（关键会计估计）**
- 会计政策和估计
- 不确定性来源

**风险分析用途：**
- 财务健康分析
- 债务到期分析
- 会计质量分析
- 现金流分析

---

#### Item 7A. Market Risk（市场风险）

**内容：**
- 利率风险
- 外汇风险
- 商品价格风险
- 权益价格风险

**关键信息：**
- 敏感性分析
- 对冲策略
- 风险暴露

**风险分析用途：**
- 宏观敏感度分析
- 利率敏感度
- 汇率风险

---

#### Item 8. Financial Statements（财务报表）

**内容：**
- 资产负债表
- 损益表
- 现金流量表
- 股东权益表
- 财务报表附注

**关键附注：**
- Note 1: Summary of Significant Accounting Policies（重要会计政策汇总）
- Note 2: Revenue Recognition（收入确认政策）
- Note 3: Debt（债务详情）
- Note 4: Derivative Instruments（衍生工具）
- Note 5: Fair Value Measurements（公允价值计量）

**风险分析用途：**
- 财务健康分析
- 债务分析
- 会计质量分析
- 会计变更分析

---

## 10-Q 季度财报

### 文件结构

```
Part I - 财务信息
Item 1. Financial Statements（财务报表）
Item 2. Management's Discussion and Analysis (MD&A)（管理层讨论与分析）
Item 3. Quantitative and Qualitative Disclosures About Market Risk（市场风险）
Item 4. Controls and Procedures（内部控制）

Part II - 其他信息
Item 1. Legal Proceedings（法律诉讼）
Item 1A. Risk Factors（风险因素，如更新）
Item 2. Unregistered Sales of Equity Securities（未注册证券销售）
Item 3. Defaults Upon Senior Securities（证券违约）
Item 4. Mine Safety Disclosures（矿山安全披露）
Item 5. Other Information（其他信息）
Item 6. Exhibits（附件）
```

### 与 10-K 的区别

| 项目 | 10-K | 10-Q |
|------|------|------|
| 更新频率 | 每年 | 每季度 |
| 审计 | 已审计 | 未审计 |
| 风险因素 | 完整 | 仅更新部分 |
| 业务描述 | 详细 | 简化 |
| 财务数据 | 5 年 | 当季 + 去年同期 |

### 关键信息提取

**最新财务数据：**
- 收入
- 净利润
- 自由现金流
- 债务水平
- 现金及等价物

**季度趋势：**
- 季度环比变化
- 同比变化
- 利润率变化

**风险分析用途：**
- 财务健康趋势
- 现金流趋势
- 债务变化

---

## Form 4 内部人交易

### 文件内容

**披露信息：**
- 内部人姓名
- 职位
- 交易日期
- 交易类型（买入/卖出）
- 交易价格
- 交易股数
- 交易后持股数

### 内部人类型

| 类型 | 说明 |
|------|------|
| Director | 董事 |
| Officer | 高管（CEO、CFO、CTO 等） |
| 10% Owner | 10%以上大股东 |

### 交易类型

| 代码 | 说明 |
|------|------|
| P | Purchase（买入） |
| S | Sale（卖出） |
| A | Grant/Award（授予/奖励） |
| F | Tax Withholding（税收代扣） |
| C | Conversion（转换） |
| E | Expired（过期） |
| H | Expiration of short position（空头头寸过期） |
| I | Discretionary transaction（自主交易） |
| M | Exercise（行权） |
| O | Exercise of out-of-the-money option（价外期权行权） |
| X | Exercise of in-the-money option（价内期权行权） |

### 分析要点

**净买入/卖出：**
- 净买入：买入 > 卖出 → 积极信号
- 净卖出：卖出 > 买入 → 消极信号

**交易频率：**
- 频繁交易 → 关注
- 稀疏交易 → 信号较弱

**买入/卖出比例：**
- > 3:1 → 强烈积极信号
- 1:3 或更低 → 强烈消极信号

**期权行权：**
- 期权行权后卖出 → 正常行为，非利空
- 直接现金买入 → 强烈积极信号

**集中度：**
- 多位高管同时卖出 → 高度关注
- 单一高管少量卖出 → 信号较弱

### 数据来源

- **SEC EDGAR**: https://www.sec.gov/edgar/search/
- **Bloomberg**: Insider Trading 数据
- **Yahoo Finance**: Insider Trading 页面

---

## 13F 机构持仓

### 文件内容

**披露信息：**
- 管理人名称
- 报告日期
- 持仓证券列表
- 持股数量
- 持仓市值

### 报告时间

- **Q1**: 4 月 15 日前
- **Q2**: 7 月 15 日前
- **Q3**: 10 月 15 日前
- **Q4**: 次年 1 月 15 日前

### 关键信息提取

**机构类型：**
- Mutual Funds（共同基金）
- Hedge Funds（对冲基金）
- Pension Funds（养老基金）
- ETF Providers（ETF 提供商）
- Bank Trust Departments（银行信托部）

**知名机构：**
- Vanguard
- BlackRock
- Fidelity
- State Street
- J.P. Morgan
- Wellington Management
- Capital Group

### 分析要点

**持仓变化：**
- 净流入/流出
- 流入/流出机构数量
- 知名机构动向

**持股占比：**
- 机构总持股占比
- 前 5 大机构占比

**趋势分析：**
- 连续 2 季度以上流入 → 积极信号
- 连续 2 季度以上流出 → 消极信号

### 数据来源

- **SEC EDGAR**: https://www.sec.gov/edgar/search/
- **WhaleWisdom**: 13F 聚合网站
- **Bloomberg**: 13F 数据
- **Dataroma**: 知名投资者跟踪

---

## 8-K 重大事件披露

### 披露类型

| 代码 | 披露类型 | 说明 |
|------|---------|------|
| 1.01 | Entry into a Material Definitive Agreement | 签订重大协议 |
| 1.02 | Termination of a Material Definitive Agreement | 终止重大协议 |
| 2.01 | Completion of Acquisition or Disposition of Assets | 完成收购或处置资产 |
| 2.02 | Results of Operations and Financial Condition | 经营业绩和财务状况 |
| 2.03 | Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement | 创造直接财务义务 |
| 2.04 | Triggering Events That Accelerate or Increase a Direct Financial Obligation | 触发财务义务的事件 |
| 2.05 | Costs Associated with Exit or Disposal Activities | 退出或处置活动的成本 |
| 2.06 | Material Impairments | 重大减值 |
| 3.01 | Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard | 退市通知 |
| 3.02 | Unregistered Sales of Equity Securities | 未注册证券销售 |
| 3.03 | Material Modification to Rights of Security Holders | 证券持有人权利的重大修改 |
| 4.01 | Changes in Registrant's Certified Accountant | 注册会计师变更 |
| 5.01 | Changes in Control of Registrant | 公司控制权变更 |
| 5.02 | Departure of Directors or Certain Officers | 董事或高管离职 |
| 5.03 | Amendments to Articles of Incorporation or Bylaws | 章程修改 |
| 5.07 | Submission of Matters to a Vote of Security Holders | 提交股东投票事项 |
| 5.08 | Shareholder Director Nominations | 股东提名董事 |
| 7.01 | Regulation FD Disclosure | 规范 FD 披露 |
| 8.01 | Other Events | 其他事件 |
| 9.01 | Financial Statements and Exhibits | 财务报表和附件 |

### 关键 8-K 类型

**2.02 - 经营业绩：**
- 季度/年度财报发布
- 业绩指引更新
- 重大业绩变动

**2.05 - 重组成本：**
- 裁员公告
- 业务重组
- 关闭工厂/办公室

**2.06 - 重大减值：**
- 资产减值
- 商誉减值
- 无形资产减值

**5.02 - 高管离职：**
- CEO、CFO 等关键高管离职
- 董事会成员离职

**8.01 - 其他事件：**
- 收购/合并
- 战略合作
- 重大诉讼

### 风险分析用途

- 识别重大事件
- 跟踪高管离职
- 监控业绩变动
- 发现重组或减值信号

---

## 文件交叉验证

### 10-K vs 10-Q

**验证项目：**
- 财务数据一致性
- 会计政策一致性
- 风险因素更新
- 债务到期时间表

### Form 4 vs 13F

**验证项目：**
- 内部人交易趋势
- 机构持仓变化
- 买卖方向一致性

### 10-K vs 8-K

**验证项目：**
- 重大事件是否披露
- 诉讼是否更新
- 风险因素是否调整

---

## 查询技巧

### SEC EDGAR 搜索

**基本搜索：**
- 公司名称
- 股票代码 (CIK)
- 文件类型

**高级搜索：**
- 时间范围
- 文件类型过滤
- 关键词搜索

### 数据提取

**自动提取工具：**
- SEC API
- Bloomberg API
- Python 库（sec-edgar-downloader）

**手动提取：**
- 下载文件
- 搜索关键词
- 提取关键数据

---

## 常见问题

### 如何快速定位关键信息？

**10-K 关键部分：**
- Business: Item 1
- Risk Factors: Item 1A
- Legal Proceedings: Item 3
- MD&A: Item 7
- Financial Statements: Item 8

### 如何判断文件重要性？

**优先级：**
1. 10-K（年度）
2. 10-Q（季度）
3. 8-K（重大事件）
4. Form 4（内部人交易）
5. 13F（机构持仓）

### 如何验证数据准确性？

- **交叉验证：** 多个文件对比
- **时间序列：** 历史数据对比
- **第三方验证：** Bloomberg、FactSet 等

---

## 注意事项

### 时效性

- 10-K: 财年结束后 60 天
- 10-Q: 季度结束后 40 天
- Form 4: 交易后 2 个工作日
- 13F: 季度结束后 45 天

### 准确性

- 审计财务报表最可靠
- MD&A 包含管理层观点
- 风险因素可能夸大

### 完整性

- 并非所有风险都会在风险因素中披露
- 重大事件可能延迟披露
- 部分信息可能省略
