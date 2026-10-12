import pytest
from backend.app.db.session import SessionLocal
from backend.app.services.ingestion_service import compute_text_embedding, EMBED_DIM
from backend.app.services.retrieval_service import RetrievalService

def test_embedding_computation():
    text = "Retention curves and natural frequency for product growth"
    embed = compute_text_embedding(text)
    assert len(embed) == EMBED_DIM
    # Test normalization: magnitude should be approximately 1.0
    magnitude = sum(x * x for x in embed) ** 0.5
    assert abs(magnitude - 1.0) < 0.05

def test_retrieval_finds_relevant_sources():
    db = SessionLocal()
    try:
        result = RetrievalService.retrieve(db, query="give away your legos Molly Graham", top_k=3)
        assert result.is_empty is False
        assert len(result.citations) > 0
        top_cit = result.citations[0]
        assert "Molly Graham" in (top_cit.guest or top_cit.doc_title)
        assert top_cit.doc_url.startswith("https://")
        assert len(top_cit.excerpt) > 20
        assert top_cit.score > 0.15
    finally:
        db.close()

def test_retrieval_abstention_on_empty_match():
    db = SessionLocal()
    try:
        # Search for completely non-existent technical astrophysics topic
        result = RetrievalService.retrieve(
            db, 
            query="quantum chromodynamics quark gluon plasma strangeness enhancement", 
            min_score=0.35
        )
        assert result.is_empty is True
        assert len(result.citations) == 0
        assert "No directly relevant evidence" in (result.message or "")
    finally:
        db.close()
