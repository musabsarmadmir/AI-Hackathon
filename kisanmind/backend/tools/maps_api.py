"""
Google Maps Places API integration for finding nearby agricultural stores.
Falls back to mock data if no API key is provided.
"""

import httpx
from backend.config import GOOGLE_MAPS_API_KEY

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


async def find_nearby_stores(lat: float, lon: float, radius_km: float = 10.0, product_type: str = "pesticide") -> dict:
    """Find nearby agricultural supply stores."""
    if not GOOGLE_MAPS_API_KEY:
        return _get_mock_stores(lat, lon, radius_km)

    keywords = "agricultural supply fertilizer pesticide seed store"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            PLACES_URL,
            params={
                "location": f"{lat},{lon}",
                "radius": int(radius_km * 1000),
                "keyword": keywords,
                "key": GOOGLE_MAPS_API_KEY,
            }
        )
        data = resp.json()

    stores = []
    for place in data.get("results", [])[:6]:
        loc = place["geometry"]["location"]
        dist_km = _haversine(lat, lon, loc["lat"], loc["lng"])
        stores.append({
            "store_name": place.get("name", "Unknown Store"),
            "distance_km": round(dist_km, 1),
            "address": place.get("vicinity", "Address not available"),
            "phone": None,
            "products_available": [product_type],
            "rating": place.get("rating"),
        })

    stores.sort(key=lambda x: x["distance_km"])
    return {"stores": stores, "search_radius_km": radius_km, "total_found": len(stores)}


def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Calculate distance in km between two coordinates."""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _get_mock_stores(lat: float, lon: float, radius_km: float) -> dict:
    """Mock nearby stores for development."""
    return {
        "stores": [
            {"store_name": "Malik Agri Store", "distance_km": 1.8, "address": "Main Bazaar, Near Post Office", "phone": "0300-1234567", "products_available": ["Propiconazole", "Mancozeb", "Urea", "DAP"], "rating": 4.3},
            {"store_name": "Chaudhry Seeds & Pesticides", "distance_km": 3.2, "address": "Agriculture Road, Block C", "phone": "0321-7654321", "products_available": ["Tricyclazole", "Emamectin Benzoate", "Neem Oil"], "rating": 4.1},
            {"store_name": "Punjab Agri Solutions", "distance_km": 4.7, "address": "Grain Market, Opposite Bus Stand", "phone": "0333-9876543", "products_available": ["Metalaxyl", "Copper Oxychloride", "Bt Spray", "Vermicompost"], "rating": 4.5},
            {"store_name": "Al-Rehman Fertilizers", "distance_km": 6.1, "address": "Canal Road, Near Pump Station", "phone": "0312-4567890", "products_available": ["Urea", "DAP", "SOP", "Zinc Sulphate"], "rating": 3.9},
        ],
        "search_radius_km": radius_km,
        "total_found": 4,
    }
