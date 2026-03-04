#!/bin/bash
# 博查API密钥一键配置脚本

echo "=========================================="
echo " 博查API密钥配置"
echo "=========================================="
echo ""

# 检测shell类型
if [ -n "$ZSH_VERSION" ]; then
    PROFILE_FILE="$HOME/.zshrc"
    SHELL_TYPE="zsh"
elif [ -n "$BASH_VERSION" ]; then
    PROFILE_FILE="$HOME/.bash_profile"
    SHELL_TYPE="bash"
else
    PROFILE_FILE="$HOME/.profile"
    SHELL_TYPE="unknown"
fi

echo "检测到Shell类型: $SHELL_TYPE"
echo "配置文件: $PROFILE_FILE"
echo ""

# 检查是否已配置
if grep -q "BOCHA_API_KEY" "$PROFILE_FILE" 2>/dev/null; then
    echo "⚠️  检测到已存在BOCHA_API_KEY配置"
    echo "旧配置："
    grep "BOCHA_API_KEY" "$PROFILE_FILE"
    echo ""
    read -p "是否要覆盖? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消配置"
        exit 0
    fi
    # 删除旧行
    sed -i.tmp '/BOCHA_API_KEY/d' "$PROFILE_FILE" 2>/dev/null || \
    sed -i '' '/BOCHA_API_KEY/d' "$PROFILE_FILE"
    echo "已删除旧配置"
fi

# 添加新配置
echo "" >> "$PROFILE_FILE"
echo "# 博查API密钥 - 配置时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$PROFILE_FILE"
echo "export BOCHA_API_KEY=YOUR_API_KEY_HERE" >> "$PROFILE_FILE"

echo "✅ 配置已添加到 $PROFILE_FILE"
echo ""
echo "=========================================="
echo " 下一步操作"
echo "=========================================="
echo ""
echo "请执行以下命令使配置生效："
echo ""
echo "  source $PROFILE_FILE"
echo ""
echo "或者重新打开终端窗口"
echo ""
echo "=========================================="
echo " 验证配置"
echo "=========================================="
echo ""
echo "配置生效后，运行以下命令验证："
echo ""
echo "  python3 test_bocha.py"
echo ""
echo "=========================================="
