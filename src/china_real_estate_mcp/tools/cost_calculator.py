"""
成本测算工具模块

提供建安成本拆解、理论底价测算、项目开发成本估算等 MCP 工具函数。
函数均为普通 Python 函数（不加装饰器），由 server.py 统一注册。
"""

from __future__ import annotations

from china_real_estate_mcp.data.city_data import get_city, list_all_cities
from china_real_estate_mcp.data.construction_costs import (
    CONSTRUCTION_COSTS,
    TAX_AND_FEES,
    PRE_DEVELOPMENT_FEES,
    get_construction_cost,
    get_total_tax_fee_rate,
    get_total_pre_development_fee_rate,
    get_cost_breakdown,
    estimate_total_development_cost,
)
from china_real_estate_mcp.models.schemas import (
    CostBreakdown,
    TheoreticalFloorPrice,
    format_currency,
    format_percentage,
)


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------

_VALID_BUILDING_TYPES = list(CONSTRUCTION_COSTS.keys())
_VALID_QUALITIES = ("low", "mid", "high")
_QUALITY_LABELS = {"low": "标准化", "mid": "中等", "high": "高品质"}


def _building_type_hint() -> str:
    return "、".join(_VALID_BUILDING_TYPES)


def _validate_building_type(building_type: str) -> str | None:
    """校验建筑类型，不合法时返回错误信息，合法返回 None。"""
    if building_type not in CONSTRUCTION_COSTS:
        return (
            f"❌ 未知建筑类型「{building_type}」，"
            f"可选类型：{_building_type_hint()}"
        )
    return None


def _validate_quality(quality: str) -> str | None:
    """校验品质档次，不合法时返回错误信息，合法返回 None。"""
    if quality not in _VALID_QUALITIES:
        return (
            f"❌ 未知品质档次「{quality}」，"
            f"可选：low（标准化）、mid（中等）、high（高品质）"
        )
    return None


def _lookup_city(city: str) -> tuple[dict | None, str | None]:
    """查找城市，返回 (city_data, error_msg)。"""
    city_data = get_city(city)
    if city_data is None:
        all_cities = "、".join(list_all_cities())
        return None, (
            f"❌ 未找到城市「{city}」。\n"
            f"当前支持的城市：{all_cities}"
        )
    return city_data, None


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def calculate_construction_cost(
    city: str,
    building_type: str = "高层住宅",
    quality: str = "mid",
) -> str:
    """计算指定城市和建筑类型的建安成本，并给出分项拆解。

    Args:
        city: 城市中文名称（如"北京"、"成都"）。
        building_type: 建筑类型，可选：多层住宅、小高层、高层住宅、超高层、别墅、商业综合体、写字楼。
        quality: 品质档次，可选：low（标准化）、mid（中等，默认）、high（高品质）。

    Returns:
        建安成本拆解的中文摘要。
    """
    # 参数校验
    if err := _validate_building_type(building_type):
        return err
    if err := _validate_quality(quality):
        return err

    city_data, err = _lookup_city(city)
    if err:
        return err

    city_name: str = city_data["city"]
    tier: int = city_data["tier"]

    try:
        cost_per_sqm = get_construction_cost(building_type, tier, quality)
    except ValueError as e:
        return f"❌ 计算出错：{e}"

    breakdown = get_cost_breakdown(cost_per_sqm)

    result = CostBreakdown(
        building_type=building_type,
        city_tier=tier,
        construction_cost_per_sqm=cost_per_sqm,
        structure_cost=breakdown["结构工程"],
        decoration_cost=breakdown["装饰工程"],
        mep_cost=breakdown["机电消防电梯"],
        other_cost=breakdown["其他"],
    )

    quality_label = _QUALITY_LABELS.get(quality, quality)
    header = f"📍 城市：{city_name}（{tier}线城市） | 品质：{quality_label}\n\n"
    return header + result.to_summary()


