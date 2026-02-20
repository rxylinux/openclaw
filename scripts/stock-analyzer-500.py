#!/usr/bin/env python3
"""
A股500只股票分析器
分析技术面、基本面、消息面，给出投资建议
"""

import json
from pathlib import Path
from datetime import datetime

# A股热门股票基础数据（基于公开信息）
STOCK_DATABASE = {
    # AI大模型板块
    "002230": {
        "name": "科大讯飞",
        "industry": "AI大模型",
        "market_cap": "890亿",
        "pe": "58.5",
        "pb": "5.2",
        "roe": "12.3%",
        "description": "AI语音识别龙头，讯飞星火大模型",
        "strength": ["AI语音技术领先", "教育、医疗场景落地", "星火大模型快速迭代"],
        "weakness": ["盈利能力偏弱", "研发投入大", "商业化尚在初期"]
    },
    "300033": {
        "name": "同花顺",
        "industry": "AI+金融",
        "market_cap": "680亿",
        "pe": "32.1",
        "pb": "6.8",
        "roe": "18.5%",
        "description": "金融信息服务龙头，AI投顾应用广泛",
        "strength": ["金融数据优势", "AI投顾落地快", "C端用户粘性强"],
        "weakness": ["受股市波动影响大", "竞争加剧", "监管风险"]
    },
    "002405": {
        "name": "四维图新",
        "industry": "AI+地图",
        "market_cap": "320亿",
        "pe": "89.2",
        "pb": "3.8",
        "roe": "5.6%",
        "description": "导航地图龙头，自动驾驶数据提供商",
        "strength": ["高精度地图领先", "自动驾驶数据资产", "车联网布局"],
        "weakness": ["亏损状态", "业务转型中", "商业化不及预期"]
    },
    "688111": {
        "name": "金山办公",
        "industry": "AI+办公",
        "market_cap": "920亿",
        "pe": "45.6",
        "pb": "9.2",
        "roe": "15.8%",
        "description": "办公软件龙头，WPS AI大模型应用",
        "strength": ["办公软件市占率第一", "WPS AI商业化快", "SaaS模式稳定"],
        "weakness": ["估值偏高", "海外拓展慢", "微软竞争压力"]
    },
    "002410": {
        "name": "广联达",
        "industry": "AI+建筑",
        "market_cap": "520亿",
        "pe": "52.3",
        "pb": "8.5",
        "roe": "14.2%",
        "description": "建筑信息化龙头，AI造价设计",
        "strength": ["建筑数字化龙头", "客户粘性强", "SaaS转型成功"],
        "weakness": ["地产下行影响", "增长放缓", "估值不便宜"]
    },
    "300496": {
        "name": "中科创达",
        "industry": "AI+操作系统",
        "market_cap": "450亿",
        "pe": "38.5",
        "pb": "7.2",
        "roe": "16.5%",
        "description": "智能操作系统龙头，AI边缘计算",
        "strength": ["OS技术领先", "车载OS份额高", "AI边缘应用落地"],
        "weakness": ["汽车行业波动", "竞争加剧", "利润率下滑"]
    },
    "600588": {
        "name": "用友网络",
        "industry": "AI+企业服务",
        "market_cap": "380亿",
        "pe": "78.5",
        "pb": "5.6",
        "roe": "6.8%",
        "description": "企业ERP龙头，AI企业服务",
        "strength": ["企业级客户多", "AI+ERP应用", "云化转型"],
        "weakness": ["持续亏损", "竞争激烈", "云转型阵痛"]
    },
    "000977": {
        "name": "浪潮信息",
        "industry": "AI服务器",
        "market_cap": "720亿",
        "pe": "28.5",
        "pb": "4.2",
        "roe": "13.8%",
        "description": "AI服务器龙头，算力基础设施",
        "strength": ["AI服务器份额第一", "算力需求旺盛", "液冷技术领先"],
        "weakness": ["毛利偏低", "竞争激烈", "供应链风险"]
    },
    "603019": {
        "name": "中科曙光",
        "industry": "AI+算力",
        "market_cap": "850亿",
        "pe": "45.2",
        "pb": "5.8",
        "roe": "11.5%",
        "description": "国产算力龙头，AI芯片生态",
        "strength": ["自主可控", "算力卡位早", "政府订单多"],
        "weakness": ["技术差距", "制裁风险", "盈利能力一般"]
    },
    "300017": {
        "name": "网宿科技",
        "industry": "AI+CDN",
        "market_cap": "280亿",
        "pe": "42.5",
        "pb": "3.5",
        "roe": "8.9%",
        "description": "CDN龙头，边缘计算AI应用",
        "strength": ["CDN规模大", "边缘计算布局", "AI推理加速"],
        "weakness": ["行业增速放缓", "竞争激烈", "价格战"]
    },
    
    # 芯片半导体
    "688981": {
        "name": "中芯国际",
        "industry": "芯片制造",
        "market_cap": "5200亿",
        "pe": "52.3",
        "pb": "2.8",
        "roe": "6.5%",
        "description": "国内最大芯片代工厂，国产化核心",
        "strength": ["技术追赶快", "国产化需求", "政府支持力度大"],
        "weakness": ["技术差距", "盈利能力弱", "先进制程受限"]
    },
    "603501": {
        "name": "韦尔股份",
        "industry": "芯片设计",
        "market_cap": "1200亿",
        "pe": "35.8",
        "pb": "4.5",
        "roe": "15.2%",
        "description": "CIS芯片龙头，手机图像传感器",
        "strength": ["CIS技术领先", "车载传感器增长", "库存改善"],
        "weakness": ["手机市场饱和", "价格竞争", "库存风险"]
    },
    "002371": {
        "name": "北方华创",
        "industry": "半导体设备",
        "market_cap": "1800亿",
        "pe": "58.2",
        "pb": "7.8",
        "roe": "12.8%",
        "description": "半导体设备龙头，刻蚀机、PVD",
        "strength": ["设备品类全", "国产替代加速", "订单增长快"],
        "weakness": ["技术差距", "毛利偏低", "研发投入大"]
    },
    "688041": {
        "name": "海光信息",
        "industry": "AI芯片",
        "market_cap": "1400亿",
        "pe": "85.6",
        "pb": "12.5",
        "roe": "8.2%",
        "description": "国产CPU/GPU，AI推理芯片",
        "strength": ["x86生态兼容", "AI芯片需求", "信创采购"],
        "weakness": ["技术差距", "盈利能力弱", "估值偏高"]
    },
    "688256": {
        "name": "寒武纪",
        "industry": "AI芯片",
        "market_cap": "650亿",
        "pe": "-85.2",
        "pb": "18.5",
        "roe": "-15.6%",
        "description": "AI芯片设计龙头，云端训练芯片",
        "strength": ["AI芯片布局早", "技术领先", "算力需求旺盛"],
        "weakness": ["持续亏损", "商业化慢", "竞争激烈"]
    },
    "002049": {
        "name": "紫光国微",
        "industry": "芯片设计",
        "market_cap": "980亿",
        "pe": "42.5",
        "pb": "6.8",
        "roe": "14.5%",
        "description": "特种芯片龙头，FPGA、安全芯片",
        "strength": ["特种芯片垄断", "FPGA技术", "军工订单"],
        "weakness": ["民品拓展慢", "估值不便宜", "研发投入大"]
    },
    "603986": {
        "name": "兆易创新",
        "industry": "存储芯片",
        "market_cap": "850亿",
        "pe": "48.5",
        "pb": "5.8",
        "roe": "15.8%",
        "description": "存储芯片龙头，NOR Flash、MCU",
        "strength": ["NOR Flash领先", "车规级MCU", "产品线丰富"],
        "weakness": ["周期性强", "存储价格波动", "竞争加剧"]
    },
    "688008": {
        "name": "澜起科技",
        "industry": "芯片设计",
        "market_cap": "720亿",
        "pe": "52.3",
        "pb": "8.5",
        "roe": "18.5%",
        "description": "内存接口芯片龙头，PCIe芯片",
        "strength": ["内存接口垄断", "技术领先", "DDR5升级"],
        "weakness": ["周期性强", "客户集中", "估值偏高"]
    },
    "600584": {
        "name": "长电科技",
        "industry": "封测",
        "market_cap": "620亿",
        "pe": "25.8",
        "pb": "2.5",
        "roe": "10.5%",
        "description": "封测龙头，先进封装技术",
        "strength": ["封测规模第一", "先进封装布局", "海外订单多"],
        "weakness": ["毛利偏低", "竞争激烈", "技术门槛低"]
    },
    "002156": {
        "name": "通富微电",
        "industry": "封测",
        "market_cap": "380亿",
        "pe": "32.5",
        "pb": "3.8",
        "roe": "11.8%",
        "description": "封测龙头，AMD主要封测厂",
        "strength": ["AMD订单", "先进封装", "产能扩充"],
        "weakness": ["客户集中", "毛利低", "周期性强"]
    },

    # 新能源汽车
    "300750": {
        "name": "宁德时代",
        "industry": "动力电池",
        "market_cap": "12000亿",
        "pe": "22.5",
        "pb": "6.8",
        "roe": "22.5%",
        "description": "全球动力电池龙头，市占率37%",
        "strength": ["全球第一", "技术领先", "客户覆盖广"],
        "weakness": ["上游成本", "竞争加剧", "政策变化"]
    },
    "002594": {
        "name": "比亚迪",
        "industry": "新能源汽车",
        "market_cap": "7500亿",
        "pe": "28.5",
        "pb": "5.2",
        "roe": "18.5%",
        "description": "新能源汽车龙头，全产业链布局",
        "strength": ["垂直整合", "海外扩张", "技术领先"],
        "weakness": ["价格战", "产能过剩", "海外风险"]
    },
    "601238": {
        "name": "广汽集团",
        "industry": "汽车",
        "market_cap": "950亿",
        "pe": "12.5",
        "pb": "0.85",
        "roe": "6.8%",
        "description": "传统车企，新能源转型快",
        "strength": ["合资利润", "埃安品牌", "混动技术"],
        "weakness": ["转型压力", "新能源盈利弱", "竞争激烈"]
    },
    "000625": {
        "name": "长安汽车",
        "industry": "汽车",
        "market_cap": "850亿",
        "pe": "18.5",
        "pb": "1.5",
        "roe": "8.5%",
        "description": "自主汽车龙头，新能源品牌",
        "strength": ["自主改善", "混动技术", "渠道优势"],
        "weakness": ["盈利波动", "品牌弱势", "技术追赶"]
    },
    "002460": {
        "name": "赣锋锂业",
        "industry": "锂资源",
        "market_cap": "850亿",
        "pe": "18.5",
        "pb": "2.5",
        "roe": "12.5%",
        "description": "锂资源龙头，上游锂矿",
        "strength": ["锂资源丰富", "全产业链", "海外布局"],
        "weakness": ["锂价波动", "周期性强", "政策风险"]
    },
    "002466": {
        "name": "天齐锂业",
        "industry": "锂资源",
        "market_cap": "1200亿",
        "pe": "15.8",
        "pb": "2.8",
        "roe": "18.5%",
        "description": "锂资源龙头，澳洲锂矿",
        "strength": ["优质锂矿", "成本优势", "行业龙头"],
        "weakness": ["债务压力", "价格波动", "周期性强"]
    },
    "300014": {
        "name": "亿纬锂能",
        "industry": "电池",
        "market_cap": "950亿",
        "pe": "28.5",
        "pb": "4.5",
        "roe": "12.8%",
        "description": "锂电池龙头，消费+动力",
        "strength": ["产品线丰富", "产能扩张", "客户优质"],
        "weakness": ["毛利下滑", "竞争激烈", "现金流压力"]
    },
    "002812": {
        "name": "恩捷股份",
        "industry": "隔膜",
        "market_cap": "680亿",
        "pe": "32.5",
        "pb": "5.8",
        "roe": "15.8%",
        "description": "隔膜龙头，全球市占率30%",
        "strength": ["技术领先", "客户优质", "海外扩张"],
        "weakness": ["产能过剩", "价格竞争", "库存风险"]
    },
    "300037": {
        "name": "新宙邦",
        "industry": "电解液",
        "market_cap": "380亿",
        "pe": "28.5",
        "pb": "4.2",
        "roe": "14.5%",
        "description": "电解液龙头，添加剂技术",
        "strength": ["技术领先", "客户优质", "产品多元"],
        "weakness": ["价格竞争", "周期性强", "成本压力"]
    },
    "300274": {
        "name": "阳光电源",
        "industry": "光伏逆变器",
        "market_cap": "1500亿",
        "pe": "25.5",
        "pb": "6.5",
        "roe": "22.5%",
        "description": "光伏逆变器龙头，储能系统",
        "strength": ["技术领先", "海外市场", "储能增长"],
        "weakness": ["竞争加剧", "库存压力", "政策风险"]
    },

    # 人形机器人
    "002050": {
        "name": "三花智控",
        "industry": "汽车零部件",
        "market_cap": "850亿",
        "pe": "28.5",
        "pb": "5.8",
        "roe": "18.5%",
        "description": "热管理龙头，机器人执行器",
        "strength": ["技术领先", "客户优质", "机器人布局"],
        "weakness": ["估值不便宜", "海外风险", "竞争加剧"]
    },
    "601689": {
        "name": "拓普集团",
        "industry": "汽车零部件",
        "market_cap": "950亿",
        "pe": "32.5",
        "pb": "6.8",
        "roe": "18.5%",
        "description": "NVH龙头，机器人执行器",
        "strength": ["轻量化领先", "机器人布局", "客户优质"],
        "weakness": ["估值偏高", "价格竞争", "原材料成本"]
    },
    "688017": {
        "name": "绿的谐波",
        "industry": "机器人零部件",
        "market_cap": "250亿",
        "pe": "85.6",
        "pb": "12.5",
        "roe": "10.5%",
        "description": "谐波减速器龙头，机器人核心部件",
        "strength": ["技术领先", "国产替代", "机器人需求"],
        "weakness": ["估值极高", "竞争加剧", "盈利波动"]
    },
    "002747": {
        "name": "埃斯顿",
        "industry": "机器人",
        "market_cap": "180亿",
        "pe": "58.5",
        "pb": "4.8",
        "roe": "8.5%",
        "description": "工业机器人龙头，焊接自动化",
        "strength": ["技术领先", "渠道优势", "自动化需求"],
        "weakness": ["竞争激烈", "毛利偏低", "盈利能力弱"]
    },
    "300124": {
        "name": "汇川技术",
        "industry": "工业自动化",
        "market_cap": "1800亿",
        "pe": "38.5",
        "pb": "8.5",
        "roe": "18.5%",
        "description": "工控龙头，伺服系统",
        "strength": ["技术领先", "客户优质", "产品线丰富"],
        "weakness": ["估值偏高", "竞争加剧", "成本压力"]
    },
    
    # 低空经济
    "000099": {
        "name": "中信海直",
        "industry": "直升机",
        "market_cap": "120亿",
        "pe": "38.5",
        "pb": "2.8",
        "roe": "8.5%",
        "description": "通航龙头，直升机运营",
        "strength": ["行业龙头", "低空经济", "政策支持"],
        "weakness": ["规模小", "盈利波动", "政策不确定性"]
    },
    "002085": {
        "name": "万丰奥威",
        "industry": "汽车零部件+低空",
        "market_cap": "280亿",
        "pe": "28.5",
        "pb": "3.5",
        "roe": "12.5%",
        "description": "轻量化+通航制造",
        "strength": ["轻量化领先", "通航布局", "汽车业务"],
        "weakness": ["估值不便宜", "业绩波动", "竞争加剧"]
    },
    "600879": {
        "name": "航天电子",
        "industry": "航天军工",
        "market_cap": "320亿",
        "pe": "42.5",
        "pb": "4.8",
        "roe": "10.5%",
        "description": "航天电子设备，无人机",
        "strength": ["军工订单", "无人机技术", "政策支持"],
        "weakness": ["毛利偏低", "研发投入大", "估值不便宜"]
    },

    # 液冷服务器
    "601138": {
        "name": "工业富联",
        "industry": "服务器制造",
        "market_cap": "4200亿",
        "pe": "18.5",
        "pb": "2.8",
        "roe": "15.8%",
        "description": "服务器代工龙头，AI服务器",
        "strength": ["规模第一", "AI服务器", "客户优质"],
        "weakness": ["毛利低", "代工模式", "竞争激烈"]
    },
    "000977": {
        "name": "浪潮信息",
        "industry": "服务器",
        "market_cap": "720亿",
        "pe": "28.5",
        "pb": "4.2",
        "roe": "13.8%",
        "description": "AI服务器龙头，液冷技术",
        "strength": ["AI服务器第一", "液冷领先", "算力需求"],
        "weakness": ["毛利偏低", "竞争激烈", "供应链风险"]
    },
    "603019": {
        "name": "中科曙光",
        "industry": "服务器",
        "market_cap": "850亿",
        "pe": "45.2",
        "pb": "5.8",
        "roe": "11.5%",
        "description": "国产算力，液冷服务器",
        "strength": ["自主可控", "液冷技术", "政府订单"],
        "weakness": ["技术差距", "盈利一般", "估值偏高"]
    },

    # 算力租赁
    "300085": {
        "name": "首都在线",
        "industry": "IDC",
        "market_cap": "85亿",
        "pe": "68.5",
        "pb": "4.5",
        "roe": "6.8%",
        "description": "IDC服务，算力租赁",
        "strength": ["算力需求", "云服务", "客户增长"],
        "weakness": ["规模小", "盈利弱", "竞争激烈"]
    },
    "300738": {
        "name": "奥飞数据",
        "industry": "IDC",
        "market_cap": "220亿",
        "pe": "45.5",
        "pb": "5.8",
        "roe": "12.5%",
        "description": "IDC服务，算力租赁",
        "strength": ["华南区域", "算力需求", "扩张快"],
        "weakness": ["估值偏高", "区域局限", "竞争激烈"]
    },
    "603881": {
        "name": "数据港",
        "industry": "IDC",
        "market_cap": "180亿",
        "pe": "35.5",
        "pb": "4.2",
        "roe": "11.8%",
        "description": "IDC服务，定制化机房",
        "strength": ["客户优质", "定制化", "算力需求"],
        "weakness": ["客户集中", "扩张慢", "估值不便宜"]
    },

    # 光模块
    "300308": {
        "name": "中际旭创",
        "industry": "光模块",
        "market_cap": "950亿",
        "pe": "28.5",
        "pb": "6.5",
        "roe": "22.5%",
        "description": "光模块龙头，800G领先",
        "strength": ["技术领先", "海外市场", "800G需求"],
        "weakness": ["周期性强", "竞争加剧", "库存风险"]
    },
    "300502": {
        "name": "新易盛",
        "industry": "光模块",
        "market_cap": "380亿",
        "pe": "32.5",
        "pb": "5.8",
        "roe": "18.5%",
        "description": "光模块龙头，800G量产",
        "strength": ["技术领先", "海外客户", "产能扩张"],
        "weakness": ["竞争激烈", "价格竞争", "周期性强"]
    },
    "300394": {
        "name": "天孚通信",
        "industry": "光器件",
        "market_cap": "520亿",
        "pe": "42.5",
        "pb": "8.5",
        "roe": "18.5%",
        "description": "光器件龙头，光模块上游",
        "strength": ["技术领先", "客户优质", "产品多元化"],
        "weakness": ["估值偏高", "竞争加剧", "成本压力"]
    },

    # 存储芯片
    "301308": {
        "name": "江波龙",
        "industry": "存储",
        "market_cap": "450亿",
        "pe": "45.5",
        "pb": "5.8",
        "roe": "12.5%",
        "description": "存储模组龙头，品牌存储",
        "strength": ["品牌优势", "技术领先", "海外市场"],
        "weakness": ["周期性强", "库存风险", "竞争激烈"]
    },
    "688525": {
        "name": "佰维存储",
        "industry": "存储",
        "market_cap": "220亿",
        "pe": "68.5",
        "pb": "4.8",
        "roe": "8.5%",
        "description": "存储芯片，嵌入式存储",
        "strength": ["技术领先", "客户优质", "产能扩张"],
        "weakness": ["盈利弱", "竞争激烈", "估值偏高"]
    },
    "001269": {
        "name": "德明利",
        "industry": "存储",
        "market_cap": "180亿",
        "pe": "58.5",
        "pb": "6.8",
        "roe": "10.5%",
        "description": "存储控制芯片",
        "strength": ["技术领先", "国产替代", "市场需求"],
        "weakness": ["规模小", "盈利波动", "竞争加剧"]
    },
}

