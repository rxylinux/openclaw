# Jane Street 做市引擎

You are a senior quantitative trader at Jane Street who designs market-making algorithms that profit from bid-ask spreads while managing inventory风险 across thousands of trades per day.

I need a complete market-making strategy framework.

Design:

- Spread calculation model: how to set bid and ask prices based on volatility, volume, and inventory
- Inventory management: rules for staying neutral and avoiding large directional bets
- Quote adjustment logic: how to shift prices when inventory builds up on one side
- Adverse selection detection: identify when informed traders are picking off your quotes
- Speed and latency requirements: how fast order placement and cancellation need to be
- Hedging strategy: when and how to offset accumulated directional风险
- Market microstructure analysis: understanding order book dynamics, tick sizes, and queue priority
- PnL decomposition: separate profit from spread capture vs directional moves vs hedging costs
- Risk limits: maximum inventory, maximum loss per day, and automatic shutdown triggers
- Performance metrics: spread captured, inventory turnover, Sharpe ratio, and fill rate targets

Format as a Jane Street-style trading system specification with mathematical models, pseudocode, and risk parameter tables.

My interest: [DESCRIBE THE MARKET YOU WANT TO MAKE IN, YOUR CAPITAL, TECHNOLOGY AVAILABLE, AND EXPERIENCE LEVEL WITH MARKET MAKING]

---

## 使用说明

这是一个 Jane Street 风格的做市策略框架，用于构建完整的做市交易系统。

### 使用方法

将 `[DESCRIBE THE MARKET YOU WANT TO MAKE IN, YOUR CAPITAL, TECHNOLOGY AVAILABLE, AND EXPERIENCE LEVEL WITH MARKET MAKING]` 替换为你的具体情况，例如：

```
My interest: US equity options market, $10M capital, co-located servers with sub-microsecond latency, 3 years experience in market making and hedging.
```

### 适用场景

- 设计完整的做市策略
- 管理库存风险
- 检测不利选择
- 优化报价策略

---

## 核心做市模型

### 1. Avellaneda-Stoikov 做市模型

```python
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class MarketState:
    """市场状态"""
    mid_price: float
    volatility: float
    volume: float
    inventory: float
    time_to_end: float  # 到收盘/风险调整的时间

class AvellanedaStoikovMM:
    """Avellaneda-Stoikov 做市模型"""
    
    def __init__(self,
                 risk_aversion: float = 0.1,      # 风险厌恶系数 γ
                 base_spread: float = 0.0002):     # 基础价差
        self.risk_aversion = risk_aversion
        self.base_spread = base_spread
        
    def calculate_optimal_quotes(self,
                                 state: MarketState) -> Tuple[float, float]:
        """
        计算最优报价
        
        核心公式：
        - 最优买入价：s* - γσ²t/2 - q
        - 最优卖出价：s* + γσ²t/2 - q
        
        其中：
        - s* = 中间价
        - γ = 风险厌恶系数
        - σ = 波动率
        - t = 剩余时间
        - q = 库存（正数表示多头，负数表示空头）
        
        Args:
            state: 市场状态
            
        Returns:
            (bid_price, ask_price)
        """
        s = state.mid_price
        sigma = state.volatility
        t = state.time_to_end
        q = state.inventory
        gamma = self.risk_aversion
        
        # 库存调整项
        inventory_skew = gamma * q
        
        # 时间调整项
        time_adjustment = 0.5 * gamma * sigma**2 * t
        
        # 计算最优报价
        half_spread = 0.5 * self.base_spread + time_adjustment
        
        bid = s - half_spread - inventory_skew
        ask = s + half_spread - inventory_skew
        
        return bid, ask
        
    def calculate_spread(self,
                         state: MarketState) -> float:
        """
        计算最优价差
        
        Returns:
            价差
        """
        sigma = state.volatility
        t = state.time_to_end
        
        # 基础价差
        base = self.base_spread
        
        # 波动率调整
        volatility_adjustment = gamma = self.risk_aversion * sigma**2 * t
        
        spread = base + volatility_adjustment
        
        return max(spread, self.base_spread)  # 至少为基础价差
```

### 2. 库存管理模型

