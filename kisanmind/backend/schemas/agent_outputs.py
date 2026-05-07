"""
Pydantic models for structured agent outputs.
Every agent returns typed, validated JSON — no free-text parsing.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# --- Shared Enums ---

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Confidence(str, Enum):
    HIGH = "high"       # >80%
    MEDIUM = "medium"   # 50-80%
    LOW = "low"         # <50%


class TreatmentType(str, Enum):
    ORGANIC = "organic"
    CHEMICAL = "chemical"
    CULTURAL = "cultural"  # e.g., crop rotation, spacing


# --- Orchestrator Output ---

class AgentTask(BaseModel):
    agent_name: str = Field(description="Name of the agent to invoke")
    sub_query: str = Field(description="Specific question/task for this agent")
    depends_on: Optional[str] = Field(None, description="Agent this task depends on (for sequential execution)")
    priority: int = Field(default=1, description="Execution priority (1=highest)")


class OrchestratorPlan(BaseModel):
    user_intent: str = Field(description="Interpreted intent of the farmer's query")
    tasks: list[AgentTask] = Field(description="List of agent tasks to execute")
    response_language: str = Field(default="en", description="Language code for response (en, ur, hi, pa)")


# --- Crop Doctor Agent Output ---

class DiseaseCandidate(BaseModel):
    disease_name: str = Field(description="Name of the identified disease/pest/deficiency")
    confidence_score: float = Field(description="Confidence percentage (0-100)")
    severity: Severity = Field(description="Severity level of the condition")
    affected_part: str = Field(description="Part of the plant affected (leaf, stem, root, fruit)")
    symptoms_matched: list[str] = Field(description="Specific symptoms that matched")
    description: str = Field(description="Brief description of the disease")


class CropDoctorOutput(BaseModel):
    crop_identified: str = Field(description="Type of crop identified in the image")
    primary_diagnosis: DiseaseCandidate = Field(description="Most likely diagnosis")
    differential_diagnoses: list[DiseaseCandidate] = Field(
        default_factory=list,
        description="Alternative possible diagnoses"
    )
    is_healthy: bool = Field(description="Whether the crop appears healthy")
    urgency: str = Field(description="How urgently action is needed")
    confidence: Confidence = Field(description="Overall confidence level")


# --- Weather Agent Output ---

class DayForecast(BaseModel):
    date: str = Field(description="Date (YYYY-MM-DD)")
    temp_min: float = Field(description="Minimum temperature (°C)")
    temp_max: float = Field(description="Maximum temperature (°C)")
    humidity: int = Field(description="Humidity percentage")
    rain_probability: float = Field(description="Rain probability (0-100%)")
    rain_mm: float = Field(description="Expected rainfall in mm")
    wind_speed: float = Field(description="Wind speed in km/h")
    condition: str = Field(description="Weather condition summary")


class WeatherOutput(BaseModel):
    location: str = Field(description="Location name")
    current_temp: float = Field(description="Current temperature (°C)")
    current_humidity: int = Field(description="Current humidity percentage")
    forecast: list[DayForecast] = Field(description="5-day forecast")
    crop_risk_level: Severity = Field(description="Risk level for crops")
    risk_factors: list[str] = Field(description="Specific weather risks identified")
    irrigation_recommendation: str = Field(description="Watering recommendation")
    advisory: str = Field(description="Weather-specific farming advisory")


# --- Market Agent Output ---

class MarketPrice(BaseModel):
    crop: str = Field(description="Crop name")
    current_price: float = Field(description="Current price per unit")
    unit: str = Field(description="Price unit (e.g., Rs/maund, Rs/kg)")
    market_name: str = Field(description="Market/mandi name")
    price_change_7d: float = Field(description="Price change in last 7 days (%)")
    price_change_30d: float = Field(description="Price change in last 30 days (%)")


class MarketOutput(BaseModel):
    prices: list[MarketPrice] = Field(description="Current market prices")
    trend: str = Field(description="Overall price trend (rising/stable/falling)")
    recommendation: str = Field(description="Buy/sell/hold recommendation")
    reasoning: str = Field(description="Why this recommendation")
    best_market: str = Field(description="Best market to sell at currently")
    estimated_revenue: Optional[str] = Field(None, description="Revenue estimate if applicable")
    confidence: Confidence = Field(description="Confidence in recommendation")


# --- Treatment Agent Output ---

class TreatmentOption(BaseModel):
    treatment_name: str = Field(description="Name of treatment/product")
    treatment_type: TreatmentType = Field(description="Type of treatment")
    active_ingredient: str = Field(description="Active ingredient")
    dosage: str = Field(description="Dosage per acre/hectare")
    application_method: str = Field(description="How to apply")
    frequency: str = Field(description="How often to apply")
    estimated_cost: str = Field(description="Estimated cost")
    effectiveness: str = Field(description="Expected effectiveness")
    safety_warnings: list[str] = Field(default_factory=list, description="Safety precautions")
    waiting_period: str = Field(default="", description="Days to wait before harvest after application")


class TreatmentOutput(BaseModel):
    disease_name: str = Field(description="Disease being treated")
    crop: str = Field(description="Crop type")
    treatments: list[TreatmentOption] = Field(description="Available treatment options")
    recommended_treatment: str = Field(description="Top recommended treatment name")
    prevention_tips: list[str] = Field(description="How to prevent this in the future")
    expected_recovery_days: int = Field(description="Estimated days to recovery with treatment")
    confidence: Confidence = Field(description="Confidence in treatment plan")


# --- Supplier Agent Output ---

class NearbyStore(BaseModel):
    store_name: str = Field(description="Store/dealer name")
    distance_km: float = Field(description="Distance in kilometers")
    address: str = Field(description="Full address")
    phone: Optional[str] = Field(None, description="Phone number if available")
    products_available: list[str] = Field(default_factory=list, description="Relevant products in stock")
    rating: Optional[float] = Field(None, description="Rating if available")


class SupplierOutput(BaseModel):
    stores: list[NearbyStore] = Field(description="Nearby agricultural stores")
    search_radius_km: float = Field(description="Search radius used")
    total_found: int = Field(description="Total stores found")


# --- Combined Final Response ---

class KisanMindResponse(BaseModel):
    """The final synthesized response sent to the user."""
    summary: str = Field(description="Brief, farmer-friendly summary of all findings")
    crop_diagnosis: Optional[CropDoctorOutput] = None
    weather: Optional[WeatherOutput] = None
    market: Optional[MarketOutput] = None
    treatment: Optional[TreatmentOutput] = None
    suppliers: Optional[SupplierOutput] = None
    overall_confidence: Confidence = Field(description="Overall confidence in the response")
    action_items: list[str] = Field(description="Prioritized list of actions the farmer should take")
    warnings: list[str] = Field(default_factory=list, description="Important warnings or alerts")
