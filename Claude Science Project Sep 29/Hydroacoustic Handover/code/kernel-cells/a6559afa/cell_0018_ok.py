def txt(m):
    c=m['content']
    if isinstance(c,list): return ' '.join(b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text')
    return str(c)
for fid in ['676a6e64-2eac-490f-b67d-6c3f5c82f047','a35831fe-107a-4961-bc9f-e6fd6d255601']:
    for i,m in enumerate(store[fid]):
        t=txt(m)
        for mt in re.finditer(r'(?i)(one (sequential )?track|sequential track|in sequence|no parallel|parallel (sub-)?agents)', t):
            s=max(0,mt.start()-250); print(fid[:8], i, m['role'], '...', t[s:mt.end()+200].replace('\n',' '), '\n')