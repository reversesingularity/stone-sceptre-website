---
name: seo-matrix-generator
description: Generates SEO-optimized landing page variations using the Zipper Approach (Niche × Theme). Use when asked to "generate landing pages", "build SEO matrix", or "scale SEO".
---

# SEO Landing Page Matrix Generator

## The Zipper Approach
Combine two variables — **Demographic** and **Theme** — to produce hyper-targeted exact-match landing pages. Each page captures a specific search intent and immediately validates it in the headline.

## Kerman Gild Default Matrix

| | Nephilim & Fallen Angels | Spiritual Warfare | End-Times Eschatology |
|---|---|---|---|
| **Christian Fiction Readers** | `/landing/christian-fiction-nephilim/` | `/landing/christian-fiction-spiritual-warfare/` | `/landing/christian-fiction-end-times/` |
| **Historical Fantasy Fans** | `/landing/historical-fantasy-nephilim/` | `/landing/historical-fantasy-spiritual-warfare/` | `/landing/historical-fantasy-end-times/` |
| **Biblical Prophecy Enthusiasts** | `/landing/biblical-prophecy-nephilim/` | `/landing/biblical-prophecy-spiritual-warfare/` | `/landing/biblical-prophecy-end-times/` |

## Execution Steps

1. **Confirm the matrix variables** with the user (or use defaults above).
2. **Scaffold the HTML template** for each Demographic × Theme cell:
   - File path: `/landing/[demographic-slug]-[theme-slug]/index.html`
   - Inline `<style>` block — no external CSS file for zipper pages (reduces HTTP requests)
   - Single external script reference: `../../shared/analytics.js` (deferred)
3. **Inject localized copy** so these exact elements match the target query:
   - `<title>` — 50–60 chars, includes both demographic and theme keywords
   - `<meta name="description">` — 150–160 chars, action-oriented
   - `<h1>` — exact-match headline (e.g., "Christian Historical Fantasy: The Nephilim Chronicles")
   - Hero paragraph — 2–3 sentences validating the visitor's search intent
4. **Internal linking:** Each zipper page links back to `/index.html` (publisher hub) using a "Explore All Series" anchor. No cross-links between zipper pages (prevents cannibalization).
5. **Canonical tag:** `<link rel="canonical" href="https://kermangildpublishing.org/landing/[slug]/">` on every zipper page.

## HTML Template Skeleton
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[DEMOGRAPHIC] [THEME] — The Nephilim Chronicles | Kerman Gild Publishing</title>
  <meta name="description" content="[150-160 char action-oriented description]">
  <link rel="canonical" href="https://kermangildpublishing.org/landing/[slug]/">
  <style>/* inline critical CSS */</style>
</head>
<body>
  <header>
    <h1>[Exact-Match H1]</h1>
    <p>[2-3 sentence intent-validation paragraph]</p>
    <a class="cta-primary" href="/index.html#bundles">Shop Chronicle Bundles</a>
  </header>
  <!-- S-Tier trust elements -->
  <section aria-label="Author introduction">
    <div class="video-placeholder"><!-- Author video --></div>
  </section>
  <section aria-label="Reader testimonials">
    <!-- 3× testimonial placeholders -->
  </section>
  <footer>
    <a href="/index.html">Explore All Series — Kerman Gild Publishing</a>
  </footer>
  <script src="../../shared/analytics.js" defer></script>
</body>
</html>
```
