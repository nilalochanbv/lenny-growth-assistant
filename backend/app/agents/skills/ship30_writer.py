from typing import List, Dict, Any, Optional
from backend.app.schemas.rag import Citation, RetrievalResult
from backend.app.agents.providers.base import BaseLLMProvider

SHIP30_SYSTEM_PROMPT = """You are a master digital writer and editorial essayist trained in the Ship 30 for 30 methodology (Nicolas Cole & Dickie Bush principles) and grounded in Lenny's Podcast and Newsletter archive.

YOUR GOAL: Write a high-voltage, approximately 1,250-word editorial essay on the user's requested topic, strictly grounded in the provided transcript evidence.

ESSAY ARCHITECTURE (MANDATORY FORMAT):
1. **Headline**: An irresistible, clear, non-clickbait headline (Rate of Revelation).
2. **The Hook (First 150 words)**:
   - 1-sentence opening that challenges conventional wisdom.
   - The friction or high-stakes cost of doing it wrong.
   - Thesis statement introducing the framework.
3. **The Core Tension & Context (250 words)**:
   - Why traditional approaches fail in fast-scaling tech companies.
   - Introduce the specific insights and guest wisdom from Lenny's interviews.
4. **The Framework: 3-4 Actionable Pillars (600 words)**:
   - Clear subheadings (H2/H3).
   - Skimmable bullet points and 1-2 sentence paragraphs.
   - Selective **bolding** on crucial mental models and direct quotes from guests.
   - Ground each pillar in specific evidence from the transcript passages.
5. **The 3-Step Execution Playbook (150 words)**:
   - What a PM or founder should do on Monday morning.
6. **The 60-Second Takeaway (100 words)**:
   - Punchy, memorable parting thought that stays with the reader.

RULES:
- Do NOT write shallow generic fluff. Make every paragraph pack dense, actionable value.
- Do NOT invent quotes or guests not in the evidence.
- Maintain formatting with markdown headings (##, ###), blockquotes (>), and bold emphasis.
"""

class Ship30WriterSkill:
    @classmethod
    async def execute(
        cls, 
        topic: str, 
        retrieval_result: RetrievalResult, 
        provider: BaseLLMProvider
    ) -> Dict[str, Any]:
        # Build context from retrieved citations
        evidence_text = ""
        citations = retrieval_result.citations if not retrieval_result.is_empty else []
        for idx, cit in enumerate(citations, 1):
            guest_tag = f" (Guest: {cit.guest})" if cit.guest else ""
            evidence_text += (
                f"\n--- [Source {idx}]: {cit.doc_title}{guest_tag} ---\n"
                f"Transcript Excerpt:\n{cit.excerpt}\n"
            )

        prompt = (
            f"Topic Request: {topic}\n\n"
            f"Available Verified Archive Evidence:\n{evidence_text if evidence_text else 'General product management and growth foundations from Lenny Rachitsky archive.'}\n\n"
            f"Write an exhaustive, comprehensive, approximately 1,250-word Ship 30 for 30-style essay according to the system instructions. "
            f"Ensure every pillar is practical, formatted with bold text and skimmable bullet points, and directly anchored in real practitioner wisdom."
        )

        response = await provider.generate(
            prompt=prompt,
            system_prompt=SHIP30_SYSTEM_PROMPT,
            temperature=0.6,
            max_tokens=3000
        )

        content = response.text
        if response.error:
            content = f"⚠️ *Error generating Ship 30 for 30 essay*: {response.error}"

        return {
            "content": content,
            "citations": citations,
            "skill": "ship30_writer"
        }
