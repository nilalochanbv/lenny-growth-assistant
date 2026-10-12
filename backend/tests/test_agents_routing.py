import pytest
import asyncio
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.agents.providers.base import BaseLLMProvider, ProviderResponse, ProviderStatus
from backend.app.agents.skills.knowledge_qa import KnowledgeQASkill
from backend.app.agents.skills.ship30_writer import Ship30WriterSkill
from backend.app.schemas.rag import Citation, RetrievalResult

class MockTestProvider(BaseLLMProvider):
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2048):
        return ProviderResponse(
            text="Mock response generated for test with citations [1].",
            model_name="mock-test-model",
            provider_type="mock",
            latency_ms=12.5
        )

    async def health_check(self):
        return ProviderStatus(
            is_available=True,
            provider_name="mock",
            model_name="mock-test-model",
            message="Mock provider ready"
        )

def test_intent_classification_routing():
    # Knowledge QA
    assert AgentOrchestrator.classify_intent("How do great product teams retain users?") == "knowledge_qa"
    assert AgentOrchestrator.classify_intent("What did Shreyas Doshi say about LNO framework?") == "knowledge_qa"

    # Ship 30 for 30 Writer
    assert AgentOrchestrator.classify_intent("Write a Ship 30 for 30 essay about product-market fit") == "ship30_writer"
    assert AgentOrchestrator.classify_intent("Turn these insights into a 1250 word article") == "ship30_writer"

    # Artifact Generator
    assert AgentOrchestrator.classify_intent("Generate an interactive HTML/CSS retention dashboard") == "artifact_generator"
    assert AgentOrchestrator.classify_intent("Create a strategy canvas template artifact") == "artifact_generator"

    # Explicit override takes precedence
    assert AgentOrchestrator.classify_intent("General question", requested_skill="ship30_writer") == "ship30_writer"

@pytest.mark.asyncio
async def test_knowledge_qa_skill_execution():
    mock_provider = MockTestProvider()
    mock_retrieval = RetrievalResult(
        query="retention test",
        citations=[
            Citation(
                chunk_id="chk-123",
                doc_title="Elena Verna on B2B Growth",
                doc_url="https://lennysnewsletter.com/p/elena-verna",
                guest="Elena Verna",
                excerpt="Product-led growth requires clear natural frequency...",
                score=0.88
            )
        ],
        is_empty=False
    )

    result = await KnowledgeQASkill.execute(
        query="What is natural frequency in retention?",
        retrieval_result=mock_retrieval,
        provider=mock_provider
    )

    assert result["skill"] == "knowledge_qa"
    assert len(result["citations"]) == 1
    assert "Mock response" in result["content"]

@pytest.mark.asyncio
async def test_knowledge_qa_honesty_limitation_when_empty():
    mock_provider = MockTestProvider()
    empty_retrieval = RetrievalResult(
        query="unsupported query",
        citations=[],
        is_empty=True
    )

    result = await KnowledgeQASkill.execute(
        query="Can you teach me ancient Greek pottery techniques?",
        retrieval_result=empty_retrieval,
        provider=mock_provider
    )

    assert result["skill"] == "knowledge_qa"
    assert len(result["citations"]) == 0
    assert "Archive Evidence Limitation" in result["content"]
