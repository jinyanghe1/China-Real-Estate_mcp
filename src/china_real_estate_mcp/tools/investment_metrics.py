"""
投资指标分析工具模块

提供房产投资回报计算、购房负担能力评估、投资时机判断和城市投资比较等功能。
所有工具函数返回中文格式化字符串，适用于 MCP 工具调用。
"""

from __future__ import annotations

from ..data.city_data import get_city, CITY_DATA
from ..data.construction_costs import (
    get_construction_cost,
    estimate_total_development_cost,
)
from ..data.demographics_data import get_demographics
from ..models.schemas import (
    InvestmentMetrics,
    InvestmentTiming,
    format_currency,
    format_percentage,
)


# ---------------------------------------------------------------------------
# 内部辅助函数
# ---------------------------------------------------------------------------

def _monthly_mortgage_payment(
    principal: float,
    annual_rate: float,
    years: int,
) -> float:
    """等额本息月供计算。

    Args:
        principal: 贷款本金（元）。
        annual_rate: 年利率（小数，如 0.031）。
        years: 贷款年限。

    Returns:
        每月还款额（元）。
    """
    if principal <= 0 or years <= 0:
        return 0.0
    if annual_rate <= 0:
        return principal / (years * 12)
    rate_m = annual_rate / 12
    months = years * 12
    payment = principal * rate_m * (1 + rate_m) ** months / (
        (1 + rate_m) ** months - 1
    )
    return payment


def _rate_investment(
    gross_yield: float,
    net_yield: float,
    payback_years: float,
    price_to_income: float,
    payment_to_income: float,
) -> str:
    """根据多维度指标给出投资评级（优/良/中/差）和说明。"""
    score = 0

    # 毛租金回报率
    if gross_yield >= 0.04:
        score += 3
    elif gross_yield >= 0.025:
        score += 2
    elif gross_yield >= 0.015:
        score += 1

    # 净租金回报率
    if net_yield >= 0.03:
        score += 3
    elif net_yield >= 0.02:
        score += 2
    elif net_yield >= 0.01:
        score += 1

    # 回本年数
    if payback_years <= 25:
        score += 3
    elif payback_years <= 35:
        score += 2
    elif payback_years <= 50:
        score += 1

    # 房价收入比
    if price_to_income <= 6:
        score += 3
    elif price_to_income <= 9:
        score += 2
    elif price_to_income <= 15:
        score += 1

    # 月供收入比
    if payment_to_income <= 0.30:
        score += 3
    elif payment_to_income <= 0.50:
        score += 2
    elif payment_to_income <= 0.70:
        score += 1

    # 总分 0-15 → 评级
    if score >= 12:
        rating = "优"
        comment = "投资价值突出，租金回报率高、负担合理，建议重点关注"
    elif score >= 8:
        rating = "良"
        comment = "投资价值较好，整体指标健康，可适当配置"
    elif score >= 5:
        rating = "中"
        comment = "投资回报一般，需结合个人财务状况审慎决策"
    else:
        rating = "差"
        comment = "投资性价比偏低，租金回报不足以覆盖持有成本，建议谨慎"

    return f"{rating}（{score}/15分）—— {comment}"


def _estimate_floor_price(city_data: dict) -> float:
    """简化估算城市理论底价（元/㎡）。

    基于 estimate_total_development_cost 逻辑，使用城市平均地价和高层住宅中等品质。
    """
    tier = city_data["tier"]
    land_price = city_data["avg_land_price"]
    try:
        cost_info = estimate_total_development_cost(
            land_cost_per_sqm=land_price,
            building_type="高层住宅",
            city_tier=tier,
            level="mid",
        )
        return cost_info["开发总成本"]
    except (ValueError, KeyError):
        # 回退：简单按 地价 + 建安 * 1.3 估算
        try:
            construction = get_construction_cost("高层住宅", tier, "mid")
        except ValueError:
            construction = 2000.0
        return land_price + construction * 1.3


