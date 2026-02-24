# AQR因子模型Python实现指南

## 完整实现架构

### 系统架构

```
FactorModelSystem
├── Factor Definitions (因子定义)
│   ├── ValueFactor
│   ├── MomentumFactor
│   ├── QualityFactor
│   ├── SizeFactor
│   └── LowVolatilityFactor
├── Portfolio Builder (组合构建)
├── Exposure Analyzer (暴露分析)
├── Correlation Analyzer (相关性分析)
├── Factor Combiner (因子组合)
├── Rebalancing Strategy (再平衡策略)
├── Timing Model (择时模型)
└── Performance Attributor (绩效归因)
```

## 1. 因子定义实现

### 基础数据结构

```python
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd

@dataclass
class FactorDefinition:
    """因子定义"""
    name: str
    description: str
    formula: str
    data_requirements: List[str]
    expected_premium: float  # 预期风险溢价（年化）
```

### 价值因子实现

```python
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

        Args:
            book_value: 账面价值序列
            market_cap: 市值序列

        Returns:
            BtM因子值
        """
        # 数据清洗
        valid_mask = (book_value > 0) & (market_cap > 0)
        btm = pd.Series(np.nan, index=book_value.index)

        # 计算BtM
        btm[valid_mask] = book_value[valid_mask] / market_cap[valid_mask]

        return btm

    def calculate_earnings_yield(self,
                                 earnings: pd.Series,
                                 market_cap: pd.Series) -> pd.Series:
        """
        计算收益市盈率倒数 (Earnings Yield)

        Earnings Yield = Earnings / Market Cap = 1 / PE
        """
        valid_mask = (earnings > 0) & (market_cap > 0)
        ey = pd.Series(np.nan, index=earnings.index)

        ey[valid_mask] = earnings[valid_mask] / market_cap[valid_mask]

        return ey

    def calculate_cf_yield(self,
                           cash_flow: pd.Series,
                           market_cap: pd.Series) -> pd.Series:
        """
        计算现金流收益率 (Cash Flow Yield)
        """
        valid_mask = (cash_flow > 0) & (market_cap > 0)
        cfy = pd.Series(np.nan, index=cash_flow.index)

        cfy[valid_mask] = cash_flow[valid_mask] / market_cap[valid_mask]

        return cfy

    def winsorize(self,
                  series: pd.Series,
                  lower: float = 0.01,
                  upper: float = 0.99) -> pd.Series:
        """
        Winsorize处理极端值

        将低于lower分位数的值设为lower分位数
        将高于upper分位数的值设为upper分位数
        """
        lower_bound = series.quantile(lower)
        upper_bound = series.quantile(upper)

        return series.clip(lower=lower_bound, upper=upper_bound)

    def standardize(self, series: pd.Series) -> pd.Series:
        """
        标准化（Z-score）

        Z = (X - Mean) / Std
        """
        return (series - series.mean()) / series.std()

    def calculate_composite_value(self,
                                  btm: pd.Series,
                                  earnings_yield: pd.Series,
                                  cf_yield: pd.Series) -> pd.Series:
        """
        计算复合价值因子

        步骤：
        1. Winsorize处理极端值
        2. 标准化每个子因子
        3. 等权重组合
        """
        # Winsorize
        btm_win = self.winsorize(btm.dropna())
        ey_win = self.winsorize(earnings_yield.dropna())
        cfy_win = self.winsorize(cf_yield.dropna())

        # 标准化
        btm_z = self.standardize(btm_win)
        ey_z = self.standardize(ey_win)
        cfy_z = self.standardize(cfy_win)

        # 等权重组合
        composite = (btm_z + ey_z + cfy_z) / 3

        return composite
```

