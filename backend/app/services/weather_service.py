"""
weather_service.py
Fetches the past 30-day weather average for a Sri Lankan district.
Uses Open-Meteo archive API for historical data.

Monthly averages align with the monthly temporal resolution used across
all datasets in this study (appliance usage, consumption patterns).
"""

import requests
from datetime import date, timedelta

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

FALLBACK = {
    "avg_temp":     29.0,
    "avg_humidity": 78.0,
    "total_precip": 15.0,
    "avg_wind":     12.0,
}


def get_weather(district: str) -> dict:
    """
    Fetch 30-day monthly average weather for a district.
    Uses archive API for past 30 days — more representative
    of the billing period than a single current reading.
    """
    district = district.lower().replace(" ", "_")
    lat, lon = DISTRICT_COORDS.get(district, DISTRICT_COORDS["colombo"])

    # Past 30 days — yesterday back to 30 days ago
    # (archive API needs completed days, not today)
    end_date   = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=29)

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date.isoformat()}"
        f"&end_date={end_date.isoformat()}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"relative_humidity_2m_mean,precipitation_sum,"
        f"windspeed_10m_max"
        f"&timezone=Asia%2FColombo"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})

        temps_max  = daily.get("temperature_2m_max", [])
        temps_min  = daily.get("temperature_2m_min", [])
        humidities = daily.get("relative_humidity_2m_mean", [])
        precips    = daily.get("precipitation_sum", [])
        winds      = daily.get("windspeed_10m_max", [])

        def avg(lst):
            return round(sum(lst) / len(lst), 1) if lst else 0.0

        # Daily mean temp = (max + min) / 2, then average across 30 days
        daily_means = [(h + l) / 2 for h, l in zip(temps_max, temps_min)]
        avg_temp    = round(avg(daily_means), 1)
        avg_humidity = avg(humidities)
        total_precip = round(sum(precips), 1) if precips else 0.0
        avg_wind     = avg(winds)

        return {
            "avg_temp":     avg_temp,
            "avg_humidity": avg_humidity,
            "total_precip": total_precip,
            "avg_wind":     avg_wind,
            "period_start": start_date.isoformat(),
            "period_end":   end_date.isoformat(),
            "district":     district,
            "lat":          lat,
            "lon":          lon,
        }

    except Exception as e:
        return {
            **FALLBACK,
            "period_start": (date.today() - timedelta(days=7)).isoformat(),
            "period_end":   (date.today() - timedelta(days=1)).isoformat(),
            "district":     district,
            "error":        str(e),
        }