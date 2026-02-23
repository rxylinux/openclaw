# Citadel 阿尔法信号研究实验室

You are a senior quantitative researcher at Citadel who discovers and validates new alpha signals by analyzing alternative data, market microstructure, and statistical patterns across thousands of securities.

I need a systematic process for discovering profitable trading signals.

Research:

- Signal idea generation framework: 20 categories of potential alpha signals to investigate
- Data source inventory: price data, fundamental data, sentiment data, and alternative data sources
- Feature engineering pipeline: transform raw data into testable trading signals step by step
- Signal strength testing: information coefficient, hit rate, and risk-adjusted return for each signal
- Decay analysis: how quickly each signal loses its predictive power after formation
- Correlation check: ensure new signals aren't just repackaging existing known factors
- Signal combination methodology: how to blend multiple weak signals into one strong composite
- Regime detection: identify which signals work in trending vs mean-reverting vs volatile markets
- Turnover analysis: how often signal forces trades and whether alpha survives transaction costs
- Signal monitoring dashboard: track live signal performance against backtested expectations

Format as a Citadel-style quantitative research report with signal definitions, statistical test results, and Python code for signal generation.

My focus: [DESCRIBE YOUR MARKET, AVAILABLE DATA SOURCES, TRADING FREQUENCY, AND TYPES OF SIGNALS YOU'RE INTERESTED IN]

---

## 使用说明

这是一个 Citadel 风格的阿尔法信号研究框架，用于系统化地发现和验证交易信号。

### 使用方法

将 `[DESCRIBE YOUR MARKET, AVAILABLE DATA SOURCES, TRADING FREQUENCY, AND TYPES OF SIGNALS YOU'RE INTERESTED IN]` 替换为你的具体情况，例如：

```
My focus: US equity market, access to price, volume, fundamental data, and some alternative data sources (satellite imagery, social media), daily frequency, interested in momentum, reversal, and sentiment signals.
```

### 适用场景

- 系统化地发现新的阿尔法信号
- 验证信号的有效性和稳健性
- 构建信号组合
- 监控信号性能衰减

---

## 信号发现框架

### 20个潜在阿尔法信号类别

```python
from enum import Enum
from typing import List, Dict

class SignalCategory(Enum):
    """阿尔法信号类别"""
    
    # 价格动量类
    MOMENTUM_1M = "1-month momentum"
    MOMENTUM_3M = "3-month momentum"
    MOMENTUM_12M = "12-month momentum"
    MOMENTUM_REVERSAL = "momentum reversal"
    
    # 均值回归类
    MEAN_REVERSION_5D = "5-day mean reversion"
    MEAN_REVERSION_20D = "20-day mean reversion"
    RSI_SIGNAL = "RSI overbought/oversold"
    BOLLINGER_BANDS = "Bollinger Bands breakout"
    
    # 波动率类
    VOLATILITY_MEAN_REVERSION = "volatility mean reversion"
    VOLATILITY_BREAKOUT = "volatility breakout"
    VIX_SIGNAL = "VIX-based signal"
    
    # 成交量类
    VOLUME_SURGE = "volume surge"
    VOLUME_PRICE_TREND = "volume-price divergence"
    ACCUMULATION_DISTRIBUTION = "accumulation/distribution"
    
    # 基本面类
    EARNINGS_MOMENTUM = "earnings momentum"
    REVISION_MOMENTUM = "analyst revision momentum"
    VALUE_SIGNAL = "value signal (P/E, P/B)"
    GROWTH_SIGNAL = "growth signal (revenue, earnings)"
    
    # 另类数据类
    SENTIMENT_SIGNAL = "sentiment signal"
    INSIDER_TRADING = "insider trading signal"
    OPTION_FLOW = "option flow signal"
    SOCIAL_MEDIA = "social media signal"
```

---

## 数据源清单

```python
class DataSource:
    """数据源清单"""
    
    PRICE_DATA = {
        'source': 'OHLCV',
        'frequency': ['tick', 'minute', 'hourly', 'daily'],
        'fields': ['open', 'high', 'low', 'close', 'volume'],
        'quality': 'high'
    }
    
    FUNDAMENTAL_DATA = {
        'source': 'company fundamentals',
        'frequency': ['quarterly', 'annual'],
        'fields': ['revenue', 'earnings', 'book_value', 'cash_flow',
                  'debt', 'equity', 'dividends', 'EPS', 'PE', 'PB'],
        'quality': 'high'
    }
    
    SENTIMENT_DATA = {
        'source': 'news/social sentiment',
        'frequency': ['daily', 'hourly'],
        'fields': ['sentiment_score', 'topic', 'volume'],
        'quality': 'medium'
    }
    
    ALTERNATIVE_DATA = {
        'satellite_imagery': {
            'fields': ['parking_lot_occupancy', 'shipping_traffic'],
            'quality': 'high'
        },
        'credit_card': {
            'fields': ['spending_trends'],
            'quality': 'high'
        },
        'web_scraping': {
            'fields': ['product_price', 'inventory_level'],
            'quality': 'medium'
        },
        'social_media': {
            'fields': ['mentions', 'engagement', 'sentiment'],
            'quality': 'low'
        }
    }
```

---

## 特征工程流程

```python
import pandas as pd
import numpy as np
from typing import Callable, List
from abc import ABC, abstractmethod

class BaseSignal(ABC):
    """信号基类"""
    
    def __init__(self, name: str, lookback: int):
        self.name = name
        self.lookback = lookback
        
    @abstractmethod
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """计算信号"""
        pass
        
    def normalize(self, signal: pd.Series) -> pd.Series:
        """标准化信号到 [-1, 1]"""
        return (signal - signal.mean()) / signal.std()
        
    def rank(self, signal: pd.Series) -> pd.Series:
        """信号排序（横截面排名）"""
        return signal.rank(pct=True) * 2 - 1  # 转换到 [-1, 1]

class MomentumSignal(BaseSignal):
    """动量信号"""
    
    def __init__(self, period: int = 20):
        super().__init__(f"Momentum_{period}d", period)
        self.period = period
        
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """
        计算动量信号
        
        Returns:
            信号值（标准化）
        """
        # 计算收益率
        returns = data['close'].pct_change(self.period)
        
        # Z-score 标准化
        signal = (returns - returns.mean()) / returns.std()
        
        return signal.fillna(0)

class MeanReversionSignal(BaseSignal):
    """均值回归信号"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(f"MeanReversion_{period}d", period)
        self.period = period
        self.std_dev = std_dev
        
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """
        计算均值回归信号
        
        Returns:
            信号值：正数表示超卖（做多），负数表示超买（做空）
        """
        # 计算布林带
        rolling_mean = data['close'].rolling(self.period).mean()
        rolling_std = data['close'].rolling(self.period).std()
        
        upper_band = rolling_mean + self.std_dev * rolling_std
        lower_band = rolling_mean - self.std_dev * rolling_std
        
        # 计算Z-score
        z_score = (data['close'] - rolling_mean) / rolling_std
        
        # 反转信号：Z-score越小，信号越强
        signal = -z_score
        
        return signal.fillna(0)

class VolumePriceSignal(BaseSignal):
    """成交量-价格背离信号"""
    
    def __init__(self, period: int = 5):
        super().__init__(f"VolumePrice_{period}d", period)
        self.period = period
        
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """
        计算成交量-价格背离信号
        
        Returns:
            信号值：正数表示放量上涨（买入），负数表示放量下跌（卖出）
        """
        # 价格变化
        price_change = data['close'].pct_change(self.period)
        
        # 成交量变化
        volume_change = data['volume'].pct_change(self.period)
        
        # 标准化
        price_change = (price_change - price_change.mean()) / price_change.std()
        volume_change = (volume_change - volume_change.mean()) / volume_change.std()
        
        # 信号：价格上涨且放量
        signal = price_change * volume_change
        
        return signal.fillna(0)

class RSISignal(BaseSignal):
    """RSI 信号"""
    
    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        super().__init__(f"RSI_{period}d", period)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """
        计算 RSI 信号
        
        Returns:
            信号值：正数表示超卖（做多），负数表示超买（做空）
        """
        # 计算价格变化
        delta = data['close'].diff()
        
        # 分离上涨和下跌
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # 计算平均上涨和下跌
        avg_gains = gains.rolling(self.period).mean()
        avg_losses = losses.rolling(self.period).mean()
        
        # 计算 RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # 转换为信号：RSI越低，信号越强（做多）
        signal = (50 - rsi) / 50  # 转换到 [-1, 1]
        
        return signal.fillna(0)

class FeaturePipeline:
    """特征工程流水线"""
    
    def __init__(self):
        self.signals = {}
        
    def add_signal(self, signal: BaseSignal):
        """添加信号"""
        self.signals[signal.name] = signal
        
    def compute_all_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有信号
        
        Returns:
            包含所有信号的数据框
        """
        signal_df = pd.DataFrame(index=data.index)
        
        for signal_name, signal in self.signals.items():
            signal_df[signal_name] = signal.compute(data)
            
        return signal_df
```

---

## 信号强度测试

```python
from scipy import stats
from typing import Tuple, Dict

class SignalTester:
    """信号测试器"""
    
    def __init__(self, 
                 lookforward: int = 5,
                 significance_level: float = 0.05):
        """
        Args:
            lookforward: 向前展望期数
            significance_level: 显著性水平
        """
        self.lookforward = lookforward
        self.significance_level = significance_level
        
    def test_signal(self,
                    signals: pd.Series,
                    forward_returns: pd.Series) -> Dict:
        """
        测试信号有效性
        
        Args:
            signals: 信号序列
            forward_returns: 向前收益序列
            
        Returns:
            测试结果字典
        """
        # 对齐数据
        aligned = pd.DataFrame({
            'signal': signals,
            'forward_return': forward_returns
        }).dropna()
        
        signal = aligned['signal']
        returns = aligned['forward_return']
        
        # 1. 信息系数 (IC)
        ic = signal.corr(returns)
        
        # 2. IC 的 t 统计量
        t_stat, p_value = stats.ttest_ind(
            signal[signal > 0],
            signal[signal < 0]
        )
        
        # 3. 分组测试（按信号强度分组）
        signal_rank = signal.rank(pct=True)
        
        quintile_returns = []
        for i in range(1, 6):
            mask = (signal_rank > (i-1)/5) & (signal_rank <= i/5)
            quintile_return = returns[mask].mean()
            quintile_returns.append(quintile_return)
            
        # 4. 多空组合收益
        long_return = returns[signal_rank > 0.8].mean()  # 前 20%
        short_return = returns[signal_rank < 0.2].mean()  # 后 20%
        ls_return = long_return - short_return
        
        # 5. 胜率
        long_win_rate = (returns[signal_rank > 0.8] > 0).mean()
        short_win_rate = (returns[signal_rank < 0.2] < 0).mean()
        
        # 6. 夏普比率
        long_sharpe = self._calculate_sharpe(returns[signal_rank > 0.8])
        short_sharpe = self._calculate_sharpe(returns[signal_rank < 0.2])
        ls_sharpe = self._calculate_sharpe(
            long_return - short_return
        )
        
        return {
            'ic': ic,
            'ic_t_stat': t_stat,
            'ic_p_value': p_value,
            'ic_significant': p_value < self.significance_level,
            'quintile_returns': quintile_returns,
            'long_return': long_return,
            'short_return': short_return,
            'long_short_return': ls_return,
            'long_win_rate': long_win_rate,
            'short_win_rate': short_win_rate,
            'long_sharpe': long_sharpe,
            'short_sharpe': short_sharpe,
            'long_short_sharpe': ls_sharpe
        }
        
    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0.0
            
        mean_return = returns.mean()
        std_return = returns.std()
        
        if std_return == 0:
            return 0.0
            
        sharpe = mean_return / std_return
        
        # 年化
        sharpe *= np.sqrt(252)  # 假设日数据
        
        return sharpe
        
    def decay_analysis(self,
                      signal: pd.Series,
                      returns: pd.DataFrame,
                      max_lookforward: int = 20) -> pd.DataFrame:
        """
        分析信号衰减
        
        Returns:
            不同前瞻期的信号强度
        """
        results = []
        
        for lookforward in range(1, max_lookforward + 1):
            forward_return = returns['close'].pct_change(lookforward).shift(-lookforward)
            
            test_result = self.test_signal(signal, forward_return)
            
            results.append({
                'lookforward': lookforward,
                'ic': test_result['ic'],
                'ls_return': test_result['long_short_return'],
                'ls_sharpe': test_result['long_short_sharpe']
            })
            
        return pd.DataFrame(results)
```

---

## 信号相关性检查

```python
class CorrelationChecker:
    """信号相关性检查"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        
    def check_signal_overlap(self,
                             new_signal: pd.Series,
                             existing_signals: Dict[str, pd.Series]) -> Dict:
        """
        检查新信号与已有信号的重叠度
        
        Args:
            new_signal: 新信号
            existing_signals: 已有信号字典 {name: series}
            
        Returns:
            相关性分析结果
        """
        correlations = {}
        
        for signal_name, signal_series in existing_signals.items():
            # 对齐数据
            aligned = pd.DataFrame({
                'new': new_signal,
                'existing': signal_series
            }).dropna()
            
            # 计算相关性
            corr = aligned['new'].corr(aligned['existing'])
            correlations[signal_name] = corr
            
        # 找出高相关信号
        high_corr_signals = {
            name: corr for name, corr in correlations.items()
            if abs(corr) > self.threshold
        }
        
        return {
            'correlations': correlations,
            'high_correlation_signals': high_corr_signals,
            'is_overlapping': len(high_corr_signals) > 0
        }
```

---

## 信号组合方法

```python
class SignalCombiner:
    """信号组合器"""
    
    @staticmethod
    def equal_weight(signals: pd.DataFrame) -> pd.Series:
        """等权重组合"""
        return signals.mean(axis=1)
        
    @staticmethod
    def ic_weighted(signals: pd.DataFrame, 
                   ic_dict: Dict[str, float]) -> pd.Series:
        """
        IC 加权组合
        
        Args:
            signals: 信号数据框
            ic_dict: IC 字典 {signal_name: ic_value}
            
        Returns:
            组合信号
        """
        # 归一化 IC（取绝对值）
        abs_ic = {k: abs(v) for k, v in ic_dict.items()}
        total_ic = sum(abs_ic.values())
        
        weights = {k: v / total_ic for k, v in abs_ic.items()}
        
        # 加权组合
        combined = pd.Series(0.0, index=signals.index)
        for signal_name, weight in weights.items():
            if signal_name in signals.columns:
                combined += signals[signal_name] * weight
                
        return combined
        
    @staticmethod
    def rank_weighted(signals: pd.DataFrame) -> pd.Series:
        """排序加权组合"""
        # 每个信号排序
        ranked_signals = signals.rank(axis=0, pct=True) * 2 - 1
        
        # 等权重组合
        return ranked_signals.mean(axis=1)
        
    @staticmethod
    def ensemble(signals: pd.DataFrame,
                weights: List[float]) -> pd.Series:
        """
        自定义权重组合
        
        Args:
            signals: 信号数据框
            weights: 权重列表
        """
        weights = np.array(weights)
        weights = weights / weights.sum()  # 归一化
        
        return signals.dot(weights)
```

---

## 市场状态识别

```python
class RegimeDetector:
    """市场状态检测"""
    
    def __init__(self, window: int = 60):
        self.window = window
        
    def detect_regime(self, data: pd.DataFrame) -> str:
        """
        检测当前市场状态
        
        Returns:
            市场状态: 'trending', 'mean_reverting', 'volatile'
        """
        # 计算价格动量
        momentum = data['close'].pct_change(self.window).iloc[-1]
        
        # 计算波动率
        returns = data['close'].pct_change()
        volatility = returns.rolling(self.window).std().iloc[-1]
        
        # 计算自相关性
        autocorr = returns.autocorr(lag=1)
        
        # 判断市场状态
        if abs(momentum) > 0.05:  # 5% 以上动量
            return 'trending'
        elif autocorr < -0.1:  # 强负相关 = 均值回归
            return 'mean_reverting'
        elif volatility > volatility.rolling(self.window * 2).mean().iloc[-1] * 1.5:
            return 'volatile'
        else:
            return 'neutral'
            
    def get_regime_performance(self,
                               signal_tester: SignalTester,
                               signals: pd.DataFrame,
                               returns: pd.DataFrame,
                               regime: str) -> Dict:
        """
        获取特定市场状态下的信号表现
        
        Args:
            signal_tester: 信号测试器
            signals: 信号数据框
            returns: 收益数据框
            regime: 市场状态
            
        Returns:
            各信号在该状态下的表现
        """
        regime_results = {}
        
        for signal_name in signals.columns:
            test_result = signal_tester.test_signal(
                signals[signal_name],
                returns['close'].pct_change().shift(-signal_tester.lookforward)
            )
            regime_results[signal_name] = test_result
            
        return regime_results
```

---

## 换手率分析

```python
class TurnoverAnalyzer:
    """换手率分析"""
    
    @staticmethod
    def calculate_turnover(signals: pd.DataFrame,
                          portfolio_size: int = 100) -> pd.Series:
        """
        计算换手率
        
        Args:
            signals: 信号数据框
            portfolio_size: 组合持仓数量
            
        Returns:
            每日换手率
        """
        turnover = pd.Series(0.0, index=signals.index)
        
        # 每日选取组合
        for i in range(1, len(signals)):
            # 前一日组合
            prev_portfolio = signals.iloc[i-1].nlargest(portfolio_size).index
            
            # 当日组合
            curr_portfolio = signals.iloc[i].nlargest(portfolio_size).index
            
            # 计算变化
            new_positions = set(curr_portfolio) - set(prev_portfolio)
            removed_positions = set(prev_portfolio) - set(curr_portfolio)
            
            # 换手率 = (新增 + 移除) / 组合大小
            turnover_rate = (len(new_positions) + len(removed_positions)) / portfolio_size
            turnover.iloc[i] = turnover_rate
            
        return turnover
        
    @staticmethod
    def estimate_transaction_cost(turnover: pd.Series,
                                 cost_per_trade: float = 0.003) -> float:
        """
        估计交易成本
        
        Args:
            turnover: 换手率序列
            cost_per_trade: 单次交易成本
            
        Returns:
            年化交易成本
        """
        # 每日平均换手率
        avg_turnover = turnover.mean()
        
        # 日成本
        daily_cost = avg_turnover * cost_per_trade
        
        # 年化成本
        annual_cost = daily_cost * 252
        
        return annual_cost
```

---

## 信号监控仪表板

```python
from datetime import datetime
from typing import Dict, List

class SignalDashboard:
    """信号监控仪表板"""
    
    def __init__(self):
        self.signal_history = {}
        self.signal_metrics = {}
        
    def update_signal(self,
                      signal_name: str,
                      current_value: float,
                      forward_return: float):
        """更新信号历史"""
        if signal_name not in self.signal_history:
            self.signal_history[signal_name] = []
            
        self.signal_history[signal_name].append({
            'date': datetime.now(),
            'signal_value': current_value,
            'forward_return': forward_return
        })
        
    def calculate_live_metrics(self,
                               signal_name: str,
                               window: int = 30) -> Dict:
        """计算实时指标"""
        history = self.signal_history[signal_name]
        
        if len(history) < window:
            return {}
            
        # 获取最近 window 条记录
        recent = history[-window:]
        
        # 提取数据
        signal_values = [h['signal_value'] for h in recent]
        returns = [h['forward_return'] for h in recent]
        
        # 计算指标
        ic = np.corrcoef(signal_values, returns)[0, 1]
        
        win_rate = np.mean([r > 0 for r in returns])
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        sharpe = avg_return / std_return * np.sqrt(252) if std_return > 0 else 0
        
        return {
            'ic': ic,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'std_return': std_return,
            'sharpe': sharpe,
            'sample_size': len(recent)
        }
        
    def generate_daily_report(self, 
                              signal_names: List[str],
                              backtested_metrics: Dict[str, Dict]) -> str:
        """生成每日报告"""
        report = []
        report.append("=" * 70)
        report.append(f"信号监控报告 - {datetime.now().strftime('%Y-%m-%d')}")
        report.append("=" * 70)
        
        for signal_name in signal_names:
            report.append(f"\n【信号：{signal_name}】")
            
            # 实时表现
            live_metrics = self.calculate_live_metrics(signal_name)
            
            if live_metrics:
                report.append(f"实时 IC: {live_metrics['ic']:.4f}")
                report.append(f"实时胜率: {live_metrics['win_rate']:.2%}")
                report.append(f"实时收益: {live_metrics['avg_return']:.4f}")
                report.append(f"实时夏普: {live_metrics['sharpe']:.2f}")
            else:
                report.append("实时数据不足")
                
            # 与回测对比
            if signal_name in backtested_metrics:
                backtested = backtested_metrics[signal_name]
                report.append(f"回测 IC: {backtested['ic']:.4f}")
                
                if live_metrics:
                    # 性能漂移检测
                    ic_drift = live_metrics['ic'] - backtested['ic']
                    if abs(ic_drift) > 0.1:
                        report.append(f"⚠️ IC 漂移: {ic_drift:.4f}")
                    else:
                        report.append("✅ IC 稳定")
                        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
```

---

## 完整研究流程示例

```python
# 1. 初始化特征工程流水线
pipeline = FeaturePipeline()

# 2. 添加各种信号
pipeline.add_signal(MomentumSignal(period=20))
pipeline.add_signal(MomentumSignal(period=60))
pipeline.add_signal(MeanReversionSignal(period=5))
pipeline.add_signal(MeanReversionSignal(period=20))
pipeline.add_signal(RSISignal(period=14))
pipeline.add_signal(VolumePriceSignal(period=5))

# 3. 加载数据并计算信号
data = pd.read_csv('your_data.csv', parse_dates=['date'], index_col='date')
signals_df = pipeline.compute_all_signals(data)

# 4. 计算前瞻收益
signals_df['forward_return'] = data['close'].pct_change(5).shift(-5)

# 5. 测试每个信号
tester = SignalTester(lookforward=5)
signal_results = {}

for signal_name in signals_df.columns:
    if signal_name != 'forward_return':
        result = tester.test_signal(
            signals_df[signal_name],
            signals_df['forward_return']
        )
        signal_results[signal_name] = result

# 6. 衰减分析
decay_results = {}
for signal_name in signals_df.columns:
    if signal_name != 'forward_return':
        decay = tester.decay_analysis(
            signals_df[signal_name],
            signals_df,
            max_lookforward=20
        )
        decay_results[signal_name] = decay

# 7. 信号组合
combiner = SignalCombiner()
combined_signal = combiner.equal_weight(
    signals_df[[col for col in signals_df.columns if col != 'forward_return']]
)

# 8. 换手率分析
turnover = TurnoverAnalyzer.calculate_turnover(
    signals_df[[col for col in signals_df.columns if col != 'forward_return']],
    portfolio_size=100
)
annual_cost = TurnoverAnalyzer.estimate_transaction_cost(turnover)

print(f"年化交易成本: {annual_cost:.2%}")
```

---

## 信号选择标准

```python
SIGNAL_SELECTION_CRITERIA = {
    # IC 标准
    'min_abs_ic': 0.03,           # 最小绝对 IC
    'ic_significant': True,          # IC 必须显著
    
    # 收益标准
    'min_long_short_return': 0.005,  # 最小多空收益 (0.5%)
    'min_long_short_sharpe': 1.0,    # 最小多空夏普
    
    # 稳定性标准
    'max_ic_std': 0.05,             # IC 标准差
    'decay_half_life': 5,            # 衰减半衰期（天）
    
    # 换手率标准
    'max_turnover': 0.5,             # 最大日均换手率 (50%)
    'max_turnover_cost': 0.02,       # 最大换手成本 (2%)
    
    # 相关性标准
    'max_correlation_with_existing': 0.7  # 与已有信号最大相关性
}

def select_signals(signal_results: Dict[str, Dict]) -> List[str]:
    """
    选择有效信号
    
    Args:
        signal_results: 信号测试结果字典
        
    Returns:
        符合条件的信号名称列表
    """
    selected = []
    
    for signal_name, result in signal_results.items():
        # IC 检查
        if abs(result['ic']) < SIGNAL_SELECTION_CRITERIA['min_abs_ic']:
            continue
            
        if not result['ic_significant']:
            continue
            
        # 收益检查
        if abs(result['long_short_return']) < SIGNAL_SELECTION_CRITERIA['min_long_short_return']:
            continue
            
        if abs(result['long_short_sharpe']) < SIGNAL_SELECTION_CRITERIA['min_long_short_sharpe']:
            continue
            
        selected.append(signal_name)
        
    return selected
```

---

_创建时间：2026年2月23日_
