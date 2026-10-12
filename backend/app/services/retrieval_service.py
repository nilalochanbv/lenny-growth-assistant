import re
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import TranscriptChunk
from backend.app.schemas.rag import Citation, RetrievalResult
from backend.app.services.ingestion_service import compute_text_embedding

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot))

def lexical_score(query_tokens: List[str], text: str) -> float:
    text_lower = text.lower()
    matches = sum(1 for token in query_tokens if token in text_lower)
    return matches / max(1, len(query_tokens))


class RetrievalService:
    @classmethod
    def retrieve(
        cls, 
        db: DBSession, 
        query: str, 
        top_k: int = None, 
        min_score: float = None
    ) -> RetrievalResult:
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        if min_score is None:
            min_score = settings.MIN_RELEVANCE_SCORE

        clean_query = query.strip()
        if not clean_query:
            return RetrievalResult(query=query, citations=[], is_empty=True, message="Empty query provided.")

        # Compute query embedding
        query_embed = compute_text_embedding(clean_query)
        query_tokens = [t.lower() for t in re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', clean_query)]

        # Fetch candidate chunks from database
        chunks = db.query(TranscriptChunk).all()
        if not chunks:
            logger.warning("No transcript chunks found in database.")
            return RetrievalResult(
                query=query, 
                citations=[], 
                is_empty=True, 
                message="No transcript chunks available in the knowledge base. Ingestion may be required."
            )

        scored_chunks = []
        for c in chunks:
            # Vector similarity
            vec_sim = 0.0
            if c.embedding:
                vec_sim = cosine_similarity(query_embed, c.embedding)

            # Lexical keyword match
            lex_sim = lexical_score(query_tokens, f"{c.doc_title} {c.guest or ''} {c.text}")

            # Hybrid score: 65% vector similarity + 35% lexical match
            final_score = (vec_sim * 0.65) + (lex_sim * 0.35)

            if final_score >= min_score:
                scored_chunks.append((c, final_score))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored_chunks[:top_k]

        citations: List[Citation] = []
        for c, score in top_matches:
            # Build clean excerpt (up to 350 chars)
            excerpt = c.text[:350].strip()
            if len(c.text) > 350:
                excerpt += "..."
                
            citations.append(Citation(
                chunk_id=c.id,
                doc_title=c.doc_title,
                doc_url=c.doc_url,
                speaker=c.speaker,
                date=c.date,
                guest=c.guest,
                excerpt=excerpt,
                score=round(score, 4)
            ))

        if not citations:
            return RetrievalResult(
                query=query,
                citations=[],
                is_empty=True,
                message="No directly relevant evidence found in Lenny's Podcast and Newsletter transcripts."
            )

        return RetrievalResult(query=query, citations=citations, is_empty=False)