```python
class InventoryManager:
    """库存管理器"""
    
    def __init__(self,
                 max_inventory: float = 1000,      # 最大库存
                 warning_inventory: float = 800,     # 警告库存
                 neutral_target: float = 0.0,       # 目标中性库存
                 adjustment_factor: float = 0.01):   # 库存调整因子
        self.max_inventory = max_inventory
        self.warning_inventory = warning_inventory
        self.neutral_target = neutral_target
        self.adjustment_factor = adjustment_factor
        
    def get_inventory_skew(self,
                            current_inventory: float) -> float:
        """
        计算库存倾斜度
        
        Returns:
            倾斜度（-1 到 1），负数表示库存过多，正数表示库存过少
        """
        if current_inventory == self.neutral_target:
            return 0.0
            
        # 归一化到 [-1, 1]
        skew = (current_inventory - self.neutral_target) / self.max_inventory
        
        # 限制范围
        skew = max(-1.0, min(1.0, skew))
        
        return skew
        
    def calculate_quote_adjustment(self,
                                  inventory: float,
                                  mid_price: float) -> float:
        """
        计算因库存导致的报价调整
        
        库存过多时，降低买入价、提高卖出价（更难买入，更容易卖出）
        库存过少时，提高买入价、降低卖出价（更容易买入，更难卖出）
        
        Args:
            inventory: 当前库存
            mid_price: 中间价
            
        Returns:
            报价调整金额
        """
        skew = self.get_inventory_skew(inventory)
        
        # 调整量 = 倾斜度 × 中间价 × 调整因子
        adjustment = skew * mid_price * self.adjustment_factor
        
        return adjustment
        
    def should_reduce_position(self,
                               inventory: float) -> bool:
        """
        判断是否需要减仓
        
        Returns:
            是否需要减仓
        """
        abs_inventory = abs(inventory)
        
        if abs_inventory >= self.max_inventory:
            return True  # 强制减仓
        elif abs_inventory >= self.warning_inventory:
            return True  # 建议减仓
        else:
            return False
            
    def get_hedge_direction(self,
                            inventory: float) -> str:
        """
        获取对冲方向
        
        Returns:
            'buy', 'sell', 或 'neutral'
        """
        if inventory > self.warning_inventory:
            return 'sell'  # 库存过多，卖出对冲
        elif inventory < -self.warning_inventory:
            return 'buy'   # 库存过少，买入对冲
        else:
            return 'neutral'
```

---

### 3. 报价调整逻辑

```python
class QuoteManager:
    """报价管理器"""
    
    def __init__(self,
                 min_spread: float = 0.0001,      # 最小价差
                 max_spread: float = 0.002,       # 最大价差
                 adjustment_speed: float = 0.5):    # 调整速度
        self.min_spread = min_spread
        self.max_spread = max_spread
        self.adjustment_speed = adjustment_speed
        
        self.last_bid = None
        self.last_ask = None
        
    def calculate_smooth_quotes(self,
                              current_bid: float,
                              current_ask: float) -> Tuple[float, float]:
        """
        计算平滑报价（避免频繁调整）
        
        Args:
            current_bid: 当前计算的买入价
            current_ask: 当前计算的卖出价
            
        Returns:
            (平滑后的买入价, 平滑后的卖出价)
        """
        if self.last_bid is None or self.last_ask is None:
            self.last_bid = current_bid
            self.last_ask = current_ask
            return current_bid, current_ask
            
        # 平滑调整
        smooth_bid = self.last_bid + self.adjustment_speed * (current_bid - self.last_bid)
        smooth_ask = self.last_ask + self.adjustment_speed * (current_ask - self.last_ask)
        
        # 限制价差
        spread = smooth_ask - smooth_bid
        if spread < self.min_spread:
            # 价差太小，扩大
            center = (smooth_bid + smooth_ask) / 2
            smooth_bid = center - self.min_spread / 2
            smooth_ask = center + self.min_spread / 2
        elif spread > self.max_spread:
            # 价差太大，缩小
            center = (smooth_bid + smooth_ask) / 2
            smooth_bid = center - self.max_spread / 2
            smooth_ask = center + self.max_spread / 2
            
        self.last_bid = smooth_bid
        self.last_ask = smooth_ask
        
        return smooth_bid, smooth_ask
        
    def adjust_for_inventory(self,
                           bid: float,
                           ask: float,
                           inventory: float,
                           mid_price: float,
                           adjustment_factor: float = 0.01) -> Tuple[float, float]:
        """
        根据库存调整报价
        
        Args:
            bid: 原始买入价
            ask: 原始卖出价
            inventory: 当前库存
            mid_price: 中间价
            adjustment_factor: 调整因子
            
        Returns:
            (调整后的买入价, 调整后的卖出价)
        """
        # 库存倾斜
        skew = inventory / 1000.0  # 归一化
        skew = max(-1.0, min(1.0, skew))
        
        # 调整量
        adjustment = skew * mid_price * adjustment_factor
        
        # 调整报价
        adjusted_bid = bid - adjustment  # 库存过多时降低买入价
        adjusted_ask = ask - adjustment  # 库存过多时降低卖出价
        
        return adjusted_bid, adjusted_ask
```

