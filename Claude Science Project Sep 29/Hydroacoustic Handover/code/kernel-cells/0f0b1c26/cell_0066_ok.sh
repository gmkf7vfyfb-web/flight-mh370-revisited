cd trace && cat >> rt.py <<'EOF'

def ticks_left(a, l, t, b, depth=5, hi=200):
    """y rows of inward tick marks on the left axis line at column l (dark pixels at l+1..l+depth-1)."""
    s = a[t:b+1, l+1:l+depth]; g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < 50)
    return [ (r[0]+r[1])/2 for r in runs([t+y for y in range(g.shape[0]) if g[y].mean() > 0.6])]

def ticks_bottom(a, l, r, b, depth=5, hi=200):
    s = a[b-depth+1:b, l:r+1]; g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < 50)
    return [ (q[0]+q[1])/2 for q in runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > 0.6])]
EOF
python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
a=load('../src/pmc24/41598_2024_60529_Fig7_HTML.jpg')
for (t,b) in [(155,206),(422,472),(686,736)]:
    print(t,b,box_lines(a,(40,t-3,700,b+3),frac=0.5), 'L',ticks_left(a,63,t,b), 'B',ticks_bottom(a,63,650,b)[:12])
a=load('../src/pmc24/41598_2024_60529_Fig8_HTML.jpg')
for (t,b) in [(159,209),(429,477),(695,744)]:
    print('F8',t,b,'L',ticks_left(a,70,t,b),'B',ticks_bottom(a,70,660,b)[:12])
a=load('../src/pmc24/41598_2024_60529_Fig5_HTML.jpg')
print('F5a L',ticks_left(a,406,17,108),'B',ticks_bottom(a,406,659,108))
C='../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised/cmst-2014/figures/cmst2014_p07_561x420.png'
a=load(C); print('CMST L',ticks_left(a,73,32,175),'B',ticks_bottom(a,73,508,175))
EOF