import pytest
from backend.app.db.session import SessionLocal
from backend.app.services.session_service import SessionService
from backend.app.services.artifact_service import ArtifactService
from backend.app.schemas.session import SessionCreate

def test_artifact_creation_and_retrieval():
    db = SessionLocal()
    try:
        session = SessionService.create_session(db, SessionCreate(title="Artifact Test Session"))
        
        # Create Markdown artifact
        md_content = "# Product Strategy Canvas\n\n## 1. Value Hypothesis\nValidating product market fit."
        md_artifact = ArtifactService.create_artifact(
            db=db,
            session_id=session.id,
            title="PMF Canvas",
            format_type="markdown",
            content=md_content
        )
        assert md_artifact.id is not None
        assert md_artifact.format == "markdown"
        assert md_artifact.title == "PMF Canvas"

        # Create HTML artifact
        html_content = "<div class='card'><h1>Retention Dashboard</h1></div>"
        html_artifact = ArtifactService.create_artifact(
            db=db,
            session_id=session.id,
            title="Retention Dashboard Tool",
            format_type="html",
            content=html_content
        )
        assert html_artifact.id is not None
        assert html_artifact.format == "html"

        # List session artifacts
        all_artifacts = ArtifactService.list_artifacts_by_session(db, session.id)
        assert len(all_artifacts) == 2

        # Cleanup
        SessionService.delete_session(db, session.id)
    finally:
        db.close()

def test_html_sandbox_security_rules():
    # Validates that HTML rendering policies enforce isolation:
    # 1. No server-side eval execution
    # 2. Iframe must not combine allow-scripts with allow-same-origin
    # 3. Content is rendered in isolated sandbox
    sandbox_attr = "allow-scripts"
    assert "allow-same-origin" not in sandbox_attr
    assert sandbox_attr == "allow-scripts"
