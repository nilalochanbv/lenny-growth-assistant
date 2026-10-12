# Product Requirements Document (PRD)
## Project: The Lenny Growth Assistant
**Author:** Principal Product Designer & Staff AI Engineer  
**Status:** Implemented & Verified (v1.0.0)  
**Target Audience:** Product Managers, Startup Founders, Growth Teams, Strategy Practitioners

---

## 1. Executive Summary & Problem Statement
Product managers and startup founders face an information paradox: while world-class practitioners share deep insights on *Lenny's Podcast* and *Lenny's Newsletter*, extracting, validating, and synthesizing these lessons into day-to-day decisions remains manual and time-consuming.

Existing general-purpose LLM chatbots suffer from three critical failures:
1. **Hallucination & Fake Attributions**: They invent generic product frameworks and attribute them to famous guests without source grounding.
2. **Lack of Deliverable Synthesis**: They generate generic chat responses instead of production-ready deliverables (e.g. 1,250-word editorial essays, interactive scorecards, canvases).
3. **Black-Box Architecture**: Users cannot verify the original transcript excerpts, timestamps, or episode context.

**The Lenny Growth Assistant** solves this by coupling a verified transcript knowledge corpus (60+ episodes/posts, 6,400+ indexed chunks) with an evidence-grounded agent architecture, local/cloud model switching, and a sandboxed Artifact Viewer.

---

## 2. Target Users & Personas
- **The Early-Stage Founder**: Needs battle-tested frameworks on finding Product-Market Fit, pricing, and initial retention loops without sifting through 100+ hours of audio.
- **The Growth Lead / Staff PM**: Wants to synthesize retention strategies, audit metrics, and create team playbooks backed by empirical practitioner wisdom (e.g. Elena Verna, Brian Chesky, Shreyas Doshi).
- **The Product Marketing / Content Lead**: Wants to distill high-signal podcasts into publication-ready, ~1,250-word essays following the *Ship 30 for 30* methodology.

---

## 3. Success Metrics & KPIs
1. **Grounding Accuracy**: 100% of factual assertions backed by retrieved transcript chunks; explicit abstention when out-of-domain evidence is absent.
2. **Retrieval Latency**: Hybrid semantic + lexical retrieval executed in under 15ms.
3. **Deliverable Usability**: Generation of complete, standalone Markdown and sandboxed HTML/CSS deliverables rendered without parent DOM interference.
4. **Session Isolation**: 0% conversation leakage across independent session IDs.
5. **Operational Resilience**: Graceful degradation between local Ollama inference and cloud LLM providers without data corruption.

---

## 4. Key Capabilities & Scope

### In-Scope (v1.0)
- **Hybrid RAG Knowledge Retrieval**: Normalized 256-dimensional semantic feature vectors combined with lexical matching against 6,479 transcript chunks.
- **Three Dedicated Agent Skills**:
  - `Knowledge Q&A`: Evidence-grounded answering with inline citation chips and abstention safeguards.
  - `Ship 30 for 30 Writer`: ~1,250-word structured essays featuring bold emphasis, skimmable headings, tension analysis, and tactical takeaways.
  - `Artifact Generator`: Self-contained Markdown and interactive HTML/CSS tools.
- **Interactive In-App Artifact Viewer**: Side-by-side split panel with isolated iframe rendering (`sandbox="allow-scripts"` without `allow-same-origin`), code view, copy, and export.
- **Source Evidence Inspector**: Deep modal showing guest name, publication date, similarity score, transcript excerpt, and link to the original episode.
- **Dual Inference Engine**: Zero-configuration Ollama local inference (`qwen2.5:0.5b`) with cloud adapter support (Gemini, Claude, OpenAI).
- **Persistent Data Store**: PostgreSQL tables for sessions, messages, citations, and artifacts.

### Explicit Non-Goals (Out of Scope for v1.0)
- Server-side execution of untrusted user or generated code (arbitrary Python eval).
- Automatic audio transcription ingestion (uses verified text markdown transcripts).
- Multi-tenant enterprise RBAC (v1 is single-workspace / local developer focused).

---

## 5. User Journey & Core Flows

### Flow 1: Grounded Q&A & Citation Inspection
1. User enters question or clicks a starter prompt (e.g., *"What did Molly Graham say about giving away your Legos?"*).
2. Backend routes to `knowledge_qa` skill and queries PostgreSQL for top-k matching chunks.
3. Assistant returns a structured response with numbered citation chips `[1]`, `[2]`.
4. User clicks a citation chip; the Evidence Modal opens displaying exact quotes and episode metadata.

### Flow 2: Long-Form Essay Generation (Ship 30 for 30)
1. User requests: *"Write an essay about leadership burnout during hypergrowth."*
2. Orchestrator detects essay intent and dispatches to `ship30_writer` skill.
3. Skill retrieves relevant practitioner discussions and formats a ~1,250-word piece with rate of revelation, core friction, 3-4 pillars, execution playbook, and a 60-second takeaway.

### Flow 3: Interactive Deliverable Generation & Preview
1. User asks: *"Generate an interactive HTML/CSS Product Retention Scorecard."*
2. Orchestrator dispatches to `artifact_generator` skill.
3. Artifact is parsed from the response and stored in PostgreSQL `artifacts` table.
4. The side panel automatically slides open, rendering the interactive tool in an isolated sandbox.

---

## 6. Risks, Trade-offs & Mitigations
| Risk | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **Model Hallucination** | High | System prompts enforce strict grounding in supplied evidence; empty retrieval triggers explicit abstention. |
| **Local Inference Latency** | Medium | Configured compact, high-speed model (`qwen2.5:0.5b`, ~397 MB) returning answers in ~8–10s. |
| **XSS in Generated HTML** | Critical | HTML artifacts render exclusively inside an isolated iframe with `sandbox="allow-scripts"` and no `allow-same-origin`. |
| **Database Dependency** | Low | SQLAlchemy connection with automated table creation on startup; resilient SQLite fallback if Postgres is down. |

---

## 7. Acceptance Criteria Checklist
- [x] Full-stack architecture: React + TypeScript (Vite) frontend and FastAPI backend.
- [x] PostgreSQL persistence for sessions, messages, and artifacts.
- [x] Ollama local model integration verified and running.
- [x] Verified transcript dataset ingested (60 documents, 6,479 chunks).
- [x] Traceable citation chips linking to original episode URLs.
- [x] Strict honest limitation response when evidence is not found.
- [x] In-app Artifact Viewer supporting Markdown and isolated HTML.
- [x] Automated test suite passing with 100% test success rate.
