"""核心工具模块的单元测试"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

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
from china_real_estate_mcp.data.city_data import list_all_cities
from china_real_estate_mcp.models.schemas import format_currency, format_percentage


# ── 工具函数格式化 ─────────────────────────────────────────

class TestFormatUtils:
    def test_format_currency_wan(self):
        result = format_currency(1234567)
        assert "万" in result

    def test_format_percentage(self):
        result = format_percentage(0.0523)
        assert "5.23%" == result


# ── 成本计算器 ─────────────────────────────────────────────

class TestCostCalculator:
    def test_construction_cost_valid_city(self):
        result = calculate_construction_cost("长沙")
        assert "建安成本" in result or "成本" in result
        assert "❌" not in result

    def test_construction_cost_invalid_city(self):
        result = calculate_construction_cost("亚特兰蒂斯")
        assert "❌" in result or "未找到" in result or "找不到" in result or "不支持" in result

    def test_theoretical_floor_price(self):
        result = calculate_theoretical_floor_price("长沙")
        assert "理论" in result or "底价" in result or "成本" in result
        assert "长沙" in result

    def test_theoretical_floor_price_core_area(self):
        result = calculate_theoretical_floor_price("北京", use_core_area=True)
        assert "北京" in result

    def test_estimate_development_cost(self):
        result = estimate_development_cost("上海", total_area_sqm=50000)
        assert "上海" in result


# ── 市场行情 ───────────────────────────────────────────────

class TestMarketAnalysis:
    def test_city_overview(self):
        result = get_city_market_overview("深圳")
        assert "深圳" in result
        assert "❌" not in result

    def test_compare_cities(self):
        result = compare_cities("长沙,武汉,成都")
        assert "长沙" in result
        assert "武汉" in result
        assert "成都" in result

    def test_price_position(self):
        result = analyze_price_position("杭州")
        assert "杭州" in result


# ── 人口结构 ───────────────────────────────────────────────

class TestDemographics:
    def test_demographic_profile(self):
        result = get_demographic_profile("长沙")
        assert "长沙" in result
        assert "人口" in result

    def test_demographic_impact(self):
        result = analyze_demographic_impact("北京")
        assert "北京" in result

    def test_housing_demand_forecast(self):
        result = forecast_housing_demand("成都", years=5)
        assert "成都" in result


# ── 投资指标 ───────────────────────────────────────────────

class TestInvestmentMetrics:
    def test_investment_return(self):
        result = calculate_investment_return("长沙", area_sqm=100)
        assert "长沙" in result
        assert "❌" not in result

    def test_affordability(self):
        result = assess_affordability("上海")
        assert "上海" in result

    def test_investment_timing(self):
        result = evaluate_investment_timing("长沙")
        assert "长沙" in result
        assert "评分" in result or "时机" in result

    def test_compare_investment(self):
        result = compare_investment_cities("长沙,武汉,南京")
        assert "长沙" in result


# ── 政策与风险 ─────────────────────────────────────────────

class TestPolicyRisk:
    def test_housing_policy(self):
        result = get_housing_policy("长沙")
        assert "长沙" in result
        assert "❌" not in result

    def test_housing_policy_tier1(self):
        result = get_housing_policy("北京")
        assert "北京" in result

    def test_market_risk(self):
        result = assess_market_risk("长沙")
        assert "长沙" in result
        assert "风险" in result

    def test_market_risk_high(self):
        result = assess_market_risk("哈尔滨")
        assert "哈尔滨" in result


# ── 全城市覆盖测试 ─────────────────────────────────────────

class TestAllCities:
    def test_all_cities_have_overview(self):
        """确保每个城市的 market_overview 都不报错"""
        failures = []
        for city in list_all_cities():
            result = get_city_market_overview(city)
            if "❌" in result:
                failures.append(city)
        assert failures == [], f"以下城市返回错误: {failures}"

    def test_all_cities_have_risk(self):
        """确保每个城市的 risk_assessment 都不报错"""
        failures = []
        for city in list_all_cities():
            result = assess_market_risk(city)
            if "❌" in result:
                failures.append(city)
        assert failures == [], f"以下城市返回错误: {failures}"
