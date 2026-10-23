mkdir -p trace && cat > trace/rt.py <<'EOF'
"""Raster trace tools: frame detection and column-wise envelope tracing of waveform panels in published figure rasters.
DIGITISED data only. Method: plot frames are found as long runs of dark pixels (axis box); the trace is the set of pixels
matching the trace colour inside the frame; per pixel column the max and min trace rows give the upper/lower envelope.
Axis calibration: frame edges = axis limits (declared per panel, read from the printed tick labels; checked by overlay)."""
import numpy as np
from PIL import Image

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

def dark(a, thr=90):
    return (a.sum(2) < 3*thr)

def frames(a, minlen=0.5, thr=90, axis_frac=None):
    d = dark(a, thr); H, W = d.shape
    rows = [y for y in range(H) if d[y].sum() > minlen*W*(axis_frac or 1)]
    cols = [x for x in range(W) if d[:, x].sum() > minlen*H*(axis_frac or 1)]
    return rows, cols

def runs(idx):
    out=[]; 
    for i in idx:
        if out and i-out[-1][1]<=1: out[-1][1]=i
        else: out.append([i,i])
    return out

def hlines(a, x0, x1, frac=0.8, thr=110):
    d = dark(a, thr)[:, x0:x1]; return runs([y for y in range(d.shape[0]) if d[y].mean() > frac])

def vlines(a, y0, y1, frac=0.8, thr=110):
    d = dark(a, thr)[y0:y1, :]; return runs([x for x in range(d.shape[1]) if d[:, x].mean() > frac])

def envelope(a, box, mask_fn):
    """box = (left, top, right, bottom) INSIDE pixel coords of the frame; returns cols, ymax_px(upper), ymin_px(lower)."""
    l, t, r, b = box; sub = a[t:b+1, l:r+1]; m = mask_fn(sub)
    cols = []; up = []; lo = []
    for j in range(m.shape[1]):
        ys = np.nonzero(m[:, j])[0]
        if len(ys): cols.append(l+j); up.append(t+ys.min()); lo.append(t+ys.max())
    return np.array(cols), np.array(up), np.array(lo)

def cal(px, p0, p1, v0, v1):
    return v0 + (np.asarray(px, float)-p0)*(v1-v0)/(p1-p0)
EOF
cd trace && python - <<'EOF'
import sys; sys.path.insert(0,'.'); from rt import *
import numpy as np
for f in ['../pmc24/41598_2024_60529_Fig8_HTML.jpg','../pmc24/41598_2024_60529_Fig5_HTML.jpg','../pmc24/41598_2024_60529_Fig7_HTML.jpg']:
    a=load(f); H,W,_=a.shape; print(f,W,H)
    # candidate vertical frame lines
    vl=vlines(a,0,H,frac=0.25); print(' vlines',vl[:20])
    hl=hlines(a,0,W,frac=0.25); print(' hlines',hl[:30])
EOF