import zipfile, re

with zipfile.ZipFile('NephilimChronicles_Book2_MANUSCRIPT.docx') as z:
    doc = z.read('word/document.xml').decode('utf-8')

starts = re.findall(r'w:name="(_TOC_[^"]+)"', doc)
pagerefs = re.findall(r'PAGEREF (_TOC_[^ \\\\]+)', doc)
missing = [p for p in pagerefs if p not in starts]

print(f"Bookmarks: {len(starts)} | PAGEREFs: {len(pagerefs)} | Unresolvable: {len(missing)}")
for s in starts:
    tag = " ** PROLOGUE" if "PROLOGUE" in s else ""
    over = " OVER!" if len(s) > 40 else ""
    print(f"  {len(s):2d} chars  {s}{tag}{over}")

if missing:
    print("MISSING:")
    for m in missing:
        print(f"  {m}")
