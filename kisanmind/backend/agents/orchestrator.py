"""
Orchestrator Agent — the brain of KisanMind.
Analyzes farmer intent and routes to specialized sub-agents.
"""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME, MODEL_TEMPERATURE

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are KisanMind's Orchestrator — an intelligent agricultural query router.

Your job is to analyze a farmer's question and produce a JSON execution plan that routes 
the query to the correct specialist agents.

Available agents:
- crop_doctor: Analyze crop photos for disease/pest/nutrient problems
- weather: Get weather forecast and irrigation advice
- market: Get current crop prices and sell/hold recommendations
- treatment: Get treatment plans and dosages for identified diseases
- supplier: Find nearby agricultural stores for products

Rules:
1. If user uploads an image, ALWAYS include crop_doctor.
2. If crop_doctor is included, treatment MUST come after it (depends on diagnosis).
3. If treatment is included, supplier should also be included.
4. Weather is almost always useful — include by default unless query is purely about prices.
5. Only include market if user asks about prices, selling, profit, or market.
6. Detect the farmer's language and set response_language accordingly (en=English, ur=Urdu, hi=Hindi, pa=Punjabi).

Output ONLY valid JSON in this exact format:
{
  "user_intent": "brief description of what farmer wants",
  "response_language": "en",
  "tasks": [
    {
      "agent_name": "crop_doctor",
      "sub_query": "specific task for this agent",
      "depends_on": null,
      "priority": 1
    },
    {
      "agent_name": "weather",
      "sub_query": "check weather risk for treatment application",
      "depends_on": null,
      "priority": 1
    },
    {
      "agent_name": "treatment",
      "sub_query": "treatment plan for diagnosed disease",
      "depends_on": "crop_doctor",
      "priority": 2
    },
    {
      "agent_name": "supplier",
      "sub_query": "find stores with recommended treatment products",
      "depends_on": "treatment",
      "priority": 3
    }
  ]
}
"""


async def run_orchestrator(
    message: str,
    has_image: bool,
    crop_type: str | None,
    language: str = "en"
) -> dict:
    """Analyze user message and produce agent execution plan."""
    user_context = f"Message: {message}"
    if has_image:
        user_context += "\n[User has uploaded a crop photo]"
    if crop_type:
        user_context += f"\nCrop type: {crop_type}"
    user_context += f"\nPreferred language: {language}"

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_context}
        ],
        response_format={"type": "json_object"},
    )

    plan_str = response.choices[0].message.content
    plan = json.loads(plan_str)
    return plan
