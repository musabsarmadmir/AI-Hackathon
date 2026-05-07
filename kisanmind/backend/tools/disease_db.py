"""
Disease knowledge base tool.
Loads and searches the curated crop disease database.
"""

import json
from pathlib import Path

DISEASES_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "diseases.json"
TREATMENTS_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "treatments.json"
CROPS_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "crops.json"

# Load databases at module level
_diseases: list[dict] = []
_treatments: list[dict] = []
_crops: list[dict] = []


def _load_databases():
    global _diseases, _treatments, _crops
    if not _diseases:
        with open(DISEASES_PATH, "r") as f:
            _diseases = json.load(f)
        with open(TREATMENTS_PATH, "r") as f:
            _treatments = json.load(f)
        with open(CROPS_PATH, "r") as f:
            _crops = json.load(f)


def search_disease_database(query: str, crop_type: str = "") -> list[dict]:
    """Search diseases by name, symptoms, or crop type."""
    _load_databases()
    results = []
    query_lower = query.lower()

    for disease in _diseases:
        score = 0
        # Match by name
        if query_lower in disease["name"].lower():
            score += 10
        # Match by crop
        if crop_type and crop_type.lower() in disease["crop"].lower():
            score += 5
        # Match by symptoms
        for symptom in disease["symptoms"]:
            if query_lower in symptom.lower():
                score += 3
        # Match by any field
        if query_lower in json.dumps(disease).lower():
            score += 1

        if score > 0:
            results.append({**disease, "_relevance_score": score})

    results.sort(key=lambda x: x["_relevance_score"], reverse=True)
    return results[:5]


def get_disease_by_id(disease_id: str) -> dict | None:
    """Get disease details by ID."""
    _load_databases()
    for disease in _diseases:
        if disease["id"] == disease_id:
            return disease
    return None


def get_treatments_for_disease(disease_id: str) -> dict | None:
    """Get treatment options for a specific disease."""
    _load_databases()
    for treatment in _treatments:
        if treatment["disease_id"] == disease_id:
            return treatment
    return None


def get_crop_info(crop_name: str) -> dict | None:
    """Get crop lifecycle information."""
    _load_databases()
    crop_lower = crop_name.lower()
    for crop in _crops:
        if crop_lower in crop["name"].lower() or crop_lower == crop["id"]:
            return crop
    return None


def get_all_diseases_for_crop(crop_name: str) -> list[dict]:
    """Get all known diseases for a specific crop."""
    _load_databases()
    crop_lower = crop_name.lower()
    return [d for d in _diseases if crop_lower in d["crop"].lower() or d["crop"] == "general"]


def get_diseases_summary_for_prompt() -> str:
    """Generate a condensed disease database summary for the LLM system prompt."""
    _load_databases()
    lines = []
    for d in _diseases:
        symptoms_str = "; ".join(d["symptoms"][:3])
        lines.append(f"- {d['name']} ({d['crop']}): {symptoms_str}")
    return "\n".join(lines)
