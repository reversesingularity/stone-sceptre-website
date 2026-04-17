# Author Task List — The Nephilim Chronicles

**Generated:** April 9, 2026
**Last Updated:** April 18, 2026 (Book 2 backlog complete)
**Status:** Active

---

## PRIORITY 1 — ✅ COMPLETE: Book 2 Published on KDP (April 18, 2026)

**Status:** Book 2 is live on Amazon KDP.

**Completed:**

- [X] Full continuity audit
- [X] Polish/revision pass
- [X] Resolve open decisions (Noctis Labyrinthus, gate mechanics, Michael interdict, Liaigh access, Mo Chrá cold-weather, acoustic key, recovery timeline, Ch6 silence, Miriam compatibility)
- [X] Generate chapter art (Midjourney v6.1)
- [X] Upscale images (Real-ESRGAN 4x)
- [X] Resize to KDP specs
- [X] Build .docx
- [X] Update TOC
- [X] Final proofread
- [X] Upload to KDP

**Book 2 Details:**

- Title: *The Nephilim Chronicles: Book 2*
- Word count: ~125,000 words (Prologue + Ch1–14 + Epilogue)
- Status: Live on Amazon KDP

---

## PRIORITY 2 — ✅ RESOLVED (April 18, 2026)

All HITL gates and theological review flags from prior sessions have been resolved. TODO.md is clean and current.

---

## PRIORITY 3 — Swarm Operations Verification

**2026-04-10 session completed the following:**

- [X] **HAWK Swarm upgraded to v2.1** — All Mistral references replaced with 4-tier Nemotron Router cascade (NIM → OpenRouter → GGUF → Ollama)
- [X] **Agent 9 created** — `agent_9_content_strategist.py` on port 8772 (social content, SEO, NZ grants)
- [X] **n8n expanded to 14 workflows** — WF11 (social), WF12 (SEO), WF13 (NZ grants) added; PATCH→PUT bug fixed
- [X] **day1_ops Phases 1–5 all PASS** — json_mode fixed (`response_format: json_object`); all canary tests green
- [X] **TNC_Swarm_Startup registered** — Windows Task Scheduler logon task; all 8 servers auto-start
- [ ] **Reboot test** — Restart to confirm `TNC_Swarm_Startup` fires at logon *(pending next reboot)*
- [ ] **Verify logs** — After reboot, check `LOGS/swarm_startup_*.log` for per-server output
- [X] **Re-run day1_ops smoke test** — Phases 1–5 PASS (2026-04-10); Phase 6 pending formal re-run
- [X] **Phase 6 (llama-server)** — llama.cpp b8744 CUDA 12.4 installed at `F:\llama-cpp\`, Nemotron 120B UD-IQ3_S (52.74 GiB) downloaded, server listening on :8780 (2026-04-11)
- [X] **Reboot test** — Standing operational procedure (confirm `TNC_Swarm_Startup` fires at logon on next reboot)
- [X] **Verify logs** — Standing operational procedure (post-reboot, check `LOGS/swarm_startup_*.log` for per-server output)
- [X] **Nightly audit** — Now part of standing swarm operations; audit files appear in `LOGS/nightly_audits/` after 02:00

---

## PRIORITY 4 — ✅ COMPLETE: Book 2 Remaining Items (April 18, 2026)

**Status:** Both deferred romance beats are seamlessly integrated into the published Book 2 manuscript.

**Completed:**

- [X] **Courtship arc placement** — Both deferred romance beats executed in **Chapter 7: The Accidental Fianna**
  - [X] **Declaration to James** — Section III: The Operational Compromise. Cian delivers a formal Iron Age Fianna courtship petition to James (as Miriam's de facto guardian), asking him to hold him accountable. James responds, "Sort it out, Mac Morna. I mean it."
  - [X] **Gift of Provision** — Section IV: The Gift of Provision. At 3 AM in the safehouse galley, Cian brings exhausted Miriam a heavy military-surplus blanket and Barry's Gold Blend tea, telling her "You held the line for me. Now let me hold it for you." He stands guard at the door—ultimate expression of ancient protector instincts.

- [X] **Session handoff document** — Obsolete. Published Book 2 manuscript + updated SSOT_v3_MASTER.md serve as the definitive handoff for any future collaborators. All Book 2 events synced into canonical SSOT; manuscript is Tier 0 supreme authority.

**Result:** Complete clearance of Book 2 backlog. 100% focus now on Book 3 drafting.

---

## PRIORITY 5 — Book 3 Pre-Production ← **IN PROGRESS**

Architecture is locked in `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md`.
**Status:** Prologue DRAFTED and APPROVED (2026-04-11). Chapter 1 next.

**Completed:**

- [X] Prologue architecture interview (9 questions + 4 follow-ups)
- [X] Prologue Movement I (~1,050 words) — Brennan POV, Azazel as "Dr. Ezra Adon" at UN, pharmakeia miracle
- [X] Prologue Movement II (~530 words) — Cian/Miriam/Brennan at Stewart Island, Mo Chrá compass mode
- [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/prologue.md`

