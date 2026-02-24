# Two Sigma风险管理系统Python实现指南

## 完整实现架构

### 主要组件

1. **KellyCriterion** - 主要类
2. **AdaptivePositionSizer** - 主要类
3. **from** - 主要类

## 代码实现

### 代码块 1

```python
import numpy as np
from typing import Tuple

class KellyCriterion:
    """Kelly Criterion 仓位管理"""
    
    def __init__(self, 
                 win_rate: float = 0.55,
                 avg_win: float = 1.0,
                 avg_loss: float = 1.0,
                 max_leverage: float = 2.0):
        """
        Args:
            win_rate: 胜率 (0-1)
            avg_win: 平均盈利 (如 1.0 表示 +100%)
            avg_loss: 平均亏损 (如 1.0 表示 -100%)
            max_leverage: 最大杠杆倍数
        """
        self.win_rate = win_rate
        self.avg_win = avg_win
        self.avg_loss = avg_loss
        self.max_leverage = max_leverage
        
    def calculate_kelly_fraction(self) -> float:
        """计算 Kelly 仓位比例"""
        p = self.win_rate
        b = self.avg_win / self.avg_loss  # 赔率
        
        # Kelly 公式: f = p - q/b
        kelly_f = p - (1 - p) / b
        
        return max(0, min(kelly_f, self.max_leverage))
        
    def fractional_kelly(self, 
                        fraction: float = 0.5) -> float:
        """部分 Kelly (降低风险)"""
        full_kelly = self.calculate_kelly_fraction()
        return full_kelly * fraction

```

### 代码块 2

```python
class AdaptivePositionSizer:
    """自适应仓位管理 (基于波动率)"""
    
    def __init__(self, 
                 base_risk_per_trade: float = 0.02,
                 volatility_window: int = 20):
        self.base_risk = base_risk_per_trade
        self.vol_window = volatility_window
        
    def calculate_position_size(self,
                                capital: float,
                                current_volatility: float,
                                avg_volatility: float) -> float:
        """
        根据当前波动率调整仓位
        
        Args:
            capital: 总资本
            current_volatility: 当前波动率
            avg_volatility: 平均波动率
            
        Returns:
            仓位金额
        """
        # 波动率调整因子
        vol_ratio = current_volatility / avg_volatility
        
        # 高波动时减仓，低波动时加仓
        adjusted_risk = self.base_risk / vol_ratio
        
        position_size = capital * adjusted_risk
        
        return position_size

```

### 代码块 3

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class StopLossType(Enum):
    """止损类型"""
    FIXED = "fixed"                  # 固定止损
    TRAILING = "trailing"            # 追踪止损
    VOLATILITY_ADJUSTED = "vol_adj"   # 波动率调整止损
    TIME_BASED = "time_based"         # 时间止损

@dataclass
class StopLossRule:
    """止损规则"""
    stop_type: StopLossType
    threshold: float                # 止损阈值
    time_limit: Optional[int] = None  # 时间限制（天）
    
class StopLossManager:
    """止损管理器"""
    
    def __init__(self):
        self.stop_rules = {}
        
    def set_stop_loss(self,
                     position_id: str,
                     entry_price: float,
                     stop_rule: StopLossRule,
                     atr: Optional[float] = None):
        """设置止损"""
        self.stop_rules[position_id] = {
            'entry_price': entry_price,
            'rule': stop_rule,
            'atr': atr,
            'trailing_high': entry_price  # 用于追踪止损
        }
        
    def check_stop_loss(self,
                       position_id: str,
                       current_price: float,
                       days_held: int) -> Tuple[bool, float]:
        """
        检查是否触发止损
        
        Returns:
            (是否触发, 止损价格)
        """
        if position_id not in self.stop_rules:
            return False, 0.0
            
        rule = self.stop_rules[position_id]
        entry = rule['entry_price']
        stop_rule = rule['rule']
        trailing_high = rule['trailing_high']
        
        # 更新追踪高点
        if current_price > trailing_high:
            self.stop_rules[position_id]['trailing_high'] = current_price
            
        if stop_rule.stop_type == StopLossType.FIXED:
            # 固定止损
            stop_price = entry * (1 - stop_rule.threshold)
            should_stop = current_price <= stop_price
            
        elif stop_rule.stop_type == StopLossType.TRAILING:
            # 追踪止损
            stop_price = trailing_high * (1 - stop_rule.threshold)
            should_stop = current_price <= stop_price
            
        elif stop_rule.stop_type == StopLossType.VOLATILITY_ADJUSTED:
            # 波动率调整止损 (2x ATR)
            atr = rule['atr']
            stop_price = entry - 2 * atr
            should_stop = current_price <= stop_price
            
        elif stop_rule.stop_type == StopLossType.TIME_BASED:
            # 时间止损
            should_stop = days_held >= stop_rule.time_limit
            stop_price = current_price
            
        return should_stop, stop_price

