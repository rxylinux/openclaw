#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建SQLite数据库和必要的表结构
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/auction-data/auction.db"
BACKUP_DIR = "/root/.openclaw/workspace/auction-data/backups"

def create_directories():
    """创建必要的目录"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"✓ 目录创建完成")

def backup_existing_database():
    """备份现有数据库"""
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"auction_{timestamp}.db")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✓ 数据库已备份到: {backup_path}")

def create_tables(conn):
    """创建数据库表结构"""
    cursor = conn.cursor()
    
    # 1. 阿里拍卖表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ali_auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            reserve_price REAL,
            current_price REAL,
            auction_status TEXT,
            auction_type TEXT,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            court TEXT,
            url TEXT UNIQUE,
            source TEXT DEFAULT 'ali',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. 京东拍卖表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jd_auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            current_bid REAL,
            bid_count INTEGER,
            auction_status TEXT,
            category TEXT,
            start_time TEXT,
            end_time TEXT,
            url TEXT UNIQUE,
            source TEXT DEFAULT 'jd',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. 司法拍卖表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS judicial_auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            assessment_price REAL,
            court_name TEXT,
            case_number TEXT,
            auction_date TEXT,
            auction_location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            source TEXT DEFAULT 'judicial',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. 房产交易表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS property_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            unit_price REAL,
            area REAL,
            rooms INTEGER,
            floor INTEGER,
            building_age INTEGER,
            location TEXT,
            district TEXT,
            listing_type TEXT,
            listing_source TEXT,
            url TEXT UNIQUE,
            source TEXT DEFAULT 'property',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 5. 价格分析表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            location TEXT,
            avg_price REAL,
            min_price REAL,
            max_price REAL,
            median_price REAL,
            sample_count INTEGER,
            analysis_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 6. 采集日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            items_collected INTEGER,
            items_new INTEGER,
            items_updated INTEGER,
            status TEXT,
            error_message TEXT,
            execution_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 7. 创建索引（逐条创建）
    indexes = [
        ("idx_ali_price", "CREATE INDEX IF NOT EXISTS idx_ali_price ON ali_auctions(price)"),
        ("idx_ali_status", "CREATE INDEX IF NOT EXISTS idx_ali_status ON ali_auctions(auction_status)"),
        ("idx_ali_created", "CREATE INDEX IF NOT EXISTS idx_ali_created ON ali_auctions(created_at)"),
        
        ("idx_jd_price", "CREATE INDEX IF NOT EXISTS idx_jd_price ON jd_auctions(price)"),
        ("idx_jd_status", "CREATE INDEX IF NOT EXISTS idx_jd_status ON jd_auctions(auction_status)"),
        ("idx_jd_created", "CREATE INDEX IF NOT EXISTS idx_jd_created ON jd_auctions(created_at)"),
        
        ("idx_judicial_price", "CREATE INDEX IF NOT EXISTS idx_judicial_price ON judicial_auctions(price)"),
        ("idx_judicial_court", "CREATE INDEX IF NOT EXISTS idx_judicial_court ON judicial_auctions(court_name)"),
        ("idx_judicial_created", "CREATE INDEX IF NOT EXISTS idx_judicial_created ON judicial_auctions(created_at)"),
        
        ("idx_property_price", "CREATE INDEX IF NOT EXISTS idx_property_price ON property_listings(price)"),
        ("idx_property_location", "CREATE INDEX IF NOT EXISTS idx_property_location ON property_listings(location)"),
        ("idx_property_district", "CREATE INDEX IF NOT EXISTS idx_property_district ON property_listings(district)"),
        ("idx_property_created", "CREATE INDEX IF NOT EXISTS idx_property_created ON property_listings(created_at)"),
        
        ("idx_analysis_date", "CREATE INDEX IF NOT EXISTS idx_analysis_date ON price_analysis(analysis_date)"),
        ("idx_logs_created", "CREATE INDEX IF NOT EXISTS idx_logs_created ON collection_logs(created_at)")
    ]
    
    created_indexes = 0
    for index_name, sql in indexes:
        try:
            cursor.execute(sql)
            created_indexes += 1
        except Exception as e:
            print(f"  ✗ 创建索引 {index_name} 失败: {e}")
    
    conn.commit()
    print(f"✓ 索引创建完成 ({created_indexes}/{len(indexes)}）")
    print(f"✓ 数据表创建完成")
    print(f"  - ali_auctions")
    print(f"  - jd_auctions")
    print(f"  - judicial_auctions")
    print(f"  - property_listings")
    print(f"  - price_analysis")
    print(f"  - collection_logs")

def insert_sample_data(conn):
    """插入示例数据"""
    cursor = conn.cursor()
    
    # 示例：阿里拍卖数据
    sample_data = [
        ('示例法拍房产 - 北京市朝阳区', 1000000.00, 800000.00, None, '拍卖中', '法拍房', '2026-03-10 10:00', '2026-03-20 10:00', '北京市朝阳区', '北京市朝阳区人民法院', 'https://paimai.taobao.com/sample1', 'ali'),
        ('示例司法拍卖 - 车辆', 150000.00, None, None, '预展中', '车辆', '2026-03-15 14:00', '2026-03-25 14:00', '上海市浦东新区', '上海市第一中级人民法院', 'https://paimai.taobao.com/sample2', 'ali'),
    ]
    
    for item in sample_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ali_auctions 
                (title, price, reserve_price, auction_status, auction_type, 
                 start_time, end_time, location, court, url, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, item)
        except Exception as e:
            print(f"✗ 插入示例数据失败: {e}")
    
    conn.commit()
    print(f"✓ 示例数据插入完成")

def display_database_info(conn):
    """显示数据库信息"""
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("数据库信息")
    print("="*50)
    print(f"数据库路径: {DB_PATH}")
    
    # 统计各表记录数
    tables = ['ali_auctions', 'jd_auctions', 'judicial_auctions', 'property_listings']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} 条记录")
    
    # 数据库大小
    size = os.path.getsize(DB_PATH) / 1024  # KB
    print(f"数据库大小: {size:.2f} KB")
    print("="*50 + "\n")

def main():
    """主函数"""
    print("="*50)
    print("法拍数据采集系统 - 数据库初始化")
    print("="*50)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 创建目录
        create_directories()
        
        # 2. 备份现有数据库
        backup_existing_database()
        
        # 3. 连接数据库
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ 数据库连接成功")
        
        # 4. 创建表结构
        create_tables(conn)
        
        # 5. 插入示例数据
        insert_sample_data(conn)
        
        # 6. 显示数据库信息
        display_database_info(conn)
        
        # 7. 关闭连接
        conn.close()
        print(f"✓ 数据库连接已关闭")
        
        print("\n" + "="*50)
        print("初始化完成！")
        print("="*50)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据库位置: {DB_PATH}")
        print()
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
