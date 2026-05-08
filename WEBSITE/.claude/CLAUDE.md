# Kerman Gild Publishing — Project Guidelines

## Tech Stack & Architecture

- **Core:** Pure static HTML5, modern CSS3 (CSS variables), Vanilla ES6+ JavaScript ONLY.
- **NO Frameworks:** No React, Vue, jQuery, or build tools (Webpack/Vite).
- **Fonts:** Google Fonts — Cinzel (headings, weights 400/600/700), Cormorant Garamond (body, ital+wght).
- **Design Philosophy:** Mobile-first, touch-first. Simplicity and readability over clever hacks.

## Complete File & URL Structure

```
/index.html                              ← Publisher hub (both series, bundles, author video)
/stone-and-sceptre/book1/               ← The Stone and the Sceptre: A Scribe's Tale (Available)
/stone-and-sceptre/book2/               ← The Red Hand & The Eternal Throne (Available)
/stone-and-sceptre/book3/               ← The Third Overturn (COMING SOON — email capture)
/nephilim/                               ← The Cydonian Oaths Book 1 (stays at this URL — do not move)
/nephilim/book2/                         ← The Cauldron of God (Available)
/nephilim/book3/                         ← The Edenic Mandate (Available)
/nephilim/book4/                         ← The Jerusalem Indictment (COMING SOON — email capture)
/nephilim/book5/                         ← Book 5 title TBD (COMING SOON — email capture)
/landing/[niche-slug]/                   ← SEO zipper matrix pages (9 total)
/shared/images/                          ← OG images, favicon
```

**Important:** `nephilim/index.html` is Book 1. Do NOT move it to `/nephilim/book1/` — the existing URL must be preserved. A duplicate `nephilim/book1/` directory was identified and permanently deleted (May 2026). The canonical Book 1 URL is `/nephilim/` and this mapping is locked.

**Note:** The book3 teaser section incorrectly named Book 4 as "The Testimony". The correct title is **The Jerusalem Indictment**. Any teaser copy referencing Book 4 must use this title.

## Series Identities

**Stone & Sceptre accent palette:** `--primary-gold: #d4af37`, `--dark-blue: #1a1a2e`, `--royal-purple: #4b0082`

**Nephilim Chronicles accent palette:** `--primary-gold: #c9871e`, `--dark-void: #0a0a0f`, `--teal-bright: #2a9d8f`

## High-Performance & Conversion Rules (S-Tier)

- **Page weight:** Total < 1.5 MB. All non-hero images use WebP + `loading="lazy"` + explicit `width`/`height`.
- **Hero image:** `fetchpriority="high"`, no `loading="lazy"`, explicit `width` and `height`.
- **Scripts:** All `<script>` tags must use `defer`. No render-blocking JS.
- **Scroll events:** Wrap ALL `window.addEventListener('scroll', ...)` calls in a `requestAnimationFrame` gate with `{ passive: true }`. Use one `ticking` boolean per handler — never share a single variable across handlers.
- **Mobile CTAs:** All sales pages must have a CSS-only sticky bottom bar (`position:fixed;bottom:0`) visible only at `max-width: 768px`. The bar must not overlap the scroll-to-top button — set scroll-top `bottom: calc(72px + 1rem)` on mobile.
- **S-Tier trust elements per page:** author/founder video placeholder, 3× reader testimonial placeholders, risk-removal copy, star-rating trust badge near primary CTA.
- **Coming Soon pages:** Use an email capture form with empty `action` attribute (placeholder for Mailchimp/ConvertKit URL). Do NOT use `mailto:` fallback — it destroys mobile UX.
- **Audiobook CTA:** `nephilim/index.html` must include a dedicated audiobook production banner between the hero buttons and the synopsis section. Form `action` is empty (TBD).

## Head Tag Requirements (every page)

1. `<link rel="preconnect" href="https://fonts.googleapis.com">` — BEFORE the Fonts stylesheet link
2. `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` — same
3. `<link rel="canonical" href="https://kermangildpublishing.org/[path]/">`
4. `og:image` (use real cover JPGs at 400×600 until 1200×630 OG images are produced) + `og:image:width` + `og:image:height`
5. `og:site_name` = "Kerman Gild Publishing"
6. Twitter Card block: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
7. `<script type="application/ld+json">` — `Book` schema on book pages, `Organization` on hub

