cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
import numpy as np
def black(a): return (a.max(2)<110)&((a.max(2)-a.min(2))<40)
for f in ['../src/pmc24/41598_2024_60529_Fig8_HTML.jpg','../src/pmc24/41598_2024_60529_Fig5_HTML.jpg']:
    a=load(f); H,W,_=a.shape; k=black(a)
    hr=runs([y for y in range(H) if k[y].mean()>0.3]); vr=runs([x for x in range(W) if k[:,x].mean()>0.08])
    print(f); print(' H',hr); print(' V',vr)
EOF