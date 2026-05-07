"""
OpenWeatherMap API integration.
Provides weather forecast and crop risk assessment tools.
"""

import httpx
from backend.config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"


async def get_weather_forecast(lat: float, lon: float, days: int = 5) -> dict:
    """Fetch weather forecast for given coordinates."""
    if not OPENWEATHER_API_KEY:
        # Return mock data for development/demo
        return _get_mock_forecast(lat, lon, days)

    async with httpx.AsyncClient(timeout=10) as client:
        # Current weather
        current_resp = await client.get(
            f"{BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        )
        current_data = current_resp.json()

        # 5-day forecast (3-hour intervals)
        forecast_resp = await client.get(
            f"{BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        )
        forecast_data = forecast_resp.json()

    # Process into daily summaries
    daily_forecasts = _process_forecast(forecast_data, days)

    return {
        "location": current_data.get("name", f"{lat},{lon}"),
        "current": {
            "temp": current_data["main"]["temp"],
            "humidity": current_data["main"]["humidity"],
            "condition": current_data["weather"][0]["description"],
            "wind_speed": current_data["wind"]["speed"] * 3.6  # m/s to km/h
        },
        "forecast": daily_forecasts
    }


def _process_forecast(forecast_data: dict, days: int) -> list[dict]:
    """Process 3-hour forecast data into daily summaries."""
    daily = {}
    for entry in forecast_data.get("list", [])[:days * 8]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {"temps": [], "humidity": [], "rain": 0, "wind": [], "conditions": []}
        daily[date]["temps"].append(entry["main"]["temp"])
        daily[date]["humidity"].append(entry["main"]["humidity"])
        daily[date]["rain"] += entry.get("rain", {}).get("3h", 0)
        daily[date]["wind"].append(entry["wind"]["speed"] * 3.6)
        daily[date]["conditions"].append(entry["weather"][0]["description"])

    result = []
    for date, data in list(daily.items())[:days]:
        result.append({
            "date": date,
            "temp_min": round(min(data["temps"]), 1),
            "temp_max": round(max(data["temps"]), 1),
            "humidity": round(sum(data["humidity"]) / len(data["humidity"])),
            "rain_mm": round(data["rain"], 1),
            "rain_probability": min(100, data["rain"] * 20),  # rough estimate
            "wind_speed": round(sum(data["wind"]) / len(data["wind"]), 1),
            "condition": max(set(data["conditions"]), key=data["conditions"].count)
        })
    return result


def _get_mock_forecast(lat: float, lon: float, days: int) -> dict:
    """Mock weather data for development without API key."""
    return {
        "location": "Lahore, Punjab",
        "current": {"temp": 32.5, "humidity": 55, "condition": "partly cloudy", "wind_speed": 12.0},
        "forecast": [
            {"date": "2026-05-08", "temp_min": 26, "temp_max": 35, "humidity": 50, "rain_mm": 0, "rain_probability": 10, "wind_speed": 14, "condition": "clear sky"},
            {"date": "2026-05-09", "temp_min": 27, "temp_max": 36, "humidity": 45, "rain_mm": 0, "rain_probability": 5, "wind_speed": 10, "condition": "clear sky"},
            {"date": "2026-05-10", "temp_min": 25, "temp_max": 33, "humidity": 70, "rain_mm": 8.5, "rain_probability": 75, "wind_speed": 18, "condition": "moderate rain"},
            {"date": "2026-05-11", "temp_min": 24, "temp_max": 30, "humidity": 80, "rain_mm": 15.2, "rain_probability": 90, "wind_speed": 22, "condition": "heavy rain"},
            {"date": "2026-05-12", "temp_min": 25, "temp_max": 32, "humidity": 65, "rain_mm": 2.0, "rain_probability": 30, "wind_speed": 15, "condition": "scattered clouds"},
        ][:days]
    }
