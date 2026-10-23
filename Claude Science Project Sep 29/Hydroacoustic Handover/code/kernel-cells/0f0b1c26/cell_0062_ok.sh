cd trace && cat >> rt.py <<'EOF'

def find_box(a, region, frac=0.7, lo=0, hi=200, chroma=45):
    """Axis box inside region (l,t,r,b): grey/black low-chroma lines spanning > frac of the region."""
    l,t,r,b = region; s = a[t:b, l:r]
    g = (s.max(2) <= hi) & (s.min(2) >= lo) & ((s.max(2)-s.min(2)) < chroma)
    rows = runs([t+y for y in range(g.shape[0]) if g[y].mean() > frac])
    cols = runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > frac])
    return rows, cols
EOF
python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
a=load('../src/pmc24/41598_2024_60529_Fig8_HTML.jpg')
for reg in [(55,120,680,200),(55,385,680,470),(55,655,680,760)]:
    for fr in (0.6,0.4):
        print(reg,fr,find_box(a,reg,frac=fr,hi=215))
EOF