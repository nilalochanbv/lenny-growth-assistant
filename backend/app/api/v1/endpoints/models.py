from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.agents.providers.ollama_provider import OllamaProvider
from backend.app.agents.providers.cloud_provider import CloudProvider

router = APIRouter()

@router.get("/models")
async def get_models_config():
    ollama_provider = OllamaProvider()
    ollama_status = await ollama_provider.health_check()

    cloud_provider = CloudProvider()
    cloud_status = await cloud_provider.health_check()

    available_models = []
    
    # Add Ollama models
    if ollama_status.is_available:
        installed = ollama_status.details.get("installed_models", [])
        for m in installed:
            available_models.append({
                "id": m,
                "name": f"Local: {m}",
                "provider": "local",
                "is_default": (m == settings.OLLAMA_MODEL)
            })
    else:
        # Include default configured model marked as offline
        available_models.append({
            "id": settings.OLLAMA_MODEL,
            "name": f"Local: {settings.OLLAMA_MODEL} (Offline)",
            "provider": "local",
            "is_default": True
        })

    # Add Cloud models
    cloud_models = [
        {"id": "gemini-2.5-flash", "name": "Cloud: Gemini 2.5 Flash", "provider": "cloud"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Cloud: Claude 3.5 Sonnet", "provider": "cloud"},
        {"id": "gpt-4o-mini", "name": "Cloud: GPT-4o Mini", "provider": "cloud"}
    ]
    for cm in cloud_models:
        cm["is_default"] = (cm["id"] == settings.CLOUD_MODEL_NAME)
        available_models.append(cm)

    return {
        "default_provider": settings.DEFAULT_PROVIDER,
        "active_local_model": settings.OLLAMA_MODEL,
        "active_cloud_model": settings.CLOUD_MODEL_NAME,
        "local_status": ollama_status.model_dump(),
        "cloud_status": cloud_status.model_dump(),
        "models": available_models
    }
