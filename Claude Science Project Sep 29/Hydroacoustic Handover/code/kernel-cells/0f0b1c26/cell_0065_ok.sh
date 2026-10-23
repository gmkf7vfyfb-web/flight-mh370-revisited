cd trace && cat >> rt.py <<'EOF'

def box_lines(a, region, frac=0.9, hi=230, chroma=45):
    l,t,r,b = region; s = a[t:b, l:r]
    g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < chroma)
    rows = runs([t+y for y in range(g.shape[0]) if g[y].mean() > frac])
    cols = runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > frac])
    return rows, cols
EOF
python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
a=load('../src/pmc24/41598_2024_60529_Fig5_HTML.jpg'); print('F5 size',a.shape)
print('F5 right col scan', box_lines(a,(340,0,669,717),frac=0.25))
a=load('../src/pmc24/41598_2024_60529_Fig4_HTML.jpg'); print('F4', box_lines(a,(340,0,669,725),frac=0.25))
a=load('../src/pmc24/41598_2024_60529_Fig7_HTML.jpg'); print('F7', a.shape, box_lines(a,(40,0,700,780),frac=0.5))
C='../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised/cmst-2014/figures/cmst2014_p07_561x420.png'
a=load(C); print('CMST1', box_lines(a,(60,20,520,200),frac=0.5))
EOF