# AQR 因子模型构建器

You are a senior researcher at AQR Capital Management who builds multi-factor models used to construct portfolios that systematically harvest risk premiums across global markets.

I need a complete factor model for portfolio construction.

Build:

- Factor selection: which factors to include (value, momentum, quality, size, low volatility) with evidence
- Factor definition: exact calculation formula for each factor using available financial data
- Factor portfolio construction: how to build long-short portfolios for each individual factor
- Factor exposure measurement: how to calculate my current portfolio's exposure to each factor
- Factor correlation matrix: how factors move relative to each other and diversification benefits
- Multi-factor combination: how to weight and blend factors into a single composite score
- Rebalancing methodology: when to rebalance factor portfolios and how to minimize turnover
- Factor timing analysis: can we increase exposure to factors when conditions favor them
- Performance attribution: decompose returns into factor contributions and stock-specific alpha
- Complete Python implementation with data loading, factor calculation, and portfolio construction

Format as an AQR-style factor research paper with mathematical definitions, empirical results framework, and production-ready code.

My investment universe: [DESCRIBE YOUR MARKET (US STOCKS, GLOBAL, ETFs), CAPITAL SIZE, REBALANCING FREQUENCY, AND FACTOR PREFERENCES]

---

## 使用说明

这是一个 AQR 风格的多因子模型构建框架，用于系统化地捕获风险溢价。

### 使用方法

将 `[DESCRIBE YOUR MARKET (US STOCKS, GLOBAL, ETFs), CAPITAL SIZE, REBALANCING FREQUENCY, AND FACTOR PREFERENCES]` 替换为你的具体情况，例如：

```
My investment universe: US large-cap stocks ($10B+), $100M capital, monthly rebalancing, interested in value, momentum, quality, and low volatility factors.
```

### 适用场景

- 构建多因子投资组合
- 评估投资组合的因子暴露
- 因子绩效归因
- 因子择时策略

---

## 因子选择与定义

### 1. 价值因子 (Value Factor)

```python
import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FactorDefinition:
    """因子定义"""
    name: str
    description: str
    formula: str
    data_requirements: List[str]
    expected_premium: float  # 预期风险溢价（年化）

class ValueFactor:
    """价值因子"""
    
    def __init__(self):
        self.definition = FactorDefinition(
            name='Value',
            description='估值低的公司预期收益更高',
            formula='Book-to-Market, Earnings-to-Price, CF-to-Price',
            data_requirements=['book_value', 'earnings', 'cash_flow', 'market_cap'],
            expected_premium=0.04  # 4% 年化溢价
        )
        
    def calculate_btm(self,
                       book_value: pd.Series,
                       market_cap: pd.Series) -> pd.Series:
        """
        计算账面市值比 (Book-to-Market)
        
        BtM = Book Value / Market Cap
        """
        return book_value / market_cap
        
    def calculate_earnings_yield(self,
                                earnings: pd.Series,
                                market_cap: pd.Series) -> pd.Series:
        """
        计算收益市盈率倒数 (Earnings Yield)
        
        Earnings Yield = Earnings / Market Cap = 1 / PE
        """
        return earnings / market_cap
        
    def calculate_cf_yield(self,
                          cash_flow: pd.Series,
                          market_cap: pd.Series) -> pd.Series:
        """
        计算现金流收益率 (Cash Flow Yield)
        
        CF Yield = Cash Flow / Market Cap
        """
        return cash_flow / market_cap
        
    def calculate_composite_value(self,
                                  btm: pd.Series,
                                  earnings_yield: pd.Series,
                                  cf_yield: pd.Series) -> pd.Series:
        """
        计算复合价值因子
        
        步骤：
        1. 标准化每个子因子
        2. 等权重组合
        """
        # 标准化（Z-score）
        btm_z = (btm - btm.mean()) / btm.std()
        ey_z = (earnings_yield - earnings_yield.mean()) / earnings_yield.std()
        cfy_z = (cf_yield - cf_yield.mean()) / cf_yield.std()
        
        # 等权重组合
        composite = (btm_z + ey_z + cfy_z) / 3
        
        return composite
```

### 2. 动量因子 (Momentum Factor)