def calculate_theoretical_floor_price(
    city: str,
    building_type: str = "高层住宅",
    use_core_area: bool = False,
) -> str:
    """测算指定城市的理论房价底价，并与当前市场均价对比。

    基于「楼面地价 + 建安成本 + 税费杂项 = 理论成本价」模型。

    Args:
        city: 城市中文名称。
        building_type: 建筑类型。
        use_core_area: 是否使用核心区地价（True）还是全市均价地价（False，默认）。

    Returns:
        理论底价测算的中文摘要。
    """
    if err := _validate_building_type(building_type):
        return err

    city_data, err = _lookup_city(city)
    if err:
        return err

    city_name: str = city_data["city"]
    tier: int = city_data["tier"]

    # 楼面地价
    if use_core_area:
        land_cost = float(city_data.get("core_land_price", city_data["avg_land_price"]))
        area_label = "核心区"
    else:
        land_cost = float(city_data["avg_land_price"])
        area_label = "全市均价"

    # 建安成本（取中等品质）
    try:
        construction_cost = get_construction_cost(building_type, tier, "mid")
    except ValueError as e:
        return f"❌ 计算出错：{e}"

    # 前期费用
    pre_dev_rate = get_total_pre_development_fee_rate()
    pre_dev_cost = (land_cost + construction_cost) * pre_dev_rate

    # 小计（土地 + 建安 + 前期）
    subtotal = land_cost + construction_cost + pre_dev_cost

    # 税费杂项：按预估售价（加成 12% 毛利）× 税费总费率
    estimated_sale_price = subtotal * 1.12
    tax_fee_rate = get_total_tax_fee_rate()
    tax_fee = estimated_sale_price * tax_fee_rate

    # 理论成本价
    total_cost = round(subtotal + tax_fee, 2)

    # 当前市场均价
    if use_core_area:
        current_price = float(city_data.get("core_area_price", city_data["avg_new_home_price"]))
    else:
        current_price = float(city_data["avg_new_home_price"])

    # 溢价率 = (当前价格 - 成本价) / 成本价
    if total_cost > 0:
        discount_to_cost = (current_price - total_cost) / total_cost
    else:
        discount_to_cost = 0.0

    # 分析文本
    if discount_to_cost > 0.3:
        analysis = (
            f"{city_name}{area_label}当前房价显著高于理论成本价，"
            f"溢价率达 {format_percentage(discount_to_cost)}，"
            "说明品牌溢价、稀缺性溢价或市场情绪推动较大。"
        )
    elif discount_to_cost > 0.1:
        analysis = (
            f"{city_name}{area_label}当前房价高于理论成本价，"
            f"溢价 {format_percentage(discount_to_cost)}，"
            "处于正常利润空间范围，市场相对理性。"
        )
    elif discount_to_cost > -0.05:
        analysis = (
            f"{city_name}{area_label}当前房价接近理论成本价，"
            "开发商利润空间极薄，部分项目可能面临亏损风险。"
        )
    else:
        analysis = (
            f"{city_name}{area_label}当前房价已低于理论成本价，"
            f"倒挂 {format_percentage(abs(discount_to_cost))}，"
            "市场处于深度调整期，新开工意愿受到抑制。"
        )

    result = TheoreticalFloorPrice(
        city=city_name,
        land_cost_per_sqm=round(land_cost, 2),
        construction_cost_per_sqm=round(construction_cost, 2),
        tax_fee_per_sqm=round(pre_dev_cost + tax_fee, 2),
        total_cost_per_sqm=total_cost,
        current_avg_price=current_price,
        discount_to_cost=round(discount_to_cost, 4),
        analysis=analysis,
    )

    header = f"📍 区域：{area_label} | 建筑类型：{building_type}\n\n"
    return header + result.to_summary()


