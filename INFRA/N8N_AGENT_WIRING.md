# THE NEPHILIM CHRONICLES — BOOKS 3–5
## n8n + Ollama + Nemotron Agent Wiring Architecture v2.1
*DESKTOP-SINGULA | Creative Swarm v2.1 | 13-Agent HAWK Topology*
*Supersedes: N8N_AGENT_WIRING_v2.0*

---

## ARCHITECTURE OVERVIEW

The v2.1 Creative Swarm uses a **HAWK 5-layer control hierarchy** with 13 agents
split between local Ollama/Nemotron GGUF (fast scene-level tasks) and NVIDIA NIM
Nemotron-3 Super (long-horizon cross-book synthesis). All inter-agent traffic routes
through n8n. Agent 9 adds content strategy, NZ grant monitoring, and YouTube anchor
content generation.

```
HAWK LAYER STACK
─────────────────────────────────────────────────────────────────
Layer 0  USER (Chris) — unrestricted authority, HITL gates
Layer 1  n8n WORKFLOW ORCHESTRATOR — webhook router, job scheduler
Layer 2  AGENT_0 (Conductor) — Nemotron, context arbiter, dispatches jobs
Layer 3  WORKER AGENTS 2–11 — Ollama or Nemotron per task profile
Layer 4  RESOURCES — Qdrant (4 tiers), Python services (8765–8772), llama-server (8780)
─────────────────────────────────────────────────────────────────
```

---

## 12-AGENT REGISTRY

| ID | Name | Model | Role |
|----|------|-------|------|
| AGENT_0 | Conductor | Nemotron-3 Super | Orchestrates all jobs, final authority below AUTHOR |
| AGENT_2 | Drift Manager | Nemotron-3 Super | Cross-book drift detection, canon semantic search |
| AGENT_3 | Constitution Updater | Nemotron-3 Super | SSOT / dossier updates via CRDT proposals |
| AGENT_4 | Reader Reaction Matrix | Ollama llama3.1 | Scene-level scoring matrix |
| AGENT_5 | Dopamine Ladder | Ollama llama3.1 | Hook/reward cycle mapping |
| AGENT_6 | Image Prompt Designer | Nemotron Router cascade | Visual direction briefs |
| AGENT_7 | KDP Formatter | Python (8766) | Manuscript assembly → .docx |
| AGENT_8 | Story Prototype Extractor | Nemotron-3 Super | Role/Plot graph extraction |
| AGENT_9 | Content Strategist / NZ Grant Monitor | Nemotron Router cascade | Social content, SEO, serialization, NZ grants |
| AGENT_10 | Cross-Book Auditor | Nemotron-3 Super | Nightly Books 3+4+5 continuity |
| AGENT_11 | SELF-REFINE Critic | Nemotron Router cascade | Scene draft scoring + critique |
| NEMOCLAW | Background Daemon | asyncio | File watcher, heartbeat, CRDT collector |

---

## SERVICES & PORTS

| Service | Port | Script | Purpose |
|---------|------|--------|---------|
| n8n workflow engine | 5678 | docker | Orchestration backbone |
| Qdrant vector store | 6333 | docker | 5 collections (see below) |
| Ollama LLM server | 11434 | ollama | Local GPU inference (llama3.1 + nomic-embed) |
| Canon Search API | 8765 | `canon_search_api.py` | Semantic SSOT search |
| KDP Format Server | 8766 | `kdp_format_server.py` | Manuscript → .docx assembly |
| Story Prototype API | 8767 | `update_story_prototype.py` | Role/Plot graph extraction |
| Nemotron Tool Router | 8768 | `nemotron_tool_router.py` | NIM → OpenRouter → Local GGUF → Ollama |
| Utility Server | 8769 | `utility_server.py` | Bookmarks, search utilities |
| Theological Guard | 8770 | `theological_guard_server.py` | 10-axiom theological validation |
| Swarm Conductor | 8771 | `conductor_server.py` | Master orchestrator (Agent 0) |
| Content Strategist | 8772 | `agent_9_content_strategist.py` | Social, SEO, serialization, NZ grants |
| Local Nemotron GGUF | 8780 | `llama-server` (llama.cpp) | CPU-only Nemotron 3 Super inference |

---

## QDRANT COLLECTIONS (5 total)

