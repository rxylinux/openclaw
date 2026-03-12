#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法拍数据Web看板
提供实时数据可视化和分析展示
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/auction-data/auction.db"

class AuctionDashboard:
    """法拍数据看板"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def get_overview(self):
        """获取数据概览"""
        cursor = self.conn.cursor()
        
        # 各数据源记录数
        cursor.execute("""
            SELECT 'ali_auctions' as source, COUNT(*) as count FROM ali_auctions
            UNION ALL
            SELECT 'jd_auctions' as source, COUNT(*) as count FROM jd_auctions
            UNION ALL
            SELECT 'judicial_auctions' as source, COUNT(*) as count FROM judicial_auctions
            UNION ALL
            SELECT 'property_listings' as source, COUNT(*) as count FROM property_listings
        """)
        
        source_counts = {row['source']: row['count'] for row in cursor.fetchall()}
        total = sum(source_counts.values())
        
        # 最近采集记录
        cursor.execute("""
            SELECT source, items_collected, items_new, status, created_at
            FROM collection_logs
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recent_logs = cursor.fetchall()
        
        return {
            'total_records': total,
            'source_counts': source_counts,
            'recent_logs': recent_logs
        }
    
    def get_price_trends(self, days=30):
        """获取价格趋势"""
        cursor = self.conn.cursor()
        
        # 阿里拍卖价格趋势
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                AVG(price) as avg_price,
                COUNT(*) as count
            FROM ali_auctions
            WHERE price IS NOT NULL
                AND created_at >= datetime('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """.format(days))
        
        price_trends = cursor.fetchall()
        
        # 转换为JSON友好的格式
        trends = []
        for row in price_trends:
            trends.append({
                'date': row['date'],
                'avg_price': float(row['avg_price']) if row['avg_price'] else 0,
                'count': row['count']
            })
        
        return trends
    
    def get_status_distribution(self):
        """获取状态分布"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                auction_status,
                COUNT(*) as count,
                AVG(price) as avg_price
            FROM ali_auctions
            WHERE auction_status IS NOT NULL
            GROUP BY auction_status
        """)
        
        status_dist = cursor.fetchall()
        
        distribution = []
        for row in status_dist:
            distribution.append({
                'status': row['auction_status'],
                'count': row['count'],
                'avg_price': float(row['avg_price']) if row['avg_price'] else 0
            })
        
        return distribution
    
    def get_category_analysis(self):
        """获取类别分析"""
        cursor = self.conn.cursor()
        
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
        
        category_stats = cursor.fetchall()
        
        categories = []
        for row in category_stats:
            success_rate = (row['completed'] / row['count'] * 100) if row['count'] > 0 else 0
            categories.append({
                'category': row['auction_type'],
                'count': row['count'],
                'avg_price': float(row['avg_price']) if row['avg_price'] else 0,
                'success_rate': success_rate
            })
        
        return categories
    
    def get_location_heatmap(self):
        """获取地区热力图数据"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                location,
                COUNT(*) as count,
                AVG(price) as avg_price
            FROM ali_auctions
            WHERE location IS NOT NULL AND location != ''
            GROUP BY location
            ORDER BY count DESC
            LIMIT 20
        """)
        
        location_stats = cursor.fetchall()
        
        locations = []
        for row in location_stats:
            locations.append({
                'location': row['location'],
                'count': row['count'],
                'avg_price': float(row['avg_price']) if row['avg_price'] else 0
            })
        
        return locations
    
    def generate_html_dashboard(self):
        """生成HTML看板"""
        # 获取数据
        overview = self.get_overview()
        price_trends = self.get_price_trends()
        status_dist = self.get_status_distribution()
        category_stats = self.get_category_analysis()
        location_heatmap = self.get_location_heatmap()
        
        # 生成HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法拍数据看板</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; font-size: 16px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #667eea; margin-top: 0; font-size: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .stat-item {{ text-align: center; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; color: #333; }}
        .status-active {{ color: #28a745; font-weight: bold; }}
        .status-completed {{ color: #17a2b8; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .progress-bar {{ height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ 法拍数据看板</h1>
            <p>实时监控和分析法拍、司法拍卖、房产交易数据</p>
            <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <!-- 数据概览 -->
        <div class="card">
            <h2>📊 数据概览</h2>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-number">{overview['total_records']:,}</div>
                    <div class="stat-label">总记录数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{overview['source_counts'].get('ali_auctions', 0):,}</div>
                    <div class="stat-label">阿里拍卖</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{overview['source_counts'].get('jd_auctions', 0):,}</div>
                    <div class="stat-label">京东拍卖</div>
                </div>
            </div>
        </div>
        
        <!-- 状态分布 -->
        <div class="card">
            <h2>📈 状态分布</h2>
            <table>
                <thead>
                    <tr>
                        <th>状态</th>
                        <th>数量</th>
                        <th>平均价格</th>
                        <th>占比</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        total_status = sum([d['count'] for d in status_dist])
        for status in status_dist:
            percentage = (status['count'] / total_status * 100) if total_status > 0 else 0
            status_class = 'status-active' if status['status'] == '拍卖中' else ('status-completed' if status['status'] == '已成交' else 'status-failed')
            
            html += f"""
                    <tr>
                        <td class="{status_class}">{status['status']}</td>
                        <td>{status['count']:,}</td>
                        <td>{status['avg_price']:,.0f}元</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <!-- 类别分析 -->
        <div class="card">
            <h2>📂 类别分析</h2>
            <table>
                <thead>
                    <tr>
                        <th>类别</th>
                        <th>数量</th>
                        <th>平均价格</th>
                        <th>成交率</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for category in category_stats:
            html += f"""
                    <tr>
                        <td>{category['category']}</td>
                        <td>{category['count']:,}</td>
                        <td>{category['avg_price']:,.0f}元</td>
                        <td>{category['success_rate']:.1f}%</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <!-- 地区热力图 -->
        <div class="card">
            <h2>🗺️ 地区热力图（TOP 10）</h2>
            <table>
                <thead>
                    <tr>
                        <th>地区</th>
                        <th>数量</th>
                        <th>平均价格</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for location in location_heatmap[:10]:
            html += f"""
                    <tr>
                        <td>{location['location']}</td>
                        <td>{location['count']}</td>
                        <td>{location['avg_price']:,.0f}元</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <!-- 最近采集日志 -->
        <div class="card">
            <h2>📝 最近采集日志</h2>
            <table>
                <thead>
                    <tr>
                        <th>数据源</th>
                        <th>采集数量</th>
                        <th>新增</th>
                        <th>状态</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for log in overview['recent_logs']:
            status_class = 'status-active' if log['status'] == 'success' else 'status-failed'
            html += f"""
                    <tr>
                        <td>{log['source']}</td>
                        <td>{log['items_collected']}</td>
                        <td>{log['items_new']}</td>
                        <td class="{status_class}">{log['status']}</td>
                        <td>{log['created_at']}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>⚠️ 本系统仅采集和分析公开数据，请遵守相关法律法规</p>
            <p>⚠️ 数据来源：阿里拍卖、京东拍卖、司法拍卖平台、房产交易网站</p>
            <p>⚠️ 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 自动刷新（每5分钟）
        setTimeout(function() {{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
        
        return html
    
    def export_json_data(self):
        """导出数据为JSON格式"""
        data = {
            'overview': self.get_overview(),
            'price_trends': self.get_price_trends(),
            'status_distribution': self.get_status_distribution(),
            'category_analysis': self.get_category_analysis(),
            'location_heatmap': self.get_location_heatmap(),
            'export_time': datetime.now().isoformat()
        }
        
        # 保存JSON文件
        json_path = f"/root/.openclaw/workspace/auction-data/dashboard_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='法拍数据Web看板')
    parser.add_argument('--html', action='store_true', help='生成HTML看板')
    parser.add_argument('--json', action='store_true', help='导出JSON数据')
    parser.add_argument('--port', type=int, default=8888, help='Web服务器端口')
    
    args = parser.parse_args()
    
    print("="*70)
    print("法拍数据Web看板")
    print("="*70)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    dashboard = AuctionDashboard()
    
    try:
        # 生成HTML看板
        if args.html:
            print("生成HTML看板...")
            html = dashboard.generate_html_dashboard()
            
            html_path = "/root/.openclaw/workspace/auction-data/dashboard.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✓ HTML看板已保存: {html_path}")
            print(f"  文件大小: {len(html.encode('utf-8')) / 1024:.1f} KB")
        
        # 导出JSON数据
        if args.json:
            print("导出JSON数据...")
            json_path = dashboard.export_json_data()
            print(f"✓ JSON数据已保存: {json_path}")
        
        # 如果都未指定，默认生成HTML
        if not args.html and not args.json:
            print("默认生成HTML看板...")
            html = dashboard.generate_html_dashboard()
            
            html_path = "/root/.openclaw/workspace/auction-data/dashboard.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✓ HTML看板已保存: {html_path}")
            print()
            print("使用提示：")
            print("  1. 在浏览器中打开 dashboard.html 查看看板")
            print("  2. 看板每5分钟自动刷新")
            print("  3. 使用 --json 参数导出JSON数据")
            print()
        
        print("="*70)
        print("看板生成完成！")
        print("="*70)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    except Exception as e:
        print(f"\n✗ 看板生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        dashboard.close()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
