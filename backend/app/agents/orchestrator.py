import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session as DBSession
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.session_service import SessionService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.agents.providers.ollama_provider import OllamaProvider
from backend.app.agents.providers.cloud_provider import CloudProvider
from backend.app.agents.skills.knowledge_qa import KnowledgeQASkill
from backend.app.agents.skills.ship30_writer import Ship30WriterSkill
from backend.app.agents.skills.artifact_generator import ArtifactGeneratorSkill

class AgentOrchestrator:
    @staticmethod
    def get_provider(provider_type: Optional[str] = None, model_name: Optional[str] = None):
        ptype = (provider_type or settings.DEFAULT_PROVIDER).lower()
        if ptype == "cloud":
            return CloudProvider(provider_type=settings.CLOUD_PROVIDER, model_name=model_name)
        else:
            return OllamaProvider(model_name=model_name or settings.OLLAMA_MODEL)

    @staticmethod
    def classify_intent(message: str, requested_skill: Optional[str] = None) -> str:
        if requested_skill and requested_skill in ["knowledge_qa", "ship30_writer", "artifact_generator"]:
            return requested_skill

        lower = message.lower()
        
        # Essay keywords
        if any(k in lower for k in [
            "essay", "ship 30", "article", "1250 word", "write an essay", 
            "write an article", "editorial", "newsletter post"
        ]):
            return "ship30_writer"

        # Artifact keywords
        if any(k in lower for k in [
            "artifact", "html", "dashboard", "calculator", "template", 
            "canvas", "checklist", "interactive tool", "create a tool", "generate code"
        ]):
            return "artifact_generator"

        # Default is source-grounded knowledge Q&A
        return "knowledge_qa"

    @classmethod
    async def process_chat(
        cls,
        db: DBSession,
        session_id: str,
        user_message: str,
        provider_preference: Optional[str] = None,
        model_name: Optional[str] = None,
        requested_skill: Optional[str] = None
    ) -> Dict[str, Any]:
        # Retrieve existing messages for session context
        past_msgs = SessionService.get_messages(db, session_id)
        history = [{"role": m.role, "content": m.content} for m in past_msgs]

        # Record user message
        SessionService.add_message(
            db=db,
            session_id=session_id,
            role="user",
            content=user_message
        )

        # Update title if it was first message
        if len(past_msgs) == 0:
            clean_title = re.sub(r'[^\w\s-]', '', user_message).strip()[:40]
            if clean_title:
                SessionService.update_session_title(db, session_id, clean_title.capitalize())

        # Determine skill and provider
        skill_type = cls.classify_intent(user_message, requested_skill)
        provider = cls.get_provider(provider_preference, model_name)
        active_provider_type = "cloud" if isinstance(provider, CloudProvider) else "local"

        logger.info(f"Processing query for session={session_id} with skill={skill_type}, provider={active_provider_type}, model={provider.model_name}")

        # Perform RAG retrieval from transcripts
        retrieval_result = RetrievalService.retrieve(db, query=user_message)

        # Dispatch to appropriate skill
        if skill_type == "ship30_writer":
            result = await Ship30WriterSkill.execute(
                topic=user_message,
                retrieval_result=retrieval_result,
                provider=provider
            )
            artifact = None

        elif skill_type == "artifact_generator":
            result = await ArtifactGeneratorSkill.execute(
                request_text=user_message,
                session_id=session_id,
                retrieval_result=retrieval_result,
                provider=provider,
                db=db
            )
            artifact = result.get("artifact")

        else: # "knowledge_qa"
            result = await KnowledgeQASkill.execute(
                query=user_message,
                retrieval_result=retrieval_result,
                provider=provider,
                history=history
            )
            artifact = None

        response_content = result["content"]
        citations = result.get("citations", [])

        # Serialize citations for database persistence
        serialized_citations = []
        for c in citations:
            if hasattr(c, "model_dump"):
                serialized_citations.append(c.model_dump())
            elif isinstance(c, dict):
                serialized_citations.append(c)

        # Persist assistant message in DB
        assistant_msg = SessionService.add_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=response_content,
            skill=skill_type,
            citations=serialized_citations
        )

        return {
            "session_id": session_id,
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": response_content,
            "skill": skill_type,
            "provider_used": active_provider_type,
            "model_used": provider.model_name,
            "citations": citations,
            "artifact": artifact,
            "created_at": assistant_msg.created_at
        }