### 动量因子实现

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

    def calculate_cumulative_return(self,
                                    prices: pd.Series,
                                    lookback: int) -> float:
        """
        计算累积收益率
        """
        if len(prices) < lookback + 1:
            return np.nan

        return (prices.iloc[-1] / prices.iloc[-lookback-1] - 1)

    def calculate_momentum(self,
                           prices: pd.DataFrame,
                           exclude_recent: bool = True) -> pd.Series:
        """
        计算动量

        标准公式：12个月累积收益率，排除最近1个月
        """
        momentum = pd.Series(np.nan, index=prices.columns)

        for stock in prices.columns:
            stock_prices = prices[stock].dropna()

            # 计算12个月累积收益
            returns_12m = self.calculate_cumulative_return(
                stock_prices, self.lookback_12m
            )

            # 排除最近1个月
            if exclude_recent:
                returns_1m = self.calculate_cumulative_return(
                    stock_prices, self.lookback_1m
                )

                if not np.isnan(returns_12m) and not np.isnan(returns_1m):
                    # 动量 = (1+R_12m) / (1+R_1m) - 1
                    momentum[stock] = (1 + returns_12m) / (1 + returns_1m) - 1
            else:
                momentum[stock] = returns_12m

        # 标准化
        momentum_win = self.winsorize(momentum.dropna())
        momentum_z = self.standardize(momentum_win)

        return momentum_z

    def winsorize(self, series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        lower_bound = series.quantile(lower)
        upper_bound = series.quantile(upper)
        return series.clip(lower=lower_bound, upper=upper_bound)

    def standardize(self, series: pd.Series) -> pd.Series:
        return (series - series.mean()) / series.std()
```

### 质量因子实现

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
        """ROE = Net Income / Shareholders Equity"""
        valid_mask = (equity > 0)
        roe = pd.Series(np.nan, index=net_income.index)
        roe[valid_mask] = net_income[valid_mask] / equity[valid_mask]
        return roe

    def calculate_roa(self,
                      net_income: pd.Series,
                      total_assets: pd.Series) -> pd.Series:
        """ROA = Net Income / Total Assets"""
        valid_mask = (total_assets > 0)
        roa = pd.Series(np.nan, index=net_income.index)
        roa[valid_mask] = net_income[valid_mask] / total_assets[valid_mask]
        return roa

    def calculate_profit_margin(self,
                                net_income: pd.Series,
                                revenue: pd.Series) -> pd.Series:
        """Profit Margin = Net Income / Revenue"""
        valid_mask = (revenue > 0)
        pm = pd.Series(np.nan, index=net_income.index)
        pm[valid_mask] = net_income[valid_mask] / revenue[valid_mask]
        return pm

    def calculate_debt_to_equity(self,
                                  total_debt: pd.Series,
                                  equity: pd.Series) -> pd.Series:
        """D/E = Total Debt / Shareholders Equity"""
        valid_mask = (equity > 0)
        de = pd.Series(np.nan, index=total_debt.index)
        de[valid_mask] = total_debt[valid_mask] / equity[valid_mask]
        return de

    def calculate_earnings_stability(self,
                                     earnings_history: pd.DataFrame) -> pd.Series:
        """
        计算收益稳定性

        稳定性 = 1 - 收益的变异系数
        """
        stability = pd.Series(np.nan, index=earnings_history.columns)

        for stock in earnings_history.columns:
            earnings = earnings_history[stock].dropna()

            if len(earnings) < 2:
                continue

            earnings_mean = earnings.mean()
            earnings_std = earnings.std()

            if earnings_mean != 0:
                cv = earnings_std / abs(earnings_mean)
                stability[stock] = max(0, 1 - cv)

        return stability

    def calculate_composite_quality(self,
                                    roe: pd.Series,
                                    roa: pd.Series,
                                    profit_margin: pd.Series,
                                    debt_to_equity: pd.Series,
                                    earnings_stability: pd.Series) -> pd.Series:
        """计算复合质量因子"""
        # Winsorize
        roe_win = self.winsorize(roe.dropna())
        roa_win = self.winsorize(roa.dropna())
        pm_win = self.winsorize(profit_margin.dropna())
        de_win = self.winsorize(debt_to_equity.dropna())
        es_win = self.winsorize(earnings_stability.dropna())

        # 标准化
        roe_z = self.standardize(roe_win)
        roa_z = self.standardize(roa_win)
        pm_z = self.standardize(pm_win)

        # 债务股权比：低D/E是高质量，所以取负
        de_z = -self.standardize(de_win)

        es_z = self.standardize(es_win)

        # 等权重组合
        composite = (roe_z + roa_z + pm_z + de_z + es_z) / 5

        return composite

    def winsorize(self, series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        lower_bound = series.quantile(lower)
        upper_bound = series.quantile(upper)
        return series.clip(lower=lower_bound, upper=upper_bound)

    def standardize(self, series: pd.Series) -> pd.Series:
        return (series - series.mean()) / series.std()
```

## 2. 因子组合构建

```python
from typing import Dict, List

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

        if len(valid_scores) < 10:
            print("Warning: Too few valid stocks")
            return {'long': {}, 'short': {}, 'net': {}, 'long_count': 0, 'short_count': 0}

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

## 3. 因子暴露分析

```python
import statsmodels.api as sm

class FactorExposureAnalyzer:
    """因子暴露分析器"""

    def __init__(self, factor_models: Dict):
        self.factor_models = factor_models

    def calculate_portfolio_exposure(self,
                                     portfolio_weights: Dict[str, float],
                                     factor_scores: pd.DataFrame) -> pd.Series:
        """
        计算投资组合对各个因子的暴露

        Exposure = Σ(权重 × 因子得分)
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
            total_weight = 0.0

            for stock in common_stocks:
                exposure += portfolio_weights[stock] * scores[stock]
                total_weight += abs(portfolio_weights[stock])

            if total_weight > 0:
                exposures[factor_name] = exposure / total_weight
            else:
                exposures[factor_name] = 0.0

        return pd.Series(exposures)

    def calculate_factor_contribution(self,
                                      portfolio_returns: pd.Series,
                                      factor_returns: pd.DataFrame) -> pd.DataFrame:
        """
        计算因子对组合收益的贡献

        使用回归分析：
        Portfolio Return = α + Σ(β_i × Factor_i) + ε
        """
        # 准备回归数据
        y = portfolio_returns
        X = factor_returns.copy()
        X = sm.add_constant(X)  # 添加截距项

        # 运行回归
        model = sm.OLS(y, X, missing='drop').fit()

        # 因子贡献 = β × 因子收益
        contributions = {}
        for factor_name in factor_returns.columns:
            if factor_name in model.params:
                contributions[factor_name] = (
                    model.params[factor_name] *
                    factor_returns[factor_name].mean() * 252
                )

        contributions['alpha'] = model.params['const'] * 252  # 年化

        return pd.DataFrame(contributions, index=['contribution']).T
```

## 4. 数据加载示例

```python
import yfinance as yf

class FactorDataLoader:
    """因子数据加载器"""

    def __init__(self, symbols: List[str], start_date: str, end_date: str):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date

    def load_price_data(self) -> pd.DataFrame:
        """加载价格数据"""
        data = yf.download(self.symbols, start=self.start_date, end=self.end_date)
        return data['Adj Close']

    def load_fundamental_data(self) -> Dict:
        """
        加载基本面数据

        注意：yfinance的基本面数据有限
        实际应用中应使用专业数据源（如Bloomberg, Compustat）
        """
        fundamentals = {}

        for symbol in self.symbols:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            fundamentals[symbol] = {
                'market_cap': info.get('marketCap'),
                'book_value': info.get('bookValue'),
                'earnings': info.get('netIncomeToCommon'),
                'total_debt': info.get('totalDebt'),
                'total_assets': info.get('totalAssets'),
                'revenue': info.get('totalRevenue')
            }

        return fundamentals
```

## 5. 配置和使用

```python
# 配置
FACTOR_MODEL_CONFIG = {
    'factors': ['value', 'momentum', 'quality', 'size', 'low_volatility'],
    'universe_size': 1000,
    'rebalance_frequency': 'monthly',
    'weighting_method': 'equal_weight'
}

# 使用示例
if __name__ == "__main__":
    # 1. 加载数据
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # 示例
    loader = FactorDataLoader(symbols, '2020-01-01', '2024-12-31')
    prices = loader.load_price_data()

    # 2. 计算因子
    value_factor = ValueFactor()

    # 模拟基本面数据
    fundamentals = pd.DataFrame({
        'book_value': [100, 200, 150, 80, 120],
        'market_cap': [1000, 2000, 1500, 800, 1200],
        'earnings': [50, 100, 75, 40, 60],
        'cash_flow': [60, 110, 80, 45, 70]
    }, index=symbols)

    # 计算价值因子
    btm = value_factor.calculate_btm(
        fundamentals['book_value'],
        fundamentals['market_cap']
    )

    ey = value_factor.calculate_earnings_yield(
        fundamentals['earnings'],
        fundamentals['market_cap']
    )

    cfy = value_factor.calculate_cf_yield(
        fundamentals['cash_flow'],
        fundamentals['market_cap']
    )

    composite_value = value_factor.calculate_composite_value(btm, ey, cfy)

    print("Value Factor Scores:")
    print(composite_value.sort_values(ascending=False))
```

## 依赖库

```python
requirements = [
    'numpy>=1.21.0',
    'pandas>=1.3.0',
    'statsmodels>=0.13.0',
    'scipy>=1.7.0',
    'yfinance>=0.2.0',  # 用于示例数据加载
    'scikit-learn>=1.0.0',  # 可选，用于高级分析
    'matplotlib>=3.4.0',  # 可选，用于可视化
    'seaborn>=0.11.0'  # 可选，用于可视化
]
```

## 注意事项

1. **数据质量**
   - 确保数据的一致性和准确性
   - 处理缺失值和异常值
   - 考虑 survivorship bias

2. **交易成本**
   - 实际实现需要考虑交易成本
   - 包括佣金、市场冲击、税收

3. **风险控制**
   - 设置最大仓位限制
   - 行业暴露限制
   - 换手率控制

4. **回测偏差**
   - 避免 look-ahead bias
   - 避免 survivorship bias
   - 考虑实际可交易性
