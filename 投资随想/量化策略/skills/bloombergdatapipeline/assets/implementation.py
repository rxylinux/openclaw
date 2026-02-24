"""BLOOMBERGDATAPIPELINE - 量化策略实现
自动从原始文档提取的Python代码
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import websocket  # pip install websocket-client
import aiohttp  # pip install aiohttp
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_batch
import pytz

@dataclass
class DataSource:
    """数据源定义"""
    name: str
    type: str  # 'price', 'fundamental', 'sentiment', 'alternative'
    real_time: bool
    provider: str  # 'bloomberg', 'yahoo', 'alphavantage', 'polygon.io', etc.
    api_endpoint: Optional[str]
    auth_required: bool
    update_frequency: str  # 'real-time', 'minute', 'daily', 'weekly', 'monthly'
    coverage: List[str]  # 涵盖的资产类别
    latency_ms: int = 0  # 数据延迟（毫秒）
    cost_level: str = 'free'  # 'free', 'low', 'medium', 'high'
    reliability: float = 1.0  # 可靠性评分 [0, 1]

class DataSourceRegistry:
    """数据源注册表"""
    
    def __init__(self):
        self.sources = {}
        self._initialize_sources()
        
    def _initialize_sources(self):
        """初始化所有数据源"""
        # 价格数据源
        self.sources['bloomberg_realtime'] = DataSource(
            name='Bloomberg Real-time',
            type='price',
            real_time=True,
            provider='bloomberg',
            api_endpoint='wss://api.bloomberg.com/stream',
            auth_required=True,
            update_frequency='real-time',
            coverage=['equities', 'futures', 'forex', 'options', 'indices'],
            latency_ms=5,
            cost_level='high',
            reliability=0.99
        )
        
        self.sources['yahoo_finance'] = DataSource(
            name='Yahoo Finance',
            type='price',
            real_time=False,
            provider='yahoo',
            api_endpoint='https://query1.finance.yahoo.com/v8/finance/chart/',
            auth_required=False,
            update_frequency='daily',
            coverage=['equities', 'etfs', 'forex', 'indices'],
            latency_ms=1000,
            cost_level='free',
            reliability=0.95
        )
        
        self.sources['polygon_io'] = DataSource(
            name='Polygon.io',
            type='price',
            real_time=True,
            provider='polygon',
            api_endpoint='https://api.polygon.io/v2',
            auth_required=True,
            update_frequency='real-time',
            coverage=['equities', 'options', 'forex'],
            latency_ms=15,
            cost_level='medium',
            reliability=0.97
        )
        
        # 基本面数据源
        self.sources['bloomberg_fundamentals'] = DataSource(
            name='Bloomberg Fundamentals',
            type='fundamental',
            real_time=False,
            provider='bloomberg',
            api_endpoint='https://api.bloomberg.com/api/v1/fundamentals',
            auth_required=True,
            update_frequency='quarterly',
            coverage=['equities', 'etfs'],
            latency_ms=0,
            cost_level='high',
            reliability=0.98
        )
        
        self.sources['finnhub'] = DataSource(
            name='Finnhub',
            type='fundamental',
            real_time=False,
            provider='finnhub',
            api_endpoint='https://finnhub.io/api/v1',
            auth_required=True,
            update_frequency='quarterly',
            coverage=['equities'],
            latency_ms=0,
            cost_level='low',
            reliability=0.92
        )
        
        # 情绪数据源
        self.sources['twitter_sentiment'] = DataSource(
            name='Twitter Sentiment',
            type='sentiment',
            real_time=True,
            provider='twitter',
            api_endpoint='https://api.twitter.com/2',
            auth_required=True,
            update_frequency='hourly',
            coverage=['equities', 'crypto'],
            latency_ms=300,
            cost_level='medium',
            reliability=0.85
        )
        
        self.sources['news_sentiment'] = DataSource(
            name='News Sentiment',
            type='sentiment',
            real_time=False,
            provider='newsapi',
            api_endpoint='https://newsapi.org/v2',
            auth_required=True,
            update_frequency='daily',
            coverage=['equities', 'sectors', 'indices'],
            latency_ms=0,
            cost_level='low',
            reliability=0.80
        )
        
        # 另类数据源
        self.sources['satellite_imagery'] = DataSource(
            name='Satellite Imagery',
            type='alternative',
            real_time=False,
            provider='planet',
            api_endpoint='https://api.planet.com/v1',
            auth_required=True,
            update_frequency='weekly',
            coverage=['retail', 'energy', 'agriculture'],
            latency_ms=0,
            cost_level='high',
            reliability=0.90
        )
        
        self.sources['credit_card_data'] = DataSource(
            name='Credit Card Spending',
            type='alternative',
            real_time=False,
            provider='proprietary',
            api_endpoint=None,
            auth_required=True,
            update_frequency='monthly',
            coverage=['consumer', 'retail'],
            latency_ms=0,
            cost_level='high',
            reliability=0.95
        )
        
    def get_source(self, name: str) -> Optional[DataSource]:
        """获取数据源"""
        return self.sources.get(name)
        
    def get_sources_by_type(self, data_type: str) -> List[DataSource]:
        """按类型获取数据源"""
        return [s for s in self.sources.values() if s.type == data_type]
        
    def get_realtime_sources(self) -> List[DataSource]:
        """获取实时数据源"""
        return [s for s in self.sources.values() if s.real_time]
        
    def get_sources_by_coverage(self, coverage: str) -> List[DataSource]:
        """按覆盖范围获取数据源"""
        return [s for s in self.sources.values() if coverage in s.coverage]

class RealTimeDataFeed:
    """实时数据流"""
    
    def __init__(self,
                 source: DataSource,
                 symbols: List[str],
                 max_reconnect_attempts: int = 5,
                 heartbeat_interval: int = 30):
        self.source = source
        self.symbols = symbols
        self.max_reconnect_attempts = max_reconnect_attempts
        self.heartbeat_interval = heartbeat_interval
        
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.subscribers = {}
        self.message_queue = asyncio.Queue()
        
    async def connect(self):
        """建立WebSocket连接"""
        ws_url = self.source.api_endpoint
        headers = {}
        
        # 添加认证头
        if self.source.auth_required:
            # 这里应该从安全存储获取API密钥
            headers['Authorization'] = 'Bearer YOUR_API_KEY'
            
        try:
            self.ws = await websocket.connect(ws_url, extra_headers=headers)
            self.connected = True
            self.reconnect_attempts = 0
            
            # 启动消息处理
            asyncio.create_task(self._receive_messages())
            asyncio.create_task(self._send_heartbeat())
            
            print(f"Connected to {self.source.name}")
            
        except Exception as e:
            print(f"Connection failed: {e}")
            await self._reconnect()
            
    async def _reconnect(self):
        """重连逻辑"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("Max reconnect attempts reached")
            return
            
        self.reconnect_attempts += 1
        wait_time = min(2 ** self.reconnect_attempts, 60)  # 指数退避，最大60秒
        
        print(f"Reconnecting in {wait_time} seconds (attempt {self.reconnect_attempts})")
        await asyncio.sleep(wait_time)
        
        await self.connect()
        
    async def _receive_messages(self):
        """接收和处理消息"""
        try:
            async for message in self.ws:
                await self._process_message(message)
        except websocket.ConnectionClosed:
            print(f"Connection to {self.source.name} closed")
            self.connected = False
            await self._reconnect()
            
    async def _process_message(self, message: Any):
        """处理单条消息"""
        try:
            if isinstance(message, str):
                data = json.loads(message)
            else:
                data = message
                
            # 根据消息类型处理
            if data.get('type') == 'quote':
                await self._handle_quote(data['data'])
            elif data.get('type') == 'trade':
                await self._handle_trade(data['data'])
            elif data.get('type') == 'heartbeat':
                self._handle_heartbeat()
            else:
                # 通知所有订阅者
                await self._notify_subscribers(data)
                
        except Exception as e:
            print(f"Error processing message: {e}")
            
    async def _handle_quote(self, quote_data: Dict):
        """处理报价数据"""
        symbol = quote_data['symbol']
        timestamp = datetime.fromtimestamp(quote_data['timestamp'] / 1000)
        
        # 构造标准化的价格对象
        price_update = {
            'symbol': symbol,
            'timestamp': timestamp,
            'bid': quote_data.get('bid'),
            'ask': quote_data.get('ask'),
            'last': quote_data.get('last'),
            'volume': quote_data.get('volume'),
            'source': self.source.name
        }
        
        # 发送到消息队列
        await self.message_queue.put(price_update)
        
        # 通知订阅者
        if symbol in self.subscribers:
            for callback in self.subscribers[symbol]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(price_update)
                    else:
                        callback(price_update)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")
                    
    async def _handle_trade(self, trade_data: Dict):
        """处理成交数据"""
        # 类似于报价处理
        pass
        
    async def _send_heartbeat(self):
        """发送心跳"""
        while self.connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                heartbeat = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                }
                await self.ws.send(json.dumps(heartbeat))
            except Exception as e:
                print(f"Heartbeat error: {e}")
                break
                
    def _handle_heartbeat(self):
        """处理心跳响应"""
        # 重置心跳计时器
        pass
        
    def subscribe(self, symbol: str, callback):
        """订阅特定股票的数据"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)
        
    def unsubscribe(self, symbol: str, callback):
        """取消订阅"""
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
            
            if not self.subscribers[symbol]:
                del self.subscribers[symbol]
                
    async def get_latest_quote(self, symbol: str) -> Optional[Dict]:
        """获取最新报价"""
        # 从消息队列获取最新的该股票数据
        # 实际实现需要维护最近报价的缓存
        return None
        
    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
        self.connected = False

class DatabaseSchema:
    """数据库架构"""
    
    # 股票代码表
    CREATE_SYMBOLS_TABLE = """
    CREATE TABLE IF NOT EXISTS symbols (
        symbol_id SERIAL PRIMARY KEY,
        ticker VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        exchange VARCHAR(20) NOT NULL,
        sector VARCHAR(50),
        industry VARCHAR(50),
        market_cap BIGINT,
        listed_date DATE,
        delisted_date DATE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE_SYMBOLS_INDEXES = [
        "CREATE INDEX idx_symbols_ticker ON symbols(ticker);",
        "CREATE INDEX idx_symbols_sector ON symbols(sector);",
        "CREATE INDEX idx_symbols_is_active ON symbols(is_active);"
    ]
    
    # 实时价格表（时序扩展）
    CREATE_TICK_TABLE = """
    CREATE TABLE IF NOT EXISTS tick_data (
        id BIGSERIAL PRIMARY KEY,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        timestamp TIMESTAMP NOT NULL,
        price NUMERIC(15, 6),
        bid NUMERIC(15, 6),
        ask NUMERIC(15, 6),
        bid_size BIGINT,
        ask_size BIGINT,
        volume BIGINT,
        source VARCHAR(50) NOT NULL
    );
    """
    
    CREATE_TICK_INDEXES = [
        "CREATE INDEX idx_tick_symbol_timestamp ON tick_data(symbol_id, timestamp DESC);",
        "CREATE INDEX idx_tick_timestamp ON tick_data(timestamp DESC);"
    ]
    
    # 分钟线表（时序扩展）
    CREATE_OHLCV_TABLE = """
    CREATE TABLE IF NOT EXISTS ohlcv_1m (
        time TIMESTAMP NOT NULL,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        open NUMERIC(15, 6),
        high NUMERIC(15, 6),
        low NUMERIC(15, 6),
        close NUMERIC(15, 6),
        volume BIGINT,
        vwap NUMERIC(15, 6),
        num_trades INTEGER,
        PRIMARY KEY (time, symbol_id)
    );
    """
    
    CREATE_OHLCV_INDEXES = [
        "CREATE INDEX idx_ohlcv_symbol_time ON ohlcv_1m(symbol_id, time DESC);",
        "CREATE INDEX idx_ohlcv_time ON ohlcv_1m(time DESC);"
    ]
    
    # 日线表（时序扩展）
    CREATE_DAILY_TABLE = """
    CREATE TABLE IF NOT EXISTS daily_data (
        date DATE NOT NULL,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        open NUMERIC(15, 6),
        high NUMERIC(15, 6),
        low NUMERIC(15, 6),
        close NUMERIC(15, 6),
        adjusted_close NUMERIC(15, 6),
        volume BIGINT,
        PRIMARY KEY (date, symbol_id)
    );
    """
    
    CREATE_DAILY_INDEXES = [
        "CREATE INDEX idx_daily_symbol_date ON daily_data(symbol_id, date DESC);",
        "CREATE INDEX idx_daily_date ON daily_data(date DESC);"
    ]
    
    # 分红数据表
    CREATE_DIVIDEND_TABLE = """
    CREATE TABLE IF NOT EXISTS dividends (
        id SERIAL PRIMARY KEY,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        ex_date DATE NOT NULL,
        payment_date DATE NOT NULL,
        amount NUMERIC(15, 6),
        frequency VARCHAR(10),
        source VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_DIVIDEND_INDEXES = [
        "CREATE INDEX idx_dividends_symbol_exdate ON dividends(symbol_id, ex_date DESC);"
    ]
    
    # 企业行动表
    CREATE_CORP_ACTION_TABLE = """
    CREATE TABLE IF NOT EXISTS corporate_actions (
        id SERIAL PRIMARY KEY,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        action_type VARCHAR(20) NOT NULL,  -- 'split', 'merger', 'spinoff', 'dividend', 'name_change'
        effective_date DATE NOT NULL,
        details JSONB,
        processed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_CORP_ACTION_INDEXES = [
        "CREATE INDEX idx_corp_actions_symbol_date ON corporate_actions(symbol_id, effective_date DESC);",
        "CREATE INDEX idx_corp_actions_processed ON corporate_actions(processed, effective_date);"
    ]
    
    # 技术指标表（特征存储）
    CREATE_FEATURES_TABLE = """
    CREATE TABLE IF NOT EXISTS technical_features (
        date DATE NOT NULL,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        PRIMARY KEY (date, symbol_id),
        -- 技术指标
        sma_5 NUMERIC(15, 6),
        sma_10 NUMERIC(15, 6),
        sma_20 NUMERIC(15, 6),
        sma_50 NUMERIC(15, 6),
        sma_200 NUMERIC(15, 6),
        ema_12 NUMERIC(15, 6),
        ema_26 NUMERIC(15, 6),
        rsi_14 NUMERIC(10, 4),
        macd NUMERIC(15, 6),
        macd_signal NUMERIC(15, 6),
        macd_histogram NUMERIC(15, 6),
        bollinger_upper NUMERIC(15, 6),
        bollinger_middle NUMERIC(15, 6),
        bollinger_lower NUMERIC(15, 6),
        atr_14 NUMERIC(15, 6),
        -- 波动率
        volatility_20 NUMERIC(10, 4),
        volatility_60 NUMERIC(10, 4),
        -- 成交量指标
        volume_sma_20 BIGINT,
        volume_ratio_5 REAL,
        -- 动量
        momentum_20d NUMERIC(15, 6),
        momentum_60d NUMERIC(15, 6),
        -- 标准化指标
        price_zscore NUMERIC(10, 4),
        volume_zscore NUMERIC(10, 4),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 基本面数据表
    CREATE_FUNDAMENTALS_TABLE = """
    CREATE TABLE IF NOT EXISTS fundamentals (
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        report_date DATE NOT NULL,
        period_type VARCHAR(10) NOT NULL,  -- 'quarterly', 'annual'
        period_end_date DATE NOT NULL,
        -- 损益表
        revenue BIGINT,
        gross_profit BIGINT,
        operating_income BIGINT,
        net_income BIGINT,
        eps NUMERIC(10, 4),
        eps_diluted NUMERIC(10, 4),
        -- 资产负债表
        total_assets BIGINT,
        total_liabilities BIGINT,
        shareholders_equity BIGINT,
        -- 现金流
        operating_cash_flow BIGINT,
        free_cash_flow BIGINT,
        -- 关键比率
        pe_ratio NUMERIC(10, 4),
        pb_ratio NUMERIC(10, 4),
        ps_ratio NUMERIC(10, 4),
        debt_to_equity NUMERIC(10, 4),
        current_ratio NUMERIC(10, 4),
        roe NUMERIC(10, 4),
        roa NUMERIC(10, 4),
        profit_margin NUMERIC(10, 4),
        PRIMARY KEY (symbol_id, report_date, period_type)
    );
    """
    
    CREATE_FUNDAMENTALS_INDEXES = [
        "CREATE INDEX idx_fundamentals_symbol_date ON fundamentals(symbol_id, report_date DESC);",
        "CREATE INDEX idx_fundamentals_date ON fundamentals(report_date DESC);"
    ]
    
    # 数据质量日志表
    CREATE_DATA_QUALITY_TABLE = """
    CREATE TABLE IF NOT EXISTS data_quality_log (
        id SERIAL PRIMARY KEY,
        symbol_id INTEGER REFERENCES symbols(symbol_id),
        data_type VARCHAR(20) NOT NULL,  -- 'price', 'volume', 'fundamental'
        issue_type VARCHAR(50) NOT NULL,  -- 'missing_value', 'outlier', 'inconsistency'
        issue_date TIMESTAMP NOT NULL,
        details JSONB,
        severity VARCHAR(10),  -- 'low', 'medium', 'high', 'critical'
        resolved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    @staticmethod
    def get_all_create_statements() -> List[str]:
        """获取所有创建语句"""
        return [
            DatabaseSchema.CREATE_SYMBOLS_TABLE,
            DatabaseSchema.CREATE_TICK_TABLE,
            DatabaseSchema.CREATE_OHLCV_TABLE,
            DatabaseSchema.CREATE_DAILY_TABLE,
            DatabaseSchema.CREATE_DIVIDEND_TABLE,
            DatabaseSchema.CREATE_CORP_ACTION_TABLE,
            DatabaseSchema.CREATE_FEATURES_TABLE,
            DatabaseSchema.CREATE_FUNDAMENTALS_TABLE,
            DatabaseSchema.CREATE_DATA_QUALITY_TABLE
        ]
    
    @staticmethod
    def get_all_index_statements() -> List[str]:
        """获取所有索引创建语句"""
        statements = []
        statements.extend(DatabaseSchema.CREATE_SYMBOLS_INDEXES)
        statements.extend(DatabaseSchema.CREATE_TICK_INDEXES)
        statements.extend(DatabaseSchema.CREATE_OHLCV_INDEXES)
        statements.extend(DatabaseSchema.CREATE_DAILY_INDEXES)
        statements.extend(DatabaseSchema.CREATE_DIVIDEND_INDEXES)
        statements.extend(DatabaseSchema.CREATE_CORP_ACTION_INDEXES)
        statements.extend(DatabaseSchema.CREATE_FUNDAMENTALS_INDEXES)
        return statements

import psycopg2
from psycopg2.extras import execute_values
import psycopg2.extras
import psycopg2.pool
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self,
                 dbname: str,
                 user: str,
                 password: str,
                 host: str = 'localhost',
                 port: int = 5432,
                 pool_size: int = 10):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.pool_size = pool_size
        
        self.pool = None
        
    def connect(self):
        """创建连接池"""
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=self.pool_size,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.dbname
        )
        print(f"Connected to PostgreSQL database: {self.dbname}")
        
    def close(self):
        """关闭连接池"""
        if self.pool:
            self.pool.closeall()
            print("Database connection pool closed")
            
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = self.pool.getconn()
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
            
    def initialize_database(self):
        """初始化数据库架构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 创建所有表
                for statement in DatabaseSchema.get_all_create_statements():
                    cursor.execute(statement)
                    
                # 创建所有索引
                for statement in DatabaseSchema.get_all_index_statements():
                    cursor.execute(statement)
                    
                conn.commit()
                print("Database schema initialized successfully")
                
            except Exception as e:
                conn.rollback()
                print(f"Error initializing database: {e}")
                raise
                
    def insert_symbol(self,
                   ticker: str,
                   name: str,
                   exchange: str,
                   sector: Optional[str] = None,
                   industry: Optional[str] = None,
                   market_cap: Optional[int] = None) -> int:
        """插入股票代码"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO symbols (ticker, name, exchange, sector, industry, market_cap, listed_date)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
                ON CONFLICT (ticker) DO NOTHING
                RETURNING symbol_id
            """, (ticker, name, exchange, sector, industry, market_cap))
            
            conn.commit()
            return cursor.fetchone()[0] if cursor.rowcount > 0 else None
            
    def insert_tick_data(self,
                       symbol_id: int,
                       timestamp: datetime,
                       price: float,
                       bid: Optional[float] = None,
                       ask: Optional[float] = None,
                       bid_size: Optional[int] = None,
                       ask_size: Optional[int] = None,
                       volume: Optional[int] = None,
                       source: str = 'bloomberg') -> bool:
        """插入Tick数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tick_data 
                (symbol_id, timestamp, price, bid, ask, bid_size, ask_size, volume, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (symbol_id, timestamp, price, bid, ask, bid_size, ask_size, volume, source))
            
            conn.commit()
            return True
            
    def bulk_insert_ticks(self,
                        data: List[Dict]) -> int:
        """批量插入Tick数据"""
        if not data:
            return 0
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            values = [
                (
                    item['symbol_id'],
                    item['timestamp'],
                    item['price'],
                    item.get('bid'),
                    item.get('ask'),
                    item.get('bid_size'),
                    item.get('ask_size'),
                    item.get('volume'),
                    item.get('source', 'bloomberg')
                )
                for item in data
            ]
            
            execute_values(
                cursor,
                """
                INSERT INTO tick_data 
                (symbol_id, timestamp, price, bid, ask, bid_size, ask_size, volume, source)
                VALUES %s
                """,
                values
            )
            
            conn.commit()
            return len(values)
            
    def insert_ohlcv(self,
                     symbol_id: int,
                     time: datetime,
                     open_price: float,
                     high_price: float,
                     low_price: float,
                     close_price: float,
                     volume: int,
                     vwap: Optional[float] = None,
                     num_trades: Optional[int] = None) -> bool:
        """插入OHLCV数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ohlcv_1m 
                (time, symbol_id, open, high, low, close, volume, vwap, num_trades)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (time, symbol_id) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    vwap = EXCLUDED.vwap,
                    num_trades = EXCLUDED.num_trades
            """, (time, symbol_id, open_price, high_price, low_price, close_price,
                  volume, vwap, num_trades))
            
            conn.commit()
            return True
            
    def insert_dividend(self,
                       symbol_id: int,
                       ex_date: datetime.date,
                       payment_date: datetime.date,
                       amount: float,
                       frequency: str,
                       source: str = 'bloomberg') -> bool:
        """插入分红数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO dividends 
                (symbol_id, ex_date, payment_date, amount, frequency, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (symbol_id, ex_date, payment_date, amount, frequency, source))
            
            conn.commit()
            return True
            
    def log_data_quality_issue(self,
                              symbol_id: int,
                              data_type: str,
                              issue_type: str,
                              details: Dict,
                              severity: str = 'medium') -> int:
        """记录数据质量问题"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO data_quality_log 
                (symbol_id, data_type, issue_type, details, severity)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (symbol_id, data_type, issue_type, json.dumps(details), severity))
            
            conn.commit()
            return cursor.fetchone()[0] if cursor.rowcount > 0 else None
            
    def query_latest_price(self,
                          symbol_id: int,
                          timestamp: Optional[datetime] = None) -> Optional[float]:
        """查询最新价格"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if timestamp is None:
                cursor.execute("""
                    SELECT price FROM tick_data 
                    WHERE symbol_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (symbol_id,))
            else:
                cursor.execute("""
                    SELECT price FROM tick_data 
                    WHERE symbol_id = %s AND timestamp <= %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (symbol_id, timestamp))
                
            result = cursor.fetchone()
            return result[0] if result else None
            
    def query_ohlcv_range(self,
                           symbol_id: int,
                           start_time: datetime,
                           end_time: datetime) -> pd.DataFrame:
        """查询OHLCV时间范围"""
        with self.get_connection() as conn:
            query = """
                SELECT time, open, high, low, close, volume
                FROM ohlcv_1m
                WHERE symbol_id = %s AND time >= %s AND time <= %s
                ORDER BY time ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(symbol_id, start_time, end_time))
            return df
            
    def query_technical_features(self,
                                 symbol_id: int,
                                 start_date: datetime.date,
                                 end_date: datetime.date) -> pd.DataFrame:
        """查询技术指标"""
        with self.get_connection() as conn:
            query = """
                SELECT date, sma_5, sma_10, sma_20, sma_50, sma_200,
                       ema_12, ema_26, rsi_14, macd, macd_signal,
                       bollinger_upper, bollinger_middle, bollinger_lower, atr_14,
                       volatility_20, volatility_60, momentum_20d, momentum_60d,
                       price_zscore, volume_zscore
                FROM technical_features
                WHERE symbol_id = %s AND date >= %s AND date <= %s
                ORDER BY date ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(symbol_id, start_date, end_date))
            return df

class DataCleaningPipeline:
    """数据清洗管道"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def validate_tick_data(self,
                           tick_data: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        验证Tick数据
        
        检查：
        1. 价格合理性（不能为负或过大偏离）
        2. 买卖价关系（bid < ask）
        3. 时间戳合理性
        4. 缺失值
        
        Args:
            tick_data: Tick数据
            
        Returns:
            (是否有效, 错误详情)
        """
        issues = []
        
        # 1. 价格合理性
        price = tick_data.get('price')
        if price is None or price <= 0:
            issues.append({
                'type': 'invalid_price',
                'severity': 'critical',
                'message': 'Price is missing or invalid'
            })
        elif price > 1e6:  # 价格超过100万
            issues.append({
                'type': 'price_outlier',
                'severity': 'high',
                'message': f'Price is too high: {price}'
            })
                
        # 2. 买卖价关系
        bid = tick_data.get('bid')
        ask = tick_data.get('ask')
        
        if bid is not None and ask is not None:
            if bid > ask:
                issues.append({
                    'type': 'invalid_bid_ask',
                    'severity': 'critical',
                    'message': f'Bid ({bid}) > Ask ({ask})'
                })
            elif (ask - bid) / bid > 0.1:  # 价差超过10%
                issues.append({
                    'type': 'wide_spread',
                    'severity': 'medium',
                    'message': f'Wide spread: {((ask-bid)/bid):.2%}'
                })
                
        # 3. 时间戳合理性
        timestamp = tick_data.get('timestamp')
        if timestamp is None:
            issues.append({
                'type': 'missing_timestamp',
                'severity': 'critical',
                'message': 'Timestamp is missing'
            })
        elif isinstance(timestamp, datetime):
            now = datetime.now()
            if abs((now - timestamp).total_seconds()) > 86400:  # 超过24小时
                issues.append({
                    'type': 'old_timestamp',
                    'severity': 'low',
                    'message': f'Timestamp is old: {timestamp}'
                })
                
        # 4. 缺失值检查
        required_fields = ['price', 'timestamp']
        for field in required_fields:
            if tick_data.get(field) is None:
                issues.append({
                    'type': 'missing_value',
                    'severity': 'critical',
                    'message': f'Missing required field: {field}'
                })
                
        if issues:
            return False, issues
        else:
            return True, None
            
    def detect_outliers(self,
                         prices: pd.Series,
                         method: str = 'zscore',
                         threshold: float = 3.0) -> pd.Series:
        """
        检测异常值
        
        Args:
            prices: 价格序列
            method: 检测方法 ('zscore', 'iqr', 'isolation_forest')
            threshold: 阈值
            
        Returns:
            异常值标记序列
        """
        if method == 'zscore':
            z_scores = (prices - prices.mean()) / prices.std()
            outliers = (np.abs(z_scores) > threshold)
            return outliers
            
        elif method == 'iqr':
            Q1 = prices.quantile(0.25)
            Q3 = prices.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (prices < lower_bound) | (prices > upper_bound)
            return outliers
            
        else:
            raise ValueError(f"Unknown method: {method}")
            
    def handle_missing_values(self,
                            data: pd.DataFrame,
                            columns: List[str]) -> pd.DataFrame:
        """
        处理缺失值
        
        策略：
        - 前向填充（时间序列）
        - 使用上一个可用值
        - 对于连续缺失，插值
        
        Args:
            data: 数据框
            columns: 需要处理的列
            
        Returns:
            清洗后的数据
        """
        cleaned_data = data.copy()
        
        for col in columns:
            if col not in cleaned_data.columns:
                continue
                
            missing_count = cleaned_data[col].isna().sum()
            
            if missing_count == 0:
                continue
                
            # 前向填充
            cleaned_data[col] = cleaned_data[col].fillna(method='ffill')
            
            # 如果还有缺失，用后向填充
            remaining_missing = cleaned_data[col].isna().sum()
            if remaining_missing > 0:
                cleaned_data[col] = cleaned_data[col].fillna(method='bfill')
                
        return cleaned_data

class CorporateActionAdjuster:
    """企业行动调整器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def process_stock_split(self,
                           symbol_id: int,
                           split_ratio: float,
                           split_date: datetime.date,
                           adjustment_factor: float = None) -> int:
        """
        处理股票拆分
        
        Args:
            symbol_id: 股票ID
            split_ratio: 拆分比例（如 2 表示 1拆2）
            split_date: 拆分日期
            adjustment_factor: 调整因子（可选，手动指定）
            
        Returns:
            受影响记录数
        """
        if adjustment_factor is None:
            adjustment_factor = 1.0 / split_ratio
            
        # 更新所有拆分前的历史价格
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tick_data
                SET price = price * %s,
                    bid = CASE WHEN bid IS NOT NULL THEN bid * %s ELSE NULL END,
                    ask = CASE WHEN ask IS NOT NULL THEN ask * %s ELSE NULL END
                WHERE symbol_id = %s AND timestamp < %s
            """, (adjustment_factor, adjustment_factor, adjustment_factor,
                  symbol_id, split_date))
            
            rows_affected = cursor.rowcount
            
            # 更新分钟线
            cursor.execute("""
                UPDATE ohlcv_1m
                SET open = open * %s,
                    high = high * %s,
                    low = low * %s,
                    close = close * %s
                WHERE symbol_id = %s AND time < %s
            """, (adjustment_factor, adjustment_factor, adjustment_factor, adjustment_factor,
                  symbol_id, split_date))
            
            rows_affected += cursor.rowcount
            
            # 更新日线
            cursor.execute("""
                UPDATE daily_data
                SET open = open * %s,
                    high = high * %s,
                    low = low * %s,
                    close = close * %s,
                    adjusted_close = adjusted_close * %s
                WHERE symbol_id = %s AND date < %s
            """, (adjustment_factor, adjustment_factor, adjustment_factor, adjustment_factor,
                  adjustment_factor, symbol_id, split_date))
            
            rows_affected += cursor.rowcount
            
            # 记录企业行动
            cursor.execute("""
                INSERT INTO corporate_actions 
                (symbol_id, action_type, effective_date, details, processed)
                VALUES (%s, 'split', %s, %s, TRUE)
            """, (symbol_id, split_date, json.dumps({
                'split_ratio': split_ratio,
                'adjustment_factor': adjustment_factor
            })))
            
            conn.commit()
            
        return rows_affected
        
    def process_dividend(self,
                         symbol_id: int,
                         dividend_data: Dict) -> int:
        """
        处理分红（调整后复权价格）
        
        Args:
            symbol_id: 股票ID
            dividend_data: 分红数据 {
                'amount': 分红金额,
                'ex_date': 除息日,
                'payment_date': 派息日
            }
            
        Returns:
            受影响记录数
        """
        # 计算调整因子
        adjustment_factor = 1.0 - (dividend_data['amount'] / dividend_data['price_before_dividend'])
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 更新所有除息日之后的收盘价
            cursor.execute("""
                UPDATE daily_data
                SET adjusted_close = close * %s
                WHERE symbol_id = %s AND date >= %s
            """, (adjustment_factor, symbol_id, dividend_data['ex_date']))
            
            rows_affected = cursor.rowcount
            
            # 插入分红记录
            cursor.execute("""
                INSERT INTO dividends 
                (symbol_id, ex_date, payment_date, amount, frequency, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (symbol_id, dividend_data['ex_date'], dividend_data['payment_date'],
                  dividend_data['amount'], 'quarterly', 'bloomberg'))
            
            rows_affected += cursor.rowcount
            
            # 记录企业行动
            cursor.execute("""
                INSERT INTO corporate_actions 
                (symbol_id, action_type, effective_date, details, processed)
                VALUES (%s, 'dividend', %s, %s, TRUE)
            """, (symbol_id, dividend_data['ex_date'], json.dumps(dividend_data)))
            
            conn.commit()
            
        return rows_affected
        
    def process_merger(self,
                      target_symbol_id: int,
                      acquirer_symbol_id: int,
                      merger_ratio: float,
                      effective_date: datetime.date) -> int:
        """
        处理并购
        
        目标股票转换为收购方股票
        
        Args:
            target_symbol_id: 目标股票ID
            acquirer_symbol_id: 收购方股票ID
            merger_ratio: 转换比例
            effective_date: 生效日期
            
        Returns:
            受影响记录数
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 更新目标股票的所有历史持仓
            cursor.execute("""
                UPDATE tick_data
                SET symbol_id = %s
                WHERE symbol_id = %s AND timestamp < %s
            """, (acquirer_symbol_id, target_symbol_id, effective_date))
            
            rows_affected = cursor.rowcount
            
            # 更新其他表
            for table in ['ohlcv_1m', 'daily_data', 'technical_features']:
                cursor.execute(f"""
                    UPDATE {table}
                    SET symbol_id = %s
                    WHERE symbol_id = %s AND time < %s
                """, (acquirer_symbol_id, target_symbol_id, effective_date))
                rows_affected += cursor.rowcount
                
            # 记录企业行动
            cursor.execute("""
                INSERT INTO corporate_actions 
                (symbol_id, action_type, effective_date, details, processed)
                VALUES (%s, 'merger', %s, %s, TRUE)
            """, (target_symbol_id, effective_date, json.dumps({
                'acquirer_symbol_id': acquirer_symbol_id,
                'merger_ratio': merger_ratio
            })))
            
            conn.commit()
            
        return rows_affected
        
    def get_unprocessed_actions(self) -> pd.DataFrame:
        """获取未处理的企业行动"""
        with self.db_manager.get_connection() as conn:
            query = """
                SELECT ca.id, s.ticker, ca.action_type, ca.effective_date, ca.details
                FROM corporate_actions ca
                JOIN symbols s ON ca.symbol_id = s.symbol_id
                WHERE ca.processed = FALSE
                ORDER BY ca.effective_date ASC
            """
            
            df = pd.read_sql_query(query, conn)
            return df
            
    def process_all_unprocessed_actions(self) -> Dict:
        """处理所有未处理的企业行动"""
        actions_df = self.get_unprocessed_actions()
        
        if actions_df.empty:
            return {'processed': 0, 'errors': []}
            
        processed = 0
        errors = []
        
        for idx, row in actions_df.iterrows():
            try:
                details = json.loads(row['details'])
                action_type = row['action_type']
                symbol_id = row['id']
                
                if action_type == 'split':
                    processed += self.process_stock_split(
                        symbol_id,
                        details.get('split_ratio', 2.0),
                        row['effective_date'],
                        details.get('adjustment_factor')
                    )
                elif action_type == 'dividend':
                    processed += self.process_dividend(symbol_id, details)
                elif action_type == 'merger':
                    processed += self.process_merger(
                        symbol_id,
                        details.get('acquirer_symbol_id'),
                        details.get('merger_ratio', 1.0),
                        row['effective_date']
                    )
                    
            except Exception as e:
                errors.append({
                    'action_id': row['id'],
                    'error': str(e)
                })
                
        return {'processed': processed, 'errors': errors}

class TechnicalIndicatorCalculator:
    """技术指标计算器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def calculate_sma(self,
                     prices: pd.Series,
                     period: int) -> pd.Series:
        """简单移动平均"""
        return prices.rolling(window=period).mean()
        
    def calculate_ema(self,
                     prices: pd.Series,
                     period: int,
                     smoothing: float = 2.0) -> pd.Series:
        """指数移动平均"""
        multiplier = smoothing / (1 + period)
        ema = prices.ewm(alpha=multiplier, adjust=False).mean()
        return ema
        
    def calculate_rsi(self,
                    prices: pd.Series,
                    period: int = 14) -> pd.Series:
        """相对强弱指标（RSI）"""
        delta = prices.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = 100 - (100 / (1 + avg_gain / avg_loss))
        return rs
        
    def calculate_macd(self,
                      prices: pd.Series,
                      fast_period: int = 12,
                      slow_period: int = 26,
                      signal_period: int = 9) -> Dict[str, pd.Series]:
        """MACD指标"""
        ema_fast = self.calculate_ema(prices, fast_period)
        ema_slow = self.calculate_ema(prices, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.rolling(window=signal_period).mean()
        
        histogram = macd_line - signal_line
        
        # 买卖信号
        macd_signal = np.where(macd_line > signal_line, 1,
                             np.where(macd_line < signal_line, -1, 0))
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram,
            'macd_signal': pd.Series(macd_signal, index=prices.index)
        }
        
    def calculate_bollinger_bands(self,
                                prices: pd.Series,
                                period: int = 20,
                                std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """布林带"""
        middle = self.calculate_sma(prices, period)
        std = prices.rolling(window=period).std()
        
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        # 带宽
        bandwidth = (upper - lower) / middle
        
        # %B指标
        percent_b = (prices - lower) / (upper - lower)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth,
            'percent_b': percent_b
        }
        
    def calculate_atr(self,
                    high: pd.Series,
                    low: pd.Series,
                    period: int = 14) -> pd.Series:
        """平均真实波幅"""
        tr = (high - low).abs()
        atr = tr.rolling(window=period).mean()
        return atr
        
    def calculate_volatility(self,
                          returns: pd.Series,
                          period: int = 20) -> pd.Series:
        """波动率（年化）"""
        volatility = returns.rolling(window=period).std() * np.sqrt(252)
        return volatility
        
    def calculate_momentum(self,
                         prices: pd.Series,
                         period: int) -> pd.Series:
        """动量（期数收益）"""
        return prices.pct_change(periods=period)
        
    def calculate_all_indicators(self,
                               symbol_id: int,
                               df: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算所有技术指标"""
        indicators = {}
        
        # 价格数据
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # 移动平均
        indicators['sma_5'] = self.calculate_sma(close, 5)
        indicators['sma_10'] = self.calculate_sma(close, 10)
        indicators['sma_20'] = self.calculate_sma(close, 20)
        indicators['sma_50'] = self.calculate_sma(close, 50)
        indicators['sma_200'] = self.calculate_sma(close, 200)
        
        # 指数移动平均
        indicators['ema_12'] = self.calculate_ema(close, 12)
        indicators['ema_26'] = self.calculate_ema(close, 26)
        
        # RSI
        indicators['rsi_14'] = self.calculate_rsi(close, 14)
        
        # MACD
        macd_results = self.calculate_macd(close)
        indicators['macd'] = macd_results['macd']
        indicators['macd_signal'] = macd_results['signal']
        indicators['macd_histogram'] = macd_results['histogram']
        
        # 布林带
        bollinger_results = self.calculate_bollinger_bands(close)
        indicators['bollinger_upper'] = bollinger_results['upper']
        indicators['bollinger_middle'] = bollinger_results['middle']
        indicators['bollinger_lower'] = bollinger_results['lower']
        
        # ATR
        indicators['atr_14'] = self.calculate_atr(high, low, 14)
        
        # 波动率
        returns = close.pct_change()
        indicators['volatility_20'] = self.calculate_volatility(returns, 20)
        indicators['volatility_60'] = self.calculate_volatility(returns, 60)
        
        # 成交量指标
        indicators['volume_sma_20'] = volume.rolling(window=20).mean()
        indicators['volume_ratio_5'] = volume / volume.rolling(window=5).mean()
        
        # 动量
        indicators['momentum_20d'] = self.calculate_momentum(close, 20)
        indicators['momentum_60d'] = self.calculate_momentum(close, 60)
        
        # 标准化指标
        indicators['price_zscore'] = (close - close.mean()) / close.std()
        indicators['volume_zscore'] = (volume - volume.mean()) / volume.std()
        
        return indicators
        
    def save_indicators_to_db(self,
                              symbol_id: int,
                              date: datetime.date,
                              indicators: Dict) -> bool:
        """保存指标到数据库"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO technical_features 
                (date, symbol_id, sma_5, sma_10, sma_20, sma_50, sma_200,
                 ema_12, ema_26, rsi_14, macd, macd_signal,
                 bollinger_upper, bollinger_middle, bollinger_lower, atr_14,
                 volatility_20, volatility_60, momentum_20d, momentum_60d,
                 price_zscore, volume_zscore)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, symbol_id) DO UPDATE SET
                    sma_5 = EXCLUDED.sma_5,
                    sma_10 = EXCLUDED.sma_10,
                    sma_20 = EXCLUDED.sma_20,
                    sma_50 = EXCLUDED.sma_50,
                    sma_200 = EXCLUDED.sma_200,
                    ema_12 = EXCLUDED.ema_12,
                    ema_26 = EXCLUDED.ema_26,
                    rsi_14 = EXCLUDED.rsi_14,
                    macd = EXCLUDED.macd,
                    macd_signal = EXCLUDED.macd_signal,
                    bollinger_upper = EXCLUDED.bollinger_upper,
                    bollinger_middle = EXCLUDED.bollinger_middle,
                    bollinger_lower = EXCLUDED.bollinger_lower,
                    atr_14 = EXCLUDED.atr_14,
                    volatility_20 = EXCLUDED.volatility_20,
                    volatility_60 = EXCLUDED.volatility_60,
                    momentum_20d = EXCLUDED.momentum_20d,
                    momentum_60d = EXCLUDED.momentum_60d,
                    price_zscore = EXCLUDED.price_zscore,
                    volume_zscore = EXCLUDED.volume_zscore,
                    updated_at = CURRENT_TIMESTAMP
            """, (date, symbol_id,
                  indicators.get('sma_5'),
                  indicators.get('sma_10'),
                  indicators.get('sma_20'),
                  indicators.get('sma_50'),
                  indicators.get('sma_200'),
                  indicators.get('ema_12'),
                  indicators.get('ema_26'),
                  indicators.get('rsi_14'),
                  indicators.get('macd'),
                  indicators.get('macd_signal'),
                  indicators.get('bollinger_upper'),
                  indicators.get('bollinger_middle'),
                  indicators.get('bollinger_lower'),
                  indicators.get('atr_14'),
                  indicators.get('volatility_20'),
                  indicators.get('volatility_60'),
                  indicators.get('momentum_20d'),
                  indicators.get('momentum_60d'),
                  indicators.get('price_zscore'),
                  indicators.get('volume_zscore')))
            
            conn.commit()
            return True

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, date
import uvicorn

app = FastAPI(title="Market Data API", version="1.0.0")

# 注入数据库管理器
db_manager = None

@app.on_event("startup")
async def startup_event():
    global db_manager
    db_manager = DatabaseManager(
        dbname='market_data',
        user='postgres',
        password='your_password',
        host='localhost',
        port=5432
    )
    db_manager.connect()
    db_manager.initialize_database()

@app.on_event("shutdown")
async def shutdown_event():
    global db_manager
    if db_manager:
        db_manager.close()

# API 端点
@app.get("/api/v1/symbols")
async def list_symbols(
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    is_active: bool = True
):
    """列出股票代码"""
    with db_manager.get_connection() as conn:
        query = "SELECT * FROM symbols WHERE is_active = %s"
        params = [is_active]
        
        if exchange:
            query += " AND exchange = %s"
            params.append(exchange)
            
        if sector:
            query += " AND sector = %s"
            params.append(sector)
            
        df = pd.read_sql_query(query, conn, params=params)
        return df.to_dict(orient='records')

@app.get("/api/v1/symbols/{ticker}")
async def get_symbol(ticker: str):
    """获取单个股票信息"""
    with db_manager.get_connection() as conn:
        query = "SELECT * FROM symbols WHERE ticker = %s"
        df = pd.read_sql_query(query, conn, params=[ticker])
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Symbol not found")
            
        return df.to_dict(orient='records')[0]

@app.get("/api/v1/data/realtime/{ticker}")
async def get_realtime_quote(ticker: str):
    """获取实时报价"""
    # 从缓存或数据库获取最新报价
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.ticker, t.price, t.timestamp, t.bid, t.ask, t.volume
            FROM tick_data t
            JOIN symbols s ON t.symbol_id = s.symbol_id
            WHERE s.ticker = %s
            ORDER BY t.timestamp DESC
            LIMIT 1
        """, (ticker.upper(),))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="No data for this symbol")
            
        return {
            'ticker': result[0],
            'price': result[1],
            'timestamp': result[2],
            'bid': result[3],
            'ask': result[4],
            'volume': result[5]
        }

