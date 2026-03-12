#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法拍数据分析脚本
对采集到的拍卖数据进行统计分析
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/auction-data/auction.db"

class AuctionAnalyzer:
    """拍卖数据分析器"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def analyze_ali_auctions(self):
        """分析阿里拍卖数据"""
        cursor = self.conn.cursor()
        
        print("="*70)
        print("阿里拍卖数据分析")
        print("="*70)
        print()
        
        # 1. 基本统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN auction_status = '拍卖中' THEN 1 END) as active,
                COUNT(CASE WHEN auction_status = '已成交' THEN 1 END) as completed,
                COUNT(CASE WHEN auction_status = '流拍' THEN 1 END) as failed,
                COUNT(CASE WHEN auction_status = '预展中' THEN 1 END) as prebidding
            FROM ali_auctions
        """)
        
        stats = cursor.fetchone()
        
        print("1. 基本统计")
        print("-" * 70)
        print(f"   总记录数: {stats['total']:>8,} 条")
        print(f"   拍卖中: {stats['active']:>8,} 条")
        print(f"   已成交: {stats['completed']:>8,} 条")
        print(f"   流拍: {stats['failed']:>8,} 条")
        print(f"   预展中: {stats['prebidding']:>8,} 条")
        if stats['completed'] > 0:
            success_rate = (stats['completed'] / stats['total']) * 100
            print(f"   成交率: {success_rate:>7.2f}%")
        print()
        
        # 2. 价格分析
        cursor.execute("""
            SELECT 
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(CASE WHEN auction_status = '已成交' THEN price END) as avg_completed_price
            FROM ali_auctions
            WHERE price IS NOT NULL
        """)
        
        price_stats = cursor.fetchone()
        
        print("2. 价格分析（单位：元）")
        print("-" * 70)
        print(f"   平均价格: {price_stats['avg_price']:>12,.0f}")
        print(f"   最低价格: {price_stats['min_price']:>12,.0f}")
        print(f"   最高价格: {price_stats['max_price']:>12,.0f}")
        if price_stats['avg_completed_price']:
            print(f"   成交均价: {price_stats['avg_completed_price']:>12,.0f}")
        print()
        
        # 3. 类别分析
        cursor.execute("""
            SELECT 
                    auction_type,
                    COUNT(*) as count,
                    AVG(price) as avg_price,
                    COUNT(CASE WHEN auction_status = '已成交' THEN 1 END) as completed
                FROM ali_auctions
                WHERE auction_type IS NOT NULL
                GROUP BY auction_type
                ORDER BY count DESC
        """)
        
        type_stats = cursor.fetchall()
        
        print("3. 类别分析")
        print("-" * 70)
        print(f"   {'类别':<15} {'数量':>8} {'平均价格':>15} {'成交数':>8}")
        print("-" * 70)
        
        for type_stat in type_stats:
            print(f"   {type_stat['auction_type']:<15} {type_stat['count']:>8,} "
                  f"{type_stat['avg_price']:>15,.0f} {type_stat['completed']:>8,}")
        print()
        
        # 4. 地区分析
        cursor.execute("""
            SELECT 
                    location,
                    COUNT(*) as count,
                    AVG(price) as avg_price
                FROM ali_auctions
                WHERE location IS NOT NULL
                GROUP BY location
                ORDER BY count DESC
                LIMIT 10
        """)
        
        location_stats = cursor.fetchall()
        
        print("4. 地区热力图（TOP 10）")
        print("-" * 70)
        print(f"   {'地区':<20} {'数量':>8} {'平均价格':>15}")
        print("-" * 70)
        
        for loc_stat in location_stats:
            print(f"   {loc_stat['location']:<20} {loc_stat['count']:>8,} "
                  f"{loc_stat['avg_price']:>15,.0f}")
        print()
        
        # 5. 时间趋势分析
        cursor.execute("""
            SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count,
                    SUM(CASE WHEN auction_status = '已成交' THEN 1 END) as completed
                FROM ali_auctions
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
        """)
        
        time_stats = cursor.fetchall()
        
        print("5. 最近7天趋势")
        print("-" * 70)
        print(f"   {'日期':<12} {'新增':>8} {'成交':>8}")
        print("-" * 70)
        
        for time_stat in time_stats:
            date_str = datetime.strptime(time_stat['date'], '%Y-%m-%d').strftime('%m-%d')
            print(f"   {date_str:<12} {time_stat['count']:>8,} {time_stat['completed']:>8,}")
        print()
        
        # 6. 成交率分析
        cursor.execute("""
            SELECT 
                    auction_type,
                    COUNT(*) as total,
                    COUNT(CASE WHEN auction_status = '已成交' THEN 1 END) as completed
                FROM ali_auctions
                WHERE auction_type IS NOT NULL
                GROUP BY auction_type
        """)
        
        completion_stats = cursor.fetchall()
        
        print("6. 类别成交率分析")
        print("-" * 70)
        print(f"   {'类别':<15} {'总数':>8} {'成交':>8} {'成交率':>10}")
        print("-" * 70)
        
        for comp_stat in completion_stats:
            if comp_stat['total'] > 0:
                rate = (comp_stat['completed'] / comp_stat['total']) * 100
                print(f"   {comp_stat['auction_type']:<15} {comp_stat['total']:>8,} "
                      f"{comp_stat['completed']:>8,} {rate:>9.1f}%")
        print()
        
        return {
            'total': stats['total'],
            'active': stats['active'],
            'completed': stats['completed'],
            'failed': stats['failed'],
            'avg_price': price_stats['avg_price']
        }
    
    def analyze_all_sources(self):
        """分析所有数据源"""
        cursor = self.conn.cursor()
        
        print("="*70)
        print("全数据源综合分析")
        print("="*70)
        print()
        
        # 1. 数据源对比
        sources = [
            ('ali_auctions', '阿里拍卖'),
            ('jd_auctions', '京东拍卖'),
            ('judicial_auctions', '司法拍卖')
        ]
        
        print("1. 数据源数据量对比")
        print("-" * 70)
        print(f"   {'数据源':<15} {'记录数':>12}")
        print("-" * 70)
        
        for table, name in sources:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {name:<15} {count:>12,} 条")
        print()
        
        # 2. 价格区间分布
        cursor.execute("""
            SELECT 
                    CASE 
                        WHEN price < 100000 THEN '10万以下'
                        WHEN price < 500000 THEN '10-50万'
                        WHEN price < 1000000 THEN '50-100万'
                        WHEN price < 5000000 THEN '100-500万'
                        ELSE '500万以上'
                    END as price_range,
                    COUNT(*) as count
                FROM ali_auctions
                WHERE price IS NOT NULL
                GROUP BY price_range
                ORDER BY price_range
        """)
        
        price_ranges = cursor.fetchall()
        
        print("2. 价格区间分布（阿里拍卖）")
        print("-" * 70)
        print(f"   {'价格区间':<15} {'数量':>12} {'占比':>10}")
        print("-" * 70)
        
        total = sum([r['count'] for r in price_ranges])
        for pr in price_ranges:
            percentage = (pr['count'] / total * 100) if total > 0 else 0
            print(f"   {pr['price_range']:<15} {pr['count']:>12,} {percentage:>9.1f}%")
        print()
        
        # 3. 最新采集记录
        for table, name in sources:
            cursor.execute(f"""
                SELECT title, price, auction_status, created_at 
                FROM {table}
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            records = cursor.fetchall()
            
            print(f"3. {name} - 最新5条记录")
            print("-" * 70)
            
            for i, record in enumerate(records, 1):
                status = record['auction_status'] or '未知'
                price = f"{record['price']:,.0f}元" if record['price'] else '未知'
                created = record['created_at'][:10]
                title = record['title'][:40] if record['title'] else '无标题'
                
                print(f"   {i}. [{status}] {title}")
                print(f"      价格: {price} | 时间: {created}")
            print()
    
    def generate_report(self):
        """生成分析报告"""
        print("="*70)
        print("生成分析报告")
        print("="*70)
        print()
        
        try:
            # 分析阿里拍卖
            ali_stats = self.analyze_ali_auctions()
            
            # 分析所有数据源
            self.analyze_all_sources()
            
            # 保存分析结果
            report = {
                'report_time': datetime.now().isoformat(),
                'ali_auctions': ali_stats,
                'summary': {
                    'total_records': ali_stats['total'],
                    'average_price': ali_stats['avg_price'],
                    'success_rate': (ali_stats['completed'] / ali_stats['total'] * 100) if ali_stats['total'] > 0 else 0
                }
            }
            
            # 保存到文件
            report_path = "/root/.openclaw/workspace/auction-data/analysis_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 分析报告已保存: {report_path}")
            print()
            
            return report
            
        except Exception as e:
            print(f"✗ 生成报告失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_to_csv(self, table='ali_auctions'):
        """导出数据到CSV"""
        cursor = self.conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        # 保存到CSV
        csv_path = f"/root/.openclaw/workspace/auction-data/{table}_export.csv"
        
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✓ 数据已导出: {csv_path}")
        print(f"  记录数: {len(rows)}")
        print(f"  字段数: {len(columns)}")
        print()
        
        return csv_path
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='法拍数据分析器')
    parser.add_argument('--table', type=str, default='ali_auctions', 
                       help='分析的数据表（默认：ali_auctions）')
    parser.add_argument('--export', action='store_true', 
                       help='导出数据到CSV')
    parser.add_argument('--all', action='store_true', 
                       help='分析所有数据源')
    parser.add_argument('--report', action='store_true', 
                       help='生成完整分析报告')
    
    args = parser.parse_args()
    
    print("="*70)
    print("法拍数据分析系统")
    print("="*70)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analyzer = AuctionAnalyzer()
    
    try:
        if args.all:
            # 分析所有数据源
            analyzer.analyze_all_sources()
        elif args.table:
            # 分析指定表
            analyzer.analyze_ali_auctions()
        
        # 导出数据
        if args.export:
            analyzer.export_to_csv(args.table)
        
        # 生成报告
        if args.report:
            analyzer.generate_report()
        
        # 显示提示
        print("="*70)
        print("分析完成！")
        print("="*70)
        print()
        print("使用提示：")
        print("  - 查看数据库: sqlite3 " + DB_PATH)
        print("  - 导出数据: python3 analyze_data.py --export")
        print("  - 分析所有源: python3 analyze_data.py --all")
        print("  - 生成报告: python3 analyze_data.py --report")
        print()
        
    except Exception as e:
        print(f"\n✗ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        analyzer.close()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
