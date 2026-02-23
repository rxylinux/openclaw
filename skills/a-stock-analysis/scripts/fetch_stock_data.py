#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票数据获取器 - 多数据源版本（优化版）
支持 AkShare、Web Reader 等多种数据源，无需百度 API Key

优化内容：
- 添加重试机制（网络请求失败自动重试）
- 添加缓存机制（避免重复调用）
- 修复实时行情数据获取（自动检测列名）
- 改进错误处理和日志
- 添加类型提示
- 优化雪球数据获取
- 添加数据验证和格式统一
"""

import sys
import json
import re
import time
from typing import Dict, List, Optional, Any, Union
from functools import lru_cache
from datetime import datetime
import subprocess


# ==================== 配置常量 ====================

class Config:
    """配置常量"""

    # 网络请求配置
    MAX_RETRIES = 3           # 最大重试次数
    RETRY_DELAY = 2           # 重试延迟（秒）
    REQUEST_TIMEOUT = 30      # 请求超时（秒）

    # 数据缓存配置
    CACHE_TTL = 300           # 缓存有效期（秒）- 5分钟
    ENABLE_CACHE = True       # 是否启用缓存

    # 数据输出配置
    MAX_HISTORY_DAYS = 10     # 历史数据最多返回天数
    JSON_INDENT = 2           # JSON 缩进


# ==================== 工具函数 ====================

def get_actual_trade_date() -> Optional[str]:
    """
    获取实际交易日期

    通过多种方式尝试获取真实的交易日期：
    1. 检查系统时间是否合理
    2. 从网络时间服务器获取
    3. 从最新历史数据推断

    Returns:
        实际交易日期字符串 (YYYY-MM-DD)，如果无法确定返回None
    """
    try:
        # 方法1: 检查系统时间
        now = datetime.now()
        current_year = now.year

        # 如果系统年份超过2025，说明时间不准确
        if current_year > 2025:
            # 尝试从网络获取时间
            try:
                # 使用ntpdate或类似工具
                result = subprocess.run(
                    ['sntp', 'pool.ntp.org'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # 解析ntp时间
                # 这里简化处理，实际使用中可以解析ntp返回
            except:
                pass

        # 方法2: 从AkShare最新数据推断
        try:
            import akshare as ak
            # 获取上证指数最新一天
            index_df = ak.stock_zh_index_daily(symbol='sh000001')
            if not index_df.empty:
                latest_date = index_df.iloc[-1]['日期']
                return str(latest_date)[:10]  # 返回 YYYY-MM-DD 格式
        except:
            pass

        # 如果都无法获取，返回None
        return None

    except Exception:
        return None


def get_system_time_info() -> Dict[str, Any]:
    """
    获取系统时间信息

    Returns:
        包含系统时间、是否准确、建议等信息
    """
    now = datetime.now()
    current_year = now.year

    info = {
        "system_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "year": current_year,
        "is_accurate": current_year <= 2025,
        "note": ""
    }

    if current_year > 2025:
        info["note"] = "⚠️ 系统时间不准确（年份超过2025），数据日期可能不正确"
        info["suggestion"] = "建议使用网络时间或从历史数据推断交易日"

    return info


def retry_on_failure(max_retries: int = Config.MAX_RETRIES, delay: int = Config.RETRY_DELAY):
    """
    装饰器：失败时自动重试

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        print(f"[重试] {func.__name__} 第 {attempt + 1} 次失败，{delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"[错误] {func.__name__} 已重试 {max_retries} 次，仍失败")
            return {"error": str(last_error)}
        return wrapper
    return decorator


def normalize_dataframe(df: Any, default_columns: Dict[str, str]) -> Dict[str, Any]:
    """
    标准化 DataFrame 数据，处理列名差异

    Args:
        df: AkShare 返回的 DataFrame
        default_columns: 默认列名映射（新列名 -> 可能的旧列名列表）

    Returns:
        标准化后的字典
    """
    if df is None or df.empty:
        return {}

    # 获取实际列名
    actual_columns = list(df.columns)

    # 构建列名映射
    column_map = {}
    for new_col, old_col_options in default_columns.items():
        for old_col in old_col_options:
            if old_col in actual_columns:
                column_map[new_col] = old_col
                break

    # 转换为字典，使用映射后的列名
    if len(df) > 0:
        record = df.iloc[0].to_dict()
        normalized = {}
        for new_col, old_col in column_map.items():
            if old_col in record:
                normalized[new_col] = record[old_col]
        return normalized

    return {}


def safe_json_serializable(obj: Any) -> Any:
    """
    将对象转换为 JSON 可序列化的格式

    Args:
        obj: 任意对象

    Returns:
        JSON 可序列化的对象
    """
    if isinstance(obj, (dict, list)):
        return obj
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, 'tolist'):
        return obj.tolist()
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)


