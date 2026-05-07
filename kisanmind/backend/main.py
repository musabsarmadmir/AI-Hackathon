# backend/main.py
"""FastAPI entry point for KisanMind.
All agents are thin wrappers around the GPT-4o-mini model.
Each endpoint receives JSON, calls the appropriate agent, and returns a structured response.
"""

import asyncio
import json
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.config import OPENAI_API_KEY
from backend.agents import orchestrator
from backend.agents.crop_doctor import run_crop_doctor_agent
from backend.agents.weather_agent import run_weather_agent
from backend.agents.market_agent import run_market_agent
from backend.agents.treatment_agent import run_treatment_agent
from backend.agents.supplier_agent import run_supplier_agent
from openai import AsyncOpenAI

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI API key missing. Set OPENAI_API_KEY or OPENAI_KEY in the environment")

app = FastAPI(title="KisanMind", version="0.2.0")


# ---------- Request schemas ----------
class QueryPayload(BaseModel):
    message: str | None = None
    image_url: str | None = None
    crop_type: str | None = None
    location: str | None = None
    language: str | None = "en"


class HealthResponse(BaseModel):
    status: str
    version: str


# small helper to call the model and expect JSON back
async def _call_model_json(messages: list[dict], model: str = "gpt-4o-mini") -> Any:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.post("/query")
async def query(payload: QueryPayload):
    """High-level query endpoint. Uses the orchestrator to plan and run agents in order.

    Returns a JSON object with the orchestrator plan and each agent's result.
    """
    # 1. Ask orchestrator for plan
    plan = await orchestrator.run_orchestrator(payload.message, bool(payload.image_url), payload.crop_type, payload.language or "en")

    results: dict[str, Any] = {"plan": plan, "agent_results": {}}

    # Execute tasks in priority order (ascending number -> higher priority)
    tasks = sorted(plan.get("tasks", []), key=lambda t: t.get("priority", 99))

    # Keep state to pass between agents (e.g., diagnosis -> treatment)
    state: dict[str, Any] = {}

    for task in tasks:
        name = task.get("agent_name")
        sub_query = task.get("sub_query") or payload.message

        if name == "crop_doctor":
            # Produce a diagnosis JSON
            if payload.image_url:
                messages = [
                    {"role": "system", "content": "You are an expert agricultural pathologist. Given an image URL, return JSON {\"disease\": string, \"confidence\": number}. Respond only with JSON."},
                    {"role": "user", "content": f"Image URL: {payload.image_url}\nQuery: {sub_query}"},
                ]
                diagnosis = await _call_model_json(messages)
            else:
                # No image; ask model to infer from text
                messages = [
                    {"role": "system", "content": "You are an expert agricultural pathologist. Given a farmer's description, return JSON {\"disease\": string, \"confidence\": number}. Respond only with JSON."},
                    {"role": "user", "content": sub_query},
                ]
                diagnosis = await _call_model_json(messages)

            # Enrich with DB
            enriched = await run_crop_doctor_agent(json.dumps(diagnosis))
            results["agent_results"]["crop_doctor"] = enriched
            state["diagnosis"] = enriched

        elif name == "weather":
            # latitude/longitude parsing not implemented here; pass None -> agent defaults
            weather_res = await run_weather_agent(sub_query, None, None, payload.crop_type)
            results["agent_results"]["weather"] = weather_res
            state["weather"] = weather_res

        elif name == "market":
            market_res = await run_market_agent(sub_query, payload.crop_type)
            results["agent_results"]["market"] = market_res
            state["market"] = market_res

        elif name == "treatment":
            # treatment depends on diagnosis
            diag = state.get("diagnosis", {})
            disease = diag.get("disease") if isinstance(diag, dict) else None
            crop = payload.crop_type or "wheat"
            treat_res = await run_treatment_agent(crop, disease or task.get("sub_query") or "unknown")
            results["agent_results"]["treatment"] = treat_res
            state["treatment"] = treat_res

        elif name == "supplier":
            supp_res = await run_supplier_agent(sub_query, state.get("treatment"), None, None)
            results["agent_results"]["supplier"] = supp_res
            state["supplier"] = supp_res

        else:
            results["agent_results"][name or "unknown"] = {"error": "Unknown agent"}

        # small cooldown to avoid spiky parallel calls when running locally
        await asyncio.sleep(0.05)

    return results


@app.post("/diagnose")
async def diagnose(payload: QueryPayload):
    if not payload.image_url:
        raise HTTPException(status_code=400, detail="image_url is required for /diagnose")
    messages = [
        {"role": "system", "content": "You are an expert agricultural pathologist. Given an image URL, return JSON {\"disease\": string, \"confidence\": number}. Respond only with JSON."},
        {"role": "user", "content": f"Image URL: {payload.image_url}\nLocation: {payload.location or ''}"},
    ]
    diagnosis = await _call_model_json(messages)
    enriched = await run_crop_doctor_agent(json.dumps(diagnosis))
    # merge raw diagnosis keys (e.g., confidence) into enriched result when missing
    if isinstance(diagnosis, dict):
        for k, v in diagnosis.items():
            enriched.setdefault(k, v)
    return enriched


@app.post("/weather")
async def weather(payload: QueryPayload):
    if not payload.location:
        raise HTTPException(status_code=400, detail="location is required for /weather")
    res = await run_weather_agent(payload.message or "", None, None, payload.crop_type)
    return res


@app.post("/treatment")
async def treatment(payload: QueryPayload):
    # accepts {crop, disease} in message for backward compatibility
    body = payload.message or ""
    # simple parsing if message is JSON-like
    try:
        j = json.loads(body)
        crop = j.get("crop")
        disease = j.get("disease")
    except Exception:
        crop = payload.crop_type or "wheat"
        disease = None
    res = await run_treatment_agent(crop, disease or "unknown")
    return res


@app.post("/supplier")
async def supplier(payload: QueryPayload):
    res = await run_supplier_agent(payload.message or "", None, None, None)
    return res
