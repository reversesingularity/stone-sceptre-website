# Author Task List — The Nephilim Chronicles
**Generated:** April 9, 2026  
**Last Updated:** April 18, 2026  
**Status:** Active

---

## PRIORITY 1 — Book 2 Publishing Pipeline

Book 2 first draft is **complete** (Prologue + Ch1–14 + Epilogue, ~125,000 words). These tasks move it to KDP:

- [ ] **Full continuity audit** — Read through all chapters sequentially; flag timeline inconsistencies, name drift, or contradictions with locked canon (SSOT_v3_MASTER.md)
- [ ] **Polish/revision pass** — Line-level prose editing across all 18 chapter files in `MANUSCRIPT/book_2/CHAPTERS/`
- [ ] **Resolve open decisions** (from HANDOFF_PROMPT_KEY_ELEMENTS.md):
  - [ ] Noctis Labyrinthus as Mars station — confirm or reject
  - [ ] Gate mechanics (Acoustic Resonance Depletion Model) — confirm or reject
  - [ ] Michael territorial interdict over Greenland — confirm or reject
  - [ ] Inter-domain transit frequency discovery — confirm or reject
  - [ ] Liaigh's access to Dudael/Cydonia-class sites — resolve
  - [ ] Mo Chrá cold-weather behavior at Antarctic temps — resolve
  - [ ] Acoustic key: 5 remaining tones mechanism — decide
  - [ ] Mo Chrá recovery timeline post-Gehenna expenditure — resolve
  - [ ] Liaigh's silence at end of Ch6 — decide cause
  - [ ] Miriam's acoustic compatibility with Gehenna frequency — resolve or leave seeded
- [ ] **Generate chapter art** — Midjourney v6.1 using prompts from `MANUSCRIPT/book_2/IMAGE_PROMPTS/`
- [ ] **Upscale images** — Real-ESRGAN 4x (`realesrgan-ncnn-vulkan.exe -n realesrgan-x4plus -s 4`)
- [ ] **Resize to KDP specs** — Run `resize_to_kdp.ps1` (1650px max width, 300 DPI)
- [ ] **Build .docx** — `$env:KDP_BOOK = "2"; python build_manuscript.py`
- [ ] **Update TOC** — In Word: Ctrl+A → F9
- [ ] **Final proofread** — full read-through in .docx format
- [ ] **Upload to KDP**

---

## PRIORITY 2 — HITL Gates Pending Review

Three publish_manuscript requests from AGENT_11 are waiting in TODO.md:

- [ ] Review HITL gate (15:42) — approve or deny
- [ ] Review HITL gate (15:47) — approve or deny
- [ ] Review HITL gate (15:50) — approve or deny

Two theological flags (RED) for Azazel Classification in `MANUSCRIPT/book_3/chapter_01_test.md`:

- [ ] Review `chapter_01_test.md` — verify Azazel is correctly identified as NEPHILIM (son of Gadreel), NOT a Watcher

---

## PRIORITY 3 — Swarm Operations Verification

**2026-04-10 session completed the following:**

