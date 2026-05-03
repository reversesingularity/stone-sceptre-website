"""KDP compliance audit — NephilimChronicles_Book3_MANUSCRIPT.docx"""
import zipfile, re, sys

DOCX = 'NephilimChronicles_Book3_MANUSCRIPT.docx'

def sep(title): print(f"\n{'='*60}\n  {title}\n{'='*60}")

z = zipfile.ZipFile(DOCX)
names = z.namelist()

# 1 ─── Required files
sep("1. REQUIRED FILES")
for f in ['word/document.xml','word/styles.xml','word/settings.xml',
          'word/numbering.xml','[Content_Types].xml']:
    status = "OK" if f in names else "MISSING ⚠"
    print(f"  {status:12} {f}")

doc  = z.read('word/document.xml').decode('utf-8')
styl = z.read('word/styles.xml').decode('utf-8')
sett = z.read('word/settings.xml').decode('utf-8')

# 2 ─── Page geometry
sep("2. PAGE GEOMETRY")
all_pgSz = re.findall(r'<w:pgSz\s+([^/]+)/>', doc)
if all_pgSz:
    first = all_pgSz[0]
    w_m = re.search(r'w:w="(\d+)"', first)
    h_m = re.search(r'w:h="(\d+)"', first)
    w = int(w_m.group(1)) if w_m else 0
    h = int(h_m.group(1)) if h_m else 0
    w_ok = "OK" if w == 8640 else f"WARN — got {w}, expect 8640"
    h_ok = "OK" if h == 12960 else f"WARN — got {h}, expect 12960"
    print(f"  Width : {w:5} twips = {w/1440:.3f}\"  (expect 6.000\")  {w_ok}")
    print(f"  Height: {h:5} twips = {h/1440:.3f}\"  (expect 9.000\")  {h_ok}")
    ornt = re.search(r'w:orient="(\w+)"', first)
    print(f"  Orient: {ornt.group(1) if ornt else 'portrait (default)'}")
else:
    print("  No <w:pgSz> found — WARN")

# 3 ─── Margins
sep("3. MARGINS (first sectPr)")
margin_match = re.search(r'<w:pgMar([^/]+)/>', doc)
if margin_match:
    mstr = margin_match.group(0)
    attrs = dict(re.findall(r'w:(\w+)="(\d+)"', mstr))
    specs = [
        ('top',    1080, '0.750"'),
        ('bottom', 1080, '0.750"'),
        ('left',   1260, '0.875" (inside/gutter)'),
        ('right',   720, '0.500" (outside)'),
        ('header',  720, '0.500"'),
        ('footer',  720, '0.500"'),
    ]
    for key, expect_twips, label in specs:
        v = attrs.get(key, 'N/F')
        ok = "OK" if str(v) == str(expect_twips) else f"WARN got {v}, expect {expect_twips}"
        print(f"  {key:8} = {str(v):5} twips  {label:35}  {ok}")
else:
    print("  Could not locate <w:pgMar> — WARN")

# 4 ─── Document settings
sep("4. DOCUMENT SETTINGS")
checks = [
    ('mirrorMargins',   'Mirror margins (required for print)'),
    ('evenAndOddHeaders','Even/odd headers'),
]
for tag, desc in checks:
    present = tag in sett
    status  = "YES" if present else "NO"
    flag    = "" if present else " ⚠"
    print(f"  {status:4}  {desc}{flag}")

# 5 ─── Fonts
sep("5. FONT USAGE")
style_fonts = set(re.findall(r'w:ascii="([^"]+)"', styl))
body_fonts  = set(re.findall(r'w:ascii="([^"]+)"', doc))
all_fonts   = style_fonts | body_fonts
print(f"  All fonts referenced: {sorted(all_fonts)}")
non_georgia = [f for f in all_fonts if 'Georgia' not in f]
if non_georgia:
    print(f"  Non-Georgia fonts: {non_georgia}")
    print("  NOTE: These may appear only in styles not used by body text — verify in Word")
