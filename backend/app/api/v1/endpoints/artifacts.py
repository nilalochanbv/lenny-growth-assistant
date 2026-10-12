from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.schemas.artifact import ArtifactResponse
from backend.app.services.artifact_service import ArtifactService

router = APIRouter()

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = ArtifactService.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactResponse(
        id=artifact.id,
        session_id=artifact.session_id,
        title=artifact.title,
        format=artifact.format,
        content=artifact.content,
        created_at=artifact.created_at,
        updated_at=artifact.updated_at
    )

@router.get("/artifacts/session/{session_id}", response_model=List[ArtifactResponse])
def get_session_artifacts(session_id: str, db: Session = Depends(get_db)):
    artifacts = ArtifactService.list_artifacts_by_session(db, session_id)
    return [
        ArtifactResponse(
            id=a.id,
            session_id=a.session_id,
            title=a.title,
            format=a.format,
            content=a.content,
            created_at=a.created_at,
            updated_at=a.updated_at
        ) for a in artifacts
    ]