def _policy_direction_for_city(city_data: dict) -> str:
    """根据城市等级和库存推测政策方向。"""
    tier = city_data["tier"]
    inv = city_data.get("inventory_months", 18)
    yoy = city_data.get("price_change_yoy", 0)

    if tier >= 3 or inv > 20 or yoy < -0.10:
        return "宽松"
    if tier == 1 and inv < 12:
        return "收紧"
    return "中性偏宽松"


# ---------------------------------------------------------------------------
# 公开工具函数
# ---------------------------------------------------------------------------

def calculate_investment_return(
    city: str,
    area_sqm: float = 100,
    price_per_sqm: float = 0,
    is_first_home: bool = True,
    loan_years: int = 30,
) -> str:
    """计算指定城市房产的投资回报指标。

    综合计算总价、首付、月供（等额本息）、月租金收入，
    并推导毛/净租金回报率、回本年数、房价收入比、月供收入比，
    最终给出投资评级（优/良/中/差）。

    Args:
        city: 城市名称（中文）。
        area_sqm: 房屋面积（㎡），默认 100。
        price_per_sqm: 单价（元/㎡），为 0 时使用城市均价。
        is_first_home: 是否首套房，影响首付比例和利率。
        loan_years: 贷款年限，默认 30 年。

    Returns:
        中文格式化的投资指标分析字符串。
    """
    try:
        city_info = get_city(city)
        if city_info is None:
            available = "、".join(list(CITY_DATA.keys())[:10]) + "……"
            return f"❌ 未找到城市「{city}」的数据。支持的城市包括：{available}"

        # 基础数据
        avg_price = city_info["avg_new_home_price"]
        unit_price = price_per_sqm if price_per_sqm > 0 else avg_price
        total_price = unit_price * area_sqm

        # 首付与贷款
        if is_first_home:
            dp_ratio = city_info.get("down_payment_ratio_first", 0.20)
            rate = city_info.get("mortgage_rate_first", 0.031)
        else:
            dp_ratio = city_info.get("down_payment_ratio_second", 0.30)
            rate = city_info.get("mortgage_rate_second", 0.035)

        down_payment = total_price * dp_ratio
        loan_amount = total_price - down_payment
        monthly_payment = _monthly_mortgage_payment(loan_amount, rate, loan_years)

        # 租金收入
        avg_rent = city_info.get("avg_rent_per_sqm", 0)
        monthly_rent = avg_rent * area_sqm

        # 回报率
        annual_rent = monthly_rent * 12
        gross_yield = annual_rent / total_price if total_price > 0 else 0
        # 净租金 = 毛租金 - 物业费(约3元/㎡·月) - 空置损失(5%) - 维修折旧(5%)
        monthly_cost = area_sqm * 3  # 物业费
        net_monthly_rent = monthly_rent * 0.90 - monthly_cost  # 扣空置5%+维修5%+物业
        net_annual_rent = max(net_monthly_rent * 12, 0)
        net_yield = net_annual_rent / total_price if total_price > 0 else 0

        # 回本年数
        payback = total_price / annual_rent if annual_rent > 0 else 999

        # 房价收入比：假设双职工家庭
        per_capita_income = city_info.get("per_capita_income", 50000)
        household_income = per_capita_income * 2
        standard_total = avg_price * 90  # 按 90㎡ 标准住房计算
        price_to_income = standard_total / household_income if household_income > 0 else 999

        # 月供收入比
        monthly_income = household_income / 12
        payment_to_income = (
            monthly_payment / monthly_income if monthly_income > 0 else 999
        )

        # 评级
        assessment = _rate_investment(
            gross_yield, net_yield, payback, price_to_income, payment_to_income
        )

        metrics = InvestmentMetrics(
            city=city_info["city"],
            property_price_per_sqm=unit_price,
            property_size_sqm=area_sqm,
            total_price=total_price,
            down_payment=down_payment,
            monthly_mortgage=monthly_payment,
            monthly_rent_income=monthly_rent,
            gross_rental_yield=gross_yield,
            net_rental_yield=net_yield,
            payback_years=payback,
            price_to_income_ratio=price_to_income,
            monthly_payment_to_income=payment_to_income,
            assessment=assessment,
        )

        # 附加补充信息
        extra = (
            f"\n\n📋 计算参数：\n"
            f"  {'首套' if is_first_home else '二套'}房 | "
            f"首付比例 {format_percentage(dp_ratio)} | "
            f"贷款利率 {format_percentage(rate)} | "
            f"贷款 {loan_years} 年\n"
            f"  贷款金额：{format_currency(loan_amount)}\n"
            f"  家庭年收入（双职工估算）：{format_currency(household_income)}"
        )

        return metrics.to_summary() + extra

    except Exception as e:
        return f"❌ 计算投资回报时发生错误：{e}"


