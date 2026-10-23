import pymupdf, re, os
os.chdir(os.path.expanduser('~')) if False else None
doc=pymupdf.open('pod/natsar2026.pdf')
print(doc.page_count)
hits=[]
for i,p in enumerate(doc):
    t=p.get_text()
    if re.search(r'Uncorrected Sweep Widths for Fixed-Wing|Weather Correction Factors|Fatigue|Probability of Detection \(POD\)|POD = 1|coverage factor', t, re.I):
        hits.append(i)
print(hits)