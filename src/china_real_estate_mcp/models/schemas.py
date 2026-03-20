"""
中国房地产数据模型定义

定义所有结构化输出类型的数据类，仅使用标准库 dataclasses，零外部依赖。
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def format_currency(value: float) -> str:
    """将数值格式化为中文货币字符串。

    例如：
        1234567  -> '123.46万元'
        8500     -> '0.85万元'
        123456789 -> '1.23亿元'
    """
    if abs(value) >= 1e8:
        return f"{value / 1e8:.2f}亿元"
    if abs(value) >= 1e4:
        return f"{value / 1e4:.2f}万元"
    return f"{value:.2f}元"


def format_percentage(value: float) -> str:
    """将小数格式化为百分比字符串。

    例如：
        0.0523 -> '5.23%'
       -0.12   -> '-12.00%'
    """
    return f"{value * 100:.2f}%"


def format_permil(value: float) -> str:
    """将数值格式化为千分比字符串。

    例如：
        7.48 -> '7.48‰'
    """
    return f"{value:.2f}‰"


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

@dataclass
class CostBreakdown:
    """建安成本拆解

    对指定建筑类型和城市等级的建安成本进行分项拆解，
    包含结构工程、装饰工程、机电消防电梯及其他费用。
    """

    building_type: str          # 建筑类型（如：高层住宅、小高层、洋房、别墅）
    city_tier: int              # 城市等级（1-5）
    construction_cost_per_sqm: float  # 建安成本（元/㎡）
    structure_cost: float       # 结构工程费用（元/㎡）
    decoration_cost: float      # 装饰工程费用（元/㎡）
    mep_cost: float             # 机电消防电梯费用（元/㎡）
    other_cost: float           # 其他费用（元/㎡）

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        return (
            f"【建安成本拆解】\n"
            f"建筑类型：{self.building_type} | 城市等级：{self.city_tier}线\n"
            f"建安成本合计：{self.construction_cost_per_sqm:.0f} 元/㎡\n"
            f"  ├ 结构工程：{self.structure_cost:.0f} 元/㎡\n"
            f"  ├ 装饰工程：{self.decoration_cost:.0f} 元/㎡\n"
            f"  ├ 机电消防电梯：{self.mep_cost:.0f} 元/㎡\n"
            f"  └ 其他：{self.other_cost:.0f} 元/㎡"
        )


@dataclass
class TheoreticalFloorPrice:
    """理论底价测算

    基于楼面地价、建安成本和税费杂项测算理论成本价，
    并与当前市场均价进行对比分析。
    """

    city: str                       # 城市名称
    land_cost_per_sqm: float        # 楼面地价（元/㎡）
    construction_cost_per_sqm: float  # 建安成本（元/㎡）
    tax_fee_per_sqm: float          # 税费杂项（元/㎡）
    total_cost_per_sqm: float       # 理论成本价（元/㎡）
    current_avg_price: float        # 当前市场均价（元/㎡）
    discount_to_cost: float         # 当前价格相对成本的溢价率
    analysis: str                   # 分析说明

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        premium_str = format_percentage(self.discount_to_cost)
        return (
            f"【{self.city} 理论底价测算】\n"
            f"楼面地价：{self.land_cost_per_sqm:.0f} 元/㎡\n"
            f"建安成本：{self.construction_cost_per_sqm:.0f} 元/㎡\n"
            f"税费杂项：{self.tax_fee_per_sqm:.0f} 元/㎡\n"
            f"理论成本价：{self.total_cost_per_sqm:.0f} 元/㎡\n"
            f"当前均价：{self.current_avg_price:.0f} 元/㎡\n"
            f"溢价率：{premium_str}\n"
            f"分析：{self.analysis}"
        )


@dataclass
class CityMarketOverview:
    """城市市场概览

    汇总城市房地产市场核心指标，包括新房/二手房均价、
    成交量、库存去化周期、租金及租售比等。
    """

    city: str                           # 城市名称
    tier: int                           # 城市等级
    avg_new_home_price: float           # 新房均价（元/㎡）
    avg_second_hand_price: float        # 二手房均价（元/㎡）
    core_area_price: float              # 核心区均价（元/㎡）
    price_change_yoy: float             # 同比变化（小数，如 -0.05）
    transaction_volume_10k_sqm: float   # 成交面积（万㎡）
    inventory_months: float             # 库存去化周期（月）
    avg_rent_per_sqm: float             # 平均租金（元/㎡·月）
    rent_to_price_ratio: float          # 租售比（年，如 1:600 记为 600）
    market_temperature: str             # 市场温度：冷/温/热

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        yoy_str = format_percentage(self.price_change_yoy)
        temp_emoji = {"冷": "🥶", "温": "😐", "热": "🔥"}.get(self.market_temperature, "")
        return (
            f"【{self.city} 市场概览】（{self.tier}线城市）{temp_emoji}\n"
            f"新房均价：{self.avg_new_home_price:.0f} 元/㎡\n"
            f"二手房均价：{self.avg_second_hand_price:.0f} 元/㎡\n"
            f"核心区均价：{self.core_area_price:.0f} 元/㎡\n"
            f"同比变化：{yoy_str}\n"
            f"成交面积：{self.transaction_volume_10k_sqm:.1f} 万㎡\n"
            f"库存去化：{self.inventory_months:.1f} 个月\n"
            f"平均租金：{self.avg_rent_per_sqm:.1f} 元/㎡·月\n"
            f"租售比：1:{self.rent_to_price_ratio:.0f}\n"
            f"市场温度：{self.market_temperature}"
        )


@dataclass
class CityComparison:
    """城市对比

    对多个城市的关键指标进行横向对比，并给出总结。
    """

    cities: list               # 参与对比的城市列表
    comparison_items: dict     # {指标名: {城市名: 值}}
    summary: str               # 对比总结

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        header = f"【城市对比】{'、'.join(self.cities)}\n"
        lines = []
        for metric, city_values in self.comparison_items.items():
            vals = " | ".join(f"{c}: {v}" for c, v in city_values.items())
            lines.append(f"  {metric}：{vals}")
        body = "\n".join(lines)
        return f"{header}{body}\n总结：{self.summary}"


@dataclass
class DemographicProfile:
    """人口画像

    城市人口结构核心指标，包括总人口、增长率、老龄化率、
    城镇化率、净迁入等，以及对住房需求趋势的判断。
    """

    city: str                   # 城市名称
    population_10k: float       # 常住人口（万人）
    growth_rate: float          # 人口增长率（小数）
    birth_rate: float           # 出生率（‰）
    aging_ratio: float          # 60岁以上人口占比（小数）
    dependency_ratio: float     # 抚养比（小数）
    urbanization_rate: float    # 城镇化率（小数）
    net_migration_10k: float    # 净迁入人口（万人）
    housing_demand_trend: str   # 住房需求趋势：上升/平稳/下降
    analysis: str               # 分析说明

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        trend_emoji = {"上升": "📈", "平稳": "➡️", "下降": "📉"}.get(
            self.housing_demand_trend, ""
        )
        return (
            f"【{self.city} 人口画像】\n"
            f"常住人口：{self.population_10k:.0f} 万人\n"
            f"人口增长率：{format_percentage(self.growth_rate)}\n"
            f"出生率：{format_permil(self.birth_rate)}\n"
            f"老龄化率（60+）：{format_percentage(self.aging_ratio)}\n"
            f"抚养比：{format_percentage(self.dependency_ratio)}\n"
            f"城镇化率：{format_percentage(self.urbanization_rate)}\n"
            f"净迁入：{self.net_migration_10k:+.1f} 万人\n"
            f"住房需求趋势：{self.housing_demand_trend} {trend_emoji}\n"
            f"分析：{self.analysis}"
        )


@dataclass
class DemographicImpact:
    """人口结构对住房需求影响

    综合评估人口老龄化、出生率、人口流动等因素
    对城市住房需求的影响。
    """

    city: str                   # 城市名称
    current_demand_index: float  # 当前需求指数（0-100）
    future_demand_trend: str    # 未来需求趋势
    aging_impact: str           # 老龄化影响说明
    birth_rate_impact: str      # 出生率影响说明
    migration_impact: str       # 人口流动影响说明
    overall_assessment: str     # 综合评估

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        return (
            f"【{self.city} 人口结构对住房需求影响】\n"
            f"当前需求指数：{self.current_demand_index:.0f}/100\n"
            f"未来需求趋势：{self.future_demand_trend}\n"
            f"老龄化影响：{self.aging_impact}\n"
            f"出生率影响：{self.birth_rate_impact}\n"
            f"人口流动影响：{self.migration_impact}\n"
            f"综合评估：{self.overall_assessment}"
        )


@dataclass
class InvestmentMetrics:
    """投资指标

    对指定城市房产的投资回报进行量化分析，
    包括租金回报率、回本年数、房价收入比、月供收入比等。
    """

    city: str                       # 城市名称
    property_price_per_sqm: float   # 房价（元/㎡）
    property_size_sqm: float        # 面积（㎡）
    total_price: float              # 总价（元）
    down_payment: float             # 首付（元）
    monthly_mortgage: float         # 月供（元）
    monthly_rent_income: float      # 月租金收入（元）
    gross_rental_yield: float       # 毛租金回报率（小数）
    net_rental_yield: float         # 净租金回报率（小数）
    payback_years: float            # 静态回本年数
    price_to_income_ratio: float    # 房价收入比
    monthly_payment_to_income: float  # 月供收入比（小数）
    assessment: str                 # 投资评估

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        return (
            f"【{self.city} 投资指标分析】\n"
            f"房价：{self.property_price_per_sqm:.0f} 元/㎡ × "
            f"{self.property_size_sqm:.0f}㎡ = {format_currency(self.total_price)}\n"
            f"首付：{format_currency(self.down_payment)}\n"
            f"月供：{format_currency(self.monthly_mortgage)}\n"
            f"月租金收入：{format_currency(self.monthly_rent_income)}\n"
            f"毛租金回报率：{format_percentage(self.gross_rental_yield)}\n"
            f"净租金回报率：{format_percentage(self.net_rental_yield)}\n"
            f"静态回本：{self.payback_years:.1f} 年\n"
            f"房价收入比：{self.price_to_income_ratio:.1f}\n"
            f"月供收入比：{format_percentage(self.monthly_payment_to_income)}\n"
            f"评估：{self.assessment}"
        )


@dataclass
class InvestmentTiming:
    """投资时机评估

    综合当前价格与理论底价的距离、市场周期、库存状况、
    政策方向等维度，对投资时机进行量化评分。
    """

    city: str                       # 城市名称
    current_price: float            # 当前均价（元/㎡）
    theoretical_floor_price: float  # 理论底价（元/㎡）
    distance_to_floor_pct: float    # 距底部百分比（小数）
    market_cycle_phase: str         # 市场周期阶段：上升/顶部/下降/底部
    inventory_status: str           # 库存状态
    policy_direction: str           # 政策方向
    timing_score: int               # 投资时机评分（0-100）
    recommendation: str             # 投资建议

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        score = self.timing_score
        if score >= 80:
            rating = "⭐⭐⭐⭐⭐ 强烈推荐"
        elif score >= 60:
            rating = "⭐⭐⭐⭐ 推荐关注"
        elif score >= 40:
            rating = "⭐⭐⭐ 中性观望"
        elif score >= 20:
            rating = "⭐⭐ 谨慎对待"
        else:
            rating = "⭐ 暂不建议"
        return (
            f"【{self.city} 投资时机评估】\n"
            f"当前均价：{self.current_price:.0f} 元/㎡\n"
            f"理论底价：{self.theoretical_floor_price:.0f} 元/㎡\n"
            f"距底部：{format_percentage(self.distance_to_floor_pct)}\n"
            f"市场周期：{self.market_cycle_phase}\n"
            f"库存状态：{self.inventory_status}\n"
            f"政策方向：{self.policy_direction}\n"
            f"时机评分：{self.timing_score}/100 → {rating}\n"
            f"建议：{self.recommendation}"
        )


@dataclass
class PolicySummary:
    """政策摘要

    汇总城市当前房地产调控政策，涵盖限购、贷款、
    补贴及其他政策，并判断整体政策方向。
    """

    city: str                   # 城市名称
    purchase_restriction: str   # 限购政策
    loan_policy: str            # 贷款政策
    subsidy_policy: str         # 补贴政策
    other_policies: list        # 其他政策列表
    policy_direction: str       # 政策方向：宽松/中性/收紧
    last_updated: str           # 最后更新时间

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        direction_emoji = {
            "宽松": "🟢", "中性": "🟡", "收紧": "🔴"
        }.get(self.policy_direction, "")
        others = "\n".join(f"  · {p}" for p in self.other_policies) if self.other_policies else "  （无）"
        return (
            f"【{self.city} 政策摘要】{direction_emoji} {self.policy_direction}\n"
            f"限购政策：{self.purchase_restriction}\n"
            f"贷款政策：{self.loan_policy}\n"
            f"补贴政策：{self.subsidy_policy}\n"
            f"其他政策：\n{others}\n"
            f"更新时间：{self.last_updated}"
        )


@dataclass
class RiskAssessment:
    """风险评估

    对城市房地产投资风险进行多维度评分，识别关键风险因素，
    并提供风险缓解建议。评分越高风险越大。
    """

    city: str                   # 城市名称
    overall_risk_score: int     # 综合风险评分（0-100，越高越危险）
    risk_factors: dict          # {风险因素名称: 评分}
    risk_level: str             # 风险等级：低/中低/中/中高/高
    key_risks: list             # 关键风险列表
    mitigation_suggestions: list  # 风险缓解建议列表

    def to_dict(self) -> dict:
        """转换为字典。"""
        return asdict(self)

    def to_summary(self) -> str:
        """返回中文摘要字符串。"""
        level_emoji = {
            "低": "🟢", "中低": "🟢", "中": "🟡", "中高": "🟠", "高": "🔴"
        }.get(self.risk_level, "")
        factors = "\n".join(
            f"  · {name}：{score}/100" for name, score in self.risk_factors.items()
        )
        risks = "\n".join(f"  ⚠️ {r}" for r in self.key_risks)
        suggestions = "\n".join(f"  💡 {s}" for s in self.mitigation_suggestions)
        return (
            f"【{self.city} 风险评估】{level_emoji} {self.risk_level}风险\n"
            f"综合风险评分：{self.overall_risk_score}/100\n"
            f"风险因素：\n{factors}\n"
            f"关键风险：\n{risks}\n"
            f"缓解建议：\n{suggestions}"
        )
