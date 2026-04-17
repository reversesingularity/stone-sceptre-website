# TODO — The Nephilim Chronicles
**Updated:** April 18, 2026

---

## ⚡ CURRENT — Book 3 Chapter 1 Drafting

1. Verify swarm is up: `python day1_ops.py --phase all` (all 6 phases should PASS)
2. Interview Chris on remaining Book 3 decisions (Noctis Labyrinthus, gate mechanics, Michael interdict)
3. Lock Chapter 1 beat outline → get approval → write prose
4. Target: Ch 1 opens at Stewart Island safehouse, same week as Prologue events (March 2028)

**Prologue: ✅ COMPLETE** — `MANUSCRIPT/book_3/CHAPTERS/prologue.md` (~1,580 words, two movements)

Ref: `ARCHIVE/session_logs/SESSION_LOG_2026-04-11.md` for full session state.

---

## ✅ COMPLETE — Operational Silence & Comedic Protocol (April 17-18, 2026)

- [x] **Operational Silence Architecture** — Raphael/Liaigh arc: conversational Empyreal Register severed at Book 3 Ch14 (Eden departure); combat protection maintained through Book 5 Ch10; 2 permitted exceptions locked; 8 Raphael POV chapters mapped; naming convention table locked. Saved to `ARCHIVE/session_logs/OPERATIONAL_SILENCE_ARCHITECTURE_April18_2026.md`
- [x] **Phantom Banter & Comedic Relief Protocol** — Five comedic mechanics for quiet chapters (Phantom Banter, Mo Chrá Peanut Gallery, James Tactical Deadpan, Brennan Engineering Neurosis, Miriam Phased Rule). Miriam comedic constraint evolves at baptism boundary (Book 3 Eden): Phase 1 GCHQ composure → Phase 2 Operational Affection → Phase 3 Devastation Payload (John 15:13 setup). Saved to `REFERENCE/PHANTOM_BANTER_PROTOCOL.md`
- [x] **SSOT_v3 cross-referenced** — Phantom Banter §4.2, Mo Chrá §4.3, Miriam §4.4 all verified consistent
- [x] **DEFERRED_ROMANCE_BEATS.md** (repo memory) — Red line updated: "Comedy never at Miriam's expense" now phased to pre-baptism only; post-baptism evolves to Operational Affection

---

## ✅ COMPLETE — Agent 13 v2.1 (Marketing Engine + Auto-Posting)

- [x] **poster.py** — Dual-track posting: API auto-post (Twitter/LinkedIn/Facebook/Threads) + clipboard (TikTok/Instagram/Substack/Royal Road)
- [x] **Scheduler upgraded** — Queue processor now calls `poster.auto_post_queue()` every 30 min
- [x] **24/6 Sabbath schedule** — Agent 13 works continuously, rests Friday 18:00 → Saturday 18:00
- [x] **LinkedIn API** — OAuth 2.0 complete, token valid until ~June 12, 2026
- [x] **Canon Search API** — Added missing `/health` endpoint
- [x] **Dashboard timeout** — Increased 4s → 12s for Nemotron Router health probes
- [ ] **Facebook API** — Page created (ID: 61570993588997), token generation in progress
- [ ] **Threads API** — Pending (same Meta app as Facebook, free)
- [ ] **LinkedIn token refresh** — Build auto-refresh before June 12 expiry

## 🚀 QUEUED — Marketing Blitz (Sundown Saturday)

```powershell
# Full blitz — all 4 books + NZ grants
python marketing_blitz.py

# Dry-run first to confirm
python marketing_blitz.py --dry-run

# NC only (if Stone & Sceptre manuscripts not yet imported)
python marketing_blitz.py --series nc
```

Outputs to `MARKETING/<book_slug>/<asset_type>/*.json`  
Requires swarm up: Agent 9 (:8772), Nemotron Router (:8768), llama-server (:8780)

---

## ⚡ INFRASTRUCTURE — Phase 6 Complete

