#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股财务数据获取脚本 - 多数据源版本
支持 AkShare、Tushare、新浪财经等多种数据源
"""

import sys
import json
import time
from typing import Dict, Optional, Any


class FinancialDataFetcher:
    """多数据源财务数据获取器"""

    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        # 标准化代码
        if len(stock_code) == 6:
            self.standard_code = stock_code
            # 判断市场
            if stock_code.startswith('688'):
                self.market = '科创板'
                self.exchange = 'SH'
            elif stock_code.startswith('6'):
                self.market = '上交所'
                self.exchange = 'SH'
            elif stock_code.startswith('00') or stock_code.startswith('30'):
                self.market = '深交所'
                self.exchange = 'SZ'
            else:
                self.market = '未知'
                self.exchange = ''
        else:
            self.standard_code = stock_code[:6]
            self.market = '未知'
            self.exchange = ''

    def get_sina_financial_data(self) -> Dict[str, Any]:
        """
        从新浪财经获取财务数据
        优点: 免费、数据全、支持科创板
        缺点: 需要HTML解析
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            print(f"[新浪财经] 获取 {self.standard_code} 财务数据...")

            # 构建URL
            url = f'http://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/{self.standard_code}/displaytype/4.phtml'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                return {"source": "Sina", "error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析表格数据
            tables = soup.find_all('table')
            if not tables:
                return {"source": "Sina", "error": "未找到数据表格"}

            # 提取财务指标
            result = {
                "source": "Sina",
                "url": url,
                "market": self.market,
                "data": {}
            }

            # 这里需要根据实际HTML结构解析
            # 简化版本：返回原始HTML供进一步处理
            result["note"] = "新浪财经数据获取成功，但需要进一步解析HTML"
            result["html_preview"] = str(tables[0])[:500] if tables else ""

            return result

        except ImportError:
            return {"source": "Sina", "error": "需要安装 requests 和 beautifulsoup4"}
        except Exception as e:
            return {"source": "Sina", "error": str(e)}

    def get_tushare_financial_data(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        从Tushare获取财务数据
        优点: 数据全、接口稳定、结构化
        缺点: 需要API Token
        """
        try:
            import tushare as ts

            print(f"[Tushare] 获取 {self.standard_code} 财务数据...")

            if not token:
                # 尝试从环境变量获取
                import os
                token = os.getenv('TUSHARE_TOKEN')

            if not token:
                return {
                    "source": "Tushare",
                    "error": "需要TUSHARE_TOKEN，请到 https://tushare.pro 注册"
                }

            # 初始化
            ts.set_token(token)
            pro = ts.pro_api()

            # 标准化代码格式 (Tushare格式: 600519.SH)
            ts_code = f"{self.standard_code}.{self.exchange}" if self.exchange else self.standard_code

            result = {"source": "Tushare", "ts_code": ts_code, "data": {}}

            # 获取基本信息
            try:
                basic = pro.stock_basic(ts_code=ts_code)
                result["data"]["basic"] = basic.to_dict('records')[0] if not basic.empty else {}
            except Exception as e:
                result["data"]["basic"] = {"error": str(e)}

            # 获取最新财务指标
            try:
                # 获取最近3期的财务指标
                indicators = pro.fina_indicator(
                    ts_code=ts_code,
                    limit=3
                )
                result["data"]["indicators"] = indicators.to_dict('records') if not indicators.empty else []
            except Exception as e:
                result["data"]["indicators"] = {"error": str(e)}

            # 获取利润表
            try:
                profit = pro.income(
                    ts_code=ts_code,
                    limit=4
                )
                result["data"]["profit"] = profit.to_dict('records') if not profit.empty else []
            except Exception as e:
                result["data"]["profit"] = {"error": str(e)}

            return result

        except ImportError:
            return {"source": "Tushare", "error": "未安装 Tushare: pip3 install tushare"}
        except Exception as e:
            return {"source": "Tushare", "error": str(e)}

    def get_eastmoney_data(self) -> Dict[str, Any]:
        """
        从东方财富获取财务数据
        """
        try:
            import requests

            print(f"[东方财富] 获取 {self.standard_code} 财务数据...")

            # 东方财富API接口
            url = f'http://data.eastmoney.com/bbsj/{self.year}/yjbb/{self.standard_code}.html'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://data.eastmoney.com'
            }

            response = requests.get(url, headers=headers, timeout=15)

            return {
                "source": "Eastmoney",
                "status_code": response.status_code,
                "note": "东方财富数据需要进一步解析JSON响应"
            }

        except Exception as e:
            return {"source": "Eastmoney", "error": str(e)}

    def get_manual_financial_guide(self) -> Dict[str, Any]:
        """
        手动获取指南：告诉用户如何获取财务数据
        """
        return {
            "source": "Guide",
            "stock_code": self.standard_code,
            "market": self.market,
            "methods": [
                {
                    "name": "巨潮资讯（官方）",
                    "url": f"http://www.cninfo.com.cn/new/disclosure/stock?stockcode={self.standard_code}&orgId=99000468",
                    "description": "最准确的官方财报，PDF格式",
                    "steps": [
                        "1. 访问巨潮资讯",
                        "2. 搜索股票代码",
                        "3. 下载最新财报PDF",
                        "4. 查看财务数据"
                    ]
                },
                {
                    "name": "东方财富",
                    "url": f"http://data.eastmoney.com/bbsj/{self.standard_code}.html",
                    "description": "详细的财务数据网页",
                    "steps": [
                        "1. 访问东方财富数据",
                        "2. 输入股票代码",
                        "3. 查看财务分析"
                    ]
                },
                {
                    "name": "同花顺",
                    "url": f"http://basic.10jqka.com.cn/{self.standard_code}/finance/",
                    "description": "财务指标可视化",
                    "steps": [
                        "1. 访问同花顺财务分析",
                        "2. 查看各项指标"
                    ]
                }
            ]
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("="*60)
        print(" A股财务数据获取工具")
        print("="*60)
        print("\n用法: python3 get_financial_data.py <股票代码> [选项]")
        print("\n示例:")
        print("  python3 get_financial_data.py 688981")
        print("  python3 get_financial_data.py 688981 --tushare YOUR_TOKEN")
        print("  python3 get_financial_data.py 688981 --guide")
        print("\n选项:")
        print("  --sina       使用新浪财经")
        print("  --tushare    使用Tushare (需要TOKEN)")
        print("  --eastmoney  使用东方财富")
        print("  --guide      显示手动获取指南")
        print("  --all        尝试所有数据源")
        print("\n提示:")
        print("  - 科创板(688)建议使用 --tushare 或 --guide")
        print("  - Tushare注册: https://tushare.pro/register")
        print("="*60)
        sys.exit(1)

    stock_code = sys.argv[1]
    fetcher = FinancialDataFetcher(stock_code)

    # 根据参数选择数据源
    if '--guide' in sys.argv:
        result = fetcher.get_manual_financial_guide()
    elif '--tushare' in sys.argv:
        token = None
        idx = sys.argv.index('--tushare')
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith('--'):
            token = sys.argv[idx + 1]
        result = fetcher.get_tushare_financial_data(token)
    elif '--sina' in sys.argv:
        result = fetcher.get_sina_financial_data()
    elif '--eastmoney' in sys.argv:
        result = fetcher.get_eastmoney_data()
    elif '--all' in sys.argv:
        results = {
            "stock_code": stock_code,
            "sources": []
        }
        results["sources"].append(fetcher.get_sina_financial_data())
        results["sources"].append(fetcher.get_eastmoney_data())
        # Tushare需要token，跳过
        result = results
    else:
        # 默认：显示获取指南
        result = fetcher.get_manual_financial_guide()

    # 输出结果
    print("\n" + "="*60)
    print("获取结果:")
    print("="*60 + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
