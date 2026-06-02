import os
import joblib
import numpy as np
from datetime import datetime
from app.services.tariff_service import calculate_bill, get_risk_level

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../ml/model.pkl")

_model = None


def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Run `python ml/train_model.py` to generate it."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict(data: dict) -> dict:
    """Predict monthly electricity consumption. All hour inputs are monthly totals."""
    model = _load_model()

    avg_prev_bill = (
        (data.get("prev_bill_1", 0) or 0)
        + (data.get("prev_bill_2", 0) or 0)
        + (data.get("prev_bill_3", 0) or 0)
    ) / 3.0

    weather = data.get("weather", {})
    month = datetime.now().month

    features = np.array([[
        data.get("members", 4),                    # 1
        avg_prev_bill,                              # 2
        data.get("fan_count", 0),                  # 3
        data.get("ac_count", 0),                   # 4
        data.get("ac_hours_per_month", 0),         # 5
        data.get("ac_tons", 1.5),                  # 6
        data.get("fridge_count", 1),               # 7
        data.get("washer_hours_per_month", 0),     # 8
        data.get("heater_hours_per_month", 0),     # 9
        data.get("other_hours_per_month", 0),      # 10
        weather.get("avg_temp", 29.0),             # 11
        weather.get("avg_humidity", 78.0),         # 12
        weather.get("total_precip", 15.0),         # 13
        weather.get("avg_wind", 12.0),             # 14
        month,                                     # 15
    ]])

    predicted_units = float(model.predict(features)[0])
    predicted_units = max(0.0, predicted_units)
    predicted_bill = calculate_bill(predicted_units)
    risk_level = get_risk_level(predicted_units)

    recommendations = _generate_recommendations(data, predicted_units, predicted_bill)

    return {
        "predicted_units": round(predicted_units, 2),
        "predicted_bill": round(predicted_bill, 2),
        "risk_level": risk_level,
        "recommendations": recommendations,
        "appliance_breakdown": _appliance_breakdown(data),
    }


def _appliance_breakdown(data: dict) -> dict:
    ac = data.get("ac_count", 0) * (data.get("ac_hours_per_month", 0) / 30) * data.get("ac_tons", 1.5) * 0.7 * 30
    fans = data.get("fan_count", 0) * 0.06 * 10 * 30
    fridge = data.get("fridge_count", 1) * 0.15 * 24 * 30
    heater = data.get("heater_hours_per_month", 0) * 1.5
    washer = data.get("washer_hours_per_month", 0) * 2.0
    other = (data.get("other_hours_per_month", 14) / 30) * 0.3 * 30
    base = data.get("members", 4) * 0.2 * 30

    return {
        "Air Conditioner": round(ac, 1),
        "Refrigerator": round(fridge, 1),
        "Fans": round(fans, 1),
        "Water Heater": round(heater, 1),
        "Washing Machine": round(washer, 1),
        "Other Appliances": round(other, 1),
        "Base Load": round(base, 1),
    }