- [x] llama.cpp b8744 CUDA 12.4 binary installed at `F:\llama-cpp\llama-server.exe`
- [x] Nemotron 120B UD-IQ3_S (52.74 GiB, 3 shards) downloaded to `F:\models\nemotron-super\UD-IQ3_S\`
- [x] llama-server listening on :8780, health OK
- [x] Start-TNCSwarm.ps1 updated with llama-server config
- [x] PYTHONUTF8=1 fix in Start-TNCSwarm.ps1 (cp1252 encoding bug)
- [x] Swarm 9/9 Python services + Nemoclaw daemon operational
- [ ] Reboot test — confirm `TNC_Swarm_Startup` fires at logon
- [x] Configure 24/6 Agent schedule (1800 Fri → 1800 Sat rest period) — **DONE** (Agent 13 scheduler.py)

---

# Midjourney Prompt Improvement — TODO

## Task
Improve visual prompts for Cian's gear and rides, optimized for Midjourney.
Create unified Chapter Art Template and Book 2 sample prompts.

## Aesthetic Direction
- **Gear/Rides**: Balanced blend of Splinter Cell (tactical darkness, single amber light, lone operative) + Ancient Future (bioluminescent amber, sacred geometry, deep space blacks)
- **Chapter Art**: Generic reusable template, same balanced aesthetic
- **Wards**: Micro-etched geometric symbols, faint amber bioluminescent glow — small, not exaggerated

## Files to Create

- [x] `CANON/dossiers/cians-gear/cians-gear-midjourney-prompts.md`
  - [x] Base Master Exoskeleton prompt
  - [x] Stealth Variant prompt
  - [x] Heavy Combat Variant prompt
  - [x] Arctic Ops Variant prompt

- [x] `CANON/dossiers/cians-rides/cians-rides-midjourney-prompts.md`
  - [x] Shadow Hound (motorcycle)
  - [x] Ward Runner (armored SUV)
  - [x] Giant Slayer (APC)
  - [x] Eagle's Whisper (drone)
  - [x] Storm Herald (helicopter)
  - [x] Thunder's Judgment (gunship)
  - [x] Siren's Bane (jet ski)
  - [x] Abyss Warden (patrol boat)
  - [x] Leviathan Breaker (submarine)

- [x] `MANUSCRIPT/book_2/IMAGE_PROMPTS/CHAPTER_ART_TEMPLATE.md`
  - [x] Generic fill-in-the-blank BASE PROMPT
  - [x] Field guide table
  - [x] Fixed aesthetic anchors section
  - [x] 4 worked examples (Prologue I, Prologue II, Ch01, Ch02)

- [x] `MANUSCRIPT/book_2/IMAGE_PROMPTS/BOOK2_IMAGE_PROMPTS_SAMPLES.md`
  - [x] Book 2 cover concept — "The Cauldron of God" (+ alternative Naamah POV)
  - [x] Chapter art samples for all 4 existing chapters (+ alternatives for each)

## Completed
- [x] Read cians-gear.md
- [x] Read cian's-rides.md
- [x] Read visualisation_prompts.md
- [x] Read REFERENCE/VISUAL_DIRECTION.md
- [x] Read CANON/CANON_ADDITION_AESTHETIC_CONTINUITY.md
- [x] Read CANON/dossiers/PROTAGONIST_DOSSIERS.md
- [x] Read MANUSCRIPT/book_2/CHAPTERS/PROLOGUE_SCENE1_TheFountainsOfTheDeep.md
- [x] Plan confirmed by user

## HITL GATE — 2026-04-09 15:42
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.

## HITL GATE — 2026-04-09 15:47
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.

## HITL GATE — 2026-04-09 15:50
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.

## ⚠ THEOLOGICAL FLAG [RED] — Azazel Classification
**Book:** 3  **Chapter:** 1  **Time:** 2026-04-09 16:21

**Violation:** Pattern match triggered: Azazel Classification

**Axiom:** AZAZEL_IS_NEPHILIM — Azazel Classification

*This flag was auto-generated by theological_guard_server.py.*

---

## ⚠ THEOLOGICAL FLAG [RED] — Azazel Classification
**Book:** 3  **Chapter:** 1  **Time:** 2026-04-09 16:22

**Violation:** Pattern match triggered: Azazel Classification

**Axiom:** AZAZEL_IS_NEPHILIM — Azazel Classification

*This flag was auto-generated by theological_guard_server.py.*

---

## ⚠ THEOLOGICAL FLAG [RED] — Azazel Classification
**Book:** 3  **Chapter:** 1  **Time:** 2026-04-09 16:22

**Violation:** Pattern match triggered: Azazel Classification

**Axiom:** AZAZEL_IS_NEPHILIM — Azazel Classification

*This flag was auto-generated by theological_guard_server.py.*

---

## HITL GATE — 2026-04-10 17:29
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.

## HITL GATE — 2026-04-10 17:49
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.

## HITL GATE — 2026-04-11 19:15
- **Agent:** AGENT_11
- **Operation:** publish_manuscript
- **Section:** N/A
- **Reason:** Operation 'publish_manuscript' requires AUTHOR approval (HITL gate)
- **Action required:** AUTHOR must review and manually approve or deny.
