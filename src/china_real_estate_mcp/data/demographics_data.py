"""
中国城市人口与人口结构数据模块

包含 30+ 主要城市的人口规模、增长率、年龄结构、城镇化率、
住房相关人口指标等数据。数据基于 2024-2025 年公开统计数据整理。

数据来源参考：国家统计局第七次人口普查、各城市统计年鉴、
各省统计公报、住建部数据等。
"""

from __future__ import annotations

DEMOGRAPHICS_DATA: dict[str, dict] = {
    # ========== 一线城市 ==========
    "北京": {
        "population_10k": 2188,
        "population_growth_rate": 0.001,
        "birth_rate_permil": 5.6,
        "death_rate_permil": 5.9,
        "natural_growth_rate_permil": -0.3,
        "urbanization_rate": 0.875,
        "age_0_14_pct": 0.118,
        "age_15_59_pct": 0.685,
        "age_60_plus_pct": 0.197,
        "age_65_plus_pct": 0.145,
        "net_migration_10k": -5,
        "avg_household_size": 2.31,
        "housing_ownership_rate": 0.70,
        "per_capita_living_area": 33.4,
    },
    "上海": {
        "population_10k": 2487,
        "population_growth_rate": 0.002,
        "birth_rate_permil": 5.0,
        "death_rate_permil": 6.2,
        "natural_growth_rate_permil": -1.2,
        "urbanization_rate": 0.893,
        "age_0_14_pct": 0.098,
        "age_15_59_pct": 0.672,
        "age_60_plus_pct": 0.230,
        "age_65_plus_pct": 0.168,
        "net_migration_10k": 10,
        "avg_household_size": 2.32,
        "housing_ownership_rate": 0.68,
        "per_capita_living_area": 31.0,
    },
    "广州": {
        "population_10k": 1882,
        "population_growth_rate": 0.005,
        "birth_rate_permil": 9.0,
        "death_rate_permil": 4.5,
        "natural_growth_rate_permil": 4.5,
        "urbanization_rate": 0.867,
        "age_0_14_pct": 0.140,
        "age_15_59_pct": 0.710,
        "age_60_plus_pct": 0.150,
        "age_65_plus_pct": 0.110,
        "net_migration_10k": 8,
        "avg_household_size": 2.55,
        "housing_ownership_rate": 0.65,
        "per_capita_living_area": 30.5,
    },
    "深圳": {
        "population_10k": 1779,
        "population_growth_rate": 0.005,
        "birth_rate_permil": 10.5,
        "death_rate_permil": 1.6,
        "natural_growth_rate_permil": 8.9,
        "urbanization_rate": 1.000,
        "age_0_14_pct": 0.155,
        "age_15_59_pct": 0.750,
        "age_60_plus_pct": 0.095,
        "age_65_plus_pct": 0.058,
        "net_migration_10k": 5,
        "avg_household_size": 2.25,
        "housing_ownership_rate": 0.45,
        "per_capita_living_area": 27.8,
    },
    # ========== 新一线城市 ==========
    "成都": {
        "population_10k": 2140,
        "population_growth_rate": 0.008,
        "birth_rate_permil": 7.2,
        "death_rate_permil": 6.8,
        "natural_growth_rate_permil": 0.4,
        "urbanization_rate": 0.799,
        "age_0_14_pct": 0.132,
        "age_15_59_pct": 0.670,
        "age_60_plus_pct": 0.198,
        "age_65_plus_pct": 0.145,
        "net_migration_10k": 20,
        "avg_household_size": 2.49,
        "housing_ownership_rate": 0.75,
        "per_capita_living_area": 38.5,
    },
    "杭州": {
        "population_10k": 1252,
        "population_growth_rate": 0.010,
        "birth_rate_permil": 7.0,
        "death_rate_permil": 5.0,
        "natural_growth_rate_permil": 2.0,
        "urbanization_rate": 0.836,
        "age_0_14_pct": 0.128,
        "age_15_59_pct": 0.700,
        "age_60_plus_pct": 0.172,
        "age_65_plus_pct": 0.128,
        "net_migration_10k": 18,
        "avg_household_size": 2.36,
        "housing_ownership_rate": 0.72,
        "per_capita_living_area": 36.2,
    },
    "武汉": {
        "population_10k": 1374,
        "population_growth_rate": 0.006,
        "birth_rate_permil": 7.8,
        "death_rate_permil": 5.8,
        "natural_growth_rate_permil": 2.0,
        "urbanization_rate": 0.845,
        "age_0_14_pct": 0.125,
        "age_15_59_pct": 0.695,
        "age_60_plus_pct": 0.180,
        "age_65_plus_pct": 0.132,
        "net_migration_10k": 12,
        "avg_household_size": 2.47,
        "housing_ownership_rate": 0.74,
        "per_capita_living_area": 37.0,
    },
    "南京": {
        "population_10k": 949,
        "population_growth_rate": 0.004,
        "birth_rate_permil": 6.5,
        "death_rate_permil": 5.5,
        "natural_growth_rate_permil": 1.0,
        "urbanization_rate": 0.870,
        "age_0_14_pct": 0.120,
        "age_15_59_pct": 0.685,
        "age_60_plus_pct": 0.195,
        "age_65_plus_pct": 0.142,
        "net_migration_10k": 6,
        "avg_household_size": 2.40,
        "housing_ownership_rate": 0.73,
        "per_capita_living_area": 35.8,
    },
    "重庆": {
        "population_10k": 3213,
        "population_growth_rate": -0.002,
        "birth_rate_permil": 6.5,
        "death_rate_permil": 8.0,
        "natural_growth_rate_permil": -1.5,
        "urbanization_rate": 0.707,
        "age_0_14_pct": 0.145,
        "age_15_59_pct": 0.620,
        "age_60_plus_pct": 0.235,
        "age_65_plus_pct": 0.178,
        "net_migration_10k": -15,
        "avg_household_size": 2.56,
        "housing_ownership_rate": 0.82,
        "per_capita_living_area": 40.2,
    },
    "苏州": {
        "population_10k": 1292,
        "population_growth_rate": 0.005,
        "birth_rate_permil": 6.2,
        "death_rate_permil": 5.0,
        "natural_growth_rate_permil": 1.2,
        "urbanization_rate": 0.818,
        "age_0_14_pct": 0.125,
        "age_15_59_pct": 0.695,
        "age_60_plus_pct": 0.180,
        "age_65_plus_pct": 0.135,
        "net_migration_10k": 8,
        "avg_household_size": 2.50,
        "housing_ownership_rate": 0.73,
        "per_capita_living_area": 37.5,
    },
    "长沙": {
        "population_10k": 1058,
        "population_growth_rate": 0.012,
        "birth_rate_permil": 8.5,
        "death_rate_permil": 5.5,
        "natural_growth_rate_permil": 3.0,
        "urbanization_rate": 0.824,
        "age_0_14_pct": 0.155,
        "age_15_59_pct": 0.675,
        "age_60_plus_pct": 0.170,
        "age_65_plus_pct": 0.125,
        "net_migration_10k": 15,
        "avg_household_size": 2.65,
        "housing_ownership_rate": 0.78,
        "per_capita_living_area": 39.0,
    },
    "天津": {
        "population_10k": 1373,
        "population_growth_rate": -0.001,
        "birth_rate_permil": 5.2,
        "death_rate_permil": 6.5,
        "natural_growth_rate_permil": -1.3,
        "urbanization_rate": 0.849,
        "age_0_14_pct": 0.110,
        "age_15_59_pct": 0.665,
        "age_60_plus_pct": 0.225,
        "age_65_plus_pct": 0.165,
        "net_migration_10k": -8,
        "avg_household_size": 2.38,
        "housing_ownership_rate": 0.76,
        "per_capita_living_area": 35.0,
    },
    "郑州": {
        "population_10k": 1282,
        "population_growth_rate": 0.006,
        "birth_rate_permil": 8.0,
        "death_rate_permil": 5.5,
        "natural_growth_rate_permil": 2.5,
        "urbanization_rate": 0.788,
        "age_0_14_pct": 0.165,
        "age_15_59_pct": 0.668,
        "age_60_plus_pct": 0.167,
        "age_65_plus_pct": 0.118,
        "net_migration_10k": 10,
        "avg_household_size": 2.68,
        "housing_ownership_rate": 0.76,
        "per_capita_living_area": 36.0,
    },
    "西安": {
        "population_10k": 1316,
        "population_growth_rate": 0.008,
        "birth_rate_permil": 7.5,
        "death_rate_permil": 5.8,
        "natural_growth_rate_permil": 1.7,
        "urbanization_rate": 0.795,
        "age_0_14_pct": 0.148,
        "age_15_59_pct": 0.690,
        "age_60_plus_pct": 0.162,
        "age_65_plus_pct": 0.118,
        "net_migration_10k": 15,
        "avg_household_size": 2.55,
        "housing_ownership_rate": 0.75,
        "per_capita_living_area": 36.5,
    },
    # ========== 二线城市 ==========
    "昆明": {
        "population_10k": 860,
        "population_growth_rate": 0.003,
        "birth_rate_permil": 8.5,
        "death_rate_permil": 5.2,
        "natural_growth_rate_permil": 3.3,
        "urbanization_rate": 0.741,
        "age_0_14_pct": 0.148,
        "age_15_59_pct": 0.685,
        "age_60_plus_pct": 0.167,
        "age_65_plus_pct": 0.118,
        "net_migration_10k": 5,
        "avg_household_size": 2.62,
        "housing_ownership_rate": 0.78,
        "per_capita_living_area": 38.0,
    },
    "合肥": {
        "population_10k": 963,
        "population_growth_rate": 0.010,
        "birth_rate_permil": 8.0,
        "death_rate_permil": 5.0,
        "natural_growth_rate_permil": 3.0,
        "urbanization_rate": 0.826,
        "age_0_14_pct": 0.158,
        "age_15_59_pct": 0.690,
        "age_60_plus_pct": 0.152,
        "age_65_plus_pct": 0.108,
        "net_migration_10k": 12,
        "avg_household_size": 2.58,
        "housing_ownership_rate": 0.76,
        "per_capita_living_area": 37.2,
    },
    "厦门": {
        "population_10k": 531,
        "population_growth_rate": 0.005,
        "birth_rate_permil": 8.0,
        "death_rate_permil": 3.5,
        "natural_growth_rate_permil": 4.5,
        "urbanization_rate": 0.901,
        "age_0_14_pct": 0.155,
        "age_15_59_pct": 0.715,
        "age_60_plus_pct": 0.130,
        "age_65_plus_pct": 0.090,
        "net_migration_10k": 5,
        "avg_household_size": 2.60,
        "housing_ownership_rate": 0.62,
        "per_capita_living_area": 29.5,
    },
    "济南": {
        "population_10k": 941,
        "population_growth_rate": 0.003,
        "birth_rate_permil": 7.0,
        "death_rate_permil": 6.5,
        "natural_growth_rate_permil": 0.5,
        "urbanization_rate": 0.747,
        "age_0_14_pct": 0.155,
        "age_15_59_pct": 0.650,
        "age_60_plus_pct": 0.195,
        "age_65_plus_pct": 0.145,
        "net_migration_10k": 3,
        "avg_household_size": 2.65,
        "housing_ownership_rate": 0.78,
        "per_capita_living_area": 37.8,
    },
    "青岛": {
        "population_10k": 1035,
        "population_growth_rate": 0.004,
        "birth_rate_permil": 6.8,
        "death_rate_permil": 6.5,
        "natural_growth_rate_permil": 0.3,
        "urbanization_rate": 0.773,
        "age_0_14_pct": 0.150,
        "age_15_59_pct": 0.660,
        "age_60_plus_pct": 0.190,
        "age_65_plus_pct": 0.142,
        "net_migration_10k": 5,
        "avg_household_size": 2.58,
        "housing_ownership_rate": 0.77,
        "per_capita_living_area": 36.5,
    },
    "福州": {
        "population_10k": 845,
        "population_growth_rate": 0.004,
        "birth_rate_permil": 8.5,
        "death_rate_permil": 5.0,
        "natural_growth_rate_permil": 3.5,
        "urbanization_rate": 0.728,
        "age_0_14_pct": 0.160,
        "age_15_59_pct": 0.680,
        "age_60_plus_pct": 0.160,
        "age_65_plus_pct": 0.115,
        "net_migration_10k": 4,
        "avg_household_size": 2.68,
        "housing_ownership_rate": 0.80,
        "per_capita_living_area": 38.5,
    },
    "大连": {
        "population_10k": 748,
        "population_growth_rate": -0.002,
        "birth_rate_permil": 5.0,
        "death_rate_permil": 7.5,
        "natural_growth_rate_permil": -2.5,
        "urbanization_rate": 0.825,
        "age_0_14_pct": 0.100,
        "age_15_59_pct": 0.648,
        "age_60_plus_pct": 0.252,
        "age_65_plus_pct": 0.188,
        "net_migration_10k": -3,
        "avg_household_size": 2.35,
        "housing_ownership_rate": 0.82,
        "per_capita_living_area": 36.0,
    },
    "南宁": {
        "population_10k": 887,
        "population_growth_rate": 0.004,
        "birth_rate_permil": 9.5,
        "death_rate_permil": 5.8,
        "natural_growth_rate_permil": 3.7,
        "urbanization_rate": 0.686,
        "age_0_14_pct": 0.200,
        "age_15_59_pct": 0.640,
        "age_60_plus_pct": 0.160,
        "age_65_plus_pct": 0.115,
        "net_migration_10k": 5,
        "avg_household_size": 2.85,
        "housing_ownership_rate": 0.80,
        "per_capita_living_area": 37.0,
    },
    "贵阳": {
        "population_10k": 622,
        "population_growth_rate": 0.005,
        "birth_rate_permil": 10.0,
        "death_rate_permil": 5.5,
        "natural_growth_rate_permil": 4.5,
        "urbanization_rate": 0.768,
        "age_0_14_pct": 0.190,
        "age_15_59_pct": 0.655,
        "age_60_plus_pct": 0.155,
        "age_65_plus_pct": 0.108,
        "net_migration_10k": 5,
        "avg_household_size": 2.78,
        "housing_ownership_rate": 0.82,
        "per_capita_living_area": 38.0,
    },
    "沈阳": {
        "population_10k": 914,
        "population_growth_rate": -0.003,
        "birth_rate_permil": 4.8,
        "death_rate_permil": 7.8,
        "natural_growth_rate_permil": -3.0,
        "urbanization_rate": 0.826,
        "age_0_14_pct": 0.098,
        "age_15_59_pct": 0.645,
        "age_60_plus_pct": 0.257,
        "age_65_plus_pct": 0.195,
        "net_migration_10k": -5,
        "avg_household_size": 2.28,
        "housing_ownership_rate": 0.85,
        "per_capita_living_area": 37.5,
    },
    "石家庄": {
        "population_10k": 1123,
        "population_growth_rate": 0.001,
        "birth_rate_permil": 7.5,
        "death_rate_permil": 6.8,
        "natural_growth_rate_permil": 0.7,
        "urbanization_rate": 0.682,
        "age_0_14_pct": 0.168,
        "age_15_59_pct": 0.642,
        "age_60_plus_pct": 0.190,
        "age_65_plus_pct": 0.138,
        "net_migration_10k": 2,
        "avg_household_size": 2.72,
        "housing_ownership_rate": 0.82,
        "per_capita_living_area": 38.5,
    },
    "太原": {
        "population_10k": 540,
        "population_growth_rate": 0.002,
        "birth_rate_permil": 6.8,
        "death_rate_permil": 6.0,
        "natural_growth_rate_permil": 0.8,
        "urbanization_rate": 0.870,
        "age_0_14_pct": 0.135,
        "age_15_59_pct": 0.665,
        "age_60_plus_pct": 0.200,
        "age_65_plus_pct": 0.148,
        "net_migration_10k": 2,
        "avg_household_size": 2.55,
        "housing_ownership_rate": 0.80,
        "per_capita_living_area": 35.0,
    },
    "哈尔滨": {
        "population_10k": 1001,
        "population_growth_rate": -0.008,
        "birth_rate_permil": 3.8,
        "death_rate_permil": 8.0,
        "natural_growth_rate_permil": -4.2,
        "urbanization_rate": 0.706,
        "age_0_14_pct": 0.095,
        "age_15_59_pct": 0.625,
        "age_60_plus_pct": 0.280,
        "age_65_plus_pct": 0.210,
        "net_migration_10k": -20,
        "avg_household_size": 2.18,
        "housing_ownership_rate": 0.88,
        "per_capita_living_area": 32.0,
    },
    "长春": {
        "population_10k": 907,
        "population_growth_rate": -0.006,
        "birth_rate_permil": 4.2,
        "death_rate_permil": 7.5,
        "natural_growth_rate_permil": -3.3,
        "urbanization_rate": 0.680,
        "age_0_14_pct": 0.100,
        "age_15_59_pct": 0.635,
        "age_60_plus_pct": 0.265,
        "age_65_plus_pct": 0.198,
        "net_migration_10k": -15,
        "avg_household_size": 2.25,
        "housing_ownership_rate": 0.86,
        "per_capita_living_area": 33.5,
    },
    "兰州": {
        "population_10k": 442,
        "population_growth_rate": 0.001,
        "birth_rate_permil": 7.5,
        "death_rate_permil": 6.0,
        "natural_growth_rate_permil": 1.5,
        "urbanization_rate": 0.815,
        "age_0_14_pct": 0.148,
        "age_15_59_pct": 0.668,
        "age_60_plus_pct": 0.184,
        "age_65_plus_pct": 0.132,
        "net_migration_10k": 1,
        "avg_household_size": 2.62,
        "housing_ownership_rate": 0.82,
        "per_capita_living_area": 34.0,
    },
    "南昌": {
        "population_10k": 643,
        "population_growth_rate": 0.003,
        "birth_rate_permil": 8.0,
        "death_rate_permil": 5.8,
        "natural_growth_rate_permil": 2.2,
        "urbanization_rate": 0.778,
        "age_0_14_pct": 0.168,
        "age_15_59_pct": 0.660,
        "age_60_plus_pct": 0.172,
        "age_65_plus_pct": 0.122,
        "net_migration_10k": 3,
        "avg_household_size": 2.70,
        "housing_ownership_rate": 0.80,
        "per_capita_living_area": 37.5,
    },
    "海口": {
        "population_10k": 293,
        "population_growth_rate": 0.008,
        "birth_rate_permil": 9.0,
        "death_rate_permil": 4.5,
        "natural_growth_rate_permil": 4.5,
        "urbanization_rate": 0.830,
        "age_0_14_pct": 0.175,
        "age_15_59_pct": 0.680,
        "age_60_plus_pct": 0.145,
        "age_65_plus_pct": 0.100,
        "net_migration_10k": 5,
        "avg_household_size": 2.68,
        "housing_ownership_rate": 0.72,
        "per_capita_living_area": 35.5,
    },
    # ========== 三线及以下城市 ==========
    "洛阳": {
        "population_10k": 707,
        "population_growth_rate": -0.002,
        "birth_rate_permil": 7.5,
        "death_rate_permil": 7.0,
        "natural_growth_rate_permil": 0.5,
        "urbanization_rate": 0.598,
        "age_0_14_pct": 0.185,
        "age_15_59_pct": 0.620,
        "age_60_plus_pct": 0.195,
        "age_65_plus_pct": 0.142,
        "net_migration_10k": -8,
        "avg_household_size": 2.82,
        "housing_ownership_rate": 0.86,
        "per_capita_living_area": 40.5,
    },
    "烟台": {
        "population_10k": 710,
        "population_growth_rate": -0.003,
        "birth_rate_permil": 5.5,
        "death_rate_permil": 8.0,
        "natural_growth_rate_permil": -2.5,
        "urbanization_rate": 0.685,
        "age_0_14_pct": 0.138,
        "age_15_59_pct": 0.628,
        "age_60_plus_pct": 0.234,
        "age_65_plus_pct": 0.175,
        "net_migration_10k": -5,
        "avg_household_size": 2.48,
        "housing_ownership_rate": 0.85,
        "per_capita_living_area": 38.0,
    },
    "温州": {
        "population_10k": 967,
        "population_growth_rate": 0.002,
        "birth_rate_permil": 7.0,
        "death_rate_permil": 5.5,
        "natural_growth_rate_permil": 1.5,
        "urbanization_rate": 0.718,
        "age_0_14_pct": 0.148,
        "age_15_59_pct": 0.665,
        "age_60_plus_pct": 0.187,
        "age_65_plus_pct": 0.138,
        "net_migration_10k": 2,
        "avg_household_size": 2.72,
        "housing_ownership_rate": 0.85,
        "per_capita_living_area": 39.0,
    },
    "徐州": {
        "population_10k": 903,
        "population_growth_rate": -0.003,
        "birth_rate_permil": 7.0,
        "death_rate_permil": 7.5,
        "natural_growth_rate_permil": -0.5,
        "urbanization_rate": 0.651,
        "age_0_14_pct": 0.178,
        "age_15_59_pct": 0.628,
        "age_60_plus_pct": 0.194,
        "age_65_plus_pct": 0.145,
        "net_migration_10k": -10,
        "avg_household_size": 2.78,
        "housing_ownership_rate": 0.86,
        "per_capita_living_area": 40.0,
    },
    "襄阳": {
        "population_10k": 526,
        "population_growth_rate": -0.003,
        "birth_rate_permil": 7.0,
        "death_rate_permil": 7.2,
        "natural_growth_rate_permil": -0.2,
        "urbanization_rate": 0.622,
        "age_0_14_pct": 0.172,
        "age_15_59_pct": 0.630,
        "age_60_plus_pct": 0.198,
        "age_65_plus_pct": 0.148,
        "net_migration_10k": -8,
        "avg_household_size": 2.80,
        "housing_ownership_rate": 0.88,
        "per_capita_living_area": 42.0,
    },
    "芜湖": {
        "population_10k": 368,
        "population_growth_rate": 0.002,
        "birth_rate_permil": 7.5,
        "death_rate_permil": 6.5,
        "natural_growth_rate_permil": 1.0,
        "urbanization_rate": 0.698,
        "age_0_14_pct": 0.155,
        "age_15_59_pct": 0.658,
        "age_60_plus_pct": 0.187,
        "age_65_plus_pct": 0.135,
        "net_migration_10k": 2,
        "avg_household_size": 2.65,
        "housing_ownership_rate": 0.83,
        "per_capita_living_area": 39.5,
    },
}


