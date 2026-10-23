def snippets(k,w=700):
    t=open(f'handoff/{k}.txt').read()
    spans=[]
    for m in kw.finditer(t):
        a,b=max(0,m.start()-w),min(len(t),m.end()+w)
        if spans and a<=spans[-1][1]: spans[-1][1]=b
        else: spans.append([a,b])
    with open(f'handoff/{k}_snip.txt','w') as f:
        for a,b in spans: f.write(f'\n=== @{a}\n'+t[a:b]+'\n')
    return len(spans)
for k in ['opsearch','amsa','sir','factual','marghany','guardian']: print(k,snippets(k))