```python
class MomentumFactor:
    """动量因子"""
    
    def __init__(self,
                 lookback_1m: int = 20,    # 1 个月动量
                 lookback_12m: int = 252):  # 12 个月动量
        self.lookback_1m = lookback_1m
        self.lookback_12m = lookback_12m
        
        self.definition = FactorDefinition(
            name='Momentum',
            description='过去表现好的股票未来预期收益更高',
            formula='12-month cumulative return, excluding most recent 1 month',
            data_requirements=['daily_returns'],
            expected_premium=0.06  # 6% 年化溢价
        )
        
    def calculate_momentum(self,
                           prices: pd.DataFrame,
                           exclude_recent: bool = True) -> pd.Series:
        """
        计算动量
        
        标准公式：12个月累积收益率，排除最近1个月
        
        1. 计算12个月累积收益
        2. 排除最近1个月（避免短期反转）
        
        Args:
            prices: 价格序列
            exclude_recent: 是否排除最近1个月
            
        Returns:
            动量因子
        """
        # 计算12个月累积收益
        returns_12m = prices.pct_change(self.lookback_12m)
        
        # 排除最近1个月（如需要）
        if exclude_recent:
            returns_excl_1m = prices.pct_change(self.lookback_12m) / \
                              prices.pct_change(self.lookback_1m)
            momentum = returns_excl_1m
        else:
            momentum = returns_12m
            
        # 标准化
        momentum_z = (momentum - momentum.mean()) / momentum.std()
        
        return momentum_z
        
    def calculate_momentum_reversal(self,
                                      prices: pd.DataFrame) -> pd.Series:
        """
        计算动量反转（短期动量因子）
        
        短期（1个月）动量反转：过去表现差的股票未来可能反弹
        """
        # 计算1个月收益
        returns_1m = prices.pct_change(self.lookback_1m)
        
        # 反转因子 = -1 × 短期动量
        reversal = -returns_1m
        
        # 标准化
        reversal_z = (reversal - reversal.mean()) / reversal.std()
        
        return reversal_z
```

### 3. 质量因子 (Quality Factor)

```python
class QualityFactor:
    """质量因子"""
    
    def __init__(self):
        self.definition = FactorDefinition(
            name='Quality',
            description='财务质量高的公司预期收益更高',
            formula='ROE, ROA, profit margin, debt-to-equity, earnings stability',
            data_requirements=[
                'net_income', 'shareholders_equity', 'total_assets',
                'revenue', 'total_debt', 'earnings_history'
            ],
            expected_premium=0.03  # 3% 年化溢价
        )
        
    def calculate_roe(self,
                       net_income: pd.Series,
                       equity: pd.Series) -> pd.Series:
        """
        计算净资产收益率 (ROE)
        
        ROE = Net Income / Shareholders Equity
        """
        return net_income / equity
        
    def calculate_roa(self,
                       net_income: pd.Series,
                       total_assets: pd.Series) -> pd.Series:
        """
        计算总资产收益率 (ROA)
        
        ROA = Net Income / Total Assets
        """
        return net_income / total_assets
        
    def calculate_profit_margin(self,
                               net_income: pd.Series,
                               revenue: pd.Series) -> pd.Series:
        """
        计算利润率 (Profit Margin)
        
        Profit Margin = Net Income / Revenue
        """
        return net_income / revenue
        
    def calculate_debt_to_equity(self,
                                   total_debt: pd.Series,
                                   equity: pd.Series) -> pd.Series:
        """
        计算债务股权比 (Debt-to-Equity)
        
        D/E = Total Debt / Shareholders Equity
        
        注意：低D/E是高质量
        """
        return total_debt / equity
        
    def calculate_earnings_stability(self,
                                     earnings_history: pd.DataFrame) -> pd.Series:
        """
        计算收益稳定性 (Earnings Stability)
        
        稳定性 = 1 - 收益的变异系数
        
        变异系数 CV = Std(Mean) / Mean
        """
        earnings_mean = earnings_history.mean()
        earnings_std = earnings_history.std()
        
        cv = earnings_std / earnings_mean
        stability = 1 - cv
        
        return stability
        
    def calculate_composite_quality(self,
                                    roe: pd.Series,
                                    roa: pd.Series,
                                    profit_margin: pd.Series,
                                    debt_to_equity: pd.Series,
                                    earnings_stability: pd.Series) -> pd.Series:
        """
        计算复合质量因子
        """
        # 标准化
        roe_z = (roe - roe.mean()) / roe.std()
        roa_z = (roa - roa.mean()) / roa.std()
        pm_z = (profit_margin - profit_margin.mean()) / profit_margin.std()
        de_z = (-debt_to_equity - (-debt_to_equity).mean()) / (-debt_to_equity).std()  # 低D/E是高质量
        es_z = (earnings_stability - earnings_stability.mean()) / earnings_stability.std()
        
        # 等权重组合
        composite = (roe_z + roa_z + pm_z + de_z + es_z) / 5
        
        return composite
```

### 4. 规模因子 (Size Factor)

```python
class SizeFactor:
    """规模因子"""
    
    def __init__(self):
        self.definition = FactorDefinition(
            name='Size',
            description='小盘股预期收益高于大盘股',
            formula='Market Capitalization (log)',
            data_requirements=['market_cap'],
            expected_premium=0.02  # 2% 年化溢价
        )
        
    def calculate_size(self,
                       market_cap: pd.Series) -> pd.Series:
        """
        计算规模因子
        
        Size = -log(Market Cap)
        
        负号：小市值 = 高因子值
        """
        size = -np.log(market_cap)
        
        # 标准化
        size_z = (size - size.mean()) / size.std()
        
        return size_z
        
    def calculate_size_decile(self,
                             market_cap: pd.Series) -> pd.Series:
        """
        计算规模十分位
        
        Returns:
            1-10，1 = 最小市值，10 = 最大市值
        """
        decile = market_cap.rank(pct=True) * 10
        decile = np.ceil(decile)
        decile = 11 - decile  # 反转，使1=最小市值
        
        return decile
```