def get_demographics(city: str) -> dict | None:
    """获取指定城市的人口统计数据。

    Args:
        city: 城市中文名称。

    Returns:
        包含城市名和人口数据的字典，未找到时返回 ``None``。
    """
    if city in DEMOGRAPHICS_DATA:
        return {"city": city, **DEMOGRAPHICS_DATA[city]}
    return None


def get_aging_index(city: str) -> float | None:
    """计算城市老龄化指数（老少比）。

    老龄化指数 = 60岁以上人口占比 / 0-14岁人口占比。
    该值越高说明老龄化程度越严重。

    Args:
        city: 城市中文名称。

    Returns:
        老龄化指数（浮点数），城市不存在时返回 ``None``。
    """
    data = DEMOGRAPHICS_DATA.get(city)
    if data is None:
        return None
    age_0_14 = data["age_0_14_pct"]
    age_60_plus = data["age_60_plus_pct"]
    if age_0_14 == 0:
        return float("inf")
    return round(age_60_plus / age_0_14, 3)


def get_dependency_ratio(city: str) -> float | None:
    """计算城市总抚养比。

    总抚养比 = (0-14岁 + 60岁以上) / 15-59岁劳动年龄人口。
    该值越高说明劳动人口负担越重。

    Args:
        city: 城市中文名称。

    Returns:
        总抚养比（浮点数），城市不存在时返回 ``None``。
    """
    data = DEMOGRAPHICS_DATA.get(city)
    if data is None:
        return None
    age_0_14 = data["age_0_14_pct"]
    age_15_59 = data["age_15_59_pct"]
    age_60_plus = data["age_60_plus_pct"]
    if age_15_59 == 0:
        return float("inf")
    return round((age_0_14 + age_60_plus) / age_15_59, 3)


