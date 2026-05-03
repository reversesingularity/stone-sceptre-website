# Author Task List — The Nephilim Chronicles

**Generated:** April 9, 2026
**Last Updated:** May 4, 2026 (AUDIOBOOK_ASSEMBLER pipeline deployed)
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
- [X] **HAWK Swarm upgraded to v2.2** — Agent 15 (Audiobook Prep) added; 15 agents, 15 workflows, 10 Python services (May 4, 2026)
- [X] **AUDIOBOOK_ASSEMBLER pipeline deployed** — `INFRA/agents/audiobook_prep_server.py` (port 8776), WF15, `CANON/PHONETIC_GLOSSARY.md`, Conductor wired
- [ ] **Reboot test** — Restart to confirm `TNC_Swarm_Startup` fires at logon *(pending next reboot)*
- [ ] **Verify logs** — After reboot, check `LOGS/swarm_startup_*.log` for per-server output
- [ ] **Deploy WF15** — Run `python n8n_deploy_workflows.py` then trigger `POST /webhook/audiobook-assemble` with `{"book": 2}`
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

## PRIORITY 5 — ✅ COMPLETE: Book 3 Drafted, Edited & Scored (April 19, 2026)

Architecture is locked in `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md`.
**Status:** All 17 chapters (Prologue + Ch1–15 + Epilogue) DRAFTED, 5 structural prose edits APPLIED, 6-metric re-score COMPLETE. Final verdict: **26.5/30 EXCELLENT** (6 EXCEPTIONAL chapters, 10 EXCELLENT, 1 GOOD). Book 3 word count: ~104,000 words.

**Completed:**

- [X] Pre-draft strategic decisions LOCKED (April 18, 2026)
  - [X] Noctis Labyrinthus confirmed as Mars station (Book 2 Ch9, "The Labyrinth of Night")
  - [X] Acoustic Resonance Depletion Model confirmed (Book 2 Ch8, 3–4 transit limit)
  - [X] Michael's territorial interdict remains ACTIVE over Greenland
  - [X] Mo Chrá compass mode LOCKED at Book 3 open (432 Hz pure compass frequency)

