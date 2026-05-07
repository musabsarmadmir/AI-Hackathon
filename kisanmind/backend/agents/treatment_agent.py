"""
Treatment Agent – returns organic and chemical treatment recommendations for a given crop and disease.
Leverages the treatments knowledge base and GPT for nuanced suggestions.
"""

import json
from pathlib import Path
from backend.config import TREATMENTS_DB_PATH, OPENAI_API_KEY, MODEL_NAME
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Load treatment knowledge base
with open(TREATMENTS_DB_PATH, "r", encoding="utf-8") as f:
    TREATMENT_DB = json.load(f)

SYSTEM_PROMPT = """You are KisanMind's Treatment Agent. Given a crop and diagnosed disease, provide:
1. An organic treatment (if available) with dosage and application notes.
2. A chemical treatment with dosage, safety interval, and cost estimate.
3. Any precautionary measures (protective gear, withdrawal period).
Return ONLY a JSON object with keys: organic, chemical, precautions.
"""


def lookup_treatment(crop: str, disease: str) -> dict:
    """Find a matching treatment entry; fallback to generic if not found."""
    for entry in TREATMENT_DB:
        if entry.get("crop", "").lower() == crop.lower() and entry.get("disease", "").lower() == disease.lower():
            return entry
    return {}


async def run_treatment_agent(crop: str, disease: str) -> dict:
    """Generate treatment recommendation, enriched with knowledge base where possible."""
    base_info = lookup_treatment(crop, disease)
    prompt = f"Crop: {crop}\nDisease: {disease}\n\nBase info from knowledge base: {json.dumps(base_info, indent=2)}"
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,
        max_tokens=500,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content)
    # Ensure keys exist
    result.setdefault("organic", base_info.get("organic", "Not available"))
    result.setdefault("chemical", base_info.get("chemical", "Not available"))
    result.setdefault("precautions", base_info.get("precautions", []))
    return result