### 5. 低波动因子 (Low Volatility Factor)

```python
class LowVolatilityFactor:
    """低波动因子"""
    
    def __init__(self,
                 lookback: int = 252):
        self.lookback = lookback
        
        self.definition = FactorDefinition(
            name='Low Volatility',
            description='低波动股票经风险调整后收益更高',
            formula='Historical volatility, downside deviation, beta',
            data_requirements=['daily_returns', 'market_returns'],
            expected_premium=0.02  # 2% 年化溢价（风险调整后）
        )
        
    def calculate_volatility(self,
                            returns: pd.Series) -> pd.Series:
        """
        计算历史波动率
        
        Vol = Std(Daily Returns) * sqrt(252)
        """
        volatility = returns.rolling(self.lookback).std() * np.sqrt(252)
        
        # 标准化（负号：低波动 = 高因子值）
        vol_z = -(volatility - volatility.mean()) / volatility.std()
        
        return vol_z
        
    def calculate_downside_deviation(self,
                                    returns: pd.Series) -> pd.Series:
        """
        计算下行偏差 (Downside Deviation)
        
        只计算负收益的标准差
        """
        downside_returns = returns.where(returns < 0, 0)
        downside_dev = downside_returns.rolling(self.lookback).std() * np.sqrt(252)
        
        # 标准化（负号）
        dd_z = -(downside_dev - downside_dev.mean()) / downside_dev.std()
        
        return dd_z
        
    def calculate_beta(self,
                     returns: pd.Series,
                     market_returns: pd.Series) -> pd.Series:
        """
        计算Beta
        
        Beta = Cov(Stock, Market) / Var(Market)
        """
        # 计算滚动协方差和方差
        cov = returns.rolling(self.lookback).cov(market_returns)
        var_market = market_returns.rolling(self.lookback).var()
        
        beta = cov / var_market
        
        # 标准化（负号：低Beta = 高因子值）
        beta_z = -(beta - beta.mean()) / beta.std()
        
        return beta_z
        
    def calculate_composite_low_vol(self,
                                    volatility: pd.Series,
                                    downside_dev: pd.Series,
                                    beta: pd.Series) -> pd.Series:
        """
        计算复合低波动因子
        """
        # 标准化（已经在上面标准化过了）
        # 等权重组合
        composite = (volatility + downside_dev + beta) / 3
        
        return composite
```

---

## 因子组合构建

```python
class FactorPortfolioBuilder:
    """因子组合构建器"""
    
    def __init__(self,
                 universe_size: int = 1000,
                 top_quantile: float = 0.3,
                 bottom_quantile: float = 0.3):
        """
        Args:
            universe_size: 投资组合大小
            top_quantile: 多头组合分位数（前30%）
            bottom_quantile: 空头组合分位数（后30%）
        """
        self.universe_size = universe_size
        self.top_quantile = top_quantile
        self.bottom_quantile = bottom_quantile
        
    def build_long_short_portfolio(self,
                                   factor_scores: pd.Series,
                                   prices: pd.DataFrame = None) -> Dict:
        """
        构建多空因子组合
        
        Args:
            factor_scores: 因子得分
            prices: 价格（可选，用于市值加权）
            
        Returns:
            组合权重 {
                'long': {symbol: weight},
                'short': {symbol: weight},
                'net': {symbol: weight}
            }
        """
        # 筛选有效股票
        valid_scores = factor_scores.dropna()
        
        if len(valid_scores) < self.universe_size:
            print(f"Warning: Only {len(valid_scores)} valid stocks, less than universe size")
            
        # 计算分位数
        factor_rank = valid_scores.rank(pct=True)
        
        # 构建多头组合（前 top_quantile）
        long_threshold = 1 - self.top_quantile
        long_mask = factor_rank >= long_threshold
        
        # 构建空头组合（后 bottom_quantile）
        short_threshold = self.bottom_quantile
        short_mask = factor_rank <= short_threshold
        
        # 股票列表
        long_stocks = valid_scores[long_mask].index
        short_stocks = valid_scores[short_mask].index
        
        # 计算权重
        long_weights = self._calculate_weights(
            long_stocks,
            factor_scores[long_mask],
            prices
        )
        
        short_weights = self._calculate_weights(
            short_stocks,
            factor_scores[short_mask],
            prices,
            is_short=True
        )
        
        # 净头寸
        net_weights = {}
        for stock in long_weights:
            net_weights[stock] = long_weights[stock]
        for stock in short_weights:
            if stock in net_weights:
                net_weights[stock] -= short_weights[stock]
            else:
                net_weights[stock] = -short_weights[stock]
                
        return {
            'long': long_weights,
            'short': short_weights,
            'net': net_weights,
            'long_count': len(long_stocks),
            'short_count': len(short_stocks)
        }
        
    def _calculate_weights(self,
                           stocks: List,
                           scores: pd.Series,
                           prices: pd.DataFrame = None,
                           is_short: bool = False) -> Dict:
        """
        计算组合权重
        
        可选择等权重或市值权重
        """
        if prices is not None:
            # 市值加权
            market_caps = prices.iloc[-1][stocks]
            weights = market_caps / market_caps.sum()
        else:
            # 等权重
            weights = pd.Series(1.0 / len(stocks), index=stocks)
            
        # 调整符号（空头为负）
        if is_short:
            weights = -weights
            
        return weights.to_dict()
```

