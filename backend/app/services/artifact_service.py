import uuid
import datetime
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from backend.app.db.models import Artifact as ArtifactModel

class ArtifactService:
    @staticmethod
    def create_artifact(
        db: DBSession, 
        session_id: str, 
        title: str, 
        format_type: str, 
        content: str
    ) -> ArtifactModel:
        artifact_id = str(uuid.uuid4())
        artifact = ArtifactModel(
            id=artifact_id,
            session_id=session_id,
            title=title,
            format=format_type.lower(),
            content=content,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return artifact

    @staticmethod
    def get_artifact(db: DBSession, artifact_id: str) -> Optional[ArtifactModel]:
        return db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()

    @staticmethod
    def list_artifacts_by_session(db: DBSession, session_id: str) -> List[ArtifactModel]:
        return db.query(ArtifactModel).filter(ArtifactModel.session_id == session_id).order_by(ArtifactModel.created_at.desc()).all()
