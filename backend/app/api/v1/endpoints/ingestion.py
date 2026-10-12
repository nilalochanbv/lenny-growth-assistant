from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.db.session import get_db, SessionLocal
from backend.app.db.models import TranscriptChunk
from backend.app.services.ingestion_service import IngestionService
from backend.app.core.logging import logger

router = APIRouter()

def run_background_ingestion():
    db = SessionLocal()
    try:
        IngestionService.ingest_all(db)
    except Exception as e:
        logger.error(f"Background ingestion error: {e}")
    finally:
        db.close()

@router.post("/ingestion/run")
def trigger_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(run_background_ingestion)
    return {
        "status": "started",
        "message": "Transcript ingestion pipeline launched in background."
    }

@router.get("/ingestion/status")
def get_ingestion_status(db: Session = Depends(get_db)):
    total_chunks = db.query(TranscriptChunk).count()
    distinct_docs = db.query(TranscriptChunk.doc_id).distinct().count()
    return {
        "total_chunks": total_chunks,
        "distinct_documents": distinct_docs,
        "is_indexed": total_chunks > 0
    }
