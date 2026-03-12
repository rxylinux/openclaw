#!/bin/bash
# 测试 Linux 版本的 Gemini Bridge

echo "=== Gemini Bridge Linux 测试脚本 ==="
echo ""

# 检查 Python 3
echo "1. 检查 Python 3..."
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 已安装: $(python3 --version)"
else
    echo "✗ Python 3 未安装"
    exit 1
fi
echo ""

# 检查 Playwright
echo "2. 检查 Playwright..."
python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright 已安装')" 2>&1 || {
    echo "✗ Playwright 未安装"
    echo "请运行: pip install playwright"
    exit 1
}
echo ""

# 检查 Chromium
echo "3. 检查 Chromium 浏览器..."
if ! python3 -m playwright install --dry-run chromium 2>&1 | grep -q "chromium"; then
    echo "⚠ Chromium 可能未安装，尝试安装..."
    python3 -m playwright install chromium
fi
echo "✓ Chromium 就绪"
echo ""

# 测试导入
echo "4. 测试代码导入..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/gemini-bridge/scripts')
from gemini_bridge_linux import GeminiBridge, VERSION
print(f'✓ 成功导入 gemini_bridge_linux.py (版本: {VERSION})')
PYEOF

if [ $? -eq 0 ]; then
    echo "导入成功"
else
    echo "✗ 导入失败"
    exit 1
fi
echo ""

# 提示用户
echo "=== 测试完成 ==="
echo ""
echo "下一步："
echo "1. 启动服务器（有头模式，便于首次登录）："
echo "   python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge_linux.py"
echo ""
echo "2. 或者后台运行（无头模式）："
echo "   python3 /root/.openclaw/workspace/skills/gemini-bridge/scripts/gemini_bridge_linux.py --headless &"
echo ""
echo "3. 测试健康检查："
echo "   curl http://localhost:19999/health"
echo ""
echo "4. 发送聊天请求："
echo "   curl -X POST http://localhost:19999/chat -H 'Content-Type: application/json' -d '{\"prompt\":\"hello\"}'"
echo ""
