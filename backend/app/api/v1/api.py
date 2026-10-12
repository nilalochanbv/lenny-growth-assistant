from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    models,
    sessions,
    chat,
    artifacts,
    ingestion
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(models.router, tags=["Models"])
api_router.include_router(sessions.router, tags=["Sessions"])
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(artifacts.router, tags=["Artifacts"])
api_router.include_router(ingestion.router, tags=["Ingestion"])
