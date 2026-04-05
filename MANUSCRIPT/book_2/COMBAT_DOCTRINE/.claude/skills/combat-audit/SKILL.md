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