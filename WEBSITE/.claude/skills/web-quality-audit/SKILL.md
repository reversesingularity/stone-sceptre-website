---
name: web-quality-audit
description: Audits HTML/CSS/JS code against Core Web Vitals and Lighthouse guidelines. Use when asked for a "quality review", "performance audit", or "lighthouse check".
---

# Web Quality and Core Web Vitals Audit

## Performance Thresholds (Hard Limits)
| Metric | Target | Fail Threshold |
|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5 s | > 4.0 s |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | > 0.25 |
| Total page weight | < 1.5 MB | > 2.0 MB |
| CSS total | < 100 KB | > 150 KB |
| JS total | < 300 KB | > 500 KB |
| Lighthouse Performance | ≥ 95 | < 90 |
| Lighthouse Accessibility | 100 | < 95 |
| Lighthouse SEO | 100 | < 95 |

## Validation Checklist

### Critical Rendering Path
- [ ] All `<script>` tags use `defer` or `async` (no render-blocking scripts)
- [ ] CSS is external and minified; no `@import` inside stylesheets
- [ ] No `document.write()` calls
- [ ] `<link rel="preconnect">` for Google Fonts

### Image Optimization
- [ ] Hero image: `fetchpriority="high"`, NO `loading="lazy"`, explicit `width` + `height`
- [ ] All non-hero images: `loading="lazy"`, explicit `width` + `height`, WebP format
- [ ] Book cover images include descriptive `alt` text (e.g., `alt="The Nephilim Chronicles Book 2 cover — a warrior angel above ancient ruins"`)
- [ ] No images sized > 300 KB after WebP conversion

### Accessibility (WCAG 2.2)
- [ ] Single `<h1>` per page; heading hierarchy is sequential (h1 → h2 → h3, no skips)
- [ ] All interactive elements reachable via keyboard (Tab order logical)
- [ ] All buttons and links have descriptive text (no "click here")
- [ ] Video placeholders have `aria-label` describing the content
- [ ] Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- [ ] Form inputs (if any) have associated `<label>` elements

### Vanilla JS Best Practices
- [ ] Scroll/resize handlers wrapped in `requestAnimationFrame`
- [ ] Touch and scroll event listeners registered with `{ passive: true }`
- [ ] No `setTimeout` used for layout calculations
- [ ] 3D cover-flip animations driven by CSS `transition`/`@keyframes`, not JS timers
- [ ] `IntersectionObserver` used for lazy-load triggers, not scroll events

### SEO
- [ ] `<title>` is 50–60 chars and unique per page
- [ ] `<meta name="description">` is 150–160 chars and unique per page
- [ ] `<link rel="canonical">` present on every page
- [ ] Open Graph tags present (`og:title`, `og:description`, `og:image`, `og:url`)
- [ ] Structured data (`application/ld+json`) for Book schema on all book pages
- [ ] Sitemap reference in `<head>` or robots.txt

## Audit Workflow
1. Read the target `index.html`, `styles.css`, and `script.js`.
2. Run through every checklist item above; note each pass/fail with the line number.
3. Report a summary table: Pass / Fail / Not Applicable per category.
4. For each Fail, output the corrected code snippet inline.
5. After applying fixes, confirm total estimated page weight is within limits.