@app.get("/api/v1/data/ohlcv/{ticker}")
async def get_ohlcv(
    ticker: str,
    start_date: date,
    end_date: date,
    interval: str = '1m'
):
    """获取OHLCV数据"""
    with db_manager.get_connection() as conn:
        # 根据interval选择表
        table_map = {
            '1m': 'ohlcv_1m',
            '5m': 'ohlcv_5m',
            '15m': 'ohlcv_15m',
            '1h': 'ohlcv_1h',
            '1d': 'daily_data'
        }
        
        table = table_map.get(interval, 'daily_data')
        
        query = f"""
            SELECT time, open, high, low, close, volume
            FROM {table} t
            JOIN symbols s ON t.symbol_id = s.symbol_id
            WHERE s.ticker = %s AND time >= %s AND time <= %s
            ORDER BY time ASC
        """
        
        df = pd.read_sql_query(query, conn, 
                              params=[ticker.upper(), start_date, end_date])
        
        return df.to_dict(orient='records')

@app.get("/api/v1/indicators/{ticker}")
async def get_technical_indicators(
    ticker: str,
    start_date: date,
    end_date: date
):
    """获取技术指标"""
    with db_manager.get_connection() as conn:
        query = """
            SELECT date, sma_5, sma_10, sma_20, sma_50, sma_200,
                   ema_12, ema_26, rsi_14, macd, macd_signal,
                   bollinger_upper, bollinger_middle, bollinger_lower, atr_14,
                   volatility_20, volatility_60, momentum_20d, momentum_60d,
                   price_zscore, volume_zscore
            FROM technical_features t
            JOIN symbols s ON t.symbol_id = s.symbol_id
            WHERE s.ticker = %s AND date >= %s AND date <= %s
            ORDER BY date ASC
        """
        
        df = pd.read_sql_query(query, conn, 
                              params=[ticker.upper(), start_date, end_date])
        
        return df.to_dict(orient='records')

