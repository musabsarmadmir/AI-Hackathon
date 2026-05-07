"""
Market price data tool.
Fetches crop market prices (mock data for hackathon, structured for real API integration).
"""


async def fetch_market_prices(crop: str, region: str = "Punjab") -> dict:
    """Fetch current market prices for a crop in a region.
    
    In production, this would scrape from:
    - Pakistan: AMIS (Agriculture Marketing Information Service)
    - India: eNAM (National Agriculture Market)
    
    For hackathon, returns realistic mock data.
    """
    # Mock market data (realistic prices in PKR)
    price_data = {
        "wheat": {
            "current_price": 3900,
            "unit": "Rs/maund (40kg)",
            "markets": [
                {"name": "Lahore Mandi", "price": 3900, "change_7d": 2.1, "change_30d": 5.3},
                {"name": "Faisalabad Mandi", "price": 3850, "change_7d": 1.8, "change_30d": 4.9},
                {"name": "Multan Mandi", "price": 3820, "change_7d": 1.5, "change_30d": 4.2},
            ],
            "trend": "rising",
            "government_support_price": 3900,
        },
        "rice": {
            "current_price": 7500,
            "unit": "Rs/maund (40kg)",
            "markets": [
                {"name": "Lahore Mandi", "price": 7500, "change_7d": -0.5, "change_30d": 3.2},
                {"name": "Gujranwala Mandi", "price": 7600, "change_7d": 0.3, "change_30d": 3.8},
                {"name": "Larkana Mandi", "price": 7200, "change_7d": -1.2, "change_30d": 2.1},
            ],
            "trend": "stable",
            "government_support_price": 7000,
        },
        "cotton": {
            "current_price": 18500,
            "unit": "Rs/maund (40kg)",
            "markets": [
                {"name": "Multan Mandi", "price": 18500, "change_7d": 3.5, "change_30d": 8.2},
                {"name": "Rahim Yar Khan Mandi", "price": 18200, "change_7d": 2.8, "change_30d": 7.5},
            ],
            "trend": "rising",
            "government_support_price": 17000,
        },
        "tomato": {
            "current_price": 2800,
            "unit": "Rs/crate (20kg)",
            "markets": [
                {"name": "Lahore Sabzi Mandi", "price": 2800, "change_7d": -8.5, "change_30d": -15.2},
                {"name": "Islamabad Sabzi Mandi", "price": 3200, "change_7d": -5.2, "change_30d": -12.0},
            ],
            "trend": "falling",
            "government_support_price": None,
        },
        "potato": {
            "current_price": 1800,
            "unit": "Rs/maund (40kg)",
            "markets": [
                {"name": "Okara Mandi", "price": 1800, "change_7d": 1.2, "change_30d": -3.5},
                {"name": "Lahore Mandi", "price": 1900, "change_7d": 0.8, "change_30d": -2.8},
            ],
            "trend": "stable",
            "government_support_price": None,
        },
    }

    crop_lower = crop.lower()
    data = price_data.get(crop_lower, {
        "current_price": 0,
        "unit": "Rs/kg",
        "markets": [{"name": "Data unavailable", "price": 0, "change_7d": 0, "change_30d": 0}],
        "trend": "unknown",
        "government_support_price": None,
    })

    return {
        "crop": crop,
        "region": region,
        **data
    }


async def get_price_trend(crop: str, days: int = 30) -> dict:
    """Get price trend analysis for a crop."""
    prices = await fetch_market_prices(crop)
    trend = prices.get("trend", "unknown")

    analysis = {
        "rising": {
            "recommendation": "HOLD — prices are trending upward. Consider waiting 1-2 weeks for better returns.",
            "risk": "Prices may plateau or correct if supply increases.",
        },
        "falling": {
            "recommendation": "SELL SOON — prices are declining. Sell within the next few days to minimize losses.",
            "risk": "Continued decline expected if supply glut persists.",
        },
        "stable": {
            "recommendation": "SELL at convenience — prices are stable. No urgency, but no benefit to waiting either.",
            "risk": "Low risk. Market is balanced.",
        },
        "unknown": {
            "recommendation": "Insufficient data for recommendation.",
            "risk": "Unknown market conditions.",
        },
    }

    return {
        "crop": crop,
        "trend": trend,
        **analysis.get(trend, analysis["unknown"]),
        "prices": prices
    }
