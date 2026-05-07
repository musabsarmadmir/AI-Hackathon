"""
Weather Agent — fetches forecasts and generates crop-specific weather advisories.
"""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.tools.weather_api import get_weather_forecast

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are KisanMind's Weather Agent — an expert in interpreting weather 
data for agricultural decision-making.

Given weather data, produce a structured JSON advisory for farmers covering:
1. Crop risk assessment based on forecast conditions
2. Irrigation recommendation (irrigate now / delay / reduce)
3. Specific warnings (disease outbreak risk during humidity, frost risk, heat stress, storm)
4. Actionable advisory in simple farmer-friendly language

Respond ONLY with JSON in this exact schema:
{
  "location": "City, Region",
  "current_temp": 32.5,
  "current_humidity": 55,
  "forecast": [...],
  "crop_risk_level": "medium",
  "risk_factors": ["Rain expected in 2 days — delay fungicide spray", "High humidity favors fungal diseases"],
  "irrigation_recommendation": "Delay irrigation by 3 days — rain expected on May 10",
  "advisory": "Good planting weather this week. Prepare fields now before rain arrives Thursday."
}"""


async def run_weather_agent(
    sub_query: str,
    lat: float | None,
    lon: float | None,
    crop_type: str | None
) -> dict:
    """Fetch weather and generate agricultural advisory."""
    # Default to Lahore if no coordinates
    lat = lat or 31.5204
    lon = lon or 74.3587

    weather_data = await get_weather_forecast(lat, lon, days=5)

    prompt = f"""Weather data:
{json.dumps(weather_data, indent=2)}

Farmer's query: {sub_query}
Crop type: {crop_type or 'general crops'}

Analyze this weather data and produce a crop advisory JSON."""

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,
        max_tokens=800,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    # Merge raw forecast data in case the LLM dropped it
    result.setdefault("forecast", weather_data.get("forecast", []))
    return result
