"""
人口结构分析工具模块

提供城市人口画像、人口结构对住房需求的影响分析、住房需求预测等功能。
"""

from __future__ import annotations

from china_real_estate_mcp.data.demographics_data import (
    get_demographics,
    get_aging_index,
    get_dependency_ratio,
    get_housing_demand_indicator,
)
from china_real_estate_mcp.data.city_data import CITY_DATA
from china_real_estate_mcp.models.schemas import (
    DemographicProfile,
    DemographicImpact,
    format_percentage,
)


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------

def _get_city_data(city: str) -> dict | None:
    """获取城市房地产基础数据，找不到时返回 None。"""
    return CITY_DATA.get(city)


def _classify_trend(aging_ratio: float, birth_rate: float, net_migration: float) -> str:
    """根据老龄化率、出生率和净迁入判断住房需求趋势。"""
    score = 0
    # 老龄化越低越好
    if aging_ratio < 0.15:
        score += 2
    elif aging_ratio < 0.20:
        score += 1
    else:
        score -= 1
    # 出生率越高越好
    if birth_rate >= 8.0:
        score += 2
    elif birth_rate >= 6.0:
        score += 1
    else:
        score -= 1
    # 净迁入正向越好
    if net_migration > 10:
        score += 2
    elif net_migration > 0:
        score += 1
    else:
        score -= 1

    if score >= 3:
        return "上升"
    if score >= 0:
        return "平稳"
    return "下降"


def _build_profile_analysis(data: dict, trend: str) -> str:
    """根据人口数据生成文字分析。"""
    parts: list[str] = []
    aging = data["age_60_plus_pct"]
    birth = data["birth_rate_permil"]
    migration = data["net_migration_10k"]

    if aging >= 0.22:
        parts.append("老龄化程度较高，养老型住房需求增加，但新增购房需求不足")
    elif aging >= 0.17:
        parts.append("老龄化处于中等水平，住房需求结构正在转型")
    else:
        parts.append("年龄结构相对年轻，劳动力充足，住房刚需较旺盛")

    if birth < 6.0:
        parts.append("出生率偏低，未来学区房等家庭型住房需求可能收缩")
    elif birth >= 8.0:
        parts.append("出生率较高，家庭型住房与教育配套需求有支撑")

    if migration > 10:
        parts.append("人口净流入显著，租赁与购房需求双重支撑")
    elif migration > 0:
        parts.append("人口小幅净流入，住房需求保持温和增长")
    else:
        parts.append("人口净流出，住房需求面临收缩压力")

    parts.append(f"综合判断住房需求趋势为「{trend}」")
    return "；".join(parts) + "。"


# ---------------------------------------------------------------------------
# 工具函数 1：人口画像
# ---------------------------------------------------------------------------

def get_demographic_profile(city: str) -> str:
    """获取城市完整人口画像。

    返回包含常住人口、增长率、出生率/死亡率、年龄结构、
    城镇化率、净迁入、户均人口等核心指标的中文摘要。

    Args:
        city: 城市中文名称，如 "北京"、"成都"。

    Returns:
        中文格式化的人口画像摘要文本。
    """
    demo = get_demographics(city)
    if demo is None:
        return f"⚠️ 未找到城市「{city}」的人口数据，请检查城市名称是否正确。"

    aging_ratio = demo["age_60_plus_pct"]
    birth_rate = demo["birth_rate_permil"]
    net_migration = demo["net_migration_10k"]
    dependency = get_dependency_ratio(city) or 0.0
    trend = _classify_trend(aging_ratio, birth_rate, net_migration)
    analysis = _build_profile_analysis(demo, trend)

    profile = DemographicProfile(
        city=city,
        population_10k=demo["population_10k"],
        growth_rate=demo["population_growth_rate"],
        birth_rate=birth_rate,
        aging_ratio=aging_ratio,
        dependency_ratio=dependency,
        urbanization_rate=demo["urbanization_rate"],
        net_migration_10k=net_migration,
        housing_demand_trend=trend,
        analysis=analysis,
    )

    # 在 schema 摘要基础上追加补充信息
    extra_lines = (
        f"\n── 补充指标 ──\n"
        f"死亡率：{demo['death_rate_permil']:.2f}‰\n"
        f"自然增长率：{demo['natural_growth_rate_permil']:.2f}‰\n"
        f"0-14岁占比：{format_percentage(demo['age_0_14_pct'])}\n"
        f"15-59岁占比：{format_percentage(demo['age_15_59_pct'])}\n"
        f"65岁以上占比：{format_percentage(demo['age_65_plus_pct'])}\n"
        f"户均人口：{demo['avg_household_size']:.2f} 人\n"
        f"住房自有率：{format_percentage(demo['housing_ownership_rate'])}\n"
        f"人均居住面积：{demo['per_capita_living_area']:.1f} ㎡"
    )
    return profile.to_summary() + extra_lines


