"""
CEB Domestic Tariff Calculator (2024 rates).
Tiers are progressive - each band is charged at its own rate.
When real tariff changes, update TIERS only.
"""

TIERS = [
    {"limit": 30,   "rate": 7.85,  "fixed": 30},
    {"limit": 60,   "rate": 10.00, "fixed": 60},
    {"limit": 90,   "rate": 27.75, "fixed": 90},
    {"limit": 120,  "rate": 32.00, "fixed": 120},
    {"limit": 180,  "rate": 45.00, "fixed": 180},
    {"limit": 300,  "rate": 75.00, "fixed": 270},
    {"limit": float("inf"), "rate": 75.00, "fixed": 480},
]


def calculate_bill(units: float) -> float:
    """Return total CEB bill in LKR for given monthly units consumed."""
    units = max(0.0, units)

    fixed_charge = TIERS[-1]["fixed"]
    for tier in TIERS:
        if units <= tier["limit"]:
            fixed_charge = tier["fixed"]
            break

    energy_charge = 0.0
    remaining = units
    prev_limit = 0

    for tier in TIERS:
        band = tier["limit"] - prev_limit
        consumed = min(remaining, band)
        energy_charge += consumed * tier["rate"]
        remaining -= consumed
        prev_limit = tier["limit"]
        if remaining <= 0:
            break

    return round(energy_charge + fixed_charge, 2)


def get_risk_level(units: float) -> str:
    if units <= 60:
        return "Low"
    elif units <= 180:
        return "Medium"
    return "High"


def get_tier_label(units: float) -> str:
    if units <= 30:
        return "Tier 1 (0–30 units)"
    elif units <= 60:
        return "Tier 2 (31–60 units)"
    elif units <= 90:
        return "Tier 3 (61–90 units)"
    elif units <= 120:
        return "Tier 4 (91–120 units)"
    elif units <= 180:
        return "Tier 5 (121–180 units)"
    elif units <= 300:
        return "Tier 6 (181–300 units)"
    return "Tier 7 (300+ units)"
