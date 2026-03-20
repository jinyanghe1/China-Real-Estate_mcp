"""
政策与风险评估工具模块

提供城市住房政策查询和市场风险综合评估功能。
基于城市等级、市场数据和人口结构进行分析。
"""

from __future__ import annotations

from ..data.city_data import get_city
from ..data.demographics_data import DEMOGRAPHICS_DATA
from ..models.schemas import PolicySummary, RiskAssessment


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------

def _clamp(value: float, lo: float = 0, hi: float = 100) -> int:
    """将数值裁剪到 [lo, hi] 并取整。"""
    return int(max(lo, min(hi, round(value))))


# ---------------------------------------------------------------------------
# 公开工具函数
# ---------------------------------------------------------------------------

def get_housing_policy(city: str) -> str:
    """查询指定城市当前住房政策摘要。

    根据城市等级和数据生成 2025 年最新政策概览，涵盖限购、贷款、
    补贴及其他政策方向。

    Args:
        city: 城市中文名称（支持模糊匹配）。

    Returns:
        中文政策摘要字符串；城市不存在时返回提示信息。
    """
    info = get_city(city)
    if info is None:
        return f"❌ 未找到城市「{city}」的数据，请检查城市名称。支持的城市包括：北京、上海、广州、深圳、成都、杭州等。"

    city_name: str = info["city"]
    tier: int = info["tier"]
    first_rate = info.get("mortgage_rate_first", 0.031)
    second_rate = info.get("mortgage_rate_second", 0.035)
    first_dp = info.get("down_payment_ratio_first", 0.15)
    second_dp = info.get("down_payment_ratio_second", 0.25)

    first_rate_bp = f"{first_rate * 100:.2f}%"
    second_rate_bp = f"{second_rate * 100:.2f}%"
    first_dp_pct = f"{first_dp * 100:.0f}%"
    second_dp_pct = f"{second_dp * 100:.0f}%"

    # ---- 按城市等级生成政策 ----
    if tier == 1:
        # 一线城市：核心区仍有限购，但已大幅放松
        if city_name in ("北京", "上海"):
            purchase = (
                f"核心区（城六区/内环内）非本市户籍限购1套，需连续5年社保或个税；"
                f"非核心区已放开限购，本市户籍家庭不限购。"
                f"2025年政策较2023年大幅放松。"
            )
        elif city_name == "深圳":
            purchase = (
                f"核心区（福田、南山、前海）非本市户籍限购1套，需3年社保；"
                f"龙岗、坪山、光明等区已全面取消限购。"
            )
        else:  # 广州
            purchase = (
                f"全市基本取消限购，仅越秀、天河部分区域非户籍限购1套；"
                f"为一线城市中限购最宽松的城市。"
            )
        loan = (
            f"首套房首付比例{first_dp_pct}，利率{first_rate_bp}（LPR-20bp左右）；"
            f"二套房首付比例{second_dp_pct}，利率{second_rate_bp}。"
            f"公积金贷款额度上调，支持\u201c商转公\u201d。"
        )
        subsidy = "暂无直接购房补贴，部分区有人才安居补贴和落户购房优惠。"
        others = [
            "存量房贷利率已统一下调至LPR水平",
            "二手房\u201c带押过户\u201d全面推行，降低交易成本",
            "支持\u201c以旧换新\u201d，部分区政府搭建置换平台",
            "个人住房转让增值税免征年限由5年调为2年",
        ]
        direction = "宽松"

    elif tier == 2:
        purchase = (
            f"已全面取消限购，不限户籍、套数。"
            f"外地购房者与本地居民享同等购房权利。"
        )
        loan = (
            f"首套房首付比例{first_dp_pct}，利率{first_rate_bp}（LPR-20bp左右）；"
            f"二套房首付比例{second_dp_pct}，利率{second_rate_bp}。"
            f"公积金贷款额度上调，支持异地公积金贷款。"
        )
        subsidy = "部分城市对新市民、青年人才有购房补贴（1-10万元不等），契税补贴常态化。"
        others = [
            "存量房贷利率已统一下调",
            "推行\u201c以旧换新\u201d置换补贴政策",
            "二手房交易增值税免征年限调整为2年",
            "支持多孩家庭增加公积金贷款额度",
            "部分城市试点现房销售制度",
        ]
        direction = "宽松"

    elif tier == 3:
        purchase = "完全取消限购，不限户籍、套数、面积。购房零门槛。"
        loan = (
            f"首套房首付比例最低{first_dp_pct}，利率{first_rate_bp}；"
            f"二套房首付比例{second_dp_pct}，利率{second_rate_bp}。"
            f"支持公积金异地贷款，部分银行可做零首付产品。"
        )
        subsidy = (
            "购房补贴力度较大：新房契税全额补贴，部分城市额外给予"
            "200-500元/㎡购房补贴；人才购房补贴最高可达20万元。"
        )
        others = [
            "存量房贷利率已下调",
            "农民进城购房补贴专项政策",
            "多孩家庭购房额外补贴",
            "商品房可退房退款试点",
            "部分城市政府直接收购存量房转为保障房",
        ]
        direction = "宽松"

    else:  # tier 4, 5
        purchase = "完全取消限购，无任何购房限制。"
        loan = (
            f"首套房首付比例最低{first_dp_pct}，利率{first_rate_bp}；"
            f"二套房首付比例{second_dp_pct}，利率{second_rate_bp}。"
            f"部分银行提供利率折扣和灵活还款方案。"
        )
        subsidy = (
            "购房补贴力度最大：契税全额返还，购房补贴300-800元/㎡，"
            "人才购房补贴最高30万元。部分县市推出\u201c买房送车位\u201d\u201c买房送家电\u201d活动。"
        )
        others = [
            "政府收购存量房转保障房",
            "农民进城购房补贴及子女入学优惠",
            "多孩家庭购房额外补贴及税费减免",
            "鼓励企事业单位团购商品房",
            "房票安置政策全面推行",
        ]
        direction = "宽松"

    summary = PolicySummary(
        city=city_name,
        purchase_restriction=purchase,
        loan_policy=loan,
        subsidy_policy=subsidy,
        other_policies=others,
        policy_direction=direction,
        last_updated="2025年",
    )
    return summary.to_summary()