# ---------------------------------------------------------------------------
# 工具函数 2：人口结构对住房需求影响分析
# ---------------------------------------------------------------------------

def analyze_demographic_impact(city: str) -> str:
    """分析城市人口结构对住房需求的影响。

    从老龄化、出生率、人口流动三个维度评估影响，
    并计算综合住房需求指数（0-100）。

    Args:
        city: 城市中文名称。

    Returns:
        中文格式化的影响分析摘要文本。
    """
    demo = get_demographics(city)
    if demo is None:
        return f"⚠️ 未找到城市「{city}」的人口数据，请检查城市名称是否正确。"

    aging_ratio = demo["age_60_plus_pct"]
    birth_rate = demo["birth_rate_permil"]
    net_migration = demo["net_migration_10k"]
    growth_rate = demo["population_growth_rate"]
    urbanization = demo["urbanization_rate"]

    # ---- 老龄化影响（满分 30，越低越好） ----
    if aging_ratio < 0.12:
        aging_score = 30
        aging_text = "老龄化率极低，劳动力充沛，住房刚需和改善需求旺盛"
    elif aging_ratio < 0.17:
        aging_score = 22
        aging_text = "老龄化处于较低水平，对住房需求影响有限，整体正面"
    elif aging_ratio < 0.22:
        aging_score = 14
        aging_text = "老龄化中等偏高，新增购房主力人群占比缩减，需求增速放缓"
    else:
        aging_score = 5
        aging_text = "老龄化严重，购房适龄人口大幅减少，住房需求明显承压"

    # ---- 出生率影响（满分 30，越高越好） ----
    if birth_rate >= 10.0:
        birth_score = 30
        birth_text = "出生率较高，未来家庭住房、学区房需求有坚实支撑"
    elif birth_rate >= 7.5:
        birth_score = 22
        birth_text = "出生率中等，中长期住房需求尚可维持"
    elif birth_rate >= 5.5:
        birth_score = 14
        birth_text = "出生率偏低，未来家庭型住房需求将逐步收缩"
    else:
        birth_score = 5
        birth_text = "出生率极低，长期住房需求缺乏新生人口支撑，前景严峻"

    # ---- 人口流动影响（满分 40，净流入越多越好） ----
    if net_migration >= 15:
        migration_score = 40
        migration_text = "人口大量净流入，租赁和购房需求双旺，市场活力强"
    elif net_migration >= 5:
        migration_score = 30
        migration_text = "人口持续净流入，住房需求稳健增长"
    elif net_migration >= 0:
        migration_score = 18
        migration_text = "人口流入流出基本均衡，住房需求主要依赖本地自然增长"
    elif net_migration >= -10:
        migration_score = 8
        migration_text = "人口小幅净流出，住房需求承压，市场活跃度下降"
    else:
        migration_score = 2
        migration_text = "人口大量净流出，住房供过于求风险显著上升"

    # ---- 额外加分：城镇化与增长率 ----
    bonus = 0
    if urbanization < 0.75:
        bonus += 5  # 城镇化空间大
    if growth_rate >= 0.008:
        bonus += 5  # 增长势头好

    demand_index = min(aging_score + birth_score + migration_score + bonus, 100)

    # 判断趋势
    if demand_index >= 70:
        future_trend = "需求较强，预计保持增长"
    elif demand_index >= 45:
        future_trend = "需求温和，预计基本平稳"
    else:
        future_trend = "需求偏弱，预计逐步收缩"

    overall_parts = []
    if demand_index >= 70:
        overall_parts.append(f"{city}人口结构对住房需求形成较强支撑")
    elif demand_index >= 45:
        overall_parts.append(f"{city}人口结构对住房需求支撑力中等")
    else:
        overall_parts.append(f"{city}人口结构对住房需求构成负面压力")

    if urbanization < 0.75:
        overall_parts.append("城镇化率仍有提升空间，可部分对冲人口自然增长放缓的影响")
    overall_parts.append(f"综合需求指数为 {demand_index}/100")
    overall = "，".join(overall_parts) + "。"

    impact = DemographicImpact(
        city=city,
        current_demand_index=demand_index,
        future_demand_trend=future_trend,
        aging_impact=aging_text,
        birth_rate_impact=birth_text,
        migration_impact=migration_text,
        overall_assessment=overall,
    )
    return impact.to_summary()


