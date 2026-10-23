cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
import numpy as np
a=load('../src/pmc24/41598_2024_60529_Fig8_HTML.jpg')
for top in (159,429,695):
    s=a[top-3:top+70,72:658]
    g=(s.max(2)<=230)&((s.max(2)-s.min(2))<45)
    m=g.mean(1); idx=np.argsort(m)[::-1][:6]
    print(top, [(top-3+i, round(m[i],2)) for i in sorted(idx)])
EOF