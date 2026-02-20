# 科技新闻推送

当收到心跳消息时：
1. 每天早上8点和晚上8点检查是否到了推送时间
2. 如果到了时间：
   a. 运行 `python3 /root/.openclaw/workspace/scripts/tech-news.py` 生成新闻
   b. 运行 `python3 /root/.openclaw/workspace/scripts/heartbeat-helper.py` 自动拆分消息
   c. 读取 `/root/.openclaw/workspace/temp/news-split-index.json` 的拆分索引文件
   d. 根据拆分索引中的文件列表，逐条读取消息内容
   e. 通过飞书逐条推送所有消息
3. 保存上次推送时间到 `/root/.openclaw/workspace/memory/heartbeat-state.json`
