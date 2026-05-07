"""
Crop Doctor Agent – uses the disease knowledge base to map image diagnosis to detailed info.
If the model already provided a disease name, we enrich it with description, severity, and recommended actions.
"""

import json
from pathlib import Path
from backend.config import DISEASES_DB_PATH

# Load disease knowledge once at import time
with open(DISEASES_DB_PATH, "r", encoding="utf-8") as f:
    DISEASE_DB = json.load(f)


def enrich_diagnosis(disease_name: str) -> dict:
    """Return detailed info for a disease, or a generic healthy response if not found."""
    for entry in DISEASE_DB:
        if entry.get("name", "").lower() == disease_name.lower():
            return {
                "disease": entry.get("name"),
                "description": entry.get("description"),
                "symptoms": entry.get("symptoms"),
                "severity": entry.get("severity"),
                "recommended_action": entry.get("recommended_action"),
            }
    # Fallback for unknown disease or healthy crop
    return {
        "disease": disease_name,
        "description": "No detailed info found.",
        "symptoms": [],
        "severity": "unknown",
        "recommended_action": "Consult a local agronomist.",
    }


async def run_crop_doctor_agent(diagnosis_json: str) -> dict:
    """Parse the raw model output, enrich with DB and return structured result."""
    try:
        raw = json.loads(diagnosis_json)
        disease_name = raw.get("disease", "unknown")
    except Exception:
        disease_name = "unknown"
    return enrich_diagnosis(disease_name)