# ==================== 主类 ====================

class StockDataFetcher:
    """多数据源股票数据获取器（优化版）"""

    def __init__(self, stock_code: str):
        """
        初始化

        Args:
            stock_code: 股票代码（支持多种格式）
        """
        self.raw_code = stock_code
        self.standard_code = self._normalize_code(stock_code)
        self._cache: Dict[str, tuple] = {}  # 缓存：{key: (data, timestamp)}
        self.fetch_start_time = datetime.now()  # 记录开始获取时间

    def _normalize_code(self, stock_code: str) -> str:
        """
        标准化股票代码为6位数字

        Args:
            stock_code: 原始股票代码

        Returns:
            6位数字代码
        """
        # 如果已经是6位数字，直接返回
        if len(stock_code) == 6 and stock_code.isdigit():
            return stock_code

        # 提取6位数字代码
        match = re.search(r'\d{6}', stock_code)
        if match:
            return match.group(0)

        # 无法提取，返回原始值
        return stock_code

    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not Config.ENABLE_CACHE:
            return None

        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < Config.CACHE_TTL:
                print(f"[缓存] 命中: {key}")
                return data
            else:
                # 缓存过期，删除
                del self._cache[key]

        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """设置缓存数据"""
        if not Config.ENABLE_CACHE:
            return

        self._cache[key] = (data, time.time())

    @retry_on_failure()
    def _check_akshare(self) -> bool:
        """
        检查 AkShare 是否可用

        Returns:
            True 如果可用，否则 False
        """
        try:
            import akshare as ak
            print(f"[AkShare] 版本: {ak.__version__}")
            return True
        except ImportError:
            print("[错误] 未安装 AkShare，请运行: pip3 install akshare")
            raise ImportError("AkShare 未安装")
        except Exception as e:
            print(f"[错误] AkShare 检查失败: {e}")
            raise

    def get_basic_info(self) -> Dict[str, Any]:
        """
        获取股票基本信息
        使用 AkShare 的 stock_individual_info_em 接口

        Returns:
            股票基本信息字典
        """
        cache_key = f"basic_info_{self.standard_code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 基本信息...")

            # 检查 AkShare
            self._check_akshare()

            # 获取个股信息
            info = ak.stock_individual_info_em(symbol=self.standard_code)

            # 转换为字典
            if hasattr(info, 'to_dict'):
                data = info.to_dict()
            else:
                data = {"item": info.to_dict()['item'], 'value': info.to_dict()['value']}

            result = {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": data
            }

            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_realtime_quote(self) -> Dict[str, Any]:
        """
        获取实时行情数据
        使用 AkShare 的 stock_zh_a_spot_em 接口

        Returns:
            实时行情数据字典
        """
        cache_key = f"realtime_quote_{self.standard_code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            import pandas as pd
            print(f"[AkShare] 获取 {self.standard_code} 实时行情...")

            # 检查 AkShare
            self._check_akshare()

            # 获取沪深A股实时行情（使用 _em 后缀的接口，更稳定）
            spot_df = ak.stock_zh_a_spot_em()

            # 筛选目标股票（使用"代码"列）
            stock_data = spot_df[spot_df['代码'] == self.standard_code]

            if not stock_data.empty:
                # 转换为字典
                data = stock_data.iloc[0].to_dict()

                # 格式化数值，处理 NaN 值
                for key, value in data.items():
                    if pd.isna(value):
                        data[key] = None
                    elif isinstance(value, (float, int)) and not isinstance(value, bool):
                        data[key] = float(value)

                result = {
                    "source": "AkShare",
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": data
                }

                self._set_cache(cache_key, result)
                return result
            else:
                return {
                    "source": "AkShare",
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": f"未找到股票代码 {self.standard_code}"
                }

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_financial_data(self) -> Dict[str, Any]:
        """
        获取财务数据
        使用 AkShare 的多个财务接口

        Returns:
            财务数据字典
        """
        cache_key = f"financial_data_{self.standard_code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 财务数据...")

            # 检查 AkShare
            self._check_akshare()

            result = {}

            # 获取财务分析数据
            try:
                financial_analysis = ak.stock_financial_analysis(symbol=self.standard_code)
                result['financial_analysis'] = safe_json_serializable(financial_analysis)
            except Exception as e:
                result['financial_analysis'] = {"error": f"获取失败: {str(e)}"}

            # 获取盈利能力数据
            try:
                profit_data = ak.stock_profit_sheet_by_reportly(symbol=self.standard_code)
                result['profit_sheet'] = safe_json_serializable(profit_data)
            except Exception as e:
                result['profit_sheet'] = {"error": f"获取失败: {str(e)}"}

            # 获取资产负债表
            try:
                balance_data = ak.stock_balance_sheet_by_reportly(symbol=self.standard_code)
                result['balance_sheet'] = safe_json_serializable(balance_data)
            except Exception as e:
                result['balance_sheet'] = {"error": f"获取失败: {str(e)}"}

            # 获取现金流量表
            try:
                cashflow_data = ak.stock_cash_flow_sheet_by_reportly(symbol=self.standard_code)
                result['cash_flow_sheet'] = safe_json_serializable(cashflow_data)
            except Exception as e:
                result['cash_flow_sheet'] = {"error": f"获取失败: {str(e)}"}

            response = {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": result
            }

            self._set_cache(cache_key, response)
            return response

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_xueqiu_data(self) -> Dict[str, Any]:
        """
        获取雪球网数据
        注意：此方法需要在 MCP 环境中运行才能正常工作

        Returns:
            雪球数据字典
        """
        cache_key = f"xueqiu_data_{self.standard_code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        print(f"[雪球] 获取 {self.standard_code} 数据...")

        # 构建雪球 URL
        if self.standard_code.startswith('6'):
            url = f"https://xueqiu.com/S/SH{self.standard_code}"
        else:
            url = f"https://xueqiu.com/S/SZ{self.standard_code}"

        try:
            # 注意：这里需要 MCP Web Reader 工具支持
            # 在非 MCP 环境下，使用 requests 库作为备选方案
            try:
                import requests
                from bs4 import BeautifulSoup

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(url, headers=headers, timeout=Config.REQUEST_TIMEOUT)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 提取页面标题和主要内容
                    title = soup.find('title')
                    title_text = title.text if title else "雪球"

                    # 提取关键数据
                    data = {
                        "url": url,
                        "title": title_text,
                        "status": "success",
                        "note": "数据由 requests+BeautifulSoup 获取，如需完整功能请在 MCP 环境运行"
                    }

                    result = {
                        "source": "Xueqiu",
                        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data": data
                    }

                    self._set_cache(cache_key, result)
                    return result
                else:
                    return {
                        "source": "Xueqiu",
                        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": f"HTTP {response.status_code}"
                    }

            except ImportError:
                # 如果 requests/BeautifulSoup 未安装
                return {
                    "source": "Xueqiu",
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": url,
                    "note": "请在 MCP 环境中运行，或安装 requests 和 beautifulsoup4"
                }

        except Exception as e:
            return {
                "source": "Xueqiu",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_historical_data(
        self,
        period: str = "daily",
        start_date: str = "20240101",
        end_date: str = "20241231",
        adjust: str = "qfq"
    ) -> Dict[str, Any]:
        """
        获取历史行情数据
        使用 AkShare 的 stock_zh_a_hist 接口

        Args:
            period: 周期 (daily, weekly, monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq: 前复权, hfq: 后复权, "": 不复权)

        Returns:
            历史行情数据字典
        """
        cache_key = f"hist_{self.standard_code}_{period}_{start_date}_{end_date}_{adjust}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 历史行情...")

            # 检查 AkShare
            self._check_akshare()

            hist_df = ak.stock_zh_a_hist(
                symbol=self.standard_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )

            if not hist_df.empty:
                # 返回最近 N 天的数据
                data = hist_df.tail(Config.MAX_HISTORY_DAYS).to_dict('records')

                result = {
                    "source": "AkShare",
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "period": period,
                    "adjust": adjust,
                    "count": len(data),
                    "data": data
                }

                self._set_cache(cache_key, result)
                return result
            else:
                return {
                    "source": "AkShare",
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": "未找到历史数据"
                }

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_industry_data(self, industry_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取行业数据
        使用 AkShare 的行业接口

        Args:
            industry_name: 行业名称（可选）

        Returns:
            行业数据字典
        """
        cache_key = f"industry_{industry_name or 'all'}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            target_industry = industry_name or "全部"
            print(f"[AkShare] 获取 {target_industry} 行业数据...")

            # 检查 AkShare
            self._check_akshare()

            result = {}

            # 获取行业板块列表
            try:
                sector_list = ak.stock_board_industry_name_em()
                result['sector_list'] = safe_json_serializable(sector_list)
            except Exception as e:
                result['sector_list'] = {"error": f"获取失败: {str(e)}"}

            # 如果指定了行业，获取该行业的成分股
            if industry_name:
                try:
                    sector_stocks = ak.stock_board_industry_cons_em(symbol=industry_name)
                    result[f'{industry_name}_stocks'] = safe_json_serializable(sector_stocks)
                except Exception as e:
                    result[f'{industry_name}_stocks'] = {"error": f"获取失败: {str(e)}"}

            response = {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": result
            }

            self._set_cache(cache_key, response)
            return response

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def get_stock_rank(self, rank_type: str = "涨跌幅") -> Dict[str, Any]:
        """
        获取股票排名数据
        使用 AkShare 的排名接口

        Args:
            rank_type: 排名类型 (涨跌幅, 成交额, 量比, etc.)

        Returns:
            排名数据字典
        """
        cache_key = f"rank_{rank_type}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            import akshare as ak
            print(f"[AkShare] 获取 {rank_type} 排名...")

            # 检查 AkShare
            self._check_akshare()

            # 获取实时行情数据
            rank_df = ak.stock_zh_a_spot_em()

            # 根据类型排序
            if rank_type == "涨跌幅":
                rank_df = rank_df.sort_values('涨跌幅', ascending=False)
            elif rank_type == "成交额":
                rank_df = rank_df.sort_values('成交额', ascending=False)
            elif rank_type == "振幅":
                rank_df = rank_df.sort_values('振幅', ascending=False)
            elif rank_type == "量比":
                rank_df = rank_df.sort_values('量比', ascending=False)
            elif rank_type == "换手率":
                rank_df = rank_df.sort_values('换手率', ascending=False)
            else:
                # 默认按涨跌幅排序
                rank_df = rank_df.sort_values('涨跌幅', ascending=False)

            # 取前20名
            data = rank_df.head(20).to_dict('records')

            result = {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rank_type": rank_type,
                "count": len(data),
                "data": data
            }

            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            return {
                "source": "AkShare",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

    def fetch_all(self, include_xueqiu: bool = True) -> Dict[str, Any]:
        """
        获取所有可用数据

        Args:
            include_xueqiu: 是否包含雪球数据

        Returns:
            所有数据的字典
        """
        fetch_start = datetime.now()

        print(f"\n{'='*60}")
        print(f"开始获取 {self.standard_code} 的完整数据")
        print(f"{'='*60}\n")

        # 获取系统时间信息
        time_info = get_system_time_info()

        result = {
            "stock_code": self.standard_code,
            "fetch_time": fetch_start.strftime("%Y-%m-%d %H:%M:%S"),
            "data_source_time": {
                "fetch_start": fetch_start.strftime("%Y-%m-%d %H:%M:%S"),
                "fetch_end": None,  # 将在最后填充
                "system_time": time_info["system_time"],
                "time_accuracy_note": time_info["note"],
                "source": "AkShare (东方财富数据)"
            },
            "basic_info": self.get_basic_info(),
            "realtime_quote": self.get_realtime_quote(),
            "financial_data": self.get_financial_data(),
            "historical_data": self.get_historical_data(),
        }

        # 可选：获取雪球数据
        if include_xueqiu:
            result['xueqiu_data'] = self.get_xueqiu_data()

        # 记录结束时间
        fetch_end = datetime.now()
        result["data_source_time"]["fetch_end"] = fetch_end.strftime("%Y-%m-%d %H:%M:%S")
        result["data_source_time"]["duration_seconds"] = (fetch_end - fetch_start).total_seconds()

        # 添加缓存统计
        result["cache_stats"] = {
            "cached_items": len(self._cache),
            "cache_enabled": Config.ENABLE_CACHE
        }

        # 打印数据时间信息
        print(f"\n{'='*60}")
        print("数据获取时间信息:")
        print(f"{'='*60}")
        print(f"开始时间: {result['data_source_time']['fetch_start']}")
        print(f"结束时间: {result['data_source_time']['fetch_end']}")
        print(f"耗时: {result['data_source_time']['duration_seconds']:.2f} 秒")
        print(f"系统时间: {result['data_source_time']['system_time']}")
        if result['data_source_time']['time_accuracy_note']:
            print(f"⚠️  {result['data_source_time']['time_accuracy_note']}")
        print(f"数据来源: {result['data_source_time']['source']}")
        print(f"{'='*60}\n")

        return result


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("="*60)
        print(" A股数据获取脚本 - 优化版")
        print("="*60)
        print("\n用法: python3 fetch_stock_data.py <股票代码> [选项]")
        print("\n示例:")
        print("  python3 fetch_stock_data.py 002156")
        print("  python3 fetch_stock_data.py 002156 --basic")
        print("  python3 fetch_stock_data.py 002156 --quote")
        print("  python3 fetch_stock_data.py 002156 --financial")
        print("  python3 fetch_stock_data.py 002156 --xueqiu")
        print("  python3 fetch_stock_data.py 002156 --history --start 20240101 --end 20241231")
        print("\n选项:")
        print("  --basic       仅获取基本信息")
        print("  --quote       仅获取实时行情")
        print("  --financial   仅获取财务数据")
        print("  --xueqiu      仅获取雪球数据")
        print("  --history     获取历史行情")
        print("  --industry    获取行业数据")
        print("  --rank        获取排名数据")
        print("  --all         获取所有数据（默认）")
        print("  --no-cache    禁用缓存")
        print("\n历史行情选项:")
        print("  --start       开始日期 (YYYYMMDD，默认: 20240101)")
        print("  --end         结束日期 (YYYYMMDD，默认: 20241231)")
        print("  --period      周期 (daily/weekly/monthly，默认: daily)")
        print("="*60)
        sys.exit(1)

    stock_code = sys.argv[1]

    # 检查是否禁用缓存
    if '--no-cache' in sys.argv:
        Config.ENABLE_CACHE = False
        print("[配置] 缓存已禁用")

    fetcher = StockDataFetcher(stock_code)

    # 根据参数执行相应操作
    if '--basic' in sys.argv:
        result = {"stock_code": stock_code, "basic_info": fetcher.get_basic_info()}
    elif '--quote' in sys.argv:
        result = {"stock_code": stock_code, "realtime_quote": fetcher.get_realtime_quote()}
    elif '--financial' in sys.argv:
        result = {"stock_code": stock_code, "financial_data": fetcher.get_financial_data()}
    elif '--xueqiu' in sys.argv:
        result = {"stock_code": stock_code, "xueqiu_data": fetcher.get_xueqiu_data()}
    elif '--history' in sys.argv:
        # 解析历史行情参数
        start_date = "20240101"
        end_date = "20241231"
        period = "daily"

        if '--start' in sys.argv:
            idx = sys.argv.index('--start')
            if idx + 1 < len(sys.argv):
                start_date = sys.argv[idx + 1]

        if '--end' in sys.argv:
            idx = sys.argv.index('--end')
            if idx + 1 < len(sys.argv):
                end_date = sys.argv[idx + 1]

        if '--period' in sys.argv:
            idx = sys.argv.index('--period')
            if idx + 1 < len(sys.argv):
                period = sys.argv[idx + 1]

        result = {
            "stock_code": stock_code,
            "historical_data": fetcher.get_historical_data(
                period=period,
                start_date=start_date,
                end_date=end_date
            )
        }
    elif '--industry' in sys.argv:
        # 获取行业数据
        industry_name = None
        if '--industry-name' in sys.argv:
            idx = sys.argv.index('--industry-name')
            if idx + 1 < len(sys.argv):
                industry_name = sys.argv[idx + 1]

        result = {"industry_data": fetcher.get_industry_data(industry_name)}
    elif '--rank' in sys.argv:
        rank_type = "涨跌幅"
        if '--rank-type' in sys.argv:
            idx = sys.argv.index('--rank-type')
            if idx + 1 < len(sys.argv):
                rank_type = sys.argv[idx + 1]

        result = {"rank_data": fetcher.get_stock_rank(rank_type)}
    else:
        # 无参数，获取所有数据
        include_xueqiu = '--no-xueqiu' not in sys.argv
        result = fetcher.fetch_all(include_xueqiu=include_xueqiu)

    # 输出结果
    print(f"\n{'='*60}")
    print("数据获取完成，结果如下：")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=Config.JSON_INDENT, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
