"""中国住宅房地产投资交易指南 MCP Server

使用 FastMCP 框架注册所有工具，供 AI 助手（Claude Desktop / Cursor 等）调用。
"""

from mcp.server.fastmcp import FastMCP

from china_real_estate_mcp.tools.cost_calculator import (
    calculate_construction_cost,
    calculate_theoretical_floor_price,
    estimate_development_cost,
)
from china_real_estate_mcp.tools.market_analysis import (
    get_city_market_overview,
    compare_cities,
    analyze_price_position,
)
from china_real_estate_mcp.tools.demographics import (
    get_demographic_profile,
    analyze_demographic_impact,
    forecast_housing_demand,
)
from china_real_estate_mcp.tools.investment_metrics import (
    calculate_investment_return,
    assess_affordability,
    evaluate_investment_timing,
    compare_investment_cities,
)
from china_real_estate_mcp.tools.policy_risk import (
    get_housing_policy,
    assess_market_risk,
)

mcp = FastMCP(
    "china-real-estate",
    instructions="🏠 中国住宅房地产投资交易指南 — 提供成本测算、市场分析、人口结构、投资评估、政策风险等专业工具",
)

# ── 成本计算器 ─────────────────────────────────────────────

@mcp.tool()
def tool_calculate_construction_cost(
    city: str, building_type: str = "高层住宅", quality: str = "mid"
) -> str:
    """计算指定城市的建安成本明细。

    Args:
        city: 城市名称（如"长沙"、"北京"）
        building_type: 建筑类型（多层住宅/小高层/高层住宅/超高层）
        quality: 品质等级（low/mid/high）
    """
    return calculate_construction_cost(city, building_type, quality)


@mcp.tool()
def tool_calculate_theoretical_floor_price(
    city: str, building_type: str = "高层住宅", use_core_area: bool = False
) -> str:
    """测算城市住宅的理论底价（成本价），并与当前市场价对比。

    Args:
        city: 城市名称
        building_type: 建筑类型
        use_core_area: 是否使用核心区数据（地价和房价均取核心区）
    """
    return calculate_theoretical_floor_price(city, building_type, use_core_area)


@mcp.tool()
def tool_estimate_development_cost(
    city: str,
    building_type: str = "高层住宅",
    total_area_sqm: float = 100000,
    use_core_area: bool = False,
) -> str:
    """估算房地产开发项目的完整成本（含土地、建安、税费、营销、财务等）。

    Args:
        city: 城市名称
        building_type: 建筑类型
        total_area_sqm: 项目总建筑面积（㎡），默认10万㎡
        use_core_area: 是否使用核心区地价
    """
    return estimate_development_cost(city, building_type, total_area_sqm, use_core_area)


# ── 市场行情 ───────────────────────────────────────────────

@mcp.tool()
def tool_get_city_market_overview(city: str) -> str:
    """获取城市房地产市场概览：房价、成交量、库存、租金等核心指标。

    Args:
        city: 城市名称
    """
    return get_city_market_overview(city)


@mcp.tool()
def tool_compare_cities(city_names: str) -> str:
    """多城市房地产市场对比分析。

    Args:
        city_names: 逗号分隔的城市名称（如"长沙,武汉,成都"）
    """
    return compare_cities(city_names)


@mcp.tool()
def tool_analyze_price_position(city: str) -> str:
    """分析城市当前房价所处位置（相对成本底、同级城市、趋势方向）。

    Args:
        city: 城市名称
    """
    return analyze_price_position(city)


# ── 人口结构 ───────────────────────────────────────────────

@mcp.tool()
def tool_get_demographic_profile(city: str) -> str:
    """获取城市人口结构画像：总量、增长、年龄结构、城镇化率等。

    Args:
        city: 城市名称
    """
    return get_demographic_profile(city)


@mcp.tool()
def tool_analyze_demographic_impact(city: str) -> str:
    """分析人口结构变化对住房需求的影响（老龄化、出生率、人口流动）。

    Args:
        city: 城市名称
    """
    return analyze_demographic_impact(city)


@mcp.tool()
def tool_forecast_housing_demand(city: str, years: int = 10) -> str:
    """预测未来住房需求变化趋势。

    Args:
        city: 城市名称
        years: 预测年数（默认10年）
    """
    return forecast_housing_demand(city, years)


# ── 投资指标 ───────────────────────────────────────────────

@mcp.tool()
def tool_calculate_investment_return(
    city: str,
    area_sqm: float = 100,
    price_per_sqm: float = 0,
    is_first_home: bool = True,
    loan_years: int = 30,
) -> str:
    """计算住宅投资回报指标：租金回报率、回本周期、月供收入比等。

    Args:
        city: 城市名称
        area_sqm: 房屋面积（㎡），默认100㎡
        price_per_sqm: 单价（元/㎡），0则使用城市均价
        is_first_home: 是否首套房
        loan_years: 贷款年限
    """
    return calculate_investment_return(city, area_sqm, price_per_sqm, is_first_home, loan_years)


@mcp.tool()
def tool_assess_affordability(city: str, annual_household_income: float = 0) -> str:
    """评估城市住房购买力与负担能力。

    Args:
        city: 城市名称
        annual_household_income: 家庭年收入（元），0则使用城市人均收入×2
    """
    return assess_affordability(city, annual_household_income)


@mcp.tool()
def tool_evaluate_investment_timing(city: str) -> str:
    """评估当前是否是投资该城市房产的好时机（综合评分0-100）。

    Args:
        city: 城市名称
    """
    return evaluate_investment_timing(city)


@mcp.tool()
def tool_compare_investment_cities(city_names: str) -> str:
    """多城市投资吸引力排名对比。

    Args:
        city_names: 逗号分隔的城市名称
    """
    return compare_investment_cities(city_names)


# ── 政策与风险 ─────────────────────────────────────────────

@mcp.tool()
def tool_get_housing_policy(city: str) -> str:
    """查询城市当前住房政策（限购、贷款、补贴等）。

    Args:
        city: 城市名称
    """
    return get_housing_policy(city)


@mcp.tool()
def tool_assess_market_risk(city: str) -> str:
    """综合评估城市房地产市场风险（6维度评分）。

    Args:
        city: 城市名称
    """
    return assess_market_risk(city)


# ── 入口 ───────────────────────────────────────────────────

def main():
    """启动 MCP Server（stdio 模式）"""
    mcp.run()


if __name__ == "__main__":
    main()
