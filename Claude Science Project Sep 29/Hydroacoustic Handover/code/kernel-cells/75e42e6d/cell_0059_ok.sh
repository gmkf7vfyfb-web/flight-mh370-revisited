cd src; python - <<'EOF'
import pymupdf,re
for f in ['ISASI2011_BEA.pdf']:
    d=pymupdf.open(f)
    for i,p in enumerate(d):
        t=p.get_text()
        for m in re.finditer(r'[^.]*\b(ULB|beacon|pinger)[^.]*\.',t):
            s=' '.join(m.group(0).split())
            if len(s)>40: print(f'p{i+1}:',s[:400])
EOF