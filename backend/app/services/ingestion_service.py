import os
import re
import json
import uuid
import math
import hashlib
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session as DBSession
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import TranscriptChunk

# Dimension for local text embedding projection
EMBED_DIM = 256

def compute_text_embedding(text: str, dim: int = EMBED_DIM) -> List[float]:
    """
    Computes a deterministic, normalized dense semantic feature embedding vector
    using character & word n-gram hashing with term-frequency sublinear scaling.
    This provides reproducible, zero-external-dependency semantic representation.
    """
    words = re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', text.lower())
    if not words:
        return [0.0] * dim
        
    vec = [0.0] * dim
    
    # Unigrams and bigrams
    ngrams = words[:]
    for i in range(len(words) - 1):
        ngrams.append(f"{words[i]}_{words[i+1]}")
        
    for token in ngrams:
        # Hash token into bucket and sign
        h = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 1 else -1.0
        vec[idx] += sign
        
    # Sublinear scaling: sign(x) * log(1 + |x|)
    scaled_vec = []
    norm_sq = 0.0
    for v in vec:
        if v != 0:
            s = math.copysign(math.log(1.0 + abs(v)), v)
        else:
            s = 0.0
        scaled_vec.append(s)
        norm_sq += s * s
        
    norm = math.sqrt(norm_sq)
    if norm > 0:
        return [round(v / norm, 5) for v in scaled_vec]
    return [0.0] * dim


class IngestionService:
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """Extracts YAML-like frontmatter between --- markers and returns (metadata, body)"""
        meta = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                raw_meta = parts[1]
                body = parts[2].strip()
                for line in raw_meta.splitlines():
                    line = line.strip()
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        meta[k] = v
        return meta, body

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Tuple[str, str]]:
        """
        Splits transcript text into overlapping chunks, capturing current speaker if available.
        Returns list of (chunk_text, speaker).
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0
        current_speaker = "Lenny Rachitsky"
        
        # Regex to detect speaker e.g. **Lenny Rachitsky** (00:00:00):
        speaker_pattern = re.compile(r'\*\*([^*]+)\*\*\s*\(([^)]+)\):')

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            speaker_match = speaker_pattern.search(para)
            if speaker_match:
                current_speaker = speaker_match.group(1).strip()

            para_len = len(para)
            if current_len + para_len > chunk_size and current_chunk:
                joined = "\n\n".join(current_chunk)
                chunks.append((joined, current_speaker))
                
                # Keep overlap from end of current chunk
                overlap_text = []
                overlap_len = 0
                for p in reversed(current_chunk):
                    if overlap_len + len(p) <= overlap:
                        overlap_text.insert(0, p)
                        overlap_len += len(p)
                    else:
                        break
                current_chunk = overlap_text
                current_len = overlap_len
                
            current_chunk.append(para)
            current_len += para_len
            
        if current_chunk:
            chunks.append(("\n\n".join(current_chunk), current_speaker))
            
        return chunks

    @classmethod
    def ingest_all(cls, db: DBSession, base_dir: str = None) -> Dict[str, Any]:
        """Ingests all podcasts and newsletters from data directory into PostgreSQL"""
        if not base_dir:
            base_dir = settings.TRANSCRIPTS_DATA_DIR

        logger.info(f"Starting transcript ingestion from {base_dir}")
        index_path = os.path.join(base_dir, "index.json")
        
        index_data = {}
        if os.path.exists(index_path):
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read index.json: {e}")

        files_processed = 0
        chunks_created = 0
        errors = []

        # Find all markdown files in podcasts and newsletters
        md_files = []
        for subdir in ["podcasts", "newsletters"]:
            target_dir = os.path.join(base_dir, subdir)
            if os.path.exists(target_dir):
                for f in os.listdir(target_dir):
                    if f.endswith(".md"):
                        md_files.append((subdir, os.path.join(target_dir, f), f))

        logger.info(f"Discovered {len(md_files)} markdown transcript files")

        for doc_type, file_path, file_name in md_files:
            try:
                rel_id = f"{doc_type}/{file_name}"
                
                # Check metadata from index.json
                meta_from_index = {}
                if doc_type == "podcasts" and "podcasts" in index_data:
                    for item in index_data["podcasts"]:
                        if item.get("filename") == rel_id or item.get("filename") == file_name:
                            meta_from_index = item
                            break
                            
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

                frontmatter, body = cls.parse_frontmatter(content)
                
                title = (
                    frontmatter.get("title") 
                    or meta_from_index.get("title") 
                    or file_name.replace(".md", "").replace("-", " ").title()
                )
                url = (
                    frontmatter.get("post_url") 
                    or meta_from_index.get("post_url") 
                    or f"https://www.lennysnewsletter.com/p/{file_name.replace('.md', '')}"
                )
                guest = frontmatter.get("guest") or meta_from_index.get("guest") or ""
                date = frontmatter.get("date") or meta_from_index.get("date") or ""

                # Delete existing chunks for this doc to prevent duplicate accumulation
                db.query(TranscriptChunk).filter(TranscriptChunk.doc_id == rel_id).delete()

                # Chunk the body text
                chunks = cls.chunk_text(
                    body, 
                    chunk_size=settings.CHUNK_SIZE, 
                    overlap=settings.CHUNK_OVERLAP
                )

                for idx, (chunk_text, speaker) in enumerate(chunks):
                    # compute dense semantic embedding vector
                    embed = compute_text_embedding(f"{title} {guest} {chunk_text}")
                    
                    chunk_record = TranscriptChunk(
                        id=str(uuid.uuid4()),
                        doc_id=rel_id,
                        doc_title=title,
                        doc_url=url,
                        doc_type=doc_type,
                        guest=guest,
                        date=date,
                        chunk_index=idx,
                        speaker=speaker,
                        text=chunk_text,
                        embedding=embed
                    )
                    db.add(chunk_record)
                    chunks_created += 1

                db.commit()
                files_processed += 1
                
            except Exception as e:
                db.rollback()
                err_msg = f"Failed ingesting {file_path}: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)

        logger.info(f"Ingestion complete: {files_processed} files processed, {chunks_created} chunks stored.")
        return {
            "status": "success" if not errors else "partial_success",
            "files_processed": files_processed,
            "chunks_created": chunks_created,
            "errors": errors
        }