## Accessibility Requirements (Lighthouse 100)

- Wrap all page content in a single `<main>` landmark (one per page; excludes `<header>` and `<footer>`)
- Series banner `<nav>` must have `aria-label="Series navigation"`
- All `<img>` must have descriptive `alt` text and explicit `width`/`height`
- Scroll-to-top buttons need `aria-label="Return to top"`
- Heading hierarchy must be sequential: `h1` → `h2` → `h3` (no skips per page)
- Interactive form inputs need `aria-label` or associated `<label>`

## Quality Gates (hard limits — must pass before any page ships)

| Metric | Target |
|---|---|
| Lighthouse Performance | ≥ 95 |
| Lighthouse Accessibility | 100 |
| Lighthouse SEO | 100 |
| LCP | ≤ 2.5 s |
| CLS | ≤ 0.1 |
| Page weight total | < 1.5 MB |
| CSS per page | < 100 KB |
| JS per page | < 300 KB |

## Series & Bundle Framing

- Frame books as bundles: "The Complete Nephilim Chronicles — Books 1–3 (Books 4–5 coming)"
- Cross-promote both series on the publisher hub
- Never present a book as an isolated product — always show the series context

## SEO Zipper Pages (future session)

- Target: 3 Demographics × 3 Themes = 9 landing pages minimum
- Demographics: Christian Fiction Readers, Historical Fantasy Fans, Biblical Prophecy Enthusiasts
- Themes: Nephilim & Fallen Angels, Spiritual Warfare, End-Times Eschatology
- Each page uses inline `<style>` only (no external CSS file), canonical tag, no cross-links between zipper pages
- Each zipper page `<title>`, `<h1>`, and hero copy must exactly match its Demographic × Theme query

## S-Tier Status (as of May 8, 2026)

All 5 book sales pages + publisher hub have reached full S-Tier baseline. No page is below standard.

| Page | `main` | JSON-LD | og:/Twitter | Canonical | Sticky CTA | Scroll-top | Trust | RAF JS | Cover img |
|------|--------|---------|-------------|-----------|------------|------------|-------|--------|-----------|
| `/index.html` (hub) | ✓ | ✓ Org | ✓ | ✓ | ✓ | ✓ | — | ✓ | — |
| `/nephilim/` (B1) | ✓ | ✓ Book | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/nephilim/book2/` | ✓ | ✓ Book | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/nephilim/book3/` | ✓ | ✓ Book | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/stone-and-sceptre/book1/` | ✓ | ✓ Book | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/stone-and-sceptre/book2/` | ✓ | ✓ Book | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Known Content Dependencies

- **Nephilim Book 1 cover:** `nephilim/images/book-cover.jpg` — directory created May 8 2026; cover file placed by Chris. All HTML paths (`<img>`, og:image, twitter:image) updated to this location. Do NOT reference `nephilim/book1/images/` — that directory was permanently deleted.
- **Stone & Sceptre Book 1 cover:** `stone-and sceptre/book1/images/book-cover.jpg` — file confirmed present. Currently used as CSS `background-url` on `.cover-background` div AND referenced in og:image meta tags.
- **Stone & Sceptre Book 2 cover:** `stone-and sceptre/book2/images/book-cover.jpg` — file confirmed present, used in `<img>` tag on the page.
- **OG images (1200×630):** Not yet produced. All pages currently use 400×600 book cover JPGs as temporary og:image values. When proper OG images are produced, update all og:image, og:image:width, og:image:height meta tags.
- **Amazon URLs:** All pages now use `amazon.com` (global). All `.com.au` links have been removed across the site.
- **Testimonials:** All 5 book pages have 3× `<blockquote>` placeholder cards. Replace placeholder text with verified Amazon reader reviews copied from each book's product page.
- **Video placeholders:** All 5 book pages have "From the Author" video section. Replace with actual embedded video when produced.

## Next Phase Targets (not yet built)

- `/stone-and-sceptre/book3/` — "The Third Overturn" COMING SOON email capture page
- `/nephilim/book4/` — "The Jerusalem Indictment" COMING SOON email capture page
- `/nephilim/book5/` — Book 5 (title TBD) COMING SOON email capture page
- `/landing/[niche-slug]/` — SEO Zipper Matrix (9 pages: 3 demographics × 3 themes). Invoke `/seo-matrix-generator` skill. Use Book 2 Nephilim page as structural template.
