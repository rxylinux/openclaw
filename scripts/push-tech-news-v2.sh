#!/bin/bash

# 科技新闻推送脚本 V2
# 由cron定时调用，确保准时推送
# 使用Python直接处理消息发送，避免命令行工具问题

cd /root/.openclaw/workspace

# 运行新闻生成脚本
python3 /root/.openclaw/workspace/scripts/tech-news.py

# 检查是否成功生成
INDEX_FILE="/root/.openclaw/workspace/temp/latest-news-index.json"
if [ -f "$INDEX_FILE" ]; then
    # 检查文件时间戳，如果太旧（超过25小时）就不推送
    FILE_AGE=$(( ($(date +%s) - $(stat -c %Y "$INDEX_FILE")) / 3600 ))
    if [ $FILE_AGE -gt 25 ]; then
        echo "索引文件已过期（${FILE_AGE}小时前），跳过推送"
        exit 0
    fi

    # 使用Python脚本直接发送消息
    python3 /root/.openclaw/workspace/scripts/send-tech-news.py

    if [ $? -eq 0 ]; then
        echo "科技新闻推送完成 - $(date)"
    else
        echo "科技新闻推送失败 - $(date)"
        exit 1
    fi
else
    echo "新闻生成失败，未找到索引文件"
    exit 1
fi