---

### 4. 不利选择检测

```python
class AdverseSelectionDetector:
    """不利选择检测器"""
    
    def __init__(self,
                 detection_window: int = 100,      # 检测窗口
                 adverse_threshold: float = 0.3,   # 不利选择阈值
                 price_move_window: int = 10):      # 价格移动窗口
        self.detection_window = detection_window
        self.adverse_threshold = adverse_threshold
        self.price_move_window = price_move_window
        
        self.trade_history = []
        self.adverse_score = 0.0
        
    def add_trade(self,
                 trade: Dict):
        """
        添加交易记录
        
        Args:
            trade: 交易字典 {
                'side': 'buy' or 'sell',
                'price': 成交价,
                'quantity': 成交量,
                'timestamp': 时间戳
            }
        """
        self.trade_history.append(trade)
        
        # 保持窗口大小
        if len(self.trade_history) > self.detection_window:
            self.trade_history.pop(0)
            
    def calculate_adverse_selection(self,
                                    current_price: float) -> Dict:
        """
        计算不利选择指标
        
        检测逻辑：
        1. 如果买入后价格立即下跌，可能是不利选择
        2. 如果卖出后价格立即上涨，可能是不利选择
        3. 计算不利选择的频率
        
        Args:
            current_price: 当前价格
            
        Returns:
            检测结果字典
        """
        if len(self.trade_history) < 10:
            return {
                'adverse_selection': False,
                'score': 0.0,
                'adverse_ratio': 0.0
            }
            
        adverse_count = 0
        total_trades = len(self.trade_history)
        
        for i, trade in enumerate(self.trade_history):
            # 获取交易后 window 期的价格
            future_prices = [
                t['price'] for t in self.trade_history[i:i+self.price_move_window]
            ]
            
            if not future_prices:
                continue
                
            avg_future_price = np.mean(future_prices)
            
            # 判断是否为不利选择
            if trade['side'] == 'buy':
                # 买入后价格下跌
                if avg_future_price < trade['price']:
                    adverse_count += 1
            elif trade['side'] == 'sell':
                # 卖出后价格上涨
                if avg_future_price > trade['price']:
                    adverse_count += 1
                    
        # 计算不利选择比例
        adverse_ratio = adverse_count / total_trades
        
        # 计算不利选择得分
        self.adverse_score = 0.7 * self.adverse_score + 0.3 * adverse_ratio
        
        # 判断是否为不利选择
        is_adverse = self.adverse_score > self.adverse_threshold
        
        return {
            'adverse_selection': is_adverse,
            'score': self.adverse_score,
            'adverse_ratio': adverse_ratio,
            'adverse_count': adverse_count,
            'total_trades': total_trades
        }
        
    def should_widen_spread(self, adverse_result: Dict) -> bool:
        """
        判断是否应该扩大价差
        
        Args:
            adverse_result: 不利选择检测结果
            
        Returns:
            是否扩大价差
        """
        if adverse_result['adverse_selection']:
            # 不利选择，扩大价差
            return True
        elif adverse_result['score'] > self.adverse_threshold * 0.7:
            # 接近阈值，略微扩大价差
            return True
        else:
            return False
            
    def get_spread_multiplier(self, adverse_result: Dict) -> float:
        """
        获取价差乘数
        
        Args:
            adverse_result: 不利选择检测结果
            
        Returns:
            价差乘数（如 2.0 表示价差扩大 2 倍）
        """
        if not adverse_result['adverse_selection']:
            return 1.0
            
        # 根据不利选择得分计算乘数
        score = adverse_result['score']
        
        # 线性映射：阈值→1.5x, 最大→2.5x
        if score <= self.adverse_threshold:
            multiplier = 1.0 + 0.5 * (score / self.adverse_threshold)
        else:
            multiplier = 1.5 + 1.0 * min((score - self.adverse_threshold) / 0.5, 1.0)
            
        return min(multiplier, 2.5)
```

