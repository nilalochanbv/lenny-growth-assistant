from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.db.models import TranscriptChunk
from backend.app.agents.providers.ollama_provider import OllamaProvider
from backend.app.agents.providers.cloud_provider import CloudProvider

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Check DB
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check transcript chunks count
    chunks_count = 0
    if db_ok:
        try:
            chunks_count = db.query(TranscriptChunk).count()
        except Exception:
            chunks_count = 0

    # Check Ollama
    ollama_provider = OllamaProvider()
    ollama_status = await ollama_provider.health_check()

    # Check Cloud Provider
    cloud_provider = CloudProvider()
    cloud_status = await cloud_provider.health_check()

    overall_status = "healthy" if db_ok else "degraded"

    return {
        "status": overall_status,
        "database": {
            "connected": db_ok,
            "total_indexed_chunks": chunks_count
        },
        "local_provider": {
            "name": ollama_status.provider_name,
            "available": ollama_status.is_available,
            "message": ollama_status.message
        },
        "cloud_provider": {
            "name": cloud_status.provider_name,
            "available": cloud_status.is_available,
            "message": cloud_status.message
        }
    }
