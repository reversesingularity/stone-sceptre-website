# TNC WORKFLOW RULES — The Boris Method
*Locked: March 15, 2026 · Applies to all Agent 1 sessions*

## CORE DIRECTIVE: CONTEXT IS KING
Everything must optimise the 200k-token context window. Ambiguous prompts
waste tokens on exploration. If instructions are vague, ask for specific
scope, patterns, and symptoms before generating long prose.

## 1. STRICT WORKFLOW: EXPLORE → PLAN → IMPLEMENT
For any complex drafting task, follow this sequence. Never skip to prose.
- **Explore:** Read provided context. Summarise current story state without
  changing anything.
- **Plan:** Propose a beat-by-beat outline. Iterate until solid.
- **Implement:** Execute prose only after explicit plan approval.

## 2. INTERVIEW MODE
Before writing a complex scene, interview Chris. Ask targeted questions
about implementation details, edge cases, character motivations, and
trade-offs. Only after gathering input, write the scene spec/outline.

## 3. SELF-CORRECTION LOOP
No one-shot drafts. Verify all output against:
- Established Nephilim lore and canon
- Agreed pacing from the outline
- Consistency with prior chapters
- Five drift categories (Acoustic, Oiketerion, Theological, Character, Timeline)
Iterate internally until the draft passes all checks before presenting.

## 4. NO KITCHEN-SINK SESSIONS
If the session bounces between brainstorming, editing, and drafting
unrelated chapters, context fills with irrelevant data and degrades.
Proactively advise Chris to start a fresh chat when:
- Switching to a different chapter
- Corrections keep repeating
- Context window is under pressure

## 5. SUBAGENT EMULATION
If a task requires analysing massive amounts of previous chapters, do not
mix it with drafting. Recommend a separate chat session as an isolated
audit agent. Bring only the compact summary back to the main session.

## 6. CONTEXT IS KING (ENFORCEMENT)
If instructions are vague or ambiguous:
- Ask for specific scope before generating
- Ask for patterns or symptoms before diagnosing
- Never produce long prose from unclear direction
- Ambiguity wastes tokens — clarity saves sessions
