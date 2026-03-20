"""
市场分析工具模块

提供城市市场概览、城市对比和价格定位分析三个核心工具函数。
所有输出均为中文，适用于 MCP 工具调用。
"""

from __future__ import annotations

from ..data.city_data import get_city, get_cities_by_tier, CITY_DATA
from ..data.construction_costs import CONSTRUCTION_COSTS
from ..models.schemas import (
    CityMarketOverview,
    CityComparison,
    format_percentage,
)


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------

_TIER_KEY_MAP = {1: "tier_1", 2: "tier_2", 3: "tier_3", 4: "tier_4"}


def _estimate_construction_cost(tier: int) -> float:
    """根据城市等级估算高层住宅中等建安成本（元/㎡）。"""
    key = _TIER_KEY_MAP.get(tier, "tier_3")
    return float(CONSTRUCTION_COSTS["高层住宅"][key]["mid"])


def _estimate_tax_fee(land_cost: float, construction_cost: float) -> float:
    """估算税费杂项，约为楼面地价与建安成本之和的 12%。"""
    return (land_cost + construction_cost) * 0.12


def _determine_temperature(inventory_months: float, price_change_yoy: float) -> str:
    """根据库存去化周期和价格同比变化判定市场温度。

    判定规则：
    - 热：库存 < 12 月 且 价格同比 > -2%
    - 冷：库存 > 18 月 或 价格同比 < -8%
    - 温：其余情况
    """
    if inventory_months < 12 and price_change_yoy > -0.02:
        return "热"
    if inventory_months > 18 or price_change_yoy < -0.08:
        return "冷"
    return "温"


def _calc_rent_to_price_ratio(avg_price: float, avg_rent: float) -> float:
    """计算租售比（年），返回值如 600 表示 1:600。"""
    if avg_rent <= 0:
        return 0.0
    return avg_price / (avg_rent * 12)


def _calc_rent_yield(avg_price: float, avg_rent: float) -> float:
    """计算年化租金回报率（小数）。"""
    if avg_price <= 0:
        return 0.0
    return (avg_rent * 12) / avg_price


def _calc_affordability(avg_price: float, per_capita_income: float,
                        area: float = 90) -> float:
    """计算房价收入比（假设双职工家庭，默认 90㎡）。"""
    household_income = per_capita_income * 2
    if household_income <= 0:
        return 0.0
    return (avg_price * area) / household_income


# ---------------------------------------------------------------------------
# 工具函数 1：城市市场概览
# ---------------------------------------------------------------------------

def get_city_market_overview(city: str) -> str:
    """获取指定城市的房地产市场综合概览。

    返回包含新房/二手房/核心区均价、同比变化、成交量、库存去化、
    租金及租售比等核心指标的中文摘要，并标注市场温度（热/温/冷）。

    Args:
        city: 城市中文名称，如 "北京"、"成都"。

    Returns:
        中文格式的市场概览摘要字符串；若城市不存在则返回提示信息。
    """
    try:
        data = get_city(city)
        if data is None:
            available = "、".join(list(CITY_DATA.keys())[:10]) + " 等"
            return f"❌ 未找到城市「{city}」的数据。可查询的城市包括：{available}"

        avg_price = data["avg_new_home_price"]
        avg_rent = data["avg_rent_per_sqm"]
        inventory = data["inventory_months"]
        yoy = data["price_change_yoy"]

        temperature = _determine_temperature(inventory, yoy)
        rent_to_price = _calc_rent_to_price_ratio(avg_price, avg_rent)

        overview = CityMarketOverview(
            city=data["city"],
            tier=data["tier"],
            avg_new_home_price=avg_price,
            avg_second_hand_price=data["avg_second_hand_price"],
            core_area_price=data["core_area_price"],
            price_change_yoy=yoy,
            transaction_volume_10k_sqm=data["transaction_volume_10k_sqm"],
            inventory_months=inventory,
            avg_rent_per_sqm=avg_rent,
            rent_to_price_ratio=rent_to_price,
            market_temperature=temperature,
        )
        return overview.to_summary()

    except Exception as e:
        return f"❌ 获取「{city}」市场概览时出错：{e}"


# ---------------------------------------------------------------------------
# 工具函数 2：城市对比
# ---------------------------------------------------------------------------