def estimate_development_cost(
    city: str,
    building_type: str = "高层住宅",
    total_area_sqm: float = 100000,
    use_core_area: bool = False,
) -> str:
    """估算完整房地产开发项目的总成本，包含土地、建安、税费、营销、财务、管理等全部费用。

    Args:
        city: 城市中文名称。
        building_type: 建筑类型。
        total_area_sqm: 项目总建筑面积（㎡），默认 100000㎡（约 10 万方）。
        use_core_area: 是否使用核心区地价。

    Returns:
        项目开发成本估算的中文摘要。
    """
    if err := _validate_building_type(building_type):
        return err

    city_data, err = _lookup_city(city)
    if err:
        return err

    if total_area_sqm <= 0:
        return "❌ 总建筑面积必须大于 0。"

    city_name: str = city_data["city"]
    tier: int = city_data["tier"]

    # 楼面地价
    if use_core_area:
        land_cost_per_sqm = float(city_data.get("core_land_price", city_data["avg_land_price"]))
        area_label = "核心区"
    else:
        land_cost_per_sqm = float(city_data["avg_land_price"])
        area_label = "全市均价"

    # 调用底层估算函数
    try:
        cost_detail = estimate_total_development_cost(
            land_cost_per_sqm=land_cost_per_sqm,
            building_type=building_type,
            city_tier=tier,
            level="mid",
        )
    except ValueError as e:
        return f"❌ 计算出错：{e}"

    # 每平方米各分项
    land_per_sqm = cost_detail["楼面地价"]
    construction_per_sqm = cost_detail["建安成本"]
    pre_dev_per_sqm = cost_detail["前期费用"]
    tax_fee_per_sqm = cost_detail["税费及附加"]
    total_per_sqm = cost_detail["开发总成本"]

    # 从税费中拆分营销费、财务费、管理费用于展示
    # 利用 TAX_AND_FEES 比率 × 预估售价来单独列示
    subtotal_base = land_per_sqm + construction_per_sqm + pre_dev_per_sqm
    estimated_sale_price = subtotal_base * 1.12

    marketing_per_sqm = round(estimated_sale_price * TAX_AND_FEES.get("营销费", 0.025), 2)
    finance_per_sqm = round(estimated_sale_price * TAX_AND_FEES.get("财务费", 0.04), 2)
    management_per_sqm = round(estimated_sale_price * TAX_AND_FEES.get("管理费", 0.03), 2)
    pure_tax_per_sqm = round(
        tax_fee_per_sqm - marketing_per_sqm - finance_per_sqm - management_per_sqm, 2
    )

    # 项目总成本
    total_project_cost = total_per_sqm * total_area_sqm

    # 当前市场均价
    if use_core_area:
        current_price = float(city_data.get("core_area_price", city_data["avg_new_home_price"]))
    else:
        current_price = float(city_data["avg_new_home_price"])

    # 预计总销售额与毛利
    total_revenue = current_price * total_area_sqm
    gross_profit = total_revenue - total_project_cost
    gross_margin = gross_profit / total_revenue if total_revenue > 0 else 0.0

    # 成本占比
    pct_land = cost_detail["成本占比_土地"]
    pct_construction = cost_detail["成本占比_建安"]
    pct_pre_dev = cost_detail["成本占比_前期"]
    pct_tax = cost_detail["成本占比_税费"]

    # 构建输出
    lines = [
        f"【{city_name} 项目开发成本估算】",
        f"📍 区域：{area_label} | 建筑类型：{building_type} | 总面积：{total_area_sqm:,.0f} ㎡",
        "",
        "━━━ 每平方米成本明细 ━━━",
        f"  楼面地价：{land_per_sqm:,.0f} 元/㎡（占比 {format_percentage(pct_land)}）",
        f"  建安成本：{construction_per_sqm:,.0f} 元/㎡（占比 {format_percentage(pct_construction)}）",
        f"  前期费用：{pre_dev_per_sqm:,.0f} 元/㎡（占比 {format_percentage(pct_pre_dev)}）",
        f"  税费合计：{tax_fee_per_sqm:,.0f} 元/㎡（占比 {format_percentage(pct_tax)}）",
        f"    ├ 纯税费：{pure_tax_per_sqm:,.0f} 元/㎡",
        f"    ├ 营销费：{marketing_per_sqm:,.0f} 元/㎡",
        f"    ├ 财务费：{finance_per_sqm:,.0f} 元/㎡",
        f"    └ 管理费：{management_per_sqm:,.0f} 元/㎡",
        f"  ──────────",
        f"  开发总成本：{total_per_sqm:,.0f} 元/㎡",
        "",
        "━━━ 项目总额 ━━━",
        f"  土地总成本：{format_currency(land_per_sqm * total_area_sqm)}",
        f"  建安总成本：{format_currency(construction_per_sqm * total_area_sqm)}",
        f"  其他总成本：{format_currency((pre_dev_per_sqm + tax_fee_per_sqm) * total_area_sqm)}",
        f"  项目总成本：{format_currency(total_project_cost)}",
        "",
        "━━━ 收益预估（基于当前均价） ━━━",
        f"  当前均价：{current_price:,.0f} 元/㎡",
        f"  预计总销售额：{format_currency(total_revenue)}",
        f"  预计毛利润：{format_currency(gross_profit)}",
        f"  预计毛利率：{format_percentage(gross_margin)}",
    ]

    # 风险提示
    if gross_margin < 0:
        lines.append("\n⚠️ 警告：当前房价低于开发成本，项目面临亏损风险！")
    elif gross_margin < 0.05:
        lines.append("\n⚠️ 注意：毛利率极低，项目抗风险能力弱。")
    elif gross_margin < 0.10:
        lines.append("\n💡 提示：毛利率偏低，需严格控制成本。")

    lines.append("\n📌 说明：以上为简化估算模型，实际项目需根据具体地块条件、规划指标、融资方案等调整。")

    return "\n".join(lines)
