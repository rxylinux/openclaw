#!/bin/bash
# 获取GitHub token
if [ -f /root/.openclaw/workspace/memory/github_token.txt ]; then
    GITHUB_TOKEN=$(cat /root/.openclaw/workspace/memory/github_token.txt)
elif [ -f /root/.openclaw/workspace/.github_token ]; then
    GITHUB_TOKEN=$(cat /root/.openclaw/workspace/.github_token)
elif [ -f /root/.openclaw/workspace/memory/gh_token.txt ]; then
    GITHUB_TOKEN=$(cat /root/.openclaw/workspace/memory/gh_token.txt)
else
    echo "找不到GitHub token文件"
    echo "请创建 /root/.openclaw/workspace/memory/github_token.txt 文件，内容为你的GitHub personal access token"
    exit 1
fi

echo "使用GitHub token: ${GITHUB_TOKEN:0:10}..."

cd /root/.openclaw/workspace/skills/baidu-search

# 移除旧的远程仓库
git remote remove origin 2>/dev/null || true

# 添加新的远程仓库（使用token）
git remote add origin https://${GITHUB_TOKEN}@github.com/rxylinux/openclaw.git

# 推送到main分支
echo "正在推送到GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ 推送成功！"
else
    echo "❌ 推送失败！"
    echo "请检查GitHub token是否有写入权限"
fi
