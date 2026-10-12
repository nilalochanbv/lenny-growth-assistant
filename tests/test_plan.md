# Quality Assurance & Test Verification Plan
## Project: The Lenny Growth Assistant
**Author:** Staff QA Engineer  
**Status:** All Automated & Manual Acceptance Checks Verified

---

## 1. Automated Test Suite Summary
The automated test suite is implemented using `pytest` and `pytest-asyncio`, covering unit contracts, data isolation, RAG retrieval accuracy, and security policies.

### Execution Command:
```bash
python -m pytest backend/tests/ -v
```

### Verified Test Results:
```
backend/tests/test_agents_routing.py::test_intent_classification_routing PASSED
backend/tests/test_agents_routing.py::test_knowledge_qa_skill_execution PASSED
backend/tests/test_agents_routing.py::test_knowledge_qa_honesty_limitation_when_empty PASSED
backend/tests/test_api_validation.py::test_health_endpoint PASSED
backend/tests/test_api_validation.py::test_api_v1_health PASSED
backend/tests/test_api_validation.py::test_models_endpoint PASSED
backend/tests/test_api_validation.py::test_session_creation_and_isolation PASSED
backend/tests/test_artifacts_security.py::test_artifact_creation_and_retrieval PASSED
backend/tests/test_artifacts_security.py::test_html_sandbox_security_rules PASSED
backend/tests/test_retrieval_rag.py::test_embedding_computation PASSED
backend/tests/test_retrieval_rag.py::test_retrieval_finds_relevant_sources PASSED
backend/tests/test_retrieval_rag.py::test_retrieval_abstention_on_empty_match PASSED

======================= 12 passed in 3.01s =======================
```

---

## 2. Test Coverage Breakdown

| Test Suite | File | Focus Area | Status |
| :--- | :--- | :--- | :--- |
| **API Validation** | `test_api_validation.py` | Health endpoints, dependency status, session creation, isolation across sessions, and cascade deletion. | **PASS** |
| **RAG Retrieval** | `test_retrieval_rag.py` | 256-dim embedding normalization, semantic + lexical hybrid matching, source metadata verification, and empty-query handling. | **PASS** |
| **Abstention & Honesty** | `test_retrieval_rag.py` | Verifies system abstains and refuses to hallucinate on out-of-domain topics (e.g. quantum astrophysics). | **PASS** |
| **Agent Routing** | `test_agents_routing.py` | Intent classification between Q&A, Ship 30 for 30 essay, and Artifact generation; explicit parameter overrides. | **PASS** |
| **Artifact Security** | `test_artifacts_security.py` | Markdown and HTML persistence in PostgreSQL; verification of `sandbox="allow-scripts"` isolation rules without `allow-same-origin`. | **PASS** |

---

## 3. Manual UI Acceptance Checklist

The following acceptance scenarios have been verified using the integrated automated browser subagent and live application verification:

- [x] **1. Initial Application Shell**:
  - The application loads at `http://localhost:5173` with dark-first theme styling.
  - Sidebar displays "Lenny Growth", "PRO" badge, "New Conversation" button, and search input.
  - Footer displays live chunk count (`6,479 chunks`) and settings cog.
  - Top header shows session title and provider pill (`Local Ollama: qwen2.5:0.5b`).

- [x] **2. Empty State & Starter Prompts**:
  - Welcome banner and 4 starter prompt cards are visible on fresh load.
  - Clicking a starter card initiates a real backend request without requiring manual typing.

- [x] **3. Source-Grounded Answering & Citations**:
  - Asking *"What did Molly Graham say about giving away your Legos?"* retrieves real transcript passages from Molly Graham's episode.
  - Inline citation chips (`[1]`, `[2]`) appear below the assistant message.
  - Clicking any citation chip opens the Evidence Modal showing the full excerpt, episode title, and direct link to LennysNewsletter.com.

- [x] **4. Follow-up Context Within Session**:
  - Follow-up question *"What practical advice does she give for managers?"* retains conversational context.
  - Both turns persist in PostgreSQL and remain accessible upon page reload.

- [x] **5. Artifact Generation & Sandboxed Preview**:
  - Asking *"Generate an interactive HTML/CSS Product Retention Scorecard"* triggers the artifact generator skill.
  - The split side panel slides open displaying the interactive tool in an isolated sandbox.
  - "Source" tab displays the underlying HTML/CSS code.
  - "Copy" and "Download" buttons successfully export the deliverable.

- [x] **6. Settings & Diagnostics Modal**:
  - Clicking the settings icon displays PostgreSQL status (`Connected (Port 5432)`), Ollama status (`Online`), and indexed chunk count.
  - Switching inference engine toggles between Local Ollama and Cloud LLM.
