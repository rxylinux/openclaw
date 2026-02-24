"""BRIDGEWATERMACROTRADER - 量化策略实现
自动从原始文档提取的Python代码
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from statsmodels.tsa.stattools import adfuller

@dataclass
class MacroIndicator:
    """宏观指标"""
    name: str
    description: str
    category: str  # 'growth', 'inflation', 'monetary', 'credit'
    current_value: float
    historical_values: pd.Series
    threshold_high: float
    threshold_low: float
    signal: float  # -1 to 1

class MacroDashboard:
    """宏观指标仪表板"""
    
    def __init__(self):
        self.indicators = {}
        
    def add_indicator(self, indicator: MacroIndicator):
        """添加指标"""
        self.indicators[indicator.name] = indicator
        
    def calculate_growth_signals(self,
                                gdp_growth: pd.Series,
                                industrial_production: pd.Series,
                                retail_sales: pd.Series,
                                employment: pd.Series) -> Dict[str, float]:
        """
        计算增长类信号
        
        指标：
        - GDP增长率
        - 工业生产指数
        - 零售销售
        - 非农就业（失业率）
        
        Returns:
            各指标信号字典
        """
        growth_signals = {}
        
        # 1. GDP增长信号
        if len(gdp_growth) > 4:
            gdp_trend = (gdp_growth.iloc[-1] - gdp_growth.iloc[-4]) / 4
            if gdp_trend > 0.02:  # 增长加速 > 2%
                gdp_signal = 1.0
            elif gdp_trend < -0.02:  # 增长放缓 < -2%
                gdp_signal = -1.0
            else:
                gdp_signal = 0.0
            growth_signals['gdp_growth'] = gdp_signal
            
        # 2. 工业生产信号
        ip_momentum = industrial_production.pct_change(12).iloc[-1]
        growth_signals['industrial_production'] = self._normalize_signal(ip_momentum, -0.05, 0.05)
        
        # 3. 零售销售信号
        retail_momentum = retail_sales.pct_change(12).iloc[-1]
        growth_signals['retail_sales'] = self._normalize_signal(retail_momentum, -0.03, 0.03)
        
        # 4. 就业信号（失业率下降 = 增长）
        if len(employment) > 12:
            unemployment_change = employment.iloc[-1] - employment.iloc[-12]
            growth_signals['employment'] = self._normalize_signal(-unemployment_change, -0.01, 0.01)
            
        # 综合增长信号
        all_signals = list(growth_signals.values())
        growth_signals['composite_growth'] = np.mean(all_signals) if all_signals else 0.0
        
        return growth_signals
        
    def calculate_inflation_signals(self,
                                  cpi: pd.Series,
                                  pce: pd.Series,
                                  ppi: pd.Series,
                                  core_inflation: pd.Series) -> Dict[str, float]:
        """
        计算通胀类信号
        
        指标：
        - CPI（消费者物价指数）
        - PCE（个人消费支出物价指数）
        - PPI（生产者物价指数）
        - 核心通胀
        
        Returns:
            各指标信号字典
        """
        inflation_signals = {}
        
        # 1. CPI信号
        if len(cpi) > 12:
            cpi_momentum = (cpi.iloc[-1] / cpi.iloc[-12]) - 1
            inflation_signals['cpi'] = self._normalize_signal(cpi_momentum, 0.01, 0.05)
            
        # 2. PCE信号（美联储首选指标）
        if len(pce) > 12:
            pce_momentum = (pce.iloc[-1] / pce.iloc[-12]) - 1
            inflation_signals['pce'] = self._normalize_signal(pce_momentum, 0.01, 0.04)
            
        # 3. PPI信号（前瞻指标）
        if len(ppi) > 12:
            ppi_momentum = (ppi.iloc[-1] / ppi.iloc[-12]) - 1
            inflation_signals['ppi'] = self._normalize_signal(ppi_momentum, 0.01, 0.05)
            
        # 4. 核心通胀信号
        if len(core_inflation) > 12:
            core_momentum = (core_inflation.iloc[-1] / core_inflation.iloc[-12]) - 1
            inflation_signals['core_inflation'] = self._normalize_signal(core_momentum, 0.01, 0.03)
            
        # 综合通胀信号
        all_signals = list(inflation_signals.values())
        inflation_signals['composite_inflation'] = np.mean(all_signals) if all_signals else 0.0
        
        return inflation_signals
        
    def calculate_monetary_signals(self,
                                  fed_funds_rate: pd.Series,
                                  yield_curve_2y10y: pd.Series,
                                  yield_curve_3m10y: pd.Series,
                                  real_rates: pd.Series) -> Dict[str, float]:
        """
        计算货币政策信号
        
        指标：
        - 联邦基金利率
        - 2年-10年期利差
        - 3个月-10年期利差
        - 实际利率
        
        Returns:
            各指标信号字典
        """
        monetary_signals = {}
        
        # 1. 联邦基金利率趋势
        if len(fed_funds_rate) > 12:
            rate_change = fed_funds_rate.iloc[-1] - fed_funds_rate.iloc[-12]
            monetary_signals['fed_funds_trend'] = self._normalize_signal(rate_change, -0.01, 0.01)
            
        # 2. 2年-10年期利差（收益率曲线）
        if len(yield_curve_2y10y) > 252:
            spread_2y10y = yield_curve_2y10y.iloc[-1]
            spread_mean = yield_curve_2y10y.iloc[-252:].mean()
            spread_std = yield_curve_2y10y.iloc[-252:].std()
            
            # 利差收窄 = 紧缩政策
            spread_z = (spread_2y10y - spread_mean) / spread_std
            monetary_signals['yield_curve_2y10y'] = -spread_z  # 负值 = 紧缩
            
        # 3. 3个月-10年期利差（领先指标）
        if len(yield_curve_3m10y) > 252:
            spread_3m10y = yield_curve_3m10y.iloc[-1]
            spread_mean = yield_curve_3m10y.iloc[-252:].mean()
            spread_std = yield_curve_3m10y.iloc[-252:].std()
            
            spread_z = (spread_3m10y - spread_mean) / spread_std
            monetary_signals['yield_curve_3m10y'] = -spread_z
            
        # 4. 实际利率
        if len(real_rates) > 252:
            real_rate_mean = real_rates.iloc[-252:].mean()
            real_rate_current = real_rates.iloc[-1]
            monetary_signals['real_rate'] = self._normalize_signal(
                real_rate_current - real_rate_mean, 
                -0.01, 0.01
            )
            
        # 综合货币政策信号
        all_signals = list(monetary_signals.values())
        monetary_signals['composite_monetary'] = np.mean(all_signals) if all_signals else 0.0
        
        return monetary_signals
        
    def calculate_credit_signals(self,
                                corporate_spreads: pd.Series,
                                high_yield_spreads: pd.Series,
                                default_rates: pd.Series) -> Dict[str, float]:
        """
        计算信贷周期信号
        
        指标：
        - 企业债信用利差
        - 高收益债利差
        - 违约率
        
        Returns:
            各指标信号字典
        """
        credit_signals = {}
        
        # 1. 企业债利差
        if len(corporate_spreads) > 126:
            spread_mean = corporate_spreads.iloc[-126:].mean()
            spread_current = corporate_spreads.iloc[-1]
            
            # 利差扩大 = 信贷收紧
            credit_signals['corporate_spreads'] = self._normalize_signal(
                spread_mean - spread_current,  # 反向：利差扩大是负面
                -0.005, 0.005
            )
            
        # 2. 高收益债利差
        if len(high_yield_spreads) > 126:
            hy_mean = high_yield_spreads.iloc[-126:].mean()
            hy_current = high_yield_spreads.iloc[-1]
            
            credit_signals['high_yield_spreads'] = self._normalize_signal(
                hy_mean - hy_current,
                -0.01, 0.01
            )
            
        # 3. 违约率
        if len(default_rates) > 12:
            default_trend = (default_rates.iloc[-1] - default_rates.iloc[-12])
            credit_signals['default_rates'] = self._normalize_signal(
                -default_trend,  # 反向
                -0.001, 0.001
            )
            
        # 综合信贷信号
        all_signals = list(credit_signals.values())
        credit_signals['composite_credit'] = np.mean(all_signals) if all_signals else 0.0
        
        return credit_signals
        
    def _normalize_signal(self,
                           value: float,
                           low_threshold: float,
                           high_threshold: float) -> float:
        """
        标准化信号到 [-1, 1]
        
        Args:
            value: 原始值
            low_threshold: 低阈值（对应-1）
            high_threshold: 高阈值（对应1）
            
        Returns:
            标准化信号
        """
        if value <= low_threshold:
            return -1.0
        elif value >= high_threshold:
            return 1.0
        else:
            # 线性映射
            return (value - low_threshold) / (high_threshold - low_threshold) * 2 - 1

class RegimeClassifier:
    """制度分类器"""
    
    def __init__(self):
        self.current_regime = None
        self.regime_history = []
        
    def classify_regime(self,
                         growth_signal: float,
                         inflation_signal: float) -> str:
        """
        基于增长/通胀矩阵分类经济制度
        
        制度矩阵：
        
                    低通胀 | 高通胀
        ---------------------------------
        高增长 |   1   |   2
        低增长 |   4   |   3
        
        1. 经济繁荣 (Growth + Low Inflation)
        2. 滞胀 (Stagflation: Low Growth + High Inflation)
        3. 经济过热 (Overheating: High Growth + High Inflation)
        4. 经济衰退 (Recession: Low Growth + Low Inflation)
        
        Args:
            growth_signal: 增长信号 [-1, 1]
            inflation_signal: 通胀信号 [-1, 1]
            
        Returns:
            制度名称
        """
        # 映射到 4 个象限
        if growth_signal > 0 and inflation_signal < 0:
            regime = 'economic_boom'  # 经济繁荣
        elif growth_signal < 0 and inflation_signal > 0:
            regime = 'stagflation'  # 滞胀
        elif growth_signal > 0 and inflation_signal > 0:
            regime = 'overheating'  # 经济过热
        else:
            regime = 'recession'  # 经济衰退
            
        self.current_regime = regime
        return regime
        
    def get_regime_allocation(self, regime: str) -> Dict[str, float]:
        """
        获取各制度下的资产配置
        
        基于 All-Weather 理念
        
        Args:
            regime: 制度名称
            
        Returns:
            各资产类别的配置权重
        """
        # All-Weather 基础配置
        base_allocation = {
            'equities': 0.30,      # 股票 30%
            'bonds': 0.40,         # 债券 40%
            'gold': 0.15,           # 黄金 15%
            'commodities': 0.10,    # 大宗商品 10%
            'cash': 0.05             # 现金 5%
        }
        
        # 根据制度调整
        regime_adjustments = {
            'economic_boom': {
                'equities': 0.50,  # 增加股票
                'bonds': 0.25,     # 减少债券
                'gold': 0.10,
                'commodities': 0.15
            },
            'stagflation': {
                'equities': 0.10,  # 大幅减少股票
                'bonds': 0.25,     # 减少债券
                'gold': 0.30,       # 大幅增加黄金
                'commodities': 0.25   # 大幅增加大宗商品
            },
            'overheating': {
                'equities': 0.25,
                'bonds': 0.20,     # 大幅减少债券（通胀）
                'gold': 0.15,
                'commodities': 0.30, # 增加大宗商品
                'cash': 0.10        # 增加现金
            },
            'recession': {
                'equities': 0.15,  # 减少股票
                'bonds': 0.55,     # 大幅增加债券
                'gold': 0.20,
                'commodities': 0.05,  # 减少大宗商品
                'cash': 0.05
            }
        }
        
        # 应用制度调整
        if regime in regime_adjustments:
            for asset, weight in regime_adjustments[regime].items():
                base_allocation[asset] = weight
                
        # 归一化
        total = sum(base_allocation.values())
        base_allocation = {k: v/total for k, v in base_allocation.items()}
        
        return base_allocation

class AssetBehaviorMap:
    """资产行为映射"""
    
    # 各制度下资产的预期表现
    REGIME_PERFORMANCE = {
        'economic_boom': {
            'equities': '⭐⭐⭐⭐⭐',  # 最佳表现
            'growth_stocks': '⭐⭐⭐⭐⭐',
            'value_stocks': '⭐⭐⭐',
            'bonds': '⭐⭐',       # 表现一般
            'treasury_bonds': '⭐⭐',
            'corporate_bonds': '⭐⭐⭐',
            'gold': '⭐',         # 表现差
            'commodities': '⭐⭐⭐',
            'energy': '⭐⭐⭐',
            'industrial_metals': '⭐⭐⭐',
            'agriculture': '⭐⭐',
            'currencies': {
                'USD': '⭐⭐',
                'EUR': '⭐⭐⭐',
                'JYP': '⭐⭐⭐',
                'EM': '⭐⭐⭐⭐'
            }
        },
        'overheating': {
            'equities': '⭐⭐⭐',
            'growth_stocks': '⭐⭐⭐',
            'value_stocks': '⭐⭐',
            'bonds': '⭐',          # 表现差（通胀）
            'treasury_bonds': '⭐',
            'corporate_bonds': '⭐⭐',
            'gold': '⭐⭐⭐⭐',     # 对冲通胀
            'commodities': '⭐⭐⭐⭐',
            'energy': '⭐⭐⭐⭐',
            'industrial_metals': '⭐⭐⭐',
            'agriculture': '⭐⭐⭐',
            'currencies': {
                'USD': '⭐⭐⭐',    # 强美元
                'EUR': '⭐',
                'JYP': '⭐',
                'EM': '⭐'
            }
        },
        'recession': {
            'equities': '⭐',         # 表现差
            'growth_stocks': '⭐',
            'value_stocks': '⭐⭐',
            'bonds': '⭐⭐⭐⭐⭐',  # 避险资产
            'treasury_bonds': '⭐⭐⭐⭐⭐',
            'corporate_bonds': '⭐⭐⭐',
            'gold': '⭐⭐⭐',
            'commodities': '⭐',
            'energy': '⭐',
            'industrial_metals': '⭐⭐',
            'agriculture': '⭐⭐',
            'currencies': {
                'USD': '⭐⭐⭐⭐',
                'EUR': '⭐⭐',
                'JYP': '⭐⭐⭐',
                'EM': '⭐'
            }
        },
        'stagflation': {
            'equities': '⭐',         # 最差
            'growth_stocks': '⭐',
            'value_stocks': '⭐⭐',
            'bonds': '⭐',          # 最差（实际负收益）
            'treasury_bonds': '⭐',
            'corporate_bonds': '⭐',
            'gold': '⭐⭐⭐⭐⭐',  # 最佳表现
            'commodities': '⭐⭐⭐',
            'energy': '⭐⭐⭐⭐',
            'industrial_metals': '⭐⭐⭐',
            'agriculture': '⭐⭐⭐',
            'currencies': {
                'USD': '⭐⭐⭐⭐',
                'EUR': '⭐',
                'JYP': '⭐',
                'EM': '⭐'
            }
        }
    }
    
    def get_expected_performance(self,
                               regime: str,
                               asset_class: str) -> str:
        """
        获取资产在特定制度下的预期表现
        
        Args:
            regime: 制度
            asset_class: 资产类别
            
        Returns:
            表现评级（星级）
        """
        if regime in self.REGIME_PERFORMANCE:
            regime_map = self.REGIME_PERFORMANCE[regime]
            
            if asset_class in regime_map:
                return regime_map[asset_class]
            elif asset_class == 'currencies':
                # 默认返回美元表现
                return regime_map['currencies']['USD']
            else:
                return '⭐⭐⭐'  # 默认中等
        else:
            return '⭐⭐⭐'

class MacroSignalBuilder:
    """宏观信号构建器"""
    
    def __init__(self):
        self.dashboard = MacroDashboard()
        self.regime_classifier = RegimeClassifier()
        self.asset_behavior = AssetBehaviorMap()
        
    def build_composite_signals(self,
                                macro_data: Dict) -> Dict:
        """
        构建综合宏观信号
        
        Args:
            macro_data: 宏观数据字典 {
                'gdp_growth': pd.Series,
                'cpi': pd.Series,
                'fed_funds_rate': pd.Series,
                ...
            }
            
        Returns:
            综合信号字典
        """
        # 1. 计算各类指标
        growth_signals = self.dashboard.calculate_growth_signals(
            macro_data['gdp_growth'],
            macro_data['industrial_production'],
            macro_data['retail_sales'],
            macro_data['employment']
        )
        
        inflation_signals = self.dashboard.calculate_inflation_signals(
            macro_data['cpi'],
            macro_data['pce'],
            macro_data['ppi'],
            macro_data['core_inflation']
        )
        
        monetary_signals = self.dashboard.calculate_monetary_signals(
            macro_data['fed_funds_rate'],
            macro_data['yield_curve_2y10y'],
            macro_data['yield_curve_3m10y'],
            macro_data['real_rates']
        )
        
        credit_signals = self.dashboard.calculate_credit_signals(
            macro_data['corporate_spreads'],
            macro_data['high_yield_spreads'],
            macro_data['default_rates']
        )
        
        # 2. 综合增长和通胀信号
        composite_growth = growth_signals['composite_growth']
        composite_inflation = inflation_signals['composite_inflation']
        
        # 3. 分类制度
        current_regime = self.regime_classifier.classify_regime(
            composite_growth,
            composite_inflation
        )
        
        # 4. 构建资产配置信号
        allocation = self.regime_classifier.get_regime_allocation(current_regime)
        
        # 5. 战术性调整（基于信号强度）
        tactical_adjustment = self._calculate_tactical_overlay(
            growth_signals,
            inflation_signals,
            monetary_signals,
            credit_signals
        )
        
        # 6. 应用战术性调整
        adjusted_allocation = {}
        for asset, base_weight in allocation.items():
            adjustment = tactical_adjustment.get(asset, 0.0)
            adjusted_allocation[asset] = max(0, min(1, base_weight + adjustment))
        
        # 归一化
        total = sum(adjusted_allocation.values())
        adjusted_allocation = {k: v/total for k, v in adjusted_allocation.items()}
        
        return {
            'current_regime': current_regime,
            'growth_signal': composite_growth,
            'inflation_signal': composite_inflation,
            'base_allocation': allocation,
            'tactical_adjustment': tactical_adjustment,
            'final_allocation': adjusted_allocation,
            'growth_signals': growth_signals,
            'inflation_signals': inflation_signals,
            'monetary_signals': monetary_signals,
            'credit_signals': credit_signals
        }
        
    def _calculate_tactical_overlay(self,
                                     growth_signals: Dict,
                                     inflation_signals: Dict,
                                     monetary_signals: Dict,
                                     credit_signals: Dict) -> Dict:
        """
        计算战术性调整
        
        当信号强度高时，进一步调整配置
        
        Args:
            各类信号
            
        Returns:
            调整量字典
        """
        adjustments = {}
        
        # 1. 基于增长信号的调整
        strong_growth = growth_signals['composite_growth'] > 0.5
        weak_growth = growth_signals['composite_growth'] < -0.5
        
        if strong_growth:
            # 强增长 → 增加股票、减少债券
            adjustments['equities'] = 0.10
            adjustments['bonds'] = -0.10
        elif weak_growth:
            # 弱增长 → 减少股票、增加债券
            adjustments['equities'] = -0.10
            adjustments['bonds'] = 0.10
            
        # 2. 基于通胀信号的调整
        high_inflation = inflation_signals['composite_inflation'] > 0.5
        low_inflation = inflation_signals['composite_inflation'] < -0.5
        
        if high_inflation:
            # 高通胀 → 增加黄金和大宗商品、减少债券
            adjustments['gold'] = 0.10
            adjustments['commodities'] = 0.10
            adjustments['bonds'] = -0.10
        elif low_inflation:
            # 低通胀 → 减少黄金和大宗商品
            adjustments['gold'] = -0.05
            adjustments['commodities'] = -0.05
            
        # 3. 基于货币政策的调整
        tightening = monetary_signals['composite_monetary'] > 0.5
        easing = monetary_signals['composite_monetary'] < -0.5
        
        if tightening:
            # 紧缩 → 增加现金、减少风险资产
            adjustments['cash'] = 0.10
            adjustments['equities'] = -0.05
        elif easing:
            # 宽松 → 减少现金、增加风险资产
            adjustments['cash'] = -0.05
            adjustments['equities'] = 0.05
            
        # 4. 基于信贷信号的调整
        credit_tightening = credit_signals['composite_credit'] > 0.3
        credit_easing = credit_signals['composite_credit'] < -0.3
        
        if credit_tightening:
            # 信贷收紧 → 减少企业债
            adjustments['corporate_bonds'] = -0.10
        elif credit_easing:
            # 信贷放松 → 增加企业债
            adjustments['corporate_bonds'] = 0.10
            
        return adjustments

class AllWeatherPortfolio:
    """全天候投资组合"""
    
    def __init__(self, capital: float = 1000000):
        self.capital = capital
        
        # 资产类别和对应ETF
        self.assets = {
            'equities': {
                'etf': 'SPY',
                'name': 'US Equities (S&P 500)',
                'volatility': 0.15
            },
            'bonds': {
                'etf': 'TLT',
                'name': 'Long-Term US Treasuries',
                'volatility': 0.08
            },
            'gold': {
                'etf': 'GLD',
                'name': 'Gold',
                'volatility': 0.15
            },
            'commodities': {
                'etf': 'DBC',
                'name': 'Commodity Index',
                'volatility': 0.20
            },
            'cash': {
                'etf': 'SHY',
                'name': 'Short-Term Treasuries',
                'volatility': 0.02
            }
        }
        
    def calculate_base_allocation(self) -> Dict[str, float]:
        """
        计算All-Weather基础配置
        
        目标：在任何经济环境下都有正收益
        
        Returns:
            各资产权重
        """
        # 风险平价配置
        # 目标波动率 = 10%
        target_volatility = 0.10
        
        # 计算各资产的风险贡献权重
        weights = {}
        total_inverse_vol = 0
        
        for asset, info in self.assets.items():
            vol = info['volatility']
            inverse_vol = 1.0 / vol
            total_inverse_vol += inverse_vol
            
        # 风险平价权重
        for asset, info in self.assets.items():
            vol = info['volatility']
            weight = (1.0 / vol) / total_inverse_vol
            weights[asset] = weight
            
        # 调整为目标波动率
        current_vol = np.sqrt(sum([
            (weights[asset] * self.assets[asset]['volatility']) ** 2
            for asset in weights
        ]))
        
        scale_factor = target_volatility / current_vol
        weights = {k: v * scale_factor for k, v in weights.items()}
        
        # 归一化
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        return weights
        
    def get_etf_tickers(self, allocation: Dict[str, float]) -> Dict[str, float]:
        """
        获取ETF配置
        
        Args:
            allocation: 各资产权重
            
        Returns:
            {ETF代码: 权重}
        """
        etf_allocation = {}
        
        for asset, weight in allocation.items():
            if asset in self.assets:
                etf = self.assets[asset]['etf']
                etf_allocation[etf] = weight
                
        return etf_allocation

class TacticalOverlay:
    """战术性覆盖"""
    
    def __init__(self,
                 signal_threshold: float = 0.5,    # 信号阈值
                 max_tilt: float = 0.20):          # 最大倾斜 20%
        self.signal_threshold = signal_threshold
        self.max_tilt = max_tilt
        
    def calculate_tactical_allocation(self,
                                    base_allocation: Dict[str, float],
                                    macro_signals: Dict) -> Dict[str, float]:
        """
        计算战术性配置
        
        Args:
            base_allocation: 基础配置
            macro_signals: 宏观信号 {
                'regime': 'economic_boom',
                'growth_signal': 0.8,
                'inflation_signal': 0.3,
                'monetary_signal': -0.5
            }
            
        Returns:
            战术性调整后的配置
        """
        regime = macro_signals['regime']
        growth = macro_signals['growth_signal']
        inflation = macro_signals['inflation_signal']
        monetary = macro_signals['monetary_signal']
        
        # 调整量
        adjustments = {asset: 0.0 for asset in base_allocation}
        
        # 1. 制度调整
        regime_adjustments = self._get_regime_adjustments(regime)
        for asset, adj in regime_adjustments.items():
            adjustments[asset] += adj
            
        # 2. 信号强度调整
        if abs(growth) > self.signal_threshold:
            tilt = self.max_tilt * (growth / 2.0)  # 归一化到 [-1, 1]
            adjustments['equities'] += tilt
            adjustments['bonds'] -= tilt
            
        if abs(inflation) > self.signal_threshold:
            tilt = self.max_tilt * (inflation / 2.0)
            adjustments['gold'] += tilt
            adjustments['commodities'] += tilt
            adjustments['bonds'] -= tilt
            
        if abs(monetary) > self.signal_threshold:
            tilt = self.max_tilt * (monetary / 2.0)
            adjustments['equities'] += tilt  # 宽松 → 增加风险资产
            adjustments['cash'] -= tilt
            
        # 3. 应用调整
        tactical_allocation = {}
        for asset, base_weight in base_allocation.items():
            adjustment = adjustments[asset]
            tactical_allocation[asset] = max(0, min(1, base_weight + adjustment))
            
        # 4. 归一化
        total = sum(tactical_allocation.values())
        tactical_allocation = {k: v/total for k, v in tactical_allocation.items()}
        
        return tactical_allocation
        
    def _get_regime_adjustments(self, regime: str) -> Dict[str, float]:
        """获取制度调整"""
        adjustments = {
            'economic_boom': {
                'equities': 0.10,
                'bonds': -0.05,
                'gold': -0.05
            },
            'overheating': {
                'bonds': -0.15,
                'gold': 0.05,
                'commodities': 0.10,
                'cash': 0.05
            },
            'recession': {
                'equities': -0.10,
                'bonds': 0.15,
                'gold': 0.05,
                'cash': 0.05
            },
            'stagflation': {
                'equities': -0.20,
                'bonds': -0.10,
                'gold': 0.20,
                'commodities': 0.15,
                'cash': 0.10
            }
        }
        
        return adjustments.get(regime, {})

class InstrumentSelector:
    """工具选择器"""
    
    # ETF 映射
    ETF_MAP = {
        # 股票
        'US_equities': 'SPY',          # S&P 500
        'US_growth': 'VUG',            # US Growth
        'US_value': 'VTV',             # US Value
        'emerging_markets': 'EEM',     # EM Markets
        'developed_international': 'VEA', # Developed International
        
        # 债券
        'long_term_treasuries': 'TLT',    # 20+ Year Treasuries
        'intermediate_treasuries': 'IEF', # 7-10 Year Treasuries
        'short_term_treasuries': 'SHY',  # 1-3 Year Treasuries
        'corporate_bonds': 'LQD',       # Investment Grade Corporate
        'high_yield': 'HYG',             # High Yield Corporate
        'emerging_bonds': 'EMB',          # EM Sovereign Debt
        
        # 大宗商品
        'gold': 'GLD',                   # Gold
        'silver': 'SLV',                 # Silver
        'oil': 'USO',                   # Crude Oil
        'energy': 'XLE',                 # Energy Sector
        'industrial_metals': 'DBB',      # Industrial Metals
        'agriculture': 'DBA',            # Agriculture
        
        # 货币
        'USD_index': 'UUP',              # US Dollar Index
        'euro': 'FXE',                  # Euro
        'japanese_yen': 'FXY',           # Japanese Yen
        'em_currencies': 'CEW'            # EM Currencies
    }
    
    # 期货映射（简化版）
    FUTURE_MAP = {
        # 股指期货
        'S&P_500': 'ES',
        'NASDAQ_100': 'NQ',
        'DOW_JONES': 'YM',
        'EURO_STOXX_50': 'FESX',
        'FTSE_100': 'Z',
        'NIKKEI_225': 'NKD',
        'HSI': 'HSI',
        
        # 利率期货
        '10Y_Treasury': 'ZN',
        '5Y_Treasury': 'ZF',
        '2Y_Treasury': 'ZT',
        'Eurodollar': 'GE',
        'Euribor': 'FGBL',
        
        # 大宗商品期货
        'Gold': 'GC',
        'Silver': 'SI',
        'Crude_Oil': 'CL',
        'Natural_Gas': 'NG',
        'Corn': 'ZC',
        'Wheat': 'ZW',
        'Soybeans': 'ZS',
        
        # 货币期货
        'EUR_USD': '6E',
        'USD_JPY': '6J',
        'GBP_USD': '6B',
        'USD_CHF': '6S'
    }
    
    def select_instruments(self,
                           allocation: Dict[str, float],
                           use_futures: bool = False) -> Dict[str, float]:
        """
        选择交易工具
        
        Args:
            allocation: 各资产类别的配置权重
            use_futures: 是否使用期货
            
        Returns:
            具体工具配置
        """
        instrument_allocation = {}
        
        # 资产类别到工具的映射
        asset_mapping = {
            'equities': 'US_equities',
            'bonds': 'long_term_treasuries',
            'gold': 'gold',
            'commodities': 'energy',  # 简化：用能源代表大宗商品
            'cash': 'short_term_treasuries'
        }
        
        for asset, weight in allocation.items():
            if asset in asset_mapping:
                mapping_key = asset_mapping[asset]
                
                if use_futures:
                    # 使用期货
                    if mapping_key in self.FUTURE_MAP:
                        instrument = self.FUTURE_MAP[mapping_key]
                        instrument_allocation[instrument] = weight
                else:
                    # 使用ETF
                    if mapping_key in self.ETF_MAP:
                        instrument = self.ETF_MAP[mapping_key]
                        instrument_allocation[instrument] = weight
                        
        return instrument_allocation

class RebalancingStrategy:
    """再平衡策略"""
    
    def __init__(self,
                 rebalance_frequency: str = 'monthly',
                 threshold_drift: float = 0.05,   # 5% 偏离阈值
                 min_holding_period: int = 20):  # 最小持仓周期
        self.rebalance_frequency = rebalance_frequency
        self.threshold_drift = threshold_drift
        self.min_holding_period = min_holding_period
        
        self.last_rebalance_date = None
        self.current_allocation = {}
        
    def should_rebalance(self,
                          current_date: pd.Timestamp,
                          target_allocation: Dict[str, float]) -> Tuple[bool, str]:
        """
        判断是否应该再平衡
        
        Args:
            current_date: 当前日期
            target_allocation: 目标配置
            
        Returns:
            (是否再平衡, 原因）
        """
        reasons = []
        
        # 1. 日历再平衡
        calendar_trigger = False
        if self.rebalance_frequency == 'monthly':
            if self.last_rebalance_date is None or \
               current_date.month != self.last_rebalance_date.month or \
               current_date.year != self.last_rebalance_date.year:
                calendar_trigger = True
                reasons.append('calendar_monthly')
                
        elif self.rebalance_frequency == 'quarterly':
            quarter = (current_date.month - 1) // 3 + 1
            if self.last_rebalance_date is None:
                last_quarter = 0
            else:
                last_quarter = (self.last_rebalance_date.month - 1) // 3 + 1
                
            if quarter != last_quarter or \
               current_date.year != self.last_rebalance_date.year:
                calendar_trigger = True
                reasons.append('calendar_quarterly')
                
        # 2. 阈值再平衡
        threshold_trigger = False
        if self.current_allocation:
            for asset, target_weight in target_allocation.items():
                if asset in self.current_allocation:
                    current_weight = self.current_allocation[asset]
                    drift = abs(current_weight - target_weight)
                    
                    if drift > self.threshold_drift:
                        threshold_trigger = True
                        reasons.append(f'threshold_{asset}_{drift:.2%}')
                        break
                        
        should_rebalance = calendar_trigger or threshold_trigger
        
        if should_rebalance:
            reason = ', '.join(reasons)
        else:
            reason = 'none'
            
        return should_rebalance, reason
        
    def execute_rebalance(self,
                          target_allocation: Dict[str, float],
                          current_allocation: Dict[str, float],
                          capital: float) -> Dict[str, float]:
        """
        执行再平衡
        
        Args:
            target_allocation: 目标配置
            current_allocation: 当前配置
            capital: 总资本
            
        Returns:
            交易列表 {instrument: trade_amount}
        """
        trades = {}
        
        for instrument in target_allocation:
            target_weight = target_allocation[instrument]
            current_weight = current_allocation.get(instrument, 0.0)
            
            # 计算交易金额
            trade_amount = (target_weight - current_weight) * capital
            
            # 只交易超过最小阈值的金额
            min_trade = capital * 0.01  # 1% 最小交易
            if abs(trade_amount) >= min_trade:
                trades[instrument] = trade_amount
                
        return trades

class CorrelationRegimeMonitor:
    """相关性制度监控器"""
    
    def __init__(self,
                 window: int = 126):  # 6个月窗口
        self.window = window
        self.correlation_history = {}
        
    def calculate_rolling_correlation(self,
                                     returns: pd.DataFrame,
                                     window: int = None) -> pd.DataFrame:
        """
        计算滚动相关性
        
        Args:
            returns: 收益数据框
            window: 滚动窗口
            
        Returns:
            相关性矩阵序列
        """
        if window is None:
            window = self.window
            
        correlation_series = []
        
        for i in range(window, len(returns)):
            window_returns = returns.iloc[i-window:i]
            corr_matrix = window_returns.corr()
            correlation_series.append(corr_matrix)
            
        return correlation_series
        
    def detect_correlation_breakdown(self,
                                     current_correlation: pd.DataFrame,
                                     historical_correlations: List[pd.DataFrame]) -> Dict:
        """
        检测相关性制度变化
        
        制度变化信号：
        1. 平均相关性显著增加（危机时所有资产趋同）
        2. 特定资产相关性模式改变
        
        Args:
            current_correlation: 当前相关性矩阵
            historical_correlations: 历史相关性列表
            
        Returns:
            检测结果
        """
        # 计算平均相关性
        current_avg_correlation = current_correlation.abs().mean().mean()
        
        historical_avgs = [corr.abs().mean().mean() for corr in historical_correlations]
        historical_mean = np.mean(historical_avgs)
        historical_std = np.std(historical_avgs)
        
        # 判断异常
        z_score = (current_avg_correlation - historical_mean) / historical_std
        
        is_breakdown = abs(z_score) > 2.0  # 2个标准差
        
        return {
            'correlation_breakdown': is_breakdown,
            'current_avg_correlation': current_avg_correlation,
            'historical_mean': historical_mean,
            'z_score': z_score,
            'crisis_warning': is_breakdown and z_score > 0  # 相关性显著增加
        }
        
    def suggest_hedging_adjustment(self,
                                   correlation_analysis: Dict) -> Dict:
        """
        基于相关性分析建议对冲调整
        
        Args:
            correlation_analysis: 相关性分析结果
            
        Returns:
            对冲调整建议
        """
        if not correlation_analysis['crisis_warning']:
            return {'adjustment': 'none'}
            
        # 危机模式：相关性显著增加
        # 建议：
        # 1. 降低仓位
        # 2. 增加现金
        # 3. 使用衍生品对冲
        
        return {
            'adjustment': 'reduce_exposure',
            'actions': [
                'reduce_position_size_by_20pct',
                'increase_cash_allocation_to_15pct',
                'consider_options_hedges'
            ]
        }

class GeopoliticalRiskFramework:
    """地缘政治风险框架"""
    
    # 风险事件类别
    RISK_CATEGORIES = {
        'elections': {
            'weight': 0.3,
            'assets_affected': ['equities', 'bonds', 'currencies']
        },
        'wars_conflicts': {
            'weight': 0.5,
            'assets_affected': ['equities', 'commodities', 'currencies']
        },
        'trade_disputes': {
            'weight': 0.4,
            'assets_affected': ['equities', 'industrial_metals']
        },
        'sanctions': {
            'weight': 0.4,
            'assets_affected': ['equities', 'currencies', 'commodities']
        },
        'policy_changes': {
            'weight': 0.2,
            'assets_affected': ['equities', 'bonds']
        }
    }
    
    def __init__(self):
        self.active_events = []
        self.risk_score = 0.0
        
    def add_event(self,
                 event_type: str,
                 severity: float,  # 0-1
                 expected_impact: float,  # 预期影响
                 start_date: pd.Timestamp,
                 end_date: pd.Timestamp = None):
        """
        添加风险事件
        
        Args:
            event_type: 事件类型
            severity: 严重程度
            expected_impact: 预期影响
            start_date: 开始日期
            end_date: 结束日期
        """
        event = {
            'type': event_type,
            'severity': severity,
            'expected_impact': expected_impact,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True
        }
        
        self.active_events.append(event)
        
    def calculate_risk_score(self) -> float:
        """
        计算综合风险得分
        
        Returns:
            风险得分 [0, 1]
        """
        if not self.active_events:
            return 0.0
            
        total_risk = 0.0
        total_weight = 0.0
        
        for event in self.active_events:
            if not event['is_active']:
                continue
                
            category_weight = self.RISK_CATEGORIES[event['type']]['weight']
            event_risk = event['severity'] * event['expected_impact'] * category_weight
            
            total_risk += event_risk
            total_weight += category_weight
            
        self.risk_score = total_risk / total_weight if total_weight > 0 else 0.0
        
        return self.risk_score
        
    def suggest_risk_adjustment(self) -> Dict:
        """
        基于风险得分建议调整
        
        Returns:
            调整建议
        """
        risk_score = self.calculate_risk_score()
        
        if risk_score < 0.3:
            # 低风险
            return {
                'risk_level': 'low',
                'adjustment': 'maintain_base_allocation',
                'cash_buffer': 0.05  # 5% 现金缓冲
            }
        elif risk_score < 0.6:
            # 中等风险
            return {
                'risk_level': 'medium',
                'adjustment': 'reduce_exposure_slightly',
                'cash_buffer': 0.10,  # 10% 现金
                'target_reductions': {
                    'equities': -0.05,
                    'emerging_markets': -0.10
                }
            }
        else:
            # 高风险
            return {
                'risk_level': 'high',
                'adjustment': 'reduce_exposure_significantly',
                'cash_buffer': 0.20,  # 20% 现金
                'target_reductions': {
                    'equities': -0.15,
                    'emerging_markets': -0.20,
                    'corporate_bonds': -0.10
                },
                'safe_havens_increase': {
                    'treasury_bonds': 0.15,
                    'gold': 0.10,
                    'usd': 0.10
                }
            }

class MacroTradingSystem:
    """完整宏观交易系统"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 配置字典 {
                'capital': 总资本,
                'base_allocation': 基础配置,
                'rebalance_frequency': 再平衡频率,
                ...
            }
        """
        # 初始化各个模块
        self.dashboard = MacroDashboard()
        self.regime_classifier = RegimeClassifier()
        self.signal_builder = MacroSignalBuilder()
        self.all_weather = AllWeatherPortfolio(config['capital'])
        self.tactical_overlay = TacticalOverlay()
        self.instrument_selector = InstrumentSelector()
        self.rebalancer = RebalancingStrategy(
            rebalance_frequency=config.get('rebalance_frequency', 'monthly')
        )
        self.correlation_monitor = CorrelationRegimeMonitor()
        self.geopolitical_framework = GeopoliticalRiskFramework()
        
        self.current_allocation = {}
        self.last_rebalance_date = None
        
    def run_daily_analysis(self, macro_data: Dict, date: pd.Timestamp) -> Dict:
        """
        运行每日分析
        
        Args:
            macro_data: 宏观数据
            date: 当前日期
            
        Returns:
            分析结果
        """
        # 1. 更新宏观数据
        self._update_macro_data(macro_data)
        
        # 2. 构建综合信号
        signals = self.signal_builder.build_composite_signals(macro_data)
        
        # 3. 检测制度
        current_regime = signals['current_regime']
        
        # 4. 计算目标配置
        base_allocation = self.all_weather.calculate_base_allocation()
        tactical_allocation = self.tactical_overlay.calculate_tactical_allocation(
            base_allocation,
            signals
        )
        
        # 5. 应用地缘政治调整
        geo_adjustment = self.geopolitical_framework.suggest_risk_adjustment()
        
        if geo_adjustment['risk_level'] == 'high':
            # 高风险：应用避险资产增加
            for asset, increase in geo_adjustment['safe_havens_increase'].items():
                if asset in tactical_allocation:
                    tactical_allocation[asset] += increase
                    
            # 减少风险资产
            for asset, reduction in geo_adjustment['target_reductions'].items():
                if asset in tactical_allocation:
                    tactical_allocation[asset] += reduction
                    
            # 增加现金
            if 'cash' not in tactical_allocation:
                tactical_allocation['cash'] = geo_adjustment['cash_buffer']
            else:
                tactical_allocation['cash'] += geo_adjustment['cash_buffer']
                    
        # 归一化配置
        total = sum(tactical_allocation.values())
        target_allocation = {k: v/total for k, v in tactical_allocation.items()}
        
        # 6. 选择工具
        instrument_allocation = self.instrument_selector.select_instruments(
            target_allocation,
            use_futures=config.get('use_futures', False)
        )
        
        # 7. 检查是否需要再平衡
        should_rebalance, reason = self.rebalancer.should_rebalance(
            date, instrument_allocation
        )
        
        return {
            'date': date,
            'current_regime': current_regime,
            'growth_signal': signals['growth_signal'],
            'inflation_signal': signals['inflation_signal'],
            'target_allocation': target_allocation,
            'instrument_allocation': instrument_allocation,
            'should_rebalance': should_rebalance,
            'rebalance_reason': reason,
            'geopolitical_risk_level': geo_adjustment['risk_level']
        }
        
    def _update_macro_data(self, macro_data: Dict):
        """更新宏观数据"""
        # GDP信号
        self.dashboard.calculate_growth_signals(
            macro_data['gdp_growth'],
            macro_data['industrial_production'],
            macro_data['retail_sales'],
            macro_data['employment']
        )
        
        # 通胀信号
        self.dashboard.calculate_inflation_signals(
            macro_data['cpi'],
            macro_data['pce'],
            macro_data['ppi'],
            macro_data['core_inflation']
        )
        
        # 货币政策信号
        self.dashboard.calculate_monetary_signals(
            macro_data['fed_funds_rate'],
            macro_data['yield_curve_2y10y'],
            macro_data['yield_curve_3m10y'],
            macro_data['real_rates']
        )
        
        # 信贷信号
        self.dashboard.calculate_credit_signals(
            macro_data['corporate_spreads'],
            macro_data['high_yield_spreads'],
            macro_data['default_rates']
        )
        
    def execute_rebalance(self,
                         target_allocation: Dict[str, float],
                         capital: float) -> Dict:
        """
        执行再平衡
        
        Args:
            target_allocation: 目标配置
            capital: 总资本
            
        Returns:
            交易列表
        """
        trades = self.rebalancer.execute_rebalance(
            target_allocation,
            self.current_allocation,
            capital
        )
        
        # 更新当前配置
        self.current_allocation = target_allocation
        self.last_rebalance_date = pd.Timestamp.now()
        
        return trades

MACRO_TRADING_CONFIG = {
    # 资本和风险
    'capital': 100000000,                # 1亿美元
    'max_drawdown': 0.15,                # 最大回撤 15%
    'target_volatility': 0.12,          # 目标波动率 12%
    
    # 再平衡
    'rebalance_frequency': 'monthly',      # 月度再平衡
    'threshold_drift': 0.05,             # 5% 偏离阈值
    'min_trade_size': 100000,             # 最小交易规模 10万
    
    # 制度检测
    'regime_change_threshold': 0.3,       # 制度变化阈值
    'regime_confirmation_days': 10,       # 制度确认天数
    
    # 战术性调整
    'signal_threshold': 0.5,              # 信号阈值
    'max_tilt': 0.20,                   # 最大倾斜 20%
    
    # 地缘政治
    'max_geopolitical_cash': 0.20,        # 最大地缘政治现金比例
    'geopolitical_adjustment_factor': 1.5, # 地缘政治调整因子
    
    # 工具选择
    'use_futures': True,                  # 使用期货
    'prefer_etf': False,                  # 优先使用ETF
    
    # 相关性监控
    'correlation_window': 126,             # 6个月窗口
    'correlation_breakdown_threshold': 2.0  # 相关性崩盘阈值（标准差）
}

MACRO_TRADING_TARGETS = {
    # 收益
    'target_annual_return': 0.08,         # 目标年化收益 8%
    'target_sharpe': 1.5,                # 目标夏普比率 1.5
    
    # 风险
    'max_drawdown': 0.15,                 # 最大回撤 15%
    'max_volatility': 0.12,               # 最大波动率 12%
    
    # 制度适应
    'regime_detection_accuracy': 0.8,      # 制度检测准确率 80%
    'regime_adaptation_speed': 10,          # 制度适应速度（天）
    
    # 交易效率
    'max_turnover': 0.3,                   # 最大换手率 30%
    'min_holding_period': 30,              # 最小持仓周期 30天
    
    # All-Weather 目标
    'positive_return_in_all_regimes': True,  # 所有制度下正收益
    'min_regime_return': 0.02,            # 最小制度收益 2%
}