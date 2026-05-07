"""
Supplier Finder Agent — locates nearby agricultural stores carrying recommended products.
"""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.tools.maps_api import find_nearby_stores

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are KisanMind's Supplier Finder — you help farmers locate the nearest 
stores where they can purchase recommended agricultural products.

Given store location data, produce a helpful JSON summary that tells the farmer:
- Which store to visit first (closest with best rating)
- What products are available where
- Contact information

Keep it practical and farmer-friendly.

Respond ONLY with JSON in this exact schema:
{
  "stores": [
    {
      "store_name": "Malik Agri Store",
      "distance_km": 1.8,
      "address": "Main Bazaar, Near Post Office",
      "phone": "0300-1234567",
      "products_available": ["Propiconazole", "Mancozeb"],
      "rating": 4.3
    }
  ],
  "search_radius_km": 10.0,
  "total_found": 4
}"""


async def run_supplier_agent(
    sub_query: str,
    treatment_result: dict | None,
    lat: float | None,
    lon: float | None
) -> dict:
    """Find nearby stores for recommended treatment products."""
    lat = lat or 31.5204
    lon = lon or 74.3587

    # Extract recommended product from treatment result
    product_type = "pesticide fertilizer"
    if treatment_result:
        recommended = treatment_result.get("recommended_treatment", "")
        if recommended:
            product_type = recommended

    stores_data = await find_nearby_stores(lat, lon, radius_km=10.0, product_type=product_type)

    # Let GPT-4o-mini format and contextualize the response
    prompt = f"""Farmer needs to buy: {product_type}
Query: {sub_query}
Nearby stores found:
{json.dumps(stores_data, indent=2)}

Format this into a helpful supplier summary JSON."""

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,
        max_tokens=500,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    # Ensure raw stores data is always present
    result.setdefault("stores", stores_data.get("stores", []))
    result.setdefault("total_found", stores_data.get("total_found", 0))
    return result
