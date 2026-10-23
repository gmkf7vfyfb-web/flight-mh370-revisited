cd src && which pdftotext || python3 -c "
import pypdfium2 as p
d=p.PdfDocument('easa_tcds_777.pdf')
import re
txt=[d[i].get_textpage().get_text_range() for i in range(len(d))]
open('easa_tcds_777.txt','w').write('\n===PAGE===\n'.join(txt))
for i,t in enumerate(txt):
    for ln in t.split('\n'):
        if re.search(r'(VMO|MMO|Maximum Operating Altitude|Maximum Speed|777-200\b)',ln):
            print(i+1,'|',ln.strip()[:160])
" | head -60