def compare_cities(city_names: str) -> str:
    """对比多个城市的房地产市场核心指标。

    接受逗号分隔的城市名称（如 "长沙,武汉,成都"），对比维度包括：
    均价、价格变化、库存去化、租金回报率、房价收入比。

    Args:
        city_names: 逗号分隔的城市中文名称字符串。

    Returns:
        中文格式的城市对比表格与总结；若部分城市不存在则跳过并提示。
    """
    try:
        names = [n.strip() for n in city_names.split(",") if n.strip()]
        if len(names) < 2:
            return "❌ 请至少提供两个城市进行对比，用逗号分隔，如 \"长沙,武汉,成都\"。"

        cities_data: list[dict] = []
        not_found: list[str] = []
        for name in names:
            data = get_city(name)
            if data is None:
                not_found.append(name)
            else:
                cities_data.append(data)

        if len(cities_data) < 2:
            return f"❌ 有效城市不足两个，无法对比。未找到：{'、'.join(not_found)}"

        city_labels = [d["city"] for d in cities_data]

        # 构建对比指标
        comparison: dict[str, dict[str, str]] = {}

        comparison["新房均价（元/㎡）"] = {
            d["city"]: f"{d['avg_new_home_price']:,.0f}" for d in cities_data
        }
        comparison["二手房均价（元/㎡）"] = {
            d["city"]: f"{d['avg_second_hand_price']:,.0f}" for d in cities_data
        }
        comparison["同比变化"] = {
            d["city"]: format_percentage(d["price_change_yoy"]) for d in cities_data
        }
        comparison["库存去化（月）"] = {
            d["city"]: f"{d['inventory_months']:.1f}" for d in cities_data
        }
        comparison["租金回报率"] = {
            d["city"]: format_percentage(
                _calc_rent_yield(d["avg_new_home_price"], d["avg_rent_per_sqm"])
            )
            for d in cities_data
        }
        comparison["房价收入比"] = {
            d["city"]: f"{_calc_affordability(d['avg_new_home_price'], d['per_capita_income']):.1f}"
            for d in cities_data
        }

        # 生成总结
        summary_parts: list[str] = []

        cheapest = min(cities_data, key=lambda d: d["avg_new_home_price"])
        most_expensive = max(cities_data, key=lambda d: d["avg_new_home_price"])
        summary_parts.append(
            f"均价最高为{most_expensive['city']}"
            f"（{most_expensive['avg_new_home_price']:,.0f}元/㎡），"
            f"最低为{cheapest['city']}"
            f"（{cheapest['avg_new_home_price']:,.0f}元/㎡）"
        )

        best_yield_city = max(
            cities_data,
            key=lambda d: _calc_rent_yield(d["avg_new_home_price"], d["avg_rent_per_sqm"]),
        )
        best_yield = _calc_rent_yield(
            best_yield_city["avg_new_home_price"], best_yield_city["avg_rent_per_sqm"]
        )
        summary_parts.append(
            f"租金回报率最优为{best_yield_city['city']}"
            f"（{format_percentage(best_yield)}）"
        )

        lowest_inv = min(cities_data, key=lambda d: d["inventory_months"])
        highest_inv = max(cities_data, key=lambda d: d["inventory_months"])
        summary_parts.append(
            f"库存压力最小为{lowest_inv['city']}"
            f"（{lowest_inv['inventory_months']:.1f}个月），"
            f"最大为{highest_inv['city']}"
            f"（{highest_inv['inventory_months']:.1f}个月）"
        )

        summary = "；".join(summary_parts) + "。"

        result = CityComparison(
            cities=city_labels,
            comparison_items=comparison,
            summary=summary,
        )

        output = result.to_summary()
        if not_found:
            output += f"\n⚠️ 以下城市未找到数据，已跳过：{'、'.join(not_found)}"
        return output

    except Exception as e:
        return f"❌ 城市对比分析时出错：{e}"


# ---------------------------------------------------------------------------
# 工具函数 3：价格定位分析
# ---------------------------------------------------------------------------

