"""
建安成本与税费数据模块

包含中国房地产开发的建安成本、成本构成明细、税费及附加成本等数据。
数据基于 2024-2025 年行业公开数据整理，为教育与参考用途。

数据来源参考：中国建设工程造价信息网、各省造价站、行业研究报告等。
"""

from __future__ import annotations

# 建安成本数据（元/㎡）- 按建筑类型和城市等级
# tier_1 对应一线城市，tier_2 对应新一线/二线，tier_3 对应三线，tier_4 对应四线及以下
# low/mid/high 分别对应标准化/中等/高品质项目
CONSTRUCTION_COSTS: dict[str, dict[str, dict[str, int]]] = {
    "多层住宅": {  # ≤6层
        "tier_1": {"low": 1500, "mid": 2000, "high": 2500},
        "tier_2": {"low": 1200, "mid": 1600, "high": 2000},
        "tier_3": {"low": 1000, "mid": 1300, "high": 1600},
        "tier_4": {"low": 800, "mid": 1100, "high": 1400},
    },
    "小高层": {  # 7-18层
        "tier_1": {"low": 1800, "mid": 2400, "high": 3000},
        "tier_2": {"low": 1500, "mid": 2000, "high": 2500},
        "tier_3": {"low": 1200, "mid": 1600, "high": 2000},
        "tier_4": {"low": 1000, "mid": 1300, "high": 1700},
    },
    "高层住宅": {  # 19-33层
        "tier_1": {"low": 2200, "mid": 2800, "high": 3500},
        "tier_2": {"low": 1800, "mid": 2400, "high": 3000},
        "tier_3": {"low": 1500, "mid": 2000, "high": 2500},
        "tier_4": {"low": 1200, "mid": 1600, "high": 2100},
    },
    "超高层": {  # ≥34层
        "tier_1": {"low": 3000, "mid": 3800, "high": 5000},
        "tier_2": {"low": 2500, "mid": 3200, "high": 4200},
        "tier_3": {"low": 2000, "mid": 2700, "high": 3500},
        "tier_4": {"low": 1700, "mid": 2300, "high": 3000},
    },
    "别墅": {  # 独栋/联排/叠拼
        "tier_1": {"low": 2500, "mid": 3500, "high": 5000},
        "tier_2": {"low": 2000, "mid": 2800, "high": 4000},
        "tier_3": {"low": 1600, "mid": 2200, "high": 3200},
        "tier_4": {"low": 1300, "mid": 1800, "high": 2600},
    },
    "商业综合体": {
        "tier_1": {"low": 3500, "mid": 4500, "high": 6000},
        "tier_2": {"low": 2800, "mid": 3600, "high": 4800},
        "tier_3": {"low": 2200, "mid": 2900, "high": 3800},
        "tier_4": {"low": 1800, "mid": 2400, "high": 3200},
    },
    "写字楼": {
        "tier_1": {"low": 3000, "mid": 4000, "high": 5500},
        "tier_2": {"low": 2500, "mid": 3200, "high": 4500},
        "tier_3": {"low": 2000, "mid": 2600, "high": 3500},
        "tier_4": {"low": 1600, "mid": 2100, "high": 2800},
    },
}

# 成本构成明细比例（占建安总成本的比例）
COST_BREAKDOWN: dict[str, float] = {
    "结构工程": 0.50,  # 含基础、主体结构
    "装饰工程": 0.25,  # 外墙、内装、门窗等
    "机电消防电梯": 0.15,  # 给排水、暖通、电气、消防、电梯
    "其他": 0.10,  # 室外配套、临时设施、安全文明等
}

# 税费与附加成本比率（占销售额的比例）
TAX_AND_FEES: dict[str, float] = {
    "增值税": 0.09,  # 一般计税 9%
    "土地增值税预征": 0.02,  # 预征率 2%-4%，取中等偏低
    "企业所得税": 0.025,  # 预缴税率
    "城建及附加": 0.012,  # 城建税 7% + 教育附加 3% + 地方教育附加 2% ≈ 增值税的 12%
    "管理费": 0.03,  # 开发管理费
    "营销费": 0.025,  # 销售费用（佣金+推广）
    "财务费": 0.04,  # 资金成本/利息
    "不可预见费": 0.03,  # 不可预见及其他
}