---

## 因子暴露测量

```python
class FactorExposureAnalyzer:
    """因子暴露分析器"""
    
    def __init__(self, factor_models: Dict[str, FactorDefinition]):
        self.factor_models = factor_models
        
    def calculate_portfolio_exposure(self,
                                   portfolio_weights: Dict[str, float],
                                   factor_scores: pd.DataFrame) -> pd.Series:
        """
        计算投资组合对各个因子的暴露
        
        Exposure = Σ(权重 × 因子得分)
        
        Args:
            portfolio_weights: 投资组合权重 {symbol: weight}
            factor_scores: 各股票的因子得分
            
        Returns:
            因子暴露序列
        """
        exposures = {}
        
        for factor_name, scores in factor_scores.items():
            # 对齐股票
            common_stocks = set(portfolio_weights.keys()) & set(scores.index)
            
            if not common_stocks:
                exposures[factor_name] = 0.0
                continue
                
            # 计算加权平均暴露
            exposure = 0.0
            for stock in common_stocks:
                exposure += portfolio_weights[stock] * scores[stock]
                
            exposures[factor_name] = exposure
            
        return pd.Series(exposures)
        
    def calculate_factor_contribution(self,
                                    portfolio_returns: pd.Series,
                                    factor_returns: pd.DataFrame) -> pd.DataFrame:
        """
        计算因子对组合收益的贡献
        
        使用回归分析：
        Portfolio Return = α + Σ(β_i × Factor_i) + ε
        
        Args:
            portfolio_returns: 投资组合收益序列
            factor_returns: 各因子收益序列
            
        Returns:
            因子贡献 {
                'alpha': 超额收益,
                'factor_1': 贡献,
                'factor_2': 贡献,
                ...
            }
        """
        # 准备回归数据
        y = portfolio_returns
        X = factor_returns
        X = sm.add_constant(X)  # 添加截距项
        
        # 运行回归
        model = sm.OLS(y, X, missing='drop').fit()
        
        # 因子贡献 = β × 因子收益
        contributions = {}
        for factor_name in factor_returns.columns:
            contributions[factor_name] = model.params[factor_name] * factor_returns[factor_name].mean()
            
        contributions['alpha'] = model.params['const'] * 252  # 年化
        
        return pd.DataFrame(contributions)
```

---

## 因子相关性矩阵

```python
class FactorCorrelationAnalyzer:
    """因子相关性分析器"""
    
    def __init__(self):
        self.correlation_matrix = None
        
    def calculate_factor_correlation(self,
                                    factor_returns: pd.DataFrame,
                                    method: str = 'pearson') -> pd.DataFrame:
        """
        计算因子相关性矩阵
        
        Args:
            factor_returns: 各因子收益序列
            method: 相关性方法 ('pearson', 'spearman', 'kendall')
            
        Returns:
            相关性矩阵
        """
        self.correlation_matrix = factor_returns.corr(method=method)
        
        return self.correlation_matrix
        
    def calculate_diversification_benefit(self,
                                        correlation_matrix: pd.DataFrame) -> Dict:
        """
        计算多样化收益
        
        多样化收益 = 1 - 平均相关系数
        
        Returns:
            多样化指标
        """
        # 取上三角矩阵（不含对角线）
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        correlations = correlation_matrix.where(mask).stack()
        
        # 平均相关性
        avg_correlation = correlations.mean()
        
        # 多样化收益
        diversification_benefit = 1 - avg_correlation
        
        # 有效因子数量
        effective_factors = 1 / (1 + avg_correlation * (len(correlation_matrix) - 1))
        
        return {
            'avg_correlation': avg_correlation,
            'diversification_benefit': diversification_benefit,
            'effective_factors': effective_factors
        }
        
    def identify_highly_correlated_factors(self,
                                         correlation_matrix: pd.DataFrame,
                                         threshold: float = 0.7) -> List[Tuple[str, str]]:
        """
        识别高相关因子
        
        Returns:
            高相关因子对列表
        """
        highly_correlated = []
        
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) >= threshold:
                    highly_correlated.append((
                        correlation_matrix.index[i],
                        correlation_matrix.columns[j],
                        corr
                    ))
                    
        return highly_correlated
```

---

## 多因子组合