| Collection | Purpose | Key Payload Fields |
|------------|---------|-------------------|
| `nephilim_chronicles` | Legacy flat canon (Books 1–2) | category, entity_type, source_file |
| `tnc_episodes` | Episodic Memory — chapter summaries | book, chapter, excerpt, char_count |
| `tnc_personas` | Persona Memory — per-character state | character_id, last_seen_chapter |
| `tnc_role_graph` | Role Graph — entity-relation-entity triples | subject, predicate, object, locked |
| `tnc_plot_graph` | Plot Graph — causal event chains | cause, effect, book, planted |

Run `python adamem_initializer.py --seed-only` to initialise the tier collections
with 46 locked canon triples. Run `--migrate-only` to port legacy points.

---

## NEMOTRON ROUTING POLICY

All Agents 0, 2, 3, 8, 9, 10 send requests to **port 8768** (Nemotron Tool Router).
The router implements a 4-tier cascade:

```
1. PRIMARY:   NVIDIA NIM  https://integrate.api.nvidia.com/v1
              Model: nvidia/nemotron-3-8b-base-4k (or configured model)
              Context window: 1,000,000 tokens
              Token budget cap: 900,000 (10% headroom enforced by router)

2. FALLBACK1: OpenRouter  https://openrouter.ai/api/v1
              Model: nvidia/nemotron-4-340b-instruct

3. FALLBACK2: Local Nemotron 3 Super GGUF  http://localhost:8780/v1
              Model: nemotron-3-super (llama-server, CPU-only)
              Context: 131,072 tokens  |  Timeout: 600s

4. FALLBACK3: Ollama local  http://localhost:11434
              Model: llama3.1
              Context cap: ~128K tokens
```

Set `NVIDIA_API_KEY` and `OPENROUTER_API_KEY` in `.env` at project root.

---

## THE 13 n8n WORKFLOWS

---

### WORKFLOW 1 — SWARM DISPATCH (Master Router)
**Webhook:** `POST /webhook/swarm-dispatch`
**Trigger:** Any agent or author initiating a new job
**Purpose:** Classify job type, route to correct workflow

```
[Webhook] ← POST { "job_type": "analyse_chapter|draft_scene|audit|...",
                   "book": 3, "chapter": 7, "payload": {...} }
    ↓
[Switch Node] → job_type
  ├── "analyse_chapter"  → trigger Workflows 2, 5, 6, 7 in parallel
  ├── "extract_triples"  → POST http://localhost:8767/extract-triples
  ├── "drift_check"      → trigger Workflow 2
  ├── "constitution_update" → trigger Workflow 4 (CRDT)
  ├── "kdp_assemble"     → POST http://localhost:8766/kdp-format
  └── "nightly_audit"    → trigger Workflow 10
    ↓
[Merge results]
    ↓
[Log to LOGS/workflow_runs.jsonl]
```

---

### WORKFLOW 2 — DRIFT MANAGER (Agent 2 — Nemotron)
**Webhook:** `POST /webhook/analyse-chapter`  ← also receives from Nemoclaw file events
**Model:** Nemotron via port 8768
**Runtime:** ~60s

```
[Webhook] ← POST { "book": 3, "chapter": "CHAPTER_07.md", "fast_mode": false }
    ↓
[HTTP Request] → GET http://localhost:8765/search
  query: "locked canon timeline characters abilities"
  returns: top 20 relevant SSOT chunks
    ↓
[Read File] → MANUSCRIPT/book_3/CHAPTER_07.md
    ↓
[HTTP Request] → POST http://localhost:8768/route
  body: {
    "task_type": "drift_analysis",
    "system": "<DRIFT MANAGER SYSTEM PROMPT>",
    "prompt": "Canon context:\n{{ssot_chunks}}\n\nChapter:\n{{chapter_text}}"
  }
    ↓
[Code Node] → Parse drift findings (JSON)
    ↓
[IF Node] → critical_violations > 0?
  YES → [n8n Desktop Notify] "CRITICAL DRIFT in Book 3 Ch 7"
  BOTH → [Append File] → LOGS/DRIFT_LOG.md
```

**Drift Manager System Prompt:**
```
You are the Drift Manager for THE NEPHILIM CHRONICLES. Your jurisdiction spans Books 3–5.
Check the chapter strictly against the provided canon context.
Report violations as JSON: [{severity, category, passage, canon_ref, correction}]
Categories: CANON_CONTRADICTION, CHARACTER_STATE, TIMELINE_ERROR, ACOUSTIC_PARADIGM,
            THEOLOGY_DRIFT, CONTINUITY_GAP
```

