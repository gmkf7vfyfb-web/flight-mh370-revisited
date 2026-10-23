a=open('pod/atsb2017.txt').read()
for kw in ['coverage confidence','probability of detection','POD','Surface search coverage','sea state','weather','suspended','fairly ineffective','choppy']:
    for m in re.finditer(kw,a,re.I):
        s=a[max(0,m.start()-200):m.end()+300].replace('\n',' ')
        pg=re.findall(r'>\s*(\d+)\s*<',a[:m.start()])
        print(f'[{kw}] p~{pg[-1] if pg else "?"}:',s[:500]); print()
    print('----')