# ---------------------------------------------------------------------------
# 工具函数 3：住房需求预测
# ---------------------------------------------------------------------------

def forecast_housing_demand(city: str, years: int = 10) -> str:
    """对城市未来住房需求进行简单预测。

    基于当前人口增长率与净迁入量投射未来人口规模，
    结合年龄结构变迁估算新增家庭户数与住房面积需求，
    并与当前库存进行对比。

    Args:
        city: 城市中文名称。
        years: 预测年数，默认 10 年。

    Returns:
        中文格式化的住房需求预测文本。
    """
    demo = get_demographics(city)
    if demo is None:
        return f"⚠️ 未找到城市「{city}」的人口数据，请检查城市名称是否正确。"

    city_info = _get_city_data(city)
    housing_indicator = get_housing_demand_indicator(city)

    # ---- 基础数据 ----
    pop_10k = demo["population_10k"]
    growth_rate = demo["population_growth_rate"]
    net_migration = demo["net_migration_10k"]
    household_size = demo["avg_household_size"]
    urbanization = demo["urbanization_rate"]
    aging_ratio = demo["age_60_plus_pct"]
    per_capita_area = demo["per_capita_living_area"]

    # ---- 人口投射 ----
    # 综合增长率 = 自然增长率 + 机械增长率（净迁入/总人口）
    migration_rate = net_migration / pop_10k if pop_10k > 0 else 0
    effective_growth = growth_rate + migration_rate * 0.5  # 迁入部分折半（渐趋稳定）
    projected_pop = pop_10k
    for _ in range(years):
        projected_pop *= (1 + effective_growth)
    projected_pop = round(projected_pop, 1)
    pop_change = round(projected_pop - pop_10k, 1)

    # ---- 年龄结构偏移 ----
    # 简单假设：每年老龄化率提升 0.3 个百分点
    aging_shift_per_year = 0.003
    projected_aging = min(aging_ratio + aging_shift_per_year * years, 0.45)
    projected_working = max(demo["age_15_59_pct"] - aging_shift_per_year * years * 0.6, 0.40)

    # ---- 新增家庭户数 ----
    # 城镇化推进带来新增城镇人口
    urbanization_increment = min(0.01 * years, max(0.95 - urbanization, 0))
    new_urban_pop = pop_10k * urbanization_increment  # 万人
    # 人口增量带来的新增户数
    growth_new_households = max(pop_change, 0) / household_size
    # 城镇化带来的新增户数
    urban_new_households = new_urban_pop / household_size
    # 小型化趋势：户均人口逐步下降带来拆户需求
    household_shrink_rate = 0.005  # 年均缩小 0.5%
    projected_household_size = household_size * (1 - household_shrink_rate) ** years
    current_households = pop_10k / household_size
    future_households_base = projected_pop / projected_household_size
    split_new_households = max(future_households_base - current_households - growth_new_households - urban_new_households, 0)

    total_new_households = round(growth_new_households + urban_new_households + split_new_households, 1)
    annual_new_households = round(total_new_households / years, 2) if years > 0 else 0

    # ---- 住房面积需求 ----
    avg_home_size = per_capita_area * projected_household_size  # ㎡/套
    total_area_demand_10k_sqm = round(total_new_households * avg_home_size / 10000, 2)  # 亿㎡ → 万㎡
    # 转为万㎡ (total_new_households 是万户, avg_home_size 是㎡/套)
    total_area_demand_wan_sqm = round(total_new_households * avg_home_size, 1)
    annual_area_demand = round(total_area_demand_wan_sqm / years, 1) if years > 0 else 0

    # ---- 库存对比 ----
    inventory_note = ""
    if city_info:
        inv_months = city_info.get("inventory_months", 0)
        txn_vol = city_info.get("transaction_volume_10k_sqm", 0)
        # 当前年成交量
        annual_txn = txn_vol  # 万㎡/年
        if annual_txn > 0 and annual_area_demand > 0:
            supply_demand_ratio = round(annual_txn / annual_area_demand, 2)
            if supply_demand_ratio > 1.5:
                inventory_note = (
                    f"当前年成交面积（{annual_txn:.0f}万㎡）远大于预测年均需求"
                    f"（{annual_area_demand:.0f}万㎡），供应充裕，去化压力较大"
                )
            elif supply_demand_ratio > 1.0:
                inventory_note = (
                    f"当前年成交面积（{annual_txn:.0f}万㎡）略高于预测年均需求"
                    f"（{annual_area_demand:.0f}万㎡），供需基本均衡"
                )
            else:
                inventory_note = (
                    f"当前年成交面积（{annual_txn:.0f}万㎡）低于预测年均需求"
                    f"（{annual_area_demand:.0f}万㎡），未来可能出现供不应求"
                )
        if inv_months > 0:
            inventory_note += f"；当前库存去化周期为 {inv_months:.0f} 个月"

    # ---- 组装输出 ----
    lines = [
        f"【{city} 未来 {years} 年住房需求预测】",
        "",
        "═══ 人口趋势 ═══",
        f"  当前常住人口：{pop_10k:.0f} 万人",
        f"  预测 {years} 年后人口：{projected_pop:.0f} 万人（{'增加' if pop_change >= 0 else '减少'} {abs(pop_change):.1f} 万人）",
        f"  综合年增长率：{format_percentage(effective_growth)}",
        "",
        "═══ 年龄结构变化 ═══",
        f"  当前60岁以上占比：{format_percentage(aging_ratio)}",
        f"  预测60岁以上占比：{format_percentage(projected_aging)}",
        f"  当前劳动年龄占比：{format_percentage(demo['age_15_59_pct'])}",
        f"  预测劳动年龄占比：{format_percentage(projected_working)}",
        "",
        "═══ 住房需求估算 ═══",
        f"  预测新增家庭户数：{total_new_households:.1f} 万户（年均 {annual_new_households:.2f} 万户）",
        f"    ├ 人口增长贡献：{growth_new_households:.1f} 万户",
        f"    ├ 城镇化贡献：{urban_new_households:.1f} 万户",
        f"    └ 家庭小型化贡献：{split_new_households:.1f} 万户",
        f"  预测户均面积：{avg_home_size:.1f} ㎡/套",
        f"  预测新增住房面积需求：{total_area_demand_wan_sqm:.0f} 万㎡（年均 {annual_area_demand:.0f} 万㎡）",
    ]

    if inventory_note:
        lines += [
            "",
            "═══ 供需对比 ═══",
            f"  {inventory_note}",
        ]

    # ---- 综合判断 ----
    if pop_change > 0 and projected_aging < 0.25:
        conclusion = "人口保持增长且老龄化可控，住房需求前景较为乐观。"
    elif pop_change > 0:
        conclusion = "人口仍有增长，但老龄化加速将削弱中长期需求动能。"
    elif projected_aging < 0.25:
        conclusion = "人口出现收缩但老龄化尚在可控范围，需求以存量更新为主。"
    else:
        conclusion = "人口收缩叠加深度老龄化，住房需求将持续萎缩，需警惕供过于求。"

    lines += [
        "",
        "═══ 综合判断 ═══",
        f"  {conclusion}",
        "",
        "⚠️ 以上预测基于简化模型，仅供参考，实际需求受政策、经济等多重因素影响。",
    ]
    return "\n".join(lines)
