#!/bin/bash
# 批量股票分析脚本
# 一次性分析多只股票并生成报告

cd /root/.openclaw/workspace/scripts

echo "=== 开始批量分析 ==="
echo "分析时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 扩展数据库中的股票代码
stocks=(
    # 其他热门科技股
    600519 601398 601857 601318 601288 601988 600036 000858 600900 000333
    000651 600690 000002 601088 600276 300760 002415 601012 000568 600809
    002475 002241 688036 601390 601186 601668 600019 600547 600030 600837
    601066 600028 601939 601766 601888 601818 600048 000001 601111 600016
    601899 601225 601138 601877 600104
)

analyzed=0
failed=0

for code in "${stocks[@]}"; do
    result=$(python3 stock-analyzer-500.py $code 2>&1)
    
    if [[ $result == *"市值:"* ]]; then
        echo "✓ $code 分析成功"
        analyzed=$((analyzed + 1))
    else
        echo "✗ $code 分析失败（可能不在数据库中）"
        failed=$((failed + 1))
    fi
    
    # 每分析10只显示进度
    if (( analyzed % 10 == 0 )); then
        echo "进度: $analyzed/${#stocks[@]}"
    fi
done

echo ""
echo "=== 批量分析完成 ==="
echo "成功: $analyzed"
echo "失败: $failed"
echo "总计: ${#stocks[@]}"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