---

### WORKFLOW 3 — STORY PROTOTYPE EXTRACTOR (Agent 8 — Nemotron)
**Webhook:** `POST /webhook/extract-story-prototype`
**Auto-triggered by:** Nemoclaw daemon on file change
**Model:** Nemotron via port 8767 → 8768

```
[Webhook or File Event from Nemoclaw]
  body: { "book": 3, "chapter_path": "MANUSCRIPT/book_3/CHAPTER_07.md" }
    ↓
[Read File] → Chapter text
    ↓
[HTTP Request] → POST http://localhost:8767/extract-triples
  body: { "chapter_text": "...", "book_num": 3, "chapter_num": 7 }
    ↓
Returns: { "role_triples": [...], "plot_events": [...],
           "contradictions": [...], "triples_saved": N }
    ↓
[IF Node] → contradictions.length > 0?
  YES → [n8n Notify] "Story Prototype: N contradictions in Book 3 Ch 7"
    ↓
[HTTP Request] → GET http://localhost:8767/foreshadow-brief?book=3&chapter=7
  Returns: unplanted effects needing setup
    ↓
[Write File] → 02_ANALYSIS/FORESHADOW_BRIEF_B3_CH07.md
```

---

### WORKFLOW 4 — CONSTITUTION UPDATER / CRDT MERGE (Agent 3 — Nemotron)
**Webhook:** `POST /webhook/constitution-update`
**Trigger:** Nemoclaw detecting pending CRDT proposals
**Model:** Python crdt_merge.py (no LLM needed for merge logic)

```
[Webhook] ← POST { "proposals_dir": "STAGING/crdt_proposals/", "count": N }
    ↓
[Execute Command Node] → python crdt_merge.py --staging-dir STAGING/crdt_proposals/ --verbose
    ↓
[Read File] → ARCHIVE/session_logs/CONSTITUTION_CHANGES.md (last merge log)
    ↓
[IF Node] → conflicts escalated to TODO.md?
  YES → [n8n Notify] "CRDT Conflict in SSOT — author review needed in TODO.md"
  NO →  [n8n Notify] "SSOT updated: N proposals merged"
    ↓
[Update n8n variable] → last_ssot_update timestamp
```

**To submit a CRDT proposal from any script:**
```python
from crdt_merge import write_proposal
write_proposal(
    agent_id="AGENT_3",
    section="§7.5",
    operation="APPEND",
    content="Cian discovers the Third Seal in Connemara...",
    justification="New plot event from Book 3 Ch 7 draft"
)
```

---

### WORKFLOW 5 — READER REACTION MATRIX (Agent 4 — Ollama)
**Webhook:** `POST /webhook/analyse-chapter`  ← runs in parallel with WF2, 6, 7
**Model:** Ollama llama3.1

```
[Webhook]
    ↓
[Read File] → Chapter
    ↓
[Code Node] → Split by scene breaks (✦ or --- markers)
    ↓
[Loop Over Scenes]
  [Ollama Chat Node]
    model: llama3.1
    system: [READER MATRIX PROMPT]
    user: "Score this scene: {{scene_text}}"
    ↓
[Aggregate]
    ↓
[Write File] → 02_ANALYSIS/REPORTS/matrix_B{{book}}_CH{{chapter}}.json
```

---

### WORKFLOW 6 — DOPAMINE LADDER (Agent 5 — Ollama)
**Webhook:** `POST /webhook/analyse-chapter`  ← runs in parallel
**Model:** Ollama llama3.1

```
[Webhook]
    ↓
[Ollama Chat Node]
  model: llama3.1
  system: [DOPAMINE LADDER PROMPT]
  user: "Map all hooks and reward cycles in: {{chapter_text}}"
    ↓
[Write File] → 02_ANALYSIS/REPORTS/dopamine_B{{book}}_CH{{chapter}}.json
```

---

### WORKFLOW 7 — IMAGE PROMPT DESIGNER (Agent 6 — Nemotron Router)
**Webhook:** `POST /webhook/analyse-chapter`  ← runs in parallel
**Model:** Nemotron Router cascade (was: Ollama mistral)

