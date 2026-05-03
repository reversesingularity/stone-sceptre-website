# THE NEPHILIM CHRONICLES — MASTER LORE BOOK
## A Comprehensive Reference for the Entire Project

**Publisher:** Kerman Gild Publishing (Auckland, NZ)
**Pen Name:** Kerman Gild
**Author:** Chris Modina
**Last Updated:** April 19, 2026
**Status:** Living document — update when canon is confirmed

> This document is a single-file reference covering canon, characters, worldbuilding, technology, the AI agent swarm, the production pipeline, and business strategy. When in doubt about any fact in this document, defer to the Canon Authority Hierarchy (Part I below).

---

## TABLE OF CONTENTS

- [Part I: Project Overview & Canon Hierarchy](#part-i-project-overview--canon-hierarchy)
- [Part II: Theological Foundation](#part-ii-theological-foundation)
- [Part III: Cosmology & Worldbuilding](#part-iii-cosmology--worldbuilding)
- [Part IV: Technology & Artifacts](#part-iv-technology--artifacts)
- [Part V: Protagonist Character Bible](#part-v-protagonist-character-bible)
- [Part VI: Antagonists](#part-vi-antagonists)
- [Part VII: The Five Books](#part-vii-the-five-books)
- [Part VIII: Master Timeline](#part-viii-master-timeline)
- [Part IX: AI Agent Swarm Architecture](#part-ix-ai-agent-swarm-architecture)
- [Part X: Production Pipeline](#part-x-production-pipeline)
- [Part XI: Business Strategy](#part-xi-business-strategy)
- [Part XII: Reference & Style Guides](#part-xii-reference--style-guides)
- [Appendix A: Locked Facts Quick Reference](#appendix-a-locked-facts-quick-reference)
- [Appendix B: Canon Drift Watch](#appendix-b-canon-drift-watch)
- [Appendix C: Project File Structure](#appendix-c-project-file-structure)

---

# PART I: PROJECT OVERVIEW & CANON HIERARCHY

## 1.1 Series Identity

| Field | Value |
|-------|-------|
| **Series Title** | The Nephilim Chronicles |
| **Genre** | Biblical Fantasy / Apocalyptic Thriller |
| **Setting** | Present day 2024–2030 with 2,600-year historical flashbacks |
| **Tone** | Epic, theological, action-driven, mythological |
| **Pen Name** | Kerman Gild |
| **Publisher** | Kerman Gild Publishing (Auckland, New Zealand) |
| **Copyright** | Kerman Gild © 2026 |
| **Secondary Series** | The Stone and the Sceptre Chronicles (same author/publisher) |

## 1.2 Series Status

| Book | Title | Status | Word Count |
|------|-------|--------|------------|
| Book 1 | The Cydonian Oaths | Published (KDP) | ~165,000 |
| Book 2 | The Cauldron of God | Published (KDP) | ~130,000 |
| Book 3 | The Edenic Mandate | KDP-Ready; Drafting Ch7+ | ~139,424+ |
| Book 4 | The Testimony | Architecture Locked | TBD |
| Book 5 | The Glory | Architecture Locked | TBD |

**Stone & Sceptre:**

| Book | Title | Status |
|------|-------|--------|
| Book 1 | The Stone and the Sceptre | Published |
| Book 2 | The Red Hand & The Eternal Throne | Published |
| Book 3 | The Third Overturn | In Development |

## 1.3 Canon Authority Hierarchy

**Rule:** Lower-tier documents ALWAYS defer to higher-tier documents. When conflict exists, the higher tier prevails.

| Tier | Document | Authority |
|------|----------|-----------|
| **Tier 0** | `MANUSCRIPT/book_1/` and `MANUSCRIPT/book_2/` (published chapters) | SUPREME — published text corrects all planning docs |
| **Tier 1** | `CANON/SERIES_BIBLE.md` | INVIOLABLE Constitutional axioms |
| **Tier 2** | `CANON/SSOT_v3_MASTER.md` | Consolidated factual canon (v3.2, April 18, 2026) |
| **Tier 3** | Dossiers in `CANON/dossiers/` | Character/entity details |
| **Tier 4** | Book outlines | Plot structure |
| **Tier 5** | Reference docs (`REFERENCE/`, `WORLDBUILDING/`) | Supporting material |

## 1.4 File Naming Rules (INVIOLABLE)

**NEVER create files named:**
- `*_ADDITIONS.md`, `*_UPDATED.md`, `*_REVISIONS.md`, `*_v2.md` (without archiving v1 first)

**Instead:**
- Update the canonical file directly (e.g., SSOT_v3_MASTER.md)
- Archive superseded versions to `ARCHIVE/superseded/` with timestamp
- Document changes in `ARCHIVE/session_logs/`

---

# PART II: THEOLOGICAL FOUNDATION

## 2.1 Constitutional Axioms (INVIOLABLE)

These axioms cannot be contradicted by any creative or plot decision. If a proposed idea conflicts, the idea must be rejected or modified.

### On God
- God is sovereign — nothing happens outside His knowledge or ultimate control
- God is good — His judgments are righteous, even when severe
- God does not lie — prophecy will be fulfilled exactly as stated
- The Bible is true and Scripture accurately describes reality in this series
- 1 Enoch is canonical *for this series* — its cosmology is treated as historical fact

### On Christ
- Christ's sacrifice is sufficient — no additional payment required for salvation
- The Resurrection happened bodily; He will return bodily
- The Tribulation is future, literal, and unavoidable

## 2.2 The Binitarian Godhead (LOCKED — §1.4)

**CRITICAL:** The series holds a Binitarian, not Trinitarian, theology.

| Element | Canon Fact |
|---------|-----------|
| **The Godhead** | A Family of Two Persons: God the Father and Jesus Christ the Son |
| **The Holy Spirit** | NOT a Person — the shared essence, mind, and projecting power of God in the natural world |
| **The Trinity doctrine** | A Harlot invention propagated through Mystery Babylon / institutional Catholicism (Nicaea/Constantinople) |
| **The Satanic Triumvirate** | NOT an "Unholy Trinity" — a strictly operational command hierarchy. Use terms: "Satanic Triumvirate" or "command triad." |

**Forbidden language:** "Third Person," "the Trinity," Holy Spirit as a Person, "Unholy Trinity."

## 2.3 Satan the Trafficker (Ezekiel 28 Framework)

Satan's fundamental nature is that of a **TRADER/TRAFFICKER**. He always knows what his targets desire, always offers to fulfill that desire, and there is always an "IF" — the condition that binds them.

| Target | What They Desired | Satan's "IF" Condition | Result |
|--------|-------------------|------------------------|--------|
| **Christ** | Kingdoms without the Cross | "IF you fall down and worship me" | FAILED |
| **Eve** | Knowledge, godhood | "IF you eat" | The Fall of mankind |
| **The 200 Watchers** | Women, procreation, fatherhood | "IF you descend" | First angelic army |
| **Lamech (Cainite)** | Power, wealth, prestige | "IF you offer your daughters" | Access to corrupt bloodline |
| **70-72 Principalities** | Worship, autonomy, power | "IF you follow me" | Control of the nations |

### The Authority Structure Compromise (Satan's Master Tactic)

Satan doesn't merely traffic with targets — he **compromises the authority structure** that could void the transaction:

| Transaction | Target | Authority Figure | How Satan Closed the Loophole |
|-------------|--------|-----------------|-------------------------------|
| Eden | Eve | Adam (husband) | Got Adam to eat WITH her |
| Pre-Flood | Naamah | Lamech (father) | Got Lamech to INSTRUCT her |
| The Watchers | The 200 | Shemyaza (captain) | Got Shemyaza to LEAD the oath |

### The Numbers 30 Principle
Under patriarchal covenantal law (Numbers 30), a father can nullify any oath his daughter makes. Satan approached Lamech FIRST (not Naamah) so Lamech became complicit — making Naamah's subsequent oaths unbreakable. This is why Satan always neutralises the authority structure first.

### The Adam/Eve Parallel
The Fall was NOT inevitable after Eve ate. Adam held covenantal authority to void the transaction. Romans 5:12 says "by one MAN sin entered" — not by Eve. Adam knew exactly what he was doing (1 Timothy 2:14). Satan needed BOTH to eat.

## 2.4 The Oiketerion Principle (Jude 1:6) (LOCKED)

| Fact | Detail |
|------|--------|
| Watchers **LOST** | Their inherent supernatural gifts when they shed their celestial bodies (the Ma'on/Oiketerion) |
| Watchers **RETAINED** | Knowledge of how those abilities functioned |
| Therefore | They could TEACH but not DEMONSTRATE post-descent |
| Therefore | Technology replaced their lost innate abilities |

## 2.5 The Knowledge Transmission Chain

```
WATCHERS (pre-Flood)
    ↓ taught
NEPHILIM (pre-Flood giants, warriors, demigods)
    ↓ drowned in Flood → spirits became
APKALLU (Nephilim priest-spirits, post-Flood)
    ↓ taught (appearing as "fish-men sages")
SUMERIANS (sudden civilization post-Flood)
    ↓ transmitted via
MYSTERY BABYLON SYSTEM (Harlot, Synagogue of Satan)
    ↓ modern manifestation
WEF / CLUB OF ROME (global governance elite)
```

## 2.6 Angelic Nature (LOCKED — Jubilees Framework)

- Angels were created on **DAY 1** of Creation (Jubilees 2:2)
- Angels are NOT "eons old" — they are created beings with a specific creation date
- They remember Creation because they witnessed it, not because they predate it
- Angels are created beings, not gods — powerful but limited
- The Ban is real: angels cannot directly intervene in mortal affairs except against supernatural violations

## 2.7 Spirits & Demons

- **Demons are Nephilim spirits** — disembodied dead of the hybrid race (NOT fallen angels)
- The Abyss is a real location containing entities to be released
- Tartarus/Dudael are distinct prisons — different entities, different terms, different releases
- Watcher wives were transformed into SIRENS at the Flood, not drowned — becoming goddess figures of mythology

---

# PART III: COSMOLOGY & WORLDBUILDING

## 3.1 Celestial Hierarchy

```
GOD THE FATHER (Supreme Sovereign)
    │
JESUS CHRIST THE SON (Logos, Creator)
    │
ARCHANGELS (Seven who stand before the Throne)
    │           Michael (guards Israel)
    │           Raphael (guides Cian)
    │           Gabriel (messenger)
    │           + 4 others
    │
SERAPHIM & CHERUBIM (Throne guardians)
    │
WATCHERS (200 assigned to observe humanity)
    │ [200 descended at Hermon — now imprisoned]
    │
PRINCIPALITIES (70-72 assigned to the nations after Babel)
    │ [many trafficked by Satan — now under his command]
    │
NEPHILIM (hybrid offspring of Watchers and human women)
    │ [all killed in Flood; spirits became APKALLU/DEMONS]
    │
SIRENS (transformed wives of Watchers)
```

## 3.2 The Watcher Fall

| Fact | Detail |
|------|--------|
| **Number** | 200 Watchers |
| **Leader** | Shemyaza (chief of all 200) |
| **Descent site** | Mount Hermon (northern Israel/Syria border) |
| **Date** | 3504 BCE |
| **Oath** | Shemyaza led a binding oath — all 200 complicit |
| **Instigator** | Satan trafficked with Lamech (Cainite) → Lamech instructed Naamah → Naamah seduced Shemyaza |
| **Naamah's leverage** | Extracted Shemyaza's True Name during seduction; used as control mechanism |
| **Result** | Giants (Nephilim) born; forbidden knowledge spread; corruption increased |
| **Judgment** | Watchers bound in Tartarus (1 Enoch 10); released only for final judgment then Lake of Fire |

### The 20 Watcher Chiefs (Partial — Key Figures)

| # | Name | Sin Domain | Earth Domain | Status |
|---|------|-----------|--------------|--------|
| 1 | **Shemyaza** | Commander; sorcery | — | Imprisoned (Tartarus) |
| 2 | **Armaros** | Counter-magic, oaths, binding | Carpathian Mountains, Romania (CLEARED Book 2 Ch6) | Imprisoned |
| 3 | **Araqiel** | Earth signs, geomancy | Greenland — Isua Greenstone Belt (Michael's interdict active) | Imprisoned |
| 5 | **Tamiel** | Demons, abortion | — | Imprisoned |
| 10 | **Asael** | Cosmetics, vanity | — | Imprisoned |
| 11 | **Penemue** | Writing, forbidden wisdom | — | Imprisoned |
| — | **Gadreel** | Weapons, warfare | — | Imprisoned; father of Azazel (NEPHILIM) |

**CRITICAL:** Watchers are permanently bound — no release window. They go from the Abyss to Gehenna. (Jude 1:6 — "everlasting chains under darkness unto the judgment of the great day.")

## 3.3 Cydonia-1 (Mars) — The Watcher Archive

| Fact | Detail |
|------|--------|
| **Location** | Cydonia region, Mars |
| **Construction** | Post-descent; built using Planar Gate transit network |
| **Purpose** | Acoustic archive of Watcher civilization; pre-Fall physics library |
| **Material** | Cydonian ore — acoustic metamaterial with memory properties |
| **The Stele** | Contains the Watcher Oath; Azazel's true coordinates for Dudael |
| **Access** | Raphael cannot enter (acoustical wards — one of his Three Limitations) |
| **Titan fleet** | 5 rovers launched Oct 15, 2026; operational on Mars May 2027 |
| **Brennan's mission** | Photographs stele; recovers coordinates; returns data to Cian |

## 3.4 Dudael/Cydonia-2 (Antarctica) — Azazel's Prison

| Fact | Detail |
|------|--------|
| **Biblical reference** | 1 Enoch 10:4-7; the "rough and jagged rocks" where Azazel was imprisoned |
| **Physical location** | Ross Ice Shelf; 79°58'22"S, 81°57'18"W (from Victoria Ashford's encrypted drive) |
| **Occupant** | Azazel (the False Prophet; NEPHILIM son of Gadreel) |
| **Security** | Watcher-grade acoustic wards; Armaros-class ward systems |
| **Book 2 plot** | Cian leads expedition; Azazel is released; False Prophet emerges |
| **Cover operation** | Antarctic drilling programme run by Synagogue shell companies (Victoria's Layer 2 data) |

## 3.5 Eden

| Fact | Detail |
|------|--------|
| **Status** | Still exists; concealed from natural discovery |
| **Time dilation** | Narnia-style: days in Eden = weeks/months on Earth (LOCKED) |
| **Occupants** | Enoch (since ~3017 BCE), Elijah (since ~860 BCE) |
| **Guardian** | Cherubim at the gate (flaming sword) |
| **River** | Used for baptism of Cian and Miriam (Book 3) |
| **Access** | Only granted by calling/commission — Cian's sword is the key |

## 3.6 The Empyreal Register

| Fact | Detail |
|------|--------|
| **Definition** | Celestial database documenting every angelic/demonic entity and their deeds |
| **Updates** | Real-time |
| **Accessible to** | Enoch the Scribe (Heaven's record-keeper), Cian mac Morna (via Mo Chrá's interface), Elijah (limited prophetic access) |
| **Purpose** | Verify Nephilim/Watcher identities, track activities, authenticate the Watchers' crimes |

## 3.7 The Schumann Resonance Connection

The Earth's natural Schumann resonance (7.83 Hz) is an echo of creation acoustics. Watcher technology interfaces with it. Mo Chrá's adaptive sheath exploits it passively (ferrite ring array harvests planetary magnetic rotation → 7.83 Hz baseline → masks sword's true acoustic signature from enemy sensors).

## 3.8 The Thirteen Houses (Synagogue of Satan)

The Synagogue of Satan operates through 13 bloodline Houses, each corresponding to a Watcher chief's earth domain. This is the Mystery Babylon system in its modern manifestation — the Harlot network controlling global governance, media, finance, and occult practice.

Key connections:
- House Tamiel: associated with Asmodeus-class demons; marked Miriam for acquisition
- House Aram: Carpathian region; Armaros domain (CLEARED Book 2 Ch6)
- WEF/Club of Rome: modern operational layer of the 13 Houses
- The "Whore of Babylon" riding the Beast = Naamah riding Ohya's political apparatus

## 3.9 The Four Horsemen Framework

| Seal | Rider | Identity | Trigger | Book |
|------|-------|---------|---------|------|
| First | White / Conquest | Geopolitical conquering figure | Book 2 close | Book 2 |
| Second | Red / War | Azazel's release destabilises world | Azazel freed | Book 3 |
| Third | Black / Famine | Follows war; economic collapse | After Azazel | Book 3 |
| Fourth | Pale / Thanatos + Hades | Ohya's emergence as the Beast | Ohya rises | Book 4 |

**KEY:** The Four Horsemen are **hindering** the Triumvirate's plans, not helping them. Thanatos acknowledges Cian as "anomaly — not within my mandate... yet."

---

# PART IV: TECHNOLOGY & ARTIFACTS

## 4.1 The Acoustic Paradigm (LOCKED — Core Canon)

**All Watcher technology is acoustic-based.** This is not metaphor. Every device, material, and system operates through specific frequencies, harmonic resonances, and acoustic patterns that interact with matter at fundamental levels.

**Scriptural foundation:**
- Genesis 1: God SPOKE creation into existence
- John 1:1-3: "In the beginning was the Word... All things were made by him"
- Job 38:7: "The morning stars sang together" — Watchers witnessed the acoustic creation event

| Human Technology Basis | Watcher Technology Basis |
|------------------------|--------------------------|
| Electromagnetic radiation | Acoustic vibration |
| Electron flow (electricity) | Harmonic resonance |
| Chemical reactions | Frequency-induced material states |
| Binary data (0s and 1s) | Tonal patterns and harmonics |
| Visual display | Auditory output |
| Photonic sensors | Acoustic sensors |

### The Creation Frequency
The fundamental harmonic established when God spoke existence into being. The Watchers heard it, remembered it, and encoded it into their technology. It:
- Is the resonant tone of the universe itself
- Cannot be perfectly replicated by human technology
- Is embedded in all Watcher-created materials
- Is what Mo Chrá has been humming for 2,636 years

## 4.2 Cydonian Ore (Watcher Metamaterial)

| Property | Description |
|----------|-------------|
| **Acoustic Memory** | Records and stores sound; remembers what it witnessed |
| **Harmonic Response** | Vibrates at specific frequencies when exposed to sound |
| **Frequency-Selective Behavior** | Different frequencies trigger different material properties |
| **Self-Maintaining Structure** | Resonance keeps molecular bonds stable indefinitely |
| **Source** | Debris from Watchers' descent through Planar Gate |
| **Locations** | Mo Chrá's blade, Cydonia-1 inscriptions, Miriam's adaptive sheath (8% composite) |

## 4.3 Mo Chrá ("My Torment") — Methuselah's Sword

| Attribute | Value |
|-----------|-------|
| **Origin** | Forged by Enoch from Cydonian ore/obsidian |
| **Length** | 54 inches (42" blade, 12" hilt) |
| **Weight** | 6.2 pounds |
| **Appearance** | Dark grey/black; appears crude but beyond modern metallurgy |
| **Wielders** | Methuselah (969 years) → Cian (2,636 years) |
| **Naming date** | 532 CE, Constantinople, Nika Riots |
| **Name meaning** | "Mo Chrá" = "My Torment" (Irish) |
| **Kill count (Methuselah)** | 980,000 Nephilim spirits |
| **Kill count (Cian)** | ~50,000 supernatural entities |
| **Personality** | Stubborn, cryptic, possibly amused. Character, not object. |

### Properties Table

| Property | Effect |
|----------|--------|
| **Longevity Transfer** | Ages Cian ~1 year per millennium |
| **Nephilim-Slaying** | Can harm/kill supernatural entities |
| **Memory Revelation** | Grants visions of Methuselah's experiences |
| **Shape-Shifting** | Bastard sword ↔ tantō ↔ dagger via acoustic negotiation |
| **Ward-Breaking** | Unravels Watcher-grade wards via counter-frequency |
| **Acoustic Testimony** | Produces pure creation frequency; Cydonian inscriptions respond |
| **Empyreal Interface** | Grants Cian access to the Empyreal Register |
| **Chains of Abyssal Damnation** | Book 2 Ch6: extends physical chains; Gehenna fire; ward-shatter (total exhaustion of sword + wielder) |
| **Anti-Ward Counter-Frequency** | Book 2 Ch7.5: autonomous Armaros-class counter-frequency hack; permanent; passive |
| **Adaptive Sheath** | JW Chen's 8% Cydonian composite sheath; 7.83 Hz ferrite ring array; passive +0.4 dB/40min trickle-charge |

### Mo Chrá's Post-Chains Recovery Arc (Book 2)

After the Chains of Abyssal Damnation deployment:
1. Goes completely dark — first time in 2,600 years
2. Faintest teal pulse at "You held the line" exchange (ember, not flame)
3. Weight-reflex when Miriam tries to move her (Ch7: first sign of life)
4. Full recovery: Ch7 — Siobhan's lullaby → smug teal glow

### Azazel's Threat Assessment Error (Brennan McNeeve's Rebuttal)

Azazel assessed Mo Chrá as "insufficient." He is wrong for three reasons:
1. **Masking Effect** — Mn-Zn ferrite rings feed Azazel's sensors the 7.83 Hz Schumann signature only
2. **Primordial Resonance** — Azazel believes the sword is steel; it is Cydonian ore — pre-Fall physics, immeasurable by fallen sensory framework
3. **Conclusion** — Mo Chrá is a Sentient Universal Anchor, not a weapon

## 4.4 The Mark System (Layers 0-3)

Azazel's prophetic "Mark of the Beast" system, anticipated across Books 3-5:

| Layer | Name | Function |
|-------|------|---------|
| **Layer Zero** | The Mandate | Global biometric ID / surveillance framework |
| **Layer One** | Acoustic tagging | Frequency-based dermal marking (sub-audible) |
| **Layer Two** | Tether activation | House Tamiel/Asmodeus-class demonic assignment |
| **Layer Three** | Full possession vector | Complete spiritual subjugation |

**Book 3 Ch5:** Layer Zero rollout begins (Adon UN speech); Brennan/James deploy Enochian Faraday cage (432 Hz archived recording solution).

## 4.5 The Titan Fleet (Mars Mission)

| Fact | Detail |
|------|--------|
| **Vehicles** | Titan-1 through Titan-5 (5 rovers) |
| **Launch date** | October 15, 2026 (LOCKED) |
| **Launch site** | Boca Chica, Texas (SpaceX Starship) |
| **Mars arrival** | May 2027 (all five units operational) |
| **Mission lead** | Brennan mac Niamh McNeeve |
| **Primary objective** | Photograph and document the Cydonian stele |
| **Secondary objective** | Transmit Watcher coordinates to Cian's team |

---

# PART V: PROTAGONIST CHARACTER BIBLE

## 5.1 Cian mac Morna

| Attribute | Value |
|-----------|-------|
| **Full Name** | Sir Cian mac Morna, Knight of the Craobh Ruadh |
| **Birth** | ~611 BCE |
| **Commission** | **586 BCE** (rescues Niamh; receives sword; granted longevity) |
| **Biological age** | ~28-30 years old |
| **Aging rate** | **1 biological year per 1,000 chronological years** (LOCKED Feb 2026) |
| **Chronological age** | 2,636 years (as of 2025) |
| **Lineage** | Descendant of Machir ben Manasseh (giant-slayer heritage) |
| **Role** | Guardian of the Two Witnesses |
| **Estimated kills** | ~50,000 supernatural entities |

### Previous Wives (Deceased)

| Wife | Period | Notes |
|------|--------|-------|
| Aoife | ~580–540 BCE | First wife |
| (Unnamed) | — | Second wife |
| Merewyn | ~980–1050 CE | 11th-century counter-intelligence framework (foundation of Josephite Network) |
| Siobhan | ~1100–1170 CE | Most recent prior to Miriam |

850 years since last wife. Refuses to love again — until Miriam.

### The Josephite Network
Founded ~1800 CE. Independent Guardian entity against the Thirteen Houses. Built on Merewyn's counter-intelligence framework; catalysed by French Revolution / Napoleonic exposure of House manipulation. Operates across Michael's jurisdictional territories (Josephite nations).

### Physical Description
- Tall, lean, deceptive build concealing tremendous power
- Jet-black hair, piercing blue eyes
- Intensity that marks a weapon of terrible efficiency
- Moves like someone expecting attack at any moment

### Voice/Personality
- Sharp, occasionally sarcastic, Celtic Irish idioms
- Deep trauma managed through dark humor and duty
- 850-year grief wall — refuses to name what he feels for Miriam
- Faithful despite questioning
- Internal monologue: world-weary, poetic, sardonic

### Thematic Verse
**John 15:13** — *"Greater love hath no man than this, that a man lay down his life for his friends."* This becomes Cian's daily reality across Books 4-5.

## 5.2 Raphael ("Liaigh")

| Attribute | Value |
|-----------|-------|
| **True Identity** | One of the Seven Archangels who stand before the Throne |
| **Known As (Cian's name)** | "Liaigh" (Irish for "healer") — INVIOLABLE until Book 5 Ch10 |
| **Assignment** | Cian's guardian angel — since Cian's youth (~2,606 years) |
| **Cian's awareness** | Does NOT know Liaigh is an archangel |

### The Three Limitations (INVIOLABLE)

| # | Limitation | Rule | Consequence |
|---|------------|------|-------------|
| **1** | THE BAN | Cannot intervene against mortal humans | Only supernatural threats |
| **2** | HEAVENLY LITURGY | Unavailable during Tamid hours | 9-10 AM, 3-4 PM; Sabbath (limited); High Holy Days |
| **3** | NAME CONSEQUENCE | If Cian learns Raphael's true name | Direct communication ends forever |

### Empyreal Speech Register (MANDATORY for all Raphael dialogue)

- Thee/thou, elevated vocabulary
- ALL CAPS for proclamations
- Divine gravitas, cosmic perspective
- Example: *"THY PETITION WAS UNNECESSARY. I OFFER MINE ASSESSMENT AS ONE WHO HATH OBSERVED BOTH THY NATURE AND HERS."*

### The Operational Silence Arc (Book 3 Ch14 → Book 5 Ch10)

| Element | Detail |
|---------|--------|
| **Seed** | Book 3 Ch10 (post-baptism): "WHAT COMETH NEXT REQUIRETH MORE OF ME THAN I HAVE GIVEN IN ALL THE CENTURIES OF OUR COMPANIONSHIP" |
| **Full Severance** | Book 3 Ch14 (Eden departure): Raphael requests silence; Cian grants it; channel closes |
| **What is severed** | 2,600 years of Empyreal Register banter, counsel, comfort |
| **What remains** | Raphael's assignment, physical/spiritual presence, combat protection; Mo Chrá's passive acoustic link |
| **Mo Chrá Farewell** | Raphael addresses the sword: "KEEP HIM FATAL, LITTLE SINGER." Mo Chrá responds with subsonic grief-salute. |
| **Final Exchange** | Cian: "Watch your own back for once, Liaigh." — Raphael: "AND THOU THINE, WARRIOR." — Channel drops. |
| **Single micro-fracture** | Book 4 Ch11 ONLY: Cian takes mortal wound; one word bleeds through: "HOLD." Never again. |
| **Tobit Protocol Exception** | Book 4 Ch7: Raphael deploys acoustic binding; Miriam hears "I AM RAPHAEL, THE HEALING OF GOD"; Cian outside vacuum, hears nothing |
| **Phantom Banter** | Cian mimics Liaigh's Empyreal Register in campfire stories; Mo Chrá plays comedic straight man; comedy always ends with grief |
| **Lifted** | Book 5 Ch10: Raphael speaks true name to dying Cian; drops Empyreal Register; normal voice: "My name is Raphael. You were the finest duty I was ever given." |

### Knowledge-Tracked Naming

| POV | Name Used |
|-----|-----------|
| Cian | "Liaigh" — inviolable until Book 5 Ch10 |
| Raphael's own POV | "Raphael" |
| Miriam pre-Tobit (Book 4 Ch7) | "Liaigh" / "the guardian" |
| Miriam post-Tobit | "Raphael" (internal) / "Liaigh" (spoken) |
| Enoch/Elijah POV | "Raphael" |
| Brennan POV | "Liaigh" / "the angel" |

## 5.3 Enoch (The First Witness)

| Attribute | Value |
|-----------|-------|
| **Biblical ID** | Enoch, son of Jared — "walked with God; was not, for God took him" (Genesis 5:24) |
| **Translation date** | ~3017 BCE |
| **Location** | Eden (since translation) |
| **Role** | Heaven's Scribe; First Witness; record-keeper of Empyreal Register |
| **Key artifact** | Forged Mo Chrá from Cydonian materials — "I made it for you. It was always meant for you." |
| **Personality** | Precise, methodical, 5,000 years of accumulated knowledge; accustomed to documenting everything |
| **Voice register** | Archaic but precise; the scribe's cadence |

## 5.4 Elijah (The Second Witness)

| Attribute | Value |
|-----------|-------|
| **Biblical ID** | Elijah the Tishbite, prophet of Israel |
| **Translation date** | ~860 BCE (fiery chariot, 2 Kings 2) |
| **Location** | Eden (since translation) |
| **Role** | Prophet of fire; Second Witness; 2,800 years of preparation |
| **Supernatural abilities** | Fire judgment (Book 3: confronts Azazel with fire); drought declaration |
| **Book 3 key scene** | Confronts Azazel with fire; "confronts him with fire" |
| **Voice register** | Prophetic, declarative, uncompromising |

## 5.5 Miriam Ashford

| Attribute | Value |
|-----------|-------|
| **Full Name** | Miriam Elizabeth Ashford (née Miriam bat Elisheva) |
| **Age** | 29 (Book 2, circa 2025) |
| **Nationality** | British-Israeli (dual citizenship) |
| **Heritage** | Jewish — Sephardic descent |
| **Role** | Secondary protagonist; intelligence analyst; "reader perspective" character |
| **Lineage note** | **NO connection to Niamh** — not a bloodline character |

### Backstory (CRITICAL CORRECTION)

- Miriam was **TARGET** of Satanic ritual abuse (SRA), NOT a survivor who was corrupted
- Mother Victoria died **BREAKING** the ritual chain
- Rituals were performed **TO CLAIM** her, not corrupt her
- Victoria's sacrifice interrupted before completion
- Demon assigned (Asmodeus-class) but **CANNOT POSSESS** her (mother's prayers created shield)

### Victoria Ashford's Intelligence Legacy

Victoria left Miriam an encrypted drive with three-layer intelligence:

| Layer | Contents |
|-------|----------|
| **Layer 1** | Complete Synagogue shell company UBO chain — 62 jurisdictions, 11 countries |
| **Layer 2** | Antarctic drilling programme — 7 years, Ross Ice Shelf, Azazel's coordinates (79°58'22"S, 81°57'18"W) |
| **Layer 3** | Paracas genetics supply chain — elongated cranial specimens; annotated "not human" |

### Acoustic Anomaly (MYSTERY SEED)

Miriam stands untouched by Mo Chrá's Gehenna/judgment frequency (Chains deployment, Book 2 Ch6) while James is driven to one knee and Brennan's electronics flatline. **No character comments.** Seed for Books 3–5.

**Resolution (Books 3-5):** Her spirit-signature is tuned to the Creation Frequency — identical resonance to Cydonian ore. The Judgment Frequency passes through her because her spirit contains no "fallen hooks." Book 4: she becomes an acoustic conduit; her Muromachi katana projects Creation frequency through contact (not through the steel's material composition).

### Romance Arc with Cian

| Date | Milestone |
|------|-----------|
| Book 2 Ch1 | Sarah notices Cian stood motionless outside Miriam's workspace for a full hour |
| Book 2 Ch5 | Cian presents Muromachi katana (warrior's protocol); Shield Position seeded |
| Book 2 Ch6 | Miriam places Mo Chrá on unconscious Cian's chest (Fianna guardianship rite); Mo Chrá acknowledges with teal pulse |
| March 2028 | The First-Name Milestone: "Mac Morna" retired; Miriam calls him "Cian" |
| August 2029 | The Coilgun Proposal: Cian proposes (tactical, briefing room setting) |
| February 2030 | The Marriage Covenant: Jerusalem, during 1,260-day ministry, over the Lia Fáil |

**Red lines:** No team member tells either character. Comedy never at Miriam's expense. Neither acts on feelings through Books 1–3.

## 5.6 Brennan mac Niamh McNeeve

| Attribute | Value |
|-----------|-------|
| **Full name** | Brennan mac Niamh McNeeve (**NOT "Brennan Webb"** — that is a drift error) |
| **Role** | Mars mission lead; drone/rover engineer; tech specialist |
| **Relation to Cian** | Descendant of Niamh (Cian's sister from 586 BCE) |
| **Bloodline** | Josephite — excluded from Beast system |
| **Function** | Key revelation vector for Cydonia discovery; Engineering Neurosis foil to Cian's Tactical Deadpan |
| **Key Book 3 scene** | Brennan/James interlude (Ch5): time dilation deployment, Layer Zero rollout, Enochian Faraday cage, Brennan's prayer ("the 0.3 dB gap as grace problem") |

## 5.7 Dismas (The Penitent Thief)

| Attribute | Value |
|-----------|-------|
| **Biblical ID** | The "Good Thief" crucified beside Christ (Luke 23:43) |
| **Status** | In Eden — "Today you will be with me in Paradise" |
| **Role in series** | Witness to Eden baptism; Book 3 Epilogue Mvt II POV chapter |
| **Thematic function** | The Grace Motif — salvation by sovereign grace alone, not accumulated merit; mirrors Miriam's acoustic anomaly |

---

# PART VI: ANTAGONISTS

## 6.1 The Satanic Triumvirate (Operational Command Hierarchy)

**NOT an "Unholy Trinity."** A strictly operational hierarchy: Empowerer → Political Ruler → Technological/Spiritual Enforcer.

| Role | Identity | Notes |
|------|----------|-------|
| **The Dragon (Empowerer)** | SATAN | Architect of Watcher rebellion; the Trafficker |
| **The Beast / Apollyon (Political Ruler)** | OHYA | Son of Shemyaza and Naamah; Nephilim spirit |
| **The False Prophet (Tech/Spiritual Enforcer)** | AZAZEL | **NEPHILIM** son of Gadreel (NOT a Watcher); cover name "Dr. Ezra Adon" |
| **The Whore of Babylon** | NAAMAH | Ohya's mother; survived Flood as Siren; seduced Shemyaza |

## 6.2 Satan (The Dragon)

- Fundamental nature: Trader/Trafficker (see §2.3)
- Fell alone initially; built his army one transaction at a time
- The 1/3 of angels joined him ONLY at the Michael War (Revelation 12) — not at his initial fall
- Will be bound for 1,000 years after Beast's defeat

## 6.3 Ohya (The Beast / Apollyon)

| Attribute | Value |
|-----------|-------|
| **Identity** | Son of Shemyaza and Naamah; Nephilim of the first generation |
| **Biblical title** | The Beast; Apollyon (Revelation 9) |
| **Status** | Spirit in the Abyss until released (Book 4) |
| **Trigger for release** | Fourth Seal; becomes the Beast riding from the sea |
| **Fate** | Cast into Lake of Fire (Revelation 19:20) |

## 6.4 Azazel (The False Prophet)

| Attribute | Value |
|-----------|-------|
| **Identity** | **NEPHILIM** son of Gadreel (CRITICAL: NOT a Watcher himself) |
| **Cover name** | "Dr. Ezra Adon" (Books 3+) |
| **Prison** | Dudael (Antarctica, Ross Ice Shelf) |
| **Released** | Book 2 — Cian's expedition triggers release |
| **Abilities** | Signs and wonders; weapons knowledge; Mark system architecture |
| **Fate** | Cast into Lake of Fire |

## 6.5 Naamah (The Whore of Babylon)

| Attribute | Value |
|-----------|-------|
| **Identity** | Daughter of Cainite Lamech (NOT Sethite Lamech/Noah's father) |
| **Role** | Seduced Shemyaza; extracted his True Name |
| **Survival** | Transformed into Siren at Flood — no longer dwelt on land |
| **Mythology** | Source of all Mother Goddess traditions: Isis, Ishtar, Inanna, Astarte, Cybele, Aphrodite, etc. |
| **Modern role** | Rides Ohya's political apparatus; coordinates Thirteen Houses |
| **Fate** | Sealed alive in ephah vessel (Zechariah 5 literalized) |

## 6.6 Lord Vârcolac (Primary Book 1 Antagonist)

| Attribute | Value |
|-----------|-------|
| **Identity** | Vampire lord; Nephilim bloodline |
| **Status** | **DEAD** — killed in Book 1 |
| **Domain** | Carpathian region (Armaros earth domain) |
| **Book 2 Note** | Armaros's earth domain was CLEARED in Book 2 Ch6; Vârcolac-class entities defeated |

---

# PART VII: THE FIVE BOOKS

## 7.1 Book 1: The Cydonian Oaths

**Theme:** Cian receives his Guardian calling — struggles with "just" being a protector  
**Four Horsemen:** Foreshadowing only  
**Key beats:** Cian at his lowest → The Cydonia Vision → Commission → Brennan "I Am Your Uncle" revelation → Accepts calling  
**Closes:** Cian sets out toward Eden in earnest

## 7.2 Book 2: The Cauldron of God

**Theme:** Finds Eden, retrieves both Witnesses — the three emerge together  
**Four Horsemen:** First Seal breaks — Conquest rides  
**Key beats:** Antarctic expedition → Azazel's release → Cian enters Eden → Meets Enoch ("I made it for you") → Elijah → The three emerge  
**Closes:** All three emerge together; Miriam/Cian arc deepens; Raphael's Tobit pattern begins

## 7.3 Book 3: The Edenic Mandate

**Theme:** The war begins — Azazel rises as False Prophet  
**Four Horsemen:** Second and Third Seals — War and Famine  
**Status (April 2026):** Prologue + Ch1–Ch6 DRAFTED; Ch7–14 resequence LOCKED

### Book 3 Chapter Map (Ch7-14 Resequence — LOCKED April 18)

Full chapter map in `WORLDBUILDING/BOOKS_3_5_ARCHITECTURE.md` and `/memories/repo/BOOK3_CH07-14_RESEQUENCE.md`.

**Key structural decisions:**
- Brennan interludes at Ch8, Ch11, Ch13 (Eden time dilation exploited)
- Baptism pure (Ch10): Elijah baptises Cian and Miriam in Eden's river (witnessed by Enoch and Dismas)
- Operational Silence seed: Ch12 Briefing end (NOT Ch10)
- Full Operational Silence severance: Ch14 (Eden departure)
- Azazel cover name: "Dr. Ezra Adon" throughout

**Key scenes locked:**
- Enoch confronts Azazel: *"I have been writing your crimes for five thousand years."*
- Elijah confronts Azazel with fire
- The Edenic Baptism (Ch10)
- Op Silence severance exchange (Ch14)
- Epilogue: Raphael POV (Mvt III); Dismas POV (Mvt II); Azazel POV (Mvt I) — triptych

### Book 3 Dopamine Scores (April 2026 Analysis)

| Chapter | Dopamine Score | Standout |
|---------|---------------|---------|
| Prologue | 20/25 | Strong Cold Open |
| Ch1 | 21/25 | Architecture of Resistance |
| Ch2 | 20/25 | The Frequency Beneath the Cure |
| Ch3 | 21/25 | The Last Cartography |
| Ch4 | 22/25 | The Gauntlet |
| Ch5 | 21/25 | The Logistics of Mercy |
| Ch6 | 22/25 | The Burning Choir |
| Ch7 | 21/25 | The Prophet |
| Ch8 | 22/25 | Brennan interlude |
| Ch9 | 21/25 | Escalation |
| Ch10 | 23/25 | The Edenic Baptism |
| Ch11 | 22/25 | Brennan interlude 2 |
| Ch12 | 22/25 | The Briefing / Op Silence seed |
| Ch13 | 23/25 | Brennan interlude 3 |
| Ch14 | 24/25 | Full Op Silence severance |
| Ch15 | **25/25** | Jerusalem (PERFECT) |
| Epilogue | 23/25 | Triptych POV |

**Overall Book 3 Score: 22.1/25 — NEAR-MASTERWORK**  
Trilogy trajectory: 19.8 → 21.6 → 22.1

## 7.4 Book 4: The Testimony

**Theme:** The 1,260 days — John 15:13 becomes Cian's daily reality  
**Four Horsemen:** Fourth Seal — Thanatos + Hades (Ohya's emergence)  
**Key beats:** Ohya rises from Abyss → 42 months of Witness ministry → Daily combat → Miriam dies (~Day 1,050) → Naamah's doom begins  
**Marriage:** Jerusalem, February 2030, over the Lia Fáil

## 7.5 Book 5: The Glory

**Theme:** The final sacrifice — John 15:13 fulfilled  
**Key beats:** End of 1,260 days → Witnesses slain by Beast → 3.5 days → Bodies lie in Jerusalem, Cian guards → Last Trump → Witnesses rise → Cian rises (First Resurrection)  
**Raphael's revelation:** Book 5 Ch10 — speaks true name to dying Cian; drops Empyreal Register; "My name is Raphael. You were the finest duty I was ever given."  
**Naamah's fate:** Sealed alive in ephah vessel  
**Beast/False Prophet fate:** Lake of Fire  
**Satan's fate:** Bound 1,000 years

---

# PART VIII: MASTER TIMELINE

## 8.1 Deep History

| Era | Date | Event |
|-----|------|-------|
| Creation | — | Acoustic paradigm: God SPOKE creation into being |
| Angels created | Day 1 of Creation | Per Jubilees 2:2 |
| Watcher Assignment | 3604 BCE | 200 Watchers assigned to observe humanity |
| The Golden Century | 3604–3504 BCE | Watchers faithful; teach righteousness |
| The Fall | **3504 BCE** | Shemyaza's Oath at Cydonia (Mars); descent to Hermon |
| Naamah's Seduction | 3504 BCE | Extracts Shemyaza's True Name |
| Nephilim Era | 3504–2348 BCE | Giants born; corruption spreads |
| The Flood | **2348 BCE** | Judgment; Watchers bound in Tartarus |
| Siren Transformation | 2348 BCE | Watcher wives become Sirens; Naamah survives |
| Post-Flood | 2348 BCE+ | Nephilim bloodlines survive via Ham/Naamah |
| Nimrod Possession | ~2200 BCE | Ohya's spirit channels into Nimrod via Semiramis ritual |
| Babel | ~2200 BCE | Tower built; languages confused |
| Cian's Birth | ~611 BCE | Irish noble family |
| **Cian's Commission** | **586 BCE** | LOCKED — receives sword; rescues Niamh; granted longevity |
| **Mo Chrá Named** | **532 CE** | LOCKED — Constantinople, Nika Riots |

## 8.2 Present-Day Critical Date Locks

| Event | Date | Status |
|-------|------|--------|
| Cydonian Revelation | 2020 CE | LOCKED |
| Cian's Vision (Book 1 Ch1) | **January 2024** | LOCKED |
| **Titan-1–5 Launch** | **October 15, 2026** | LOCKED |
| **Titan-1 Mars Arrival** | **May 2027** | LOCKED |
| Miriam arrives at safehouse | ~September 8, 2027 | LOCKED |
| **Anti-Singularity Event (Book 1 Ch10)** | September 15, 2027 | LOCKED |
| Mo Chrá / Liaigh recovery | ~October 4, 2027 | LOCKED |
| **Book 2 Chapter 1** | November 3, 2027 | LOCKED |
| Book 2 Chapter 4 | ~November 14, 2027 | LOCKED |
| Antarctic expedition departs | ~December 2027 | Projected |
| Dudael approach | January 2028 | Projected |
| Austral summer closes | ~February 2028 | Hard deadline |
| 1,260-day ministry begins | 2028 | Projected |
| Miriam dies | ~Day 1,050 | Book 4–5 |
| Marriage Covenant | February 2030 | Jerusalem, Lia Fáil |
| Witnesses slain | End of 1,260 | Beast kills Enoch and Elijah |
| Bodies lie 3.5 days | Post-death | Cian guards |
| **Last Trump / First Resurrection** | Post-3.5 days | Witnesses rise; Cian rises |

---

# PART IX: AI AGENT SWARM ARCHITECTURE

## 9.1 Overview

The TNC Creative Swarm is a **13-agent Hybrid Bottom-Up Narrative Community** using a HAWK (Hierarchical Agent Workflow) 5-layer topology. It serves Books 3–5 of The Nephilim Chronicles.

**Primary LLM:** Nemotron 3 Super (120B total, 12B active, Latent MoE) — long-horizon reasoning  
**Secondary LLM:** Ollama llama3.1 (RTX 3080) — fast scene-level tasks  
**Orchestration:** n8n (:5678) — webhook routing, job scheduling, agent chaining  
**Vector memory:** Qdrant (:6333) — 5 collections, 52,781+ points

## 9.2 HAWK 5-Layer Topology

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
║  LAYER 2 — OPERATOR (Master Orchestrator)                        ║
║  Agent 0: SWARM CONDUCTOR — Nemotron 3 Super                     ║
║  Decomposes user intent → task graph → dispatches to Layer 3     ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 3 — AGENT (Specialized Workers)                           ║
║  Agents 1–12 — each owns a single cognitive domain               ║
║  All inter-agent traffic through Layer 2 or n8n bus              ║
╠══════════════════════════════════════════════════════════════════╣
║  LAYER 4 — RESOURCE                                              ║
║  Qdrant :6333 | Ollama :11434 | Nemotron API                     ║
║  Python services :8765–:8772 | llama-server :8780                ║
╚══════════════════════════════════════════════════════════════════╝
```

**Design principle:** Layer 3 agents NEVER call each other directly. All inter-agent communication passes through Layer 2 (Conductor) or Layer 1 (n8n bus). This eliminates deadlock and enforces auditability.

## 9.3 Full Agent Registry

| ID | Name | Model | Role | Port |
|----|------|-------|------|------|
| AGENT_0 | Swarm Conductor | Nemotron-3 Super | Orchestrates all jobs; final authority below Author | 8771 |
| AGENT_1 | Content Creator | Claude Sonnet 4.6 | Prose, outlines, interviews, scene drafts | — |
| AGENT_2 | Drift Manager v2 | Nemotron-3 Super | Cross-book drift detection; canon semantic search | — |
| AGENT_3 | Constitution Updater v2 | Nemotron-3 Super | CRDT-merged SSOT updates with conflict resolution | — |
| AGENT_4 | Reader Reaction Matrix | Ollama llama3.1 | Per-scene 8-criterion scoring | — |
| AGENT_5 | Dopamine Ladder | Ollama llama3.1 | Hook density + tension arc mapping | — |
| AGENT_6 | Image Prompt Designer | Nemotron Router cascade | Visual direction briefs for KDP art | — |
| AGENT_7 | KDP Formatter | Python (deterministic) | Assembles .docx from markdown | 8766 |
| AGENT_8 | Story Prototype Extractor | Nemotron-3 Super | Role/Plot graph extraction into Qdrant | 8767 |
| AGENT_9 | Content Strategist / NZ Grant Monitor | Nemotron Router cascade | Social content, SEO, serialization, NZ grants | 8772 |
| AGENT_10 | Cross-Book Auditor | Nemotron-3 Super | Nightly Books 3+4+5 continuity | — |
| AGENT_11 | Self-Refine Critic | Nemotron Router cascade | Scene draft scoring + critique; meta-evaluates Agents 4+5 | — |
| AGENT_12 | Nemoclaw Daemon | asyncio | File watcher, CRDT collector, heartbeat (1 min) | — |
| AGENT_13 | Marketing Agent v2.1 | llama3.1 + Qdrant | 24/6 autonomous content generation; multi-platform posting | — |

## 9.4 Python Service Map

| Service | Port | Script | Purpose |
|---------|------|--------|---------|
| Canon Search API | 8765 | `canon_search_api.py` | Semantic SSOT search over Qdrant |
| KDP Format Server | 8766 | `kdp_format_server.py` | Manuscript → .docx assembly |
| Story Prototype API | 8767 | `update_story_prototype.py` | Role/Plot graph extraction |
| Nemotron Tool Router | 8768 | `nemotron_tool_router.py` | NIM → OpenRouter → Local GGUF → Ollama |
| Utility Server | 8769 | `utility_server.py` | /crdt-merge, /self-refine, /cross-book-audit |
| Theological Guard | 8770 | `theological_guard_server.py` | 9-axiom theological validation (RED/AMBER flags) |
| Swarm Conductor | 8771 | `conductor_server.py` | Master orchestrator (Agent 0) |
| Content Strategist | 8772 | `agent_9_content_strategist.py` | Social, SEO, serialization, NZ grants |
| Local Nemotron GGUF | 8780 | `llama-server` (llama.cpp) | CPU-only Nemotron 3 Super (120.67B IQ3_S, 25 GPU layers) |
| Nemoclaw Daemon | — | `nemoclaw_daemon.py` | File-watch MANUSCRIPT/, CRDT polling |
| n8n | 5678 | docker | Workflow orchestration backbone |
| Qdrant | 6333 | docker | Canon vector store |
| Ollama | 11434 | ollama | Local GPU inference (llama3.1, nomic-embed-text) |
| PostgreSQL | 5432 | docker | n8n database |

## 9.5 Qdrant Collections

| Collection | Purpose | Key Fields |
|------------|---------|-----------|
| `nephilim_chronicles` | Legacy flat canon (Books 1–2) | category, entity_type, source_file |
| `tnc_episodes` | Episodic Memory — chapter summaries | book, chapter, excerpt, char_count |
| `tnc_personas` | Persona Memory — per-character state | character_id, last_seen_chapter |
| `tnc_role_graph` | Role Graph — entity-relation triples | subject, predicate, object, locked |
| `tnc_plot_graph` | Plot Graph — causal event chains | cause, effect, book, planted |

**Total points (as of April 2026):** 52,781+  
**Seed command:** `python adamem_initializer.py --seed-only`  
**Migration command:** `python adamem_initializer.py --migrate-only`

## 9.6 Nemotron Router Cascade (4-Tier)

```
Tier 1: NVIDIA NIM — nvidia/nemotron-3-8b-base-4k (1M token context; 900K cap)
     ↓ (failover)
Tier 2: OpenRouter — nvidia/nemotron-4-340b-instruct
     ↓ (failover)
Tier 3: Local GGUF — llama-server :8780 (131,072 ctx; 600s timeout; CPU-only)
     ↓ (failover)
Tier 4: Ollama local — llama3.1 (~128K ctx)
```

**Environment variables required:** `NVIDIA_API_KEY`, `OPENROUTER_API_KEY` (in `.env` at project root)

## 9.7 n8n Workflows (14 Total)

| ID | Name | Webhook |
|----|------|---------|
| 3ZbHxaIS3vHGPNXx | TNC_WF0_CONDUCTOR | POST /webhook/conductor-dispatch |
| 4pctLpZeBZzs3hEQ | TNC_WF1_SWARM_DISPATCH | POST /webhook/swarm-dispatch |
| sxKHpffVlWomVjy0 | TNC_WF2567_ANALYSE_CHAPTER | POST /webhook/analyse-chapter |
| YcpyX6wXnrAjK359 | TNC_WF3_STORY_PROTOTYPE | POST /webhook/extract-story-prototype |
| 3Arf65KNgaWXHvsA | TNC_WF4_CONSTITUTION_UPDATER_V2 | POST /webhook/constitution-update |
| MDOr5EaOTOg7ghxa | TNC_WF6_IMAGE_PROMPT | POST /webhook/image-prompt |
| eTiFjMSRwvb4HMvr | TNC_WF8_SELF_REFINE | POST /webhook/refine-scene |
| IhXSpbND4ALuBBJ8 | TNC_WF9_KDP_ASSEMBLER | POST /webhook/kdp-assemble |
| rTtVfp6XzWN9Luro | TNC_WF10_NIGHTLY_AUDIT | Cron 02:00 + POST /webhook/nightly-continuity-prep |
| dQgY5SSCq1LyMEkG | TNC_WF11_SOCIAL_CONTENT | POST /webhook/social-content |
| 6lhSEXzWpJotIIlQ | TNC_WF12_SEO_SERIALIZATION | POST /webhook/seo-serialization |
| XTliifWSWfjldTfJ | TNC_WF13_NZ_GRANT_MONITOR | Cron 08:00 Mon + POST /webhook/nz-grant-check |
| OlncMJ1Rt5wJ5Oxx | TNC_WF_NEMOCLAW_FILE_EVENT | POST /webhook/nemoclaw-file-event |
| kZIN5HtNBBbrxc8b | TNC_WF_THEOLOGICAL_GUARD | POST /webhook/theological-guard |

**Deploy command:** `python n8n_deploy_workflows.py --force`

## 9.8 CRDT Canon Management

The swarm uses Conflict-free Replicated Data Types (CRDTs) for async agent outputs to prevent simultaneous edits corrupting canon documents. The `crdt_merge.py` module handles conflict resolution. `utility_server.py` exposes `/crdt-merge` endpoint. Agent 3 (Constitution Updater) proposes changes via CRDT before any SSOT write.

## 9.9 Swarm Health & Startup

```powershell
# Verify all ports listening:
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(8765,8766,8767,8768,8769,8770,8771,8772,8780) } | Select-Object LocalPort | Sort-Object LocalPort

# Start swarm if any port missing:
.\Start-TNCSwarm.ps1

# Full smoke test (6 phases):
python day1_ops.py --phase all
```

**VRAM note:** Server warns 16,803 MiB projected vs 8,915 MiB free at 25 GPU layers + 131,072 context. Loading succeeds via mmap. If OOM, reduce to `-ngl 15` or `-c 32768`.

---

# PART X: PRODUCTION PIPELINE

## 10.1 Manuscript Build System

```powershell
# Build KDP-compliant .docx for Book 3:
python build_manuscript.py --book 3

# Verify output:
python verify_docx.py --file output/book_3.docx
```

**Output:** KDP-compliant .docx assembled from `MANUSCRIPT/book_3/` markdown files  
**Book 3 status:** Verified April 2026 (139,424 words)

## 10.2 KDP Compliance Checklist

- [ ] Section breaks between chapters
- [ ] Title page with pen name (Kerman Gild) and copyright (Kerman Gild © 2026)
- [ ] No headers on chapter-opening pages
- [ ] 0.5-inch first-line paragraph indent throughout
- [ ] Font: Times New Roman 12pt body text
- [ ] Chapter headings match TOC
- [ ] Word count target: 120,000–180,000 words per book

## 10.3 Canon Ingestion Pipeline

```powershell
# Ingest new canon doc into Qdrant:
python ingest_canon.py --file CANON/NEW_DOCUMENT.md

# Specialized ingestor (Jubilees):
python ingest_jubilees.py

# Miriam dossier:
python ingest_miriam_dossier.py
```

## 10.4 Skills Auto-Invoke Table

These skills are automatically invoked when drafting any scene touching their domain:

| Skill | Auto-Invoke Trigger |
|-------|-------------------|
| `acoustic-check` | Any supernatural phenomenon, Watcher tech, angelic activity, dimensional transitions, weapon discharges, pulsing/glowing descriptions |
| `theological-guard` | Salvation, divine authority, villain redemption arcs, identity of Christ, Witnesses' nature, philosophical framing |
| `oiketerion-check` | Any scene where Watchers use abilities — verify they are using KNOWLEDGE, not innate power |
| `raphael-register` | Any Raphael/Liaigh dialogue — verify Empyreal Register compliance |
| `era-voice` | Historical flashback scenes — verify period-accurate language |
| `precision-anchor` | Any combat/action sequence — verify spatial geometry and tactical realism |

## 10.5 Nightly Audit

`TNC_WF10_NIGHTLY_AUDIT` runs at 02:00 daily. Outputs to `02_ANALYSIS/NIGHTLY_AUDIT_YYYY-MM-DD.md`. Reviews last 24 hours of manuscript changes for drift against SSOT_v3.

---

# PART XI: BUSINESS STRATEGY

## 11.1 Company Overview

| Field | Value |
|-------|-------|
| **Company** | Kerman Gild Publishing |
| **Location** | Auckland, New Zealand |
| **Mission** | "Epic Chronicles of Faith, History & Divine Providence" |
| **Focus** | High-stakes historical fiction integrating biblical archaeology with supernatural thriller pacing |
| **Current overhead** | $455,900 annually |
| **2026 revenue projection** | $1,054,420 |
| **EBITDA target** | 40–45% by 2028 |

## 11.2 Product Portfolio

| Product | Series | Price Point | Status |
|---------|--------|-------------|--------|
| The Cydonian Oaths | Nephilim Ch. Book 1 | Fiction ($2.70/unit KDP) | Published |
| The Cauldron of God | Nephilim Ch. Book 2 | Fiction | Published |
| The Edenic Mandate | Nephilim Ch. Book 3 | Fiction | KDP-Ready |
| The Stone and the Sceptre | Stone & Sceptre Book 1 | Fiction | Published |
| The Red Hand & The Eternal Throne | Stone & Sceptre Book 2 | Fiction | Published |
| **Business Guide** | Non-fiction | **$3,499 ASP** | **Primary revenue lever** |
| Literary Magazine | Subscription | DTC gated | In development |

**Revenue density insight:** The Business Guide at $3,499 ASP generates more monthly gross profit with 2 extra sales than the Literary Magazine does with 20,000 units.

## 11.3 Revenue Strategy (Four Levers)

| Lever | Mechanism | Target |
|-------|-----------|--------|
| **DTC Migration** | Proprietary website ($10,000 investment); bypass 11% variable sales fees | Primary |
| **Print Cost Floor** | Negotiate 10% reduction in print/bind costs | $150/unit floor |
| **Tiered Subscriptions** | Gate scientific and literary content for recurring revenue | MRR growth |
| **Operational Lag** | Delay Sales/Distribution Manager hire until 2028 | $35,000 savings 2027 |

## 11.4 Digital Marketing

### YouTube / TikTok Strategy

| Platform | Tactic | Target |
|----------|--------|--------|
| **YouTube** | "Super + Nano" content: Nemotron 3 Super-powered long-form anchor content + high-volume short clips | Brand authority + top-of-funnel |
| **TikTok Shop** | Affiliate outreach to #BookTok niche communities | 400–600% sales increase potential |
| **Marketing spend** | Reallocated from 30% → **15% of revenue** (surgical targeting) | Lower CPA |

### SEO & Serialization

- Professional keyword research targeting **300% increase in search visibility**
- Digital asset serialization via DTC platform for recurring engagement
- Agent 9 (Content Strategist) monitors SEO performance daily

## 11.5 New Zealand Grants & Institutional Support

| Organization | Purpose |
|-------------|---------|
| **Mātātuhi Foundation** | Project-specific funding; NZ literary heritage; regional readership |
| **NZ Society of Authors (NZSA)** | Contract legal advice; manuscript assessments |
| **The Coalition for Books** | KETE marketing platform for national profile of historical titles |
| **NZAMA** | External feedback for historical accuracy |

**Monitoring:** Agent 9 runs NZ Grant Monitor (TNC_WF13) every Monday 08:00, POST /webhook/nz-grant-check.

## 11.6 Print Strategy

- **POD-First (Print-on-Demand):** Eliminates warehousing and inventory risk for fiction
- Traditional print runs of 10,000 units would tie up $1.5M in capital — avoided
- Business Guides: "confirmed demand" production model only

---

# PART XII: REFERENCE & STYLE GUIDES

## 12.1 Combat Style Guide (Mandatory for All Action Sequences)

**Genre mandate:** "Tom Clancy meets Frank Peretti." Every combat sequence must deliver: tactical realism + mythic weight + cosmic stakes + metaphysical logic + cinematic spectacle.

### Mortal Plane Author Models

| Element | Model Author |
|---------|-------------|
| Tactical planning / operational briefings | Tom Clancy |
| Precision marksmanship, bolt cycling | Stephen Hunter |
| One-vs-many methodical kill progressions | Mark Greaney |
| CQB, veteran psychology, "cognitive fossil" | Jack Carr |
| Sword choreography — Mo Chrá as active character | R.A. Salvatore |

### Celestial Plane Author Models

| Element | Model Author |
|---------|-------------|
| Angelic/demonic hierarchy logic | C.S. Lewis |
| Visible angelic combat, dual-plane storytelling | Frank Peretti |
| Spycraft + spiritual conflict, occult physics as hard science | Tim Powers |
| Cosmic scale, ancient grudges, reality-warping impact | Steven Erikson |
| Sensory surrealism, symbolic battlefields | Ted Dekker |
| Quiet terror of celestial beings, mythic minimalism | Neil Gaiman |
| Non-anthropomorphic cherubim, scale-shifting battles | Madeleine L'Engle |
| Divine council, territorial spirits, cosmic geography | Michael Heiser |

### Pre-Action Scene Checklist

- [ ] Spatial geometry of battlefield perfectly clear?
- [ ] Gear/weapons treated with Clancy-level technical respect?
- [ ] Melee fluid, spatially precise, emotionally grounded (Salvatore/Mo Chrá)?
- [ ] Supernatural warfare follows strict rules and jurisdictions (Powers/Heiser)?
- [ ] **Acoustic Paradigm is the driving force of all supernatural elements?**
- [ ] Dual-plane storytelling: celestial war visibly impacts mortal operators?
- [ ] Celestial entities have "quiet terror," not human familiarity (Gaiman)?

## 12.2 Prose Register Guide

| POV / Context | Register |
|--------------|---------|
| Cian internal monologue | World-weary, poetic, Irish cadence; sardonic humor hiding grief |
| Cian dialogue | Sharp, occasionally sarcastic; Celtic idioms; direct |
| Raphael / Liaigh speech | Empyreal Register (MANDATORY): thee/thou, ALL CAPS proclamations, divine gravitas |
| Enoch dialogue | Archaic, precise; the scribe's cadence; meticulous |
| Elijah dialogue | Prophetic, declarative, uncompromising |
| Miriam dialogue | Analytical, precise; intelligence-community cadence |
| Brennan dialogue | Engineering Neurosis voice; exponentially escalating detail; comic foil to Cian's Tactical Deadpan |
| Narrative / description | Literary historical fiction — dense, evocative, grounded. NOT genre pulp. |

## 12.3 The Phantom Banter Protocol (Books 3-5)

During Operational Silence (Book 3 Ch14 → Book 5 Ch10), Cian uses "Phantom Banter" — mimicking Liaigh's Empyreal Register in campfire stories and briefing-room anecdotes. Mo Chrá reacts as comedic straight man. **Comedy always ends with grief.** This is the primary tool for maintaining the Raphael relationship's emotional presence despite the communication severance.

## 12.4 Visual Direction Reference

Two visual languages in the series:

| Language | Context | Style |
|----------|---------|-------|
| **Mortal Plane** | Human world scenes | Cinematic realism; high-contrast shadows; documentary precision |
| **Celestial Plane** | Angelic/demonic reality | Geometric precision + overwhelming scale; non-human proportions; acoustic light |

**Principle:** Celestial entities are never humanized visually. Cherubim are not beautiful winged humans — they are terrifying multi-faced wheel-within-wheel beings. Raphael's physical form in combat is not described in human terms.

## 12.5 Pre-Draft Verification Checklist

Before writing any scene:

- [ ] Character ages/states match SSOT_v3?
- [ ] Timeline placement correct?
- [ ] Raphael's Three Limitations respected?
- [ ] Empyreal Register used for angelic dialogue?
- [ ] Acoustic Paradigm maintained (all supernatural follows acoustic root)?
- [ ] Azazel confirmed as NEPHILIM (son of Gadreel), NOT a Watcher?
- [ ] No Trinitarian language? (Binitarian Godhead per §1.4)
- [ ] No "Unholy Trinity" language? (Use "Satanic Triumvirate" or "command triad")
- [ ] Brennan's name: "McNeeve" (NOT "Webb")?
- [ ] No contradictions with published Book 1 or Book 2?

---

# APPENDIX A: LOCKED FACTS QUICK REFERENCE

The following facts are INVIOLABLE. Any content contradicting these must be corrected immediately.

| Fact | Value | Source |
|------|-------|--------|
| Cian's Commission date | **586 BCE** | SSOT §2.2 |
| Sword naming date | **532 CE** (Constantinople, Nika Riots) | SSOT §4.3 |
| Cian's aging rate | **1 biological year per 1,000 chronological years** | SSOT §4.1 (locked Feb 2026) |
| Cian's age (2025) | **2,636 chronological years; ~28-30 biological** | SSOT §4.1 |
| Titan-1–5 Launch | **October 15, 2026** | SSOT §2.2 |
| Titan fleet Mars arrival | **May 2027** | SSOT §2.2 |
| Brennan's surname | **McNeeve** (NOT "Webb") | SSOT §4.5 |
| Azazel's identity | **NEPHILIM** son of Gadreel (NOT a Watcher) | SSOT §3.1 |
| Azazel's cover name | **"Dr. Ezra Adon"** | SESSION_STARTUP |
| The Dragon | **SATAN** | SSOT §3.1 |
| The Beast | **OHYA** (son of Shemyaza and Naamah) | SSOT §3.1 |
| The False Prophet | **AZAZEL** | SSOT §3.1 |
| The Whore of Babylon | **NAAMAH** | SSOT §3.1 |
| The Godhead | **Binitarian** (Father + Son; Holy Spirit is NOT a Person) | SERIES_BIBLE §1.4 |
| "Unholy Trinity" | **FORBIDDEN** — use "Satanic Triumvirate" | SERIES_BIBLE §1.4 |
| Watcher descent date | **3504 BCE** | SSOT §2.1 |
| The Flood date | **2348 BCE** | SSOT §2.1 |
| Demons are | **Nephilim spirits** (NOT fallen angels) | SERIES_BIBLE §2.6 |
| Watcher wives became | **Sirens** (transformed, not drowned) | SERIES_BIBLE §2.6 |
| Raphael's name (Cian POV) | **"Liaigh"** — inviolable until Book 5 Ch10 | SSOT §4.2 |
| Raphael's Three Limitations | The Ban / Heavenly Liturgy / Name Consequence | SSOT §4.2 |
| Cian's death | Falls protecting the Witnesses; rises at Last Trump | SSOT §3.3 |
| Miriam's death | ~Day 1,050 of 1,260-day ministry; orphaned daughter | SSOT §3.3 |
| Vârcolac's status | **DEAD** (killed Book 1) | VARCOLAC_STATUS_DEAD.md |
| Eden time dilation | **Narnia-style** (days in Eden = weeks/months on Earth) | SESSION_STARTUP |
| Op Silence seed chapter | **Book 3 Ch12** (NOT Ch10) | OPERATIONAL_SILENCE.md |
| Op Silence severance | **Book 3 Ch14** | SSOT §4.2 |
| Mo Chrá kill count (Cian) | ~50,000 supernatural entities | SSOT §4.3 |
| Mo Chrá kill count (Methuselah) | 980,000 Nephilim spirits | SSOT §4.3 |
| Mo Chrá appearance | Dark grey/black; 54 inches; 6.2 pounds | SSOT §4.3 |
| Miriam's lineage to Niamh | **NONE** | SSOT §4.4 |
| Angels created on | **Day 1** of Creation (Jubilees 2:2) | SERIES_BIBLE §2.2 |
| Lamech of Naamah | **CAINITE Lamech** (NOT Noah's father) | SERIES_BIBLE §2.5 |
| Book 3 baptism chapter | **Ch10** | SESSION_STARTUP |
| Series present day | **2024+** (NOT 2020 as series start) | SSOT §2.2 |

---

# APPENDIX B: CANON DRIFT WATCH

Known drift errors — correct immediately if encountered:

| Error | Correction | Source of Truth |
|-------|-----------|-----------------|
| "Brennan Webb" | **Brennan McNeeve** (full: Brennan mac Niamh McNeeve) | SSOT §4.5 |
| "Azazel is a Watcher" | Azazel is a **NEPHILIM** — son of Gadreel (who IS a Watcher chief) | SSOT §3.1 |
| "Unholy Trinity" | **Satanic Triumvirate** or "command triad" | SERIES_BIBLE §1.4 |
| "The Trinity" / "Third Person" | **Binitarian Godhead** — Holy Spirit is essence, not Person | SERIES_BIBLE §1.4 |
| Miriam descended from Niamh | **False** — Miriam has NO bloodline connection to Niamh | SSOT §4.4 |
| Op Silence seeds at Ch10 baptism | Seed was **moved to Ch12** (Briefing end) | OPERATIONAL_SILENCE.md |
| Book 1 opens in 2020 | Book 1 Ch1 vision: **January 2024** | SSOT §2.2 |
| Cian aging at normal human rate | **1 year per 1,000 years** (locked Feb 2026) | SSOT §4.1 |
| Liaigh/Raphael calls Cian by first name | **Never** — always "Warrior," "Guardian," "Thee/Thou" — no first name in Empyreal Register until Book 5 Ch10 (and then only in normal voice) | SSOT §4.2 |
| Demons = fallen angels | **False** — demons are Nephilim spirits; fallen angels are the Watchers, in Tartarus | SERIES_BIBLE §2.6 |
| Watcher wives drowned in Flood | **False** — transformed into Sirens (still exist post-Flood) | SERIES_BIBLE §2.6 |
| Vârcolac still alive in Book 2+ | **False** — killed in Book 1 | VARCOLAC_STATUS_DEAD.md |
| Raphael can enter Cydonia-1 | **False** — acoustical wards (Limitation 1 exception category) | SSOT §4.2 |

---

# APPENDIX C: PROJECT FILE STRUCTURE

```
nephilim_chronicles/
├── MASTER_LORE_BOOK.md          ← This file
├── CLAUDE.md                    ← AI session instructions (1M window)
├── .github/copilot-instructions.md  ← GitHub Copilot context
│
├── CANON/                       ← Tier 1-2 canonical documents
│   ├── SERIES_BIBLE.md          ← INVIOLABLE Constitutional axioms
│   ├── SSOT_v3_MASTER.md        ← Consolidated factual canon (v3.2)
│   ├── WATCHER_TECHNOLOGY.md    ← Acoustic Paradigm & Watcher tech
│   ├── NARRATIVE_BRIEFING_SERIES_CONTINUITY.md
│   └── dossiers/                ← Character dossiers
│       ├── WATCHER_DOSSIERS.md
│       ├── NEPHILIM_DOSSIERS.md
│       ├── PROTAGONIST_DOSSIERS.md
│       └── ANTAGONIST_DOSSIERS.md
│
├── MANUSCRIPT/
│   ├── book_1/                  ← Published (Tier 0)
│   ├── book_2/                  ← Published (Tier 0)
│   └── book_3/                  ← KDP-Ready; drafting
│       ├── CHAPTERS/
│       │   ├── prologue.md
│       │   ├── CHAPTER_01_TheArchitectureOfResistance.md
│       │   ├── CHAPTER_02_TheFrequencyBeneathTheCure.md
│       │   ├── CHAPTER_03_TheLastCartography.md
│       │   ├── CHAPTER_04_TheGauntlet.md
│       │   ├── CHAPTER_05_TheLogisticsOfMercy.md
│       │   └── CHAPTER_06_TheBurningChoir.md
│       └── ANALYSIS/
│           └── DOPAMINE_LADDER_READER_REACTION_MATRIX_BOOK_3_COMPLETE.md
│
├── WORLDBUILDING/
│   ├── FIVE_BOOK_STRUCTURE.md
│   ├── BOOKS_3_5_ARCHITECTURE.md
│   ├── THE_CYDONIA_REVELATION.md
│   ├── AZAZELS_PRISON_DUDAEL_ANTARCTICA.md
│   └── SYNAGOGUE_OF_SATAN_THIRTEEN_HOUSES.md
│
├── REFERENCE/
│   └── COMBAT_STYLE_GUIDE.md
│
├── BUSINESS/
│   ├── business_plan.md
│   ├── 2026_profitability_agentic_strategy_blueprint.md
│   └── strategic_profit_maximization_ai_integration_plan.md
│
├── ARCHIVE/
│   ├── session_logs/            ← SESSION_LOG_YYYY-MM-DD.md
│   ├── superseded/              ← Old versions with timestamps
│   └── book_1_chapters/
│
├── LOGS/                        ← Day1 ops, nightly audits
├── INFRA/                       ← Infrastructure scripts
├── 02_ANALYSIS/                 ← Nightly audit outputs
├── 03_IMAGE_PROMPTS/
├── STAGING/
├── TRIAGE/
├── ASSETS/
│   ├── covers/
│   └── maps/
│
├── CREATIVE_SWARM_ARCHITECTURE_v2.md
├── N8N_AGENT_WIRING.md
├── build_manuscript.py
├── canon_search_api.py
├── ingest_canon.py
├── adamem_initializer.py
├── nemoclaw_daemon.py
├── day1_ops.py
└── Start-TNCSwarm.ps1
```

---

*End of Master Lore Book — April 19, 2026*  
*Maintained by: Chris Modina / Kerala Gild Publishing*  
*Update protocol: Edit this file directly when canon is confirmed; archive superseded content to ARCHIVE/superseded/*
