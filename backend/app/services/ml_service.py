import os
import joblib
import numpy as np
from app.services.tariff_service import calculate_bill, get_risk_level

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../ml/model.pkl")

_model = None


def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict(data: dict) -> dict:
    """
    Run prediction from form inputs.
    Returns predicted_units, predicted_bill, risk_level, recommendations.
    Replace model.pkl with the real trained model when ready.
    """
    model = _load_model()

    avg_prev_bill = (
        (data.get("prev_bill_1", 0) or 0)
        + (data.get("prev_bill_2", 0) or 0)
        + (data.get("prev_bill_3", 0) or 0)
    ) / 3.0

    features = np.array([[
        data.get("members", 4),
        avg_prev_bill,
        data.get("fan_count", 0),
        data.get("ac_count", 0),
        data.get("ac_hours_per_day", 0),
        data.get("ac_tons", 1.5),
        data.get("fridge_count", 1),
        data.get("washer_hours_per_week", 0),
        data.get("heater_hours_per_week", 0),
        data.get("other_hours_per_day", 0),
        data.get("temperature", 30.0),
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
    """Estimate monthly kWh per appliance category for the pie chart."""
    days = 30
    ac = data.get("ac_count", 0) * data.get("ac_hours_per_day", 0) * data.get("ac_tons", 1.5) * 0.7 * days
    fans = data.get("fan_count", 0) * 0.06 * 10 * days
    fridge = data.get("fridge_count", 1) * 0.15 * 24 * days
    heater = data.get("heater_hours_per_week", 0) / 7 * 1.5 * days
    washer = data.get("washer_hours_per_week", 0) / 7 * 2.0 * days
    other = data.get("other_hours_per_day", 2) * 0.3 * days
    base = data.get("members", 4) * 0.2 * days

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
    ac_hours = data.get("ac_hours_per_day", 0)
    ac_tons = data.get("ac_tons", 1.5)
    fan_count = data.get("fan_count", 0)
    fridge_count = data.get("fridge_count", 0)
    washer_hours = data.get("washer_hours_per_week", 0)
    heater_hours = data.get("heater_hours_per_week", 0)
    temperature = data.get("temperature", 30.0)
    members = data.get("members", 4)

    if ac_count > 0 and ac_hours > 6:
        saving = round(ac_count * (ac_hours - 6) * ac_tons * 0.7 * 30, 1)
        recs.append({
            "title": "Reduce AC usage",
            "description": f"Your AC runs {ac_hours:.0f} hrs/day. Reducing to 6 hrs could save ~{saving} kWh/month.",
            "category": "Air Conditioner",
            "saving_kwh": saving,
            "icon": "ac",
        })

    if ac_count > 0 and ac_tons >= 2:
        recs.append({
            "title": "Consider inverter AC",
            "description": "Inverter ACs consume 30–40% less electricity than non-inverter units at the same cooling capacity.",
            "category": "Air Conditioner",
            "saving_kwh": round(ac_count * ac_hours * ac_tons * 0.7 * 0.35 * 30, 1),
            "icon": "ac",
        })

    if ac_count > 0 and temperature >= 30:
        recs.append({
            "title": "Set AC to 24°C",
            "description": "Each degree above 24°C saves approximately 6% on cooling energy. Set thermostat to 24°C.",
            "category": "Air Conditioner",
            "saving_kwh": round(ac_count * ac_hours * 0.15 * 30, 1),
            "icon": "temperature",
        })

    if fridge_count >= 2:
        recs.append({
            "title": "Consolidate refrigerators",
            "description": "Each additional fridge consumes ~72 kWh/month. Consider consolidating to one efficient unit.",
            "category": "Refrigerator",
            "saving_kwh": 72.0,
            "icon": "fridge",
        })

    if washer_hours > 3:
        recs.append({
            "title": "Wash with cold water",
            "description": "Cold water washing uses 90% less energy than hot water washing. Use full loads only.",
            "category": "Washing Machine",
            "saving_kwh": round(washer_hours / 7 * 1.2 * 30, 1),
            "icon": "washer",
        })

    if heater_hours > 1:
        recs.append({
            "title": "Use solar water heating",
            "description": "A solar water heater can eliminate water heating electricity costs entirely.",
            "category": "Water Heater",
            "saving_kwh": round(heater_hours / 7 * 1.5 * 30, 1),
            "icon": "heater",
        })

    if fan_count == 0 and ac_count > 0:
        recs.append({
            "title": "Use fans alongside AC",
            "description": "Ceiling fans improve air circulation, letting you raise the AC temperature by 2–3°C without discomfort.",
            "category": "Fans",
            "saving_kwh": round(ac_count * ac_hours * 0.1 * 30, 1),
            "icon": "fan",
        })

    recs.append({
        "title": "Switch to LED lighting",
        "description": "LED bulbs use 75% less energy than incandescent bulbs and last 25× longer.",
        "category": "Lighting",
        "saving_kwh": round(members * 0.3 * 30, 1),
        "icon": "bulb",
    })

    recs.append({
        "title": "Unplug standby devices",
        "description": "Devices on standby can account for 10% of your bill. Unplug chargers and electronics when not in use.",
        "category": "General",
        "saving_kwh": round(units * 0.08, 1),
        "icon": "plug",
    })

    return recs
