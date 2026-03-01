#!/bin/bash
# Context Manager 功能演示脚本

echo "======================================"
echo "  Context Manager 功能演示"
echo "======================================"
echo ""

# 设置工作目录
cd /root/.openclaw/workspace

echo "📋 任务 1: 场景检测"
echo "--------------------------------------"
echo ""
echo "测试消息: '帮我分析一下苹果公司的股票'"
python3 scripts/context-manager.py detect "帮我分析一下苹果公司的股票"
echo ""

echo "测试消息: '帮我写一个Python脚本处理数据'"
python3 scripts/context-manager.py detect "帮我写一个Python脚本处理数据"
echo ""

echo "测试消息: '今天有什么新闻'"
python3 scripts/context-manager.py detect "今天有什么新闻"
echo ""

echo "======================================"
echo ""
echo "📋 任务 2: 获取场景文件"
echo "--------------------------------------"
echo ""
echo "场景: investment_analysis"
python3 scripts/context-manager.py files investment_analysis
echo ""

echo "======================================"
echo ""
echo "📋 任务 3: 场景摘要"
echo "--------------------------------------"
echo ""
echo "场景: investment_analysis"
python3 scripts/context-manager.py summary investment_analysis
echo ""

echo "======================================"
echo ""
echo "📋 任务 4: 自动上下文加载"
echo "--------------------------------------"
echo ""
echo "测试消息: '帮我分析特斯拉的财报'"
python3 scripts/auto-context-loader.py "帮我分析特斯拉的财报"
echo ""

echo "======================================"
echo ""
echo "📋 任务 5: 使用报告"
echo "--------------------------------------"
echo ""
python3 scripts/context-manager.py report
echo ""

echo "======================================"
echo ""
echo "✅ 演示完成"
echo ""
echo "更多功能请查看文档: docs/context-manager-guide.md"
echo "======================================"
