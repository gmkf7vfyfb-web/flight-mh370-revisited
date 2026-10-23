cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
G='../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised/ground-truth-cases/figures/'
a=load(G+'nielsen2021_p06_1870x1491.png'); print(a.shape)
print('N rows',box_lines(a,(0,0,1870,1491),frac=0.2)[0]); print('N cols',box_lines(a,(0,0,1870,1491),frac=0.3)[1])
for (l,t,r,b) in [(70,30,580,640),(70,780,580,1440)]:
    print('Nticks B',ticks_bottom(a,l,r,b)[:9])
v=load(G+'vergoz2021_p05_1598x1694.jpeg'); print(v.shape)
yel=(v[:,:,0]>170)&(v[:,:,1]>170)&(v[:,:,2]<110)
blk=(v.max(2)<40)
import numpy as np
rows=runs([y for y in range(v.shape[0]) if blk[y,300:1250].mean()>0.5]); print('V black rows',rows)
cols=runs([x for x in range(v.shape[1]) if blk[:,x].mean()>0.25]); print('V black cols',cols[:10])
EOF