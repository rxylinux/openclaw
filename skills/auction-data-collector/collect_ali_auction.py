#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里拍卖数据采集脚本
采集阿里拍卖平台的公开拍卖数据
"""

import requests
import sqlite3
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/auction-data/auction.db"

# 请求头（模拟真实浏览器）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

class AliAuctionCollector:
    """阿里拍卖数据采集器"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.base_url = "https://paimai.taobao.com"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.collected_count = 0
        self.updated_count = 0
        self.new_count = 0
    
    def search_auctions(self, keyword="", days=7, category="all"):
        """搜索拍卖信息"""
        try:
            # 使用阿里拍卖的搜索API或网页
            search_url = f"{self.base_url}/auction/search.htm"
            
            params = {
                'q': keyword,
                'days': days,
                'category': category,
                'sort': 'start_time_desc'
            }
            
            print(f"🔍 搜索拍卖信息: {keyword}")
            print(f"   时间范围: {days} 天")
            print(f"   类别: {category}")
            
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            auctions = self.parse_search_result(response.text)
            
            return auctions
            
        except requests.RequestException as e:
            print(f"✗ 搜索失败: {e}")
            return []
    
    def parse_search_result(self, html):
        """解析搜索结果"""
        auctions = []
        
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找拍卖列表项
            auction_items = soup.find_all('div', class_='auction-item')
            
            print(f"   找到 {len(auction_items)} 个拍卖项")
            
            for item in auction_items:
                try:
                    auction = self.parse_auction_item(item)
                    if auction:
                        auctions.append(auction)
                except Exception as e:
                    print(f"   ✗ 解析单项失败: {e}")
                    continue
            
        except Exception as e:
            print(f"✗ 解析搜索结果失败: {e}")
        
        return auctions
    
    def parse_auction_item(self, item_element):
        """解析单个拍卖项"""
        try:
            # 提取标题
            title_elem = item_element.find('a', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            if not title:
                return None
            
            # 提取价格信息
            price = self.extract_price(item_element)
            
            # 提取起拍价
            reserve_price = self.extract_reserve_price(item_element)
            
            # 提取状态
            status = self.extract_status(item_element)
            
            # 提取类型
            auction_type = self.extract_type(item_element)
            
            # 提取时间
            start_time = self.extract_time(item_element)
            end_time = self.extract_end_time(item_element)
            
            # 提取位置
            location = self.extract_location(item_element)
            
            # 提取法院
            court = self.extract_court(item_element)
            
            # 提取URL
            url = self.extract_url(item_element)
            
            if not url:
                return None
            
            return {
                'title': title,
                'price': price,
                'reserve_price': reserve_price,
                'current_price': price if status == '拍卖中' else None,
                'auction_status': status,
                'auction_type': auction_type,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'court': court,
                'url': url,
                'source': 'ali'
            }
            
        except Exception as e:
            print(f"   ✗ 解析拍卖项失败: {e}")
            return None
    
    def extract_price(self, item_element):
        """提取价格"""
        try:
            price_elem = item_element.find('span', class_='price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # 提取数字（万元）
                match = re.search(r'([\d.]+)', price_text)
                if match:
                    return float(match.group(1)) * 10000  # 转换为元
            return None
        except:
            return None
    
    def extract_reserve_price(self, item_element):
        """提取起拍价"""
        try:
            reserve_elem = item_element.find('span', class_='reserve-price')
            if reserve_elem:
                price_text = reserve_elem.get_text(strip=True)
                match = re.search(r'([\d.]+)', price_text)
                if match:
                    return float(match.group(1)) * 10000
            return None
        except:
            return None
    
    def extract_status(self, item_element):
        """提取拍卖状态"""
        try:
            status_elem = item_element.find('span', class_='status')
            if status_elem:
                return status_elem.get_text(strip=True)
            
            # 从标题中推断状态
            title_elem = item_element.find('a', class_='title')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if '拍卖中' in title_text:
                    return '拍卖中'
                elif '已成交' in title_text:
                    return '已成交'
                elif '预展中' in title_text:
                    return '预展中'
                elif '流拍' in title_text:
                    return '流拍'
            
            return '未知'
        except:
            return '未知'
    
    def extract_type(self, item_element):
        """提取拍卖类型"""
        try:
            type_elem = item_element.find('span', class_='type')
            if type_elem:
                return type_elem.get_text(strip=True)
            
            # 根据位置信息推断类型
            location = self.extract_location(item_element)
            if location and '法院' in location:
                return '司法拍卖'
            elif '法拍' in location:
                return '法拍房'
            else:
                return '资产拍卖'
        except:
            return '未知'
    
    def extract_time(self, item_element):
        """提取开始时间"""
        try:
            time_elem = item_element.find('span', class_='start-time')
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                return self.parse_datetime(time_text)
            return None
        except:
            return None
    
    def extract_end_time(self, item_element):
        """提取结束时间"""
        try:
            time_elem = item_element.find('span', class_='end-time')
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                return self.parse_datetime(time_text)
            return None
        except:
            return None
    
    def extract_location(self, item_element):
        """提取位置信息"""
        try:
            location_elem = item_element.find('span', class_='location')
            if location_elem:
                return location_elem.get_text(strip=True)
            return None
        except:
            return None
    
    def extract_court(self, item_element):
        """提取法院信息"""
        try:
            court_elem = item_element.find('span', class_='court')
            if court_elem:
                return court_elem.get_text(strip=True)
            return None
        except:
            return None
    
    def extract_url(self, item_element):
        """提取URL"""
        try:
            url_elem = item_element.find('a', class_='title')
            if url_elem:
                href = url_elem.get('href')
                if href and not href.startswith('http'):
                    return f"{self.base_url}{href}"
                return href
            return None
        except:
            return None
    
    def parse_datetime(self, datetime_str):
        """解析日期时间字符串"""
        try:
            # 尝试常见的日期格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M',
                '%m/%d %H:%M',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def save_auction(self, auction):
        """保存拍卖数据到数据库"""
        try:
            cursor = self.conn.cursor()
            
            # 检查URL是否已存在
            cursor.execute("""
                SELECT id, price, auction_status FROM ali_auctions
                WHERE url = ?
            """, (auction['url'],))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute("""
                    UPDATE ali_auctions
                    SET price = ?, auction_status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE url = ?
                """, (auction['price'], auction['auction_status'], auction['url']))
                self.updated_count += 1
                print(f"   ✓ 更新: {auction['title'][:30]}...")
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO ali_auctions
                    (title, price, reserve_price, current_price, auction_status, auction_type,
                     start_time, end_time, location, court, url, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (auction['title'], auction['price'], auction['reserve_price'],
                      auction['current_price'], auction['auction_status'], auction['auction_type'],
                      auction['start_time'], auction['end_time'], auction['location'],
                      auction['court'], auction['url'], auction['source']))
                self.new_count += 1
                print(f"   ✓ 新增: {auction['title'][:30]}...")
            
            self.conn.commit()
            self.collected_count += 1
            
        except sqlite3.IntegrityError:
            print(f"   ✗ 重复: {auction['title'][:30]}...")
        except Exception as e:
            print(f"   ✗ 保存失败: {e}")
    
    def collect_auctions(self, keyword="", days=7, category="all", limit=100):
        """采集拍卖数据"""
        print("="*60)
        print("阿里拍卖数据采集")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"搜索关键词: {keyword if keyword else '全部'}")
        print(f"时间范围: 最近 {days} 天")
        print(f"拍卖类别: {category}")
        print(f"采集上限: {limit} 条")
        print("="*60)
        print()
        
        start_time = time.time()
        
        try:
            # 搜索拍卖
            auctions = self.search_auctions(keyword, days, category)
            
            # 限制数量
            auctions = auctions[:limit]
            
            print(f"\n找到 {len(auctions)} 条拍卖信息")
            print("开始保存数据...")
            print()
            
            # 保存到数据库
            for i, auction in enumerate(auctions, 1):
                print(f"[{i}/{len(auctions)}] ", end="")
                self.save_auction(auction)
                
                # 每保存10条输出进度
                if i % 10 == 0:
                    print(f"  进度: {i}/{len(auctions)}")
                    time.sleep(0.5)  # 避免请求过快
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print("\n" + "="*60)
            print("采集完成！")
            print("="*60)
            print(f"执行时间: {execution_time:.2f} 秒")
            print(f"采集总数: {self.collected_count} 条")
            print(f"  - 新增: {self.new_count} 条")
            print(f"  - 更新: {self.updated_count} 条")
            print()
            
            # 保存采集日志
            self.save_collection_log('ali_auctions', self.collected_count, 
                                    self.new_count, self.updated_count,
                                    'success', '', execution_time)
            
        except Exception as e:
            print(f"\n✗ 采集过程出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 保存错误日志
            self.save_collection_log('ali_auctions', self.collected_count, 
                                    self.new_count, self.updated_count,
                                    'error', str(e), time.time() - start_time)
        
        finally:
            self.conn.close()
            print(f"数据库连接已关闭")
    
    def save_collection_log(self, source, collected, new, updated, status, error, execution_time):
        """保存采集日志"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO collection_logs
                (source, items_collected, items_new, items_updated, status, error_message, execution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source, collected, new, updated, status, error, execution_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"✗ 保存日志失败: {e}")
    
    def get_statistics(self):
        """获取采集统计信息"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 获取阿里拍卖统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN auction_status = '拍卖中' THEN 1 END) as active,
                    COUNT(CASE WHEN auction_status = '已成交' THEN 1 END) as completed,
                    COUNT(CASE WHEN auction_status = '流拍' THEN 1 END) as failed,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price
                FROM ali_auctions
                WHERE price IS NOT NULL
            """)
            
            stats = cursor.fetchone()
            
            print("\n" + "="*60)
            print("阿里拍卖数据统计")
            print("="*60)
            print(f"总记录数: {stats[0]} 条")
            print(f"  - 拍卖中: {stats[1]} 条")
            print(f"  - 已成交: {stats[2]} 条")
            print(f"  - 流拍: {stats[3]} 条")
            if stats[4]:
                print(f"平均价格: {stats[4]:.2f} 元")
                print(f"最低价格: {stats[5]:.2f} 元")
                print(f"最高价格: {stats[6]:.2f} 元")
            print("="*60 + "\n")
            
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"✗ 获取统计信息失败: {e}")
            return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='阿里拍卖数据采集器')
    parser.add_argument('--keyword', type=str, default='', help='搜索关键词')
    parser.add_argument('--days', type=int, default=7, help='时间范围（天）')
    parser.add_argument('--category', type=str, default='all', help='拍卖类别')
    parser.add_argument('--limit', type=int, default=100, help='采集数量上限')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    collector = AliAuctionCollector()
    
    # 显示统计信息
    if args.stats:
        collector.get_statistics()
        return 0
    
    # 采集数据
    collector.collect_auctions(args.keyword, args.days, args.category, args.limit)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