else:
    print("  Georgia only — OK")

# 6 ─── TOC bookmarks
sep("6. TOC BOOKMARKS vs PAGEREFs")
bm_starts  = re.findall(r'w:name="(_TOC_[^"]+)"', doc)
pagerefs   = re.findall(r'PAGEREF (_TOC_\S+)', doc)
unresolved = [p for p in pagerefs if p not in bm_starts]
print(f"  Bookmarks defined : {len(bm_starts)}")
print(f"  PAGEREFs in TOC   : {len(pagerefs)}")
print(f"  Unresolved refs   : {len(unresolved)}  {'OK' if not unresolved else 'WARN ⚠'}")
for u in unresolved:
    print(f"    MISSING BM: {u}")
print()
print("  Bookmark inventory:")
for b in bm_starts:
    flag = " *** > 40 chars ⚠" if len(b) > 40 else ""
    print(f"    {len(b):2d}ch  {b}{flag}")

# 7 ─── Section breaks
sep("7. SECTION BREAKS")
odd  = len(re.findall(r'w:val="oddPage"', doc))
nxt  = len(re.findall(r'w:val="nextPage"', doc))
cont = len(re.findall(r'w:val="continuous"', doc))
even = len(re.findall(r'w:val="evenPage"', doc))
total_secPr = doc.count('<w:sectPr')
print(f"  Total sectPr elements : {total_secPr}")
print(f"  Odd-page   breaks: {odd:3}  (expect 18 for prologue+15ch+epilogue+appendices)")
print(f"  Next-page  breaks: {nxt:3}")
print(f"  Even-page  breaks: {even:3}")
print(f"  Continuous breaks: {cont:3}")
print(f"  Section layout    : {'OK' if odd >= 18 else 'WARN — chapters may not start on recto'}")

# 8 ─── Images
sep("8. EMBEDDED IMAGES")
imgs = [n for n in names if n.startswith('word/media/')]
print(f"  Embedded media files: {len(imgs)}")
for img in imgs:
    data = z.read(img)
    print(f"    {img}  ({len(data):,} bytes)")

# 9 ─── Word count
sep("9. WORD COUNT")
text_runs = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', doc)
words = sum(len(t.split()) for t in text_runs)
pages_est = words // 250
print(f"  Approx word count : {words:,}")
print(f"  Approx page count : ~{pages_est}  (@ 250 words/page)")
kdp_min = 24
print(f"  KDP minimum pages : {kdp_min}  — {'OK' if pages_est >= kdp_min else 'WARN'}")
print(f"  KDP price point   : {'Standard novel length OK' if words >= 50000 else 'SHORT — verify' if words >= 20000 else 'VERY SHORT — warn'}")

# 10 ─── Chapter heading check
sep("10. CHAPTER HEADINGS (style check)")
h1_styles = re.findall(r'<w:pStyle w:val="([^"]+)"/>[^<]*<w:t>([^<]+)</w:t>', doc)
heading1  = re.findall(r'w:val="Heading1"', doc)
heading2  = re.findall(r'w:val="Heading2"', doc)
chapter_h = re.findall(r'w:val="ChapterHeading"', doc)
print(f"  'Heading1' paragraphs   : {len(heading1)}")
print(f"  'Heading2' paragraphs   : {len(heading2)}")
print(f"  'ChapterHeading' paras  : {len(chapter_h)}")

# 11 ─── ISBN placeholder check
sep("11. ISBN / METADATA PLACEHOLDERS")
isbn_pending = len(re.findall(r'\[PENDING\]', doc))
print(f"  [PENDING] placeholders in docx: {isbn_pending}")
if isbn_pending:
    print("  ACTION REQUIRED: Fill in Print ISBN and eBook ISBN before KDP upload")

print("\n" + "="*60)
print("  AUDIT COMPLETE")
print("="*60)
