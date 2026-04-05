# THE NEPHILIM CHRONICLES — BOOK 2
## n8n + Ollama Agent Wiring Architecture
*Team Book Two (Timbuktu) | DESKTOP-SINGULA Integration Plan*

---

## THE CORE MAPPING

Your 7-agent Cowork framework maps directly to n8n workflows.
Every Cowork agent = one n8n workflow with an Ollama node at its heart.

```
CURRENT (Cowork)                    TARGET (n8n + Ollama)
─────────────────────────────────────────────────────────────────
Agent 1 — Content Creator           Claude.ai (stays here — no change)
Agent 2 — Drift Manager          →  n8n Workflow: DRIFT_MANAGER
Agent 3 — Constitution Updater   →  n8n Workflow: CONSTITUTION_UPDATER  
Agent 4 — Reader Reaction Matrix →  n8n Workflow: READER_MATRIX
Agent 5 — Dopamine Ladder        →  n8n Workflow: DOPAMINE_LADDER
Agent 6 — Image Prompt Designer  →  n8n Workflow: IMAGE_PROMPTS
Agent 7 — KDP Formatter          →  n8n Workflow: KDP_FORMATTER
                                     (Python script triggered by n8n)
```

---

## WHY THIS IS BETTER THAN COWORK ALONE

| Factor | Cowork | n8n + Ollama |
|--------|--------|--------------|
| Cost | Pro subscription usage | Zero — local GPU |
| Trigger | Manual (you invoke) | Automatic (file watcher) |
| Speed | API latency | RTX 3080 — sub-second |
| Parallelism | One agent at a time | Multiple agents simultaneously |
| Qdrant access | None | Native — canon search built in |
| Logging | Manual | Automatic execution history |
| Scheduling | Manual | Cron — run nightly, etc. |

---

## STEP 1 — VOLUME MOUNT (PREREQUISITE)

n8n runs in Docker and needs access to your TNC_Book2 folder.
Edit: `F:\Projects-cmodi.000\self-hosted-ai-starter-kit\docker-compose.yml`

Find the n8n service and add a volume:
```yaml
  n8n:
    volumes:
      - n8n_storage:/home/node/.n8n
      - C:/Users/cmodi.000/Documents/TNC_Book2:/data/TNC_Book2   # ADD THIS
```

This maps your Windows TNC_Book2 folder into the n8n container at /data/TNC_Book2.
All n8n file operations will use the /data/TNC_Book2 path internally.

After editing, restart the stack:
```powershell
docker compose --profile gpu-nvidia down
docker compose --profile gpu-nvidia up -d
```

---

## STEP 2 — THE 6 n8n WORKFLOWS

---

### WORKFLOW 1 — DRIFT MANAGER (Agent 2)
**Trigger:** Manual webhook OR file watcher (chapter saved)
**Model:** mistral (strong at analytical/comparison tasks)
**Runtime:** ~45 seconds per chapter on RTX 3080

```
[Webhook / File Trigger]
    ↓
[Read File Node] → /data/TNC_Book2/00_CANON/CONSTITUTION.md
    ↓
[Read File Node] → /data/TNC_Book2/00_CANON/CHARACTER_DOSSIERS.md
    ↓
[Read File Node] → /data/TNC_Book2/01_MANUSCRIPT/CHAPTERS/CHAPTER_XX.md
    ↓
[Ollama Chat Node]
  model: mistral
  system: [DRIFT MANAGER PROMPT from TNC_Book2_Cowork_Setup.md]
  user: "Analyse chapter {{$json.chapter_number}} for drift..."
    ↓
[Append File Node] → /data/TNC_Book2/00_CANON/DRIFT_LOG.md
    ↓
[Optional: Gmail/Slack notify] → "Drift report ready for Chapter X"
```

---

### WORKFLOW 2 — CONSTITUTION UPDATER (Agent 3)
**Trigger:** File created in 05_SESSION_NOTES/
**Model:** mistral
**Runtime:** ~30 seconds

```
[File Watcher] → /data/TNC_Book2/05_SESSION_NOTES/*.md
    ↓
[Read New Session Note]
    ↓
[Code Node] → Extract all "### NEW CANON" blocks via regex
    ↓
[IF Node] → Any new canon found?
  YES ↓                          NO ↓
[Ollama Chat Node]              [Stop]
  model: mistral
  system: [CONSTITUTION UPDATER PROMPT]
  user: "Integrate these canon decisions: {{$json.canon_items}}"
    ↓
[Read File] → CONSTITUTION.md
[Ollama] → Produce updated section
[Write File] → CONSTITUTION.md (updated)
    ↓
[Append to session note] → [INTEGRATED — {{$today}}]
```

---

### WORKFLOW 3 — READER REACTION MATRIX (Agent 4)
**Trigger:** Manual webhook with chapter number input
**Model:** llama3.1 (better long-form analytical reasoning)
**Runtime:** ~60-90 seconds per chapter

```
[Webhook] ← POST { "chapter": "CHAPTER_03", "run_type": "full" }
    ↓
[Read File] → Chapter file
    ↓
[Code Node] → Split chapter by scene breaks (✦ or --- markers)
    ↓
[Loop Over Scenes]
    ↓
[Ollama Chat Node] (per scene)
  model: llama3.1
  system: [READER MATRIX PROMPT]
  user: "Score this scene: {{$json.scene_text}}"
    ↓
[Aggregate Results]
    ↓
[Code Node] → Format as CSV/JSON
    ↓
[Write File] → /data/TNC_Book2/02_ANALYSIS/REPORTS/matrix_ch{{chapter}}.json
    ↓
[HTTP Request] → Python script to convert JSON → XLSX
    (or: direct xlsx write via python-docx equivalent)
```