def assess_market_risk(city: str) -> str:
    """对指定城市房地产市场进行综合风险评估。

    从库存、价格、人口、经济、供需、政策六个维度进行打分（0-100，
    分数越高风险越大），加权计算综合风险分。

    Args:
        city: 城市中文名称（支持模糊匹配）。

    Returns:
        中文风险评估摘要字符串；城市不存在时返回提示信息。
    """
    info = get_city(city)
    if info is None:
        return f"❌ 未找到城市「{city}」的数据，请检查城市名称。支持的城市包括：北京、上海、广州、深圳、成都、杭州等。"

    city_name: str = info["city"]
    tier: int = info["tier"]
    demo = DEMOGRAPHICS_DATA.get(city_name, {})

    # ---- 1. 库存风险 (weight=0.25) ----
    inv_months = info.get("inventory_months", 18)
    if inv_months <= 6:
        inv_risk = 10
    elif inv_months <= 12:
        inv_risk = 20 + (inv_months - 6) * 5
    elif inv_months <= 18:
        inv_risk = 50 + (inv_months - 12) * 5
    elif inv_months <= 24:
        inv_risk = 80 + (inv_months - 18) * 2
    else:
        inv_risk = 90 + min((inv_months - 24), 5) * 2

    # ---- 2. 价格风险 (weight=0.20) ----
    yoy = info.get("price_change_yoy", 0)
    if yoy >= 0:
        price_risk = max(0, 20 - yoy * 200)
    elif yoy >= -0.05:
        price_risk = 30 + abs(yoy) * 600
    elif yoy >= -0.10:
        price_risk = 60 + (abs(yoy) - 0.05) * 600
    else:
        price_risk = 90 + min((abs(yoy) - 0.10), 0.05) * 200

    # ---- 3. 人口风险 (weight=0.20) ----
    aging = demo.get("age_60_plus_pct", 0.18)
    growth = demo.get("population_growth_rate", 0)
    net_mig = demo.get("net_migration_10k", 0)

    aging_score = min(100, max(0, (aging - 0.10) / 0.20 * 100))
    if growth >= 0.005:
        growth_score = 10
    elif growth >= 0:
        growth_score = 30 + (0.005 - growth) / 0.005 * 30
    else:
        growth_score = 60 + min(abs(growth) / 0.01, 1) * 40

    if net_mig >= 10:
        mig_score = 10
    elif net_mig >= 0:
        mig_score = 20 + (10 - net_mig) * 3
    else:
        mig_score = 50 + min(abs(net_mig) / 20, 1) * 50

    demo_risk = aging_score * 0.35 + growth_score * 0.35 + mig_score * 0.30

    # ---- 4. 经济风险 (weight=0.10) ----
    gdp = info.get("gdp_billion_yuan", 500)
    income = info.get("per_capita_income", 40000)

    if gdp >= 2000:
        gdp_score = 15
    elif gdp >= 1000:
        gdp_score = 30 + (2000 - gdp) / 1000 * 20
    elif gdp >= 500:
        gdp_score = 50 + (1000 - gdp) / 500 * 20
    else:
        gdp_score = 70 + min((500 - gdp) / 300, 1) * 30

    if income >= 60000:
        income_score = 15
    elif income >= 45000:
        income_score = 30 + (60000 - income) / 15000 * 30
    else:
        income_score = 60 + min((45000 - income) / 15000, 1) * 40

    econ_risk = gdp_score * 0.5 + income_score * 0.5

    # ---- 5. 供需风险 (weight=0.15) ----
    volume = info.get("transaction_volume_10k_sqm", 500)
    price = info.get("avg_new_home_price", 15000)
    rent = info.get("avg_rent_per_sqm", 30)

    # 租售比作为供需关系的代理指标
    rent_price_ratio_annual = (rent * 12) / price if price > 0 else 0.02
    if rent_price_ratio_annual >= 0.04:
        rp_score = 15
    elif rent_price_ratio_annual >= 0.025:
        rp_score = 30 + (0.04 - rent_price_ratio_annual) / 0.015 * 30
    else:
        rp_score = 60 + min((0.025 - rent_price_ratio_annual) / 0.01, 1) * 40

    # 成交量：量越低风险越高（按城市规模归一化）
    pop = demo.get("population_10k", 500)
    vol_per_capita = volume / pop if pop > 0 else 0.5
    if vol_per_capita >= 1.0:
        vol_score = 15
    elif vol_per_capita >= 0.5:
        vol_score = 30 + (1.0 - vol_per_capita) / 0.5 * 30
    else:
        vol_score = 60 + min((0.5 - vol_per_capita) / 0.3, 1) * 40

    sd_risk = rp_score * 0.5 + vol_score * 0.5

    # ---- 6. 政策风险 (weight=0.10) ----
    # 一线城市仍有限购 → 政策收紧风险更高；低线城市宽松到底 → 政策空间有限
    if tier == 1:
        pol_risk = 35
    elif tier == 2:
        pol_risk = 25
    elif tier == 3:
        pol_risk = 40  # 政策已用尽，若效果不佳则缺乏后续手段
    else:
        pol_risk = 55  # 政策已完全放开但效果有限

    # ---- 加权汇总 ----
    inv_risk = _clamp(inv_risk)
    price_risk = _clamp(price_risk)
    demo_risk = _clamp(demo_risk)
    econ_risk = _clamp(econ_risk)
    sd_risk = _clamp(sd_risk)
    pol_risk = _clamp(pol_risk)

    overall = (
        inv_risk * 0.25
        + price_risk * 0.20
        + demo_risk * 0.20
        + econ_risk * 0.10
        + sd_risk * 0.15
        + pol_risk * 0.10
    )
    overall = _clamp(overall)

    risk_factors = {
        "库存风险": inv_risk,
        "价格风险": price_risk,
        "人口风险": demo_risk,
        "经济风险": econ_risk,
        "供需风险": sd_risk,
        "政策风险": pol_risk,
    }

    # ---- 风险等级 ----
    if overall <= 25:
        risk_level = "低"
    elif overall <= 40:
        risk_level = "中低"
    elif overall <= 55:
        risk_level = "中"
    elif overall <= 70:
        risk_level = "中高"
    else:
        risk_level = "高"

    # ---- 关键风险识别 ----
    key_risks: list[str] = []
    if inv_risk >= 70:
        key_risks.append(f"库存去化周期达{inv_months:.0f}个月，去化压力极大")
    elif inv_risk >= 50:
        key_risks.append(f"库存去化周期{inv_months:.0f}个月，高于健康水平")

    if price_risk >= 70:
        key_risks.append(f"房价同比下跌{abs(yoy)*100:.1f}%，下行趋势明显")
    elif price_risk >= 50:
        key_risks.append(f"房价同比变动{yoy*100:+.1f}%，价格承压")

    if demo_risk >= 60:
        aging_pct = aging * 100
        issues = []
        if aging >= 0.20:
            issues.append(f"老龄化率{aging_pct:.1f}%")
        if growth < 0:
            issues.append("人口负增长")
        if net_mig < 0:
            issues.append("人口净流出")
        if issues:
            key_risks.append(f"人口结构不利：{'、'.join(issues)}")

    if econ_risk >= 55:
        key_risks.append("经济基本面偏弱，居民收入水平有限")

    if sd_risk >= 60:
        key_risks.append("供需失衡，租售比偏低或成交低迷")

    if pol_risk >= 45:
        if tier >= 3:
            key_risks.append("刺激政策空间已基本用尽，后续提振手段有限")
        else:
            key_risks.append("政策仍存在收紧可能，需关注调控方向变化")

    if not key_risks:
        key_risks.append("当前未发现突出风险点，市场整体较为健康")

    # ---- 缓解建议 ----
    suggestions: list[str] = []
    if inv_risk >= 50:
        suggestions.append("优先选择去化良好的核心板块和品牌开发商项目")
    if price_risk >= 50:
        suggestions.append("关注价格止跌信号，可等待企稳后再入手")
    if demo_risk >= 50:
        suggestions.append("关注人口流入趋势，选择有产业支撑和年轻人口集聚的区域")
    if econ_risk >= 50:
        suggestions.append("控制杠杆比例，月供不超过家庭收入30%")
    if sd_risk >= 50:
        suggestions.append("重视租金回报率，选择租赁需求旺盛的地段")
    if pol_risk >= 40:
        suggestions.append("密切关注政策动向，利用当前宽松窗口期合理配置")

    if overall >= 60:
        suggestions.append("综合风险较高，建议以自住刚需为主，谨慎投资")
    elif overall >= 40:
        suggestions.append("风险适中，建议选择核心地段优质资产，分散投资风险")
    else:
        suggestions.append("整体风险可控，可适度关注改善和投资机会")

    if not suggestions:
        suggestions.append("市场风险较低，保持正常关注即可")

    assessment = RiskAssessment(
        city=city_name,
        overall_risk_score=overall,
        risk_factors=risk_factors,
        risk_level=risk_level,
        key_risks=key_risks,
        mitigation_suggestions=suggestions,
    )
    return assessment.to_summary()