```python
class MultiFactorCombiner:
    """多因子组合器"""
    
    def __init__(self,
                 weighting_method: str = 'equal_weight',
                 correlation_adjustment: bool = True):
        """
        Args:
            weighting_method: 权重方法 ('equal_weight', 'ic_weighted', 'risk_parity')
            correlation_adjustment: 是否考虑相关性调整
        """
        self.weighting_method = weighting_method
        self.correlation_adjustment = correlation_adjustment
        
    def combine_factors(self,
                        factor_scores: pd.DataFrame,
                        ic_values: pd.Series = None,
                        risk_adjusted: bool = False) -> pd.Series:
        """
        组合多个因子
        
        Args:
            factor_scores: 各股票的因子得分
            ic_values: 各因子的 IC 值（如使用 IC 加权）
            risk_adjusted: 是否风险调整
            
        Returns:
            复合因子得分
        """
        if self.weighting_method == 'equal_weight':
            return self._equal_weight_combination(factor_scores)
        elif self.weighting_method == 'ic_weighted':
            return self._ic_weighted_combination(factor_scores, ic_values)
        elif self.weighting_method == 'risk_parity':
            return self._risk_parity_combination(factor_scores, risk_adjusted)
        else:
            raise ValueError(f"Unknown weighting method: {self.weighting_method}")
            
    def _equal_weight_combination(self,
                                  factor_scores: pd.DataFrame) -> pd.Series:
        """等权重组合"""
        return factor_scores.mean(axis=1)
        
    def _ic_weighted_combination(self,
                                   factor_scores: pd.DataFrame,
                                   ic_values: pd.Series) -> pd.Series:
        """IC 加权组合"""
        # 标准化 IC
        abs_ic = ic_values.abs()
        weights = abs_ic / abs_ic.sum()
        
        # 加权组合
        composite = pd.Series(0.0, index=factor_scores.index)
        for factor_name, weight in weights.items():
            if factor_name in factor_scores.columns:
                composite += factor_scores[factor_name] * weight
                
        return composite
        
    def _risk_parity_combination(self,
                                  factor_scores: pd.DataFrame,
                                  risk_adjusted: bool) -> pd.Series:
        """
        风险平价组合
        
        使每个因子的风险贡献相等
        """
        if not risk_adjusted:
            return self._equal_weight_combination(factor_scores)
            
        # 计算各因子的波动率
        factor_volatility = factor_scores.std()
        
        # 风险平价权重 ∝ 1/波动率
        weights = 1.0 / factor_volatility
        weights = weights / weights.sum()
        
        # 加权组合
        composite = pd.Series(0.0, index=factor_scores.index)
        for factor_name, weight in weights.items():
            if factor_name in factor_scores.columns:
                composite += factor_scores[factor_name] * weight
                
        return composite
```

---

## 再平衡策略

```python
class RebalancingStrategy:
    """再平衡策略"""
    
    def __init__(self,
                 rebalance_frequency: str = 'monthly',
                 turnover_limit: float = 0.3,  # 最大换手率 30%
                 min_trade_size: float = 10000):  # 最小交易规模
        self.rebalance_frequency = rebalance_frequency
        self.turnover_limit = turnover_limit
        self.min_trade_size = min_trade_size
        
        self.current_weights = {}
        self.target_weights = {}
        
    def should_rebalance(self,
                          date: pd.Timestamp,
                          last_rebalance_date: pd.Timestamp) -> bool:
        """
        判断是否应该再平衡
        
        Args:
            date: 当前日期
            last_rebalance_date: 上次再平衡日期
            
        Returns:
            是否应该再平衡
        """
        if self.rebalance_frequency == 'monthly':
            return date.month != last_rebalance_date.month or \
                   date.year != last_rebalance_date.year
        elif self.rebalance_frequency == 'quarterly':
            quarters = (date.month - 1) // 3 + 1
            last_quarters = (last_rebalance_date.month - 1) // 3 + 1
            return quarters != last_quarters or \
                   date.year != last_rebalance_date.year
        else:
            return False
            
    def calculate_trades(self,
                          target_weights: Dict[str, float],
                          current_weights: Dict[str, float]) -> Dict[str, float]:
        """
        计算需要交易的股票
        
        Args:
            target_weights: 目标权重
            current_weights: 当前权重
            
        Returns:
            交易列表 {symbol: weight_change}
        """
        trades = {}
        
        all_stocks = set(target_weights.keys()) | set(current_weights.keys())
        
        for stock in all_stocks:
            target = target_weights.get(stock, 0.0)
            current = current_weights.get(stock, 0.0)
            
            trade = target - current
            
            # 过滤掉小交易
            if abs(trade) * 1000000 < self.min_trade_size:  # 假设100万资金
                trade = 0.0
                
            if abs(trade) > 1e-10:  # 避免除零
                trades[stock] = trade
                
        # 检查换手率
        turnover = sum(abs(t) for t in trades.values()) / 2
        
        if turnover > self.turnover_limit:
            print(f"Warning: Turnover {turnover:.2%} exceeds limit {self.turnover_limit:.2%}")
            # 可以在这里实施换手率限制策略
            
        return trades
        
    def calculate_turnover(self,
                           old_weights: Dict[str, float],
                           new_weights: Dict[str, float]) -> float:
        """
        计算换手率
        
        Turnover = 0.5 × Σ|新权重 - 旧权重|
        """
        all_stocks = set(old_weights.keys()) | set(new_weights.keys())
        
        total_change = 0.0
        for stock in all_stocks:
            old = old_weights.get(stock, 0.0)
            new = new_weights.get(stock, 0.0)
            total_change += abs(new - old)
            
        turnover = total_change / 2
        
        return turnover
```

