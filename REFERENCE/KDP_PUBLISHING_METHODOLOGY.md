# KDP Publishing Methodology — The Nephilim Chronicles

**Established:** Books 1 & 2 (The Cydonian Oaths / The Cauldron of God)
**Last Updated:** April 7, 2026
**Purpose:** Repeatable playbook for assembling any TNC book from manuscript → KDP-ready .docx + images

---

## TABLE OF CONTENTS

1. [Overview — The Full Pipeline](#1-overview)
2. [Manuscript Structure & File Conventions](#2-manuscript-structure)
3. [Image Pipeline (Generate → Upscale → KDP-Ready)](#3-image-pipeline)
4. [build_manuscript.py — The Assembly Engine](#4-build-engine)
5. [KDP Format Server (n8n Integration)](#5-kdp-format-server)
6. [KDP Specifications (Paperback & eBook)](#6-kdp-specifications)
7. [Pre-Submission Checklist](#7-pre-submission-checklist)
8. [Troubleshooting & Lessons Learned](#8-troubleshooting)

---

## 1. OVERVIEW

The publishing pipeline has four stages:

```
WRITE chapters (.md)  →  GENERATE images (Midjourney)  →  UPSCALE + RESIZE  →  BUILD .docx
```

All tooling is local. No cloud dependencies except Midjourney for image generation.

**Key tools:**
- `build_manuscript.py` — Python script that assembles markdown chapters + images → KDP-compliant .docx
- `kdp_format_server.py` — HTTP wrapper (port 8766) so n8n can trigger builds via webhook
- `resize_to_kdp.ps1` — PowerShell script that takes upscaled images → KDP-ready dimensions
- `realesrgan-ncnn-vulkan.exe` — AI upscaler (Real-ESRGAN, portable, no CUDA required)
- ImageMagick (`magick`) — Final resize + DPI embedding + format conversion

**Python dependencies:** `python-docx`

---

## 2. MANUSCRIPT STRUCTURE

### Directory Layout (Per Book)

```
MANUSCRIPT/
  book_N/
    CHAPTERS/
      BOOK_N_FRONT_MATTER.md        ← Title page, copyright, dedication, TOC, epigraphs
      PROLOGUE_SCENE1_Title.md
      PROLOGUE_SCENE2_Title.md       ← (if multi-scene prologue)
      CHAPTER_01_Title.md
      CHAPTER_02_Title.md
      ...
      CHAPTER_NN_Title.md
      EPILOGUE_Title.md
      BOOK_N_APPENDICES.md
      README.md                      ← Chapter manifest / notes
    IMAGES/
      chapters/                      ← Raw generated images (Midjourney output)
      covers/                        ← Cover art (raw)
      upscaled/                      ← 4x AI-upscaled versions (regenerable, .gitignored)
        chapters/
        covers/
      kdp_ready/                     ← Final KDP-spec images (regenerable from upscaled)
        chapters/
        covers/
      tools/                         ← Real-ESRGAN binary + models (.gitignored)
      resize_to_kdp.ps1              ← PowerShell resizer script
    IMAGE_PROMPTS/
      PROLOGUE_I_Title.md            ← Per-chapter Midjourney prompt + visual concept
      CHAPTER_01_Title.md
      ...
      MAP_01_Title.md
      BOOK_N_IMAGE_PROMPTS_SAMPLES.md  ← Master prompt reference with aesthetic notes
```

### Markdown Chapter Format

Each chapter .md file follows this structure:

```markdown
# CHAPTER TITLE
## Subtitle (optional)

First paragraph of body text (no first-line indent applied).

Subsequent paragraphs get 0.3" first-line indent automatically.

**Bold text** and *italic text* and ***bold-italic*** are supported inline.

---

Scene breaks use triple dashes (converted to ✦ centered glyph).

| Tables | Are | Supported |
|--------|-----|-----------|
| For    | appendices | data |
```

### Front Matter Template

The front matter file uses `## PAGE N: LABEL` markers to delineate pages:

```markdown
## PAGE 1: SERIES HALF-TITLE
## PAGE 2: ALSO BY
## PAGE 3: FULL TITLE PAGE
## PAGE 4: COPYRIGHT
## PAGE 5: DEDICATION
## PAGE 6: BLANK
## PAGE 7: EPIGRAPH
## PAGE 8: TABLE OF CONTENTS
## PAGE 9: PREFACE (optional)
```

Each page auto-receives a page break before it. The builder parses these markers and applies specific formatting per page type (see `build_front_matter()` in build_manuscript.py).

### Source File Assembly Order

Defined in `SOURCE_FILES_BOOK{N}` list in build_manuscript.py. **Order matters** — this is the exact sequence pages appear in the final .docx. When adding Book 3, duplicate the pattern and update filenames.

### Chapter–Image Mapping

The `CHAPTER_IMAGE_MAP` dictionary maps chapter filename prefixes to image filenames:

```python
CHAPTER_IMAGE_MAP = {
    "PROLOGUE_SCENE1": "prologue1.png",
    "PROLOGUE_SCENE2": "prologue2.png",
    "CHAPTER_01": "chapter1.png",
    ...
    "CHAPTER_07_5": "chapter7_5.png",   # ← longer prefix BEFORE shorter
    "CHAPTER_07": "chapter7.png",
    ...
    "EPILOGUE": "epilogue.png",
}
```

**Critical:** Longer prefixes must appear before shorter ones (e.g., `CHAPTER_07_5` before `CHAPTER_07`) because matching is prefix-based.

Map images are listed separately in `MAP_IMAGES` and rendered in a dedicated Maps section after the epilogue.

---

## 3. IMAGE PIPELINE

### Stage 1: Generate (Midjourney v6.1)

**Aesthetic continuity:** See `REFERENCE/VISUAL_DIRECTION.md` and `IMAGE_PROMPTS/BOOK_N_IMAGE_PROMPTS_SAMPLES.md`

**Core visual language:**
- Deep space blacks, celestial golds, amber bioluminescence
- "Balanced Splinter Cell tactical atmosphere + Ancient Future aesthetic"
- Sacred geometry, structures built for giants
- `--ar 9:16` for chapter art (vertical), `--ar 2:3` for covers, `--ar 16:9` for establishing shots
- `--v 6.1 --s 250`
- Always include: `--no text, words, letters, no bright colors, no fantasy creatures`

**Per-chapter prompt files** live in `IMAGE_PROMPTS/` with this structure:
```
**Chapter:** Chapter N — Title
**POV:** Character — context
**Key moment:** The visual concept description
**Visual concept:** Detailed art direction

/imagine prompt text here --ar 9:16 --v 6.1 --s 250 --no text, words, letters...

**Alternative — Variant Name:**
/imagine alternative prompt...

**Iteration tips:**
- Adjustment guidance for common generation issues
```

**Per-book visual continuity table** should be maintained comparing Book N vs Book N+1 (palette, threat scale, character bearing, chapter art style).

### Stage 2: Upscale (Real-ESRGAN 4x)

**Tool:** `realesrgan-ncnn-vulkan.exe` (portable binary, Vulkan GPU acceleration)
**Location:** `MANUSCRIPT/book_N/IMAGES/tools/`
**Model:** `realesrgan-x4plus` (best for realistic/photographic content)

**Command — Single image:**
```powershell
.\realesrgan-ncnn-vulkan.exe -i input.jpg -o output.png -n realesrgan-x4plus -s 4
```

**Command — Batch (entire folder):**
```powershell
.\realesrgan-ncnn-vulkan.exe -i chapters -o ..\upscaled\chapters -n realesrgan-x4plus -s 4 -f png
.\realesrgan-ncnn-vulkan.exe -i covers -o ..\upscaled\covers -n realesrgan-x4plus -s 4 -f png
```

**Notes:**
- Input: Midjourney raw output (~1024px)
- Output: 4x upscaled (~4096px), PNG format for lossless quality
- The `upscaled/` folder is .gitignored (regenerable from raw + tool)
- The `tools/` folder is .gitignored (downloadable binary)
- Uses Vulkan GPU — works on AMD/NVIDIA/Intel without CUDA
- Processes images as tiles, may introduce slight tile boundaries on very large images

### Stage 3: Resize to KDP Specs (ImageMagick)

**Script:** `MANUSCRIPT/book_N/IMAGES/resize_to_kdp.ps1`
**Requires:** ImageMagick (`magick` on PATH)

**What it does:**

| Image Type | Target Dimensions | DPI | Format | Notes |
|-----------|-------------------|-----|--------|-------|
| Kindle eBook cover | 1600 x 2560 px | 300 | JPG | RGB |
| Paperback full wrap | 4125 x 2775 px | 300 | JPG + PDF | PDF in CMYK colorspace |
| Interior chapter art | max 1650px wide | 300 | PNG | Maintains aspect ratio |
| Interior maps | max 1650px wide | 300 | PNG | Same as chapter art |

**Key commands used:**
```powershell
# Cover (exact dimensions, stretch to fit)
magick input.png -resize 4125x2775! -density 300 -units PixelsPerInch -quality 100 output.jpg

# Interior (max width, maintain aspect ratio, Lanczos filter for quality)
magick input.png -filter Lanczos -resize "1650x>" -density 300 -units PixelsPerInch -quality 100 output.png

# CMYK PDF for print cover
magick input.png -resize 4125x2775! -density 300 -units PixelsPerInch -colorspace CMYK output.pdf
```

**Interior image width rationale:** 5.5" printable area × 300 DPI = 1650px max. Maintaining aspect ratio prevents distortion.

**Output location:** `MANUSCRIPT/book_N/IMAGES/kdp_ready/chapters/` and `kdp_ready/covers/`

---

## 4. BUILD ENGINE — build_manuscript.py

### How to Run

```powershell
# Book 1
python build_manuscript.py

# Book 2
$env:KDP_BOOK = "2"; python build_manuscript.py

# Custom paths
$env:KDP_BOOK = "3"
$env:KDP_MANUSCRIPT_DIR = "path\to\book_3\CHAPTERS"
$env:KDP_OUTPUT_FILE = "path\to\output.docx"
python build_manuscript.py
```

### Page Format

| Property | Value |
|----------|-------|
| Trim size | 6" × 9" (KDP Paperback) |
| Top margin | 0.75" |
| Bottom margin | 0.75" |
| Inside margin (gutter) | 0.875" |
| Outside margin | 0.5" |
| Body font | Georgia 12pt |
| Line spacing | 15pt exactly |
| First-line indent | 0.3" (suppressed on first paragraph after heading/break) |
| Heading font | Georgia 20pt bold, centered |
| Scene break glyph | ✦ (centered) |

### Headers & Footers

- **Odd/even page headers enabled** (mirror margins for binding)
- **Verso (left/even pages):** Author name (KERMAN GILD) — left aligned, 9pt
- **Recto (right/odd pages):** Book title — right aligned, 9pt
- **Footer:** Centered page number, 9pt
- **First page of each chapter:** No footer (blank — chapter opener convention)
- **Chapter starts:** Always on recto (odd-page section break)

### Image Embedding

- Chapter art is embedded on its own page **before** the chapter heading
- Images use **floating anchor** (wp:anchor) with `wrapTopAndBottom` — this prevents paragraph line-spacing from clipping the image
- Centered horizontally and vertically within margin area
- Max dimensions: 4.5" wide × 6.5" tall (maintains aspect ratio)
- Maps section uses inline images (no floating), max 4.5" × 7.0"
- Custom "Chapter Image" paragraph style: single line spacing, centered, no indent, 36pt space after

### Table of Contents

- TOC entries in front matter use `PAGEREF` Word field codes linked to bookmarks
- Bookmarks auto-generated from chapter heading text (`_TOC_` prefix, alphanumeric + underscores)
- Page numbers display as "000" until Word recalculates fields (Ctrl+A → F9 in Word)
- Uses right-aligned tab stop with dot leader at 4.625" from left indent

### Markdown → DOCX Parsing Rules

| Markdown | DOCX Result |
|----------|-------------|
| `# Title` | Chapter heading (20pt bold centered, 2" top space) |
| `## Subtitle` | Chapter subtitle (12pt italic centered) |
| `## Location` (in body) | Scene location tag (12pt italic centered) |
| `---` or `***` | Scene break (✦ glyph) |
| `**text**` | Bold run |
| `*text*` | Italic run |
| `***text***` | Bold-italic run |
| `--` (bare) | Em dash (—) |
| Pipe tables | Word table (9pt, Table Grid style) |
| Code fences | Skipped (shouldn't appear in final manuscript) |
| Blockquotes `>` | Skipped (author notes) |
| `### headings` | Skipped in chapters; rendered as sub-headings in appendices |

### Adding a New Book

1. Create `MANUSCRIPT/book_N/CHAPTERS/` with all .md files
2. Add to build_manuscript.py:
   - `MANUSCRIPT_DIR_BOOK{N}` path constant
   - `OUTPUT_FILE_BOOK{N}` path constant
   - `SOURCE_FILES_BOOK{N}` list (assembly order)
   - Update `CHAPTER_IMAGE_MAP` if chapter structure differs
   - Add `BOOK_TITLES[N] = "Title"`
   - Add `elif book == N:` block in `main()`
3. Create `IMAGE_DIR_BOOK{N}` pointing to `kdp_ready/chapters/`
4. Run with `$env:KDP_BOOK = "N"`

---

## 5. KDP FORMAT SERVER

**File:** `kdp_format_server.py`
**Port:** 8766

HTTP wrapper so n8n workflows can trigger manuscript builds remotely.

```
POST http://localhost:8766/kdp-format
Body: {"book": 2}

GET  http://localhost:8766/health
```

Response:
```json
{
  "status": "ok",
  "output_file": "path/to/docx",
  "elapsed_seconds": 12.3,
  "log": "build output..."
}
```

---

## 6. KDP SPECIFICATIONS QUICK REFERENCE

### Paperback Interior

| Spec | Value |
|------|-------|
| Trim | 6" × 9" |
| Paper | Cream (fiction standard) |
| Bleed | No bleed (text-only interior) |
| Interior images | 300 DPI, max 1650px wide (5.5" print area) |
| File format | .docx (Word) — KDP converts to PDF internally |

### Kindle eBook Cover

| Spec | Value |
|------|-------|
| Dimensions | 1600 × 2560 px |
| DPI | 300 |
| Format | JPG |
| Color | RGB |

### Paperback Cover (Full Wrap)

| Spec | Value |
|------|-------|
| Dimensions | 4125 × 2775 px (back + spine + front + bleed) |
| DPI | 300 |
| Format | PDF (CMYK) or JPG (RGB fallback) |
| Spine | Calculated from page count — use KDP Cover Calculator |
| Bleed | 0.125" on all edges |

**Note:** Spine width varies by page count. For a 600-page book on cream paper, expect ~1.5" spine. Always use KDP's cover calculator for exact dimensions.

---

## 7. PRE-SUBMISSION CHECKLIST

### Manuscript (.docx)

- [ ] Open .docx in Word → Ctrl+A → F9 (update all fields — page numbers in TOC)
- [ ] Verify TOC page numbers are correct
- [ ] Check first/last pages visually — no blank pages where they shouldn't be
- [ ] Verify headers: author name on verso, book title on recto
- [ ] Verify no page numbers on chapter openers (first page of each chapter)
- [ ] Spot-check scene breaks (✦ glyph centered)
- [ ] Verify chapter images display correctly (not clipped)
- [ ] Check maps section at end (Book 2+)
- [ ] Run spell-check in Word
- [ ] Proof-read the entire manuscript (human eyes!)

### Images

- [ ] All chapter images present in `kdp_ready/chapters/`
- [ ] All at 300 DPI (verify with `magick identify -format "%wx%h %x DPI" file.png`)
- [ ] No image exceeds 1650px width for interiors
- [ ] Cover dimensions match KDP requirements exactly
- [ ] Cover PDF is CMYK colorspace

### KDP Upload

- [ ] Upload .docx as manuscript
- [ ] Upload cover PDF separately
- [ ] Preview in KDP Previewer — check every page
- [ ] Verify gutters / margins don't clip text
- [ ] Check image rendering in preview (especially chapter art)
- [ ] Set trim size to 6" × 9"
- [ ] Set paper type to Cream
- [ ] Set bleed to No Bleed

---

## 8. TROUBLESHOOTING & LESSONS LEARNED

### Image Clipping Bug (Book 2)
**Problem:** Chapter art images were being clipped by paragraph line-spacing.
**Solution:** Converted inline images to floating anchors (`wp:anchor` with `wrapTopAndBottom`). The `_convert_inline_to_floating()` function handles this. Maps keep inline display (they work fine without floating).

### CHAPTER_IMAGE_MAP Prefix Ordering
**Problem:** `CHAPTER_07` matched before `CHAPTER_07_5`, causing wrong image assignment.
**Solution:** Always list longer prefixes first in the dictionary. Python dicts preserve insertion order.

### TOC Page Numbers Show "000"
**Expected.** Word field codes need manual recalculation. Open .docx → Ctrl+A → F9 → confirm "Update entire table."

### Em Dash Conversion
The builder converts bare `--` to `—` (em dash). Source manuscripts should use `—` directly when possible, but `--` is caught as a fallback.

### Smart Quotes
Smart quotes in source .md files are preserved as-is. No conversion needed.

### .gitignore Strategy
These directories are regenerable and should NOT be committed:
```
MANUSCRIPT/book_N/IMAGES/tools/      # Real-ESRGAN binary (~50MB)
MANUSCRIPT/book_N/IMAGES/upscaled/   # 4x upscaled images (large)
```

The `kdp_ready/` folder IS committed — these are the final production-ready images.

### Dependencies
```
pip install python-docx
# ImageMagick must be on PATH (for resize_to_kdp.ps1)
# Real-ESRGAN binary in IMAGES/tools/ (download from GitHub releases)
```

---

*This methodology was developed across Books 1 and 2 of The Nephilim Chronicles. Apply it directly to Book 3 and beyond.*
