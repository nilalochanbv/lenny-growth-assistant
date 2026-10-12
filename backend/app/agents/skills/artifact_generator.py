import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from backend.app.schemas.rag import RetrievalResult
from backend.app.agents.providers.base import BaseLLMProvider
from backend.app.services.artifact_service import ArtifactService

ARTIFACT_SYSTEM_PROMPT = """You are an expert product architect and growth artifact generator for The Lenny Growth Assistant.

Your task is to produce a standalone, production-ready deliverable requested by the user, grounded in transcript insights.
Acceptable formats:
1. Markdown Document: Comprehensive strategy canvas, PRD template, career matrix, or growth audit checklist.
2. Complete HTML/CSS Artifact: Standalone single-page interactive tool, retention scorecard, or executive dashboard with embedded CSS styles.

CRITICAL OUTPUT FORMAT:
You MUST structure your response into two distinct parts:
PART 1: A brief, friendly chat message (1-2 paragraphs) introducing the artifact to the user.
PART 2: The complete artifact code, wrapped strictly inside an artifact block:

```artifact:format[Title of Deliverable]
[Your complete Markdown or HTML/CSS code goes here]
```
where format is either 'markdown' or 'html'.

HTML REQUIREMENTS:
- If format is HTML, include complete self-contained HTML with embedded `<style>` tags.
- Use elegant, modern, dark-themed styling (slate/charcoal background `#0f172a`, border `#334155`, text `#f8fafc`, accent `#38bdf8` or `#6366f1`).
- Never use external script tags or insecure remote assets.
"""

class ArtifactGeneratorSkill:
    @classmethod
    async def execute(
        cls, 
        request_text: str, 
        session_id: str, 
        retrieval_result: RetrievalResult, 
        provider: BaseLLMProvider,
        db: DBSession
    ) -> Dict[str, Any]:
        evidence_text = ""
        citations = retrieval_result.citations if not retrieval_result.is_empty else []
        for idx, cit in enumerate(citations, 1):
            evidence_text += f"\n--- [Source {idx}]: {cit.doc_title} ---\n{cit.excerpt}\n"

        prompt = (
            f"User Deliverable Request: {request_text}\n\n"
            f"Relevant Transcript Evidence:\n{evidence_text if evidence_text else 'General product and growth best practices.'}\n\n"
            f"Generate a polished, complete deliverable following the artifact block format specified."
        )

        response = await provider.generate(
            prompt=prompt,
            system_prompt=ARTIFACT_SYSTEM_PROMPT,
            temperature=0.4,
            max_tokens=3500
        )

        raw_text = response.text
        if response.error:
            return {
                "content": f"⚠️ *Error generating artifact*: {response.error}",
                "citations": citations,
                "skill": "artifact_generator",
                "artifact": None
            }

        # Parse artifact block: ```artifact:format[Title] ... ```
        pattern = re.compile(r'```artifact:(markdown|html)\[(.*?)\]\s*(.*?)\s*```', re.DOTALL | re.IGNORECASE)
        match = pattern.search(raw_text)

        artifact_record = None
        clean_chat_message = raw_text

        if match:
            fmt = match.group(1).lower()
            title = match.group(2).strip() or "Generated Deliverable"
            code = match.group(3).strip()

            # Clean out the artifact code block from the chat message
            clean_chat_message = pattern.sub(f"\n\n*(Created artifact: **{title}** — viewable in the side panel)*\n\n", raw_text).strip()

            # Persist artifact in DB
            artifact_model = ArtifactService.create_artifact(
                db=db,
                session_id=session_id,
                title=title,
                format_type=fmt,
                content=code
            )
            artifact_record = {
                "id": artifact_model.id,
                "session_id": artifact_model.session_id,
                "title": artifact_model.title,
                "format": artifact_model.format,
                "content": artifact_model.content,
                "created_at": artifact_model.created_at,
                "updated_at": artifact_model.updated_at
            }
        else:
            # Fallback: Check if there's standard markdown code block or html
            html_block = re.search(r'```html\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
            if html_block:
                code = html_block.group(1).strip()
                title = "Interactive Deliverable"
                artifact_model = ArtifactService.create_artifact(
                    db=db,
                    session_id=session_id,
                    title=title,
                    format_type="html",
                    content=code
                )
                artifact_record = {
                    "id": artifact_model.id,
                    "session_id": artifact_model.session_id,
                    "title": artifact_model.title,
                    "format": "html",
                    "content": code,
                    "created_at": artifact_model.created_at,
                    "updated_at": artifact_model.updated_at
                }

        return {
            "content": clean_chat_message,
            "citations": citations,
            "skill": "artifact_generator",
            "artifact": artifact_record
        }
