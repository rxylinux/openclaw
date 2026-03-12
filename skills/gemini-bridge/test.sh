#!/bin/bash
# Gemini Bridge 快速测试脚本

set -e

echo "=== Gemini Bridge 测试 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_case() {
    local name="$1"
    local command="$2"

    echo -n "测试: $name ... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
    fi
}

# 1. 检查 Python
test_case "Python 3 已安装" "python3 --version"

# 2. 检查 Chrome
test_case "Chrome 已安装" "which 'Google Chrome' || which google-chrome || which chrome"

# 3. 检查脚本存在
test_case "gemini_bridge.py 存在" "test -f /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py"

# 4. 检查 CLI 脚本存在
test_case "gemini_chat.sh 存在" "test -f /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_chat.sh"

echo ""
echo "=== 权限检查 ==="
echo ""
echo "请手动检查以下权限："
echo "1. 系统设置 > 隐私与安全性 > 自动化"
echo "2. 确保 'Google Chrome' 被勾选"
echo ""
read -p "按回车继续..." -r

echo ""
echo "=== 启动服务 ==="
echo ""

# 启动服务（后台）
python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge.py > /tmp/gemini-bridge.log 2>&1 &
PID=$!
echo "服务已启动，PID: $PID"

# 等待服务启动
sleep 3

echo ""
echo "=== 功能测试 ==="
echo ""

# 5. 健康检查
echo "5. 健康检查..."
HEALTH=$(curl -s http://localhost:19999/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 服务响应正常${NC}"
    echo "$HEALTH" | python3 -m json.tool
    ((PASSED++))
else
    echo -e "${RED}✗ 服务无响应${NC}"
    ((FAILED++))
fi

echo ""

# 6. 发送简单请求
echo "6. 发送简单请求..."
RESPONSE=$(curl -s -X POST http://localhost:19999/chat \
  -d '{"prompt":"1+1=","timeout":30}')

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 请求成功${NC}"
    echo "$RESPONSE" | python3 -m json.tool
    ((PASSED++))
else
    echo -e "${RED}✗ 请求失败${NC}"
    ((FAILED++))
fi

echo ""

# 7. 创建新会话
echo "7. 创建新会话..."
NEW_SESSION=$(curl -s -X POST http://localhost:19999/new)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 新会话创建成功${NC}"
    echo "$NEW_SESSION" | python3 -m json.tool
    ((PASSED++))
else
    echo -e "${RED}✗ 新会话创建失败${NC}"
    ((FAILED++))
fi

echo ""

# 8. 读取历史
echo "8. 读取会话历史..."
HISTORY=$(curl -s http://localhost:19999/history)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 历史读取成功${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ 历史读取失败${NC}"
    ((FAILED++))
fi

echo ""
echo "=== 测试结果 ==="
echo ""
echo "通过: $PASSED"
echo "失败: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    echo ""
    echo "你可以开始使用 Gemini Bridge 了："
    echo "  curl -X POST http://localhost:19999/chat -d '{\"prompt\":\"你好\"}'"
else
    echo -e "${RED}部分测试失败${NC}"
    echo ""
    echo "请检查："
    echo "1. Chrome 是否已启动并登录 gemini.google.com"
    echo "2. 自动化权限是否已授予"
    echo "3. 查看日志: cat /tmp/gemini-bridge.log"
fi

echo ""
echo "停止服务？(y/n)"
read -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill $PID
    echo "服务已停止"
fi
