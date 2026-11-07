"""Generic PDF vector panel extractor (PyMuPDF).

Finds plot panels on a page from numeric tick-label rows/columns in the text
layer, anchors them to axis lines, fits a linear (or log10) axis transform per
axis by least squares (labels snapped to tick marks where present), and
returns every vertex of every drawing path inside each panel, with the
transform applied.  Text words inside the panel are returned too.
"""
import re, math, fitz, numpy as np

MINUS = '\u2212\u2013\u2012\u2010'

def parse_num(s):
    t = s.strip().replace('\u00a0', '')
    for m in MINUS:
        t = t.replace(m, '-')
    t = t.rstrip('°').rstrip('%')
    if re.fullmatch(r'-?\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?', t):
        neg = t.startswith('-'); parts = t.lstrip('-').split(':')
        v = sum(float(p) * 60 ** (len(parts) - 1 - i) for i, p in enumerate(parts))
        return (-v if neg else v), 'hms_seconds'
    if re.fullmatch(r'[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?', t):
        return float(t), 'num'
    return None, None

def words_num(page):
    out = []
    for w in page.get_text('words'):
        v, kind = parse_num(w[4])
        if v is not None:
            out.append(dict(x0=w[0], y0=w[1], x1=w[2], y1=w[3], xc=(w[0]+w[2])/2, yc=(w[1]+w[3])/2,
                            v=v, kind=kind, txt=w[4], h=w[3]-w[1]))
    return out

def _monotone(vals):
    d = np.diff(vals)
    return (np.all(d > 0) or np.all(d < 0)) and len(vals) >= 3