# 前期费用比率（占土地成本 + 建安成本之和的比例）
PRE_DEVELOPMENT_FEES: dict[str, float] = {
    "勘察设计费": 0.03,
    "报批报建费": 0.015,
    "监理费": 0.015,
    "前期工程费": 0.02,
    "基础设施配套费": 0.04,
}


def get_construction_cost(
    building_type: str,
    city_tier: int,
    level: str = "mid",
) -> float:
    """获取指定建筑类型、城市等级和品质档次的建安成本（元/㎡）。

    Args:
        building_type: 建筑类型，如 ``"高层住宅"``、``"多层住宅"`` 等。
        city_tier: 城市等级（1-4）。
        level: 品质档次，``"low"`` / ``"mid"`` / ``"high"``。

    Returns:
        建安成本（元/㎡）。

    Raises:
        ValueError: 建筑类型或参数不合法时抛出。
    """
    if building_type not in CONSTRUCTION_COSTS:
        available = ", ".join(CONSTRUCTION_COSTS.keys())
        raise ValueError(
            f"未知建筑类型 '{building_type}'，可选类型: {available}"
        )

    tier_key = f"tier_{min(max(city_tier, 1), 4)}"
    tier_data = CONSTRUCTION_COSTS[building_type].get(tier_key)
    if tier_data is None:
        raise ValueError(f"城市等级 {city_tier} 对应的 tier_key '{tier_key}' 不存在")

    if level not in tier_data:
        raise ValueError(f"品质档次 '{level}' 不合法，可选: low, mid, high")

    return float(tier_data[level])


def get_total_tax_fee_rate() -> float:
    """计算税费及附加成本的合计比率（占销售额比例）。

    Returns:
        税费合计比率（小数形式）。
    """
    return sum(TAX_AND_FEES.values())


def get_total_pre_development_fee_rate() -> float:
    """计算前期费用合计比率（占土地 + 建安成本之和的比例）。

    Returns:
        前期费用合计比率（小数形式）。
    """
    return sum(PRE_DEVELOPMENT_FEES.values())


def get_cost_breakdown(total_construction_cost: float) -> dict[str, float]:
    """根据建安总成本，分解为各工程类别的金额。

    Args:
        total_construction_cost: 建安总成本（元/㎡ 或 总额均可）。

    Returns:
        各分项成本字典，键为分项名称，值为对应金额。
    """
    return {
        category: round(total_construction_cost * ratio, 2)
        for category, ratio in COST_BREAKDOWN.items()
    }


def estimate_total_development_cost(
    land_cost_per_sqm: float,
    building_type: str,
    city_tier: int,
    level: str = "mid",
) -> dict[str, float]:
    """估算每平方米开发总成本（含土地、建安、前期、税费）。

    这是一个简化估算模型，实际项目需根据具体情况调整。

    Args:
        land_cost_per_sqm: 楼面地价（元/㎡）。
        building_type: 建筑类型。
        city_tier: 城市等级（1-4）。
        level: 品质档次。

    Returns:
        各成本分项及合计的字典。
    """
    construction = get_construction_cost(building_type, city_tier, level)
    pre_dev_rate = get_total_pre_development_fee_rate()
    pre_dev = round((land_cost_per_sqm + construction) * pre_dev_rate, 2)

    subtotal = land_cost_per_sqm + construction + pre_dev

    # 税费按预估销售价（假设利润率 10%-15%）折算，此处简化为按成本加成估算
    estimated_sale_price = subtotal * 1.12  # 假设 12% 毛利
    tax_fee_rate = get_total_tax_fee_rate()
    tax_fee = round(estimated_sale_price * tax_fee_rate, 2)

    total = round(subtotal + tax_fee, 2)

    return {
        "楼面地价": land_cost_per_sqm,
        "建安成本": construction,
        "前期费用": pre_dev,
        "税费及附加": tax_fee,
        "开发总成本": total,
        "成本占比_土地": round(land_cost_per_sqm / total, 4),
        "成本占比_建安": round(construction / total, 4),
        "成本占比_前期": round(pre_dev / total, 4),
        "成本占比_税费": round(tax_fee / total, 4),
    }
