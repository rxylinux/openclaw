import sys
import json
import requests
import os


# A股专业财经网站列表（根据2025年最新验证）
STOCK_SITES = [
    {"id": 1, "name": "财联社", "domain": "caifinance.com", "type": "官方新闻", "feature": "24小时实时新闻推送、公司公告、政策解读"},
    {"id": 2, "name": "开盘啦", "domain": "kaipanla.com", "type": "市场情绪", "feature": "板块热度、个股异动、隔夜挂单"},
    {"id": 3, "name": "淘股吧", "domain": "taoguba.com.cn", "type": "股民社区", "feature": "股票讨论、实战经验、游资大佬"},
    {"id": 4, "name": "雪球网", "domain": "xueqiu.com", "type": "高端社区", "feature": "游资大佬专栏、深度研报、实盘分享"},
    {"id": 5, "name": "韭研公社", "domain": "jiuyangongshe.com", "type": "逻辑派", "feature": "题材挖掘、炒作路径、事件日历"},
    {"id": 6, "name": "萝卜投研", "domain": "luobotou.com", "type": "研报数据", "feature": "券商研报、数据推演、逻辑支撑"},
    {"id": 7, "name": "巨潮资讯", "domain": "cninfo.com.cn", "type": "官方信息", "feature": "上市公司公告、财报、招股说明书"},
    {"id": 8, "name": "选股通", "domain": "xuangutong.com", "type": "热点题材", "feature": "热点板块、涨停家数、深度解析"},
    {"id": 9, "name": "理杏仁", "domain": "lixinger.com", "type": "财务数据", "feature": "专业财务分析、PE/PB估值、图表化数据"},
    {"id": 10, "name": "慧博投研", "domain": "hibor.net", "type": "研报汇总", "feature": "海量研报库、行业分析、个股研究"},
    {"id": 11, "name": "I问财", "domain": "iwencai.com", "type": "智能筛选", "feature": "条件选股、ROE筛选、营收增长筛选"},
    {"id": 12, "name": "果仁网", "domain": "guorn.com", "type": "量化回测", "feature": "量化策略、回测功能、指数PE查询"},
    {"id": 13, "name": "财报说", "domain": "caibaoshuo.com", "type": "财务对比", "feature": "杜邦分析、财务对比、股票筛选器"},
    {"id": 14, "name": "东方财富", "domain": "eastmoney.com", "type": "综合行情", "feature": "研报中心、实时行情、资金流向"},
    {"id": 15, "name": "同花顺", "domain": "10jqka.com.cn", "type": "行情数据", "feature": "选股器、公司筛选、iFinD终端"}
]


def baidu_search(api_key, requestBody: dict):
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=requestBody, headers=headers)
    response.raise_for_status()
    results = response.json()
    if "code" in results:
        raise Exception(results["message"])
    datas = results["references"]
    keys_to_remove = {"snippet"}
    for item in datas:
        for key in keys_to_remove:
            if key in item:
                del item[key]
    return datas


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python baidu_search.py <query>")
        print("\n内置8个必备股票网站：")
        for site in STOCK_SITES:
            print(f"{site['id']}. {site['name']} - {site['domain']} ({site['type']})")
            print(f"   特色：{site['feature']}")
        print("\n参数说明：")
        print("- search_sites: 在特定股票网站中搜索，格式如 '1,2,3' 或 'all'")
        print("- 示例：python baidu_search.py '{\"query\":\"贵州茅台\",\"search_sites\":\"all\"}'")
        sys.exit(1)

    query = sys.argv[1]
    parse_data = {}
    try:
        parse_data = json.loads(query)
        print(f"success parse request body: {parse_data}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")

    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment.")
        sys.exit(1)

    # 检查是否要搜索股票网站
    search_sites = parse_data.get("search_sites") if "search_sites" in parse_data else None

    site_list = []
    if search_sites:
        if search_sites == "all":
            site_list = [site['domain'] for site in STOCK_SITES]
        else:
            # 解析网站编号，如 "1,2,3"
            try:
                site_numbers = [int(x.strip()) for x in search_sites.split(",")]
                for num in site_numbers:
                    if 1 <= num <= len(STOCK_SITES):
                        site_list.append(STOCK_SITES[num-1]['domain'])
            except ValueError as e:
                print(f"search_sites参数错误：{e}，格式应为 '1,2,3' 或 'all'")
                sys.exit(1)

        print(f"在股票网站中搜索：{site_list}")

    # 构建search_filter，只在指定网站中搜索
    search_filter = {}
    if site_list:
        search_filter["match"] = {"site": site_list}

    request_body = {
        "messages": [
            {
                "content": parse_data["query"],
                "role": "user"
            }
        ],
        "edition": parse_data["edition"] if "edition" in parse_data else "standard",
        "search_source": "baidu_search_v2",
        "resource_type_filter": parse_data["resource_type_filter"] if "resource_type_filter" in parse_data else [
            {"type": "web", "top_k": 20}],
        "search_filter": {**search_filter, **(parse_data["search_filter"] if "search_filter" in parse_data else {})},
        "block_websites": parse_data["block_websites"] if "block_websites" in parse_data else None,
        "search_recency_filter": parse_data[
            "search_recency_filter"] if "search_recency_filter" in parse_data else "year",
        "safe_search": parse_data["safe_search"] if "safe_search" in parse_data else False,
    }
    try:
        results = baidu_search(api_key, request_body)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
