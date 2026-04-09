# Author Task List — The Nephilim Chronicles
**Generated:** April 9, 2026  
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

The startup script is registered but hasn't been tested end-to-end at boot:

- [ ] **Reboot test** — Restart the machine to confirm `TNC_Swarm_Startup` fires at logon and all services come up
- [ ] **Verify logs** — After reboot, check `LOGS/` for server stdout/stderr files (one per server)
- [ ] **Run day1_ops smoke test** — `.\.venv\Scripts\python.exe day1_ops.py` (confirms all 12 services wired correctly)
- [ ] **Check nightly audit** — After 02:00, verify `02_ANALYSIS/` has a fresh audit file

---

## PRIORITY 4 — Book 2 Remaining Items

- [ ] **Session handoff document** — Finalize handoff notes for any future collaborators (mentioned in SESSION_7_STATUS.md as outstanding)
- [ ] **Courtship arc placement** — Decide final placement for deferred romance beats (Gift of Provision, Declaration to James) in Ch7+ (see `DEFERRED_ROMANCE_BEATS.md` in repo memory)

---

## PRIORITY 5 — Book 3 Pre-Production

Architecture is locked in `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md`. Before drafting begins:

- [ ] **Scaffold Book 3 manuscript** — Create `MANUSCRIPT/book_3/CHAPTERS/` with chapter files (replace or build on `chapter_01_test.md`)
- [ ] **Update build_manuscript.py** — Add `SOURCE_FILES_BOOK3`, `MANUSCRIPT_DIR_BOOK3`, `OUTPUT_FILE_BOOK3` constants; add `elif book == 3:` block
- [ ] **Copy resize_to_kdp.ps1** to `MANUSCRIPT/book_3/IMAGES/` and update paths
- [ ] **Confirm or decide** open world-building questions that Book 3 depends on (Michael interdict, gate mechanics, Liaigh status)
- [ ] **Lock Book 3 detailed outline** — Beat-by-beat scene breakdown using architecture doc as skeleton

---

## PRIORITY 6 — Canon Maintenance

- [ ] **SSOT_v3_MASTER.md** — Incorporate any new facts from Book 2 Ch13–14 drafting (Josephite ops, Stewart Island safehouse, Azazel acoustic fingerprint captured by Mo Chrá)
- [ ] **Watcher/Nephilim dossier updates** — Ensure entities encountered in Book 2 endgame have current dossier entries
- [ ] **Clean TODO.md** — The current TODO.md has accumulated HITL gates and theological flags mixed with completed Midjourney tasks. Archive or reorganize once resolved.

---

## Reference: Files to Know

| File | Purpose |
|------|---------|
| `Start-TNCSwarm.ps1` | Boot-time swarm startup (registered as scheduled task) |
| `REFERENCE/COMBAT_STYLE_GUIDE.md` | Mandatory action/combat style framework |
| `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md` | Locked architecture for Books 3–5 |
| `WORLDBUILDING/ENDGAME_FATES.md` | Character fates (Option B locked) |
| `WORLDBUILDING/FIVE_BOOK_STRUCTURE.md` | Series-level structure |
| `MANUSCRIPT/book_2/SESSION_NOTES/SESSION_7_STATUS.md` | Latest Book 2 session status |
| `.github/copilot-instructions.md` | Copilot canon authority + combat guide |