```

### 代码块 4

```python
class DrawdownController:
    """最大回撤控制器"""
    
    def __init__(self,
                 max_drawdown: float = 0.20,      # 最大回撤 20%
                 warning_level: float = 0.15,       # 警告级别 15%
                 recovery_mode: bool = False):
        self.max_drawdown = max_drawdown
        self.warning_level = warning_level
        self.recovery_mode = recovery_mode
        
        self.peak_value = 0.0
        self.current_value = 0.0
        
    def update_value(self, current_value: float) -> Dict:
        """
        更新当前价值并检查回撤
        
        Returns:
            状态字典 {
                'drawdown': 当前回撤,
                'peak': 历史高点,
                'action': 需要采取的行动
            }
        """
        self.current_value = current_value
        
        # 更新历史高点
        if current_value > self.peak_value:
            self.peak_value = current_value
            self.recovery_mode = False
            
        # 计算回撤
        drawdown = (self.peak_value - current_value) / self.peak_value
        
        # 决定行动
        action = 'none'
        if drawdown >= self.max_drawdown:
            action = 'halt_trading'  # 停止交易
        elif drawdown >= self.warning_level:
            action = 'reduce_position'  # 减仓
        elif self.recovery_mode and drawdown < self.warning_level / 2:
            action = 'resume_normal'  # 恢复正常
            
        return {
            'drawdown': drawdown,
            'peak': self.peak_value,
            'action': action
        }
        
    def get_position_multiplier(self, drawdown: float) -> float:
        """
        根据回撤调整仓位倍数
        
        回撤越大，仓位越小
        """
        if drawdown >= self.max_drawdown:
            return 0.0
        elif drawdown >= self.warning_level:
            # 线性递减
            return 1.0 - (drawdown - self.warning_level) / (self.max_drawdown - self.warning_level)
        else:
            return 1.0

```

### 代码块 5

```python
from scipy.stats import pearsonr
import pandas as pd

class CorrelationMonitor:
    """相关性监控"""
    
    def __init__(self,
                 threshold: float = 0.8,    # 相关性阈值
                 window: int = 30):          # 计算窗口
        self.threshold = threshold
        self.window = window
        self.historical_returns = {}
        
    def update_returns(self,
                       symbol: str,
                       returns: pd.Series):
        """更新历史收益"""
        self.historical_returns[symbol] = returns.tail(self.window)
        
    def check_correlation_breakdown(self) -> Dict[str, float]:
        """
        检查相关性突变
        
        Returns:
            异常相关性的组合
        """
        symbols = list(self.historical_returns.keys())
        correlations = {}
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                sym1, sym2 = symbols[i], symbols[j]
                
                if len(self.historical_returns[sym1]) == 0 or \
                   len(self.historical_returns[sym2]) == 0:
                    continue
                    
                # 计算滚动相关性
                corr = self.historical_returns[sym1].corr(
                    self.historical_returns[sym2]
                )
                
                correlations[(sym1, sym2)] = corr
                
        # 找出异常高相关性
        abnormal_corr = {
            pair: corr for pair, corr in correlations.items()
            if abs(corr) > self.threshold
        }
        
        return abnormal_corr

```

### 代码块 6

```python
from scipy.stats import norm
import numpy as np

class ValueAtRisk:
    """VaR 计算"""
    
    @staticmethod
    def historical_var(returns: pd.Series,
                       confidence_level: float = 0.95) -> float:
        """
        历史模拟法 VaR
        
        Args:
            returns: 收益序列
            confidence_level: 置信水平 (0.95 = 95%)
            
        Returns:
            VaR 值（负数）
        """
        alpha = 1 - confidence_level
        var = np.percentile(returns, alpha * 100)
        return var
        
    @staticmethod
    def parametric_var(returns: pd.Series,
                        confidence_level: float = 0.95) -> float:
        """
        参数法 VaR (假设正态分布)
        
        Args:
            returns: 收益序列
            confidence_level: 置信水平
            
        Returns:
            VaR 值（负数）
        """
        mean = returns.mean()
        std = returns.std()
        
        alpha = 1 - confidence_level
        z_score = norm.ppf(alpha)
        
        var = mean + z_score * std
        return var
        
    @staticmethod
    def expected_shortfall(returns: pd.Series,
                           confidence_level: float = 0.95) -> float:
        """
        条件 VaR / 期望损失 (ES)
        
        损失超过 VaR 时的平均损失
        """
        var = ValueAtRisk.historical_var(returns, confidence_level)
        es = returns[returns <= var].mean()
        return es

