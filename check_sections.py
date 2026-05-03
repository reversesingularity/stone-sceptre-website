import zipfile, re
z = zipfile.ZipFile('NephilimChronicles_Book3_MANUSCRIPT.docx')
doc = z.read('word/document.xml').decode('utf-8')
print('oddPage occurrences :', doc.count('oddPage'))
print('nextPage occurrences:', doc.count('nextPage'))
print('sectPr count        :', doc.count('<w:sectPr'))
print()
# Show first few sectPr elements that contain type
count = 0
for m in re.finditer(r'<w:sectPr[^>]*>.*?</w:sectPr>', doc, re.DOTALL):
    snippet = m.group(0)
    if 'oddPage' in snippet or 'nextPage' in snippet or 'w:type' in snippet:
        print(f"--- sectPr #{count+1} ---")
        print(snippet[:300])
        print()
        count += 1
        if count >= 5:
            break
if count == 0:
    print("No sectPr with type found.")
    # Show the first sectPr at all
    m = re.search(r'<w:sectPr[^>]*>.*?</w:sectPr>', doc, re.DOTALL)
    if m:
        print("First sectPr found:")
        print(m.group(0)[:400])