def analyze_price_position(city: str) -> str:
    """分析指定城市当前房价在成本底线、历史趋势和同级城市中的定位。

    评估维度：
    1. 理论成本底线：基于楼面地价 + 建安成本 + 税费估算
    2. 历史走势：通过同比变化判断价格趋势
    3. 同级城市对比：与同等级城市均价比较

    Args:
        city: 城市中文名称。

    Returns:
        中文格式的价格定位详细分析文本；若城市不存在则返回提示。
    """
    try:
        data = get_city(city)
        if data is None:
            available = "、".join(list(CITY_DATA.keys())[:10]) + " 等"
            return f"❌ 未找到城市「{city}」的数据。可查询的城市包括：{available}"

        city_name = data["city"]
        tier = data["tier"]
        avg_price = data["avg_new_home_price"]
        yoy = data["price_change_yoy"]
        land_price = data["avg_land_price"]

        # --- 1. 理论成本底线 ---
        construction_cost = _estimate_construction_cost(tier)
        tax_fee = _estimate_tax_fee(land_price, construction_cost)
        floor_price = land_price + construction_cost + tax_fee
        premium_rate = (avg_price - floor_price) / floor_price if floor_price > 0 else 0

        if premium_rate < 0:
            floor_comment = (
                f"当前均价已低于理论成本价，跌幅约{format_percentage(abs(premium_rate))}，"
                "说明市场存在亏本销售或地价回调的可能"
            )
        elif premium_rate < 0.15:
            floor_comment = (
                f"当前均价仅高于理论成本价{format_percentage(premium_rate)}，"
                "利润空间极薄，价格接近底部区域"
            )
        elif premium_rate < 0.30:
            floor_comment = (
                f"当前均价高于理论成本价{format_percentage(premium_rate)}，"
                "处于合理利润区间"
            )
        else:
            floor_comment = (
                f"当前均价高于理论成本价{format_percentage(premium_rate)}，"
                "溢价空间较大，仍有一定下行空间"
            )

        # --- 2. 历史走势判断 ---
        if yoy > 0.02:
            trend_label = "上涨趋势"
            trend_comment = f"同比上涨{format_percentage(yoy)}，市场处于量价回升阶段"
        elif yoy > -0.03:
            trend_label = "基本平稳"
            trend_comment = f"同比变化{format_percentage(yoy)}，价格波动较小，市场较为平稳"
        elif yoy > -0.08:
            trend_label = "温和下跌"
            trend_comment = f"同比下跌{format_percentage(abs(yoy))}，处于调整期，但跌幅可控"
        else:
            trend_label = "明显下跌"
            trend_comment = f"同比下跌{format_percentage(abs(yoy))}，市场仍在深度调整中"

        # --- 3. 同级城市对比 ---
        peers = get_cities_by_tier(tier)
        if len(peers) > 1:
            peer_prices = [p["avg_new_home_price"] for p in peers]
            peer_avg = sum(peer_prices) / len(peer_prices)
            diff_rate = (avg_price - peer_avg) / peer_avg if peer_avg > 0 else 0

            peer_names = [p["city"] for p in peers if p["city"] != city_name]
            sorted_peers = sorted(peers, key=lambda p: p["avg_new_home_price"], reverse=True)
            rank = next(
                (i + 1 for i, p in enumerate(sorted_peers) if p["city"] == city_name),
                None,
            )
            rank_str = f"第{rank}/{len(peers)}" if rank else "N/A"

            if diff_rate > 0.15:
                peer_comment = (
                    f"高于同级城市均价{format_percentage(diff_rate)}，"
                    "在同等级城市中属于高价位，需关注性价比"
                )
            elif diff_rate > -0.15:
                peer_comment = (
                    f"与同级城市均价偏差{format_percentage(abs(diff_rate))}，"
                    "处于同等级城市正常价格区间"
                )
            else:
                peer_comment = (
                    f"低于同级城市均价{format_percentage(abs(diff_rate))}，"
                    "在同等级城市中价格偏低，或具有一定价值洼地特征"
                )
        else:
            peer_avg = avg_price
            rank_str = "1/1"
            peer_comment = "该等级仅此一城，无法进行同级对比"
            peer_names = []

        # --- 组装输出 ---
        lines = [
            f"【{city_name} 价格定位分析】",
            f"城市等级：{tier}线城市",
            f"当前新房均价：{avg_price:,.0f} 元/㎡",
            "",
            "━━━ 一、理论成本底线 ━━━",
            f"  楼面地价：{land_price:,.0f} 元/㎡",
            f"  建安成本：{construction_cost:,.0f} 元/㎡",
            f"  税费杂项：{tax_fee:,.0f} 元/㎡",
            f"  理论成本价：{floor_price:,.0f} 元/㎡",
            f"  当前溢价率：{format_percentage(premium_rate)}",
            f"  ▸ {floor_comment}",
            "",
            "━━━ 二、价格走势 ━━━",
            f"  同比变化：{format_percentage(yoy)}",
            f"  趋势判断：{trend_label}",
            f"  ▸ {trend_comment}",
            "",
            "━━━ 三、同级城市对比 ━━━",
            f"  同级城市数量：{len(peers)} 个",
            f"  同级均价：{peer_avg:,.0f} 元/㎡",
            f"  价格排名：{rank_str}",
        ]
        if peer_names:
            lines.append(f"  对比城市：{'、'.join(peer_names[:6])}")
        lines += [
            f"  ▸ {peer_comment}",
            "",
            "━━━ 综合判断 ━━━",
        ]

        # 综合评级
        signals: list[str] = []
        if premium_rate < 0.15:
            signals.append("价格接近成本底部")
        if yoy < -0.05:
            signals.append("价格仍在下行通道")
        if diff_rate < -0.15 if len(peers) > 1 else False:
            signals.append("低于同级均价")

        if not signals:
            overall = f"{city_name}当前价格处于相对合理区间，建议结合具体板块与自身需求综合判断。"
        else:
            overall = f"{city_name}当前{'，'.join(signals)}，建议密切关注市场变化，审慎决策。"

        lines.append(f"  {overall}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 分析「{city}」价格定位时出错：{e}"