@app.get("/api/v1/fundamentals/{ticker}")
async def get_fundamentals(
    ticker: str,
    period_type: str = 'quarterly'
):
    """获取基本面数据"""
    with db_manager.get_connection() as conn:
        query = """
            SELECT * FROM fundamentals f
            JOIN symbols s ON f.symbol_id = s.symbol_id
            WHERE s.ticker = %s AND period_type = %s
            ORDER BY report_date DESC
            LIMIT 1
        """
        
        df = pd.read_sql_query(query, conn, params=[ticker.upper(), period_type])
        
        return df.to_dict(orient='records')[0] if not df.empty else None

@app.get("/api/v1/data/quality/{ticker}")
async def get_data_quality(ticker: str, days: int = 30):
    """获取数据质量报告"""
    with db_manager.get_connection() as conn:
        query = """
            SELECT issue_type, COUNT(*) as issue_count, severity
            FROM data_quality_log d
            JOIN symbols s ON d.symbol_id = s.symbol_id
            WHERE s.ticker = %s AND issue_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY issue_type, severity
            ORDER BY severity DESC, issue_count DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[ticker.upper(), days])
        
        return df.to_dict(orient='records')

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM symbols")
        symbol_count = cursor.fetchone()[0]
        
        return {
            'status': 'healthy',
            'database': 'connected',
            'symbols_count': symbol_count,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import schedule
import time
from typing import Callable, Optional

class DataUpdateScheduler:
    """数据更新调度器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.scheduled_jobs = {}
        
    def schedule_realtime_data_collection(self,
                                       data_feeds: List[RealTimeDataFeed]):
        """调度实时数据收集"""
        for feed in data_feeds:
            job = schedule.every(1).minutes.do(
                self._collect_realtime_data,
                feed
            )
            self.scheduled_jobs[f"realtime_{feed.source.name}"] = job
        print(f"Scheduled realtime collection for {feed.source.name}")
        
    def schedule_daily_eod_update(self,
                                  data_source_registry: DataSourceRegistry):
        """调度每日收盘后更新"""
        job = schedule.every().day.at("18:00").do(
            self._update_daily_eod_data,
            data_source_registry
        )
        self.scheduled_jobs['daily_eod'] = job
        print("Scheduled daily EOD update at 18:00")
        
    def schedule_weekly_fundamental_update(self,
                                        data_source_registry: DataSourceRegistry):
        """调度每周基本面更新"""
        job = schedule.every().friday.at("20:00").do(
            self._update_fundamental_data,
            data_source_registry
        )
        self.scheduled_jobs['weekly_fundamentals'] = job
        print("Scheduled weekly fundamental update on Friday 20:00")
        
    def schedule_monthly_feature_recalculation(self):
        """调度每月指标重新计算"""
        job = schedule.every().month.do(
            self._recalculate_features
        )
        self.scheduled_jobs['monthly_features'] = job
        print("Scheduled monthly feature recalculation")
        
    async def _collect_realtime_data(self,
                                    feed: RealTimeDataFeed):
        """收集实时数据"""
        if not feed.connected:
            await feed.connect()
            
        # 从消息队列获取数据并存储
        while feed.connected:
            try:
                tick_data = await feed.message_queue.get(timeout=1.0)
                
                # 验证数据
                is_valid, issues = self.db_manager.cleaner.validate_tick_data(tick_data)
                
                if not is_valid:
                    for issue in issues:
                        self.db_manager.log_data_quality_issue(
                            tick_data['symbol_id'],
                            'price',
                            issue['type'],
                            issue,
                            issue['severity']
                        )
                    continue
                    
                # 存储到数据库
                if 'symbol_id' not in tick_data:
                    continue
                    
                self.db_manager.insert_tick_data(
                    symbol_id=tick_data['symbol_id'],
                    timestamp=tick_data['timestamp'],
                    price=tick_data['price'],
                    bid=tick_data.get('bid'),
                    ask=tick_data.get('ask'),
                    volume=tick_data.get('volume'),
                    source=tick_data.get('source', feed.source.name)
                )
                
            except Exception as e:
                print(f"Error collecting realtime data: {e}")
                await asyncio.sleep(5)
                
    def _update_daily_eod_data(self, data_source_registry: DataSourceRegistry):
        """更新每日收盘后数据"""
        print("Starting daily EOD data update...")
        
        # 获取所有活跃股票
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol_id, ticker FROM symbols WHERE is_active = TRUE")
            symbols = cursor.fetchall()
            
        for symbol_id, ticker in symbols:
            try:
                # 从Yahoo Finance获取日数据
                import yfinance as yf
                stock = yf.Ticker(ticker)
                
                # 获取最近5年数据
                hist = stock.history(period="5y")
                
                # 批量插入
                for date, row in hist.iterrows():
                    self.db_manager.insert_ohlcv(
                        symbol_id=symbol_id,
                        time=date,
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        volume=row['Volume']
                    )
                    
                print(f"Updated EOD data for {ticker}: {len(hist)} records")
                
            except Exception as e:
                print(f"Error updating EOD data for {ticker}: {e}")
                continue
                
    def _update_fundamental_data(self, data_source_registry: DataSourceRegistry):
        """更新基本面数据"""
        print("Starting weekly fundamental data update...")
        
        # 获取所有活跃股票
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol_id, ticker FROM symbols WHERE is_active = TRUE")
            symbols = cursor.fetchall()
            
        for symbol_id, ticker in symbols:
            try:
                # 使用Finnhub API获取基本面数据
                import requests
                
                api_key = "YOUR_FINNHUB_API_KEY"
                base_url = "https://finnhub.io/api/v1"
                
                # 获取公司概况
                profile_url = f"{base_url}/stock/profile2?symbol={ticker}&token={api_key}"
                response = requests.get(profile_url).json()
                
                if len(response) == 0:
                    print(f"No data for {ticker}")
                    continue
                    
                profile = response[0]
                
                # 插入或更新基本面数据
                # 这里简化处理，实际应该更复杂
                print(f"Updated fundamentals for {ticker}")
                
            except Exception as e:
                print(f"Error updating fundamentals for {ticker}: {e}")
                continue
                
    def _recalculate_features(self):
        """重新计算技术指标"""
        print("Starting monthly feature recalculation...")
        
        # 为所有股票重新计算最近1年的技术指标
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol_id, ticker FROM symbols WHERE is_active = TRUE")
            symbols = cursor.fetchall()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            for symbol_id, ticker in symbols:
                try:
                    # 获取OHLCV数据
                    df = self.db_manager.query_ohlcv_range(
                        symbol_id, 
                        start_date,
                        end_date
                    )
                    
                    if df.empty:
                        continue
                        
                    # 计算所有指标
                    indicator_calc = TechnicalIndicatorCalculator(self.db_manager)
                    indicators = indicator_calc.calculate_all_indicators(symbol_id, df)
                    
                    # 保存指标
                    for date, row in df.iterrows():
                        indicator_calc.save_indicators_to_db(
                            symbol_id,
                            date.date(),
                            indicators
                        )
                        
                    print(f"Recalculated features for {ticker}")
                    
                except Exception as e:
                    print(f"Error recalculating features for {ticker}: {e}")
                    continue
                    
    def start(self):
        """启动调度器"""
        print("Starting data update scheduler...")
        schedule.run_pending()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
            
    def stop(self):
        """停止调度器"""
        print("Stopping data update scheduler...")
        schedule.clear()

