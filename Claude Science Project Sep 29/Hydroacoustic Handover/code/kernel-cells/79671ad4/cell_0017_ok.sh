cd src; python -c "
import pypdfium2 as p,re
d=p.PdfDocument('dk100.pdf'); print(len(d))
t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
open('dk100.txt','w').write('\n=====PAGE=====\n'.join(t))
for i,x in enumerate(t):
  for kw in ['yards','Radiation','dB)','detected','REV','Date']:
    for m in re.finditer(kw,x): print(i+1,kw,repr(re.sub(r'\s+',' ',x[max(0,m.start()-250):m.start()+250])))
" | head -30