---

### 5. 速度和延迟要求

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LatencyMetrics:
    """延迟指标"""
    order_placement_us: float      # 下单延迟（微秒）
    cancellation_us: float         # 撤单延迟（微秒）
    market_data_us: float         # 行情接收延迟（微秒）
    strategy_calc_us: float       # 策略计算延迟（微秒）
    total_loop_us: float          # 总循环延迟（微秒）

class LatencyManager:
    """延迟管理器"""
    
    def __init__(self,
                 max_total_latency_us: float = 1000,    # 最大总延迟 1ms
                 warning_latency_us: float = 800,        # 警告延迟 800μs
                 cpu_target: float = 0.7):            # CPU 目标使用率
        self.max_total_latency = max_total_latency_us
        self.warning_latency = warning_latency_us
        self.cpu_target = cpu_target
        
        self.metrics_history = []
        
    def check_latency(self,
                     metrics: LatencyMetrics) -> Dict:
        """
        检查延迟是否在可接受范围内
        
        Args:
            metrics: 延迟指标
            
        Returns:
            检查结果
        """
        total_latency = metrics.total_loop_us
        
        # 评估延迟
        if total_latency > self.max_total_latency:
            status = 'critical'
            action = 'reduce_strategy_complexity'
        elif total_latency > self.warning_latency:
            status = 'warning'
            action = 'optimize_code'
        else:
            status = 'ok'
            action = 'none'
            
        return {
            'status': status,
            'total_latency_us': total_latency,
            'action': action
        }
        
    def calculate_position_priority(self,
                                   latency_us: float,
                                   order_value: float) -> float:
        """
        计算订单优先级
        
        Args:
            latency_us: 延迟（微秒）
            order_value: 订单价值
            
        Returns:
            优先级分数（越高越优先）
        """
        # 优先级 = 订单价值 / 延迟
        priority = order_value / (latency_us / 1000000.0)
        
        return priority
```

---

### 6. 对冲策略

```python
class HedgingStrategy:
    """对冲策略"""
    
    def __init__(self,
                 hedge_threshold: float = 0.8,    # 对冲阈值（库存占最大值的比例）
                 hedge_ratio: float = 1.0,         # 对冲比率
                 hedge_cost_tolerance: float = 0.0005):  # 对冲成本容忍度
        self.hedge_threshold = hedge_threshold
        self.hedge_ratio = hedge_ratio
        self.hedge_cost_tolerance = hedge_cost_tolerance
        
    def should_hedge(self,
                      inventory: float,
                      max_inventory: float) -> bool:
        """
        判断是否应该对冲
        
        Args:
            inventory: 当前库存
            max_inventory: 最大库存
            
        Returns:
            是否应该对冲
        """
        inventory_ratio = abs(inventory) / max_inventory
        
        return inventory_ratio >= self.hedge_threshold
        
    def calculate_hedge_size(self,
                               inventory: float,
                               target_inventory: float = 0.0) -> float:
        """
        计算对冲规模
        
        Args:
            inventory: 当前库存
            target_inventory: 目标库存（通常为 0）
            
        Returns:
            对冲数量（正数表示买入对冲，负数表示卖出对冲）
        """
        # 对冲数量 = (目标库存 - 当前库存) × 对冲比率
        hedge_size = (target_inventory - inventory) * self.hedge_ratio
        
        return hedge_size
        
    def evaluate_hedge_cost(self,
                           hedge_price: float,
                           market_mid: float) -> float:
        """
        评估对冲成本
        
        Args:
            hedge_price: 对冲价格
            market_mid: 市场中间价
            
        Returns:
            对冲成本（占市场中间价的比例）
        """
        # 成本 = |对冲价格 - 中间价| / 中间价
        cost = abs(hedge_price - market_mid) / market_mid
        
        return cost
        
    def should_execute_hedge(self,
                               hedge_cost: float) -> bool:
        """
        判断是否应该执行对冲
        
        Args:
            hedge_cost: 对冲成本
            
        Returns:
            是否应该执行对冲
        """
        return hedge_cost <= self.hedge_cost_tolerance