def _fit(pos, vals):
    """least-squares val = a + b*pos; returns a,b,resid(max abs in value units), mode"""
    pos = np.asarray(pos, float); vals = np.asarray(vals, float)
    best = None
    for mode in ('lin', 'log'):
        if mode == 'log':
            if np.any(vals <= 0): continue
            y = np.log10(vals)
        else:
            y = vals
        A = np.vstack([np.ones_like(pos), pos]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        r = y - A @ coef
        span = (y.max() - y.min()) or 1.0
        rel = float(np.max(np.abs(r)) / span)
        cand = dict(a=float(coef[0]), b=float(coef[1]), mode=mode, max_resid=float(np.max(np.abs(r))),
                    rms_resid=float(np.sqrt(np.mean(r**2))), rel_resid=rel, n=len(pos))
        if best is None or rel < best['rel_resid'] - 1e-9:
            best = cand
    return best

def group_rows(ws, tol=1.2):
    """numeric words sharing a baseline (x tick label rows)"""
    ws = sorted(ws, key=lambda w: w['yc'])
    rows, cur = [], []
    for w in ws:
        if cur and abs(w['yc'] - np.mean([c['yc'] for c in cur])) > tol:
            rows.append(cur); cur = []
        cur.append(w)
    if cur: rows.append(cur)
    out = []
    for r in rows:
        r = sorted(r, key=lambda w: w['xc'])
        # split on large gaps (separate panels side by side)
        segs, s = [], [r[0]]
        for a, b in zip(r, r[1:]):
            gaps = [q['xc'] - p['xc'] for p, q in zip(s, s[1:])]
            typ = np.median(gaps) if gaps else None
            if typ and (b['xc'] - a['xc']) > 2.5 * typ:
                segs.append(s); s = [b]
            else:
                s.append(b)
        segs.append(s)
        for s in segs:
            if len(s) >= 3 and _monotone([w['v'] for w in s]):
                out.append(s)
    return out

def group_cols(ws, key='x1', tol=1.8):
    ws = sorted(ws, key=lambda w: w[key])
    cols, cur = [], []
    for w in ws:
        if cur and abs(w[key] - np.mean([c[key] for c in cur])) > tol:
            cols.append(cur); cur = []
        cur.append(w)
    if cur: cols.append(cur)
    out = []
    for c in cols:
        c = sorted(c, key=lambda w: w['yc'])
        segs, s = [], [c[0]]
        for a, b in zip(c, c[1:]):
            gaps = [q['yc'] - p['yc'] for p, q in zip(s, s[1:])]
            typ = np.median(gaps) if gaps else None
            if (typ and (b['yc'] - a['yc']) > 2.5 * typ) or (b['yc'] - a['yc']) > 120:
                segs.append(s); s = [b]
            else:
                s.append(b)
        segs.append(s)
        for s in segs:
            if len(s) >= 3 and _monotone([w['v'] for w in s]):
                # equal spacing check (linear or log) loosely
                out.append(s)
    return out

def segments(drawings):
    """flatten to straight segments with path index"""
    segs = []
    for pi, d in enumerate(drawings):
        for it in d['items']:
            if it[0] == 'l':
                segs.append((pi, it[1].x, it[1].y, it[2].x, it[2].y))
            elif it[0] == 're':
                r = it[1]
                for (a, b, c, e) in ((r.x0, r.y0, r.x1, r.y0), (r.x1, r.y0, r.x1, r.y1), (r.x0, r.y1, r.x1, r.y1), (r.x0, r.y0, r.x0, r.y1)):
                    segs.append((pi, a, b, c, e))
            elif it[0] == 'qu':
                q = it[1]; pts = [q.ul, q.ur, q.lr, q.ll, q.ul]
                for p, q2 in zip(pts, pts[1:]):
                    segs.append((pi, p.x, p.y, q2.x, q2.y))
    return np.array(segs) if segs else np.zeros((0, 5))

def find_hline(S, y_below, xs, maxgap=14):
    """horizontal segment just above label row (y < y_below) covering label x positions"""
    if len(S) == 0: return None
    h = S[np.abs(S[:, 2] - S[:, 4]) < 0.3]
    best = None
    for s in h:
        y = s[2]; xa, xb = sorted((s[1], s[3]))
        if 0 <= y_below - y <= maxgap and xa <= min(xs) + 4.0 and xb >= max(xs) - 4.0:
            if best is None or y > best[0] or (abs(y - best[0]) < 0.3 and xb - xa > best[2] - best[1]):
                best = (y, xa, xb)
    return best

def find_vline(S, x_left, ys, side='left', maxgap=14):
    if len(S) == 0: return None
    v = S[np.abs(S[:, 1] - S[:, 3]) < 0.3]
    best = None
    for s in v:
        x = s[1]; ya, yb = sorted((s[2], s[4]))
        gap = (x - x_left) if side == 'left' else (x_left - x)
        if 0 <= gap <= maxgap and ya <= min(ys) + 4.0 and yb >= max(ys) - 4.0:
            if best is None or gap < best[3]:
                best = (x, ya, yb, gap)
    return best

def snap_ticks(S, axis, line_pos, label_pos, tol=2.5, maxlen=9):
    """for each label, position of nearest short perpendicular tick touching the axis line"""
    out = []
    if axis == 'x':
        cand = S[(np.abs(S[:, 1] - S[:, 3]) < 0.3) & (np.abs(S[:, 2] - S[:, 4]) > 0.8) & (np.abs(S[:, 2] - S[:, 4]) < maxlen)]
        cand = cand[(np.minimum(cand[:, 2], cand[:, 4]) <= line_pos + 1.0) & (np.maximum(cand[:, 2], cand[:, 4]) >= line_pos - 1.0)]
        tp = cand[:, 1] if len(cand) else np.array([])
    else:
        cand = S[(np.abs(S[:, 2] - S[:, 4]) < 0.3) & (np.abs(S[:, 1] - S[:, 3]) > 0.8) & (np.abs(S[:, 1] - S[:, 3]) < maxlen)]
        cand = cand[(np.minimum(cand[:, 1], cand[:, 3]) <= line_pos + 1.0) & (np.maximum(cand[:, 1], cand[:, 3]) >= line_pos - 1.0)]
        tp = cand[:, 2] if len(cand) else np.array([])
    for p in label_pos:
        if len(tp):
            j = np.argmin(np.abs(tp - p))
            out.append(float(tp[j]) if abs(tp[j] - p) <= tol else None)
        else:
            out.append(None)
    return out

def _mult_near(page_words, region, which):
    """Matlab style 'x10^n' multiplier near the axis; returns (factor, text) or (1,None)"""
    x0, y0, x1, y1 = region
    for i, w in enumerate(page_words):
        t = w[4]
        if re.fullmatch(r'[×x]10', t) or t in ('×10', '\u00d710'):
            wx, wy = (w[0]+w[2])/2, (w[1]+w[3])/2
            ok = False
            if which == 'y' and x0 - 40 <= wx <= x0 + 60 and y0 - 22 <= wy <= y0 + 2: ok = True
            if which == 'x' and x1 - 60 <= wx <= x1 + 40 and y1 <= wy <= y1 + 30: ok = True
            if ok:
                # exponent: next small word up-right
                for w2 in page_words:
                    if w2 is w: continue
                    if w[2] - 1 <= w2[0] <= w[2] + 8 and w2[3] <= w[3] + 1 and w2[1] >= w[1] - 8:
                        v, _ = parse_num(w2[4])
                        if v is not None and abs(v) < 40:
                            return 10.0 ** v, f"{t}^{w2[4]}"
    return 1.0, None

def detect_panels(page, clip=None, ws=None, drawings=None):
    if drawings is None: drawings = page.get_drawings()
    S = segments(drawings)
    if ws is None: ws = words_num(page)
    if clip is not None:
        ws = [w for w in ws if fitz.Rect(clip).contains(fitz.Point(w['xc'], w['yc']))]
    rows = group_rows(ws)
    colsL = group_cols(ws, 'x1')
    colsR = group_cols(ws, 'x0')
    used_cols = set()
    panels = []
    for row in rows:
        xs = [w['xc'] for w in row]; ytop = min(w['y0'] for w in row)
        hl = find_hline(S, ytop, xs)
        yb = hl[0] if hl else ytop - 3
        # candidate left columns: right edge left of first label (+tolerance), bottom label near yb
        best = None
        for ci, col in enumerate(colsL):
            xr = np.mean([w['x1'] for w in col]); ys = [w['yc'] for w in col]
            if xr > min(xs) + 6: continue
            if max(ys) > yb + 8: continue
            spc = np.median(np.diff(sorted(ys))) if len(ys) > 1 else 20
            if yb - max(ys) > max(40, 2.0 * spc): continue
            if hl:
                if not (-3 <= hl[1] - xr <= 40): continue
                score = (yb - max(ys)) + 0.5 * (hl[1] - xr)
            else:
                if min(xs) - xr > 60: continue
                score = (yb - max(ys)) + 0.5 * (min(xs) - xr)
            if best is None or score < best[0]: best = (score, ci)
        if best is None:
            # x-only panel: vertical axis line at the left end of the x axis line
            if hl is None: continue
            v = S[(np.abs(S[:, 1] - S[:, 3]) < 0.3) & (np.abs(S[:, 1] - hl[1]) < 1.2)]
            v = v[(np.maximum(v[:, 2], v[:, 4]) >= hl[0] - 1.2) & (np.maximum(v[:, 2], v[:, 4]) <= hl[0] + 1.2)]
            if len(v) == 0: continue
            ytop_line = float(np.min(np.minimum(v[:, 2], v[:, 4])))
            if hl[0] - ytop_line < 15: continue
            panels.append(dict(row=row, col=None, rcol=None, hline=hl, vline=(hl[1], ytop_line, hl[0], 0), region=(hl[1], ytop_line, hl[2], hl[0])))
            continue
        col = colsL[best[1]]; used_cols.add(('L', best[1]))
        ys = [w['yc'] for w in col]; xr = np.mean([w['x1'] for w in col])
        vl = find_vline(S, xr, ys, 'left')
        xl = vl[0] if vl else (hl[1] if hl else xr + 3)
        ytop_line = vl[1] if vl else min(ys)
        xright = hl[2] if hl else max(xs)
        region = (xl, ytop_line, xright, yb)
        # right-hand axis
        rcol = None
        for ci, c in enumerate(colsR):
            xlft = np.mean([w['x0'] for w in c]); cy = [w['yc'] for w in c]
            if 0 <= xlft - xright <= 14 and min(cy) >= ytop_line - 8 and max(cy) <= yb + 8:
                rcol = c; break
        panels.append(dict(row=row, col=col, rcol=rcol, hline=hl, vline=vl, region=region))
    return panels, drawings, S

def calibrate(panel, S, page_words):
    xl, yt, xr, yb = panel['region']
    row, col = panel['row'], panel['col']
    xpos = [w['xc'] for w in row]; xv = [w['v'] for w in row]
    xt = snap_ticks(S, 'x', yb, xpos)
    xsn = [t if t is not None else p for t, p in zip(xt, xpos)]
    fx = _fit(xsn, xv); fx0 = _fit(xpos, xv)
    if fx0['rel_resid'] < fx['rel_resid']:
        fx = fx0; fx['n_tick_snapped'] = 0; fx['position_source'] = 'label centres (tick snapping gave larger residual)'
    else:
        fx['n_tick_snapped'] = sum(t is not None for t in xt); fx['position_source'] = 'tick marks where found, else label centres'
    fx['labels'] = [w['txt'] for w in row]; fx['label_kind'] = row[0]['kind']
    if col is not None:
        ypos = [w['yc'] for w in col]; yv = [w['v'] for w in col]
        yt_ = snap_ticks(S, 'y', xl, ypos)
        ysn = [t if t is not None else p for t, p in zip(yt_, ypos)]
        fy = _fit(ysn, yv); fy0 = _fit(ypos, yv)
        if fy0['rel_resid'] < fy['rel_resid']:
            fy = fy0; fy['n_tick_snapped'] = 0; fy['position_source'] = 'label centres (tick snapping gave larger residual)'
        else:
            fy['n_tick_snapped'] = sum(t is not None for t in yt_); fy['position_source'] = 'tick marks where found, else label centres'
        fy['labels'] = [w['txt'] for w in col]; fy['label_kind'] = col[0]['kind']
    else:
        Hh = yb - yt
        fy = dict(a=yb / Hh, b=-1.0 / Hh, mode='frac', max_resid=0.0, rms_resid=0.0, rel_resid=0.0, n=0,
                  n_tick_snapped=0, labels=[], label_kind='none (no numeric y labels): y_data is fraction of axis height, 0 = x-axis line, 1 = top of left axis line')
    mx, mxt = _mult_near(page_words, panel['region'], 'x'); my, myt = _mult_near(page_words, panel['region'], 'y')
    fx['multiplier'], fx['multiplier_text'] = mx, mxt
    fy['multiplier'], fy['multiplier_text'] = my, myt
    out = dict(x=fx, y=fy)
    if panel.get('rcol'):
        rc = panel['rcol']; rp = [w['yc'] for w in rc]; rv = [w['v'] for w in rc]
        rt = snap_ticks(S, 'y', xr, rp); rsn = [t if t is not None else p for t, p in zip(rt, rp)]
        fr = _fit(rsn, rv); fr['n_tick_snapped'] = sum(t is not None for t in rt); fr['labels'] = [w['txt'] for w in rc]
        fr['label_kind'] = rc[0]['kind']; fr['multiplier'] = 1.0; fr['multiplier_text'] = None
        out['y_right'] = fr
    # resolution: data units per PDF point and per 0.01 pt (PDF coordinate precision is ~1e-3 pt)
    for k in out:
        f = out[k]
        f['units_per_pt'] = abs(f['b']) * f['multiplier'] if f['mode'] == 'lin' else None
    return out

def apply(f, p):
    v = f['a'] + f['b'] * p
    if f['mode'] == 'log': v = 10 ** v
    return v * f['multiplier']

def color_hex(c):
    if c is None: return ''
    return '#' + ''.join(f'{int(round(255*max(0,min(1,x)))):02x}' for x in c[:3])

def panel_vertices(panel, drawings, cal, tol=1.0, exclude_frame=True):
    xl, yt, xr, yb = panel['region']
    R = fitz.Rect(xl - tol, yt - tol, xr + tol, yb + tol)
    W, H = xr - xl, yb - yt
    rows = []
    for pi, d in enumerate(drawings):
        r = d['rect']
        if not (r.x1 >= R.x0 and r.x0 <= R.x1 and r.y1 >= R.y0 and r.y0 <= R.y1): continue
        inter = fitz.Rect(r) & R
        if r.width > 0 and r.height > 0 and inter.get_area() / max(r.get_area(), 1e-9) < 0.5 and not R.contains(r):
            # mostly outside: skip unless it is a degenerate (line) path
            pass
        # frame / tick / grid filter: axis-aligned path lying on the border
        if exclude_frame:
            items = d['items']
            def on_border(x1, y1, x2, y2):
                hz = abs(y1 - y2) < 0.3; vt = abs(x1 - x2) < 0.3
                if hz and (abs(y1 - yb) < 1.2 or abs(y1 - yt) < 1.2) and abs(x2 - x1) > 0.6 * W: return True
                if vt and (abs(x1 - xl) < 1.2 or abs(x1 - xr) < 1.2) and abs(y2 - y1) > 0.6 * H: return True
                if hz and abs(x2 - x1) < 9 and (abs(x1 - xl) < 9.5 or abs(x2 - xr) < 9.5 or abs(x1 - xr) < 9.5 or abs(x2 - xl) < 9.5): return True
                if vt and abs(y2 - y1) < 9 and (abs(y1 - yb) < 9.5 or abs(y2 - yt) < 9.5 or abs(y1 - yt) < 9.5 or abs(y2 - yb) < 9.5): return True
                return False
            segs = []
            for it in items:
                if it[0] == 'l': segs.append((it[1].x, it[1].y, it[2].x, it[2].y))
                elif it[0] == 're':
                    q = it[1]
                    if abs(q.x0 - xl) < 1.5 and abs(q.x1 - xr) < 1.5 and abs(q.y0 - yt) < 1.5 and abs(q.y1 - yb) < 1.5:
                        segs.append('frame')
                    else: segs.append(None)
                else: segs.append(None)
            if segs and all(s == 'frame' or (s is not None and on_border(*s)) for s in segs):
                continue
            # white background fills covering the panel
            if d.get('fill') is not None and all(c > 0.98 for c in d['fill'][:3]) and d.get('color') is None and r.width > 0.8 * W:
                continue
        lastp = None
        for ii, it in enumerate(d['items']):
            pts = []
            if it[0] == 'l':
                pts = [('l1', it[2])] if (lastp is not None and abs(lastp.x - it[1].x) < 1e-6 and abs(lastp.y - it[1].y) < 1e-6) else [('l0', it[1]), ('l1', it[2])]
                lastp = it[2]
            elif it[0] == 'c':
                pts = ([] if (lastp is not None and abs(lastp.x - it[1].x) < 1e-6 and abs(lastp.y - it[1].y) < 1e-6) else [('c0', it[1])]) + [('ctrl1', it[2]), ('ctrl2', it[3]), ('c1', it[4])]
                lastp = it[4]
            elif it[0] == 're':
                q = it[1]; pts = [('re_ul', q.tl), ('re_lr', q.br)]
            elif it[0] == 'qu':
                q = it[1]; pts = [('qu_ul', q.ul), ('qu_ur', q.ur), ('qu_lr', q.lr), ('qu_ll', q.ll)]
            if it[0] in ('re', 'qu'): lastp = None
            for vi, (kind, p) in enumerate(pts):
                inside = (xl - tol <= p.x <= xr + tol) and (yt - tol <= p.y <= yb + tol)
                row = dict(path_id=pi, item_idx=ii, vertex_idx=vi, item_type=it[0], vertex_kind=kind,
                           x_pt=round(p.x, 4), y_pt=round(p.y, 4), x_data=apply(cal['x'], p.x), y_data=apply(cal['y'], p.y),
                           inside_axes=int(inside), stroke=color_hex(d.get('color')), fill=color_hex(d.get('fill')),
                           width=d.get('width'), path_type=d.get('type'))
                if 'y_right' in cal: row['y_right_data'] = apply(cal['y_right'], p.y)
                rows.append(row)
    return rows

def panel_text(page, panel, cal, tol=1.0):
    xl, yt, xr, yb = panel['region']
    out = []
    for w in page.get_text('words'):
        xc, yc = (w[0]+w[2])/2, (w[1]+w[3])/2
        if xl - tol <= xc <= xr + tol and yt - tol <= yc <= yb + tol:
            out.append(dict(text=w[4], x_pt=round(xc, 3), y_pt=round(yc, 3), x_data=apply(cal['x'], xc), y_data=apply(cal['y'], yc)))
    return out

def axis_titles(page, panel):
    xl, yt, xr, yb = panel['region']
    d = page.get_text('dict'); xt, yl, tt = [], [], []
    rowbot = max(w['y1'] for w in panel['row']); colleft = min(w['x0'] for w in panel['col']) if panel['col'] else xl
    for b in d['blocks']:
        for l in b.get('lines', []):
            txt = ''.join(s['text'] for s in l['spans']).strip()
            if not txt: continue
            bx = fitz.Rect(l['bbox']); dirx = l['dir']
            if abs(dirx[0]) > 0.9 and rowbot - 1 <= bx.y0 <= rowbot + 16 and bx.x0 >= xl - 20 and bx.x1 <= xr + 20:
                xt.append(txt)
            if abs(dirx[1]) > 0.9 and colleft - 30 <= bx.x0 and bx.x1 <= colleft + 1 and bx.y0 >= yt - 20 and bx.y1 <= yb + 20:
                yl.append(txt)
            if abs(dirx[0]) > 0.9 and yt - 16 <= bx.y1 <= yt + 1 and bx.x0 >= xl - 20 and bx.x1 <= xr + 20:
                tt.append(txt)
    return ' / '.join(xt), ' / '.join(yl), ' / '.join(tt)

# ---------------------------------------------------------------------------
# Tick labels drawn as glyph outlines (no text layer): group small filled
# glyph paths into words, render each word at high zoom and read it with OCR.
_OCR = None
def _ocr():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR
        _OCR = RapidOCR()
    return _OCR

def _subpath_boxes(d):
    boxes, cur, last = [], None, None
    for it in d['items']:
        if it[0] == 're':
            boxes.append(fitz.Rect(it[1])); continue
        if it[0] == 'qu':
            boxes.append(fitz.Rect(it[1].rect)); continue
        pts = list(it[1:])
        start, end = pts[0], pts[-1]
        if last is None or abs(start.x - last.x) > 0.01 or abs(start.y - last.y) > 0.01:
            if cur is not None: boxes.append(cur)
            cur = fitz.Rect(start, start)
        for p in pts: cur |= p
        last = end
    if cur is not None: boxes.append(cur)
    return boxes

def glyph_words(page, drawings=None, maxh=11.0, clip=None, stroked=False):
    if drawings is None: drawings = page.get_drawings()
    cont = []
    for d in drawings:
        if d['type'] != 'f' and not (stroked and d['type'] == 's'): continue
        r = d['rect']
        if d['type'] == 'f' and (r.height > maxh or r.height < 0.3): continue
        if clip is not None and not fitz.Rect(clip).intersects(r): continue
        for b in _subpath_boxes(d):
            if 0.2 < b.height <= maxh and b.width <= 12 and not (stroked and d['type'] == 's' and (b.width < 0.3 or b.height < 1.0) and max(b.width, b.height) < 6 and min(b.width, b.height) < 0.3):
                cont.append(b)
    # merge overlapping contours into glyphs
    cont.sort(key=lambda r: r.x0)
    glyphs = []
    for b in cont:
        for gidx, gb in enumerate(glyphs):
            if gb.intersects(b) or gb.contains(b) or b.contains(gb):
                glyphs[gidx] = gb | b; break
        else:
            glyphs.append(fitz.Rect(b))
    # merge glyphs into words on a shared line with small gaps
    glyphs.sort(key=lambda r: r.x0)
    words = []
    for gb in glyphs:
        placed = False
        for widx, w in enumerate(words):
            hh = max(w.height, gb.height, 3)
            vo = min(w.y1, gb.y1) - max(w.y0, gb.y0)
            if vo > 0.4 * min(w.height, gb.height) and -0.5 <= gb.x0 - w.x1 <= 0.42 * hh:
                words[widx] = w | gb; placed = True; break
        if not placed: words.append(fitz.Rect(gb))
    return words

def ocr_words(page, drawings=None, zoom=8, clip=None, stroked=False):
    import numpy as _np
    eng = _ocr(); out = []
    for w in glyph_words(page, drawings, clip=clip, stroked=stroked):
        if w.width < 1 or w.height < 2: continue
        pad = 0.6 * w.height
        cr = fitz.Rect(w.x0 - pad, w.y0 - pad, w.x1 + pad, w.y1 + pad)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=cr, alpha=False)
        img = _np.frombuffer(pix.samples, dtype=_np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        try:
            res, _ = eng(img, use_det=False, use_cls=False, use_rec=True)
        except Exception:
            res = None
        if not res: continue
        txt, conf = res[0][0], float(res[0][1])
        t = txt.replace(' ', '').replace('O', '0').replace('o', '0')
        v, kind = parse_num(t)
        if v is None: continue
        out.append(dict(x0=w.x0, y0=w.y0, x1=w.x1, y1=w.y1, xc=(w.x0+w.x1)/2, yc=(w.y0+w.y1)/2, v=v,
                        kind='ocr_' + kind, txt=t, h=w.height, conf=conf))
    return out

def _split_consistent(seq, posk, maxgap=120):
    """split an ordered label list into runs with monotone values and constant
    position-per-value ratio (linear) or per-log-value ratio (log)."""
    runs, cur = [], []
    def ok(run, w):
        if not run: return True
        if w[posk] - run[-1][posk] > maxgap: return False
        if abs(w[posk] - run[-1][posk]) < 0.5: return False
        if w['v'] == run[-1]['v']: return False
        if len(run) >= 2:
            d0 = run[-1]['v'] - run[-2]['v']; d1 = w['v'] - run[-1]['v']
            if d0 * d1 <= 0: return False
            r0 = (run[-1][posk] - run[-2][posk]) / d0; r1 = (w[posk] - run[-1][posk]) / d1
            if not (0.85 < r1 / r0 < 1.18):
                # allow log spacing
                if min(x['v'] for x in run + [w]) > 0:
                    l0 = math.log10(run[-1]['v']) - math.log10(run[-2]['v']); l1 = math.log10(w['v']) - math.log10(run[-1]['v'])
                    q0 = (run[-1][posk] - run[-2][posk]) / l0; q1 = (w[posk] - run[-1][posk]) / l1
                    if 0.85 < q1 / q0 < 1.18: return True
                return False
        return True
    for w in seq:
        if ok(cur, w): cur.append(w)
        else:
            runs.append(cur)
            cur = [cur[-1], w] if (len(cur) >= 1 and ok([cur[-1]], w) and False) else [w]
    if cur: runs.append(cur)
    return [r for r in runs if len(r) >= 3]

def group_rows(ws, tol=1.2):
    ws = sorted(ws, key=lambda w: w['yc'])
    rows, cur = [], []
    for w in ws:
        if cur and abs(w['yc'] - np.mean([c['yc'] for c in cur])) > tol:
            rows.append(cur); cur = []
        cur.append(w)
    if cur: rows.append(cur)
    out = []
    for r in rows:
        r = sorted(r, key=lambda w: w['xc'])
        # de-duplicate identical position
        out += _split_consistent(r, 'xc', maxgap=150)
    return out

def group_cols(ws, key='x1', tol=1.8):
    ws = sorted(ws, key=lambda w: w[key])
    cols, cur = [], []
    for w in ws:
        if cur and abs(w[key] - np.mean([c[key] for c in cur])) > tol:
            cols.append(cur); cur = []
        cur.append(w)
    if cur: cols.append(cur)
    out = []
    for c in cols:
        c = sorted(c, key=lambda w: w['yc'])
        out += _split_consistent(c, 'yc', maxgap=120)
    return out
