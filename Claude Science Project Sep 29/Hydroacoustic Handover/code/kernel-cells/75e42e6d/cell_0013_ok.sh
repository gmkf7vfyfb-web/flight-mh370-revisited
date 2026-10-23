cd src; python - <<'EOF'
import pymupdf, glob
for f in glob.glob('*.pdf'):
    d = pymupdf.open(f); out=[]
    for i,p in enumerate(d): out.append(f'--- page {i+1} ---\n'+p.get_text())
    open(f[:-4]+'.txt','w').write('\n'.join(out)); print(f, len(d), sum(len(x) for x in out))
EOF