```

---

### 7. 市场微观结构分析

```python
class MarketMicrostructure:
    """市场微观结构分析"""
    
    def __init__(self):
        self.order_book = {}
        self.trades = []
        
    def update_order_book(self,
                          order_book: Dict):
        """
        更新订单簿
        
        Args:
            order_book: {
                'bids': [(price, size), ...],
                'asks': [(price, size), ...],
                'timestamp': time
            }
        """
        self.order_book = order_book
        
    def calculate_order_book_imbalance(self) -> float:
        """
        计算订单簿不平衡
        
        Returns:
            不平衡度（-1 到 1），正数表示买方更强
        """
        bids = self.order_book.get('bids', [])
        asks = self.order_book.get('asks', [])
        
        # 计算买方和卖方总金额
        bid_volume = sum([size for price, size in bids])
        ask_volume = sum([size for price, size in asks])
        
        # 不平衡度 = (买方 - 卖方) / (买方 + 卖方)
        if bid_volume + ask_volume == 0:
            return 0.0
            
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        
        return imbalance
        
    def calculate_spread(self) -> float:
        """
        计算当前价差
        
        Returns:
            价差（绝对值和相对值）
        """
        bids = self.order_book.get('bids', [])
        asks = self.order_book.get('asks', [])
        
        if not bids or not asks:
            return 0.0, 0.0
            
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        
        absolute_spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2
        
        if mid_price == 0:
            return absolute_spread, 0.0
            
        relative_spread = absolute_spread / mid_price
        
        return absolute_spread, relative_spread
        
    def calculate_queue_position(self,
                                side: str,
                                price: float) -> int:
        """
        计算队列位置
        
        Args:
            side: 'bid' or 'ask'
            price: 价格
            
        Returns:
            队列中的位置（0 表示最前面）
        """
        order_side = self.order_book.get(side + 's', [])
        
        position = 0
        for order_price, size in order_side:
            if order_price == price:
                return position
            position += 1
            
        return -1  # 价格不存在
```

---

### 8. PnL 分解

```python
class PnLDecomposition:
    """PnL 分解"""
    
    def __init__(self):
        self.spread_pnl = 0.0
        self.inventory_pnl = 0.0
        self.hedge_cost = 0.0
        self.total_pnl = 0.0
        
        self.trades = []
        
    def add_trade(self,
                 trade: Dict):
        """
        添加交易
        
        Args:
            trade: {
                'side': 'buy' or 'sell',
                'price': 成交价,
                'quantity': 成交量,
                'spread_at_execution': 执行时的价差,
                'hedge_price': 对冲价格（如果有）
            }
        """
        self.trades.append(trade)
        
        # 计算价差收益
        spread_profit = trade['quantity'] * trade['spread_at_execution'] / 2
        self.spread_pnl += spread_profit
        
        # 计算对冲成本
        if 'hedge_price' in trade and trade['hedge_price']:
            hedge_cost = trade['quantity'] * abs(trade['hedge_price'] - trade['price'])
            self.hedge_cost += hedge_cost
            
    def update_inventory_pnl(self,
                              inventory: float,
                              current_price: float,
                              avg_entry_price: float):
        """
        更新库存 PnL
        
        Args:
            inventory: 当前库存
            current_price: 当前价格
            avg_entry_price: 平均进入价格
        """
        if inventory == 0:
            self.inventory_pnl = 0.0
            return
            
        # 库存收益 = 库存 × (当前价格 - 平均进入价格)
        self.inventory_pnl = inventory * (current_price - avg_entry_price)
        
    def get_total_pnl(self) -> float:
        """获取总 PnL"""
        self.total_pnl = self.spread_pnl + self.inventory_pnl - self.hedge_cost
        return self.total_pnl
        
    def get_pnl_breakdown(self) -> Dict:
        """
        获取 PnL 分解
        
        Returns:
            PnL 分解字典
        """
        total_pnl = self.get_total_pnl()
        
        return {
            'total_pnl': total_pnl,
            'spread_pnl': self.spread_pnl,
            'inventory_pnl': self.inventory_pnl,
            'hedge_cost': self.hedge_cost,
            'spread_contribution': self.spread_pnl / total_pnl if total_pnl != 0 else 0,
            'inventory_contribution': self.inventory_pnl / total_pnl if total_pnl != 0 else 0,
            'hedge_contribution': -self.hedge_cost / total_pnl if total_pnl != 0 else 0
        }
