"""
API request/response models for the FastAPI endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str = Field(description="The farmer's text message")
    image_base64: Optional[str] = Field(None, description="Base64-encoded crop photo")
    latitude: Optional[float] = Field(None, description="User's latitude for location-based services")
    longitude: Optional[float] = Field(None, description="User's longitude for location-based services")
    language: str = Field(default="en", description="Preferred response language (en, ur, hi, pa)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    crop_type: Optional[str] = Field(None, description="Type of crop if known")


class ChatResponse(BaseModel):
    """Response sent back to the frontend."""
    message: str = Field(description="Farmer-friendly text response")
    structured_data: Optional[dict] = Field(None, description="Structured agent outputs for card rendering")
    agents_used: list[str] = Field(default_factory=list, description="Which agents were invoked")
    execution_time_ms: float = Field(description="Total execution time in milliseconds")
    session_id: str = Field(description="Session ID for follow-up messages")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    model: str = "gpt-4o-mini"