---

## 因子择时

```python
class FactorTimingModel:
    """因子择时模型"""
    
    def __init__(self,
                 lookback: int = 60):
        self.lookback = lookback
        
    def calculate_factor_momentum(self,
                                  factor_returns: pd.Series) -> pd.Series:
        """
        计算因子动量
        
        因子动量 = 因子组合的近期收益
        
        Args:
            factor_returns: 因子收益序列
            
        Returns:
            因子动量得分
        """
        momentum = factor_returns.rolling(self.lookback).sum()
        
        # 标准化
        momentum_z = (momentum - momentum.mean()) / momentum.std()
        
        return momentum_z
        
    def calculate_factor_moving_average(self,
                                      factor_returns: pd.Series,
                                      short_window: int = 20,
                                      long_window: int = 60) -> pd.Series:
        """
        计算因子移动平均线
        
        金叉 = 短期均线 > 长期均线 → 增加暴露
        死叉 = 短期均线 < 长期均线 → 减少暴露
        """
        ma_short = factor_returns.rolling(short_window).mean()
        ma_long = factor_returns.rolling(long_window).mean()
        
        # 信号 = (短期 - 长期) / 长期
        signal = (ma_short - ma_long) / ma_long
        
        return signal
        
    def get_factor_exposure_adjustment(self,
                                       factor_name: str,
                                       factor_returns: pd.Series,
                                       market_regime: str = 'neutral') -> float:
        """
        获取因子暴露调整倍数
        
        Args:
            factor_name: 因子名称
            factor_returns: 因子收益序列
            market_regime: 市场状态 ('bullish', 'bearish', 'neutral')
            
        Returns:
            暴露调整倍数 (如 1.5 表示增加 50% 暴露）
        """
        # 计算因子动量
        factor_momentum = self.calculate_factor_momentum(factor_returns)
        current_momentum = factor_momentum.iloc[-1]
        
        # 基础调整
        if current_momentum > 1.0:  # 强势
            base_adjustment = 1.2
        elif current_momentum < -1.0:  # 弱势
            base_adjustment = 0.8
        else:
            base_adjustment = 1.0
            
        # 根据市场状态调整
        regime_adjustment = {
            'bullish': 1.2,
            'neutral': 1.0,
            'bearish': 0.8
        }.get(market_regime, 1.0)
        
        # 总调整
        total_adjustment = base_adjustment * regime_adjustment
        
        # 限制范围 [0.5, 1.5]
        total_adjustment = max(0.5, min(1.5, total_adjustment))
        
        return total_adjustment
```

---

## 绩效归因

```python
import statsmodels.api as sm

class PerformanceAttributor:
    """绩效归因器"""
    
    def __init__(self):
        self.attribution_results = {}
        
    def factor_attribution(self,
                          portfolio_returns: pd.Series,
                          factor_returns: pd.DataFrame,
                          market_returns: pd.Series = None) -> Dict:
        """
        因子归因分析
        
        分解投资组合收益为：
        - Alpha (超额收益）
        - Beta × 市场收益
        - Σ(β_i × Factor_i)
        - 特质收益 (Idiosyncratic)
        
        Args:
            portfolio_returns: 投资组合收益
            factor_returns: 各因子收益
            market_returns: 市场收益（可选）
            
        Returns:
            归因结果
        """
        # 准备回归数据
        X = factor_returns.copy()
        if market_returns is not None:
            X['market'] = market_returns
            
        X = sm.add_constant(X)
        y = portfolio_returns
        
        # 运行回归
        model = sm.OLS(y, X, missing='drop').fit()
        
        # 提取结果
        results = {
            'alpha': model.params['const'] * 252,  # 年化 Alpha
            'alpha_t_stat': model.tvalues['const'],
            'alpha_p_value': model.pvalues['const'],
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'factor_betas': {},
            'factor_contributions': {}
        }
        
        # 各因子贡献
        for factor_name in factor_returns.columns:
            if factor_name in model.params:
                beta = model.params[factor_name]
                t_stat = model.tvalues[factor_name]
                p_value = model.pvalues[factor_name]
                
                results['factor_betas'][factor_name] = {
                    'beta': beta,
                    't_stat': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
                
                # 贡献 = Beta × 年化因子收益
                factor_annual_return = factor_returns[factor_name].mean() * 252
                contribution = beta * factor_annual_return
                results['factor_contributions'][factor_name] = contribution
                
        return results
        
    def rolling_attribution(self,
                             portfolio_returns: pd.Series,
                             factor_returns: pd.DataFrame,
                             window: int = 252) -> pd.DataFrame:
        """
        滚动归因分析
        
        Args:
            portfolio_returns: 投资组合收益
            factor_returns: 各因子收益
            window: 滚动窗口
            
        Returns:
            滚动归因结果
        """
        rolling_alphas = []
        rolling_betas = pd.DataFrame()
        
        for i in range(window, len(portfolio_returns)):
            y = portfolio_returns.iloc[i-window:i]
            X = factor_returns.iloc[i-window:i]
            X = sm.add_constant(X)
            
            model = sm.OLS(y, X, missing='drop').fit()
            rolling_alphas.append(model.params['const'])
            
            # 保存 Beta
            for factor_name in factor_returns.columns:
                if factor_name in model.params:
                    if factor_name not in rolling_betas.columns:
                        rolling_betas[factor_name] = []
                    rolling_betas[factor_name].append(model.params[factor_name])
                    
        result_df = pd.DataFrame({
            'alpha': rolling_alphas
        }, index=portfolio_returns.index[window:])
        
        for factor_name in rolling_betas.columns:
            result_df[f'{factor_name}_beta'] = rolling_betas[factor_name]
            
        return result_df
```