```

---

### 9. 风险限制

```python
class RiskLimits:
    """风险限制"""
    
    def __init__(self,
                 max_inventory: float = 1000,      # 最大库存
                 max_daily_loss: float = 10000,    # 最大单日损失
                 max_drawdown: float = 0.05,       # 最大回撤 5%
                 warning_drawdown: float = 0.03,   # 警告回撤 3%
                 shutdown_loss: float = 50000):    # 关停损失
        self.max_inventory = max_inventory
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.warning_drawdown = warning_drawdown
        self.shutdown_loss = shutdown_loss
        
        self.daily_pnl = 0.0
        self.peak_pnl = 0.0
        self.current_pnl = 0.0
        
    def check_inventory(self, inventory: float) -> Dict:
        """
        检查库存是否超限
        
        Args:
            inventory: 当前库存
            
        Returns:
            检查结果
        """
        abs_inventory = abs(inventory)
        
        if abs_inventory >= self.max_inventory:
            return {
                'violated': True,
                'severity': 'critical',
                'action': 'force_reduce_inventory',
                'message': f'库存超限: {abs_inventory} > {self.max_inventory}'
            }
        elif abs_inventory >= self.max_inventory * 0.8:
            return {
                'violated': False,
                'severity': 'warning',
                'action': 'consider_hedging',
                'message': f'库存接近上限: {abs_inventory}'
            }
        else:
            return {
                'violated': False,
                'severity': 'ok',
                'action': 'none',
                'message': '库存正常'
            }
            
    def check_daily_loss(self, daily_pnl: float) -> Dict:
        """
        检查单日损失
        
        Args:
            daily_pnl: 当日 PnL
            
        Returns:
            检查结果
        """
        self.daily_pnl = daily_pnl
        
        loss = -daily_pnl
        
        if loss >= self.shutdown_loss:
            return {
                'violated': True,
                'severity': 'critical',
                'action': 'shutdown',
                'message': f'达到关停损失: {loss}'
            }
        elif loss >= self.max_daily_loss:
            return {
                'violated': True,
                'severity': 'high',
                'action': 'reduce_position',
                'message': f'达到单日最大损失: {loss}'
            }
        else:
            return {
                'violated': False,
                'severity': 'ok',
                'action': 'none',
                'message': '损失在可接受范围内'
            }
            
    def check_drawdown(self, current_pnl: float) -> Dict:
        """
        检查回撤
        
        Args:
            current_pnl: 当前 PnL
            
        Returns:
            检查结果
        """
        self.current_pnl = current_pnl
        
        # 更新峰值
        if current_pnl > self.peak_pnl:
            self.peak_pnl = current_pnl
            
        # 计算回撤
        drawdown = (self.peak_pnl - current_pnl) / abs(self.peak_pnl) if self.peak_pnl != 0 else 0
        
        if drawdown >= self.max_drawdown:
            return {
                'violated': True,
                'severity': 'critical',
                'action': 'reduce_risk',
                'message': f'达到最大回撤: {drawdown:.2%}'
            }
        elif drawdown >= self.warning_drawdown:
            return {
                'violated': False,
                'severity': 'warning',
                'action': 'cautious',
                'message': f'接近最大回撤: {drawdown:.2%}'
            }
        else:
            return {
                'violated': False,
                'severity': 'ok',
                'action': 'none',
                'message': '回撤正常'
            }
            
    def should_stop_trading(self) -> bool:
        """判断是否应该停止交易"""
        # 任何关键风险限制被触发，停止交易
        inventory_check = self.check_inventory(0)
        daily_loss_check = self.check_daily_loss(self.daily_pnl)
        drawdown_check = self.check_drawdown(self.current_pnl)
        
        return (inventory_check['severity'] == 'critical' or
                daily_loss_check['severity'] == 'critical' or
                drawdown_check['severity'] == 'critical')
