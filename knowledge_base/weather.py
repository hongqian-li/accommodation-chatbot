"""
Weather data for HAMK campuses using the Open-Meteo API.

Open-Meteo is free and requires no API key.
API docs: https://open-meteo.com/en/docs
"""

import requests
from knowledge_base.campus_data import CAMPUSES, find_campus

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes → human-readable description
WMO_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "icy fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light showers", 81: "showers", 82: "heavy showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with heavy hail",
}


def _wmo(code: int) -> str:
    return WMO_DESCRIPTIONS.get(code, f"code {code}")


def get_campus_weather(campus_name: str) -> str:
    """
    Fetch current weather and 3-day forecast for a HAMK campus.

    Args:
        campus_name: Lowercase campus/city name (e.g. 'hämeenlinna', 'mustiala').

    Returns:
        Formatted weather string, or '' on failure or unknown campus.
    """
    campus = CAMPUSES.get(campus_name.lower())
    if not campus:
        return ""

    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": campus["lat"],
                "longitude": campus["lon"],
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum",
                "timezone": "Europe/Helsinki",
                "forecast_days": 3,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return ""

    cur = data.get("current", {})
    daily = data.get("daily", {})

    lines = [
        f"Weather at {campus['display']}:",
        (
            f"Now: {cur.get('temperature_2m', '?')}°C, "
            f"{_wmo(cur.get('weather_code', 0))}, "
            f"wind {cur.get('wind_speed_10m', '?')} km/h"
        ),
        "3-day forecast:",
    ]

    dates = daily.get("time", [])
    max_t = daily.get("temperature_2m_max", [])
    min_t = daily.get("temperature_2m_min", [])
    codes = daily.get("weather_code", [])
    precip = daily.get("precipitation_sum", [])

    for i in range(min(3, len(dates))):
        rain = f", {precip[i]:.1f} mm" if precip[i] > 0 else ""
        lines.append(f"  {dates[i]}: {min_t[i]}–{max_t[i]}°C, {_wmo(codes[i])}{rain}")

    return "\n".join(lines)


def get_weather_for_query(query: str) -> str:
    """
    Parse a user query for a campus/city name and return weather info.

    Returns:
        Formatted weather string, or '' if no known location found.
    """
    campus = find_campus(query)
    return get_campus_weather(campus) if campus else ""
