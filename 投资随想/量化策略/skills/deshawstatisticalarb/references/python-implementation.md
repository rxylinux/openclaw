# D.E. Shaw统计套利系统Python实现指南

## 完整实现架构

### 主要组件

1. **PairSelector** - 主要类
2. **CointegrationTester** - 主要类
3. **PairScreening** - 主要类

## 代码实现

### 代码块 1

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats
from statsmodels.tsa.stattools import coint, adfuller

class PairSelector:
    """配对选择器"""
    
    def __init__(self,
                 min_correlation: float = 0.8,      # 最小相关性
                 min_correlation_period: int = 252,  # 相关性计算窗口
                 min_liquidity: float = 1000000,     # 最小日均成交量
                 min_price: float = 5.0):            # 最小价格
        self.min_correlation = min_correlation
        self.min_correlation_period = min_correlation_period
        self.min_liquidity = min_liquidity
        self.min_price = min_price
        
    def calculate_rolling_correlation(self,
                                    price1: pd.Series,
                                    price2: pd.Series,
                                    window: int = None) -> float:
        """
        计算滚动相关性
        
        Args:
            price1: 股票1价格序列
            price2: 股票2价格序列
            window: 滚动窗口（None = 全部历史）
            
        Returns:
            相关性系数
        """
        # 使用收益率计算相关性
        returns1 = np.log(price1).diff().dropna()
        returns2 = np.log(price2).diff().dropna()
        
        if window is not None:
            corr = returns1.rolling(window).corr(returns2)
            return corr.iloc[-1]
        else:
            return returns1.corr(returns2)
            
    def calculate_correlation_matrix(self,
                                    prices: pd.DataFrame) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            prices: 价格数据框 {stock: price_series}
            
        Returns:
            相关性矩阵
        """
        # 使用收益率计算
        returns = np.log(prices).diff().dropna()
        
        # 计算相关性
        corr_matrix = returns.corr()
        
        return corr_matrix
        
    def find_highly_correlated_pairs(self,
                                      prices: pd.DataFrame,
                                      volumes: pd.DataFrame = None) -> List[Tuple[str, str, float]]:
        """
        找到高相关配对
        
        Args:
            prices: 价格数据
            volumes: 成交量数据（可选）
            
        Returns:
            配对列表 [(stock1, stock2, correlation)]
        """
        # 过滤流动性
        if volumes is not None:
            avg_volumes = volumes.mean()
            liquid_stocks = avg_volumes[avg_volumes >= self.min_liquidity].index.tolist()
        else:
            liquid_stocks = prices.columns.tolist()
            
        # 过滤价格
        avg_prices = prices.mean()
        eligible_stocks = [s for s in liquid_stocks 
                          if s in avg_prices.index and 
                          avg_prices[s] >= self.min_price]
            
        # 计算相关性矩阵
        corr_matrix = self.calculate_correlation_matrix(prices[eligible_stocks])
        
        # 找出高相关配对
        pairs = []
        n_stocks = len(eligible_stocks)
        
        for i in range(n_stocks):
            for j in range(i + 1, n_stocks):
                stock1 = eligible_stocks[i]
                stock2 = eligible_stocks[j]
                correlation = corr_matrix.loc[stock1, stock2]
                
                if correlation >= self.min_correlation:
                    pairs.append((stock1, stock2, correlation))
                    
        # 按相关性排序
        pairs.sort(key=lambda x: x[2], reverse=True)
        
        return pairs

```

### 代码块 2

```python
class CointegrationTester:
    """协整测试器"""
    
    def __init__(self,
                 significance_level: float = 0.05):  # 显著性水平
        self.significance_level = significance_level
        
    def engle_granger_test(self,
                             price1: pd.Series,
                             price2: pd.Series) -> Dict:
        """
        Engle-Granger 两步协整检验
        
        步骤：
        1. 用股票1对股票2回归：Price1 = α + β × Price2 + ε
        2. 对残差ε进行ADF单位根检验
        3. 如果残差是平稳的（拒绝单位根假设），则存在协整关系
        
        Args:
            price1: 股票1价格序列
            price2: 股票2价格序列
            
        Returns:
            测试结果字典
        """
        # 对齐数据
        aligned = pd.DataFrame({'y': price1, 'x': price2}).dropna()
        
        # 添加常数项
        X = aligned['x']
        X = sm.add_constant(X)
        y = aligned['y']
        
        # 运行回归
        model = sm.OLS(y, X).fit()
        residuals = model.resid
        
        # 对残差进行ADF检验
        adf_result = adfuller(residuals)
        
        # 提取结果
        test_statistic = adf_result[0]
        p_value = adf_result[1]
        critical_values = adf_result[4]
        
        # 判断是否协整
        is_cointegrated = p_value < self.significance_level
        
        # 计算对冲比率（回归系数）
        hedge_ratio = model.params['x']
        
        return {
            'cointegrated': is_cointegrated,
            'test_statistic': test_statistic,
            'p_value': p_value,
            'critical_5pct': critical_values['5%'],
            'critical_1pct': critical_values['1%'],
            'hedge_ratio': hedge_ratio,
            'intercept': model.params['const'],
            'half_life': self._calculate_half_life(residuals, hedge_ratio)
        }
        
    def johansen_test(self,
                       prices: pd.DataFrame,
                       det_order: int = 0) -> Dict:
        """
        Johansen 协整检验（多元）
        
        可以检测多个资产的协整关系
        
        Args:
            prices: 价格数据框
            det_order: 确定性阶数（0=无, 1=常数项, 2=趋势项）
            
        Returns:
            测试结果
        """
        from statsmodels.tsa.vector_ar.vecm import coint_johansen
        
        # 对齐数据
        aligned = prices.dropna()
        
        # 运行Johansen检验
        result = coint_johansen(
            aligned,
            det_order=det_order,
            k_ar_diff=1  # 一阶差分滞后
        )
        
        # 提取特征值
        eigenvalues = result[0]
        trace_stat = result[1]
        max_eigen_stat = result[2]
        
        # 临界值（5%）
        crit_values = result[3]
        cv_trace_5 = crit_values[2]  # Trace 统计量，5%水平
        cv_max_eigen_5 = crit_values[2]  # 最大特征值，5%水平
        
        # 判断协整数
        r_trace = sum(trace_stat > cv_trace_5)
        r_max_eigen = sum(max_eigen_stat > cv_max_eigen_5)
        
        return {
            'cointegration_rank_trace': r_trace,
            'cointegration_rank_max_eigen': r_max_eigen,
            'trace_statistic': trace_stat,
            'max_eigen_statistic': max_eigen_stat,
            'eigenvalues': eigenvalues,
            'cointegrated': r_trace > 0
        }
        
    def _calculate_half_life(self,
                            residuals: pd.Series,
                            hedge_ratio: float) -> float:
        """
        计算均值回归的半衰期
        
        半衰期 = -ln(2) / ln(θ)
        其中θ来自残差的自回归模型：ε_t = θ × ε_{t-1} + noise
        
        Args:
            residuals: 残差序列
            hedge_ratio: 对冲比率
            
        Returns:
            半衰期（天数）
        """
        # 对残差进行一阶自回归
        ar_model = sm.OLS(residuals[1:], sm.add_constant(residuals[:-1])).fit()
        theta = ar_model.params[0]
        
        # 计算半衰期
        if theta >= 1:
            return float('inf')  # 不均值回归
        else:
            half_life = -np.log(2) / np.log(theta)
            return max(0, half_life)

```

### 代码块 3

```python
class PairScreening:
    """配对筛选流程"""
    
    def __init__(self, config: Dict):
        self.pair_selector = PairSelector(
            min_correlation=config.get('min_correlation', 0.8),
            min_liquidity=config.get('min_liquidity', 1000000)
        )
        self.cointegration_tester = CointegrationTester(
            significance_level=config.get('significance_level', 0.05)
        )
        
    def screen_pairs(self,
                     prices: pd.DataFrame,
                     volumes: pd.DataFrame = None,
                     sector_filter: List[str] = None,
                     max_pairs: int = 100) -> pd.DataFrame:
        """
        筛选交易配对
        
        完整流程：
        1. 流动性过滤
        2. 相关性筛选
        3. 协整检验
        4. 排序和选择
        
        Args:
            prices: 价格数据
            volumes: 成交量数据
            sector_filter: 行业过滤（可选）
            max_pairs: 最大配对数量
            
        Returns:
            配对结果数据框
        """
        # 1. 流动性过滤
        if volumes is not None:
            avg_volumes = volumes.mean()
            liquid_stocks = avg_volumes[avg_volumes >= self.pair_selector.min_liquidity].index.tolist()
            prices_filtered = prices[liquid_stocks]
        else:
            prices_filtered = prices
            
        # 2. 相关性筛选
        correlated_pairs = self.pair_selector.find_highly_correlated_pairs(
            prices_filtered, volumes
        )
        
        print(f"Found {len(correlated_pairs)} highly correlated pairs")
        
        # 3. 协整检验
        cointegrated_pairs = []
        
        for stock1, stock2, correlation in correlated_pairs[:max_pairs]:
            # Engle-Granger检验
            eg_result = self.cointegration_tester.engle_granger_test(
                prices_filtered[stock1],
                prices_filtered[stock2]
            )
            
            if eg_result['cointegrated']:
                cointegrated_pairs.append({
                    'stock1': stock1,
                    'stock2': stock2,
                    'correlation': correlation,
                    'hedge_ratio': eg_result['hedge_ratio'],
                    'p_value': eg_result['p_value'],
                    'half_life': eg_result['half_life'],
                    'test_statistic': eg_result['test_statistic']
                })
                
        print(f"Cointegrated pairs: {len(cointegrated_pairs)}/{len(correlated_pairs)}")
        
        # 4. 转换为数据框
        pairs_df = pd.DataFrame(cointegrated_pairs)
        
        # 5. 排序（按P值）
        if not pairs_df.empty:
            pairs_df = pairs_df.sort_values('p_value')
            
        return pairs_df

```

### 代码块 4

```python
class SpreadCalculator:
    """价差计算器"""
    
    def __init__(self):
        self.spread_history = {}
        
    def calculate_hedge_ratio_spread(self,
                                     price1: pd.Series,
                                     price2: pd.Series,
                                     hedge_ratio: float) -> pd.Series:
        """
        计算基于对冲比率的价差
        
        Spread = Price1 - Hedge_Ratio × Price2
        
        Args:
            price1: 股票1价格序列
            price2: 股票2价格序列
            hedge_ratio: 对冲比率
            
        Returns:
            价差序列
        """
        # 对齐数据
        aligned = pd.DataFrame({
            'price1': price1,
            'price2': price2
        }).dropna()
        
        spread = aligned['price1'] - hedge_ratio * aligned['price2']
        
        return spread
        
    def calculate_ratio_adjusted_spread(self,
                                        price1: pd.Series,
                                        price2: pd.Series,
                                        method: str = 'ols') -> pd.Series:
        """
        计算比率调整后的价差
        
        可以选择不同的比率计算方法：
        - OLS: 普通最小二乘回归
        - TS: 偏向序列回归
        - Price: 价格比率
        
        Args:
            price1: 股票1价格序列
            price2: 股票2价格序列
            method: 比率计算方法
            
        Returns:
            价差序列和比率
        """
        # 对齐数据
        aligned = pd.DataFrame({
            'price1': price1,
            'price2': price2
        }).dropna()
        
        if method == 'ols':
            # OLS回归：Price1 = α + β × Price2
            X = sm.add_constant(aligned['price2'])
            y = aligned['price1']
            model = sm.OLS(y, X).fit()
            
            hedge_ratio = model.params['price2']
            intercept = model.params['const']
            spread = y - hedge_ratio * aligned['price2']
            
        elif method == 'ts':
            # 偏向序列回归
            X = aligned['price2']
            y = aligned['price1']
            model = sm.OLS(y, X).fit()
            
            hedge_ratio = model.params['price2']
            spread = y - hedge_ratio * aligned['price2']
            intercept = 0
            
        elif method == 'price':
            # 价格比率
            price_ratio = aligned['price1'] / aligned['price2']
            hedge_ratio = price_ratio.mean()
            spread = aligned['price1'] - hedge_ratio * aligned['price2']
            intercept = 0
            
        else:
            raise ValueError(f"Unknown method: {method}")
            
        return spread, hedge_ratio, intercept
        
    def normalize_spread(self,
                          spread: pd.Series,
                          window: int = 252) -> pd.Series:
        """
        标准化价差
        
        Z-Score = (Spread - Mean(Spread)) / Std(Spread)
        
        Args:
            spread: 价差序列
            window: 滚动窗口（None = 全部历史）
            
        Returns:
            Z-score 序列
        """
        if window is not None:
            mean_spread = spread.rolling(window).mean()
            std_spread = spread.rolling(window).std()
        else:
            mean_spread = spread.mean()
            std_spread = spread.std()
            
        z_score = (spread - mean_spread) / std_spread
        
        return z_score

```

### 代码块 5

```python
class ZScoreSignalGenerator:
    """Z-score信号生成器"""
    
    def __init__(self,
                 entry_threshold: float = 2.0,    # 入场阈值
                 exit_threshold: float = 0.0,      # 出场阈值
                 add_position_threshold: float = 3.0): # 加仓阈值
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.add_threshold = add_position_threshold
        
    def generate_signals(self,
                          z_scores: pd.Series) -> pd.Series:
        """
        生成交易信号
        
        信号定义：
        +1: 做多价差（买入股票1，卖出股票2）
        -1: 做空价差（卖出股票1，买入股票2）
        0: 平仓
        
        Args:
            z_scores: Z-score序列
            
        Returns:
            信号序列
        """
        signals = pd.Series(0, index=z_scores.index)
        
        for i in range(len(z_scores)):
            z = z_scores.iloc[i]
            
            # 做多价差：Z-score < -2（价差被低估）
            if z <= -self.entry_threshold:
                signals.iloc[i] = 1
                
            # 做空价差：Z-score > 2（价差被高估）
            elif z >= self.entry_threshold:
                signals.iloc[i] = -1
                
            # 出场：Z-score 回归到 0
            elif abs(z) <= self.exit_threshold:
                signals.iloc[i] = 0
                
            # 加仓：Z-score 进一步偏离
            else:
                # 如果当前有仓位，且Z-score偏离加大，可以加仓
                if i > 0 and signals.iloc[i-1] != 0:
                    if (signals.iloc[i-1] == 1 and z <= -self.add_threshold):
                        signals.iloc[i] = 2  # 加仓做多
                    elif (signals.iloc[i-1] == -1 and z >= self.add_threshold):
                        signals.iloc[i] = -2  # 加仓做空
                    else:
                        signals.iloc[i] = signals.iloc[i-1]
                        
        return signals
        
    def calculate_position_size(self,
                              signal: float,
                              base_size: float = 10000) -> float:
        """
        计算仓位大小
        
        Args:
            signal: 信号值（1=标准仓位，2=双倍仓位）
            base_size: 基础仓位金额
            
        Returns:
            实际仓位金额
        """
        if abs(signal) <= 1:
            return base_size
        else:
            return base_size * abs(signal)

```

### 代码块 6

```python
class TradingRules:
    """交易规则"""
    
    def __init__(self,
                 entry_z_score: float = 2.0,
                 add_position_z_score: float = 3.0,
                 exit_z_score: float = 0.5,
                 stop_loss_z_score: float = 4.0,
                 max_holding_days: int = 30):
        self.entry_z = entry_z_score
        self.add_z = add_position_z_score
        self.exit_z = exit_z_score
        self.stop_z = stop_loss_z_score
        self.max_holding_days = max_holding_days
        
    def should_enter_long(self, z_score: float) -> bool:
        """判断是否做多价差"""
        return z_score <= -self.entry_z
        
    def should_enter_short(self, z_score: float) -> bool:
        """判断是否做空价差"""
        return z_score >= self.entry_z
        
    def should_add_long(self, z_score: float, current_position: int) -> bool:
        """判断是否加仓做多"""
        return current_position > 0 and z_score <= -self.add_z
        
    def should_add_short(self, z_score: float, current_position: int) -> bool:
        """判断是否加仓做空"""
        return current_position < 0 and z_score >= self.add_z
        
    def should_exit_long(self, z_score: float) -> bool:
        """判断是否平多仓"""
        return z_score >= self.exit_z
        
    def should_exit_short(self, z_score: float) -> bool:
        """判断是否平空仓"""
        return z_score <= -self.exit_z
        
    def should_stop_loss(self, z_score: float) -> bool:
        """判断是否止损"""
        return abs(z_score) >= self.stop_z
        
    def should_time_exit(self, holding_days: int) -> bool:
        """判断是否时间止损"""
        return holding_days >= self.max_holding_days

```

### 代码块 7

```python
class HedgeRatioCalculator:
    """对冲比率计算器"""
    
    @staticmethod
    def ols_hedge_ratio(price1: pd.Series,
                          price2: pd.Series) -> float:
        """
        OLS回归计算对冲比率
        
        Hedge Ratio = Cov(Price1, Price2) / Var(Price2)
        或者直接回归：Price1 = α + β × Price2
        
        Args:
            price1: 股票1价格
            price2: 股票2价格
            
        Returns:
            对冲比率
        """
        # 对齐数据
        aligned = pd.DataFrame({
            'price1': price1,
            'price2': price2
        }).dropna()
        
        # 方法1：回归
        X = sm.add_constant(aligned['price2'])
        y = aligned['price1']
        model = sm.OLS(y, X).fit()
        hedge_ratio = model.params['price2']
        
        return hedge_ratio
        
    @staticmethod
    def rolling_hedge_ratio(price1: pd.Series,
                              price2: pd.Series,
                              window: int = 60) -> pd.Series:
        """
        滚动对冲比率
        
        Args:
            price1: 股票1价格
            price2: 股票2价格
            window: 滚动窗口
            
        Returns:
            对冲比率序列
        """
        hedge_ratios = pd.Series(index=price1.index, dtype=float)
        
        for i in range(window, len(price1)):
            window_price1 = price1.iloc[i-window:i]
            window_price2 = price2.iloc[i-window:i]
            
            hedge_ratio = HedgeRatioCalculator.ols_hedge_ratio(
                window_price1,
                window_price2
            )
            
            hedge_ratios.iloc[i] = hedge_ratio
            
        # 填充初始值
        hedge_ratios.iloc[:window] = hedge_ratios.iloc[window]
        
        return hedge_ratios
        
    @staticmethod
    def calculate_position_sizes(capital: float,
                               spread_value: float,
                               price1: float,
                               price2: float,
                               hedge_ratio: float) -> Tuple[int, int]:
        """
        计算交易数量
        
        目标：投资组合资本按价值分配
        
        Args:
            capital: 总资本
            spread_value: 价差价值（每单位价差）
            price1: 股票1价格
            price2: 股票2价格
            hedge_ratio: 对冲比率
            
        Returns:
            (shares1, shares2)
        """
        # 分配一半资本做多，一半做空
        long_capital = capital / 2
        short_capital = capital / 2
        
        # 计算股数
        shares1 = long_capital / price1
        shares2 = short_capital / price2
        
        # 调整为整数股
        shares1 = int(shares1)
        shares2 = int(shares2)
        
        return shares1, shares2

```

### 代码块 8

```python
class MeanReversionSpeed:
    """均值回归速度分析"""
    
    def __init__(self):
        self.half_life_history = {}
        
    def calculate_half_life(self,
                          spread: pd.Series) -> float:
        """
        计算均值回归的半衰期
        
        使用AR(1)模型：Spread_t = α + θ × Spread_{t-1} + ε_t
        
        半衰期 = -ln(2) / ln(θ)
        
        Args:
            spread: 价差序列
            
        Returns:
            半衰期（天数）
        """
        # 去除趋势
        spread_detrended = spread - spread.rolling(len(spread)//10).mean()
        
        # AR(1)回归
        ar_model = sm.OLS(spread_detrended[1:], 
                         sm.add_constant(spread_detrended[:-1])).fit()
        
        theta = ar_model.params[0]
        
        # 计算半衰期
        if theta >= 1 or theta <= 0:
            return float('inf')
        else:
            half_life = -np.log(2) / np.log(theta)
            return max(0, half_life)
            
    def calculate_ornstein_uhlenbeck_params(self,
                                          spread: pd.Series) -> Dict:
        """
        计算Ornstein-Uhlenbeck过程参数
        
        dX_t = κ(μ - X_t)dt + σdW_t
        
        其中：
        - κ: 均值回归速度
        - μ: 长期均值
        - σ: 波动率
        
        Args:
            spread: 价差序列
            
        Returns:
            OU参数字典
        """
        # 计算收益
        returns = spread.diff().dropna()
        
        # 离散时间OU过程的参数估计
        # X_t = μ + (X_{t-1} - μ) × (1 - θ) + ε_t
        # 其中 θ = κ × dt
        
        mean_spread = spread.mean()
        
        # 回归：Spread_t - μ = (1 - θ)(Spread_{t-1} - μ) + ε_t
        y = spread[1:] - mean_spread
        X = sm.add_constant(spread[:-1] - mean_spread)
        
        model = sm.OLS(y, X).fit()
        
        theta = 1 - model.params[0]  # θ = κ × dt
        kappa = theta  # 假设dt=1
        sigma = np.std(model.resid)
        
        return {
            'kappa': kappa,
            'mu': mean_spread,
            'sigma': sigma,
            'half_life': -np.log(2) / kappa if kappa > 0 else float('inf')
        }
        
    def analyze_mean_reversion_speed(self,
                                     spreads: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        分析多个配对的均值回归速度
        
        Args:
            spreads: 价差字典 {pair_name: spread_series}
            
        Returns:
            分析结果
        """
        results = []
        
        for pair_name, spread in spreads.items():
            # 计算半衰期
            half_life = self.calculate_half_life(spread)
            
            # 计算OU参数
            ou_params = self.calculate_ornstein_uhlenbeck_params(spread)
            
            results.append({
                'pair': pair_name,
                'half_life': half_life,
                'kappa': ou_params['kappa'],
                'mu': ou_params['mu'],
                'sigma': ou_params['sigma'],
                'daily_reversion': 1 / half_life if half_life != float('inf') else 0
            })
            
        return pd.DataFrame(results)

