T=re.sub(r'\s+',' ',' '.join(pages('csiro3.pdf')))
print([m.group(0)[:250] for m in re.finditer(r'[^.]*(RNZAF|New Zealand|Orion|29 March|aerial search)[^.]*\.',T,re.I)])
for n in names:
    if n.startswith('28') or n.startswith('29') or n.startswith('30'):
        dd=pymupdf.open(stream=z.read(n),filetype='pdf'); t=re.sub(r'\s+',' ',' '.join(p.get_text() for p in dd))
        for m in re.finditer(r'[^.]*(New Zealand|RNZAF|objects|sighted|spotted)[^.]*\.',t,re.I): print(n[:40],'||',m.group(0).strip()[:260])