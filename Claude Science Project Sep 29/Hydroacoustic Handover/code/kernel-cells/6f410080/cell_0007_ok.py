def pagesnips(k,pat,w=900,fn=None):
    t=open(f'handoff/{k}.txt').read()
    pages=[(m.start(),m.group(1)) for m in re.finditer(r'\[\*\*Page (\d+)\*\*\]',t)]
    def pg(i):
        p='?'
        for s,n in pages:
            if s<=i:p=n
            else:break
        return p
    spans=[]
    for m in re.finditer(pat,t,re.I):
        a,b=max(0,m.start()-w),min(len(t),m.end()+w)
        if spans and a<=spans[-1][1]: spans[-1][1]=b
        else: spans.append([a,b])
    with open(fn or f'handoff/{k}_psnip.txt','w') as f:
        for a,b in spans: f.write(f'\n=== PDFpage {pg(a)}\n'+t[a:b]+'\n')
    return len(spans)
print(pagesnips('opsearch',r'satellite imag|imagery|Pl[eé]iades|PLEIADES|French|Gaofen|Thai|WorldView|DigitalGlobe|Geoscience Australia.{0,40}imag'))