class MarketDataPipeline:
    """完整市场数据管道"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 配置字典 {
                'database': 数据库配置,
                'data_sources': 数据源配置,
                'symbols': 股票列表,
                'schedule': 调度配置
            }
        """
        self.config = config
        
        # 初始化各个组件
        self.db_manager = DatabaseManager(**config['database'])
        self.source_registry = DataSourceRegistry()
        self.cleaner = DataCleaningPipeline(self.db_manager)
        self.corporate_adjuster = CorporateActionAdjuster(self.db_manager)
        self.indicator_calc = TechnicalIndicatorCalculator(self.db_manager)
        self.scheduler = DataUpdateScheduler(self.db_manager)
        
        # 初始化实时数据流
        self.realtime_feeds = []
        
    def initialize(self):
        """初始化管道"""
        print("Initializing market data pipeline...")
        
        # 1. 初始化数据库
        self.db_manager.connect()
        self.db_manager.initialize_database()
        
        # 2. 插入股票代码
        self._load_symbols()
        
        # 3. 初始化实时数据流
        self._initialize_realtime_feeds()
        
        # 4. 设置调度任务
        self._setup_schedules()
        
        print("Market data pipeline initialized successfully")
        
    def _load_symbols(self):
        """加载股票代码"""
        print("Loading symbols...")
        
        symbols_config = self.config.get('symbols', {})
        
        if 'list' in symbols_config:
            for symbol_data in symbols_config['list']:
                symbol_id = self.db_manager.insert_symbol(
                    ticker=symbol_data['ticker'],
                    name=symbol_data.get('name', symbol_data['ticker']),
                    exchange=symbol_data.get('exchange', 'NYSE'),
                    sector=symbol_data.get('sector'),
                    industry=symbol_data.get('industry'),
                    market_cap=symbol_data.get('market_cap')
                )
                
        print(f"Loaded {len(symbols_config.get('list', []))} symbols")
        
    def _initialize_realtime_feeds(self):
        """初始化实时数据流"""
        print("Initializing realtime data feeds...")
        
        realtime_config = self.config.get('realtime', {})
        
        if 'symbols' in realtime_config:
            symbols = realtime_config['symbols']
            source = self.source_registry.get_source(realtime_config.get('source'))
            
            if source and source.real_time:
                feed = RealTimeDataFeed(source, symbols)
                self.realtime_feeds.append(feed)
                
                # 设置调度
                self.scheduler.schedule_realtime_data_collection([feed])
                
        print(f"Initialized {len(self.realtime_feeds)} realtime feeds")
        
    def _setup_schedules(self):
        """设置调度任务"""
        print("Setting up scheduled tasks...")
        
        schedule_config = self.config.get('schedule', {})
        
        if schedule_config.get('daily_eod', True):
            self.scheduler.schedule_daily_eod_update(self.source_registry)
            
        if schedule_config.get('weekly_fundamentals', True):
            self.scheduler.schedule_weekly_fundamental_update(self.source_registry)
            
        if schedule_config.get('monthly_features', True):
            self.scheduler.schedule_monthly_feature_recalculation()
            
        print(f"Setup {len(self.scheduler.scheduled_jobs)} scheduled tasks")
        
    def start(self):
        """启动管道"""
        print("Starting market data pipeline...")
        
        # 启动调度器
        # self.scheduler.start()  # 在生产环境中启动
        
        print("Market data pipeline started")
        
    def get_realtime_data(self, symbol: str) -> Optional[Dict]:
        """获取实时数据"""
        for feed in self.realtime_feeds:
            if symbol in feed.symbols:
                return await feed.get_latest_quote(symbol)
        return None
        
    def get_historical_data(self,
                           symbol: str,
                           start_date: date,
                           end_date: date,
                           interval: str = '1d') -> List[Dict]:
        """获取历史数据"""
        symbol_id = self._get_symbol_id(symbol)
        if symbol_id is None:
            return []
            
        df = self.db_manager.query_ohlcv_range(
            symbol_id,
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.min.time())
        )
        
        return df.to_dict('records')
        
    def get_features(self,
                    symbol: str,
                    start_date: date,
                    end_date: date) -> List[Dict]:
        """获取技术指标"""
        symbol_id = self._get_symbol_id(symbol)
        if symbol_id is None:
            return []
            
        df = self.db_manager.query_technical_features(
            symbol_id,
            start_date,
            end_date
        )
        
        return df.to_dict('records')
        
    def get_fundamentals(self,
                         symbol: str) -> Optional[Dict]:
        """获取基本面数据"""
        symbol_id = self._get_symbol_id(symbol)
        if symbol_id is None:
            return None
            
        with self.db_manager.get_connection() as conn:
            query = """
                SELECT * FROM fundamentals
                WHERE symbol_id = %s
                ORDER BY report_date DESC
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn, params=[symbol_id])
            
            return df.to_dict('records')[0] if not df.empty else None
            
    def _get_symbol_id(self, ticker: str) -> Optional[int]:
        """获取股票ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol_id FROM symbols WHERE ticker = %s", (ticker.upper(),))
            result = cursor.fetchone()
            return result[0] if result else None