- [X] **Prologue: THE FIRMAMENT OPENS** — ~4,200 words DRAFTED
  - [X] Movement I: Brennan POV, Azazel UN presentation (HFRS-9 cure), spectrograph analysis
  - [X] Movement II: Stewart Island kitchen, Mo Chrá nine-second creation harmonic, team reaction
  - [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/prologue.md`

- [X] **Chapter 1: THE ARCHITECTURE OF RESISTANCE** — ~3,800 words DRAFTED
  - [X] Movement I: War room debrief; Dudael intelligence synthesis
  - [X] Movement II: Miriam's FININT financial anatomy (cure as trojan horse)
  - [X] Movement III: Brennan dissolves McNeeve Space Systems
  - [X] Movement IV: Mo Chrá compass vector established (southeast → Tigris-Euphrates)
  - [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/CHAPTER_01_TheArchitectureOfResistance.md`

- [X] **Chapter 2: THE FREQUENCY BENEATH THE CURE** — ~3,600 words DRAFTED

---

## PRIORITY 6 — ✅ COMPLETE: Book 3 Website Deployed (April 26, 2026)

**Status:** Full website integration for *The Edenic Mandate* (Book 3) live on `kermangildpublishing.org`.

**Completed:**

- [X] Created full Book 3 landing page (`nephilim/book3/index.html`) with:
  - [X] Hero section with Revelation 11:3 quote
  - [X] Full synopsis (Azazel release, Two Witnesses in Eden, Brennan interludes)
  - [X] 9 character cards (Cian, Liaigh, Enoch, Elijah, Miriam, Brennan, Dismas, Azazel, Mo Chrá)
  - [X] All 15 chapters + prologue/epilogue triptych with full chapter descriptions
  - [X] Author bio and Book 4 teaser
  - [X] Responsive 3D book cover display (front + back + spine)
- [X] Added Book 3 to series navigation on Book 1 page (`nephilim/index.html`)
- [X] Added Book 3 teaser section on Book 1 page
- [X] Added Book 3 footer link on Book 1 page
- [X] Added Book 3 to series navigation on Book 2 page (`nephilim/book2/index.html`)
- [X] Added Book 3 teaser section before footer on Book 2 page
- [X] Added Book 3 footer link on Book 2 page
- [X] Added Book 3 card to root landing page (`index.html`) with Revelation 11:3 quote
- [X] Added Book 3 footer link to root landing page
- [X] Deployed 7 files to GitHub Pages via REST API (April 26, 2026)

**Live URL:** https://kermangildpublishing.org/nephilim/book3/
  - [X] Movement I: Spectral archaeology; Brennan reverse-engineers vaccine vials
  - [X] Movement II: Trap architecture (Cydonian metamaterial suspension revealed)
  - [X] Movement III: Mo Chrá synthesizes acoustic countermeasure (432 Hz harmonic)
  - [X] Movement IV: Stakes clarification (millions vaccinated; House Khem race begins)
  - [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/CHAPTER_02_TheFrequencyBeneathTheCure.md`

- [X] **Chapter 3: THE LAST CARTOGRAPHY** — ~3,900 words DRAFTED
  - [X] Movement I: Miriam maps House Khem acoustic geomantic web via FININT
  - [X] Movement II: Geomantic realization (House Khem walks Nephilim territorial claims from 3504 BCE)
  - [X] Movement III: Brennan farewell (stays behind to build Philadelphian Cell Layer Zero)
  - [X] Movement IV: Team departure for Iraq with countermeasure jammer
  - [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/CHAPTER_03_TheLastCartography.md`

- [X] **Chapter 4: THE GAUNTLET** — ~4,500+ words DRAFTED (10/10 adrenaline peak)
  - [X] Movement I: Ward Runner pursuit across House Khem territory
  - [X] Movement II: Acoustic cat-and-mouse (Khem detects vehicles, not Mo Chrá creation harmonic)
  - [X] Movement III: Vehicle graveyard at cherubim threshold; Josephite rearguard known-casualties op
  - [X] Movement IV: Running fight CQB (Cian dual-wields Mo Chrá + SIG Sauer P365)
  - [X] Movement V: Threshold crossing (Mo Chrá creation harmonic; absolute silence; Eden entry)
  - [X] Saved to `MANUSCRIPT/book_3/CHAPTERS/CHAPTER_04_TheGauntlet.md`

- [X] **Chapters 5–15 + Epilogue** — All remaining chapters DRAFTED (~66,000 words)
- [X] **5 structural prose edits** — Ch3 Section I trim, Ch3 planted cliffhanger, Ch9 distinct theological vector, Ch9 dread beat, Ch9 Movement III restructure
- [X] **6-metric scoring framework** — TIR (Theological/Intellectual Resonance) added as 6th metric; all 17 chapters rescored via 4 parallel blind sub-agents
- [X] **Final verdict: 26.5/30 EXCELLENT** — 6 EXCEPTIONAL: Ch4 (29.0), Ch11 (29.0), Ch14 (29.0), Ch12 (28.0), Ch15 (28.5), Epilogue (27.5)

**Scaffolding (completed):***

- [X] **Scaffold Book 3 manuscript** — All chapter markdown files created + populated
- [X] **Update build_manuscript.py** — SOURCE_FILES_BOOK3, MANUSCRIPT_DIR_BOOK3, OUTPUT_FILE_BOOK3, elif book == 3 routing completed (Commit 41309d0)
- [X] **Lock Book 3 detailed outline** — Act I (Prologue + Ch1–4) beat architecture fully locked (Commit 41309d0)


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

## PRIORITY 5D — ✅ COMPLETE: Book 3 Scoring Framework Upgrade (April 19, 2026)

**Status:** 6-Metric Dopamine Framework verified. Book 3 scores **26.5/30 EXCELLENT** across all 17 chapters.

**Completed:**

- [X] **Identified 5-metric framework blind spot** — Theological chapters (Ch6, Ch7, Ch9, Ch10) systematically underscored under 5-metric /25 framework
- [X] **Designed TIR metric** — Theological/Intellectual Resonance (1–5) as 6th metric; measures doctrine-made-embodied, worldbuilding revelation, intellectual payoff
- [X] **Applied 5 structural prose edits** prior to re-score:
  - Ch3 Section I scalpel trim (bureaucratic overrun removed)
  - Ch3 planted cliffhanger (Cian senses Dudael pulse at section end)
  - Ch9 distinct theological vector (grace as zero-friction frequency, not absence of Dread)
  - Ch9 dread beat added (Mo Chrá ghost-registers Azazel’s counter-design)
  - Ch9 Movement III restructure (Dismas’s sacrament delivered with Enoch/Elijah present)
- [X] **4 parallel blind sub-agent re-score** — All 17 chapters scored independently via 4 separate agents
- [X] **Final verdict: 26.5/30 EXCELLENT** — 6 EXCEPTIONAL, 10 EXCELLENT, 1 GOOD
  - EXCEPTIONAL chapters: Ch4 (29.0/30), Ch11 (29.0/30), Ch14 (29.0/30), Ch12 (28.0/30), Ch15 (28.5/30), Epilogue (27.5/30)
  - Endgame run Ch11–Epilogue: **27.75/30 average across 6 chapters**
  - TIR 5.0 (PERFECT): Ch1, Ch2, Ch3, Ch5, Ch6, Ch7, Ch9, Ch10, Ch11, Ch12, Ch14, Ch15, Epilogue (13 of 17 chapters)
- [X] **Analysis document updated** — `MANUSCRIPT/book_3/ANALYSIS/DOPAMINE_LADDER_READER_REACTION_MATRIX_BOOK_3_COMPLETE.md`
- [X] **4 landmark passages identified** by independent scoring agents:
  - Ch11’s Istanbul field report — “most devastating passage in the manuscript”
  - Ch14’s farewell chord — “emotional apex of the entire series to date”
  - Ch9’s Dismas testimony — “single most powerful passage in all three books”
  - Epilogue’s closing line — “The math did not work. The prayer made it work.”

**Verdict:** Book 3 is publication-ready. Proceed to KDP preparation and Book 4 planning.

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
