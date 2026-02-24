"""
AQR因子模型实现
完整的因子计算、组合构建、暴露分析和绩效归因系统
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import statsmodels.api as sm


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class FactorDefinition:
    """因子定义"""
    name: str
    description: str
    formula: str
    data_requirements: List[str]
    expected_premium: float  # 预期风险溢价（年化）


# ============================================================================
# 因子定义
# ============================================================================

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

    def calculate_btm(self, book_value: pd.Series, market_cap: pd.Series) -> pd.Series:
        """计算账面市值比"""
        valid_mask = (book_value > 0) & (market_cap > 0)
        btm = pd.Series(np.nan, index=book_value.index)
        btm[valid_mask] = book_value[valid_mask] / market_cap[valid_mask]
        return btm

    def calculate_earnings_yield(self, earnings: pd.Series, market_cap: pd.Series) -> pd.Series:
        """计算收益市盈率倒数"""
        valid_mask = (earnings > 0) & (market_cap > 0)
        ey = pd.Series(np.nan, index=earnings.index)
        ey[valid_mask] = earnings[valid_mask] / market_cap[valid_mask]
        return ey

    def calculate_cf_yield(self, cash_flow: pd.Series, market_cap: pd.Series) -> pd.Series:
        """计算现金流收益率"""
        valid_mask = (cash_flow > 0) & (market_cap > 0)
        cfy = pd.Series(np.nan, index=cash_flow.index)
        cfy[valid_mask] = cash_flow[valid_mask] / market_cap[valid_mask]
        return cfy

    def winsorize(self, series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        """Winsorize处理极端值"""
        lower_bound = series.quantile(lower)
        upper_bound = series.quantile(upper)
        return series.clip(lower=lower_bound, upper=upper_bound)

    def standardize(self, series: pd.Series) -> pd.Series:
        """标准化"""
        return (series - series.mean()) / series.std()

    def calculate_composite_value(self, btm: pd.Series, earnings_yield: pd.Series,
                                   cf_yield: pd.Series) -> pd.Series:
        """计算复合价值因子"""
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


class MomentumFactor:
    """动量因子"""

    def __init__(self, lookback_1m: int = 20, lookback_12m: int = 252):
        self.lookback_1m = lookback_1m
        self.lookback_12m = lookback_12m
        self.definition = FactorDefinition(
            name='Momentum',
            description='过去表现好的股票未来预期收益更高',
            formula='12-month cumulative return, excluding most recent 1 month',
            data_requirements=['daily_returns'],
            expected_premium=0.06
        )

    def calculate_momentum(self, prices: pd.DataFrame, exclude_recent: bool = True) -> pd.Series:
        """计算动量"""
        momentum = pd.Series(np.nan, index=prices.columns)

        for stock in prices.columns:
            stock_prices = prices[stock].dropna()

            if len(stock_prices) < self.lookback_12m + 1:
                continue

            # 计算12个月累积收益
            returns_12m = stock_prices.iloc[-1] / stock_prices.iloc[-self.lookback_12m-1] - 1

            # 排除最近1个月
            if exclude_recent and len(stock_prices) > self.lookback_1m + 1:
                returns_1m = stock_prices.iloc[-1] / stock_prices.iloc[-self.lookback_1m-1] - 1
                if not np.isnan(returns_12m) and not np.isnan(returns_1m):
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


class QualityFactor:
    """质量因子"""

    def __init__(self):
        self.definition = FactorDefinition(
            name='Quality',
            description='财务质量高的公司预期收益更高',
            formula='ROE, ROA, profit margin, debt-to-equity, earnings stability',
            data_requirements=['net_income', 'equity', 'total_assets', 'revenue', 'total_debt'],
            expected_premium=0.03
        )

    def calculate_roe(self, net_income: pd.Series, equity: pd.Series) -> pd.Series:
        """ROE = Net Income / Shareholders Equity"""
        valid_mask = (equity > 0)
        roe = pd.Series(np.nan, index=net_income.index)
        roe[valid_mask] = net_income[valid_mask] / equity[valid_mask]
        return roe

    def calculate_roa(self, net_income: pd.Series, total_assets: pd.Series) -> pd.Series:
        """ROA = Net Income / Total Assets"""
        valid_mask = (total_assets > 0)
        roa = pd.Series(np.nan, index=net_income.index)
        roa[valid_mask] = net_income[valid_mask] / total_assets[valid_mask]
        return roa

    def calculate_profit_margin(self, net_income: pd.Series, revenue: pd.Series) -> pd.Series:
        """Profit Margin = Net Income / Revenue"""
        valid_mask = (revenue > 0)
        pm = pd.Series(np.nan, index=net_income.index)
        pm[valid_mask] = net_income[valid_mask] / revenue[valid_mask]
        return pm

    def calculate_debt_to_equity(self, total_debt: pd.Series, equity: pd.Series) -> pd.Series:
        """D/E = Total Debt / Shareholders Equity"""
        valid_mask = (equity > 0)
        de = pd.Series(np.nan, index=total_debt.index)
        de[valid_mask] = total_debt[valid_mask] / equity[valid_mask]
        return de

    def calculate_composite_quality(self, roe: pd.Series, roa: pd.Series, profit_margin: pd.Series,
                                     debt_to_equity: pd.Series, earnings_stability: pd.Series) -> pd.Series:
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
        de_z = -self.standardize(de_win)  # 低D/E是高质量
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


class SizeFactor:
    """规模因子"""

    def __init__(self):
        self.definition = FactorDefinition(
            name='Size',
            description='小盘股预期收益高于大盘股',
            formula='Market Capitalization (log)',
            data_requirements=['market_cap'],
            expected_premium=0.02
        )

    def calculate_size(self, market_cap: pd.Series) -> pd.Series:
        """计算规模因子"""
        size = -np.log(market_cap)  # 负号：小市值 = 高因子值
        size_z = self.standardize(size)
        return size_z

    def standardize(self, series: pd.Series) -> pd.Series:
        return (series - series.mean()) / series.std()


class LowVolatilityFactor:
    """低波动因子"""

    def __init__(self, lookback: int = 252):
        self.lookback = lookback
        self.definition = FactorDefinition(
            name='Low Volatility',
            description='低波动股票经风险调整后收益更高',
            formula='Historical volatility, downside deviation, beta',
            data_requirements=['daily_returns', 'market_returns'],
            expected_premium=0.02
        )

    def calculate_volatility(self, returns: pd.Series) -> float:
        """计算历史波动率"""
        if len(returns) < self.lookback:
            return np.nan
        volatility = returns.tail(self.lookback).std() * np.sqrt(252)
        return volatility

    def calculate_volatility_for_all(self, returns: pd.DataFrame) -> pd.Series:
        """计算所有股票的波动率"""
        volatilities = pd.Series(np.nan, index=returns.columns)

        for stock in returns.columns:
            vol = self.calculate_volatility(returns[stock].dropna())
            if not np.isnan(vol):
                volatilities[stock] = vol

        # 标准化（负号：低波动 = 高因子值）
        vol_z = -(volatilities - volatilities.mean()) / volatilities.std()
        return vol_z

    def calculate_composite_low_vol(self, volatility: pd.Series, downside_dev: pd.Series,
                                     beta: pd.Series) -> pd.Series:
        """计算复合低波动因子"""
        # 等权重组合
        composite = (volatility + downside_dev + beta) / 3
        return composite


# ============================================================================
# 因子组合构建
# ============================================================================

class FactorPortfolioBuilder:
    """因子组合构建器"""

    def __init__(self, universe_size: int = 1000, top_quantile: float = 0.3,
                 bottom_quantile: float = 0.3):
        self.universe_size = universe_size
        self.top_quantile = top_quantile
        self.bottom_quantile = bottom_quantile

    def build_long_short_portfolio(self, factor_scores: pd.Series,
                                   prices: pd.DataFrame = None) -> Dict:
        """构建多空因子组合"""
        valid_scores = factor_scores.dropna()

        if len(valid_scores) < 10:
            return {'long': {}, 'short': {}, 'net': {}, 'long_count': 0, 'short_count': 0}

        # 计算分位数
        factor_rank = valid_scores.rank(pct=True)

        # 构建多头组合
        long_threshold = 1 - self.top_quantile
        long_mask = factor_rank >= long_threshold
        long_stocks = valid_scores[long_mask].index

        # 构建空头组合
        short_threshold = self.bottom_quantile
        short_mask = factor_rank <= short_threshold
        short_stocks = valid_scores[short_mask].index

        # 计算权重
        long_weights = self._calculate_weights(long_stocks, factor_scores[long_mask], prices)
        short_weights = self._calculate_weights(short_stocks, factor_scores[short_mask],
                                                 prices, is_short=True)

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

    def _calculate_weights(self, stocks: List, scores: pd.Series,
                           prices: pd.DataFrame = None, is_short: bool = False) -> Dict:
        """计算组合权重"""
        if prices is not None:
            market_caps = prices.iloc[-1][stocks]
            weights = market_caps / market_caps.sum()
        else:
            weights = pd.Series(1.0 / len(stocks), index=stocks)

        if is_short:
            weights = -weights

        return weights.to_dict()


# ============================================================================
# 因子暴露分析
# ============================================================================

class FactorExposureAnalyzer:
    """因子暴露分析器"""

    def __init__(self, factor_models: Dict):
        self.factor_models = factor_models

    def calculate_portfolio_exposure(self, portfolio_weights: Dict[str, float],
                                      factor_scores: pd.DataFrame) -> pd.Series:
        """计算投资组合对各个因子的暴露"""
        exposures = {}

        for factor_name, scores in factor_scores.items():
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


# ============================================================================
# 绩效归因
# ============================================================================

class PerformanceAttributor:
    """绩效归因器"""

    def __init__(self):
        self.attribution_results = {}

    def factor_attribution(self, portfolio_returns: pd.Series, factor_returns: pd.DataFrame,
                           market_returns: pd.Series = None) -> Dict:
        """因子归因分析"""
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
            'alpha': model.params['const'] * 252 if 'const' in model.params else np.nan,
            'alpha_t_stat': model.tvalues['const'] if 'const' in model.tvalues else np.nan,
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'factor_betas': {},
            'factor_contributions': {}
        }

        # 各因子贡献
        for factor_name in factor_returns.columns:
            if factor_name in model.params:
                beta = model.params[factor_name]
                t_stat = model.tvalues.get(factor_name, np.nan)
                p_value = model.pvalues.get(factor_name, np.nan)

                results['factor_betas'][factor_name] = {
                    'beta': beta,
                    't_stat': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05 if not np.isnan(p_value) else False
                }

                # 贡献 = Beta × 年化因子收益
                factor_annual_return = factor_returns[factor_name].mean() * 252
                contribution = beta * factor_annual_return
                results['factor_contributions'][factor_name] = contribution

        return results


# ============================================================================
# 完整因子模型系统
# ============================================================================

class FactorModelSystem:
    """完整因子模型系统"""

    def __init__(self, config: Dict):
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
        self.attributor = PerformanceAttributor()

        # 存储状态
        self.factor_scores = {}
        self.portfolio_weights = {}

    def calculate_all_factors(self, data: Dict) -> Dict[str, pd.Series]:
        """计算所有因子得分"""
        factor_scores = {}

        # 价值因子
        if 'book_value' in data['fundamentals'] and 'earnings' in data['fundamentals']:
            btm = self.factors['value'].calculate_btm(
                data['fundamentals']['book_value'],
                data['fundamentals']['market_cap']
            )
            earnings_yield = self.factors['value'].calculate_earnings_yield(
                data['fundamentals']['earnings'],
                data['fundamentals']['market_cap']
            )
            cf_yield = self.factors['value'].calculate_cf_yield(
                data['fundamentals'].get('cash_flow', pd.Series()),
                data['fundamentals']['market_cap']
            )
            factor_scores['value'] = self.factors['value'].calculate_composite_value(
                btm, earnings_yield, cf_yield
            )

        # 动量因子
        if 'prices' in data:
            factor_scores['momentum'] = self.factors['momentum'].calculate_momentum(
                data['prices']
            )

        # 质量因子
        if all(key in data['fundamentals'] for key in ['net_income', 'equity', 'total_assets',
                                                        'revenue', 'total_debt']):
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
            earnings_stability = data['fundamentals'].get('earnings_stability', pd.Series())
            factor_scores['quality'] = self.factors['quality'].calculate_composite_quality(
                roe, roa, profit_margin, debt_to_equity, earnings_stability
            )

        # 规模因子
        if 'market_cap' in data['fundamentals']:
            factor_scores['size'] = self.factors['size'].calculate_size(
                data['fundamentals']['market_cap']
            )

        # 低波动因子
        if 'returns' in data:
            factor_scores['low_volatility'] = self.factors['low_volatility'] \
                .calculate_volatility_for_all(data['returns'])

        self.factor_scores = factor_scores
        return factor_scores

    def build_factor_portfolios(self, factor_scores: Dict[str, pd.Series],
                                prices: pd.DataFrame) -> Dict[str, Dict]:
        """为每个因子构建多空组合"""
        factor_portfolios = {}

        for factor_name, scores in factor_scores.items():
            portfolio = self.portfolio_builder.build_long_short_portfolio(scores, prices)
            factor_portfolios[factor_name] = portfolio

        return factor_portfolios

    def calculate_performance_metrics(self, returns: pd.Series) -> Dict:
        """计算绩效指标"""
        cumulative_return = (1 + returns).prod() - 1
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
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


# ============================================================================
# 配置
# ============================================================================

FACTOR_MODEL_CONFIG = {
    'factors': ['value', 'momentum', 'quality', 'size', 'low_volatility'],
    'universe_size': 1000,
    'top_quantile': 0.3,
    'bottom_quantile': 0.3,
    'weighting_method': 'equal_weight',
    'rebalance_frequency': 'monthly',
    'turnover_limit': 0.3,
}


# ============================================================================
# 示例使用
# ============================================================================

if __name__ == "__main__":
    # 示例数据
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

    # 模拟价格数据
    import yfinance as yf

    print("加载价格数据...")
    data = yf.download(symbols, start='2020-01-01', end='2024-12-31')['Adj Close']

    # 模拟基本面数据
    fundamentals = pd.DataFrame({
        'market_cap': [2500000000000, 2300000000000, 1800000000000,
                       1500000000000, 800000000000],
        'book_value': [60000000000, 150000000000, 250000000000,
                       200000000000, 150000000000],
        'earnings': [100000000000, 70000000000, 60000000000,
                     30000000000, 40000000000],
        'cash_flow': [110000000000, 80000000000, 70000000000,
                      40000000000, 45000000000],
        'total_assets': [350000000000, 500000000000, 400000000000,
                         500000000000, 200000000000],
        'revenue': [380000000000, 200000000000, 280000000000,
                    500000000000, 120000000000],
        'total_debt': [100000000000, 80000000000, 25000000000,
                       70000000000, 15000000000],
        'equity': [60000000000, 150000000000, 250000000000,
                   200000000000, 150000000000],
        'net_income': [100000000000, 70000000000, 60000000000,
                       30000000000, 40000000000]
    }, index=symbols)

    # 收益数据
    returns = data.pct_change().dropna()

    # 准备数据
    model_data = {
        'prices': data,
        'returns': returns,
        'fundamentals': fundamentals
    }

    # 创建系统
    print("\n创建因子模型系统...")
    system = FactorModelSystem(FACTOR_MODEL_CONFIG)

    # 计算因子
    print("\n计算因子得分...")
    factor_scores = system.calculate_all_factors(model_data)

    print("\n因子得分:")
    for factor_name, scores in factor_scores.items():
        print(f"\n{factor_name}:")
        print(scores.sort_values(ascending=False))

    # 构建组合
    print("\n构建因子组合...")
    portfolios = system.build_factor_portfolios(factor_scores, data)

    print("\n组合详情:")
    for factor_name, portfolio in portfolios.items():
        print(f"\n{factor_name}:")
        print(f"  Long: {portfolio['long_count']} stocks")
        print(f"  Short: {portfolio['short_count']} stocks")
        print(f"  Net positions: {len(portfolio['net'])}")

    print("\n完成!")
