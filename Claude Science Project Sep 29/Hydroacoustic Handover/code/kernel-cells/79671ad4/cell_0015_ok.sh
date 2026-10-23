cd src; curl -sSL -m 60 -o dk100.pdf -w "%{http_code}\n" "https://archive.org/download/manualsbase-id-639203/639203.pdf" 2>&1 | tail -1; ls -la dk100.pdf; python -c "
import pypdfium2 as p
d=p.PdfDocument('dk100.pdf'); print(len(d))
t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
open('dk100.txt','w').write('\n=====PAGE=====\n'.join(t))
import re
for i,x in enumerate(t):
  for kw in ['yards','dB','Radiation','160','157','detect']:
    for m in re.finditer(kw,x): print(i+1,kw,repr(x[max(0,m.start()-200):m.start()+200]))
" | head -40