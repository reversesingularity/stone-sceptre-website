---
name: page-cro
description: Optimizes static HTML landing pages for conversion performance. Use when asked to "optimize conversions", "improve landing page", or "implement CRO".
---

# Landing Page Conversion Optimization (CRO)

## Core Principles

1. **The Offer Formula:** Every hero section must contain a clear value proposition. For fiction: frame it as an experience promise with risk removal — e.g., "Enter an epic biblical saga of divine providence and cosmic war — or your money back."
2. **S-Tier Trust Elements:** The page must include:
   - Author/founder introduction video placeholder (`<div class="video-placeholder" aria-label="Author introduction video">`)
   - Reader video testimonial placeholders (minimum 3)
   - Risk-removal copy (explicit money-back or satisfaction guarantee)
   - Star ratings or review counts near the primary CTA
3. **Mobile-First CTA:** 64% of visitors arrive on mobile. Implement a sticky bottom bar (`position: fixed; bottom: 0`) visible only at `max-width: 768px`. It must contain the primary purchase CTA and never obscure content on desktop.
4. **Visual Hierarchy (Functional Layering):**
   - Single `<h1>` per page — the primary hook
   - Supporting `<h2>` subheadings every 300–400 words
   - High-contrast CTA buttons (minimum 4.5:1 contrast ratio)
   - Whitespace between sections: `padding-block: clamp(3rem, 8vw, 6rem)`

## Workflow

1. Read the current HTML structure of the target page.
2. Identify missing S-Tier elements (video, testimonials, risk removal, mobile CTA).
3. Inject the missing elements using semantic HTML5 — no JS required for static trust elements.
4. Verify the mobile sticky CTA is implemented with CSS only (no JS scroll listeners).
5. Run the `web-quality-audit` skill to confirm no regressions in performance or accessibility.

## Bundle Framing Rule
Never present individual books as isolated products. Always wrap in bundle language: "The Complete Nephilim Chronicles — Books 1–4 + Companion Guide."
