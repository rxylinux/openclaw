#!/bin/bash

echo "========================================"
echo "  A股数据获取脚本 - 功能测试报告"
echo "========================================"
echo ""

# 测试1：基本信息
echo "【测试1】基本信息获取"
python3 fetch_stock_data.py 002156 --basic 2>&1 | grep -E "股票代码|股票简称|行业" | head -3
echo ""

# 测试2：实时行情
echo "【测试2】实时行情获取"
python3 fetch_stock_data.py 002156 --quote 2>&1 | grep -E "最新价|涨跌幅|成交量" | head -3
echo ""

# 测试3：缓存功能
echo "【测试3】缓存功能测试"
python3 -c "
from fetch_stock_data import StockDataFetcher
fetcher = StockDataFetcher('002156')
print('第一次：', end='')
fetcher.get_basic_info()
print('第二次：', end='')
fetcher.get_basic_info()
" 2>&1 | grep -E "获取|缓存"
echo ""

# 测试4：历史数据
echo "【测试4】历史数据获取"
python3 fetch_stock_data.py 002156 --history 2>&1 | grep -E "count|fetch_time" | head -2
echo ""

# 测试5：帮助信息
echo "【测试5】命令行参数"
python3 fetch_stock_data.py 2>&1 | grep -E "用法|示例" | head -2
echo ""

echo "========================================"
echo "  测试完成！"
echo "========================================"