```
[Webhook]
    ↓
[Read File] → REFERENCE/VISUAL_DIRECTION.md
    ↓
[HTTP Request] → POST http://localhost:8768/route
  body: { "task_type": "image_prompt",
          "prompt": "Chapter text: {{chapter_text}}\nVisual guidelines: {{visual_bible}}",
          "max_tokens": 1024 }
    ↓
[Append File] → 03_IMAGE_PROMPTS/BOOK_{{book}}_PROMPTS.md
```

---

### WORKFLOW 8 — SELF-REFINE LOOP (Agent 11 — Nemotron Router)
**Webhook:** `POST /webhook/refine-scene`
**Model:** Nemotron Router cascade (scorer) + llama3.1 (revisor) + Nemotron (revisor if available)

```
[Webhook] ← POST { "draft_path": "MANUSCRIPT/book_3/CHAPTER_07.md",
                    "book": 3, "chapter": 7,
                    "author_notes": "...", "max_iter": 3, "threshold": 85 }
    ↓
[Execute Command Node] → python self_refine_loop.py
    --input {{draft_path}} --book {{book}} --chapter {{chapter}}
    --max-iter {{max_iter}} --threshold {{threshold}}
    --output MANUSCRIPT/book_3/CHAPTER_07_refined.md
    ↓
[Read File] → *.refine_report.json
    ↓
[IF Node] → passed == true?
  YES → [n8n Notify] "Refinement PASS — score {{final_score}}/100"
  NO  → [n8n Notify] "BEST-EFFORT — score {{final_score}} — author review advised"
    ↓
[Append File] → LOGS/refine_history.jsonl
```

**SELF-REFINE Rubric (11 criteria, total 100 points):**

| Criterion | Weight |
|-----------|--------|
| Canon Fidelity | 25 |
| Theological Consistency | 15 |
| Character Voice Accuracy | 12 |
| Acoustic Paradigm Adherence | 10 |
| Timeline Consistency | 8 |
| Plot Coherence | 8 |
| Prose Quality | 8 |
| Emotional Resonance | 5 |
| Pacing & Structure | 5 |
| Foreshadowing Integration | 2 |
| Originality | 2 |

---

### WORKFLOW 9 — KDP ASSEMBLER (Agent 7 — Python)
**Webhook:** `POST /webhook/kdp-assemble`

```
[Webhook] ← POST { "book": 3 }
    ↓
[HTTP Request] → POST http://localhost:8766/kdp-format
  body: { "book_num": 3 }
    ↓
Returns: { "output_path": "...", "chapter_count": N, "word_count": N }
    ↓
[n8n Notify] → "Book {{book}} .docx assembled: {{word_count}} words"
```

---

### WORKFLOW 10 — NIGHTLY CROSS-BOOK AUDIT (Agent 10 — Nemotron)
**Cron Trigger:** Daily at 02:00 AM
**Webhook:** `POST /webhook/nightly-continuity-prep`  ← Nemoclaw pre-loads at 01:45

```
[Cron Trigger: 02:00]  OR  [Webhook from Nemoclaw at 01:45]
    ↓
[Execute Command Node] → python cross_book_audit.py --books 3,4,5
    ↓
[Read File] → 02_ANALYSIS/NIGHTLY_AUDIT_{{today}}.md
    ↓
[Code Node] → Parse critical_violations count
    ↓
[IF Node] → critical_violations > 0?
  YES → [n8n Notify — HIGH PRIORITY] "CRITICAL: N violations — review audit"
  NO  → [n8n Notify] "Nightly audit clean: {{violation_count}} minor"
    ↓
[Append File] → LOGS/AUDIT_SUMMARY.log
```

---

### WORKFLOW 11 — SOCIAL CONTENT GENERATOR (Agent 9 — Nemotron Router)
**Webhook:** `POST /webhook/social-content`
**Model:** Nemotron Router cascade via Agent 9 microservice

```
[Webhook] ← POST { "book_title": "...", "chapter_title": "...",
                    "hook_line": "...", "platforms": ["tiktok","linkedin","twitter","youtube_community"] }
    ↓
[HTTP Request] → POST http://localhost:8772/generate-social
  body: { full payload from webhook }
    ↓
Returns: { "tiktok": {...}, "linkedin": {...}, "twitter": {...}, "youtube_community": {...} }
    ↓
[Log to LOGS/workflow_runs.jsonl]
    ↓
[Respond to Webhook]
```

---

### WORKFLOW 12 — SEO & SERIALIZATION (Agent 9 — Nemotron Router)
**Webhook:** `POST /webhook/seo-serialization`
**Model:** Nemotron Router cascade via Agent 9 microservice

