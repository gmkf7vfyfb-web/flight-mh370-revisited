rows=[]
for b in blocks:
    name=b.split('\n')[0].strip()
    if not name.startswith('april') and not name.startswith('march'): continue
    d=re.search(r'Media Release\s*\n\s*([^\n]+)',b); date=d.group(1).strip() if d else '?'
    bt=re.sub(r'\s+',' ',b)
    ws=[m.group(0).strip() for m in re.finditer(r'[^.]*(weather|visibility|swell|winds|cyclone|suspend)[^.]*\.(?:\d[^.]*\.)?',bt,re.I)]
    ws=[w for w in ws if 'Prime Minister' not in w]
    if ws: rows.append((name.replace('.aspx',''),date,' '.join(ws)[:330]))
for r_ in rows: print(r_[0],'|',r_[1],'|',r_[2])