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

def find_box(a, region, frac=0.7, lo=0, hi=200, chroma=45):
    """Axis box inside region (l,t,r,b): grey/black low-chroma lines spanning > frac of the region."""
    l,t,r,b = region; s = a[t:b, l:r]
    g = (s.max(2) <= hi) & (s.min(2) >= lo) & ((s.max(2)-s.min(2)) < chroma)
    rows = runs([t+y for y in range(g.shape[0]) if g[y].mean() > frac])
    cols = runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > frac])
    return rows, cols

def box_lines(a, region, frac=0.9, hi=230, chroma=45):
    l,t,r,b = region; s = a[t:b, l:r]
    g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < chroma)
    rows = runs([t+y for y in range(g.shape[0]) if g[y].mean() > frac])
    cols = runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > frac])
    return rows, cols

def ticks_left(a, l, t, b, depth=5, hi=200):
    """y rows of inward tick marks on the left axis line at column l (dark pixels at l+1..l+depth-1)."""
    s = a[t:b+1, l+1:l+depth]; g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < 50)
    return [ (r[0]+r[1])/2 for r in runs([t+y for y in range(g.shape[0]) if g[y].mean() > 0.6])]

def ticks_bottom(a, l, r, b, depth=5, hi=200):
    s = a[b-depth+1:b, l:r+1]; g = (s.max(2) <= hi) & ((s.max(2)-s.min(2)) < 50)
    return [ (q[0]+q[1])/2 for q in runs([l+x for x in range(g.shape[1]) if g[:, x].mean() > 0.6])]
