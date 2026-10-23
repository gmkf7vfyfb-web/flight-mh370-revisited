mkdir -p audit/lit && cd audit/lit && curl -sS -L -o fr2012-07717.pdf https://public-inspection.federalregister.gov/2012-07717.pdf; file fr2012-07717.pdf; python3 -c "
import pypdfium2 as p,re
d=p.PdfDocument('fr2012-07717.pdf'); print('pages',len(d))
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    m=re.search(r'near\s+horizontal',t)
    if m: print('pdf page',i+1, repr(t[max(0,m.start()-400):m.end()+200])); 
" 2>&1 | head -20