---

### WORKFLOW 4 — DOPAMINE LADDER (Agent 5)
**Trigger:** Manual webhook (run alongside Reader Matrix)
**Model:** llama3.1
**Runtime:** ~60 seconds per chapter

```
[Webhook] ← POST { "chapter": "CHAPTER_03" }
    ↓
[Read File] → Chapter file
    ↓
[Ollama Chat Node]
  model: llama3.1
  system: [DOPAMINE LADDER PROMPT]
  user: "Map all hooks and reward cycles in: {{$json.chapter_text}}"
    ↓
[Code Node] → Parse hook map from response
    ↓
[Write File] → /data/TNC_Book2/02_ANALYSIS/REPORTS/dopamine_ch{{chapter}}.json
    ↓
[HTTP Request] → Python XLSX writer
```

**Note:** Workflows 3 and 4 can be chained — trigger both from one webhook
for a combined "analysis run" per chapter.

---

### WORKFLOW 5 — IMAGE PROMPT DESIGNER (Agent 6)
**Trigger:** Manual webhook with chapter input
**Model:** mistral (creative/descriptive tasks)
**Runtime:** ~20 seconds per chapter

```
[Webhook] ← POST { "chapter": "CHAPTER_03" }
    ↓
[Read File] → Chapter file
    ↓
[Read File] → /data/TNC_Book2/00_CANON/VISUAL_BIBLE.md (create this)
    ↓
[Ollama Chat Node]
  model: mistral
  system: [IMAGE PROMPT DESIGNER system from Cowork setup]
  user: "Generate image prompt for Chapter {{chapter}}"
    ↓
[Append File] → /data/TNC_Book2/03_IMAGE_PROMPTS/CHAPTER_PROMPTS.md
```

---

### WORKFLOW 6 — KDP FORMATTER (Agent 7)
**Trigger:** Manual webhook ("book is done — assemble")
**Runtime:** Python script handles formatting; Ollama not needed here

```
[Webhook] ← POST { "action": "assemble_manuscript" }
    ↓
[HTTP Request] → POST http://localhost:8766/kdp-format
    (a small Python server we create — similar to canon_search_api.py)
    ↓
Python script:
  - Reads all CHAPTERS/*.md in order
  - Uses python-docx to assemble MANUSCRIPT_DRAFT.docx
  - Applies Book 1 KDP specs (margins, fonts, headers, etc.)
  - Writes to /data/TNC_Book2/04_KDP/MANUSCRIPT_DRAFT.docx
  - Generates KDP_CHECKLIST.md
    ↓
[Write File] → Confirmation to n8n
    ↓
[Desktop notification] → "KDP manuscript assembled"
```

---

## STEP 3 — THE MASTER ANALYSIS WEBHOOK

One n8n workflow to rule them all — trigger all analysis agents at once:

```
POST http://localhost:5678/webhook/analyse-chapter
Body: { "chapter": "CHAPTER_03" }

    ↓ Triggers simultaneously:
    ├── DRIFT MANAGER (compare against canon)
    ├── READER MATRIX (score scenes)
    ├── DOPAMINE LADDER (map hooks)
    └── IMAGE PROMPTS (generate visual prompt)

    ↓ When all complete:
    └── Summary email/notification with all 4 outputs
```

---

## STEP 4 — QDRANT INTEGRATION (The Upgrade)

This is what separates your setup from plain Cowork.
The Drift Manager and Constitution Updater can query Qdrant 
BEFORE calling Ollama — giving them semantic canon memory:

```
[Chapter text arrives]
    ↓
[HTTP Request] → POST http://qdrant:6333/collections/nephilim_chronicles/points/search
  body: { "vector": [embed chapter key phrases via Ollama first],
          "limit": 10,
          "filter": { "category": "canon" } }
    ↓
[Returns top 10 most relevant canon chunks]
    ↓
[Ollama Chat Node]
  context: relevant canon chunks from Qdrant
  user: "Now check this chapter for drift against the above canon..."
```

This means your Drift Manager has seen the ENTIRE canon database,
not just the files you happened to load. Far more thorough.

---

## RECOMMENDED BUILD ORDER

**Week 1 — Foundation:**
1. Add TNC_Book2 volume mount to docker-compose.yml
2. Build Workflow 2 (Constitution Updater) — simplest, highest daily value
3. Build Workflow 1 (Drift Manager) — most important quality gate

**Week 2 — Analysis:**
4. Build Workflow 3 + 4 (Reader Matrix + Dopamine Ladder) as linked pair
5. Add Qdrant context injection to Drift Manager

**Week 3 — Production:**
6. Build Workflow 5 (Image Prompts)
7. Build the KDP Python server + Workflow 6

**Week 4 — Polish:**
8. Build Master Analysis Webhook (trigger all at once)
9. Add email/desktop notifications
10. Test full pipeline on Chapters 1-3

---

## WHAT THIS MEANS FOR YOUR WORKFLOW

**Before (Cowork):**
You write a chapter → manually open Cowork → paste instructions → 
wait for response → manually copy output to files → repeat for each agent

**After (n8n + Ollama):**
You write a chapter → save the file → POST one webhook →
four analysis reports appear in your project folders automatically →
Drift log updated → Canon integrated → Image prompt ready →
All processed on your RTX 3080 → zero API cost → zero manual steps

---

*Architecture Version 1.0 — DESKTOP-SINGULA | February 2026*
*Ready for n8n workflow implementation*
