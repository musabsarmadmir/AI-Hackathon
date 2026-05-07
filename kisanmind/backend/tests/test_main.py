import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_query_monkeypatched(monkeypatch):
    # Monkeypatch orchestrator and agent functions to avoid external API calls
    async def fake_orchestrator(message, has_image, crop_type, language):
        return {
            "user_intent": "test",
            "response_language": language,
            "tasks": [
                {"agent_name": "crop_doctor", "sub_query": "", "depends_on": None, "priority": 1},
                {"agent_name": "weather", "sub_query": "", "depends_on": None, "priority": 2},
            ],
        }

    async def fake_run_crop_doctor_agent(d):
        return {"disease": "healthy", "description": "Looks fine", "severity": "low", "recommended_action": "none"}

    async def fake_run_weather_agent(sub_query, lat, lon, crop_type):
        return {"location": "Test City", "forecast": [], "irrigation_recommendation": "none"}

    monkeypatch.setattr("backend.main.orchestrator.run_orchestrator", fake_orchestrator)
    monkeypatch.setattr("backend.main.run_crop_doctor_agent", fake_run_crop_doctor_agent)
    monkeypatch.setattr("backend.main.run_weather_agent", fake_run_weather_agent)

    r = client.post("/query", json={"message": "I have yellow leaves", "image_url": None})
    assert r.status_code == 200
    data = r.json()
    assert "plan" in data
    assert "agent_results" in data
    assert data["agent_results"]["crop_doctor"]["disease"] == "healthy"
*** End Patch