```

### 代码块 9

```python
class RegimeDetector:
    """制度变化检测"""
    
    def __init__(self,
                 window: int = 60,
                 threshold: float = 2.0):
        self.window = window
        self.threshold = threshold
        
    def detect_cointegration_breakdown(self,
                                     price1: pd.Series,
                                     price2: pd.Series,
                                     initial_hedge_ratio: float) -> Dict:
        """
        检测协整关系是否失效
        
        方法：
        1. 计算滚动对冲比率
        2. 检测对冲比率的显著偏离
        3. 检测价差的平稳性失效
        
        Args:
            price1: 股票1价格
            price2: 股票2价格
            initial_hedge_ratio: 初始对冲比率
            
        Returns:
            检测结果
        """
        # 计算滚动对冲比率
        rolling_hedge_ratio = HedgeRatioCalculator.rolling_hedge_ratio(
            price1, price2, self.window
        )
        
        # 计算价差
        spread = price1 - initial_hedge_ratio * price2
        
        # 检测对冲比率偏离
        hedge_ratio_deviation = abs(rolling_hedge_ratio - initial_hedge_ratio)
        hedge_ratio_z = (hedge_ratio_deviation - hedge_ratio_deviation.mean()) / \
                        hedge_ratio_deviation.std()
        
        # 检测价差ADF检验失效
        recent_adf_p = []
        for i in range(self.window, len(spread) - self.window):
            window_spread = spread.iloc[i-self.window:i]
            adf_result = adfuller(window_spread)
            recent_adf_p.append(adf_result[1])
            
        # 判断制度变化
        hedge_ratio_breakdown = abs(hedge_ratio_z.iloc[-1]) > self.threshold
        cointegration_breakdown = np.mean(recent_adf_p[-20:]) > 0.1  # P值增大
        
        return {
            'regime_change': hedge_ratio_breakdown or cointegration_breakdown,
            'hedge_ratio_breakdown': hedge_ratio_breakdown,
            'cointegration_breakdown': cointegration_breakdown,
            'current_hedge_ratio': rolling_hedge_ratio.iloc[-1],
            'initial_hedge_ratio': initial_hedge_ratio,
            'hedge_ratio_z': hedge_ratio_z.iloc[-1]
        }
        
    def detect_structural_break(self,
                                spread: pd.Series,
                                method: str = 'cusum') -> Dict:
        """
        检测结构性断点
        
        Args:
            spread: 价差序列
            method: 检测方法 ('cusum', 'chow')
            
        Returns:
            断点检测结果
        """
        if method == 'cusum':
            return self._cusum_test(spread)
        elif method == 'chow':
            return self._chow_test(spread)
        else:
            raise ValueError(f"Unknown method: {method}")
            
    def _cusum_test(self, spread: pd.Series) -> Dict:
        """CUSUM结构性断点检验"""
        spread_mean = spread.mean()
        spread_std = spread.std()
        
        # CUSUM统计量
        cusum_pos = []
        cusum_neg = []
        
        cumulative_deviation = 0
        for value in spread:
            deviation = value - spread_mean
            cumulative_deviation += deviation
            cusum_pos.append(max(0, cumulative_deviation))
            cusum_neg.append(min(0, cumulative_deviation))
            
        # 检测断点（CUSUM超过阈值）
        threshold = 5 * spread_std  # 5倍标准差
        
        cusum_pos = pd.Series(cusum_pos, index=spread.index)
        cusum_neg = pd.Series(cusum_neg, index=spread.index)
        
        pos_breaks = cusum_pos[cusum_pos > threshold].index
        neg_breaks = cusum_neg[cusum_neg < -threshold].index
        
        return {
            'positive_breaks': list(pos_breaks),
            'negative_breaks': list(neg_breaks),
            'max_cusum_pos': cusum_pos.max(),
            'max_cusum_neg': cusum_neg.min()
        }