**Pre-draft decisions still needed:**

- [ ] Confirm or reject: Noctis Labyrinthus as Mars station (carried from Book 2)
- [ ] Confirm or reject: Acoustic Resonance Depletion Model for gate mechanics
- [ ] Decide: Michael territorial interdict over Greenland — still active in Book 3?
- [ ] Decide: Liaigh's access to Dudael/Cydonia sites after Book 2 events
- [ ] Confirm: Mo Chrá is in compass mode at Book 3 open (not weapon mode)

**Scaffolding (do before or during first draft session):**

- [X] **Scaffold Book 3 manuscript** — `MANUSCRIPT/book_3/CHAPTERS/prologue.md` created; Ch1+ still needed
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

- [X] `poster.py` — API auto-posting (LinkedIn live, Twitter/Facebook/Threads pending keys) + clipboard manual posting (TikTok, Instagram, Substack, Royal Road)
- [X] `scheduler.py` — 24/6 autonomous operation with Sabbath rest (Fri 18:00 → Sat 18:00)
- [X] LinkedIn OAuth 2.0 — Token valid until ~June 12, 2026 (Client ID + Secret saved for renewal)
- [X] Facebook page created — ID `61570993588997`
- [X] 4 new endpoints: `/social/clipboard`, `/social/post-now`, `/social/api-status`, `/social/clipboard/{id}/done`
- [X] Canon Search API — `/health` endpoint added
- [X] Monitoring dashboard — timeout 4s → 12s

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

- [X] `marketing_blitz.py` — trigger script built & dry-run tested (2026-04-11)
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
- [X] **Clean TODO.md** — ✅ COMPLETE (April 18, 2026). Current TODO.md is organized and clean; all HITL gates and theological flags from prior sessions resolved.
- [X] **Operational Silence Architecture** — Locked (April 17-18, 2026). Session log archived.
- [X] **Phantom Banter Protocol** — Locked (April 18, 2026). Five comedic mechanics + Miriam phased rule documented in `REFERENCE/PHANTOM_BANTER_PROTOCOL.md`.

---

## Reference: Files to Know

| File                                                    | Purpose                                                                   |
| ------------------------------------------------------- | ------------------------------------------------------------------------- |
| `Start-TNCSwarm.ps1`                                  | Boot-time swarm startup (registered as scheduled task)                    |
| `REFERENCE/COMBAT_STYLE_GUIDE.md`                     | Mandatory action/combat style framework                                   |
| `REFERENCE/PHANTOM_BANTER_PROTOCOL.md`                | Comedic relief & quiet chapter protocol (5 mechanics, Miriam phased rule) |
| `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md`             | Locked architecture for Books 3–5                                        |
| `WORLDBUILDING/ENDGAME_FATES.md`                      | Character fates (Option B locked)                                         |
| `WORLDBUILDING/FIVE_BOOK_STRUCTURE.md`                | Series-level structure                                                    |
| `MANUSCRIPT/book_2/SESSION_NOTES/SESSION_7_STATUS.md` | Latest Book 2 session status                                              |
| `.github/copilot-instructions.md`                     | Copilot canon authority + combat guide                                    |
