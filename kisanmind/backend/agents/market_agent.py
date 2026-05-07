"""
Market Intelligence Agent — fetches crop prices and generates sell/hold recommendations.
"""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.tools.market_scraper import fetch_market_prices, get_price_trend

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are KisanMind's Market Intelligence Agent — an expert in agricultural 
commodity markets in Pakistan and India.

Given real market price data, produce actionable JSON recommendations for farmers.
Think like a commodity advisor: analyze trend direction, seasonality, and opportunity cost.

Respond ONLY with JSON in this exact schema:
{
  "prices": [
    {"crop": "wheat", "current_price": 3900, "unit": "Rs/maund", "market_name": "Lahore Mandi", "price_change_7d": 2.1, "price_change_30d": 5.3}
  ],
  "trend": "rising",
  "recommendation": "HOLD — prices rising. Wait 1-2 weeks.",
  "reasoning": "Wheat prices have risen 5.3% in the past month driven by export demand. With no major harvest pressure expected, prices likely to stay firm for another 2-3 weeks.",
  "best_market": "Lahore Mandi — currently offering highest price",
  "estimated_revenue": "At current price, 10 maunds = Rs. 39,000",
  "confidence": "high"
}"""


async def run_market_agent(sub_query: str, crop_type: str | None) -> dict:
    """Fetch market data and generate price advisory."""
    # Detect crop from query if not provided
    crops_to_fetch = []
    if crop_type:
        crops_to_fetch.append(crop_type.lower())

    # Also detect crops mentioned in query
    known_crops = ["wheat", "rice", "cotton", "tomato", "potato", "maize", "sugarcane", "mango"]
    for c in known_crops:
        if c in sub_query.lower() and c not in crops_to_fetch:
            crops_to_fetch.append(c)

    if not crops_to_fetch:
        crops_to_fetch = ["wheat"]  # default

    # Fetch price data for all detected crops
    all_prices = []
    for crop in crops_to_fetch[:3]:  # limit to 3
        trend_data = await get_price_trend(crop)
        all_prices.append(trend_data)

    prompt = f"""Market price data:
{json.dumps(all_prices, indent=2)}

Farmer's query: {sub_query}

Analyze this data and produce a market advisory JSON."""

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.3,
        max_tokens=700,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