```
[Webhook] ← POST { "book_title": "...", "series_name": "...",
                    "genre": "...", "synopsis": "..." }
    ↓
┌─── [HTTP Request] → POST http://localhost:8772/seo-metadata
│      Returns: { keywords, bisac_categories, ab_titles, html_description }
│
├─── [HTTP Request] → POST http://localhost:8772/serialization-schedule
│      Returns: { serialization plan with DTC exclusivity windows }
    ↓
[Merge Results Node] → Combines SEO + Schedule payloads
    ↓
[Respond to Webhook]
```

---

### WORKFLOW 13 — NZ GRANT MONITOR (Agent 9 — Schedule + Manual)
**Schedule:** Daily at 08:00 AM NZST
**Manual Webhook:** `POST /webhook/nz-grant-scan`
**Model:** Nemotron Router cascade (LLM-powered extraction from source HTML/RSS)

```
[Schedule Trigger: 08:00 daily]  OR  [Webhook: POST /webhook/nz-grant-scan]
    ↓
[HTTP Request] → POST http://localhost:8772/scrape-nz-grants
  body: {}
    ↓
Returns: { "grants_found": N, "hitl_flags": M, "results": [...] }
    ↓
[IF Node] → grants_found > 0?
  YES → [Log Grant Results to LOGS/workflow_runs.jsonl]
  NO  → [No-Op]
```

NZ grant sources scraped:
- **NZSA** — New Zealand Society of Authors grants/awards
- **Mātātuhi Foundation** — Māori literary grants
- **Creative NZ** — Arts Council of New Zealand funding

Results appended to `LOGS/OPPORTUNITIES_LOG.md`. Sources that fail direct scrape
fall back to RSS, then flag for HITL (human-in-the-loop) review.

---

## NEMOCLAW DAEMON INTEGRATION

The Nemoclaw daemon (`nemoclaw_daemon.py`) runs outside n8n as a persistent
background process. It calls n8n webhooks reactively and on schedule.

```
NEMOCLAW DAEMON (always running on DESKTOP-SINGULA)
├── Every 60s:   Scan MANUSCRIPT/book_3,4,5/ for file changes
│     → On change: POST /webhook/nemoclaw-file-event
│                  Auto-vectorize to tnc_episodes (Ollama embed + Qdrant upsert)
│                  POST /webhook/extract-story-prototype (Agent 8)
├── Every 5min:  POST /webhook/constitution-update if CRDT proposals pending
├── Every 5min:  GET  all 7 services /health → log to LOGS/DAEMON_HEALTH.log
├── Every 30min: POST /webhook/analyse-chapter (drift fast-mode) if recent chapter
├── At 01:45:    POST /webhook/nightly-continuity-prep
└── On SIGTERM:  Graceful shutdown + in-flight task completion
```

**Start:**
```powershell
python nemoclaw_daemon.py --log-level INFO
```

---

## CRDT PROPOSAL FLOW (End-to-End)

```
Any Agent or script
    │  from crdt_merge import write_proposal
    │  write_proposal(agent_id, section, operation, content, justification)
    ↓
STAGING/crdt_proposals/proposal_AGENT_X_<timestamp>.json
    ↓
Nemoclaw (5min scan) → POST /webhook/constitution-update
    ↓
n8n Workflow 4 → python crdt_merge.py
    ↓
crdt_merge.py pipeline:
  1. Load all proposals from staging dir
  2. validate_proposal() — deontic + locked section check
  3. classify_conflicts() → safe / additive / conflict / deprecate
  4. CONFLICT → escalate_to_author() → TODO.md + n8n notify
  5. SAFE/ADDITIVE → atomic_write() to Canon/SSOT_v3_MASTER.md
     (temp → validate word+heading counts → rename → archive old version)
  6. Log to ARCHIVE/session_logs/CONSTITUTION_CHANGES.md
```

---

## GOVERNANCE INTEGRATION

```powershell
# Test deontic permissions
python governance.py --check-permission AGENT_2 MODIFY   # → DENIED
python governance.py --check-permission AGENT_3 MODIFY   # → PERMITTED
python governance.py --check-permission AGENT_0 DEPRECATE # → PERMITTED

# PIMMUR compliance check on a prompt file
python governance.py --check-prompt MANUSCRIPT/book_3/CHAPTER_07.md

# View audit log
python governance.py --show-audit --last 30
python governance.py --show-audit --agent AGENT_3
```