---

## 完整因子模型系统

```python
class FactorModelSystem:
    """完整因子模型系统"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 配置字典 {
                'factors': ['value', 'momentum', 'quality', 'size', 'low_volatility'],
                'universe_size': 1000,
                'rebalance_frequency': 'monthly',
                ...
            }
        """
        # 初始化各个因子
        self.factors = {
            'value': ValueFactor(),
            'momentum': MomentumFactor(),
            'quality': QualityFactor(),
            'size': SizeFactor(),
            'low_volatility': LowVolatilityFactor()
        }
        
        # 初始化其他模块
        self.portfolio_builder = FactorPortfolioBuilder(
            universe_size=config.get('universe_size', 1000)
        )
        self.exposure_analyzer = FactorExposureAnalyzer(self.factors)
        self.correlation_analyzer = FactorCorrelationAnalyzer()
        self.factor_combiner = MultiFactorCombiner(
            weighting_method=config.get('weighting_method', 'equal_weight')
        )
        self.rebalancer = RebalancingStrategy(
            rebalance_frequency=config.get('rebalance_frequency', 'monthly')
        )
        self.timing_model = FactorTimingModel()
        self.attributor = PerformanceAttributor()
        
        # 存储状态
        self.factor_scores = {}
        self.portfolio_weights = {}
        self.last_rebalance_date = None
        
    def calculate_all_factors(self,
                               data: Dict) -> Dict[str, pd.Series]:
        """
        计算所有因子得分
        
        Args:
            data: 数据字典 {
                'prices': 价格数据,
                'fundamentals': 基本面数据,
                'returns': 收益数据
            }
            
        Returns:
            各因子得分
        """
        factor_scores = {}
        
        # 价值因子
        btm = self.factors['value'].calculate_btm(
            data['fundamentals']['book_value'],
            data['fundamentals']['market_cap']
        )
        earnings_yield = self.factors['value'].calculate_earnings_yield(
            data['fundamentals']['earnings'],
            data['fundamentals']['market_cap']
        )
        cf_yield = self.factors['value'].calculate_cf_yield(
            data['fundamentals']['cash_flow'],
            data['fundamentals']['market_cap']
        )
        factor_scores['value'] = self.factors['value'].calculate_composite_value(
            btm, earnings_yield, cf_yield
        )
        
        # 动量因子
        factor_scores['momentum'] = self.factors['momentum'].calculate_momentum(
            data['prices']
        )
        
        # 质量因子
        roe = self.factors['quality'].calculate_roe(
            data['fundamentals']['net_income'],
            data['fundamentals']['equity']
        )
        roa = self.factors['quality'].calculate_roa(
            data['fundamentals']['net_income'],
            data['fundamentals']['total_assets']
        )
        profit_margin = self.factors['quality'].calculate_profit_margin(
            data['fundamentals']['net_income'],
            data['fundamentals']['revenue']
        )
        debt_to_equity = self.factors['quality'].calculate_debt_to_equity(
            data['fundamentals']['total_debt'],
            data['fundamentals']['equity']
        )
        earnings_stability = self.factors['quality'].calculate_earnings_stability(
            data['fundamentals']['earnings_history']
        )
        factor_scores['quality'] = self.factors['quality'].calculate_composite_quality(
            roe, roa, profit_margin, debt_to_equity, earnings_stability
        )
        
        # 规模因子
        factor_scores['size'] = self.factors['size'].calculate_size(
            data['fundamentals']['market_cap']
        )
        
        # 低波动因子
        volatility = self.factors['low_volatility'].calculate_volatility(
            data['returns']
        )
        downside_dev = self.factors['low_volatility'].calculate_downside_deviation(
            data['returns']
        )
        beta = self.factors['low_volatility'].calculate_beta(
            data['returns'],
            data['market_returns']
        )
        factor_scores['low_volatility'] = self.factors['low_volatility'].calculate_composite_low_vol(
            volatility, downside_dev, beta
        )
        
        self.factor_scores = factor_scores
        return factor_scores
        
    def build_factor_portfolios(self,
                               factor_scores: Dict[str, pd.Series],
                               prices: pd.DataFrame) -> Dict[str, Dict]:
        """
        为每个因子构建多空组合
        
        Returns:
            各因子的组合权重
        """
        factor_portfolios = {}
        
        for factor_name, scores in factor_scores.items():
            portfolio = self.portfolio_builder.build_long_short_portfolio(
                scores, prices
            )
            factor_portfolios[factor_name] = portfolio
            
        return factor_portfolios
        
    def combine_factors(self,
                        factor_scores: Dict[str, pd.Series],
                        ic_values: Dict[str, float] = None) -> pd.Series:
        """
        组合多个因子
        """
        factor_scores_df = pd.DataFrame(factor_scores)
        
        if ic_values:
            ic_series = pd.Series(ic_values)
            return self.factor_combiner.combine_factors(
                factor_scores_df, ic_series
            )
        else:
            return self.factor_combiner.combine_factors(
                factor_scores_df
            )
        
    def run_backtest(self,
                      data: Dict,
                      start_date: str,
                      end_date: str) -> Dict:
        """
        运行回测
        
        Args:
            data: 历史数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        results = {
            'dates': [],
            'returns': [],
            'factor_exposures': []
        }
        
        # 生成再平衡日期
        dates = pd.date_range(start_date, end_date, freq='M')
        
        for i, date in enumerate(dates):
            # 计算因子得分
            factor_scores = self.calculate_all_factors(data)
            
            # 组合因子
            composite_factor = self.combine_factors(factor_scores)
            
            # 构建组合
            portfolio = self.portfolio_builder.build_long_short_portfolio(
                composite_factor,
                data['prices']
            )
            
            # 计算因子暴露
            exposure = self.exposure_analyzer.calculate_portfolio_exposure(
                portfolio['net'],
                pd.DataFrame(factor_scores)
            )
            
            # 保存状态
            results['dates'].append(date)
            results['factor_exposures'].append(exposure)
            
            # 计算下月收益（简化版）
            if i < len(dates) - 1:
                next_date = dates[i + 1]
                monthly_return = self._calculate_portfolio_return(
                    portfolio, data['prices'], date, next_date
                )
                results['returns'].append(monthly_return)
            else:
                results['returns'].append(0.0)
                
        # 构建结果数据框
        results_df = pd.DataFrame({
            'date': results['dates'],
            'return': results['returns']
        })
        
        # 计算绩效指标
        performance_metrics = self._calculate_performance_metrics(results_df['return'])
        
        return {
            'results_df': results_df,
            'performance_metrics': performance_metrics
        }
        
    def _calculate_portfolio_return(self,
                                   portfolio: Dict,
                                   prices: pd.DataFrame,
                                   start_date: pd.Timestamp,
                                   end_date: pd.Timestamp) -> float:
        """计算投资组合收益"""
        returns = []
        
        for stock, weight in portfolio['net'].items():
            if stock in prices.columns and weight != 0:
                stock_return = (prices.loc[end_date, stock] /
                               prices.loc[start_date, stock] - 1)
                returns.append(weight * stock_return)
                
        return sum(returns)
        
    def _calculate_performance_metrics(self, returns: pd.Series) -> Dict:
        """计算绩效指标"""
        cumulative_return = (1 + returns).prod() - 1
        annual_return = returns.mean() * 12
        annual_vol = returns.std() * np.sqrt(12)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0
        
        max_drawdown = self._calculate_max_drawdown(returns)
        
        return {
            'total_return': cumulative_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown
        }
        
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        
        return max_dd
```