```

### 代码块 7

```python
class StressTest:
    """压力测试"""
    
    # 历史危机场景
    SCENARIOS = {
        '2008_crisis': {
            'equity_drop': -0.50,
            'correlation_spike': 0.9,
            'volatility_multiplier': 3.0
        },
        'covid_crash': {
            'equity_drop': -0.35,
            'correlation_spike': 0.85,
            'volatility_multiplier': 2.5
        },
        'flash_crash': {
            'equity_drop': -0.10,
            'correlation_spike': 0.95,
            'volatility_multiplier': 5.0
        }
    }
    
    def __init__(self, portfolio):
        self.portfolio = portfolio
        
    def run_scenario(self,
                    scenario_name: str) -> Dict:
        """
        运行压力测试场景
        
        Args:
            scenario_name: 场景名称
            
        Returns:
            测试结果
        """
        if scenario_name not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")
            
        scenario = self.SCENARIOS[scenario_name]
        
        # 模拟投资组合在场景下的表现
        initial_value = self.portfolio.get_total_value()
        
        # 应用股票跌幅
        loss = initial_value * abs(scenario['equity_drop'])
        
        # 应用相关性影响（相关性上升时分散失效）
        correlation_penalty = loss * 0.2 * scenario['correlation_spike']
        
        total_loss = loss + correlation_penalty
        
        return {
            'scenario': scenario_name,
            'initial_value': initial_value,
            'loss': total_loss,
            'final_value': initial_value - total_loss,
            'drawdown': total_loss / initial_value
        }
        
    def run_all_scenarios(self) -> Dict[str, Dict]:
        """运行所有压力测试场景"""
        results = {}
        for scenario_name in self.SCENARIOS:
            results[scenario_name] = self.run_scenario(scenario_name)
        return results

```

### 代码块 8

```python
class LeverageController:
    """杠杆控制器"""
    
    def __init__(self,
                 max_leverage: float = 3.0,      # 最大杠杆
                 warning_leverage: float = 2.5,    # 警告杠杆
                 deleverage_threshold: float = 2.8): # 减杠杆触发点
        self.max_leverage = max_leverage
        self.warning_leverage = warning_leverage
        self.deleverage_threshold = deleverage_threshold
        
    def check_leverage(self,
                      current_leverage: float) -> str:
        """
        检查杠杆水平
        
        Returns:
            行动指令
        """
        if current_leverage >= self.max_leverage:
            return 'force_deleverage'  # 强制减杠杆
        elif current_leverage >= self.deleverage_threshold:
            return 'deleverage'       # 主动减杠杆
        elif current_leverage >= self.warning_leverage:
            return 'warning'           # 警告
        else:
            return 'ok'
            
    def calculate_target_leverage(self,
                                  current_leverage: float,
                                  max_drawdown: float) -> float:
        """
        根据回撤调整目标杠杆
        
        回撤越大，目标杠杆越低
        """
        base_leverage = min(current_leverage, self.max_leverage)
        
        # 回撤调整因子
        drawdown_factor = max(0.5, 1 - max_drawdown * 2)
        
        target_leverage = base_leverage * drawdown_factor
        
        return max(1.0, min(target_leverage, self.max_leverage))

```

### 代码块 9

```python
import json
from datetime import datetime
from typing import Dict, List