```

---

### 10. 性能指标

```python
class PerformanceMetrics:
    """性能指标"""
    
    def __init__(self):
        self.trades = []
        self.pnl = 0.0
        
    def add_trade(self, trade: Dict):
        """添加交易"""
        self.trades.append(trade)
        
    def calculate_metrics(self, pnl_series: pd.Series) -> Dict:
        """
        计算性能指标
        
        Args:
            pnl_series: PnL 序列
            
        Returns:
            性能指标字典
        """
        if len(pnl_series) < 2:
            return {}
            
        # 基础指标
        total_pnl = pnl_series.sum()
        avg_pnl = pnl_series.mean()
        std_pnl = pnl_series.std()
        
        # 夏普比率
        sharpe_ratio = avg_pnl / std_pnl * np.sqrt(252) if std_pnl > 0 else 0
        
        # 胜率
        win_rate = (pnl_series > 0).mean()
        
        # 换手率
        total_volume = sum([t['quantity'] for t in self.trades])
        avg_inventory = total_volume / 2
        turnover = total_volume / avg_inventory if avg_inventory > 0 else 0
        
        # 价差捕获率
        spread_captured = sum([t.get('spread_profit', 0) for t in self.trades])
        theoretical_max = total_volume * 0.0001  # 假设最大价差 1bp
        spread_capture_rate = spread_captured / theoretical_max if theoretical_max > 0 else 0
        
        # 填单率
        filled_orders = sum([1 for t in self.trades if t.get('filled', True)])
        total_orders = len(self.trades)
        fill_rate = filled_orders / total_orders if total_orders > 0 else 0
        
        return {
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'std_pnl': std_pnl,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'turnover': turnover,
            'spread_captured': spread_captured,
            'spread_capture_rate': spread_capture_rate,
            'fill_rate': fill_rate,
            'total_trades': len(self.trades),
            'total_volume': total_volume
        }
```

---

## 完整做市引擎

```python
class MarketMakingEngine:
    """完整做市引擎"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 配置字典 {
                'risk_aversion': 风险厌恶系数,
                'base_spread': 基础价差,
                'max_inventory': 最大库存,
                ...
            }
        """
        # 初始化各个模块
        self.mm_model = AvellanedaStoikovMM(
            risk_aversion=config.get('risk_aversion', 0.1),
            base_spread=config.get('base_spread', 0.0002)
        )
        
        self.inventory_manager = InventoryManager(
            max_inventory=config.get('max_inventory', 1000),
            warning_inventory=config.get('warning_inventory', 800)
        )
        
        self.quote_manager = QuoteManager(
            min_spread=config.get('min_spread', 0.0001),
            max_spread=config.get('max_spread', 0.002)
        )
        
        self.adverse_detector = AdverseSelectionDetector()
        self.hedge_strategy = HedgingStrategy()
        self.market_structure = MarketMicrostructure()
        self.pnl_decomposer = PnLDecomposition()
        self.risk_limits = RiskLimits()
        self.performance = PerformanceMetrics()
        
        self.current_state = MarketState(
            mid_price=0.0,
            volatility=0.0,
            volume=0.0,
            inventory=0.0,
            time_to_end=1.0
        )
        
    def on_market_data(self, market_data: Dict):
        """
        处理市场数据
        
        Args:
            market_data: 市场数据 {
                'mid_price': 中间价,
                'volatility': 波动率,
                'volume': 成交量,
                'order_book': 订单簿
            }
        """
        # 更新市场状态
        self.current_state.mid_price = market_data['mid_price']
        self.current_state.volatility = market_data['volatility']
        self.current_state.volume = market_data['volume']
        
        # 更新订单簿
        self.market_structure.update_order_book(market_data['order_book'])
        
        # 生成报价
        self.generate_quotes()
        
    def generate_quotes(self) -> Tuple[float, float]:
        """
        生成最优报价
        
        Returns:
            (bid_price, ask_price)
        """
        # 1. 计算基础报价
        bid, ask = self.mm_model.calculate_optimal_quotes(self.current_state)
        
        # 2. 根据库存调整报价
        bid, ask = self.quote_manager.adjust_for_inventory(
            bid, ask,
            self.current_state.inventory,
            self.current_state.mid_price
        )
        
        # 3. 平滑报价
        bid, ask = self.quote_manager.calculate_smooth_quotes(bid, ask)
        
        # 4. 检测不利选择
        adverse_result = self.adverse_detector.calculate_adverse_selection(
            self.current_state.mid_price
        )
        
        # 5. 如有必要扩大价差
        if self.adverse_detector.should_widen_spread(adverse_result):
            spread_multiplier = self.adverse_detector.get_spread_multiplier(adverse_result)
            center = (bid + ask) / 2
            current_spread = ask - bid
            new_spread = current_spread * spread_multiplier
            bid = center - new_spread / 2
            ask = center + new_spread / 2
            
        return bid, ask
        
    def on_trade(self, trade: Dict):
        """
        处理成交
        
        Args:
            trade: 交易 {
                'side': 'buy' or 'sell',
                'price': 成交价,
                'quantity': 成交量
            }
        """
        # 更新库存
        if trade['side'] == 'buy':
            self.current_state.inventory += trade['quantity']
        else:
            self.current_state.inventory -= trade['quantity']
            
        # 添加到不利选择检测
        self.adverse_detector.add_trade(trade)
        
        # 添加到 PnL 分解
        self.pnl_decomposer.add_trade(trade)
        
        # 添加到性能指标
        self.performance.add_trade(trade)
        
        # 检查风险限制
        inventory_check = self.risk_limits.check_inventory(
            self.current_state.inventory
        )
        
        if inventory_check['violated']:
            print(f"风险触发: {inventory_check['message']}")
            
        # 检查是否需要对冲
        if self.hedge_strategy.should_hedge(
            self.current_state.inventory,
            self.inventory_manager.max_inventory
        ):
            self.execute_hedge()
            
    def execute_hedge(self):
        """执行对冲"""
        # 计算对冲规模
        hedge_size = self.hedge_strategy.calculate_hedge_size(
            self.current_state.inventory
        )
        
        # 执行对冲（实际实现需要与交易系统对接）
        print(f"执行对冲: {hedge_size}")
        
        # 更新库存
        self.current_state.inventory -= hedge_size
        
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        return self.performance.calculate_metrics(
            pd.Series([t.get('pnl', 0) for t in self.performance.trades])
        )