def assess_affordability(
    city: str,
    annual_household_income: float = 0,
) -> str:
    """评估指定城市的购房负担能力。

    计算 90/120/144 ㎡ 住房的房价收入比，以及月供占收入比例，
    并与健康基准对比（房价收入比 < 6 为健康，6-9 为适中，> 9 为压力大）。

    Args:
        city: 城市名称（中文）。
        annual_household_income: 家庭年收入（元），为 0 时使用
            城市人均可支配收入 × 2（双职工家庭）。

    Returns:
        中文格式化的购房负担能力分析字符串。
    """
    try:
        city_info = get_city(city)
        if city_info is None:
            return f"❌ 未找到城市「{city}」的数据。"

        city_name = city_info["city"]
        avg_price = city_info["avg_new_home_price"]
        per_capita_income = city_info.get("per_capita_income", 50000)

        # 家庭收入
        if annual_household_income > 0:
            household_income = annual_household_income
            income_source = f"用户输入：{format_currency(household_income)}/年"
        else:
            household_income = per_capita_income * 2
            income_source = (
                f"城市人均收入 {format_currency(per_capita_income)} × 2 = "
                f"{format_currency(household_income)}/年"
            )

        monthly_income = household_income / 12

        # 贷款参数（首套）
        dp_ratio = city_info.get("down_payment_ratio_first", 0.20)
        rate = city_info.get("mortgage_rate_first", 0.031)

        areas = [90, 120, 144]
        lines: list[str] = []
        lines.append(f"【{city_name} 购房负担能力评估】\n")
        lines.append(f"家庭年收入：{income_source}")
        lines.append(f"新房均价：{avg_price:.0f} 元/㎡")
        lines.append(f"首套首付比例：{format_percentage(dp_ratio)} | "
                      f"贷款利率：{format_percentage(rate)}\n")
        lines.append(f"{'面积':>6} | {'总价':>10} | {'房价收入比':>8} | "
                      f"{'月供':>10} | {'月供/收入':>8} | 评价")
        lines.append("-" * 72)

        for area in areas:
            total = avg_price * area
            loan = total * (1 - dp_ratio)
            monthly_pay = _monthly_mortgage_payment(loan, rate, 30)
            ratio = total / household_income if household_income > 0 else 999
            pay_ratio = monthly_pay / monthly_income if monthly_income > 0 else 999

            # 评价
            if ratio < 6:
                level = "✅ 健康"
            elif ratio < 9:
                level = "⚠️ 适中"
            elif ratio < 15:
                level = "🔴 压力大"
            else:
                level = "🔴 严重偏高"

            lines.append(
                f"{area:>4}㎡ | {format_currency(total):>10} | "
                f"{ratio:>8.1f} | {format_currency(monthly_pay):>10} | "
                f"{format_percentage(pay_ratio):>8} | {level}"
            )

        # 总结
        base_ratio = avg_price * 90 / household_income if household_income > 0 else 999
        lines.append("")
        lines.append("📊 基准对比（国际通行标准）：")
        lines.append("  房价收入比 < 6：居民可合理负担")
        lines.append("  房价收入比 6-9：中等压力，需合理规划")
        lines.append("  房价收入比 > 9：负担较重，购房压力显著")
        lines.append("")

        if base_ratio < 6:
            lines.append(
                f"💡 {city_name} 90㎡住房房价收入比为 {base_ratio:.1f}，"
                f"处于健康区间，居民购房负担相对合理。"
            )
        elif base_ratio < 9:
            lines.append(
                f"💡 {city_name} 90㎡住房房价收入比为 {base_ratio:.1f}，"
                f"处于适中区间，建议量力而行、合理利用公积金等工具。"
            )
        elif base_ratio < 15:
            lines.append(
                f"💡 {city_name} 90㎡住房房价收入比为 {base_ratio:.1f}，"
                f"负担较重。建议考虑近郊或更小面积，关注政策补贴。"
            )
        else:
            lines.append(
                f"💡 {city_name} 90㎡住房房价收入比为 {base_ratio:.1f}，"
                f"负担极重。普通家庭购房非常困难，建议长期规划或考虑租房。"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 评估购房负担能力时发生错误：{e}"


def evaluate_investment_timing(city: str) -> str:
    """评估指定城市的房产投资时机。

    综合以下信号进行评分（0-100）：
    - 当前价格与理论底价的距离
    - 库存去化周期（< 12 个月偏紧，12-18 平衡，> 18 偏高）
    - 房价同比变化趋势
    - 政策方向

    并判断市场周期阶段（上升/顶部/下降/底部）。

    Args:
        city: 城市名称（中文）。

    Returns:
        中文格式化的投资时机评估字符串。
    """
    try:
        city_info = get_city(city)
        if city_info is None:
            return f"❌ 未找到城市「{city}」的数据。"

        city_name = city_info["city"]
        current_price = city_info["avg_new_home_price"]
        inventory_months = city_info.get("inventory_months", 18)
        yoy = city_info.get("price_change_yoy", 0)

        # 1. 理论底价距离评分 (0-30)
        floor_price = _estimate_floor_price(city_info)
        if floor_price > 0:
            distance_pct = (current_price - floor_price) / floor_price
        else:
            distance_pct = 0

        if distance_pct <= 0:
            # 已跌破成本线
            price_score = 30
        elif distance_pct <= 0.10:
            price_score = 25
        elif distance_pct <= 0.20:
            price_score = 20
        elif distance_pct <= 0.40:
            price_score = 12
        elif distance_pct <= 0.60:
            price_score = 6
        else:
            price_score = 0

        # 2. 库存去化评分 (0-25)
        if inventory_months <= 8:
            inv_score = 25
            inv_status = "供不应求"
        elif inventory_months <= 12:
            inv_score = 20
            inv_status = "供给偏紧"
        elif inventory_months <= 18:
            inv_score = 15
            inv_status = "供需平衡"
        elif inventory_months <= 24:
            inv_score = 8
            inv_status = "库存偏高"
        elif inventory_months <= 30:
            inv_score = 4
            inv_status = "库存积压"
        else:
            inv_score = 0
            inv_status = "严重过剩"

        # 3. 价格趋势评分 (0-25)
        # 下跌末期（跌幅收窄）或刚转正是较好时机
        if -0.03 <= yoy <= 0.02:
            trend_score = 25  # 底部企稳
        elif -0.06 <= yoy < -0.03:
            trend_score = 20  # 跌幅收窄
        elif 0.02 < yoy <= 0.08:
            trend_score = 18  # 温和上涨
        elif -0.10 <= yoy < -0.06:
            trend_score = 12  # 仍在下跌
        elif yoy > 0.08:
            trend_score = 8   # 过热，追高风险
        else:
            trend_score = 5   # 大幅下跌

        # 4. 政策方向评分 (0-20)
        policy = _policy_direction_for_city(city_info)
        policy_scores = {"宽松": 20, "中性偏宽松": 15, "中性": 10, "收紧": 5}
        pol_score = policy_scores.get(policy, 10)

        # 总分
        total_score = price_score + inv_score + trend_score + pol_score
        total_score = max(0, min(100, total_score))

        # 市场周期判断
        if yoy > 0.05:
            cycle = "上升期"
        elif yoy > 0 and inventory_months < 15:
            cycle = "上升期"
        elif yoy >= -0.03 and inventory_months <= 18:
            cycle = "顶部/盘整期"
        elif yoy < -0.03 and yoy >= -0.08:
            cycle = "下降调整期"
        elif yoy < -0.08:
            cycle = "深度调整期"
        else:
            cycle = "底部筑底期"

        # 建议
        if total_score >= 75:
            recommendation = (
                "多维指标向好，当前为较佳入场时机。建议重点关注优质地段，"
                "积极筛选性价比房源。"
            )
        elif total_score >= 55:
            recommendation = (
                "市场具备一定投资价值，但部分指标存在不确定性。"
                "建议精选核心地段，控制仓位，分批建仓。"
            )
        elif total_score >= 35:
            recommendation = (
                "市场仍在调整中，建议保持观望、做好储备。"
                "可关注政策变化和成交量信号，等待更明确的企稳迹象。"
            )
        else:
            recommendation = (
                "市场下行压力较大，投资风险偏高。"
                "建议暂不入场，持币观望，等待市场出清和政策转向。"
            )

        timing = InvestmentTiming(
            city=city_name,
            current_price=current_price,
            theoretical_floor_price=round(floor_price),
            distance_to_floor_pct=round(distance_pct, 4),
            market_cycle_phase=cycle,
            inventory_status=f"{inv_status}（{inventory_months:.0f}个月）",
            policy_direction=policy,
            timing_score=total_score,
            recommendation=recommendation,
        )

        # 评分明细
        detail = (
            f"\n\n📐 评分明细：\n"
            f"  ├ 底价距离：{price_score}/30（溢价 {format_percentage(distance_pct)}）\n"
            f"  ├ 库存状况：{inv_score}/25（{inv_status}）\n"
            f"  ├ 价格趋势：{trend_score}/25（同比 {format_percentage(yoy)}）\n"
            f"  └ 政策方向：{pol_score}/20（{policy}）"
        )

        return timing.to_summary() + detail

    except Exception as e:
        return f"❌ 评估投资时机时发生错误：{e}"


def compare_investment_cities(city_names: str) -> str:
    """对比多个城市的投资指标并排名。

    综合对比租金回报率、房价收入比、库存去化周期、投资时机评分等，
    按投资吸引力进行排名。

    Args:
        city_names: 逗号分隔的城市名称（如 ``"北京,上海,成都,长沙"``）。

    Returns:
        中文格式化的城市投资对比排名表。
    """
    try:
        names = [n.strip() for n in city_names.split(",") if n.strip()]
        if len(names) < 2:
            return "❌ 请至少提供两个城市进行比较，以逗号分隔。"

        rows: list[dict] = []
        errors: list[str] = []

        for name in names:
            info = get_city(name)
            if info is None:
                errors.append(name)
                continue

            cname = info["city"]
            avg_price = info["avg_new_home_price"]
            rent = info.get("avg_rent_per_sqm", 0)
            inv_months = info.get("inventory_months", 0)
            yoy = info.get("price_change_yoy", 0)
            per_capita = info.get("per_capita_income", 50000)
            household_income = per_capita * 2

            # 租金回报率（毛）
            gross_yield = (rent * 12) / avg_price if avg_price > 0 else 0

            # 房价收入比（90㎡）
            pir = avg_price * 90 / household_income if household_income > 0 else 999

            # 理论底价距离
            floor_price = _estimate_floor_price(info)
            dist = (
                (avg_price - floor_price) / floor_price
                if floor_price > 0
                else 0
            )

            # 简化时机评分复用
            # 底价距离分
            if dist <= 0:
                ps = 30
            elif dist <= 0.10:
                ps = 25
            elif dist <= 0.20:
                ps = 20
            elif dist <= 0.40:
                ps = 12
            else:
                ps = 4

            # 库存分
            if inv_months <= 8:
                ivs = 25
            elif inv_months <= 12:
                ivs = 20
            elif inv_months <= 18:
                ivs = 15
            elif inv_months <= 24:
                ivs = 8
            else:
                ivs = 2

            # 趋势分
            if -0.03 <= yoy <= 0.02:
                ts = 25
            elif -0.06 <= yoy < -0.03:
                ts = 20
            elif 0.02 < yoy <= 0.08:
                ts = 18
            elif -0.10 <= yoy < -0.06:
                ts = 12
            else:
                ts = 5

            # 政策分
            policy = _policy_direction_for_city(info)
            pol_map = {"宽松": 20, "中性偏宽松": 15, "中性": 10, "收紧": 5}
            pols = pol_map.get(policy, 10)

            timing_score = max(0, min(100, ps + ivs + ts + pols))

            # 综合投资吸引力评分：租金回报(30%) + 房价收入比(25%) + 库存(20%) + 时机(25%)
            yield_norm = min(gross_yield / 0.05, 1.0) * 30
            pir_norm = max(0, min(1.0, (20 - pir) / 14)) * 25
            inv_norm = max(0, min(1.0, (36 - inv_months) / 28)) * 20
            timing_norm = timing_score / 100 * 25
            attractiveness = yield_norm + pir_norm + inv_norm + timing_norm

            rows.append({
                "city": cname,
                "avg_price": avg_price,
                "gross_yield": gross_yield,
                "price_to_income": pir,
                "inventory_months": inv_months,
                "yoy": yoy,
                "timing_score": timing_score,
                "attractiveness": round(attractiveness, 1),
                "floor_price": round(floor_price),
                "policy": policy,
            })

        if not rows:
            return f"❌ 所有城市均未找到数据：{'、'.join(errors)}"

        # 按吸引力排序
        rows.sort(key=lambda r: r["attractiveness"], reverse=True)

        # 构建输出
        lines: list[str] = []
        city_list = "、".join(r["city"] for r in rows)
        lines.append(f"【城市投资对比】{city_list}\n")

        # 表头
        lines.append(
            f"{'排名':>4} | {'城市':>4} | {'均价(元/㎡)':>10} | "
            f"{'毛租金回报':>8} | {'房价收入比':>8} | "
            f"{'库存(月)':>7} | {'同比':>7} | "
            f"{'时机分':>5} | {'综合分':>5}"
        )
        lines.append("-" * 90)

        for i, r in enumerate(rows, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f" {i}")
            lines.append(
                f"{medal:>4} | {r['city']:>4} | "
                f"{r['avg_price']:>10,.0f} | "
                f"{format_percentage(r['gross_yield']):>8} | "
                f"{r['price_to_income']:>8.1f} | "
                f"{r['inventory_months']:>7.0f} | "
                f"{format_percentage(r['yoy']):>7} | "
                f"{r['timing_score']:>5} | "
                f"{r['attractiveness']:>5.1f}"
            )

        # 总结
        best = rows[0]
        worst = rows[-1]
        lines.append("")
        lines.append("📊 对比总结：")
        lines.append(
            f"  🏆 投资吸引力最高：{best['city']}（综合 {best['attractiveness']:.1f} 分）"
        )
        if len(rows) >= 2:
            lines.append(
                f"  📉 投资吸引力最低：{worst['city']}（综合 {worst['attractiveness']:.1f} 分）"
            )

        # 各维度冠军
        best_yield = max(rows, key=lambda r: r["gross_yield"])
        best_pir = min(rows, key=lambda r: r["price_to_income"])
        best_inv = min(rows, key=lambda r: r["inventory_months"])
        lines.append(f"\n  各维度最优：")
        lines.append(
            f"  · 租金回报率最高：{best_yield['city']}（{format_percentage(best_yield['gross_yield'])}）"
        )
        lines.append(
            f"  · 房价收入比最低：{best_pir['city']}（{best_pir['price_to_income']:.1f}）"
        )
        lines.append(
            f"  · 库存最健康：{best_inv['city']}（{best_inv['inventory_months']:.0f} 个月）"
        )

        if errors:
            lines.append(f"\n⚠️ 以下城市未找到数据，已跳过：{'、'.join(errors)}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 对比城市投资指标时发生错误：{e}"