class DailyRiskDashboard:
    """每日风险仪表板"""
    
    def __init__(self):
        self.risk_metrics = {}
        self.alerts = []
        
    def generate_daily_report(self,
                             portfolio,
                             var_calculator: ValueAtRisk,
                             drawdown_controller: DrawdownController,
                             correlation_monitor: CorrelationMonitor,
                             stress_test: StressTest) -> str:
        """生成每日风险报告"""
        
        report = []
        report.append("=" * 60)
        report.append(f"每日风险报告 - {datetime.now().strftime('%Y-%m-%d')}")
        report.append("=" * 60)
        
        # 1. 投资组合概览
        report.append("\n【投资组合概览】")
        total_value = portfolio.get_total_value()
        report.append(f"总资产: ${total_value:,.2f}")
        report.append(f"持仓数量: {portfolio.get_position_count()}")
        report.append(f"当前杠杆: {portfolio.get_leverage():.2f}x")
        
        # 2. 回撤分析
        report.append("\n【回撤分析】")
        dd_status = drawdown_controller.update_value(total_value)
        report.append(f"当前回撤: {dd_status['drawdown']*100:.2f}%")
        report.append(f"历史高点: ${dd_status['peak']:,.2f}")
        report.append(f"状态: {dd_status['action']}")
        
        # 3. VaR 分析
        report.append("\n【VaR 分析】")
        returns = portfolio.get_returns()
        var_95 = var_calculator.historical_var(returns, 0.95)
        var_99 = var_calculator.historical_var(returns, 0.99)
        es_95 = var_calculator.expected_shortfall(returns, 0.95)
        
        report.append(f"VaR (95%): ${abs(var_95 * total_value):,.2f} ({var_95*100:.2f}%)")
        report.append(f"VaR (99%): ${abs(var_99 * total_value):,.2f} ({var_99*100:.2f}%)")
        report.append(f"ES (95%): ${abs(es_95 * total_value):,.2f} ({es_95*100:.2f}%)")
        
        # 4. 相关性监控
        report.append("\n【相关性监控】")
        abnormal_corr = correlation_monitor.check_correlation_breakdown()
        if abnormal_corr:
            report.append("⚠️ 发现异常高相关性:")
            for pair, corr in abnormal_corr.items():
                report.append(f"  {pair}: {corr:.3f}")
        else:
            report.append("✅ 相关性正常")
            
        # 5. 压力测试
        report.append("\n【压力测试】")
        stress_results = stress_test.run_all_scenarios()
        for scenario, result in stress_results.items():
            report.append(f"{scenario}: {result['drawdown']*100:.2f}% 回撤")
            
        # 6. 行动建议
        report.append("\n【行动建议】")
        if dd_status['action'] == 'halt_trading':
            report.append("🛑 建议停止交易")
        elif dd_status['action'] == 'reduce_position':
            report.append("⚠️ 建议减仓 30-50%")
        elif abnormal_corr:
            report.append("⚠️ 建议检查相关集中度")
        else:
            report.append("✅ 风险可控，正常交易")
            
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
        
    def check_daily_checklist(self,
                              portfolio,
                              risk_params: Dict) -> List[str]:
        """
        每日风险检查清单
        
        Returns:
            需要处理的问题列表
        """
        issues = []
        
        # 1. 杠杆检查
        if portfolio.get_leverage() > risk_params['max_leverage']:
            issues.append(f"杠杆超限: {portfolio.get_leverage():.2f}x > {risk_params['max_leverage']}x")
            
        # 2. 单一持仓检查
        positions = portfolio.get_all_positions()
        max_position = max(positions, key=lambda x: x['weight'])
        if max_position['weight'] > risk_params['max_single_position']:
            issues.append(f"单一持仓过重: {max_position['symbol']} {max_position['weight']*100:.1f}%")
            
        # 3. 行业集中度检查
        sector_exposure = portfolio.get_sector_exposure()
        max_sector = max(sector_exposure.items(), key=lambda x: x[1])
        if max_sector[1] > risk_params['max_sector_exposure']:
            issues.append(f"行业集中度过高: {max_sector[0]} {max_sector[1]*100:.1f}%")
            
        # 4. 流动性检查
        illiquid_positions = [
            pos for pos in positions
            if pos['liquidity_score'] < risk_params['min_liquidity_score']
        ]
        if illiquid_positions:
            issues.append(f"流动性不足持仓: {[p['symbol'] for p in illiquid_positions]}")
            
        return issues

```

### 代码块 10

```python
DEFAULT_RISK_PARAMS = {
    # 仓位管理
    'kelly_fraction': 0.25,          # 部分 Kelly (25%)
    'max_leverage': 3.0,             # 最大杠杆
    'base_risk_per_trade': 0.02,     # 单笔风险 2%
    
    # 止损
    'stop_loss_threshold': 0.05,      # 5% 止损
    'trailing_stop_distance': 0.10,   # 10% 追踪止损
    'max_holding_days': 90,           # 最大持仓 90 天
    
    # 回撤控制
    'max_drawdown': 0.20,            # 最大回撤 20%
    'warning_drawdown': 0.15,         # 警告回撤 15%
    
    # 集中度
    'max_single_position': 0.10,      # 单一持仓最多 10%
    'max_sector_exposure': 0.30,      # 单一行业最多 30%
    
    # 相关性
    'correlation_threshold': 0.8,     # 相关性阈值
    
    # 流动性
    'min_liquidity_score': 0.5,      # 最低流动性评分
    'min_daily_volume': 1000000,      # 最低日成交量
}

```