**Log files:**
- `LOGS/agent_audit.jsonl` — append-only tool invocation audit trail
- `LOGS/pimmur_checks.jsonl` — PIMMUR compliance scan results
- `TODO.md` — HITL escalations written here automatically

**Deontic Permission Table:**

| Agent | APPEND | MODIFY | DEPRECATE | DELETE |
|-------|--------|--------|-----------|--------|
| AGENT_0 (Conductor) | ✓ | ✓ | ✓ | ✗ |
| AGENT_2 (Drift Manager) | ✓ | ✗ | ✗ | ✗ |
| AGENT_3 (Constitution Updater) | ✓ | ✓ | ✓ | ✗ |
| AGENT_8–11 (Workers) | ✓ | ✗ | ✗ | ✗ |
| AUTHOR | ✓ | ✓ | ✓ | ✓ |

**Locked SSOT sections (no agent may modify — ever):**
`§1, §2, §3, §4.2, §5, §9.1`

---

## COMPLETE WEBHOOK REFERENCE

| Webhook URL | Triggered by | Fires |
|-------------|-------------|-------|
| `POST /webhook/swarm-dispatch` | Any agent or author | Master router |
| `POST /webhook/analyse-chapter` | Author, Nemoclaw | WF2+5+6+7 in parallel |
| `POST /webhook/nemoclaw-file-event` | Nemoclaw daemon | File ingestion |
| `POST /webhook/extract-story-prototype` | Nemoclaw, author | WF3 Role/Plot graph |
| `POST /webhook/constitution-update` | Nemoclaw, author | WF4 CRDT merge |
| `POST /webhook/refine-scene` | Author | WF8 SELF-REFINE |
| `POST /webhook/kdp-assemble` | Author | WF9 KDP build |
| `POST /webhook/nightly-continuity-prep` | Cron 02:00, Nemoclaw 01:45 | WF10 audit |
| `POST /webhook/social-content` | Author, Conductor | WF11 social content |
| `POST /webhook/seo-serialization` | Author, Conductor | WF12 SEO + serialization |
| `POST /webhook/nz-grant-scan` | Author, Schedule 08:00 | WF13 NZ grant monitor |

---

## STARTUP SEQUENCE (Full v2.0 Stack)

```powershell
# 1. Start infrastructure (if not already running)
docker compose --profile gpu-nvidia up -d

# 2. Start Python services
Start-Job { python F:\...\canon_search_api.py }         # port 8765
Start-Job { python F:\...\kdp_format_server.py }        # port 8766
Start-Job { python F:\...\update_story_prototype.py }   # port 8767
Start-Job { python F:\...\nemotron_tool_router.py }     # port 8768
Start-Job { python F:\...\nemoclaw_daemon.py }          # background warden

# 3. Verify all services
Invoke-WebRequest http://localhost:8768/health | ConvertFrom-Json

# 4. Initialise AdaMem (first time only)
python adamem_initializer.py --seed-only --verbose
```

---

## WHAT CHANGED FROM v1.0

| v1.0 | v2.1 |
|------|------|
| 7 agents (Cowork frame) | 13 agents (HAWK topology) |
| All Ollama (mistral/llama3.1) | Nemotron-3 Super for Agents 0,2,3,8,10 + local GGUF cascade |
| Flat `nephilim_chronicles` collection | 4 AdaMem tier collections + legacy |
| No Story Prototype | Role Graph + Plot Graph dual-knowledge system |
| Manual CRDT / no merge safety | Full CRDT staging + atomic write + conflict escalation |
| No background warden | Nemoclaw daemon (24/7 file watch + health checks) |
| No scene refinement | SELF-REFINE loop (11-criterion weighted rubric) |
| No governance layer | Audit log + deontic permissions + PIMMUR compliance |
| No content strategy | Agent 9: TikTok/LinkedIn/YouTube + NZ grant monitor |
| 6 n8n workflows | 13 n8n workflows |
| Ports 8765–8766 | Ports 8765–8772, 8780 (llama-server) |

---

*Architecture Version 2.1 — DESKTOP-SINGULA | The Nephilim Chronicles Books 3–5*
*13-Agent HAWK Topology | AdaMem 4-Tier | Story Prototype | CRDT | SELF-REFINE | Governance | Content Strategy*
