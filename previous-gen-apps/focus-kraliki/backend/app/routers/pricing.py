from fastapi import APIRouter

router = APIRouter(prefix="/pricing", tags=["pricing"])

# Model catalog for pricing display (aligned with stack-2026/LLM_MODELS.md)
MODEL_CATALOG = [
    {
        "id": "google/gemini-3-flash-preview",
        "name": "Gemini 3 Flash",
        "provider": "Google",
        "description": "Multimodal general-purpose model for daily Focus work",
        "inputPrice": 0.50,  # per 1M tokens
        "outputPrice": 3.00,
        "contextWindow": 1048576,
        "recommended": True,
        "features": ["Multimodal", "Fast", "Huge context"]
    },
    {
        "id": "z-ai/glm-4.7",
        "name": "GLM-4.7",
        "provider": "Z.AI",
        "description": "Best-in-class coding and reasoning",
        "inputPrice": 0.60,
        "outputPrice": 2.20,
        "contextWindow": 202752,
        "recommended": True,
        "features": ["Coding", "Reasoning", "SWE-bench 73.8%"]
    },
    {
        "id": "meta-llama/llama-4-scout",
        "name": "Llama 4 Scout",
        "provider": "Groq",
        "description": "Real-time apps with ultra-low latency",
        "inputPrice": 0.11,
        "outputPrice": 0.34,
        "contextWindow": 327680,
        "recommended": False,
        "features": ["275+ t/s", "Realtime", "Low cost"]
    },
    {
        "id": "meta-llama/llama-3.3-70b-instruct",
        "name": "Llama 3.3 70B",
        "provider": "Groq",
        "description": "Quality + speed balance",
        "inputPrice": 0.59,
        "outputPrice": 0.79,
        "contextWindow": 131072,
        "recommended": False,
        "features": ["Balanced", "Fast", "Large model"]
    },
    {
        "id": "deepseek/deepseek-v3.2",
        "name": "DeepSeek V3.2",
        "provider": "DeepSeek",
        "description": "Budget option for bulk processing",
        "inputPrice": 0.22,
        "outputPrice": 0.32,
        "contextWindow": 163840,
        "recommended": False,
        "features": ["Budget", "Bulk", "Efficient"]
    }
]

@router.get("/models")
async def list_models():
    """Get available AI models with pricing"""
    return {
        "models": MODEL_CATALOG,
        "total": len(MODEL_CATALOG),
        "currency": "USD",
        "unit": "per 1M tokens"
    }