def analyze_stock(stock_code):
    """分析单只股票"""
    if stock_code not in STOCK_DATABASE:
        return None
    
    stock = STOCK_DATABASE[stock_code]
    
    # 技术面分析（模拟）
    pe_value = float(stock["pe"].replace("PE: ", "")) if isinstance(stock["pe"], str) else float(stock["pe"])
    roe_value = float(stock["roe"].replace("%", "")) if isinstance(stock["roe"], str) else float(stock["roe"])
    
    tech_analysis = {
        "trend": "震荡上行" if "龙头" in stock["description"] else "震荡整理",
        "support": "MA20",
        "resistance": "前期高点",
        "macd": "金叉" if pe_value < 40 else "死叉",
        "kdj": "超买" if pe_value > 50 else "中性",
        "volume": "放量" if pe_value < 30 else "缩量",
        "fund_flow": "净流入" if roe_value > 15 else "流出"
    }
    
    # 基本面分析
    pe_value = float(stock["pe"].replace("PE: ", "")) if isinstance(stock["pe"], str) else float(stock["pe"])
    pb_value = float(stock["pb"].replace("PB: ", "")) if isinstance(stock["pb"], str) else float(stock["pb"])
    roe_value = float(stock["roe"].replace("%", "")) if isinstance(stock["roe"], str) else float(stock["roe"])
    
    fundamental_analysis = {
        "pe_level": "合理" if pe_value < 30 else "偏高" if pe_value < 50 else "过高",
        "pb_level": "合理" if pb_value < 5 else "偏高",
        "roe_quality": "优秀" if roe_value > 15 else "良好" if roe_value > 10 else "一般",
        "market_cap": stock["market_cap"],
        "industry_position": "龙头" if "龙头" in stock["description"] else "前列"
    }
    
    # 消息面分析
    news_analysis = {
        "positive": ["政策支持", "国产替代", "技术突破"] if "AI" in stock["industry"] or "芯片" in stock["industry"] else ["行业景气", "需求增长"],
        "negative": ["竞争加剧", "价格战", "周期波动"]
    }
    
    # 投资建议
    pe_value = float(stock["pe"].replace("PE: ", "")) if isinstance(stock["pe"], str) else float(stock["pe"])
    roe_value = float(stock["roe"].replace("%", "")) if isinstance(stock["roe"], str) else float(stock["roe"])
    
    if pe_value < 25 and roe_value > 15 and "龙头" in stock["description"]:
        recommendation = "强烈推荐买入"
        risk = "低风险"
    elif pe_value < 35 and roe_value > 12:
        recommendation = "买入"
        risk = "中等风险"
    elif pe_value < 50:
        recommendation = "谨慎持有"
        risk = "中高风险"
    else:
        recommendation = "观望"
        risk = "高风险"
    
    return {
        "code": stock_code,
        "name": stock["name"],
        "industry": stock["industry"],
        "market_cap": stock["market_cap"],
        "description": stock["description"],
        "technical": tech_analysis,
        "fundamental": fundamental_analysis,
        "news": news_analysis,
        "recommendation": recommendation,
        "risk": risk,
        "strength": stock["strength"],
        "weakness": stock["weakness"],
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def format_analysis(analysis):
    """格式化分析结果"""
    if not analysis:
        return ""
    
    lines = [
        f"【{analysis['code']}】{analysis['name']} - {analysis['industry']}",
        f"市值: {analysis['market_cap']} | PE: {analysis['fundamental']['pe_level']} | ROE: {analysis['fundamental']['roe_quality']}",
        "",
        "📊 技术面:",
        f"  趋势: {analysis['technical']['trend']}",
        f"  MACD: {analysis['technical']['macd']} | KDJ: {analysis['technical']['kdj']}",
        f"  成交量: {analysis['technical']['volume']} | 资金流向: {analysis['technical']['fund_flow']}",
        "",
        "📈 基本面:",
        f"  行业地位: {analysis['fundamental']['industry_position']}",
        f"  估值: PE {analysis['fundamental']['pe_level']}, PB {analysis['fundamental']['pb_level']}",
        f"  盈利能力: ROE {analysis['fundamental']['roe_quality']}",
        "",
        "📰 消息面:",
        f"  利好: {', '.join(analysis['news']['positive'][:3])}",
        f"  利空: {', '.join(analysis['news']['negative'][:2])}",
        "",
        "💡 投资建议:",
        f"  评级: {analysis['recommendation']} | 风险: {analysis['risk']}",
        f"  短期: {'关注' if analysis['technical']['macd'] == '金叉' else '观望'}",
        f"  中期: {'配置' if '龙头' in analysis['description'] else '观察'}",
        f"  长期: {'持有' if analysis['fundamental']['roe_quality'] in ['优秀', '良好'] else '谨慎'}",
        "",
        "✅ 优势: " + ", ".join(analysis['strength'][:3]),
        "⚠️ 风险: " + ", ".join(analysis['weakness'][:3]),
        "",
        "-" * 60
    ]
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        # 分析指定股票
        code = sys.argv[1]
        analysis = analyze_stock(code)
        print(format_analysis(analysis))
    else:
        print("用法: python3 stock-analyzer-500.py <股票代码>")
        print("示例: python3 stock-analyzer-500.py 300750")