- [x] **HAWK Swarm upgraded to v2.1** — All Mistral references replaced with 4-tier Nemotron Router cascade (NIM → OpenRouter → GGUF → Ollama)
- [x] **Agent 9 created** — `agent_9_content_strategist.py` on port 8772 (social content, SEO, NZ grants)
- [x] **n8n expanded to 14 workflows** — WF11 (social), WF12 (SEO), WF13 (NZ grants) added; PATCH→PUT bug fixed
- [x] **day1_ops Phases 1–5 all PASS** — json_mode fixed (`response_format: json_object`); all canary tests green
- [x] **TNC_Swarm_Startup registered** — Windows Task Scheduler logon task; all 8 servers auto-start
- [ ] **Reboot test** — Restart to confirm `TNC_Swarm_Startup` fires at logon *(pending next reboot)*
- [ ] **Verify logs** — After reboot, check `LOGS/swarm_startup_*.log` for per-server output
- [x] **Re-run day1_ops smoke test** — Phases 1–5 PASS (2026-04-10); Phase 6 pending formal re-run
- [x] **Phase 6 (llama-server)** — llama.cpp b8744 CUDA 12.4 installed at `F:\llama-cpp\`, Nemotron 120B UD-IQ3_S (52.74 GiB) downloaded, server listening on :8780 (2026-04-11)
- [ ] **Check nightly audit** — After 02:00, verify `02_ANALYSIS/` has a fresh audit file

---

## PRIORITY 4 — Book 2 Remaining Items

- [ ] **Session handoff document** — Finalize handoff notes for any future collaborators (mentioned in SESSION_7_STATUS.md as outstanding)
- [ ] **Courtship arc placement** — Decide final placement for deferred romance beats (Gift of Provision, Declaration to James) in Ch7+ (see `DEFERRED_ROMANCE_BEATS.md` in repo memory)

---

## PRIORITY 5 — Book 3 Pre-Production ← **IN PROGRESS**

Architecture is locked in `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md`.  
**Status:** Prologue DRAFTED and APPROVED (2026-04-11). Chapter 1 next.

**Completed:**
- [x] Prologue architecture interview (9 questions + 4 follow-ups)
- [x] Prologue Movement I (~1,050 words) — Brennan POV, Azazel as "Dr. Ezra Adon" at UN, pharmakeia miracle
- [x] Prologue Movement II (~530 words) — Cian/Miriam/Brennan at Stewart Island, Mo Chrá compass mode
- [x] Saved to `MANUSCRIPT/book_3/CHAPTERS/prologue.md`

**Pre-draft decisions still needed:**
- [ ] Confirm or reject: Noctis Labyrinthus as Mars station (carried from Book 2)
- [ ] Confirm or reject: Acoustic Resonance Depletion Model for gate mechanics
- [ ] Decide: Michael territorial interdict over Greenland — still active in Book 3?
- [ ] Decide: Liaigh's access to Dudael/Cydonia sites after Book 2 events
- [ ] Confirm: Mo Chrá is in compass mode at Book 3 open (not weapon mode)

**Scaffolding (do before or during first draft session):**
- [x] **Scaffold Book 3 manuscript** — `MANUSCRIPT/book_3/CHAPTERS/prologue.md` created; Ch1+ still needed
- [ ] **Update build_manuscript.py** — Add `SOURCE_FILES_BOOK3`, `MANUSCRIPT_DIR_BOOK3`, `OUTPUT_FILE_BOOK3` constants; add `elif book == 3:` block
- [ ] **Lock Book 3 detailed outline** — Beat-by-beat scene breakdown using `BOOKS_3_5_ARCHITECTURE.md` chapter map

**First scene target — Prologue Movement I: ✅ COMPLETE**  
POV: Brennan McNeeve (debriefing at Stewart Island, watching UN broadcast)  
Beat: Azazel (as "Dr. Ezra Adon") delivers pharmakeia miracle at UN General Assembly  
File: `MANUSCRIPT/book_3/CHAPTERS/prologue.md` (~1,580 words total, two movements)

---

## PRIORITY 5B — Agent 13 v2.1 Marketing Engine (OPERATIONAL)

**Status:** Agent 13 upgraded to v2.1 with autonomous 24/6 operation, poster module, and LinkedIn API integration.

**Completed (April 13, 2026):**
- [x] `poster.py` — API auto-posting (LinkedIn live, Twitter/Facebook/Threads pending keys) + clipboard manual posting (TikTok, Instagram, Substack, Royal Road)
- [x] `scheduler.py` — 24/6 autonomous operation with Sabbath rest (Fri 18:00 → Sat 18:00)
- [x] LinkedIn OAuth 2.0 — Token valid until ~June 12, 2026 (Client ID + Secret saved for renewal)
- [x] Facebook page created — ID `61570993588997`
- [x] 4 new endpoints: `/social/clipboard`, `/social/post-now`, `/social/api-status`, `/social/clipboard/{id}/done`
- [x] Canon Search API — `/health` endpoint added
- [x] Monitoring dashboard — timeout 4s → 12s

**Pending:**
- [ ] Facebook API token — complete Graph API Explorer flow → page token → long-lived token
- [ ] Threads API — same Meta app, free
- [ ] LinkedIn token auto-refresh — build before June 12 expiry
- [ ] Twitter/X — $100/mo Basic tier decision (clipboard posting works without it)

## PRIORITY 5C — Marketing Blitz (All Published Books)

**Status:** Script built (`marketing_blitz.py`). Dry-run verified. Ready to fire.

**Execution command:** `python marketing_blitz.py` (full blitz, all 4 books + NZ grants)

Requires: Swarm up (Agent 9 on :8772, Nemotron Router on :8768, llama-server on :8780)

**Assets to generate:**
- [x] `marketing_blitz.py` — trigger script built & dry-run tested (2026-04-11)
- [ ] **SEO metadata** — 4 books × Amazon KDP 7-keyword slots, BISAC, A/B titles, HTML descriptions
- [ ] **Social content** — 8 chapter packs (4 per NC book) × TikTok, LinkedIn, Twitter, YouTube community
- [ ] **YouTube briefs** — 8 anchor video scripts (4 per NC book) with hooks, thumbnails, outlines
- [ ] **Serialization schedules** — 4 books × DTC exclusivity windows, revenue projections
- [ ] **NZ grants** — Scrape NZSA, Mātātuhi, Creative NZ
- [ ] Upload optimized SEO to Amazon KDP for all 4 titles
- [ ] Schedule social content calendar across platforms
- [ ] Purchase domain ($35 NZD) and stand up DTC landing page

**Note:** Stone & Sceptre social/YouTube require manuscript files — currently not in workspace. SEO + serialization will generate from descriptions.

---

## PRIORITY 6 — Canon Maintenance

- [ ] **SSOT_v3_MASTER.md** — Incorporate any new facts from Book 2 Ch13–14 drafting (Josephite ops, Stewart Island safehouse, Azazel acoustic fingerprint captured by Mo Chrá)
- [ ] **Watcher/Nephilim dossier updates** — Ensure entities encountered in Book 2 endgame have current dossier entries
- [ ] **Clean TODO.md** — The current TODO.md has accumulated HITL gates and theological flags mixed with completed Midjourney tasks. Archive or reorganize once resolved.
- [x] **Operational Silence Architecture** — Locked (April 17-18, 2026). Session log archived.
- [x] **Phantom Banter Protocol** — Locked (April 18, 2026). Five comedic mechanics + Miriam phased rule documented in `REFERENCE/PHANTOM_BANTER_PROTOCOL.md`.

---

## Reference: Files to Know

| File | Purpose |
|------|---------|
| `Start-TNCSwarm.ps1` | Boot-time swarm startup (registered as scheduled task) |
| `REFERENCE/COMBAT_STYLE_GUIDE.md` | Mandatory action/combat style framework |
| `REFERENCE/PHANTOM_BANTER_PROTOCOL.md` | Comedic relief & quiet chapter protocol (5 mechanics, Miriam phased rule) |
| `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md` | Locked architecture for Books 3–5 |
| `WORLDBUILDING/ENDGAME_FATES.md` | Character fates (Option B locked) |
| `WORLDBUILDING/FIVE_BOOK_STRUCTURE.md` | Series-level structure |
| `MANUSCRIPT/book_2/SESSION_NOTES/SESSION_7_STATUS.md` | Latest Book 2 session status |
| `.github/copilot-instructions.md` | Copilot canon authority + combat guide |