def _generate_recommendations(data: dict, units: float, bill: float) -> list:
    recs = []

    ac_count = data.get("ac_count", 0)
    ac_hours_per_month = data.get("ac_hours_per_month", 0)
    ac_hours_daily = ac_hours_per_month / 30
    ac_tons = data.get("ac_tons", 1.5)
    fan_count = data.get("fan_count", 0)
    fridge_count = data.get("fridge_count", 0)
    washer_hours = data.get("washer_hours_per_month", 0)
    heater_hours = data.get("heater_hours_per_month", 0)
    members = data.get("members", 4)

    # --- AC recommendations ---
    if ac_count > 0 and ac_hours_daily > 6:
        saving = round(ac_count * (ac_hours_daily - 6) * ac_tons * 0.7 * 30, 1)
        recs.append({
            "title": "Reduce AC usage hours",
            "description": (
                f"Your AC runs {ac_hours_daily:.0f} hrs/day. Reducing to 6 hrs could save "
                f"~{saving} kWh/month. In Colombo's climate, switching the AC off at "
                f"night and using a ceiling fan instead can reduce your bill significantly."
            ),
            "category": "Air Conditioner",
            "saving_kwh": saving,
            "icon": "ac",
        })

    if ac_count > 0:
        recs.append({
            "title": "Set AC thermostat to 24°C",
            "description": (
                "Each degree below 24°C increases energy use by about 6%. "
                "Setting your AC to 24°C instead of 18°C can cut AC electricity "
                "costs by up to 36% — no hardware change needed, just a setting adjustment."
            ),
            "category": "Air Conditioner",
            "saving_kwh": round(ac_count * ac_hours_daily * 0.18 * 30, 1),
            "icon": "temperature",
        })

    if ac_count > 0 and fan_count > 0:
        recs.append({
            "title": "Use fan with AC at higher temperature",
            "description": (
                "Running a ceiling fan alongside the AC lets you set the thermostat "
                "2–3°C higher while feeling equally cool. A fan uses only 60W compared "
                "to 1,000W+ for an AC — this is one of the most cost-effective habits "
                "for Sri Lankan households."
            ),
            "category": "Air Conditioner",
            "saving_kwh": round(ac_count * ac_hours_daily * 0.12 * 30, 1),
            "icon": "fan",
        })

    if ac_count > 0:
        recs.append({
            "title": "Clean AC filters monthly",
            "description": (
                "Dirty AC filters force the unit to work harder, increasing electricity "
                "use by 5–15%. Cleaning the filter takes 10 minutes and costs nothing — "
                "this is one of the simplest ways to reduce your bill in Sri Lanka's "
                "dusty urban environment."
            ),
            "category": "Air Conditioner",
            "saving_kwh": round(ac_count * ac_hours_daily * ac_tons * 0.7 * 0.1 * 30, 1),
            "icon": "ac",
        })

    # --- Fridge recommendations ---
    if fridge_count >= 1:
        recs.append({
            "title": "Keep fridge away from heat sources",
            "description": (
                "Placing the refrigerator away from direct sunlight, the stove, or "
                "walls improves efficiency by up to 15%. Also ensure the door seal is "
                "tight — a loose seal wastes electricity continuously. This is free "
                "to fix and relevant in Colombo's warm climate."
            ),
            "category": "Refrigerator",
            "saving_kwh": round(fridge_count * 0.15 * 24 * 0.1 * 30, 1),
            "icon": "fridge",
        })

    if fridge_count >= 2:
        recs.append({
            "title": "Consider consolidating to one refrigerator",
            "description": (
                "Each additional fridge consumes approximately 108 kWh/month under "
                "the CEB tariff. At the higher tiers, this can add LKR 4,000–8,000 "
                "to your bill. If a second fridge is not essential, unplugging it "
                "during low-usage months is an easy saving."
            ),
            "category": "Refrigerator",
            "saving_kwh": 108.0,
            "icon": "fridge",
        })

    # --- Washing machine ---
    if washer_hours > 8:
        recs.append({
            "title": "Wash with full loads during off-peak hours",
            "description": (
                "Running the washing machine with full loads reduces the number of "
                "cycles needed. In Sri Lanka, washing with cold water also saves "
                "significantly as water heating accounts for a large portion of "
                "washer energy use. Aim for 2–3 full loads per week instead of "
                "daily smaller loads."
            ),
            "category": "Washing Machine",
            "saving_kwh": round(washer_hours * 1.0, 1),
            "icon": "washer",
        })

    # --- Water heater ---
    if heater_hours > 4:
        recs.append({
            "title": "Reduce water heater usage time",
            "description": (
                "Water heaters are one of the highest energy consumers in Sri Lankan "
                "homes. Switch the heater on only 15–20 minutes before use instead "
                "of leaving it on all day. This simple habit change can save "
                f"~{round(heater_hours * 1.0, 1)} kWh/month at no cost."
            ),
            "category": "Water Heater",
            "saving_kwh": round(heater_hours * 1.0, 1),
            "icon": "heater",
        })

    # --- CEB tier awareness ---
    if units > 60:
        recs.append({
            "title": "Stay below the next CEB tariff tier",
            "description": (
                "Sri Lanka's CEB uses a progressive tariff — the more you use, the "
                "higher the rate for ALL units, not just the extra ones. Reducing "
                "usage to stay under 90, 120, or 180 units can result in a "
                "significantly lower total bill. Even saving 5–10 units can drop "
                "you to a cheaper tier."
            ),
            "category": "General",
            "saving_kwh": round(units * 0.05, 1),
            "icon": "plug",
        })

    # --- Lighting ---
    recs.append({
        "title": "Switch all bulbs to LED",
        "description": (
            "LED bulbs use 75% less electricity than incandescent bulbs and last "
            "years longer. In Sri Lanka, replacing 5 bulbs saves approximately "
            f"{round(members * 0.25 * 30, 1)} kWh/month. LED bulbs are widely "
            "available at supermarkets for LKR 200–400 each and pay for themselves "
            "within 1–2 months."
        ),
        "category": "Lighting",
        "saving_kwh": round(members * 0.25 * 30, 1),
        "icon": "bulb",
    })

    # --- Standby power ---
    recs.append({
        "title": "Unplug devices not in use",
        "description": (
            "Televisions, phone chargers, microwave ovens, and set-top boxes consume "
            "electricity even on standby. In a typical Colombo household, standby "
            "power accounts for 8–10% of the total bill. Using a power strip with "
            "a switch to cut off multiple devices at once is an easy and free habit."
        ),
        "category": "General",
        "saving_kwh": round(units * 0.08, 1),
        "icon": "plug",
    })

    # --- Iron ---
    recs.append({
        "title": "Iron clothes in batches",
        "description": (
            "Electric irons use 1,000–2,500W — one of the highest wattage appliances "
            "in the home. Ironing a week's clothes in one session instead of daily "
            "reduces warm-up energy waste. This is a simple habit change with no cost."
        ),
        "category": "General",
        "saving_kwh": round(members * 0.1 * 30, 1),
        "icon": "plug",
    })

    return recs
