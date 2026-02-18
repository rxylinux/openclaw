import sys
import json
import requests
import os


# 内置的股票网站列表
STOCK_SITES = [
    "caifinance.com",           # 财联社
    "kaipanla.cn",             # 开盘啦
    "taoguba.com",              # 淘股吧
    "xueqiu.com",               # 雪球网
    "jiuyangongshe.com",         # 韭研公社
    "luobotou.com",              # 萝卜投研
    "juchao.com",               # 巨潮资讯
    "xuangutong.com"            # 选股通
]


def baidu_search(api_key, requestBody: dict):
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    headers = {
        "Authorization": "Bearer %s" % api_key,
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }

    # 使用POST方法发送JSON数据
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
        print("\n内置股票网站列表：")
        print("1. 财联社 - caifinance.com")
        print("2. 开盘啦 - kaiplanla.cn")
        print("3. 淘股吧 - taoguba.com")
        print("4. 雪球网 - xueqiu.com")
        print("5. 韭研公社 - jiuyangongshe.com")
        print("6. 萝卜投研 - luobotou.com")
        print("7. 巨潮资讯 - juchao.com")
        print("8. 选股通 - xuangutong.com")
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

    # We will pass these via env vars for security
    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        print("Error: BAIDU_API_KEY must be set in environment.")
        sys.exit(1)

    # 检查是否要搜索股票网站
    search_sites = parse_data.get("search_sites") if "search_sites" in parse_data else None

    # 如果指定了股票网站搜索
    site_list = []
    if search_sites:
        if search_sites == "all":
            site_list = STOCK_SITES
        else:
            # 解析网站编号，如 "1,2,3"
            try:
                site_numbers = [int(x.strip()) for x in search_sites.split(",")]
                for num in site_numbers:
                    if 1 <= num <= len(STOCK_SITES):
                        site_list.append(STOCK_SITES[num-1])
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