def get_housing_demand_indicator(city: str) -> dict | None:
    """计算城市住房需求相关指标。

    基于人口结构数据估算住房刚需和改善需求潜力。

    Args:
        city: 城市中文名称。

    Returns:
        住房需求指标字典，城市不存在时返回 ``None``。
    """
    data = DEMOGRAPHICS_DATA.get(city)
    if data is None:
        return None

    pop_10k = data["population_10k"]
    household_size = data["avg_household_size"]
    ownership_rate = data["housing_ownership_rate"]
    per_capita_area = data["per_capita_living_area"]
    urbanization = data["urbanization_rate"]
    growth_rate = data["population_growth_rate"]

    # 估算城市总户数（万户）
    total_households = round(pop_10k / household_size, 1)

    # 无房家庭比例估算
    rentier_ratio = round(1 - ownership_rate, 3)

    # 新增城镇化住房需求（万人/年 → 万套/年）
    new_urban_pop = round(pop_10k * (1 - urbanization) * 0.01, 1)  # 假设年城镇化率提升 1%
    new_urban_demand = round(new_urban_pop / household_size, 1)

    # 人口净流入带来的住房需求（万套/年）
    net_migration = data["net_migration_10k"]
    migration_demand = round(max(net_migration, 0) / household_size, 1)

    return {
        "city": city,
        "total_households_10k": total_households,
        "rentier_ratio": rentier_ratio,
        "per_capita_area_sqm": per_capita_area,
        "new_urbanization_demand_10k_units": new_urban_demand,
        "migration_demand_10k_units": migration_demand,
        "population_growth_rate": growth_rate,
        "aging_index": get_aging_index(city),
        "dependency_ratio": get_dependency_ratio(city),
    }
