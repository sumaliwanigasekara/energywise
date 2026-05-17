import requests

DISTRICT_COORDS = {
    "colombo":      (6.9271,  79.8612),
    "gampaha":      (7.0917,  79.9997),
    "kalutara":     (6.5854,  79.9607),
    "kandy":        (7.2906,  80.6337),
    "galle":        (6.0535,  80.2210),
    "matara":       (5.9549,  80.5550),
    "hambantota":   (6.1241,  81.1185),
    "jaffna":       (9.6615,  80.0255),
    "trincomalee":  (8.5874,  81.2152),
    "batticaloa":   (7.7102,  81.6924),
    "anuradhapura": (8.3114,  80.4037),
    "kurunegala":   (7.4863,  80.3647),
    "ratnapura":    (6.6828,  80.3992),
    "nuwara_eliya": (6.9497,  80.7891),
    "badulla":      (6.9934,  81.0550),
}

WMO_CONDITIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


def get_weather(district: str) -> dict:
    district = district.lower().replace(" ", "_")
    lat, lon = DISTRICT_COORDS.get(district, DISTRICT_COORDS["colombo"])

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weathercode"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=Asia%2FColombo"
        f"&forecast_days=7"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        temperature = current.get("temperature_2m", 30.0)
        humidity = current.get("relative_humidity_2m", 75)
        wmo = current.get("weathercode", 0)
        condition = WMO_CONDITIONS.get(wmo, "Unknown")

        max_temps = daily.get("temperature_2m_max", [temperature] * 7)
        min_temps = daily.get("temperature_2m_min", [temperature] * 7)
        avg_temp = round(
            sum((h + l) / 2 for h, l in zip(max_temps, min_temps)) / len(max_temps), 1
        )

        return {
            "temperature": round(temperature, 1),
            "humidity": humidity,
            "condition": condition,
            "avg_temperature": avg_temp,
            "district": district,
            "lat": lat,
            "lon": lon,
        }

    except Exception as e:
        return {
            "temperature": 30.0,
            "humidity": 75,
            "condition": "Unavailable",
            "avg_temperature": 30.0,
            "district": district,
            "error": str(e),
        }
