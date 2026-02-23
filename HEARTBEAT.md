# 定时任务执行

当收到心跳消息时：

## 任务 1：科技新闻推送

1. 每天早上 8 点和晚上 8 点检查是否到了推送时间
2. 如果到了时间：
   a. 运行 `python3 /root/.openclaw/workspace/scripts/tech-news.py` 生成新闻
   b. 运行 `python3 /root/.openclaw/workspace/scripts/heartbeat-helper.py` 自动拆分消息
   c. 读取 `/root/.openclaw/workspace/temp/news-split-index.json` 的拆分索引文件
   d. 根据拆分索引中的文件列表，逐条读取消息内容
   e. 通过飞书逐条推送所有消息
3. 保存上次推送时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`

---

## 任务 2：投资随想复盘

1. 每周日晚上 8 点检查是否到了复盘时间
2. 如果到了时间：
   a. 读取 `/root/.openclaw/workspace/investment-thought-journal/` 目录
   b. 查询 `/root/.openclaw/workspace/investment-thought-journal/交易记录/` 中的最新交易
   c. 读取 `/root/.openclaw/workspace/investment-thought-journal/洞察总结/季度复盘.md` 的复盘框架
   d. 生成本周投资复盘报告：
      - 交易表现总结
      - 投资逻辑验证
      - 经验教训提取
      - 策略效果评估
   e. 通过飞书推送复盘报告
3. 保存上次复盘时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`

---

## 任务 3：投资组合分析

1. 每月最后一天检查是否到了分析时间
2. 如果到了时间：
   a. 读取 `/root/.openclaw/workspace/stocks-analysis/` 或投资组合数据
   b. 生成投资组合分析报告：
      - 整体收益统计
      - 资产配置分析
      - 风险指标计算
      - 与基准对比
      - 优化建议
   c. 通过飞书推送分析报告
3. 保存上次分析时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`

---

## 任务 4：策略有效性评估

1. 每季度最后一天检查是否到了评估时间
2. 如果到了时间：
   a. 读取 `/root/.openclaw/workspace/investment-thought-journal/` 目录
   b. 生成策略有效性评估报告：
      - 各策略表现统计
      - 成功率分析
      - 风险收益比评估
      - 适用性分析
      - 优化建议
   c. 通过飞书推送评估报告
3. 保存上次评估时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`

---

## 状态管理

### 心跳状态文件

```json
{
  "last_push_time": "2026-02-21T08:00:00Z",
  "last_check_time": "2026-02-21T08:00:00Z",
  "last_review_time": "2026-02-21T20:00:00Z",
  "last_analysis_time": "2026-02-28T20:00:00Z",
  "last_evaluation_time": "2026-03-31T20:00:00Z",
  "news_sent_count": 3,
  "source": "latest-news-index.json",
  "status": "completed"
}
```


## 优先级

### 高优先级
- 科技新闻推送（每天 2 次）
- 投资随想复盘（每周 1 次）

### 中优先级
- 投资组合分析（每月 1 次）

### 低优先级
- 策略有效性评估（每季度 1 次）