PIPELINE_CONFIG = {
    # 数据库配置
    'database': {
        'dbname': 'market_data',
        'user': 'postgres',
        'password': 'your_password',
        'host': 'localhost',
        'port': 5432,
        'pool_size': 10
    },
    
    # 数据源配置
    'data_sources': {
        'bloomberg': {
            'api_key': 'YOUR_BLOOMBERG_API_KEY',
            'enabled': True,
            'priority': 1
        },
        'polygon': {
            'api_key': 'YOUR_POLYGON_API_KEY',
            'enabled': True,
            'priority': 2
        },
        'yahoo': {
            'enabled': True,
            'priority': 3
        }
    },
    
    # 股票列表
    'symbols': {
        'list': [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'exchange': 'NASDAQ',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'market_cap': 2500000000000
            },
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet Inc.',
                'exchange': 'NASDAQ',
                'sector': 'Technology',
                'industry': 'Internet Software & Services',
                'market_cap': 1600000000000
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'exchange': 'NASDAQ',
                'sector': 'Technology',
                'industry': 'Software - Infrastructure',
                'market_cap': 2100000000000
            }
        ]
    },
    
    # 实时数据配置
    'realtime': {
        'enabled': True,
        'source': 'bloomberg',
        'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
        'tick_sources': ['polygon'],
        'max_latency_ms': 100,
        'reconnect_interval_sec': 30
    },
    
    # 调度配置
    'schedule': {
        'daily_eod': True,
        'weekly_fundamentals': True,
        'monthly_features': True,
        'hourly_data_quality_check': True
    },
    
    # 数据验证规则
    'validation': {
        'price_max_change_pct': 50,  # 单次最大价格变化百分比
        'min_volume': 0,
        'max_spread_pct': 10,       # 最大买卖价差百分比
        'outlier_detection': True,
        'outlier_method': 'zscore',
        'outlier_threshold': 3.0
    },
    
    # 企业行动处理
    'corporate_actions': {
        'auto_process': True,
        'processing_delay_days': 1
    },
    
    # 特征计算配置
    'features': {
        'sma_periods': [5, 10, 20, 50, 200],
        'ema_periods': [12, 26],
        'rsi_period': 14,
        'macd_periods': [12, 26, 9],
        'bollinger_period': 20,
        'bollinger_std': 2.0,
        'atr_period': 14,
        'volatility_periods': [20, 60],
        'momentum_periods': [20, 60]
    }
}

