"""
KisanMind Configuration
Loads environment variables and defines app-wide settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from local.env
ENV_PATH = Path(__file__).resolve().parent.parent.parent / "local.env"
load_dotenv(ENV_PATH)

# --- API Keys ---
# Prefer the common name OPENAI_API_KEY but accept legacy OPENAI_KEY for compatibility.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or ""
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY", "")

# --- Model Configuration ---
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.3  # Low temp for factual, reliable outputs
MODEL_MAX_TOKENS = 2048

# --- Agent Configuration ---
AGENT_TIMEOUT_SECONDS = 15
MAX_PARALLEL_AGENTS = 5

# --- Knowledge Base Paths ---
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
DISEASES_DB_PATH = KNOWLEDGE_DIR / "diseases.json"
TREATMENTS_DB_PATH = KNOWLEDGE_DIR / "treatments.json"
CROPS_DB_PATH = KNOWLEDGE_DIR / "crops.json"

# --- Server Configuration ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