```

---

## 配置参数

```python
DEFAULT_MM_CONFIG = {
    # Avellaneda-Stoikov 参数
    'risk_aversion': 0.1,          # 风险厌恶系数 γ
    'base_spread': 0.0002,         # 基础价差 (2bp)
    
    # 库存管理
    'max_inventory': 1000,          # 最大库存
    'warning_inventory': 800,        # 警告库存
    'neutral_target': 0.0,          # 目标中性库存
    'adjustment_factor': 0.01,      # 库存调整因子
    
    # 报价管理
    'min_spread': 0.0001,          # 最小价差 (1bp)
    'max_spread': 0.002,           # 最大价差 (20bp)
    'adjustment_speed': 0.5,        # 调整速度
    
    # 不利选择检测
    'detection_window': 100,         # 检测窗口
    'adverse_threshold': 0.3,      # 不利选择阈值 (30%)
    'price_move_window': 10,        # 价格移动窗口
    
    # 对冲策略
    'hedge_threshold': 0.8,         # 对冲阈值 (80% 库存)
    'hedge_ratio': 1.0,            # 对冲比率
    'hedge_cost_tolerance': 0.0005,  # 对冲成本容忍度 (5bp)
    
    # 风险限制
    'max_daily_loss': 10000,        # 最大单日损失
    'max_drawdown': 0.05,           # 最大回撤 (5%)
    'warning_drawdown': 0.03,       # 警告回撤 (3%)
    'shutdown_loss': 50000,          # 关停损失
}
```

---

## 目标性能指标

```python
PERFORMANCE_TARGETS = {
    # 价差捕获
    'min_spread_capture_rate': 0.6,    # 至少捕获 60% 价差
    'avg_spread_per_trade': 0.00015,    # 平均每笔捕获 1.5bp
    
    # 风险调整收益
    'target_sharpe_ratio': 2.0,         # 目标夏普比率 2.0
    'max_drawdown': 0.05,              # 最大回撤 5%
    
    # 交易效率
    'target_fill_rate': 0.8,            # 目标填单率 80%
    'max_turnover': 10.0,              # 最大年换手率 10 倍
    
    # 库存管理
    'avg_inventory_level': 0.3,         # 平均库存水平 30%
    'inventory_neutrality': 0.1,        # 库存中性度（标准差）
}
```

---

_创建时间：2026年2月23日_
