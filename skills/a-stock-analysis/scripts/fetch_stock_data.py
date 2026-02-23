#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票数据获取器 - 多数据源版本
支持 AkShare、Web Reader 等多种数据源，无需百度 API Key
"""

import sys
import json
import subprocess
from typing import Dict, List, Optional


class StockDataFetcher:
    """多数据源股票数据获取器"""

    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        # 标准化股票代码（6位数字）
        if len(stock_code) == 6:
            self.standard_code = stock_code
        else:
            # 提取6位数字代码
            import re
            match = re.search(r'\d{6}', stock_code)
            self.standard_code = match.group(0) if match else stock_code

    def get_basic_info(self) -> Dict:
        """
        获取股票基本信息
        使用 AkShare 的 stock_individual_info_em 接口
        """
        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 基本信息...")

            # 获取个股信息
            info = ak.stock_individual_info_em(symbol=self.standard_code)
            return {
                "source": "AkShare",
                "data": info.to_dict() if hasattr(info, 'to_dict') else info
            }
        except ImportError:
            print("[错误] 未安装 AkShare，请运行: pip3 install akshare")
            return {"source": "AkShare", "error": "未安装 AkShare 库"}
        except Exception as e:
            return {"source": "AkShare", "error": str(e)}

    def get_realtime_quote(self) -> Dict:
        """
        获取实时行情数据
        使用 AkShare 的 stock_zh_a_spot 接口
        """
        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 实时行情...")

            # 获取沪深A股实时行情
            spot_df = ak.stock_zh_a_spot()

            # 筛选目标股票
            stock_data = spot_df[spot_df['代码'] == self.standard_code]

            if not stock_data.empty:
                return {
                    "source": "AkShare",
                    "data": stock_data.to_dict('records')[0] if len(stock_data) > 0 else {}
                }
            else:
                return {"source": "AkShare", "error": "未找到该股票数据"}
        except Exception as e:
            return {"source": "AkShare", "error": str(e)}

    def get_financial_data(self) -> Dict:
        """
        获取财务数据
        使用 AkShare 的多个财务接口
        """
        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 财务数据...")

            result = {}

            # 获取财务分析数据
            try:
                financial_analysis = ak.stock_financial_analysis(symbol=self.standard_code)
                result['financial_analysis'] = financial_analysis.to_dict() if hasattr(financial_analysis, 'to_dict') else str(financial_analysis)
            except:
                result['financial_analysis'] = "暂无数据"

            # 获取盈利能力数据
            try:
                profit_data = ak.stock_profit_sheet_by_reportly(symbol=self.standard_code)
                result['profit_sheet'] = profit_data.to_dict() if hasattr(profit_data, 'to_dict') else str(profit_data)
            except:
                result['profit_sheet'] = "暂无数据"

            return {
                "source": "AkShare",
                "data": result
            }
        except ImportError:
            return {"source": "AkShare", "error": "未安装 AkShare 库"}
        except Exception as e:
            return {"source": "AkShare", "error": str(e)}

    def get_xueqiu_data(self) -> Dict:
        """
        获取雪球网数据
        使用 Web Reader MCP 工具
        """
        print(f"[Web Reader] 获取 {self.standard_code} 雪球数据...")

        # 构建雪球 URL
        if self.standard_code.startswith('6'):
            url = f"https://xueqiu.com/S/SH{self.standard_code}"
        else:
            url = f"https://xueqiu.com/S/SZ{self.standard_code}"

        try:
            # 使用 subprocess 调用 MCP Web Reader
            result = subprocess.run(
                ['python3', '-c', f'''
import json
from mcp__web_reader__webReader import webReader

result = webReader(
    url="{url}",
    return_format="markdown",
    retain_images=False
)
print(result)
'''],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "source": "Xueqiu",
                    "url": url,
                    "data": result.stdout
                }
            else:
                return {"source": "Xueqiu", "error": "获取失败"}
        except Exception as e:
            return {"source": "Xueqiu", "error": str(e)}

    def get_historical_data(self, period: str = "daily", start_date: str = "20240101", end_date: str = "20241231") -> Dict:
        """
        获取历史行情数据
        使用 AkShare 的 stock_zh_a_hist 接口
        """
        try:
            import akshare as ak
            print(f"[AkShare] 获取 {self.standard_code} 历史行情...")

            hist_df = ak.stock_zh_a_hist(
                symbol=self.standard_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )

            return {
                "source": "AkShare",
                "data": hist_df.tail(10).to_dict('records') if not hist_df.empty else []  # 返回最近10天
            }
        except Exception as e:
            return {"source": "AkShare", "error": str(e)}

    def get_industry_data(self, industry_name: str) -> Dict:
        """
        获取行业数据
        使用 AkShare 的行业接口
        """
        try:
            import akshare as ak
            print(f"[AkShare] 获取 {industry_name} 行业数据...")

            result = {}

            # 获取行业板块数据
            try:
                sector_data = ak.stock_board_industry_name_em()
                result['sectors'] = sector_data.to_dict() if hasattr(sector_data, 'to_dict') else str(sector_data)
            except:
                result['sectors'] = "暂无数据"

            return {
                "source": "AkShare",
                "data": result
            }
        except Exception as e:
            return {"source": "AkShare", "error": str(e)}

    def fetch_all(self, xueqiu: bool = True) -> Dict:
        """
        获取所有可用数据
        """
        print(f"\n{'='*60}")
        print(f"开始获取 {self.standard_code} 的完整数据")
        print(f"{'='*60}\n")

        result = {
            "stock_code": self.standard_code,
            "basic_info": self.get_basic_info(),
            "realtime_quote": self.get_realtime_quote(),
            "financial_data": self.get_financial_data(),
        }

        # 可选：获取雪球数据
        if xueqiu:
            result['xueqiu_data'] = self.get_xueqiu_data()

        return result


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python3 fetch_stock_data.py <股票代码> [选项]")
        print("\n示例:")
        print("  python3 fetch_stock_data.py 002156")
        print("  python3 fetch_stock_data.py 002156 --basic")
        print("  python3 fetch_stock_data.py 002156 --financial")
        print("  python3 fetch_stock_data.py 002156 --xueqiu")
        print("\n选项:")
        print("  --basic       仅获取基本信息")
        print("  --quote       仅获取实时行情")
        print("  --financial   仅获取财务数据")
        print("  --xueqiu      仅获取雪球数据")
        print("  --all         获取所有数据（默认）")
        sys.exit(1)

    stock_code = sys.argv[1]
    fetcher = StockDataFetcher(stock_code)

    # 根据参数执行相应操作
    if len(sys.argv) == 2:
        # 无参数，获取所有数据
        result = fetcher.fetch_all()
    elif '--basic' in sys.argv:
        result = {"stock_code": stock_code, "basic_info": fetcher.get_basic_info()}
    elif '--quote' in sys.argv:
        result = {"stock_code": stock_code, "realtime_quote": fetcher.get_realtime_quote()}
    elif '--financial' in sys.argv:
        result = {"stock_code": stock_code, "financial_data": fetcher.get_financial_data()}
    elif '--xueqiu' in sys.argv:
        result = {"stock_code": stock_code, "xueqiu_data": fetcher.get_xueqiu_data()}
    else:
        result = fetcher.fetch_all()

    # 输出结果
    print(f"\n{'='*60}")
    print("数据获取完成，结果如下：")
    print(f"{'='*60}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
