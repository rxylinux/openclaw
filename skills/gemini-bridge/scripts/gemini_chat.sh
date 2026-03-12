#!/bin/bash
# gemini_chat.sh v1 — Gemini CLI 工具
# 通过 Chrome 自动化与 Gemini 对话
#
# 用法: bash gemini_chat.sh "your question" [--timeout 60] [--session default]
#
# 前置条件:
#   - macOS with Chrome
#   - Chrome 已登录 gemini.google.com
#   - Chrome > 设置 > 隐私与安全性 > 自动化 > 允许 Google Chrome

set -euo pipefail

PROMPT="${1:?Usage: gemini_chat.sh 'question' [--timeout 60] [--session default]}"
TIMEOUT=60
SESSION_ID=""
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --session) SESSION_ID="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# 构建 JSON 请求
PAYLOAD="{\"prompt\":\"$(echo "$PROMPT" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\",\"timeout\":$TIMEOUT"
if [[ -n "$SESSION_ID" ]]; then
  PAYLOAD="$PAYLOAD,\"session_id\":\"$SESSION_ID\""
fi
PAYLOAD="$PAYLOAD}"

# 调用 API
curl -s -X POST http://127.0.0.1:19999/chat \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool

echo ""
