# THE NEPHILIM CHRONICLES

## Creative Swarm — Architecture Upgrade Specification v2.0

**Target:** Books 3–5 (The Edenic Mandate, The Testimony, The Glory)
**Prepared for:** Kerman Gild Publishing | Chris Modina
**Date:** April 8, 2026
**Status:** PRODUCTION BLUEPRINT — Ready for implementation

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [HAWK Framework — 5-Layer Topology](#2-hawk-framework--5-layer-topology)
3. [Swarm Topology v2.0 — Full Agent Registry](#3-swarm-topology-v20--full-agent-registry)
4. [Model Routing: Nemotron 3 Super vs Ollama RTX 3080](#4-model-routing-nemotron-3-super-vs-ollama-rtx-3080)
5. [Nemoclaw Daemon — 24/7 Background Engine](#5-nemoclaw-daemon--247-background-engine)
6. [Cognitive Memory Architecture (AdaMem)](#6-cognitive-memory-architecture-adamem)
7. [Story Prototype — Dual-Knowledge Graph](#7-story-prototype--dual-knowledge-graph)
8. [CRDT Canon Management](#8-crdt-canon-management)
9. [Execution Plan — OpenCode &amp; Kilo Code CLI](#9-execution-plan--opencode--kilo-code-cli)
10. [Quality Evaluation — SELF-REFINE Loops](#10-quality-evaluation--self-refine-loops)
11. [Infrastructure Changes](#11-infrastructure-changes)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. EXECUTIVE SUMMARY

The Book 2 swarm was a **pipeline**: seven sequential agents on a flat topology, each
consuming and producing files. It served its purpose. For Books 3–5 it is insufficient.

Books 3–5 demand something fundamentally different:

- **Three books must remain internally consistent** with each other *and* with the
  locked canon of Books 1–2. Drift is no longer a per-chapter problem; it is a
  cross-book, multi-year problem.
- **Azazel's arc alone** involves interactions with Enoch, Elijah, Cian, the Naamah/Whore
  thread, the Four Horsemen, the Witnesses' 1,260-day ministry, and the Seal sequence —
  all of which must be causally coherent.
- **The theology has to hold** at each of the 12+ key doctrinal pivot points across the
  finale trilogy.

This document specifies the upgrade from a 7-agent pipeline to a **12-agent Hybrid
Bottom-Up Narrative Community** organized under the HAWK framework, with:

- **Nemotron 3 Super (120B)** as the long-horizon reasoning spine
- **OpenClaw/Nemoclaw** as the persistent background daemon
- **CreAgentive's Story Prototype** (Role Graph + Plot Graph) stored in Qdrant
- **AdaMem** four-tier memory decomposed from the flat Qdrant collection
- **CRDTs** for conflict-free constitutional merges across async agent outputs
- **SELF-REFINE loops** as quality gates on every scored output

---

## 2. HAWK FRAMEWORK — 5-Layer Topology

HAWK (Hierarchical Agent Workflow) decouples the system into five concentric layers.
Every component in the swarm maps to exactly one layer.

```
╔══════════════════════════════════════════════════════════════════╗
║  LAYER 0 — USER                                                  ║
║  Chris (author): writes prose, approves beats, locks canon       ║
║  Interface: Claude.ai (Agent 1), n8n dashboard, VS Code          ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 1 — WORKFLOW (n8n Orchestration)                          ║
║  n8n :5678 — routes tasks, fires triggers, chains agents         ║
║  Master Webhook: /webhook/swarm-dispatch                         ║
║  Schedules: Nemoclaw heartbeat (1 min), nightly audit (02:00)    ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 2 — OPERATOR (Master Orchestrator Agent)                  ║
║  Agent 0: SWARM CONDUCTOR — Nemotron 3 Super                     ║
║  Decomposes user intent → task graph → dispatches to Layer 3     ║
║  Manages inter-agent dependencies, evaluates completion          ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 3 — AGENT (Specialized Workers)                           ║
║  Agents 1–12 — each owns a single cognitive domain               ║
║  Communicate via n8n message bus + Qdrant shared memory          ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 4 — RESOURCE                                              ║
║  Qdrant :6333 | Ollama :11434 | Nemotron API (OpenRouter/NIM)    ║
║  canon_search_api.py :8765 | kdp_format_server.py :8766          ║
║  PostgreSQL :5432 | Local filesystem: /data/TNC_Books35/          ║
╚══════════════════════════════════════════════════════════════════╝
```

> **Design principle:** Agents in Layer 3 NEVER call each other directly. All
> inter-agent communication passes through Layer 2 (the Conductor) or Layer 1
> (the n8n message bus). This eliminates deadlock and enforces auditability.

---

## 3. SWARM TOPOLOGY v2.0 — FULL AGENT REGISTRY

### Retained & Upgraded from v1.0

| # | Agent Name                        | Role                                              | Model                            | Trigger                  |
| - | --------------------------------- | ------------------------------------------------- | -------------------------------- | ------------------------ |
| 1 | **Content Creator**         | Prose, outlines, interviews, scene drafts         | Claude Sonnet 4.6 (this session) | Manual                   |
| 2 | **Drift Manager v2**        | Canon drift detection with cross-book scope       | **Nemotron 3 Super**       | File save                |
| 3 | **Constitution Updater v2** | CRDT-merged SSOT updates with conflict resolution | **Nemotron 3 Super**       | Session note saved       |
| 4 | **Reader Reaction Matrix**  | Per-scene 8-criterion scoring + SELF-REFINE loop  | llama3.1 (Ollama)                | Manual/auto after draft  |
| 5 | **Dopamine Ladder**         | Hook density + tension arc mapping                | llama3.1 (Ollama)                | Auto alongside Agent 4   |
| 6 | **Image Prompt Designer**   | Visual direction prompts for KDP art              | Nemotron Router cascade          | Manual                   |
| 7 | **KDP Formatter**           | Assembles `.docx` from markdown                 | Deterministic (no LLM)           | Manual ("book complete") |

### New Agents (v2.0 Additions)

| #  | Agent Name                        | Role                                                         | Model                      | Trigger                      |
| -- | --------------------------------- | ------------------------------------------------------------ | -------------------------- | ---------------------------- |
| 0  | **Swarm Conductor**         | Master orchestrator; decomposes tasks, routes, audits        | **Nemotron 3 Super** | All swarm dispatches         |
| 8  | **Story Prototype Manager** | Maintains Role Graph + Plot Graph in Qdrant                  | **Nemotron 3 Super** | Chapter saved; session end   |
| 9  | **Content Strategist / NZ Grant Monitor** | Social content, SEO, serialization, NZ grants | **Nemotron Router cascade** | Manual / scheduled (daily) |
| 10 | **Cross-Book Continuity**   | Audits Books 3+4+5 draft coherence as a set                  | **Nemotron 3 Super** | Nightly (02:00)              |
| 11 | **Self-Refine Scorer**      | Meta-evaluates Agents 4+5 outputs; requests revisions        | Nemotron Router cascade    | After Agents 4+5 complete    |
| 12 | **Nemoclaw Daemon**         | Persistent 24/7 daemon: background vectorization, graph sync | Nemoclaw (OpenClaw)        | Continuous heartbeat (1 min) |
| 13 | **Marketing Agent v2.1**    | 24/6 autonomous content generation, multi-platform posting (API + clipboard), campaign planning, SEO tracking, web scraping | llama3.1 (Ollama) + Qdrant | Scheduler (15-min cycles, Sabbath rest) |

### Agent Dependency Graph

```
      [User: Chris]
           │
           ▼
    [Agent 0: Conductor]      ← LAYER 2 GATEWAY
    /   |   |   |   |   \
   ▼    ▼   ▼   ▼   ▼    ▼
  [1]  [2] [3] [8] [9] [10]   ← PRIMARY LAYER 3 AGENTS
   │              │
   ▼              ▼
  [4 + 5]        [12]          ← ANALYSIS + DAEMON
      │
      ▼
     [11]                      ← SELF-REFINE gate
      │
      ▼
  [6] [7]                      ← PRODUCTION OUTPUT

     [13]                      ← AUTONOMOUS (24/6 scheduler, Sabbath rest)
```

---

## 4. MODEL ROUTING: NEMOTRON 3 SUPER vs OLLAMA RTX 3080

### Routing Decision Matrix

```
TASK TYPE                                          → MODEL
─────────────────────────────────────────────────────────────────────
Long-horizon multi-step reasoning                  → Nemotron 3 Super
Tool calls requiring >3-step chains                → Nemotron 3 Super
Cross-book continuity audit (3 books at once)      → Nemotron 3 Super
CRDT semantic merge (conflicting SSOT updates)     → Nemotron 3 Super
Theological validation against long doctrinal doc  → Nemotron 3 Super
Story Prototype semantic triple extraction         → Nemotron 3 Super
Orchestration / task decomposition                 → Nemotron 3 Super
─────────────────────────────────────────────────────────────────────
Scene-level scoring (1,200–3,000 tokens)           → Ollama (llama3.1)
Dopamine hook pattern matching                     → Ollama (llama3.1)
Image prompt generation (short context)            → Nemotron Router cascade
Self-refine scoring (short evaluation chain)       → Nemotron Router cascade
Deterministic file assembly                        → Python (no LLM)
─────────────────────────────────────────────────────────────────────
```

### Why Nemotron 3 Super for the Heavy Lifters

Nemotron 3 Super (120B) is a hybrid **Mamba-Transformer MoE** with:

- **1 million-token native context window** — can hold all three Books 3–5 drafts
  + the full SSOT_v3_MASTER.md (39KB) + all character dossiers simultaneously with
    zero chunking artifacts.
- **Multi-Token Prediction (MTP)** — dramatically reduces hallucination drift on
  long-horizon tasks (cross-book continuity audits).
- **Best-in-class tool-call reliability** — essential for the CRDT Constitution Updater
  where a malformed merge call corrupts canon.

### n8n Nemotron Router Node

In n8n, Nemotron is accessed via an HTTP Request node to **port 8768** (Nemotron Tool Router),
which implements a 4-tier cascade:

1. **NVIDIA NIM API** (primary): `https://integrate.api.nvidia.com/v1`
2. **OpenRouter API** (fallback 1): `https://openrouter.ai/api/v1/chat/completions`
   Model string: `nvidia/nemotron-4-340b-instruct`
3. **Local Nemotron 3 Super GGUF** (fallback 2): `http://localhost:8780/v1/chat/completions`
   Served via llama-server (llama.cpp), CPU-only, zero-cost inference
4. **Ollama llama3.1** (fallback 3): `http://localhost:11434/api/chat`

The router (`nemotron_tool_router.py`) handles:

1. Context budget calculation (how much to load into the 1M window)
2. Automatic tool schema injection for CRDT/graph operations
3. Retry logic with exponential backoff
4. Response validation before downstream write

---

## 5. NEMOCLAW DAEMON — 24/7 BACKGROUND ENGINE

### What Nemoclaw Is

OpenClaw (Nemoclaw) is a **daemon-based autonomous agent** running a persistent
heartbeat loop. Unlike n8n workflows (triggered by events), Nemoclaw runs
**continuously** — checking system state every N seconds, deciding whether to act.

This is the missing piece in the v1.0 swarm: there was no background warden.

### Nemoclaw Task Registry for Books 3–5

| Task                              | Interval         | Description                                                                            |
| --------------------------------- | ---------------- | -------------------------------------------------------------------------------------- |
| **Draft Watcher**           | 60s              | Scans `/data/TNC_Books35/MANUSCRIPT/` for new/changed `.md` files                  |
| **Auto-Vectorizer**         | On file change   | Embeds new chapter text → upserts to Qdrant `tnc_episodes` collection               |
| **Story Prototype Sync**    | On file change   | Queues chapter for semantic triple extraction (Agent 8)                                |
| **Heartbeat Health Check**  | 5 min            | Pings all services (n8n, Qdrant, Ollama, Postgres); logs to `DAEMON_HEALTH.log`      |
| **Nightly Continuity Prep** | 01:45            | Pre-loads Books 3+4+5 chapters into Nemotron context for 02:00 audit                   |
| **Persona Arc Tracker**     | Per chapter save | Extracts character state deltas → updates AdaMem Persona tier                         |
| **CRDT Staging Collector**  | 5 min            | Scans staging area for agent update proposals; triggers merge when ≥2 proposals exist |
| **Drift Alert Monitor**     | 30 min           | Lightweight drift scan (fast Ollama pass) across latest chapter draft                  |

### Nemoclaw Configuration Contract

```python
# nemoclaw_daemon.py — heartbeat loop contract
SERVICES = {
    "n8n":    "http://localhost:5678/healthz",
    "qdrant": "http://localhost:6333/healthz",
    "ollama": "http://localhost:11434/api/tags",
    "canon":  "http://localhost:8765/health",
    "kdp":    "http://localhost:8766/health",
}

WATCH_PATH = "/data/TNC_Books35/MANUSCRIPT/"
STAGING_PATH = "/data/TNC_Books35/STAGING/crdt_proposals/"
DAEMON_LOG = "/data/TNC_Books35/LOGS/DAEMON_HEALTH.log"

HEARTBEAT_INTERVALS = {
    "health_check":       300,   # 5 minutes
    "file_watch":          60,   # 1 minute
    "drift_alert":       1800,   # 30 minutes
    "crdt_collect":       300,   # 5 minutes
    "nightly_prep":    "01:45",  # cron-style
}
```

### Nemoclaw Integration with n8n

Nemoclaw does not replace n8n — it **feeds** n8n:

```
Nemoclaw detects new chapter file
    → POSTs to http://localhost:5678/webhook/nemoclaw-file-event
    → n8n reads the event, dispatches to Agents 2 + 8 simultaneously
    → Nemoclaw logs the dispatch and awaits completion webhook
    → On completion, Nemoclaw updates DAEMON_HEALTH.log
```

---

## 6. COGNITIVE MEMORY ARCHITECTURE (AdaMem)

### Current State (v1.0 — Flat)

The v1.0 Qdrant setup has a **single collection** `nephilim_chronicles` with ~52,000
points. All agents query the same pool. There is no distinction between what is
*currently active*, what is *historical summary*, who a character *is*, or how
entities *relate*.

### AdaMem Four-Tier Decomposition

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: WORKING MEMORY                                          │
│ Location: Agent 0 (Conductor) in-context window (Nemotron 1M)  │
│ Contents: Current chapter + immediate session context           │
│ TTL: Session duration only                                      │
│ Size: Up to 800K tokens (leaving 200K for generation)           │
│ Access: Agents 0, 1, 2, 9 (direct context injection)           │
├─────────────────────────────────────────────────────────────────┤
│ TIER 2: EPISODIC MEMORY                                         │
│ Qdrant Collection: tnc_episodes                                 │
│ Schema: { book, chapter, scene_id, summary, token_count,        │
│           themes[], characters[], timestamp, canon_status }     │
│ Contents: Compressed chapter summaries (300–500 words each)     │
│ Populated by: Nemoclaw after each chapter save                  │
│ Queried by: Agents 2, 8, 10 (cross-book continuity)            │
├─────────────────────────────────────────────────────────────────┤
│ TIER 3: PERSONA MEMORY                                          │
│ Qdrant Collection: tnc_personas                                 │
│ Schema: { character_id, name, arc_stage, last_seen_chapter,     │
│           voice_samples[], relationships{}, active_wounds[],    │
│           theological_role, status: alive|dead|translated }     │
│ Contents: Character state derived from manuscript + dossiers    │
│ Populated by: Nemoclaw (arc extractor) + Constitution Updater   │
│ Queried by: Agents 1, 2, 9 (voice + theology consistency)      │
├─────────────────────────────────────────────────────────────────┤
│ TIER 4: GRAPH MEMORY (Story Prototype)                          │
│ Qdrant Collections: tnc_role_graph + tnc_plot_graph             │
│ Contents: Semantic triples — see Section 7                      │
│ Populated by: Agent 8 (Story Prototype Manager)                 │
│ Queried by: Agents 0, 2, 8, 9, 10                              │
└─────────────────────────────────────────────────────────────────┘
```

### Migration Plan: v1.0 → AdaMem

The existing `nephilim_chronicles` collection is **not deleted** — it becomes the seed
corpus. The `adamem_initializer.py` script (see Section 9) categorizes each point
by its metadata and migrates them to the appropriate tier collection.

```
nephilim_chronicles (52K points)
    ├─ payload.category == "chapter_summary"  → tnc_episodes
    ├─ payload.category == "character_dossier" → tnc_personas
    ├─ payload.category == "canon_fact"        → tnc_role_graph
    ├─ payload.category == "plot_event"        → tnc_plot_graph
    └─ payload.category == "raw_text"          → kept in canonical (full-text recall)
```

---

## 7. STORY PROTOTYPE — DUAL-KNOWLEDGE GRAPH

### Conceptual Foundation

The Story Prototype decouples **what happened** (narrative logic) from **how it
sounds** (prose style). This is the difference between:

- *"Azazel is released from Dudael by the False Prophet's ritual in Antarctica"* — a
  **graph triple** (narrative logic, stored in Plot Graph)
- *"The chains dissolved like memory. What emerged was not a man."* — **prose style**
  (generated by Agent 1, informed by the graph)

Claude (Agent 1) generates prose. The Story Prototype ensures the prose is
**causally coherent** across all three books before the sentence is ever written.

### Role Graph — Schema

Stored in Qdrant collection `tnc_role_graph`.
Each point = one semantic triple: **(Subject, Predicate, Object)**

```json
{
  "id": "uuid",
  "vector": [<embedding of "Subject Predicate Object" string>],
  "payload": {
    "subject":    "CIAN_MAC_MORNA",
    "predicate":  "IS_WIELDER_OF",
    "object":     "MO_CHRA",
    "confidence": "LOCKED",
    "source":     "CANON/SERIES_BIBLE.md",
    "book_scope": ["1", "2", "3", "4", "5"],
    "added_by":   "Agent_8",
    "timestamp":  "2026-04-08T00:00:00Z"
  }
}
```

**Confidence tiers:**

| Value         | Meaning                                      |
| ------------- | -------------------------------------------- |
| `LOCKED`    | Published canon — never overwrite           |
| `CONFIRMED` | Approved by author in session                |
| `PROPOSED`  | Agent suggestion — requires author decision |
| `INFERRED`  | Derived from context — flag for review      |

### Role Graph Seed Triples (Books 3–5 Critical)

```
(CIAN, GUARDIAN_OF, ENOCH)
(CIAN, GUARDIAN_OF, ELIJAH)
(RAPHAEL, CANNOT_KILL, FALLEN_WATCHERS)
(RAPHAEL, ALIAS_IS, LIAIGH)     ← confidence: LOCKED, reveal_book: 5
(AZAZEL, IMPRISONED_IN, DUDAEL)
(AZAZEL, IS, NEPHILIM)          ← NOT a Watcher — LOCKED
(AZAZEL, IS_SON_OF, GADREEL)
(OHYA, IS_VESSEL_OF, THE_BEAST)
(OHYA, IS_SON_OF, SHEMYAZA)
(NAAMAH, IS, WHORE_OF_BABYLON)
(NAAMAH, SURVIVED_FLOOD_AS, SIREN)
(ENOCH, MADE, MO_CHRA)
(ELIJAH, IS, SECOND_WITNESS)
(ENOCH, IS, FIRST_WITNESS)
(MO_CHRA, INTERFACES_WITH, EMPYREAL_REGISTER)
(SHEMYAZA, DOES_NOT_KNOW, NAAMAH_HOLDS_TRUE_NAME)
```

### Plot Graph — Schema

Stored in Qdrant collection `tnc_plot_graph`.
Each point = one causal event triple: **(Cause, Effect, Timing)**

```json
{
  "id": "uuid",
  "vector": [<embedding of event description>],
  "payload": {
    "event_id":     "B3_EVT_007",
    "description":  "Azazel released from Dudael via Antarctic ritual",
    "causes":       ["B3_EVT_003_EXPEDITION_ARRIVES", "B3_EVT_005_RITUAL_COMPLETED"],
    "effects":      ["B3_EVT_009_SECOND_SEAL_BREAKS", "B3_EVT_011_WAR_RIDER"],
    "book":         "3",
    "chapter_est":  "4-6",
    "status":       "PLANNED",
    "lock_status":  "AUTHOR_APPROVED"
  }
}
```

### Story Prototype — Foreshadowing Engine

The dual graph enables **automated foreshadowing consistency checks**:

Before Agent 1 writes Chapter 4 of Book 3, Agent 8 queries:

1. *"What effects does `B3_EVT_007` have that are not yet visible in chapters 1–3?"*
2. Returns: Second Seal Break, War Rider → Agent 1 is informed to seed the atmosphere
3. Agent 9 (Theological Guard) validates the Seal sequence against Revelation 6

This is how foreshadowing moves from the author's mental model into a **queryable,
machine-verifiable system**.

### update_story_prototype.py — Interface Contract

```python
# update_story_prototype.py
# Called by Nemoclaw on chapter save; also callable manually

def extract_role_triples(chapter_text: str, model="nemotron") -> list[Triple]:
    """Ask Nemotron to extract all entity-relation-entity pairs from chapter."""

def extract_plot_events(chapter_text: str, existing_graph: list) -> list[Event]:
    """Extract causal events, linking to existing plot nodes."""

def upsert_to_qdrant(triples: list, collection: str) -> UpsertResult:
    """Embed + upsert to tnc_role_graph or tnc_plot_graph."""

def check_contradictions(new_triples: list) -> list[Contradiction]:
    """Compare new triples against LOCKED canon — return contradictions."""

def generate_foreshadow_brief(chapter_num: int, book: int) -> str:
    """Return narrative seeds that should be present given the plot graph state."""
```

---

## 8. CRDT CANON MANAGEMENT

### The Problem with v1.0

The v1.0 Constitution Updater **file-locked and overwrote** SSOT_v3_MASTER.md.
With multiple async agents now capable of proposing canon updates simultaneously
(Agents 2, 3, 8, 9, 10 can all flag new canon), a naive write strategy will corrupt
the document.

### CRDT-Inspired Merge Strategy

We adapt **CRDT (Conflict-Free Replicated Data Type)** principles to markdown
canon documents. Specifically, we use a **G-Set** (grow-only set) for facts and an
**LWW-Element-Set** (last-write-wins with semantic conflict resolution) for mutable
character states.

```
Step 1: STAGING
    Each agent writes its proposed update to:
    /data/TNC_Books35/STAGING/crdt_proposals/proposal_<agent>_<timestamp>.json

    Schema:
    {
      "agent_id": "AGENT_8",
      "section": "§7.3 — Azazel's Release",
      "operation": "APPEND",        // or MODIFY, DEPRECATE
      "proposed_text": "...",
      "confidence": "CONFIRMED",
      "conflicts_with": [],         // auto-populated by Agent 8
      "timestamp": "ISO8601"
    }

Step 2: COLLECTION (Nemoclaw — every 5 min)
    Nemoclaw scans STAGING directory.
    If ≥1 proposal pending, fires n8n webhook → triggers Agent 3 (Constitution Updater v2)

Step 3: SEMANTIC MERGE (Nemotron 3 Super — Agent 3)
    Load all pending proposals into Nemotron 1M context alongside full SSOT.
  
    Resolution rules:
    ┌──────────────────────────────────────────────────────────┐
    │ RULE 1: No proposal may contradict LOCKED canon.         │
    │         → Reject + log to DRIFT_LOG.md                  │
    │ RULE 2: Two APPEND operations to same section are safe.  │
    │         → Merge both (G-Set semantics)                   │
    │ RULE 3: Two MODIFY operations to same section conflict.  │
    │         → Ask Author (flag in TODO.md) if semantic diff  │
    │           > threshold; else LWW by timestamp             │
    │ RULE 4: A DEPRECATE operation is final if zero agents    │
    │         flagged the deprecated section as LOCKED.        │
    └──────────────────────────────────────────────────────────┘

Step 4: ATOMIC COMMIT
    Nemotron produces the merged SSOT update as a complete section replacement.
    Agent 3 writes atomically using write-to-temp, validate, rename strategy:
  
    1. Write merged section to SSOT_v3_MASTER.md.tmp
    2. Validate: check word count, heading structure, no broken [[refs]]
    3. Rename to SSOT_v3_MASTER.md
    4. Archive old version to ARCHIVE/superseded/SSOT_v3_<timestamp>.md
    5. Clear processed proposals from STAGING
    6. Append summary to ARCHIVE/session_logs/CONSTITUTION_CHANGES.md

Step 5: NOTIFICATION
    n8n sends desktop notification:
    "Constitution updated: 3 proposals merged, 0 conflicts, 1 Author query pending"
```

---

## 9. EXECUTION PLAN — OpenCode & Kilo Code CLI

### Tool Assignment

| Tool                    | Role                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| **OpenCode**      | Primary code generation agent — runs on Nemotron 3 Super        |
| **Kilo Code CLI** | Terminal-based executor for scaffolding, file ops, n8n API calls |

Both tools are invoked from the project root (`nephilim_chronicles/`) using the
local `.venv` Python environment.

### Scripts to Build — Priority Order

---

#### SCRIPT 1: `nemotron_tool_router.js`

**Type:** n8n Custom Node
**Priority:** P0 — all heavy-agent workflows depend on this
**OpenCode Prompt:**

```
Build an n8n custom node "nemotron_tool_router" that:
1. Accepts: { task_type, context_payload, tool_schemas[], max_tokens }
2. Calculates context budget: if payload > 200K tokens, summarize episodic chunks first
3. Routes to NVIDIA NIM API (primary) or OpenRouter (fallback) based on health check
4. Injects tool schemas into the Nemotron system prompt in OpenAI tool-call format
5. Validates response: confirms tool_call format is valid JSON before returning
6. On failure: logs to /data/TNC_Books35/LOGS/nemotron_errors.log and fires alert
7. Returns: { result, tool_calls[], usage_tokens, model_used }
```

---

#### SCRIPT 2: `update_story_prototype.py`

**Type:** Python service (called by Nemoclaw + Agent 8)
**Priority:** P0 — Story Prototype cannot function without it
**OpenCode Prompt:**

```
Build update_story_prototype.py with these endpoints (FastAPI, port 8767):
POST /extract-triples
  - Input: { chapter_text, book_num, chapter_num, chapter_id }
  - Calls Nemotron tool router to extract Role and Plot triples
  - Checks new triples against tnc_role_graph for contradictions
  - Returns { role_triples[], plot_events[], contradictions[], foreshadow_brief }

POST /upsert-triples
  - Input: { triples[], collection_name, author_approved: bool }
  - Embeds each triple via Ollama nomic-embed-text
  - Upserts to appropriate Qdrant collection
  - Returns { upserted_count, skipped_locked, errors[] }

GET /foreshadow-brief/{book}/{chapter}
  - Queries plot_graph for unplanted effects targeting this chapter range
  - Returns list of narrative seeds Agent 1 should weave into the scene
```

---

#### SCRIPT 3: `crdt_merge.py`

**Type:** Python utility (called by Agent 3 n8n workflow)
**Priority:** P0 — SSOT integrity depends on this
**OpenCode Prompt:**

```
Build crdt_merge.py:
1. scan_staging(staging_dir) → list[Proposal]: reads all .json proposal files
2. classify_conflicts(proposals) → ConflictMap:
   - SAFE (no overlap), ADDITIVE (same section, append), CONFLICT (same section, modify)
3. merge_safe(proposals, ssot_path): directly apply SAFE proposals
4. merge_additive(proposals, ssot_path): append to section in chronological order
5. escalate_conflict(proposals, todo_path): write human-readable query to TODO.md
6. atomic_write(new_content, ssot_path, archive_dir):
   - Write to .tmp, validate structure, rename, archive old version
7. Returns MergeReport with counts of: merged, escalated, rejected, archived
```

---

#### SCRIPT 4: `adamem_initializer.py`

**Type:** Python one-time migration script
**Priority:** P1 — run once to decompose flat Qdrant into 4 tiers
**OpenCode Prompt:**

```
Build adamem_initializer.py:
1. Connect to Qdrant :6333
2. Scroll all 52K+ points from "nephilim_chronicles" collection
3. For each point, classify by payload.category:
   - "chapter_summary" OR no category + contains "Chapter" → tnc_episodes
   - "character_dossier" OR entity_type in ["character","watcher","nephilim"] → tnc_personas
   - "canon_fact" OR contains subject/predicate/object → tnc_role_graph
   - "plot_event" → tnc_plot_graph
   - else → keep in nephilim_chronicles (raw text fallback)
4. Create new collections with appropriate vector configs (768-dim nomic embeddings)
5. Upsert classified points to new collections
6. Print migration report: counts per collection, unclassified count
7. Do NOT delete original collection until author confirms migration successful
```

---

#### SCRIPT 5: `nemoclaw_daemon.py`

**Type:** Python daemon (persistent process, runs on system startup)
**Priority:** P1 — enables all background capabilities
**OpenCode Prompt:**

```
Build nemoclaw_daemon.py using OpenClaw patterns:
1. Main heartbeat loop: asyncio event loop, never exits unless SIGTERM
2. Tasks (use asyncio.create_task):
   - watch_filesystem(): watchdog observer on WATCH_PATH, debounce 5s
   - check_health(): HTTP GET all 6 services, log results every 5 min
   - collect_crdt_proposals(): scan STAGING dir, POST to n8n webhook
   - drift_alert(): every 30 min, run lightweight Ollama drift check
   - nightly_prep(): at 01:45, POST to n8n /webhook/nightly-continuity-prep
3. On file event: { event_type, path } → POST to n8n /webhook/nemoclaw-file-event
4. Graceful shutdown: on SIGTERM, complete in-flight tasks, log shutdown
5. Restart policy: wrap main() in while True with 10s sleep on exception
```

---

#### SCRIPT 6: `cross_book_audit.py`

**Type:** Python script (triggered nightly by n8n at 02:00)
**Priority:** P1
**OpenCode Prompt:**

```
Build cross_book_audit.py:
1. Load all draft chapters from:
   /data/TNC_Books35/MANUSCRIPT/book_3/
   /data/TNC_Books35/MANUSCRIPT/book_4/
   /data/TNC_Books35/MANUSCRIPT/book_5/
2. Load SSOT_v3_MASTER.md, SERIES_BIBLE.md, all dossiers
3. POST entire payload to Nemotron via nemotron_tool_router with tool:
   check_cross_book_continuity(books_text, canon_docs) → AuditReport
4. AuditReport schema:
   { critical_violations[], soft_conflicts[], timeline_anomalies[],
     character_state_deltas[], theological_flags[], seal_sequence_check }
5. Write report to /data/TNC_Books35/02_ANALYSIS/NIGHTLY_AUDIT_<date>.md
6. If critical_violations > 0: POST desktop alert via n8n
```

---

#### SCRIPT 7: `self_refine_loop.py`

**Type:** Python utility (called by Agent 11)
**Priority:** P2

```
Build self_refine_loop.py:
def refine(initial_output: str, scoring_agent: str, max_iterations=3) -> str:
    """
    SELF-REFINE loop:
    1. Score initial_output using scoring_agent (mistral via Ollama)
    2. If score >= 8/10 on all criteria: return output
    3. Else: generate critique, produce revised output
    4. Repeat up to max_iterations
    5. Return best-scoring version
    """
```

---

### Kilo Code CLI — Setup Commands

```bash
# Install and configure Kilo Code CLI
npm install -g kilo-code

# Set Nemotron as primary model
kilo config set model nvidia/nemotron-3-super-120b
kilo config set api-base https://integrate.api.nvidia.com/v1
kilo config set context-window 1000000

# Project root alias
kilo config set workspace F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles

# Build Script 1 (n8n custom node)
kilo build "Build nemotron_tool_router.js n8n custom node per spec" --output n8n_nodes/

# Build Script 2
kilo build "Build update_story_prototype.py FastAPI service per spec" --output .

# Sequential build order: Scripts 1 → 4 → 5 → 2 → 3 → 6 → 7
```

---

## 10. QUALITY EVALUATION — SELF-REFINE LOOPS

### The Gap in v1.0

Agents 4 (Reader Matrix) and 5 (Dopamine Ladder) **reported scores but never
corrected the draft**. A 6/10 scene would receive a report noting it scored 6/10.
The author still had to manually interpret and rewrite. In v2.0, sub-threshold scenes
trigger automatic revision cycles.

### SELF-REFINE Architecture

```
Agent 1 produces chapter draft
        │
        ▼
Agent 4 (Reader Matrix) scores all 8 criteria per scene
Agent 5 (Dopamine Ladder) maps hook density
        │
        ▼
Agent 11 (Self-Refine Scorer) evaluates:
    IF any criterion < 8/10:
        → Generate critique: "Scene 3 fails Theological Accuracy (5/10)
           because: Azazel performs creation-class abilities. Oiketerion
           principle: Watchers lost innate power post-descent."
        → POST critique to Agent 1 via n8n with instruction:
           "Revise scene 3 incorporating this critique"
        → Agent 1 produces targeted revision
        → Agent 4+5 re-score revision
        → Loop max 3 times
    ELSE:
        → Scene approved; flag for Author final review
```

### Theological Guard Integration (Agent 9)

Agent 9 runs **in parallel** with Agents 4+5 on every draft, using Nemotron 3 Super
to validate against a compressed SERIES_BIBLE.md + theological axiom set:

| Check                        | Description                                |
| ---------------------------- | ------------------------------------------ |
| Acoustic Paradigm            | All supernatural tech uses sound/vibration |
| Oiketerion Principle         | Watchers cannot DEMONSTRATE, only TEACH    |
| Raphael's Three Limitations  | Logged per Raphael appearance              |
| Seal Sequence                | Seal breaks match SSOT timeline            |
| Nephilim vs Watcher          | Azazel is Nephilim, NOT Watcher            |
| Christology                  | Christ's role never diluted or reframed    |
| Knowledge Transmission Chain | Watchers → Nephilim → Apkallu → Humans  |

Any theological violation → red-flag to Author TODO.md immediately, **before** any
canon documents are updated.

### Scorer Agent Rubric (Consolidated v2.0)

Each scored item uses the 8-criterion Reader Reaction Matrix plus 3 new criteria
introduced for the finale trilogy:

| Criterion                                   | Description                                      | Books 3–5 Weight |
| ------------------------------------------- | ------------------------------------------------ | ----------------- |
| Theological accuracy                        | Doctrinal integrity                              | **×2.0**   |
| Canon consistency                           | Against SSOT + dossiers                          | ×1.5             |
| Prose quality                               | Literary register maintained                     | ×1.0             |
| Pacing                                      | Matches dopamine ladder position                 | ×1.0             |
| Character voice fidelity                    | Per-character speech/thought patterns            | ×1.5             |
| Emotional resonance                         | Reader impact                                    | ×1.0             |
| Operational/tactical realism                | Combat, tech, logistics                          | ×1.0             |
| Romance thread continuity                   | Cian/Miriam arc coherence                        | ×1.0             |
| **Cross-book causality** *(new)*    | Does this event's effects appear in later books? | **×2.0**   |
| **Seal/prophecy alignment** *(new)* | Horsemen/Revelation sequence coherence           | **×2.0**   |
| **John 15:13 echo** *(new)*         | Is the thematic verse lived, not just stated?    | ×1.5             |

Minimum pass threshold: **8.0 weighted average**. Critical violations in Theological
Accuracy or Cross-book causality block approval regardless of overall score.

---

## 11. INFRASTRUCTURE CHANGES

### New Docker Services

Add to `docker-compose.yml`:

```yaml
  # Story Prototype API
  story-prototype:
    image: python:3.11-slim
    volumes:
      - ./:/app
      - tnc_books35:/data/TNC_Books35
    command: >
      sh -c "cd /app && .venv/bin/python update_story_prototype.py"
    ports:
      - "8767:8767"
    depends_on:
      - qdrant
    restart: unless-stopped

  # Nemoclaw Daemon
  nemoclaw:
    image: python:3.11-slim
    volumes:
      - ./:/app
      - tnc_books35:/data/TNC_Books35
    command: >
      sh -c "cd /app && .venv/bin/python nemoclaw_daemon.py"
    depends_on:
      - n8n
      - qdrant
    restart: always
    environment:
      - NEMOTRON_API_KEY=${NEMOTRON_API_KEY}
      - N8N_WEBHOOK_BASE=http://n8n:5678
```

### New Volume

```yaml
volumes:
  tnc_books35:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles
```

### New Qdrant Collections

```bash
# Run once: create AdaMem tier collections
curl -X PUT http://localhost:6333/collections/tnc_episodes \
  -H 'Content-Type: application/json' \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'

curl -X PUT http://localhost:6333/collections/tnc_personas \
  -H 'Content-Type: application/json' \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'

curl -X PUT http://localhost:6333/collections/tnc_role_graph \
  -H 'Content-Type: application/json' \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'

curl -X PUT http://localhost:6333/collections/tnc_plot_graph \
  -H 'Content-Type: application/json' \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'
```

### New Ports Summary

| Port           | Service                                       |
| -------------- | --------------------------------------------- |
| 5678           | n8n                                           |
| 11434          | Ollama                                        |
| 6333           | Qdrant                                        |
| 5432           | PostgreSQL                                    |
| 8765           | canon_search_api.py                           |
| 8766           | kdp_format_server.py                          |
| **8767** | **update_story_prototype.py** *(new)* |

### Directory Structure (Books 3–5)

```
/data/TNC_Books35/
├── 00_CANON/               ← symlink or copy of CANON/
├── 01_MANUSCRIPT/
│   ├── book_3/
│   ├── book_4/
│   └── book_5/
├── 02_ANALYSIS/
│   ├── DRIFT_LOG.md
│   ├── NIGHTLY_AUDIT_<date>.md
│   └── REPORTS/
│       ├── matrix_b3ch<n>.json
│       └── dopamine_b3ch<n>.json
├── 03_IMAGE_PROMPTS/
├── 04_KDP/
├── 05_SESSION_NOTES/
├── LOGS/
│   ├── DAEMON_HEALTH.log
│   └── nemotron_errors.log
└── STAGING/
    └── crdt_proposals/
```

---

## 12. IMPLEMENTATION ROADMAP

### Phase 0 — Infrastructure (Week 1)

| Task                                             | Owner     | Tool                    |
| ------------------------------------------------ | --------- | ----------------------- |
| Create AdaMem Qdrant collections (4 new)         | Systems   | `curl` commands above |
| Run `adamem_initializer.py` migration          | OpenCode  | Script 4                |
| Add Nemoclaw + Story Prototype to docker-compose | Systems   | Manual edit             |
| Create `/data/TNC_Books35/` directory tree     | Kilo Code | `mkdir`               |
| Configure Nemotron API key in `.env`           | Systems   | Manual                  |

### Phase 1 — Core Routing (Week 2)

| Task                                          | Owner    | Tool              |
| --------------------------------------------- | -------- | ----------------- |
| Build `nemotron_tool_router.js` (n8n node)  | OpenCode | Script 1          |
| Deploy custom node to n8n                     | Systems  | n8n CLI           |
| Build `update_story_prototype.py` (FastAPI) | OpenCode | Script 2          |
| Seed Role Graph with locked canon triples     | OpenCode | Manual + Script 2 |
| Build `crdt_merge.py`                       | OpenCode | Script 3          |

### Phase 2 — Daemon & Background Intelligence (Week 3)

| Task                                      | Owner    | Tool              |
| ----------------------------------------- | -------- | ----------------- |
| Build `nemoclaw_daemon.py`              | OpenCode | Script 5          |
| Start Nemoclaw as Docker service          | Systems  | docker-compose    |
| Verify heartbeat + file watch working     | Systems  | DAEMON_HEALTH.log |
| Wire Nemoclaw → n8n webhooks             | Systems  | n8n               |
| Build `cross_book_audit.py`             | OpenCode | Script 6          |
| Configure nightly 02:00 audit cron in n8n | Systems  | n8n schedule      |

### Phase 3 — Agent Upgrades (Week 4)

| Task                                                      | Owner    | Tool              |
| --------------------------------------------------------- | -------- | ----------------- |
| Upgrade Agent 2 (Drift Manager) to Nemotron               | Systems  | n8n Workflow edit |
| Upgrade Agent 3 (Constitution Updater) to CRDT + Nemotron | Systems  | n8n + Script 3    |
| Add Agent 9 (Theological Guard) n8n workflow              | Systems  | n8n               |
| Add Agent 10 (Cross-Book Continuity) n8n workflow         | Systems  | n8n + Script 6    |
| Add Agent 11 (Self-Refine Scorer) n8n workflow            | Systems  | n8n + Script 7    |
| Build `self_refine_loop.py`                             | OpenCode | Script 7          |

### Phase 4 — Conductor & Full Integration (Week 5)

| Task                                                  | Owner   | Tool              |
| ----------------------------------------------------- | ------- | ----------------- |
| Build Agent 0 (Swarm Conductor) n8n workflow          | Systems | n8n               |
| Implement HAWK master dispatch webhook                | Systems | n8n               |
| Integration test: save Book 3 Ch1 draft               | Systems | End-to-end        |
| Verify all 12 agents fire correctly                   | Systems | n8n execution log |
| Story Prototype — verify Role + Plot graphs populate | Systems | Qdrant dashboard  |
| Author sign-off: swarm live for Book 3 drafting       | Chris   | Review            |

### Phase 5 — Book 3 Production (Ongoing)

- Every chapter draft triggers full HAWK dispatch automatically
- Nemoclaw runs continuously in background
- Nightly audits produce continuity reports before next writing session
- Author TODO.md is the primary interface — system writes to it; Chris resolves

---

## APPENDIX A — New n8n Webhook Registry

| Webhook                              | Method | Payload                  | Purpose                      |
| ------------------------------------ | ------ | ------------------------ | ---------------------------- |
| `/webhook/swarm-dispatch`          | POST   | `{task_type, payload}` | Master entry point (Agent 0) |
| `/webhook/nemoclaw-file-event`     | POST   | `{event_type, path}`   | Nemoclaw → n8n file events  |
| `/webhook/analyse-chapter`         | POST   | `{book, chapter}`      | Trigger Agents 2,4,5,8,9     |
| `/webhook/constitution-update`     | POST   | `{proposals_dir}`      | Trigger Agent 3 CRDT merge   |
| `/webhook/nightly-continuity-prep` | POST   | `{}`                   | Pre-load for 02:00 audit     |
| `/webhook/kdp-assemble`            | POST   | `{book}`               | Trigger Agent 7              |

---

## APPENDIX B — Services at a Glance (v2.0)

| Service                   | URL            | Role                                         | Model             |
| ------------------------- | -------------- | -------------------------------------------- | ----------------- |
| n8n                       | :5678          | Orchestration (Layer 1+2)                    | —                |
| Ollama                    | :11434         | Local LLM (Agents 4,5,6,11)                  | mistral, llama3.1 |
| Qdrant                    | :6333          | All memory tiers                             | —                |
| PostgreSQL                | :5432          | n8n state + execution log                    | —                |
| canon_search_api.py       | :8765          | Semantic canon search                        | nomic-embed-text  |
| kdp_format_server.py      | :8766          | KDP DOCX assembly                            | —                |
| update_story_prototype.py | :8767          | Role/Plot graph service                      | Nemotron          |
| Nemoclaw daemon           | (no port)      | Background warden                            | OpenClaw          |
| Nemotron 3 Super          | OpenRouter/NIM | Long-horizon reasoning (Agents 0,2,3,8,9,10) | 120B MoE          |

---

*Architecture Version 2.0 — DESKTOP-SINGULA | April 8, 2026*
*Books 3–5: The Edenic Mandate, The Testimony, The Glory*
*Kerman Gild Publishing*
