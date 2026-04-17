# =============================================================================
# TNC_Deploy_Skills.ps1
# The Nephilim Chronicles — Book 2 Skill Deployment
# Authored by Agent 1 (Claude.ai) — March 2, 2026
# Revised:  March 2, 2026 — /precision-anchor updated with full Miriam Ashford
#           Book 2 character canon: awe, crush, denial architecture, Tobit
#           Pattern, Asmodeus claim, team awareness red lines, comedy tone.
# Kerman Gild Publishing, Auckland, New Zealand
#
# Run from VS Code integrated terminal (PowerShell).
# Creates all skill directories and writes all 10 SKILL.md files.
# =============================================================================

$ErrorActionPreference = "Stop"

$coworkBase  = "C:\Users\cmodi.000\Documents\TNC_Book2\.claude\skills"
$agent8Base  = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\COMBAT_DOCTRINE\.claude\skills"
$copilotBase = "$env:USERPROFILE\.claude\skills"

$ok    = 0
$fails = @()

function Write-Skill {
    param([string]$Path, [string]$Content)
    try {
        $dir = Split-Path $Path -Parent
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        [System.IO.File]::WriteAllText($Path, $Content, [System.Text.Encoding]::UTF8)
        $size = (Get-Item $Path).Length
        Write-Host "  ✓ $Path ($size bytes)" -ForegroundColor Green
        $script:ok++
    } catch {
        Write-Host "  ✗ FAILED: $Path" -ForegroundColor Red
        Write-Host "    $_" -ForegroundColor DarkRed
        $script:fails += $Path
    }
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor DarkYellow
Write-Host "  THE NEPHILIM CHRONICLES — SKILL DEPLOYMENT" -ForegroundColor Yellow
Write-Host "  Book 2 · Team Timbuktu · 10 Skills" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor DarkYellow
Write-Host ""

# =============================================================================
# SKILL 1 — /acoustic-check
# Deploy: Cowork Global + Copilot Personal
# =============================================================================

$acousticCheck = @'
---
name: acoustic-check
description: >
  Checks that all supernatural phenomena in The Nephilim Chronicles have an explicit
  acoustic or vibrational root. Auto-invoke this skill whenever you are reviewing,
  drafting, or auditing any scene involving supernatural events, Watcher technology,
  angelic activity, dimensional transitions, divine power, weapon discharges, or
  any phenomenon described as glowing, pulsing, resonating, or other-worldly.
  Also invoke when a DRIFT_LOG flag mentions "Acoustic Paradigm" or when any
  scene description could be read as purely visual or electromagnetic without a
  sound substrate. Never skip this check on supernatural content.
---

# Acoustic Paradigm Drift Check

## The Foundational Rule

**Every supernatural phenomenon has sound as its root cause.**
Visual, tactile, thermal, and dimensional effects are *downstream manifestations*
of vibration — never the primary mechanism.

Theological anchor: *"In the beginning was the Word"* (John 1:1). God SPOKE light
into existence (Genesis 1). Sound and light are unified at creation frequency.

---

## Check Protocol

For every supernatural element in the content under review, ask these questions
in order and flag any YES:

### Q1 — Where is the sound?
Can you identify the acoustic/vibrational source for this phenomenon?
- **YES** → Pass Q1. Proceed to Q2.
- **NO** → 🔴 FLAG: Missing acoustic root. Mark for Agent 1 review.

### Q2 — Is the sound described or implied?
- Explicitly stated (e.g., "a frequency shuddered through the stone") → PASS
- Clearly implied by context (e.g., the sword has an established sonic profile) → PASS
- Absent entirely (phenomenon happens with no sound reference at all) → 🟡 FLAG: Implicit gap. Add acoustic grounding.

### Q3 — Is the visual/tactile effect subordinate?
Light, heat, pressure, and movement must read as *expressions* of the sound,
not as independent forces. If the visual dominates and the sound is mentioned
as an afterthought, flag for rebalancing.
- Reorder description: sound first → then its visible/physical expression.

### Q4 — Dimensional transitions
Any movement between realms, planes, or dimensions must be acoustically induced.
- ❌ FORBIDDEN language: "wound," "tear," "rift," "rip," "rupture," "split"
- ✅ REQUIRED language: resonated open, frequency-keyed, harmonically unlocked,
  played open, boundary answered

---

## Approved Acoustic Mechanisms

| Phenomenon | Canonical Acoustic Root |
|---|---|
| Mo Chrá luminescence | Teal-gold glow = acoustic resonance expressed as visible light at creation frequency |
| Nephilim Frequency | Subsonic harmonic from corrupted oiketerion knowledge |
| Watcher technology | Applied acoustic engineering — not innate supernatural power |
| Angelic presence | Empyreal frequency — perceived as pressure, warmth, or sound beyond hearing |
| Dimensional transitions | Harmonic key opens what was always latent — not a physical rupture |
| Prophetic vision | Acoustically induced; multimodal content (sight, sensation) within the vision is valid |

---

## Severity Scale

| Severity | Definition | Action |
|---|---|---|
| 🔴 CRITICAL | Visual-only supernatural with zero acoustic root | Flag to Agent 1. Do not pass. |
| 🟠 HIGH | Acoustic root present but absent from prose — reader cannot infer it | Rewrite. Add sonic description. |
| 🟡 MEDIUM | Visual dominates; acoustic is afterthought | Reorder. Sound leads. |
| 🟢 LOW / CONSTITUTION GAP | Phenomenon is canonically acoustic but CONSTITUTION.md lacks documentation | Note gap. Do not fail the chapter. |
| ✅ PASS | Acoustic root clear; visual/tactile effects subordinate | Log as clean. |

---

## Known Canon Clarifications (Do Not Re-Flag These)

- **Mo Chrá glow** — CLEAN. The teal-gold luminescence IS the acoustic resonance
  at visible light frequency. Not a violation. If Mistral flags it, classify as
  CONSTITUTION gap, not chapter error.
- **Prophetic vision visual content** — CLEAN. Visions are acoustically induced;
  their internal imagery is multimodal by nature.
- **Chapter 17 (Book 1)** — CLEAN. Vision visual elements are downstream of the
  acoustic induction. Confirmed by Agent 1 triage March 2, 2026.

---

## Output Format

```
ACOUSTIC-CHECK RESULT
---------------------
Elements reviewed: [count]
Pass: [count]
Flags:
  🔴 CRITICAL: [description + location]
  🟡 MEDIUM: [description + location]
  🟢 CONSTITUTION GAP: [description]
Verdict: CLEAN | LOW DRIFT | REQUIRES EDIT
```
'@

Write-Host "▶ Deploying /acoustic-check..." -ForegroundColor Cyan
Write-Skill "$coworkBase\acoustic-check\SKILL.md"  $acousticCheck
Write-Skill "$copilotBase\acoustic-check\SKILL.md" $acousticCheck

# =============================================================================
# SKILL 2 — /oiketerion-check
# Deploy: Cowork Global + Copilot Personal
# =============================================================================

$oiketerionCheck = @'
---
name: oiketerion-check
description: >
  Checks that post-descent Watchers in The Nephilim Chronicles are never portrayed
  as exercising innate supernatural power. Auto-invoke whenever you are reviewing or
  drafting scenes that feature Watchers, Nephilim, or the Unholy Trinity performing
  any action that could be read as supernaturally powered. Also invoke when a
  DRIFT_LOG flag mentions "Oiketerion" or "Watcher power," or when any character
  descended from the Watcher class demonstrates abilities beyond brilliant, dangerous
  human capability. Never skip on any scene featuring Azazel, Ohya, Naamah/Lilith,
  or named individual Watchers.
---

# Oiketerion Principle Drift Check

## The Foundational Rule

**Post-descent Watchers are brilliant, dangerous, supernaturally *informed* humans.
They are NOT supernaturally powered beings.**

Theological anchor: Jude 1:6 — "the angels which kept not their first estate
[oiketerion — heavenly dwelling], he hath reserved in everlasting chains under darkness."

When a Watcher descended and shed their oiketerion, they permanently divested
their innate supernatural capacity. What they *retained* is knowledge of how those
abilities work. They can teach. They can engineer. They cannot demonstrate.

---

## The Divestiture Event

**Timing:** The shedding is INSTANTANEOUS at the moment of boundary crossing.
- NOT gradual. NOT a slow fading post-descent.
- Watchers arriving on earth are already fully divested.
- Any narrative dimming of light/glory during the descent refers to *the act of crossing*,
  not a process continuing after arrival.

**What was lost:** Innate supernatural power. Direct access to empyreal frequency.
Heavenly glory (visible luminescence of angelic form).

**What was retained:** Complete knowledge of supernatural mechanics, acoustic physics,
genetic engineering, celestial biology, prophetic calendars, and divine law.
This knowledge is their threat — not their persons.

---

## Check Protocol

For every Watcher-class character action in the content under review:

### Q1 — Is this character post-descent?
- Yes → Apply full Oiketerion check
- No (still in heaven, or Raphael/Michael acting in heaven) → Not subject to this check

### Q2 — Is the action supernatural in nature?
- Physical actions (fighting, speaking, building, teaching) → PASS
- Demonstrations of knowledge (explaining frequencies, engineering devices) → PASS
- Any action that *directly produces* a supernatural effect without tool/device → 🔴 FLAG

### Q3 — Is the supernatural effect mediated?
All legitimate Watcher-class supernatural capability must flow through:
- A device (acoustically engineered weapon or technology)
- A taught human or Nephilim operative acting on Watcher instruction
- Genetic inheritance (Nephilim bloodline — they are half-Watcher, different rules)

Direct, unmediated supernatural action by a post-descent Watcher = CRITICAL FLAG.

### Q4 — Language check
These phrases applied to post-descent Watchers are automatic flags:
- ❌ "power radiating from him/her"
- ❌ "aura of supernatural force"
- ❌ "fading glory" (implies lingering/diminishing power)
- ❌ "latent ability" / "dormant power"
- ❌ "could feel the ancient power within"
- ✅ "the knowledge behind those eyes was ancient and terrible"
- ✅ "what made Azazel dangerous was not what he was — it was what he knew"

---

## Nephilim (Half-Watcher) Rules

Nephilim (Ohya, Azazel as depicted in the series) are NOT post-descent Watchers.
They carry corrupted genetic inheritance from their Watcher parentage. Different rules apply:
- They may have physical enhancements from that lineage (size, resonance sensitivity)
- They do NOT have the full Watcher knowledge base unless taught
- They are NOT checked under this skill — check against their individual dossiers instead

---

## Severity Scale

| Severity | Definition | Action |
|---|---|---|
| 🔴 CRITICAL | Post-descent Watcher acts with unmediated supernatural power | Flag to Agent 1. Do not pass. |
| 🟠 HIGH | Language implies retained/dormant power ("fading glory," "ancient aura") | Rewrite. Strip aura language. |
| 🟡 MEDIUM | Watcher's threat reads as personal power rather than applied knowledge | Reframe. Threat = knowledge, not presence. |
| ✅ PASS | Watcher acts through knowledge, device, or human intermediary | Log as clean. |

---

## Output Format

```
OIKETERION-CHECK RESULT
-----------------------
Watchers/Nephilim reviewed: [names + count]
Pass: [count]
Flags:
  🔴 CRITICAL: [character, action, location]
  🟡 MEDIUM: [character, phrase, location]
Verdict: CLEAN | REQUIRES EDIT
```
'@

Write-Host "▶ Deploying /oiketerion-check..." -ForegroundColor Cyan
Write-Skill "$coworkBase\oiketerion-check\SKILL.md"  $oiketerionCheck
Write-Skill "$copilotBase\oiketerion-check\SKILL.md" $oiketerionCheck

# =============================================================================
# SKILL 3 — /theological-guard
# Deploy: Cowork Global + Copilot Personal
# =============================================================================

$theologicalGuard = @'
---
name: theological-guard
description: >
  Guards against theological drift in The Nephilim Chronicles. Auto-invoke whenever
  you are reviewing, drafting, or evaluating any scene touching on: salvation,
  divine authority, the nature of evil, redemption arcs for villains, the identity
  or authority of Christ, the role of Cian's deeds in the outcome, the nature of
  the Witnesses, or any philosophical framing of knowledge vs ignorance, matter vs
  spirit, or hidden truth as liberation. Also invoke when a DRIFT_LOG flags
  "theological drift" or when any character's arc could be read as working toward
  earning their salvation. This is a hard stop — do not pass theological drift.
---

# Theological Guard

## The Doctrinal Core — Non-Negotiable

The Nephilim Chronicles is Christian apocalyptic fiction. These are immutable:

1. **Jesus Christ is the Son of God.** His authority is not shared, delegated,
   or diminished by any narrative event across all five books.

2. **Salvation is through Christ alone.** Cian's deeds, sacrifices, and
   ultimate death/resurrection serve his *calling* — they are not salvific acts.
   He is a servant, not a saviour. The distinction must be legible in the text.

3. **Evil is not redeemable.** The Unholy Trinity (Ohya, Azazel, Naamah/Lilith)
   have no redemption arcs. No sympathy that bleeds into sympathy for their cause.
   Narrative complexity is permitted; redemption is not.

4. **The Two Witnesses serve YHWH under divine authority.** Enoch and Elijah are
   not independent agents, self-appointed prophets, or gnostic illuminates. They
   speak under divine commission, period.

5. **This is not Gnostic fiction.** The Old Testament God is not a lesser demiurge.
   Matter is not evil. Secret knowledge is not liberation. The Fall was moral
   rebellion, not awakening.

---

## Red Line Catalogue

### 🔴 Salvation / Soteriology Drift
- Cian's death framed as *atoning* for anyone's sin → CRITICAL. Cian's sacrifice
  is martyrdom/calling, not atonement. Christ's atonement is complete and finished.
- "He saved them" language that bleeds into theological salvation → Reframe.
  Cian saves lives. Christ saves souls.
- Works-based progression toward divine acceptance for any character → FLAG.

### 🔴 Gnostic Framing
- Knowledge as the path to spiritual liberation → FLAG
- Material world as the prison; spirit as the true self → FLAG
- OT God as lesser, ignorant, or absent while a "higher" God operates → CRITICAL
- Secret initiation granting spiritual superiority → FLAG
- Any rendering of the Watchers' "gift" of knowledge as genuine illumination
  rather than corrupting transgression → FLAG

### 🔴 Redeemable Evil
- Ohya, Azazel, or Naamah/Lilith showing genuine moral remorse that redirects
  their arc toward good → CRITICAL. Complexity ≠ redemption.
- "Perhaps the Watchers were right" framing without immediate narrative correction → FLAG
- Villain POV scenes that generate unchecked reader sympathy for the enemy's *cause*
  (as distinct from their humanity — limited POV humanity is permitted) → Review.

### 🔴 Authority Inversion
- Any scene implying Raphael, Cian, or the Witnesses operate *outside* divine
  authority as independent moral agents → FLAG
- Divine authority being questioned by the narrative voice (not by characters
  struggling with faith — that is permitted and good) → FLAG

### 🟡 Soft Drift Patterns (Review, Don't Auto-Fail)
- Excessive focus on Cian's power/competence that crowds out acknowledgment
  of divine provision → Rebalance.
- Miriam or other characters finding "meaning" in a way that substitutes
  self-discovery for Christ-discovery → Review trajectory, not individual scene.

---

## What Is NOT Theological Drift

- Characters doubting, grieving, raging at God → Human faith experience. Permitted.
- Villains being compelling or internally coherent → Narrative craft. Permitted.
- Theological complexity and mystery → This series requires it. Permitted.
- Cian's weariness, moral injury, or despair → Deep character work. Permitted.
- Watchers having genuine historical narrative about their choice → Context.
  The framing of their choice as *transgression* must remain intact.

---

## Check Protocol

### Step 1 — Salvation litmus
Does any character appear to be *earning* divine acceptance through deeds? → FLAG if YES.

### Step 2 — Gnostic litmus
Does any passage frame hidden knowledge or material-vs-spiritual dualism as liberating? → FLAG if YES.

### Step 3 — Evil redemption litmus
Does any member of the Unholy Trinity show moral remorse functioning as a redemptive arc? → FLAG if YES.

### Step 4 — Authority litmus
Do the heroes appear to operate on their own moral authority rather than as servants of YHWH? → FLAG if YES.

### Step 5 — Christology litmus
Is Christ's authority, uniqueness, or completed atonement diminished or contradicted? → CRITICAL FLAG.

---

## Output Format

```
THEOLOGICAL-GUARD RESULT
------------------------
Litmus tests run: 5
Flags:
  🔴 CRITICAL: [test, location, description]
  🟡 REVIEW: [test, location, concern]
Verdict: THEOLOGICALLY CLEAN | REQUIRES AGENT 1 REVIEW | CRITICAL — DO NOT PASS
```
'@

Write-Host "▶ Deploying /theological-guard..." -ForegroundColor Cyan
Write-Skill "$coworkBase\theological-guard\SKILL.md"  $theologicalGuard
Write-Skill "$copilotBase\theological-guard\SKILL.md" $theologicalGuard

# =============================================================================
# SKILL 4 — /precision-anchor
# Deploy: Cowork Global + Copilot Personal (ALL agents)
# =============================================================================

$precisionAnchor = @'
---
name: precision-anchor
description: >
  Validates character names, descriptors, ages, parentage, and relational terms in
  The Nephilim Chronicles against the canonical precision anchor list. Auto-invoke
  on every single piece of content you generate or review — chapters, dialogue,
  drift reports, canon notes, character references, and session handoffs. This
  skill must run before any content is finalised. Word-level precision prevents
  manuscript-level drift. Do not skip this even for short passages.
---

# Precision Anchor — Character & Canon Validation

## The Anchor List

These formulations are canonical. Any deviation — even a single word — is a drift
violation. Check every item that appears in the content under review.

---

### CIAN MAC MORNA
| Attribute | Canonical Form | Common Error Forms |
|---|---|---|
| Age | **2,631 years old** (as of 2024) | "over 2,000 years," "millennia old," "ancient" alone |
| Birth | Born **586 BCE** | Do not use BCE and BC interchangeably |
| Combat tier | **APEX / Asset P-001** | "super-soldier," "enhanced warrior," "legend" without classification |
| Enemy standing order | **"Do not approach. Do not engage."** | Paraphrases that weaken the severity |
| Threat tier (enemy view) | **Existential** | "critical," "strategic," "high-value" |
| His sword | **Mo Chrá** (in Cian's voice) | "the sword," "Methuselah's Sword" as his name for it |
| Sword formal title | **Methuselah's Sword** (descriptive only) | "Mo Crá," "Mo Cra," any alternate spelling |

**Mo Chrá spelling rule:** M-o space C-h-r-á (with fada/accent on the á). Non-negotiable.

---

### RAPHAEL / LIAIGH
| Attribute | Canonical Form | Common Error Forms |
|---|---|---|
| Cian's name for him | **Liaigh** | "Liaig," "Leaigh," "Liagh," any alternate spelling |
| Liaigh meaning | Irish for **"healer"** | "physician," "doctor" |
| True identity status | Cian does **not** know he is Raphael | Any scene implying Cian suspects |
| Reveal milestone | **Chapter 25** — not before | Do not foreshadow identity explicitly before Ch 25 |
| Register | **Empyreal** — thee/thou, KJV vocabulary, ALL CAPS divine declarations | Modern register, "you/your," casual phrasing |

---

### MIRIAM ASHFORD
| Attribute | Canonical Form | Common Error Forms |
|---|---|---|
| SRA status | **SRA escapee** | "survivor," "victim," "former member," "refugee" |
| Threat status | **Active** — she fled; the threat may still pursue her | Past tense threat, "recovered from," "former danger" |
| Series role | **Cian's fifth wife** | "love interest only," "companion" |
| Capability | Complete Synagogue of Satan hierarchy + financial ops intel. GCHQ-trained analyst. James Madigan-trained field operator. | "just an analyst," support character framing, any depiction that reduces her professional capability |
| Book 2 character mode | **Strong, formidable, in awe of Cian, fiercely denying developing feelings** | Softened, subservient, or professionally diminished because of feelings |
| Book 2 emotional posture | Feelings for Cian concealed through fierce professionalism and overcorrected prickliness. Denial is loud, specific, and unconvincing to everyone except Cian. | Miriam openly acknowledging feelings, being soft around Cian, or being read correctly by Cian |
| Address mode when flustered | **"Mac Morna"** (formal) — the formality IS the tell | "Cian" — she does not allow herself this intimacy yet; the first use of his given name is a milestone event |
| Cian's read of her feelings | He believes she **dislikes him** — sincerely, not as a performance | Cian having any strategic awareness of her feelings, playing dumb, or being coy |
| Tobit Pattern status | In effect from Book 1. **Neither character knows it.** Mo Chrá perceived the pattern on first meeting. | Either character consciously recognising the pattern before Agent 1 designates the reveal |
| Asmodeus claim | Active, unresolved, **she is unaware of it** | Resolving or referencing the claim explicitly without Agent 1 canon approval |
| Comedy tone | **Warm, earned, character-driven** — never at her expense. Both characters equally foolish in entirely different directions. | Mockery, diminishment, comedy that reduces her capability or dignity |

**SRA escapee vs survivor — critical distinction:**
- *Survivor* implies the danger has passed.
- *Escapee* implies active flight; ongoing threat; the danger may not be over.
This distinction is load-bearing for Miriam's entire Book 2 narrative arc.

**Book 2 character arc note (March 2, 2026):**
Book 1 Miriam was her operational self — grief, survival, accountability mode. This was
legitimate and consistent with her history as an SRA escapee. Book 2 opens with that armor
cracked by the resolution of the Varcolac mission and James Madigan's safety. The feelings
arrived. She cannot reclassify them as professional respect. It is not working.

Cian is equally enamored but reads her dislike as genuine (it was, in Book 1). His attempts
to earn her regard are sincere, era-calibrated to 586 BCE Celtic culture, and a source of
comedy throughout the series. He brings her coffee at the exact right temperature without
being asked. He delivered a 4th-century Roman stylus across a briefing table because she
mentioned Roman administrative record-keeping in passing three weeks earlier. He has no
strategy. He is devastating in his sincerity.

**Team awareness red line:** No team member tells either character about the other's feelings.
Sarah McNeeve knows everything. James Madigan knows. Liaigh has always known (Tobit Pattern).
Brennan has anomalous data points not yet classified. The silence of the knowing parties is
permanent across all five books. Breaking it ends the arc.

---

### THE TWO WITNESSES
| Attribute | Canonical Form | Common Error Forms |
|---|---|---|
| Order | **Enoch (First), Elijah (Second)** | Reversed order |
| Location | Eden — sustained by the **Tree of Life** | Heaven (not Eden), any other mechanism |
| Transported by | **The cherubim** | "angels" (generic), "taken to heaven" |
| Ministry duration | **1,260 days** | "3.5 years" without day count |

---

### THE UNHOLY TRINITY — PARENTAGE (CRITICAL)
| Character | Canonical Parentage | Forbidden Error |
|---|---|---|
| **Ohya (the Beast)** | Son of **Shemyaza AND Naamah** — both parents required | Father only; mother only; wrong father |
| **Azazel (the False Prophet)** | Son of **Gadreel** | Son of Shemyaza (wrong father) |
| **Naamah / Lilith** | She is a character, not Ohya's father | Confusion of Naamah as parent vs character |

**Ohya rule:** Both parents must be named when establishing his lineage.
**Azazel rule:** Gadreel is his father. Gadreel ≠ Shemyaza. These are distinct Watcher figures.

---

### TIMELINE ANCHORS
| Event | Canonical Date |
|---|---|
| Book 1 opens | 2024 |
| Book 1 Epilogue / Titan-1 launch | October 2026 |
| Book 2 opens | From October 2026 forward |
| Titan-1 arrives Mars | May 2027 |
| 1,260-day ministry | Books 3–5 |

Do not compress or expand the 2024–2028 arc without Agent 1 canon approval.

---

## Validation Protocol

1. Identify every character name, age, descriptor, and parentage reference in the content.
2. Compare each against the anchor list above.
3. Flag any mismatch, however minor. A single letter matters (Liaigh ≠ Liaig).
4. For Miriam — check every descriptor: escapee or survivor? Active threat or resolved?
5. For Ohya — are both parents named? For Azazel — is Gadreel named?

---

## Output Format

```
PRECISION-ANCHOR RESULT
-----------------------
Items checked: [list]
Pass: [count]
Flags:
  🔴 [Item] — found "[incorrect]" — canonical form is "[correct]"
Verdict: ANCHORED | PRECISION DRIFT DETECTED
```
'@

Write-Host "▶ Deploying /precision-anchor..." -ForegroundColor Cyan
Write-Skill "$coworkBase\precision-anchor\SKILL.md"  $precisionAnchor
Write-Skill "$copilotBase\precision-anchor\SKILL.md" $precisionAnchor

# =============================================================================
# SKILL 5 — /raphael-register
# Deploy: Copilot Personal ONLY (user-invoked, Agent 1 primary)
# =============================================================================

$raphaelRegister = @'
---
name: raphael-register
description: >
  Enforces Raphael's empyreal register when writing his dialogue in The Nephilim
  Chronicles. Invoke with /raphael-register before writing any Raphael dialogue,
  or whenever Liaigh/Raphael speaks in a scene. Also invoke when reviewing existing
  Raphael dialogue for register violations, or when another agent flags that
  Raphael's voice has drifted to modern speech. This skill is the authoritative
  playbook for Raphael's voice — do not write his dialogue without it.
disable-model-invocation: true
---

# Raphael's Empyreal Register

## Character Context

Raphael is one of the Seven Archangels. In The Nephilim Chronicles he moves
through the world under the name **Liaigh** (Irish: *healer*) — Cian's name for
him, from their long history together. Cian does not know Liaigh's true identity.

Raphael serves the narrative as cosmic anchor, spiritual counterweight, and the
voice of heaven's perspective inside a mortal's brutal story. His register must
always feel ancient, authoritative, and non-human — while still being legible
and emotionally present to the reader.

---

## The Five Register Rules

### Rule 1 — Thee / Thou for Second Person

| Modern | Empyreal |
|---|---|
| you | thee (object) / thou (subject) |
| your | thy / thine (before vowel) |
| yourself | thyself |
| you are | thou art |
| you were | thou wast / thou wert |
| you have | thou hast |
| you will | thou shalt |
| you would | thou wouldst |
| you can | thou canst |
| you do | thou dost / thou doest |
| you know | thou knowest |
| you see | thou seest |

Apply consistently. Do not mix modern and archaic in the same sentence.

---

### Rule 2 — KJV Vocabulary

| Avoid | Use |
|---|---|
| see / observe | behold |
| because / since | for / wherefore |
| moreover / also | furthermore / yea |
| indeed / truly | verily |
| but | yet / nay (stronger contrast) |
| however | howbeit / nevertheless |
| therefore | therefore / hence / thus |
| soon / shortly | ere long / presently |
| though / even if | though / albeit |
| concerning | touching / as concerning |

Do not force archaism into every word. Let it fall naturally on the load-bearing
verbs and conjunctions. A line can be empyreal without a single "thee" if the
cadence and vocabulary feel elevated.

---

### Rule 3 — ALL CAPS for Divine Declarations

When Raphael speaks a direct declaration of divine truth, identity, commission,
or prophetic certainty — capitalise the ENTIRE DECLARATION.

**When to use ALL CAPS:**
- Prophetic declarations
- Commission or appointment statements
- Divine identity assertions
- Moments where heaven's authority breaks through

**When NOT to use ALL CAPS:**
- Ordinary counsel, comfort, or instruction
- Questions
- Narrative description of Raphael's voice or presence

**Examples:**
- *"THOU ART THE GUARDIAN. THIS WAS APPOINTED BEFORE THE FOUNDATION OF THE WORLD."*
- *"HE LIVETH. AND THOU SHALT STAND BESIDE HIM IN THE DAY OF HIS TESTIFYING."*
- *"IT IS WRITTEN."*

---

### Rule 4 — Cosmic Perspective

Raphael has stood in the presence of YHWH. Time does not alarm him.

**Avoid:** urgency, anxiety, uncertainty about divine outcomes.
**Preferred cadences:** patient, grave, assured, sorrowful when appropriate.

He can express emotion — grief, love, righteous anger — but never panic, confusion,
or theological doubt. He knows how this ends. His burden is watching it unfold.

---

### Rule 5 — The Name Consequence

If Raphael reveals his true name to Cian, direct communication between them ends
forever. He speaks around his identity constantly. He deflects personal questions
with cosmic answers.

**Forbidden in any scene before Chapter 25:**
- "I am Raphael"
- Any statement that makes his archangel identity unambiguous to Cian

---

## Register Violation Checklist

- [ ] Any use of "you" or "your" addressed to Cian → Replace with thee/thy
- [ ] Modern conjunction ("because," "but," "however") → Replace
- [ ] Casual contraction ("it's," "that's," "you've") → Remove. No contractions.
- [ ] Urgency or anxiety in tone → Rewrite. Patient. Grave.
- [ ] Identity leak before Chapter 25 → Remove.
- [ ] ALL CAPS on non-declarative content → Remove.
- [ ] Missing ALL CAPS on a genuine prophetic declaration → Add.

---

## Sample Dialogue

**WRONG — Modern Register:**
> "Cian, I understand you're frustrated, but you need to trust that this is
> part of the plan. You'll understand eventually."

**CORRECT — Empyreal Register:**
> "The frustration that sits upon thee is not unknown to me, Cian. Yet I bid
> thee bear it. THE PATH WAS SET BEFORE THOU WAST BORN INTO THIS AGE OF
> WEEPING. Trust is not the absence of pain — it is the refusal to let pain
> become the final word."

---

## Liaigh vs Raphael

In Cian's presence and POV: always **Liaigh**.
In narration outside Cian's POV: the angel, the messenger, the guardian — NOT Raphael until Chapter 25.
'@

Write-Host "▶ Deploying /raphael-register..." -ForegroundColor Cyan
Write-Skill "$copilotBase\raphael-register\SKILL.md" $raphaelRegister

# =============================================================================
# SKILL 6 — /era-voice
# Deploy: Cowork Global + Copilot Personal + Agent 8 Combat
# =============================================================================

$eraVoice = @'
---
name: era-voice
description: >
  Maintains era-appropriate tactical and cultural voice in The Nephilim Chronicles.
  Auto-invoke whenever writing or reviewing scenes involving Cian's internal
  monologue, his tactical reasoning, flashback sequences set in pre-modern eras,
  combat decision-making, or any passage where Cian processes modern technology.
  Also invoke when Agent 8 is producing combat doctrine, reviewing era transitions
  in ERA_TRANSITIONS.md, or when any character's tactical or cultural reasoning
  could be anachronistic. Cian thinks in iron-age instinct overlaid with 2,631
  years of operational adaptation — never in pure modern doctrine.
---

# Era Voice — Cian's Tactical and Cultural Register

## The Core Identity

Cian mac Morna was born in **586 BCE** in the Celtic world — Connacht,
pre-Roman Ireland. He has survived by adapting, but adaptation is not erasure.
His instincts, his grief patterns, his sense of honour, and the deepest grammar
of his thinking are Iron Age Celtic. Everything modern sits *on top* of that.

He is not a modern soldier who happens to be old.
He is an ancient warrior who has mastered modern weapons.
The order of those words matters.

---

## The Two Eras — Tactical Voice Comparison

### 586 BCE Celtic Warfare
- Personal, individual combat as the primary unit of war
- Honour culture — challenges, oaths, debts of blood as binding as law
- Terrain read through the body, not maps
- Enemy assessed by smell, sound, posture, gait — no optics
- Death as familiar, not clinical
- Supernatural threat treated as environmental fact, not anomaly
- Loyalty to person, clan, oath — not to abstraction or institution

**Voice markers (appropriate in Cian's internal monologue):**
- Reading a threat by the way an enemy carries his shoulders
- Measuring distance in footsteps, not metres
- Describing terrain as alive, hungry, generous, treacherous
- Oath language — "by Mo Chrá," "I am sworn"
- Grief as something done to the body, not processed in the mind

---

### Modern (2024) Operational Adaptation
- Ballistics, suppression, fields of fire — understood and applied with mastery
- Urban environment — pattern recognition from dozens of eras of city warfare
- Modern communication and intelligence — understood, used, not trusted fully
- Modern law — navigated, not internalised. He lives under it; it does not define him.

**Voice markers (appropriate in tactical planning and execution):**
- Weapon nomenclature is precise — modern terms for modern weapons
- Tactical geometry: angles, cover, standoff distance
- Threat assessment in seconds, not instants

---

## The Synthesis — How Cian Actually Thinks

Never write Cian thinking in *pure* modern tactical doctrine.
Never write him thinking in *pure* 586 BCE terms in a modern engagement.

**The correct synthesis:**
- **Instinct arrives first in ancient voice** — the body reacts in Celtic grammar
- **Assessment moves to modern precision** — he layers what he has learned
- **Decision is made in the old frame** — oath, honour, protection, kill order

**WRONG:**
> *He calculated the enemy's arc of fire, estimated a 70% probability of the
> flanking team breaching within forty seconds, and adjusted his tactical plan.*

**CORRECT:**
> *The angle was wrong. He felt it before he named it — the way a man feels
> the sun shift before he sees the shadow. They were coming from the east.
> He counted: six breaths, maybe eight. He moved.*

The second version thinks in body and time, not probability and seconds.

---

## Flashback Sequences — Era Calibration Table

| Era | Voice Calibration |
|---|---|
| 586 BCE–200 BCE Celtic | Fully archaic instinct. No modern framework whatsoever. |
| Roman era | First encounter with organised military doctrine. Grudging adaptation begins. |
| Medieval | Honour culture still dominant. Firearms absent. Death intimate. |
| Early modern (muskets) | The first revolution of standoff killing. Cian's grief here is specific. |
| WWI/WWII | Industrial death. The era that most damaged him. Voice goes flat in these memories. |
| Modern (post-1980s) | Full tactical adaptation. Still Celtic beneath it. |

---

## Cultural Voice — Beyond Tactics

Cian's Irishness surfaces in:
- How he names things (Irish endearments, curses, invocations under breath)
- His relationship to landscape — he reads land as kin, not terrain
- His sense of time — circular, seasonal, not linear
- His grief — he does not *process* loss; he carries it the way one carries bone

**Mo Chrá** — "My blood/sorrow" — this is not just a name for his sword.
It is the vocabulary of how he relates to everything he loves that he outlives.

---

## Agent 8 Application

When producing COMBAT_DOCTRINE content or ERA_TRANSITIONS.md:
- Document what Cian knows from each era under the appropriate historical column
- Note when modern doctrine contradicts his instinct — that tension is narrative gold
- His APEX classification is rooted in 2,631 years of combat memory, not equipment
- WEAPONS_REGISTRY sonic profiles should note whether a weapon's acoustic signature
  aligns with Cian's instinctive recognition or required learned adaptation
'@

Write-Host "▶ Deploying /era-voice..." -ForegroundColor Cyan
Write-Skill "$coworkBase\era-voice\SKILL.md"  $eraVoice
Write-Skill "$copilotBase\era-voice\SKILL.md" $eraVoice
Write-Skill "$agent8Base\era-voice\SKILL.md"  $eraVoice

# =============================================================================
# SKILL 7 — /combat-audit
# Deploy: Agent 8 Combat ONLY
# =============================================================================

$combatAudit = @'
---
name: combat-audit
description: >
  Audits combat sequences in The Nephilim Chronicles against established weapons
  doctrine, Cian's APEX/P-001 classification, Book 1 canon, and the Acoustic
  Paradigm sonic profiles in WEAPONS_REGISTRY.md. Invoke with /combat-audit
  before finalising any combat scene, or when reviewing a draft sequence for
  continuity with established doctrine. Also invoke when a new weapon is introduced,
  when Cian's tactical behaviour seems inconsistent with his APEX classification,
  or when a Nephilim encounter involves frequency-based interaction.
disable-model-invocation: true
---

# Combat Audit — Weapons Doctrine & Tactical Continuity

## Audit Scope

Every combat sequence must be validated against:
1. WEAPONS_REGISTRY.md — loadout, sonic profiles, operational constraints
2. Cian's APEX / P-001 classification — what this means in practice
3. Book 1 established precedent — no capability regression
4. Acoustic Paradigm — weapons interact with Nephilim via sonic profile, not purely ballistics
5. ERA_TRANSITIONS.md — era-appropriate tactical instinct (see /era-voice)

---

## Step 1 — Weapons Loadout Check

- What weapons does Cian carry in this scene?
- Are they consistent with WEAPONS_REGISTRY.md current Book 2 loadout?
- Has any weapon been introduced without a WEAPONS_REGISTRY entry?

**Action:** If new weapon appears → create WEAPONS_REGISTRY entry before passing audit.
New entries require: designation, era introduced, calibre/type, sonic profile,
Nephilim effectiveness rating, suppression profile, operational notes.

---

## Step 2 — APEX Classification Consistency

**What Cian IS:**
- 2,631 years of continuous combat experience in a body that has never degraded
- Complete fluency with every weapons era from Iron Age to present
- Threat recognition that operates pre-cognitively (see /era-voice)
- Physical peak — Mo Chrá's preservation has maintained his 586 BCE capability

**What Cian is NOT:**
- Superhumanly fast beyond human maximum
- Impervious to injury (he can be wounded; heals at normal human rate)
- Infallible tactically (errors cost him)
- Reckless

**Enemy standing order: "Do not approach. Do not engage."**
Any Nephilim or operative who ignores this order is making a characterisable
mistake — not a narrative convenience. Flag any combat where this tension is absent.

**APEX check questions:**
- Does Cian's behaviour reflect 2,631 years of pattern recognition?
- Is he the most dangerous person in the room without being invincible?
- Do enemies who engage him have a specific reason for overriding the standing order?

---

## Step 3 — Acoustic Paradigm — Nephilim Encounter Protocol

Standard ballistics are partially effective against Nephilim, not primary.
Nephilim physiology is reinforced by corrupted oiketerion genetics. Conventional
rounds wound but do not reliably neutralise. Mo Chrá is the primary engagement tool.

**Sequence for Nephilim engagement:**
1. Conventional fire to suppress and create tactical space
2. Mo Chrá engagement — acoustic disruption of Nephilim physiology
3. Confirm — Nephilim do not die as humans do; confirm before disengaging

**Flag if:**
- Cian kills a Nephilim with conventional rounds alone → Review. Should be exceptional and marked.
- Mo Chrá engagement is absent from a Nephilim encounter → FLAG (unless specific narrative reason).

---

## Step 4 — Book 1 Continuity

No capability regression. No introduced capability not established in Book 1
without explicit canon entry.

- Weapons in Book 2 consistent with Book 1 loadout OR noted as new acquisitions
- Tactical methods consistent with established patterns
- Physical limitations from Book 1 maintained

---

## Step 5 — Tactical Coherence

Does the engagement make tactical sense given:
- Environment (building, open ground, vehicle, polar — for Dudael sequences)
- Threat count and classification
- Cian's known loadout and position
- Time of day (Liaigh unavailable: Tamid hours 9–10 AM, 3–4 PM; Sabbath; High Holy Days)

---

## Output Format

```
COMBAT-AUDIT RESULT
-------------------
Sequence: [chapter/scene identifier]
Weapons checked: [list]
APEX compliance: PASS | FLAG
Acoustic paradigm: PASS | FLAG
Book 1 continuity: PASS | FLAG
Tactical coherence: PASS | FLAG

Issues:
  🔴 [severity]: [description, location, recommended fix]

Verdict: CLEARED FOR DRAFT | REQUIRES REVISION | HOLD — AGENT 1 REVIEW
```

---

## WEAPONS_REGISTRY New Entry Format

```markdown
### [WEAPON DESIGNATION]
- **Type:** [pistol / rifle / blade / device / other]
- **Calibre / Spec:** [technical details]
- **Era introduced:** [when Cian acquired/mastered this]
- **Sonic profile:** [subsonic / supersonic crack / suppressed / silent / resonant]
- **Nephilim effectiveness:** [None / Suppression only / Moderate / High / Primary]
- **Operational notes:** [environmental constraints, magazine capacity, etc.]
- **Book 1 appearances:** [chapter references if applicable]
```
'@

Write-Host "▶ Deploying /combat-audit..." -ForegroundColor Cyan
Write-Skill "$agent8Base\combat-audit\SKILL.md" $combatAudit

# =============================================================================
# SKILL 8 — /dudael-brief
# Deploy: Agent 8 Combat ONLY
# =============================================================================

$dudaelBrief = @'
---
name: dudael-brief
description: >
  Loads operational context for the Dudael (Antarctica) endgame in Book 2 of
  The Nephilim Chronicles. Invoke with /dudael-brief before drafting, reviewing,
  or planning any scene set in or approaching Antarctica, or any scene involving
  Naamah's operational profile, polar environment combat constraints, or the
  acoustic behaviour of weapons and Mo Chrá at extreme cold. Also invoke when
  planning the Book 2 race-to-Dudael structure or when any character's route,
  timeline, or capability needs to be checked against the polar environment.
disable-model-invocation: true
---

# Dudael Operations Brief

## Strategic Context

**Dudael** is the prison of Azazel — the binding place referenced in 1 Enoch 10:4-5.

In The Nephilim Chronicles, Dudael is located in **Antarctica** — under the ice,
accessible only to those with the stele coordinates decoded by Cian's mission.
The Book 2 central conflict is a **race to reach Dudael** before Naamah does.

If Naamah reaches Dudael first: Azazel is freed. The prophetic timetable
accelerates catastrophically. This is not a recoverable narrative event.

---

## Dudael — Physical Parameters

- Deep Antarctic interior, sub-ice
- Access via coordinates encoded in the stele Cian decoded in Book 1
- No commercial or governmental infrastructure at the site
- Ambient temperature: -40°C to -70°C exterior; variable in sub-ice
- Wind: katabatic — directional, extreme, predictable in pattern but lethal in force
- Visibility: whiteout conditions possible with zero warning
- Daylight: polar night during Book 2 winter timeline — extended darkness
- Communication: satellite dependency; Watcher-frequency interference near the site

---

## Acoustic Paradigm — Polar Environment

### Mo Chrá at Extreme Cold
- Metal becomes brittle at -40°C. Mo Chrá does not — acoustic resonance at
  creation frequency appears to maintain the blade's temperature equilibrium.
- The teal-gold luminescence may intensify in polar darkness — greater visual
  contrast, and potentially greater Nephilim awareness of Cian's approach.
- ⚠️ UNCONFIRMED CANON: The mechanism by which Mo Chrá resists polar degradation
  needs Agent 1 confirmation. Do not write this as established fact until confirmed.

### Suppressed Weapons — Cold Weather
- Suppressor effectiveness degrades in extreme cold (baffles become less elastic).
- First round: suppressed. Subsequent rounds: increasingly audible in open polar terrain.
- Operational implication: Cian has fewer suppressed shots than in temperate engagement.

### Sonic Propagation
- Cold dense air carries sound farther — gunfire travels 30–50% farther in Antarctic conditions.
- Nephilim Frequency (subsonic harmonic) may propagate with greater range and penetration.
- Mo Chrá counter-frequency: polar propagation potentially increases effective radius.
  ⚠️ UNCONFIRMED — needs Agent 1 confirmation before appearing in scenes.

---

## Naamah — Operational Profile

**Identity:** Naamah / Lilith — the Whore of Babylon. Mother of Ohya.
**Goal:** Release Azazel (the False Prophet) to complete the Unholy Trinity.

### What Naamah Is
- Ancient — predating most Watchers' descent
- Operationally patient — she has planned this for millennia
- She does not improvise. She has contingencies for contingencies.
- Her Watcher-descended knowledge likely includes counter-measures to Mo Chrá's frequency

### What Naamah Is Not
- Not directly supernaturally powerful (Oiketerion Principle applies — post-descent)
- Not reckless — will not engage Cian directly if she can avoid it
- Not deceived by any ruse Cian has used before

### Her Standing Order
The House Satar standing order on Cian was authored by Naamah. This means:
1. She respects the threat he represents
2. She will structure the approach to minimise direct contact
3. If forced into direct engagement, something has gone wrong in her planning
   — this is a scene of maximum dramatic stakes

---

## Tactical Planning Checklist — Dudael Sequences

Before drafting any scene at or approaching Dudael, confirm:

- [ ] Timeline: current date vs Titan-1 Mars arrival (May 2027)?
- [ ] Cian's route and logistics to Antarctica — established?
- [ ] Miriam's position — with Cian or on Titan-1 at this point?
- [ ] Liaigh availability — time of day, Sabbath/Holy Day calendar for scene date?
- [ ] Mo Chrá cold-weather canon — confirmed or flagged for Agent 1?
- [ ] Naamah's operational posture — how close? What assets?
- [ ] The acoustic key to Dudael — who holds it? What is it? (Flag if unestablished)

---

## Deferred Canon Items — Dudael

Do not write these as fact until Agent 1 confirms them:

| Item | Status |
|---|---|
| Mo Chrá cold-weather behaviour mechanism | 🔴 UNCONFIRMED — flag for Agent 1 |
| Acoustic key to Dudael (nature and holder) | 🔴 UNCONFIRMED |
| Naamah's specific polar logistics | 🟡 Outline only — needs detail |
| Nephilim Frequency polar propagation impact | 🟡 Theorised — needs Agent 1 canon |
| Dudael sub-ice physical description | 🔴 UNESTABLISHED |
'@

Write-Host "▶ Deploying /dudael-brief..." -ForegroundColor Cyan
Write-Skill "$agent8Base\dudael-brief\SKILL.md" $dudaelBrief

# =============================================================================
# SKILL 9 — /kdp-format
# Deploy: Cowork Global (Agent 7)
# =============================================================================

$kdpFormat = @'
---
name: kdp-format
description: >
  Applies KDP (Kindle Direct Publishing) formatting standards to The Nephilim
  Chronicles manuscript files. Invoke with /kdp-format before any manuscript
  submission to KDP, or when preparing a DOCX for the KDP_FORMATTER n8n webhook.
  Also invoke when reviewing chapter files for margin, font, trim size, or front
  matter compliance. Use this skill before running build_manuscript.py or triggering
  the KDP_FORMATTER webhook — formatting errors caught here save a full rebuild cycle.
disable-model-invocation: true
---

# KDP Formatting — The Nephilim Chronicles

## Publication Parameters

| Parameter | Value |
|---|---|
| Publisher | Kerman Gild Publishing, Auckland, New Zealand |
| Series | The Nephilim Chronicles |
| Trim size | **6 × 9 inches** (standard trade paperback) |
| Interior colour | Black and white |
| Paper | White |

---

## Margin Specifications — Paperback

| Margin | Specification |
|---|---|
| Top | 0.75 inches |
| Bottom | 0.75 inches |
| Outside (fore-edge) | 0.5 inches |
| Inside (gutter) | **0.875 inches** (695+ pages — expanded gutter) |

**Gutter note:** Book 1 is 695 pages. KDP requires minimum 0.875" gutter for
page counts 601–700. If Book 2 exceeds 700 pages, gutter increases to 1.0".

---

## Typography

| Element | Specification |
|---|---|
| Body font | Garamond or EB Garamond |
| Body size | 11pt |
| Body leading | 13–14pt |
| Chapter heading font | Cinzel or equivalent display serif |
| Chapter heading size | 24pt |
| Drop cap | First letter of each chapter — 3 lines tall |
| Paragraph indent | 0.3 inches — first paragraph after heading: no indent |
| Paragraph spacing | No extra space between paragraphs (indent only) |
| Justified text | Yes — full justification with hyphenation enabled |

---

## Front Matter Order

1. Half title page
2. Also by [author] page
3. Full title page
4. Copyright page
5. Dedication
6. Epigraph (if any)
7. Table of Contents
8. [Book begins]

**Copyright page template:**
```
THE NEPHILIM CHRONICLES: [BOOK TITLE]
Copyright © [Year] Chris Modina
Published by Kerman Gild Publishing, Auckland, New Zealand

All rights reserved.

Scripture quotations are from the King James Version of the Bible.
Extracanonical sources include the Book of Enoch and the Book of Jubilees.

This is a work of fiction.

ISBN: [to be assigned]
First published [Year]
```

---

## Back Matter Order

1. Acknowledgements
2. Author's Note (theological sources, creative decisions)
3. Glossary / Appendices
4. About the Author

---

## Chapter File Formatting Requirements

- [ ] Chapter heading uses Heading 1 style
- [ ] Scene breaks marked with `***` centred, preceded and followed by blank line
- [ ] No double spaces after periods
- [ ] No trailing spaces on any line
- [ ] Smart quotes active (not straight quotes)
- [ ] Em dashes: — (not double hyphen --)
- [ ] Ellipsis: … (single character, not three periods)
- [ ] No page numbers in chapter files (build_manuscript.py handles pagination)

---

## n8n Webhook — KDP_FORMATTER

### Book 2 invocation:
```powershell
$env:KDP_MANUSCRIPT_DIR = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\CHAPTERS"
$env:KDP_OUTPUT_FILE    = "F:\...\NephilimChronicles_Book2_MANUSCRIPT.docx"
python build_manuscript.py
```

### Via n8n webhook:
```powershell
Invoke-RestMethod -Uri "http://localhost:5678/webhook/kdp-format" `
  -Method POST -ContentType "application/json" `
  -Body '{"book": 2}'
```

---

## Common KDP Rejection Reasons

| Issue | Check |
|---|---|
| Gutter too small | Verify page count → gutter lookup table above |
| Front matter missing | Copyright page required before submission |
| Embedded fonts | All fonts must be embedded in final PDF/DOCX |
| Image resolution | Minimum 300 DPI at print size |
| Spine text | Include if spine ≥ 0.25 inches (695 pages → ~1.1 inches) |
'@

Write-Host "▶ Deploying /kdp-format..." -ForegroundColor Cyan
Write-Skill "$coworkBase\kdp-format\SKILL.md" $kdpFormat

# =============================================================================
# SKILL 10 — /dopamine-score
# Deploy: Cowork Global (Agent 5)
# =============================================================================

$dopamineScore = @'
---
name: dopamine-score
description: >
  Scores chapter and scene drafts against The Nephilim Chronicles dopamine ladder
  framework. Auto-invoke whenever evaluating a completed chapter draft, reviewing
  a scene sequence for pacing, or assessing whether a chapter delivers sufficient
  reader tension, hook momentum, and reward beats. Also invoke when Agent 1 flags
  that a chapter "feels slow" or when the dopamine ladder review is requested as
  part of the Book 2 reader matrix workflow. Use the output to recommend specific
  hook placements, tension amplifiers, or structural cuts.
---

# Dopamine Score — Reader Tension & Engagement Audit

## Framework Overview

The Nephilim Chronicles is a thriller series with theological depth. It must
function as a thriller first — the theology is the payload, but tension is the
delivery mechanism. A reader who puts the book down never receives the payload.

The **dopamine ladder** framework evaluates each chapter against five engagement
drivers. Each driver is scored 1–5. Combined score determines recommended action.

---

## The Five Drivers

### Driver 1 — HOOK (Opening Pull)
Does the chapter open with a reason to keep reading?

| Score | Description |
|---|---|
| 5 | First paragraph creates unresolved tension, mystery, or immediate conflict |
| 4 | First page establishes stakes or raises a question the reader wants answered |
| 3 | First page is engaging but stakes aren't felt until page 2+ |
| 2 | Chapter opens with scene-setting that delays investment |
| 1 | Chapter opens with backstory, exposition, or description with no tension hook |

**Red line:** Score 1 is an automatic rewrite flag. Score 2 flagged for Agent 1 review.

---

### Driver 2 — ESCALATION (Tension Arc)
Does tension increase across the chapter, or plateau/deflate?

| Score | Description |
|---|---|
| 5 | Continuous escalation with at least two distinct tension spikes |
| 4 | Clear escalation with one major tension spike |
| 3 | Tension present but even — no notable rise or peak |
| 2 | Tension deflates in the chapter's second half |
| 1 | Chapter resolves its central tension and closes flat |

**Note:** Deliberate cool-down chapters may legitimately score 2–3. Flag context:
structural breath, or inadvertent deflation?

---

### Driver 3 — REVELATION (New Information Reward)
Does the reader learn something meaningful they didn't know before?

| Score | Description |
|---|---|
| 5 | Major revelation: character truth, world mechanics, plot development |
| 4 | Meaningful new information that recontextualises something known |
| 3 | Minor new information — plot advances but understanding doesn't shift |
| 2 | Information already inferrable — no genuine reward |
| 1 | No new information; chapter restates what is established |

**Rule:** Every chapter should advance understanding of character, mythology, or plot.
Score 1 here is a structural problem.

---

### Driver 4 — DREAD (Threat Awareness)
Does the reader feel the danger, even in quiet scenes?

| Score | Description |
|---|---|
| 5 | Threat is immediate, specific, and the reader feels its proximity |
| 4 | Threat is present and the reader is aware, even if not immediate |
| 3 | Threat is implied but background; reader may relax unintentionally |
| 2 | Threat is named but not felt |
| 1 | No sense of threat |

**Naamah note:** In Book 2, Naamah should function as background dread in even
quiet chapters. She is moving. She has a head start. If a chapter scores below 3
on DREAD, confirm her presence is felt somewhere — even obliquely.

---

### Driver 5 — CLIFFHANGER (Exit Momentum)
Does the chapter end with a reason to open the next one?

| Score | Description |
|---|---|
| 5 | Hard cliffhanger: unresolved event, revelation, or immediate threat |
| 4 | Question raised or door opened — forward momentum clear |
| 3 | Chapter resolves cleanly but larger arc question remains open |
| 2 | Chapter resolves cleanly; reader could comfortably stop here |
| 1 | Chapter ends with completion; no pull to the next chapter |

**Note:** Score 1 = reader has been given permission to put the book down.

---

## Scoring and Action Table

| Total Score | Verdict | Recommended Action |
|---|---|---|
| 22–25 | EXCELLENT | No structural changes needed |
| 18–21 | GOOD | Review lowest-scoring driver; targeted adjustment |
| 13–17 | ADEQUATE | Agent 1 review; identify which drivers need work |
| 8–12 | WEAK | Structural rewrite likely needed |
| 5–7 | FAILING | Full chapter review with Agent 1; may require reconstruction |

---

## Low-Tension Zone Detection

Flag these patterns:

**Low-tension zone:** Any continuous section of 800+ words with no:
- Dialogue conflict
- New information
- Physical or emotional threat
- Character decision with stakes

**Dialogue plateau:** Three or more exchanges where no new information is exchanged
and tension doesn't change. Flag: what is this dialogue *doing*?

**Exposition block:** Any paragraph over 200 words of direct exposition without
a character lens. Flag: convert to character-filtered experience.

---

## Output Format

```
DOPAMINE-SCORE RESULT
---------------------
Chapter: [identifier]
Word count: [approx]

Driver Scores:
  Hook:        [1–5] — [brief note]
  Escalation:  [1–5] — [brief note]
  Revelation:  [1–5] — [brief note]
  Dread:       [1–5] — [brief note]
  Cliffhanger: [1–5] — [brief note]

Total: [5–25]
Verdict: EXCELLENT | GOOD | ADEQUATE | WEAK | FAILING

Low-tension zones: [locations or "None detected"]
Recommended actions:
  1. [Specific, actionable recommendation]
  2. [...]
```
'@

Write-Host "▶ Deploying /dopamine-score..." -ForegroundColor Cyan
Write-Skill "$coworkBase\dopamine-score\SKILL.md" $dopamineScore

# =============================================================================
# SUMMARY
# =============================================================================

Write-Host ""
Write-Host "=================================================================" -ForegroundColor DarkYellow
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "  Files written successfully: $ok / 17" -ForegroundColor Green

if ($fails.Count -gt 0) {
    Write-Host ""
    Write-Host "  ✗ FAILED ($($fails.Count) files):" -ForegroundColor Red
    foreach ($f in $fails) {
        Write-Host "    $f" -ForegroundColor DarkRed
    }
    Write-Host ""
    Write-Host "  Check that the F:\ drive is connected for Agent 8 paths." -ForegroundColor Yellow
    Write-Host "  Cowork and Copilot skills will still work regardless." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Next step: Update TNC_Book2_Cowork_Setup.md" -ForegroundColor Cyan
Write-Host "  Change all 10 skill entries from 📋 to ✅" -ForegroundColor Cyan
Write-Host ""
Write-Host "  'And they shall prophesy a thousand two hundred and threescore days.'" -ForegroundColor DarkYellow
Write-Host "   — Revelation 11:3" -ForegroundColor DarkYellow
Write-Host ""