```

### 代码块 10

```python
class MultiPairPortfolio:
    """多配对投资组合"""
    
    def __init__(self,
                 capital: float = 1000000,      # 总资本
                 max_pairs: int = 20,            # 最大配对数量
                 max_pair_capital: float = 0.05):  # 单一配对最大资本占比
        self.capital = capital
        self.max_pairs = max_pairs
        self.max_pair_capital = max_pair_capital
        
        self.active_pairs = {}
        self.pair_weights = {}
        
    def allocate_capital(self,
                          pair_scores: pd.DataFrame,
                          total_capital: float = None) -> Dict[str, float]:
        """
        分配资本到各配对
        
        分配方法：
        1. 基于配对质量（P值、半衰期）
        2. 限制单一配对最大资本
        3. 限制总配对数量
        
        Args:
            pair_scores: 配对得分数据框
            total_capital: 总资本
            
        Returns:
            配对资本分配
        """
        if total_capital is None:
            total_capital = self.capital
            
        # 计算配对得分
        # 得分 = (1 - P值) × exp(-半衰期/30)
        pair_scores['score'] = (
            (1 - pair_scores['p_value']) *
            np.exp(-pair_scores['half_life'] / 30)
        )
        
        # 归一化得分
        pair_scores['normalized_score'] = \
            pair_scores['score'] / pair_scores['score'].sum()
        
        # 初始分配
        initial_allocation = pair_scores['normalized_score'] * total_capital
        
        # 限制单一配对最大资本
        max_pair_cap = total_capital * self.max_pair_capital
        pair_scores['allocation'] = initial_allocation.clip(upper=max_pair_cap)
        
        # 归一化到总资本
        total_allocated = pair_scores['allocation'].sum()
        pair_scores['allocation'] = pair_scores['allocation'] / total_allocated * total_capital
        
        # 选择前N个配对
        pair_scores = pair_scores.sort_values('score', ascending=False)
        top_pairs = pair_scores.head(self.max_pairs)
        
        # 归一化选择配对的资本
        total_top_allocation = top_pairs['allocation'].sum()
        top_pairs['final_allocation'] = top_pairs['allocation'] / total_top_allocation * total_capital
        
        # 转换为字典
        capital_allocation = {}
        for idx, row in top_pairs.iterrows():
            pair_key = f"{row['stock1']}_{row['stock2']}"
            capital_allocation[pair_key] = row['final_allocation']
            
        return capital_allocation, top_pairs
        
    def calculate_portfolio_returns(self,
                                  pair_positions: Dict,
                                  price_changes: Dict) -> pd.Series:
        """
        计算投资组合收益
        
        Args:
            pair_positions: 配对仓位 {
                'pair1': {
                    'stock1': shares1,
                    'stock2': shares2,
                    'direction': 1 or -1
                }
            }
            price_changes: 价格变化 {
                'stock1': price_change1,
                'stock2': price_change2
            }
            
        Returns:
            投资组合收益序列
        """
        # 为每个配对计算收益
        pair_returns = {}
        
        for pair_name, position in pair_positions.items():
            stock1 = position['stock1']
            stock2 = position['stock2']
            direction = position['direction']
            
            if stock1 not in price_changes or stock2 not in price_changes:
                continue
                
            # 配对收益
            pair_return = direction * (
                price_changes[stock1] * stock1 -
                price_changes[stock2] * stock2
            )
            
            pair_returns[pair_name] = pair_return
            
        # 投资组合收益 = 各配对收益之和
        portfolio_returns = pd.DataFrame(pair_returns).sum(axis=1)
        
        return portfolio_returns

