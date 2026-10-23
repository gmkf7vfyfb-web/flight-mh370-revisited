def pages(fn):
    d=pymupdf.open('pod/'+fn); return [p.get_text() for p in d]
c1=pages('csiro1.pdf'); c4=pages('csiro4.pdf')
for i,t in enumerate(c1):
    if re.search(r'probability of detection|POD',t): print('C1 PDF p',i+1, len(t))
print(re.sub(r'\n\s*\n','\n',c4[4] if len(c4)>4 else '')[:100])
for i in range(min(8,len(c4))):
    t=c4[i]
    if 'POD' in t or 'probability' in t.lower(): print('==C4 PDF p',i+1); print(re.sub(r'\s+',' ',t)[:4500])