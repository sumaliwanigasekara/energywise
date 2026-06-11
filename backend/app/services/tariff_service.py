"""
CEB Domestic Tariff Calculator.
Approved Tariff effective from 11th May 2026.
Source: Public Utilities Commission of Sri Lanka (PUCSL)
https://www.pucsl.gov.lk/electricity-tariff-revision-2026-may/

Three separate schedules apply based on total monthly consumption.
When tariff changes, update the three schedule blocks below only.
"""


# --- Schedule 1: Total consumption 0-60 kWh/month ---
TIERS_LOW = [
    {"limit": 30,           "rate": 5.00,  "fixed": 80.00},
    {"limit": 60,           "rate": 9.00,  "fixed": 210.00},
]

# --- Schedule 2: Total consumption 61-180 kWh/month ---
TIERS_MID = [
    {"limit": 60,           "rate": 14.00, "fixed": 0.00},
    {"limit": 90,           "rate": 20.00, "fixed": 400.00},
    {"limit": 120,          "rate": 28.00, "fixed": 1000.00},
    {"limit": 180,          "rate": 44.00, "fixed": 1500.00},
]

# --- Schedule 3: Total consumption above 180 kWh/month ---
TIERS_HIGH = [
    {"limit": 180,          "rate": 32.50, "fixed": 0.00},
    {"limit": float("inf"), "rate": 100.00, "fixed": 2500.00},
]


def _apply_tiers(units: float, tiers: list) -> float:
    """Calculate energy charge by applying progressive tier rates."""
    energy_charge = 0.0
    remaining = units
    prev_limit = 0
    for tier in tiers:
        band = tier["limit"] - prev_limit
        consumed = min(remaining, band)
        energy_charge += consumed * tier["rate"]
        remaining -= consumed
        prev_limit = tier["limit"]
        if remaining <= 0:
            break
    return energy_charge


def calculate_bill(units: float) -> float:
    """
    Return total CEB bill in LKR for given monthly units consumed.
    Schedule is selected based on total consumption band.
    """
    units = max(0.0, units)

    if units <= 60:
        tiers = TIERS_LOW
    elif units <= 180:
        tiers = TIERS_MID
    else:
        tiers = TIERS_HIGH

    # Fixed charge is determined by which tier the total consumption falls in
    fixed_charge = tiers[-1]["fixed"]
    for tier in tiers:
        if units <= tier["limit"]:
            fixed_charge = tier["fixed"]
            break

    energy_charge = _apply_tiers(units, tiers)
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
    elif units <= 360:
        return "Tier 6 (181–360 units)"
    return "Tier 7 (360+ units)"