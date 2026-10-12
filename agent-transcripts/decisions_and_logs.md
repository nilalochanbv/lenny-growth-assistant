# Engineering Log: Agent Transcripts, Key Decisions & Corrections
## Project: The Lenny Growth Assistant
**Author:** Principal Product Designer & Staff AI Engineer

---

## 1. Architectural Decisions & Rationale

### Decision 1: Verified Transcript Starter Corpus
- **Context**: The assessment requires grounding answers in authentic Lenny's Podcast / Newsletter transcripts without fabricating data.
- **Action**: Ingested the official public starter repository `LennysNewsletter/lennys-newsletterpodcastdata` containing 50 podcast transcripts and 10 newsletter posts in structured markdown.
- **Outcome**: Parsed 6,479 granular chunks with speaker timestamps, episode titles, guest names, and canonical URLs.

### Decision 2: Zero-External-Dependency Semantic Projection
- **Context**: Relying on external embedding API calls during ingestion creates external point-of-failure vulnerabilities, rate limits, and network latency.
- **Action**: Implemented a normalized 256-dimensional semantic feature projection vector based on n-gram hashing and sublinear term-frequency scaling, combined with lexical matching.
- **Outcome**: Entire corpus of 60 documents (6,479 chunks) was ingested and indexed in under 5 seconds into PostgreSQL. Retrieval latency is under 15ms.

### Decision 3: Local Ollama Model Selection
- **Context**: The assessment requires Ollama local inference to work on the host machine.
- **Initial Attempt**: Pulled `llama3.2:1b` (1.3 GB); encountered network TLS timeout during extended download over slower connection.
- **Correction**: Selected `qwen2.5:0.5b` (397 MB), which completed in ~2 minutes. Validated generation latency of ~8-10 seconds on local CPU.

### Decision 4: PostgreSQL Dialect Configuration
- **Issue**: Initial connection attempt with `postgresql://` generated `No module named 'psycopg'` because SQLAlchemy 2.0 defaults to psycopg 3.
- **Correction**: Configured driver explicitly as `postgresql+psycopg2://postgres:postgres@localhost:5432/lenny_growth_db`. Connection succeeded immediately.

### Decision 5: Sandboxed HTML Rendering Policy
- **Requirement**: Prevent XSS and unauthorized access to application cookies, parent DOM, or local storage from generated HTML deliverables.
- **Implementation**: The Artifact Viewer embeds HTML inside an `<iframe>` configured with `sandbox="allow-scripts"` and strictly **omits** `allow-same-origin`. Markdown is passed through `DOMPurify` with strict tag whitelisting.

---

## 2. Iterative Debugging & Corrections Log

| Challenge | Root Cause | Solution Applied | Status |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Authentication** | Service running on Port 5432 had default `scram-sha-256` password requirement. | Updated `pg_hba.conf` to trust for localhost/127.0.0.1, set user password to `postgres`, and created `lenny_growth_db`. | Resolved |
| **Ollama Service Startup** | `ollama.exe` was present in Local Programs but daemon was not running. | Launched `ollama serve` as background service, verified HTTP response on port 11434. | Resolved |
| **TypeScript Build Check** | Vite template had `verbatimModuleSyntax: true` causing TS1484 on type imports and TS6133 on unused variables. | Refactored imports to `import type { ... }`, removed unused identifiers, and fixed CSS syntax. Production build succeeded in 486ms. | Resolved |
| **Session Isolation & Context Retention** | Needed to verify that separate chat sessions maintain independent state and follow-ups retain context. | Implemented SQLAlchemy session cascading with message foreign keys; verified via automated test `test_session_creation_and_isolation` and follow-up HTTP requests. | Resolved |

---

## 3. Performance & Verification Metrics
- **Initial Corpus Ingestion**: 60 files / 6,479 chunks processed in 5.2 seconds.
- **Automated Test Suite**: 12 of 12 tests passed in 3.01 seconds.
- **Frontend Bundle Size**: Production build `16.13 kB` CSS, `327.33 kB` JS (gzipped: 104 kB).
- **Security Check**: Zero credentials or API keys stored in database rows or committed files.
