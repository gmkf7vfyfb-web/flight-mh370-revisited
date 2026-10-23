c2=pages('csiro2.pdf'); c3=None
for fn in ['griffin2018.pdf','griffin_web.pdf','csiro1.pdf','csiro2.pdf','csiro4.pdf']:
    P=pages(fn); T=re.sub(r'\s+',' ',' '.join(P))
    print('##',fn,len(P),T[:200])
    for m in re.finditer(r'[^.]*(RNZAF|New Zealand|29 March|Orion|surface search|aerial search)[^.]*\.',T,re.I):
        print('   ',m.group(0).strip()[:300])