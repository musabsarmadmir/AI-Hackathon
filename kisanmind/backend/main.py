# backend/main.py
"""FastAPI entry point for KisanMind.
All agents are thin wrappers around the GPT-4o-mini model.
Each endpoint receives JSON, calls the appropriate agent, and returns a structured response.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

# Load API key from environment (local.env will be sourced when container starts)
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

app = FastAPI(title="KisanMind", version="0.1.0")

# ---------- Request schemas ----------
class ImagePayload(BaseModel):
    image_url: str  # public URL to the crop photo
    location: str | None = None
    language: str | None = "en"

class WeatherPayload(BaseModel):
    location: str

class SupplierPayload(BaseModel):
    crop: str
    location: str
    need: str | None = "fertilizer"

# ---------- Helper for OpenAI calls ----------
def call_gpt(messages: list[dict], temperature: float = 0.2, json_schema: dict | None = None):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_completion_tokens=1024,
            response_format={"type": "json_object"} if json_schema else None,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Endpoints ----------
@app.post("/diagnose")
def diagnose(payload: ImagePayload):
    messages = [
        {"role": "system", "content": "You are an expert agricultural pathologist. Analyze the image URL and give a concise diagnosis (disease name or healthy). Return JSON {\"disease\": string, \"confidence\": number}.",},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": payload.image_url}}]},
    ]
    result = call_gpt(messages, json_schema={"type": "object", "properties": {"disease": {"type": "string"}, "confidence": {"type": "number"}}, "required": ["disease", "confidence"]})
    return result

@app.post("/weather")
def weather(payload: WeatherPayload):
    prompt = f"Provide a 3‑day irrigation recommendation for {payload.location}. Return JSON {{\"schedule\": [{{\"day\": int, \"water_liters\": float}}]}}."
    messages = [{"role": "system", "content": "You are a weather‑aware farming advisor. Use concise, actionable advice."}, {"role": "user", "content": prompt}]
    result = call_gpt(messages, json_schema={"type": "object", "properties": {"schedule": {"type": "array", "items": {"type": "object", "properties": {"day": {"type": "integer"}, "water_liters": {"type": "number"}}, "required": ["day", "water_liters"]}}}, "required": ["schedule"]})
    return result

@app.post("/treatment")
def treatment(crop: str, disease: str):
    prompt = f"Suggest an organic and a chemical treatment for {crop} suffering from {disease}. Return JSON {{\"organic\": string, \"chemical\": string}}."
    messages = [{"role": "system", "content": "You are a crop treatment specialist."}, {"role": "user", "content": prompt}]
    result = call_gpt(messages, json_schema={"type": "object", "properties": {"organic": {"type": "string"}, "chemical": {"type": "string"}}, "required": ["organic", "chemical"]})
    return result

@app.post("/supplier")
def supplier(payload: SupplierPayload):
    prompt = f"Find nearby suppliers for {payload.need} for {payload.crop} in {payload.location}. Return JSON {{\"suppliers\": [{{\"name\": string, \"address\": string, \"distance_km\": number}}]}}."
    messages = [{"role": "system", "content": "You are a local services finder. Use only public data, do not fabricate addresses."}, {"role": "user", "content": prompt}]
    result = call_gpt(messages, json_schema={"type": "object", "properties": {"suppliers": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "address": {"type": "string"}, "distance_km": {"type": "number"}}, "required": ["name", "address", "distance_km"]}}}, "required": ["suppliers"]})
    return result
