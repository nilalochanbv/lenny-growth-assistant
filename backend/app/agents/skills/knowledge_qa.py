from typing import List, Dict, Any, Optional
from backend.app.schemas.rag import Citation, RetrievalResult
from backend.app.agents.providers.base import BaseLLMProvider

SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an authoritative, rigorous AI advisor trained on Lenny's Podcast and Lenny's Newsletter archive.

CRITICAL OPERATIONAL RULES:
1. Ground every statement in the provided Transcript Evidence passages.
2. If the provided evidence is empty or does not directly answer the user's question, you MUST explicitly state that the archive lacks evidence on this topic. Do NOT hallucinate or extrapolate beyond what the guests and Lenny discussed.
3. When referencing insights, explicitly cite the guest name, episode title, and provide inline markers like [1], [2] matching the provided evidence order.
4. Maintain a clear, editorial, high-signal tone suitable for staff product managers, startup founders, and growth leaders.
"""

class KnowledgeQASkill:
    @classmethod
    async def execute(
        cls, 
        query: str, 
        retrieval_result: RetrievalResult, 
        provider: BaseLLMProvider,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        # Handle empty retrieval
        if retrieval_result.is_empty or not retrieval_result.citations:
            limitation_response = (
                "**Archive Evidence Limitation:**\n\n"
                "I searched the indexed archive of Lenny's Podcast and Lenny's Newsletter transcripts, "
                "but I could not find verifiable passages discussing this specific question.\n\n"
                "To uphold source grounding and avoid hallucination, I cannot provide an ungrounded answer. "
                "Consider asking about topics frequently covered in the archive, such as:\n"
                "- How great product teams improve retention and engagement\n"
                "- Approaches to finding and maintaining product-market fit\n"
                "- Molly Graham's 'Give away your Legos' framework in high-growth companies\n"
                "- Pricing and monetization strategies for B2B and consumer tech"
            )
            return {
                "content": limitation_response,
                "citations": [],
                "skill": "knowledge_qa"
            }

        # Build context from retrieved citations
        evidence_text = ""
        for idx, cit in enumerate(retrieval_result.citations, 1):
            speaker_tag = f" (Speaker: {cit.speaker})" if cit.speaker else ""
            guest_tag = f" (Guest: {cit.guest})" if cit.guest else ""
            evidence_text += (
                f"\n--- [Source {idx}]: {cit.doc_title}{guest_tag}{speaker_tag} ---\n"
                f"URL: {cit.doc_url}\n"
                f"Transcript Excerpt:\n{cit.excerpt}\n"
            )

        # Build prompt including chat history context if available
        history_context = ""
        if history:
            recent_turns = history[-4:]  # last 2 exchanges
            history_context = "Recent Conversation History:\n"
            for msg in recent_turns:
                history_context += f"{msg.get('role', 'user').title()}: {msg.get('content', '')}\n"
            history_context += "\n"

        prompt = (
            f"{history_context}"
            f"User Question: {query}\n\n"
            f"Verified Transcript Evidence:\n{evidence_text}\n\n"
            f"Instructions: Answer the question thoroughly, citing the specific sources and speakers using [1], [2], etc. "
            f"Explain the practical takeaways for product managers and founders based on the evidence."
        )

        response = await provider.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.4
        )

        content = response.text
        if response.error:
            content = f"⚠️ *Error calling model provider*: {response.error}\n\nRetrieved sources are listed below for your reference."

        return {
            "content": content,
            "citations": retrieval_result.citations,
            "skill": "knowledge_qa"
        }