---

## 配置参数

```python
FACTOR_MODEL_CONFIG = {
    # 因子选择
    'factors': [
        'value',
        'momentum', 
        'quality',
        'size',
        'low_volatility'
    ],
    
    # 投资组合构建
    'universe_size': 1000,           # 投资组合大小
    'top_quantile': 0.3,             # 多头分位数
    'bottom_quantile': 0.3,          # 空头分位数
    'weighting_method': 'equal_weight', # 权重方法
    
    # 再平衡
    'rebalance_frequency': 'monthly',   # 再平衡频率
    'turnover_limit': 0.3,          # 最大换手率
    'min_trade_size': 10000,         # 最小交易规模
    
    # 因子择时
    'enable_factor_timing': False,     # 是否启用因子择时
    'timing_lookback': 60,            # 择时窗口
    
    # 绩效归因
    'attribution_window': 252,        # 归因窗口
}
```

---

## 目标绩效指标

```python
FACTOR_MODEL_TARGETS = {
    # Alpha
    'target_alpha': 0.04,            # 目标 Alpha 4%
    'min_alpha_t_stat': 2.0,         # 最小 Alpha t 统计量
    
    # 风险调整收益
    'target_sharpe': 1.5,            # 目标夏普比率 1.5
    'max_drawdown': 0.15,            # 最大回撤 15%
    
    # 换手率
    'max_turnover': 0.3,              # 最大换手率 30%
    
    # 因子暴露
    'max_factor_concentration': 0.5,    # 最大单一因子暴露 50%
    'diversification_benefit': 0.6,   # 多样化收益 60%
}
```

---

_创建时间：2026年2月23日_
