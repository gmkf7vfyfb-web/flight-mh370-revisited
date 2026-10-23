cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
import numpy as np
G='../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised/ground-truth-cases/figures/'
v=load(G+'vergoz2021_p05_1598x1694.jpeg')
blk=(v.max(2)<45)
for y in (285,390,660,770,1110,1225,1490,1600):
    xs=np.nonzero(blk[y])[0]; r=runs(list(xs)); big=[q for q in r if q[1]-q[0]>200]; print(y,big)
# strip vertical extents: rows where black fraction in x 260..1190 > 0.6 or yellow
yel=(v[:,:,0]>150)&(v[:,:,1]>150)&(v[:,:,2]<120)
occ=(blk|yel)[:,300:1180].mean(1)
print(runs([y for y in range(v.shape[0]) if occ[y]>0.95]))
# x tick marks at bottom axis (y ~ 1640-1650 dark ticks?)
for yy in range(1626,1650,2):
    g=(v[yy].max(1)<120); r=[q for q in runs(list(np.nonzero(g)[0])) if q[1]-q[0]<4]; 
    if 5<len(r)<40: print(yy,[ (q[0]+q[1])/2 for q in r][:20])
EOF