# 8个必备股票网站配置

## 网站详细信息

### 1. 财联社
- **域名：** caifinance.com
- **功能：** 专业财经新闻、A股24小时电报
- **特色：** 机构和私募都在使用，消息快

### 2. 开盘啦
- **域名：** kaipanla.com
- **功能：** 股票竞价、板块竞价、龙虎榜、市场情绪
- **特色：** 一站式股票平台，实时竞价数据

### 3. 淘股吧
- **域名：** taoguba.com.cn
- **功能：** A股股票炒股论坛交流分享社区
- **特色：** "股市里的黄埔军校"，很多游资大佬从这里走出来

### 4. 雪球网
- **域名：** xueqiu.com
- **功能：** 聪明的投资者都在这里，股票投资社区
- **特色：** 顶级游资聚集地，实盘分享、经典语录

### 5. 韭研公社
- **域名：** jiucaigongshe.com
- **功能：** 为实战研究赋能（原韭菜公社）
- **特色：** 逻辑派投资者聚集地，题材挖掘、炒作路径分析

### 6. 萝卜投研
- **域名：** robo.datayes.com
- **功能：** 智能股票投研|选股|基本面分析|选股|研究|投研
- **特色：** 整合各大券商研究报告，深度数据推演

### 7. 巨潮资讯
- **域名：** webchat.cninfo.com.cn
- **功能：** 深市日历、新股日历、龙虎榜、大宗交易
- **特色：** 官方信息第一出口，公告、政策、内幕消息

### 8. 选股通
- **域名：** xuangutong.com.cn
- **功能：** 选股通-智选好股票，热点题材拆解
- **特色：** 每天哪些板块最热、涨停家数统计

## 使用说明

在搜索时，可以使用以下格式在特定网站中搜索：

```bash
# 在所有8个股票网站中搜索
python3 skills/baidu-search/scripts/search.py '{"query":"中芯国际","search_sites":"all"}'

# 在指定网站中搜索（编号1-8）
python3 skills/baidu-search/scripts/search.py '{"query":"中芯国际","search_sites":"1,2,3"}'
```

## 网站编号对应
1. 财联社 - caifinance.com
2. 开盘啦 - kaipanla.com
3. 淘股吧 - taoguba.com.cn
4. 雪球网 - xueqiu.com
5. 韭研公社 - jiucaigongshe.com
6. 萝卜投研 - robo.datayes.com
7. 巨潮资讯 - webchat.cninfo.com.cn
8. 选股通 - xuangutong.com.cn