class PipelineMonitor:
    """管道监控器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.alerts = []
        
    def check_data_freshness(self, ticker: str, max_age_minutes: int = 60) -> Dict:
        """检查数据新鲜度"""
        symbol_id = self._get_symbol_id(ticker)
        if symbol_id is None:
            return {'status': 'error', 'message': 'Symbol not found'}
            
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查最新数据时间
            cursor.execute("""
                SELECT MAX(timestamp) as last_update
                FROM tick_data
                WHERE symbol_id = %s
            """, (symbol_id,))
            
            result = cursor.fetchone()
            if not result or result[0] is None:
                return {'status': 'error', 'message': 'No data available'}
                
            last_update = result[0]
            age_minutes = (datetime.now() - last_update).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                return {
                    'status': 'warning',
                    'message': f'Data is stale: {age_minutes:.1f} minutes old',
                    'ticker': ticker,
                    'last_update': last_update.isoformat()
                }
            else:
                return {
                    'status': 'ok',
                    'age_minutes': age_minutes,
                    'ticker': ticker,
                    'last_update': last_update.isoformat()
                }
                
    def check_data_quality(self, ticker: str, days: int = 7) -> Dict:
        """检查数据质量"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT issue_type, COUNT(*) as count, severity
                FROM data_quality_log d
                JOIN symbols s ON d.symbol_id = s.symbol_id
                WHERE s.ticker = %s AND issue_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY issue_type, severity
            """, (ticker.upper(), days))
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return {'status': 'ok', 'ticker': ticker}
                
            # 生成质量报告
            critical_issues = df[df['severity'] == 'critical']
            high_issues = df[df['severity'] == 'high']
            
            if len(critical_issues) > 0:
                return {
                    'status': 'critical',
                    'ticker': ticker,
                    'critical_issues': critical_issues.to_dict('records'),
                    'total_issues': len(df)
                }
            elif len(high_issues) > 0:
                return {
                    'status': 'warning',
                    'ticker': ticker,
                    'high_issues': high_issues.to_dict('records'),
                    'total_issues': len(df)
                }
            else:
                return {
                    'status': 'ok',
                    'ticker': ticker,
                    'total_issues': len(df),
                    'issues_summary': df.to_dict('records')
                }
                
    def _get_symbol_id(self, ticker: str) -> Optional[int]:
        """获取股票ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol_id FROM symbols WHERE ticker = %s", (ticker.upper(),))
            result = cursor.fetchone()
            return result[0] if result else None
            
    def generate_pipeline_report(self) -> Dict:
        """生成管道报告"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 统计各表记录数
            report = {}
            
            tables = ['tick_data', 'ohlcv_1m', 'daily_data', 'dividends', 
                    'corporate_actions', 'technical_features', 'fundamentals']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                report[table] = result[0] if result else 0
                
            # 统计数据质量问题
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM data_quality_log
                WHERE issue_date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY severity
            """)
            
            quality_stats = {}
            for row in cursor.fetchall():
                quality_stats[row[0]] = row[1]
                
            report['data_quality'] = quality_stats
            report['generated_at'] = datetime.now().isoformat()
            
            return report