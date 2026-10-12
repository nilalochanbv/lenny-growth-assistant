from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import AppError, app_error_handler, generic_error_handler
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import TranscriptChunk
from backend.app.services.ingestion_service import IngestionService
from backend.app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up The Lenny Growth Assistant API...")
    init_db()
    
    # Auto-seed initial knowledge base if empty
    db = SessionLocal()
    try:
        count = db.query(TranscriptChunk).count()
        if count == 0:
            logger.info("Knowledge base is empty. Running initial transcript ingestion...")
            IngestionService.ingest_all(db)
        else:
            logger.info(f"Knowledge base already contains {count} indexed transcript chunks.")
    except Exception as e:
        logger.error(f"Error during startup transcript check: {e}")
    finally:
        db.close()
        
    yield
    logger.info("Shutting down The Lenny Growth Assistant API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="The Lenny Growth Assistant: Source-grounded RAG & Ship 30 for 30 workspace for PMs and Founders.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct root health check
@app.get("/health")
def root_health():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
