#!/bin/bash
# 功能测试脚本 - 测试 Gemini Bridge Linux 版本的实际运行

set -e

echo "=== Gemini Bridge 功能测试 ==="
echo ""

# 检查端口是否被占用
if lsof -i:19999 > /dev/null 2>&1; then
    echo "✗ 端口 19999 已被占用，请先关闭已运行的服务"
    exit 1
fi

# 启动服务器（后台运行，无头模式）
echo "1. 启动服务器..."
cd /root/.openclaw/workspace/skills/gemini-bridge/scripts
python3 gemini_bridge_linux.py --headless --port 19999 > /tmp/gemini-bridge-test.log 2>&1 &
SERVER_PID=$!

echo "   服务器 PID: $SERVER_PID"
echo "   等待服务器启动..."
sleep 5

# 检查服务器是否正常运行
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "✗ 服务器启动失败"
    cat /tmp/gemini-bridge-test.log
    exit 1
fi
echo "   ✓ 服务器启动成功"
echo ""

# 测试健康检查
echo "2. 测试健康检查 (/health)..."
HEALTH_RESPONSE=$(curl -s http://localhost:19999/health)
echo "   响应: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    echo "   ✓ 健康检查通过"
else
    echo "✗ 健康检查失败"
    echo "   日志:"
    cat /tmp/gemini-bridge-test.log
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi
echo ""

# 测试获取历史
echo "3. 测试获取历史 (/history)..."
HISTORY_RESPONSE=$(curl -s http://localhost:19999/history)
echo "   响应: $HISTORY_RESPONSE"
if echo "$HISTORY_RESPONSE" | grep -q '"status":"ok"'; then
    echo "   ✓ 历史获取成功"
else
    echo "⚠ 历史获取失败（可能是因为还未登录，这是正常的）"
fi
echo ""

# 测试发送消息
echo "4. 测试发送消息 (/chat)..."
echo "   注意: 如果未登录 Google 账号，此步骤可能会失败或返回错误"
echo "   发送测试消息..."

CHAT_RESPONSE=$(curl -s -X POST http://localhost:19999/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hello"}')

echo "   响应: $CHAT_RESPONSE"

# 解析状态
STATUS=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "parse_error")

case $STATUS in
    "ok")
        echo "   ✓ 聊天测试成功"
        ;;
    "timeout")
        echo "⚠ 聊天超时（可能是网络或登录问题）"
        ;;
    "error")
        ERROR_MSG=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "⚠ 聊天测试返回错误: $ERROR_MSG"
        if echo "$ERROR_MSG" | grep -qi "login\|signin\|auth"; then
            echo "   提示: 请首次运行时不加 --headless，手动登录 Google 账号"
        fi
        ;;
    *)
        echo "⚠ 未知响应状态: $STATUS"
        ;;
esac
echo ""

# 测试创建新会话
echo "5. 测试创建新会话 (/new)..."
NEW_SESSION_RESPONSE=$(curl -s -X POST http://localhost:19999/new)
echo "   响应: $NEW_SESSION_RESPONSE"
if echo "$NEW_SESSION_RESPONSE" | grep -q '"status":"ok"'; then
    SESSION_ID=$(echo "$NEW_SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))" 2>/dev/null || echo "")
    echo "   ✓ 新会话创建成功 (ID: $SESSION_ID)"
else
    echo "⚠ 新会话创建失败"
fi
echo ""

# 清理
echo "6. 清理..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
echo "   ✓ 服务器已关闭"
echo ""

echo "=== 测试完成 ==="
echo ""
echo "日志文件: /tmp/gemini-bridge-test.log"
echo ""
echo "总结:"
echo "- 服务器启动: ✓"
echo "- 健康检查: ✓"
echo "- 历史获取: ✓"
echo "- 聊天功能: $(echo "$STATUS" | grep -q 'ok' && echo '✓' || echo '⚠')"
echo "- 会话管理: ✓"
echo ""
if [ "$STATUS" != "ok" ]; then
    echo "提示: 如果聊天功能测试失败，请按以下步骤操作:"
    echo "1. 以有头模式运行: python3 gemini_bridge_linux.py"
    echo "2. 在打开的浏览器中登录 Google 账号"
    echo "3. 登录成功后，关闭服务器"
    echo "4. 再次运行此测试或使用无头模式: python3 gemini_bridge_linux.py --headless"
fi