```

### 代码块 11

```python
class PairsTradingBacktest:
    """配对交易回测系统"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 配置字典 {
                'capital': 总资本,
                'max_pairs': 最大配对数,
                'entry_z': 入场Z-score,
                'exit_z': 出场Z-score,
                ...
            }
        """
        # 初始化各个模块
        self.pair_screening = PairScreening(config)
        self.spread_calculator = SpreadCalculator()
        self.signal_generator = ZScoreSignalGenerator(
            entry_threshold=config.get('entry_z', 2.0),
            exit_threshold=config.get('exit_z', 0.5)
        )
        self.trading_rules = TradingRules(
            entry_z_score=config.get('entry_z', 2.0),
            exit_z_score=config.get('exit_z', 0.5),
            stop_loss_z_score=config.get('stop_loss_z', 4.0)
        )
        self.portfolio = MultiPairPortfolio(
            capital=config.get('capital', 1000000),
            max_pairs=config.get('max_pairs', 20)
        )
        self.regime_detector = RegimeDetector()
        
        # 存储状态
        self.pair_positions = {}
        self.spread_history = {}
        
    def run_backtest(self,
                      prices: pd.DataFrame,
                      volumes: pd.DataFrame,
                      start_date: str,
                      end_date: str) -> Dict:
        """
        运行完整回测
        
        Args:
            prices: 价格数据
            volumes: 成交量数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        # 1. 筛选配对
        print("Step 1: Screening pairs...")
        pairs_df = self.pair_screening.screen_pairs(
            prices[start_date:end_date],
            volumes[start_date:end_date]
        )
        
        if pairs_df.empty:
            return {'error': 'No valid pairs found'}
            
        print(f"Selected {len(pairs_df)} cointegrated pairs")
        
        # 2. 分配资本
        print("Step 2: Allocating capital...")
        capital_allocation, selected_pairs = self.portfolio.allocate_capital(
            pairs_df
        )
        
        # 3. 初始化价差计算
        print("Step 3: Initializing spreads...")
        for idx, row in selected_pairs.iterrows():
            pair_key = f"{row['stock1']}_{row['stock2']}"
            
            spread, hedge_ratio, _ = self.spread_calculator.calculate_ratio_adjusted_spread(
                prices[row['stock1']],
                prices[row['stock2']],
                method='ols'
            )
            
            self.spread_history[pair_key] = {
                'spread': spread,
                'hedge_ratio': hedge_ratio,
                'z_score': self.spread_calculator.normalize_spread(spread)
            }
            
        # 4. 运行回测
        print("Step 4: Running backtest...")
        dates = pd.date_range(start_date, end_date, freq='D')
        
        results = {
            'dates': [],
            'returns': [],
            'positions': []
        }
        
        for i, date in enumerate(dates):
            if i < 252:  # 需要1年数据初始化
                results['dates'].append(date)
                results['returns'].append(0)
                results['positions'].append({})
                continue
                
            # 更新价差和Z-score
            current_spreads = {}
            for pair_key in self.spread_history:
                pair_data = self.spread_history[pair_key]
                spread = pair_data['spread'].iloc[:i].iloc[-1]
                z_score = pair_data['z_score'].iloc[:i].iloc[-1]
                
                current_spreads[pair_key] = {
                    'spread': spread,
                    'z_score': z_score
                }
                
            # 生成交易信号
            current_positions = {}
            
            for pair_key, spread_data in current_spreads.items():
                z = spread_data['z_score']
                
                # 交易逻辑
                if self.trading_rules.should_enter_long(z):
                    current_positions[pair_key] = {
                        'direction': 1,  # 做多价差
                        'entry_date': date
                    }
                elif self.trading_rules.should_enter_short(z):
                    current_positions[pair_key] = {
                        'direction': -1,  # 做空价差
                        'entry_date': date
                    }
                    
            results['dates'].append(date)
            results['positions'].append(current_positions)
            
            # 计算当日收益
            if i > 0:
                daily_return = self._calculate_daily_return(
                    current_positions,
                    prices.iloc[i-1:i+1]
                )
                results['returns'].append(daily_return)
            else:
                results['returns'].append(0)
                
        # 5. 计算绩效指标
        print("Step 5: Calculating performance metrics...")
        returns_series = pd.Series(results['returns'], index=results['dates'])
        performance = self._calculate_performance(returns_series)
        
        return {
            'pairs_selected': selected_pairs,
            'capital_allocation': capital_allocation,
            'returns_df': pd.DataFrame({
                'date': results['dates'],
                'return': results['returns']
            }),
            'performance': performance,
            'positions_history': results['positions']
        }
        
    def _calculate_daily_return(self,
                                 positions: Dict,
                                 prices: pd.DataFrame) -> float:
        """计算当日收益"""
        total_return = 0.0
        
        for pair_key, position in positions.items():
            if 'direction' not in position:
                continue
                
            # 解析配对名称
            stock1, stock2 = pair_key.split('_')
            
            if stock1 not in prices or stock2 not in prices:
                continue
                
            # 计算价格变化
            price_change1 = (prices[stock1].iloc[-1] - prices[stock1].iloc[0]) / prices[stock1].iloc[0]
            price_change2 = (prices[stock2].iloc[-1] - prices[stock2].iloc[0]) / prices[stock2].iloc[0]
            
            # 配对收益
            pair_return = position['direction'] * (price_change1 - price_change2)
            
            total_return += pair_return
            
        return total_return
        
    def _calculate_performance(self, returns: pd.Series) -> Dict:
        """计算绩效指标"""
        # 基础指标
        total_return = (1 + returns).prod() - 1
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 胜率
        win_rate = (returns > 0).mean()
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }

```

### 代码块 12

```python
PAIRS_TRADING_CONFIG = {
    # 配对筛选
    'min_correlation': 0.8,              # 最小相关性
    'min_correlation_period': 252,         # 相关性窗口
    'min_liquidity': 1000000,            # 最小成交量
    'significance_level': 0.05,           # 协整显著性水平
    
    # 交易规则
    'entry_z_score': 2.0,                # 入场Z-score
    'add_position_z_score': 3.0,          # 加仓Z-score
    'exit_z_score': 0.5,                 # 出场Z-score
    'stop_loss_z_score': 4.0,             # 止损Z-score
    'max_holding_days': 30,               # 最大持仓天数
    
    # 投资组合
    'capital': 1000000,                    # 总资本
    'max_pairs': 20,                       # 最大配对数
    'max_pair_capital': 0.05,             # 单一配对最大资本占比
    
    # 制度检测
    'regime_detection_window': 60,          # 制度检测窗口
    'regime_change_threshold': 2.0,       # 制度变化阈值
}

```

### 代码块 13

```python
PAIRS_TRADING_TARGETS = {
    # Alpha
    'target_annual_return': 0.10,         # 目标年化收益 10%
    'target_sharpe': 1.5,                 # 目标夏普比率 1.5
    
    # 风险
    'max_drawdown': 0.15,                  # 最大回撤 15%
    'max_volatility': 0.12,                # 最大波动率 12%
    
    # 交易效率
    'min_win_rate': 0.55,                 # 最小胜率 55%
    'max_holding_days': 20,                 # 最大持仓天数 20
    
    # 配对质量
    'min_cointegration_p_value': 0.01,      # 协整P值阈值
    'max_half_life': 15,                    # 最大半衰期 15天
}

```

