# 定时任务执行

当收到心跳消息时：

## 任务 1：科技新闻推送 ⚡ 改为Cron执行

**已配置Cron任务，每天8:00和20:00准时推送，不再依赖心跳检查。**

Cron任务详情：
```cron
# 科技新闻推送 - 每天8点和20点
0 8 * * * /root/.openclaw/workspace/scripts/push-tech-news.sh >> /root/.openclaw/logs/cron-news.log 2>&1
0 20 * * * /root/.openclaw/workspace/scripts/push-tech-news.sh >> /root/.openclaw/logs/cron-news.log 2>&1
```

**心跳任务：检查推送状态**
1. 每次心跳检查 `/root/.openclaw/workspace/memory/heartbeat-state.json`
2. 如果 `last_push_time` 距离当前时间超过24小时，发送预警消息
3. 如果推送失败（status != completed），发送告警消息

---

## 任务 2：投资随想复盘

1. 每周日晚上 8 点检查是否到了复盘时间
2. 如果到了时间：
   a. 提醒用户：`investment-thought-journal` 目录已被删除
   b. 询问是否需要重新创建复盘框架
   c. 如果用户确认，创建新的复盘框架
   d. 通过飞书推送复盘报告
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
   a. 提醒用户：`investment-thought-journal` 目录已被删除
   b. 询问是否需要重新创建评估框架
   c. 如果用户确认，创建新的评估框架
   d. 通过飞书推送评估报告
3. 保存上次评估时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`

---

## 状态管理

### 心跳状态文件

```json
{
  "last_push_time": "2026-02-27T12:00:00Z",
  "last_check_time": "2026-02-27T12:11:00Z",
  "last_review_time": "2026-02-21T20:00:00Z",
  "last_analysis_time": "2026-02-28T20:00:00Z",
  "last_evaluation_time": "2026-03-31T20:00:00Z",
  "news_sent_count": 12,
  "source": "latest-news-index.json",
  "status": "completed",
  "use_cron": true
}
```

---

## 优先级

### 高优先级
- ~~科技新闻推送（每天 2 次）~~ ✅ 已改为Cron自动执行
- 科技新闻状态监控（每次心跳检查推送状态）
- 投资随想复盘（每周 1 次）

### 中优先级
- 投资组合分析（每月 1 次）

### 低优先级
- 策略有效性评估（每季度 1 次）

---

## Cron任务管理

### 查看当前Cron任务
```bash
crontab -l
```

### 编辑Cron任务
```bash
crontab -e
```

### 查看Cron日志
```bash
tail -f /root/.openclaw/logs/cron-news.log
```

### 手动测试推送脚本
```bash
/root/.openclaw/workspace/scripts/push-tech-news.sh
```
