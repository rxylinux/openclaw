# GitHub Token配置说明

## 如何获取GitHub Personal Access Token

1. 登录GitHub网站 (github.com)
2. 点击右上角头像 -> Settings
3. 左侧菜单找到 "Developer settings"
4. 点击 "Personal access tokens" (Tokens (classic))
5. 点击 "Generate new token (classic)"
6. 填写以下信息：
   - Note: OpenClaw A股技能搜索 (或任何描述性名称)
   - Expiration: 选择过期时间（建议90 days或No expiration）
   - 勾选权限：
     - ✅ repo (Full control of private repositories) - 必需
     - ✅ workflow (GitHub Actions) - 可选
7. 点击 "Generate token"
8. **重要：立即复制生成的token**（只显示一次）

## 配置方法

**方法1：创建token文件（推荐）**
将你的GitHub Personal Access Token保存到以下文件：
/root/.openclaw/workspace/memory/github_token.txt

**方法2：使用环境变量**
设置环境变量：
export GITHUB_TOKEN="你的GitHub Personal Access Token"

## 当前推送脚本位置
/root/.openclaw/workspace/skills/baidu-search/git-push.sh

## 推送脚本功能
1. 自动查找GitHub token文件
2. 移除旧的远程仓库
3. 添加新的远程仓库（使用token）
4. 推送到GitHub

## 使用方法
创建好token文件后，运行：
bash /root/.openclaw/workspace/skills/baidu-search/git-push.sh

## 安全提示
⚠️ **重要：** GitHub Personal Access Token等同于你的GitHub密码，请妥善保管，不要泄露给他人。
⚠️ **建议：** 设置token的过期时间，不要使用永久token。
⚠️ **权限最小化：** 只授予必要的权限（repo即可，不需要workflow等）
