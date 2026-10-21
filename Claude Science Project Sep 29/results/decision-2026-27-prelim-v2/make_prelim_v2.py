"""Preliminary 2026-27 decision table, v2 (21 Oct 2026). Pipeline test, before calibration, not for release.
Two posteriors: HEADLINE 'DS' = core + drift finds + searched areas (no Australian term; Pete's Decision 1 = B, 21 Oct)
and SENSITIVITY 'ApopS' = the same + Australian non-recovery on populated coasts only (Pete's 15 Oct ruling).
Maps: composer v3.2 re-run with the populated-coast maps saved (reproduces published v3.2 exactly).
Usage: python make_prelim_v2.py <composer_out_dir> <project_dir> <out_dir>
"""
import sys, json, os, glob, numpy as np, pandas as pd
from matplotlib.path import Path as MPath
from scipy.stats import kendalltau
CMP, PROJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(PROJ, 'results/composer-views-run-j')); import views_common as V
X = os.path.expanduser('~/Downloads/mh370-exchange')
GEOJSON = os.path.expanduser('~/Downloads/flight-mh370-revisited/outputs/mh370_search_evidence/search_footprints.geojson')
PD = 0.9; TR = ['D0','D1','D2','D3','D4','D5']
POST = {'DS': ('DS', '', 'core + drift finds + searched areas (no Australian term)'),
        'ApopS': ('ApopS', '', 'core + drift finds + Australian non-finds on populated coasts + searched areas'),
        'DSP': ('DS', 'P', 'as DS, conditional on H (Pleiades objects are MH370 debris)'),
        'ApopSP': ('ApopS', 'P', 'as ApopS, conditional on H (Pleiades objects are MH370 debris)')}
VARP = ('', '_r0', '_r10', '_V2')
VAR = {'': 'detection model V1 central', '_r0': 'rho 0 (search missed nothing it covered)', '_r10': 'rho 0.5 (x10)', '_V2': 'pessimistic detection (V2)', '_V0': 'scalar detection base (V0)'}
m = np.load(os.path.join(CMP, 'maps-v3.npz')); NY, NX = int(m['NY']), int(m['NX'])
J = json.load(open(os.path.join(CMP, 'views-v3-run-j.json')))['cells']
rowmid = V.ROW_MID[:NY]; lonmid = V.LON0+(np.arange(NX)+0.5)*V.STEP; LAT = np.repeat(rowmid,NX); LON = np.tile(lonmid,NY)
feat = {f['properties']['id']: f for f in json.load(open(GEOJSON))['features']}
def poly_frac(fid, n=12):
    g = feat[fid]['geometry']; polys = [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    fr = np.zeros(NY*NX); allpts = np.vstack([np.asarray(r)[:,:2] for rings in polys for r in rings])
    cand = np.where((LON>allpts[:,0].min()-0.3)&(LON<allpts[:,0].max()+0.3)&(LAT>allpts[:,1].min()-0.3)&(LAT<allpts[:,1].max()+0.3))[0]
    u = (np.arange(n)+0.5)/n
    for ci in cand:
        y, x = divmod(ci, NX); q0, q1 = V.authalic_q(V.ROW_EDGES[y]), V.authalic_q(V.ROW_EDGES[y+1])
        lats = V._inv_q(q0+u*(q1-q0)); lons = V.LON0+(x+u)*V.STEP; gl, gn = np.meshgrid(lats, lons); pts = np.column_stack([gn.ravel(), gl.ravel()])
        ins = np.zeros(len(pts), bool)
        for rings in polys:
            ib = MPath(np.asarray(rings[0])[:,:2]).contains_points(pts)
            for hole in rings[1:]: ib &= ~MPath(np.asarray(hole)[:,:2]).contains_points(pts)
            ins |= ib
        fr[ci] = ins.mean()
    return fr
FRN = poly_frac('oi2024_proposed_inboard_northwest'); NEXT_KM2 = FRN.sum()*V.CELL_KM2; ncell = int(round(FRN.sum()))
f = np.load(f'{X}/searched-areas/spatial-fields-v2/fields.npz')
cov = 1-(1-f['p2'])*(1-0.889*f['oi2018'])*(1-0.7808*f['oi2025']); rows_, cols_ = cov.shape; south, west, step = float(f['south']), float(f['west']), float(f['step'])
fl_lat = np.repeat(south+(np.arange(rows_)+0.5)*step, cols_); fl_lon = np.tile(west+(np.arange(cols_)+0.5)*step, rows_)
ci = V.cell_index(fl_lat, fl_lon); ok = ci < NY*NX
num = np.bincount(ci[ok], cov.ravel().astype(float)[ok], NY*NX); den = np.bincount(ci[ok], None, NY*NX); cell_cov = np.where(den>0, num/np.maximum(den,1), 0.0)
del f, cov, fl_lat, fl_lon, ci
by = np.arange(NY)//2; bx = np.arange(NX)//2; NBY, NBX = by.max()+1, bx.max()+1; cell_block = np.repeat(by,NX)*NBX+np.tile(bx,NY)
blk_cov = np.bincount(cell_block, cell_cov, NBY*NBX)/np.bincount(cell_block, None, NBY*NBX); BLOCK_KM2 = 4*V.CELL_KM2
def block_centre(b):
    yb, xb = divmod(b, NBX); return float(rowmid[by==yb].mean()), float(lonmid[bx==xb].mean())
def tag(c): return 'searched' if c>=0.5 else ('partly searched' if c>=0.1 else 'unsearched')
def deff(t, base):
    c = J[f'head|{t}|all|mix']; v = c[base]; pn, ess = v['north_of_33S'], v['kish_ess']; se = c['boot'][base]['north33_se']; mult = np.sqrt(pn*(1-pn)/ess)
    if not (0.05 <= pn <= 0.95): return np.nan, float(ess)   # design effect not estimable from a near-degenerate north-of-33 S share
    return (float((se/mult)**2) if se>0 and mult>0 else np.nan), float(ess)
np.savez_compressed(os.path.join(OUT, 'grid-helpers.npz'), cell_cov=cell_cov, FRN=FRN, cell_block=cell_block, blk_cov=blk_cov)
blk_rows, summ, blockmass = [], [], {}
for t in TR:
    for base in POST:
        de, ess = deff(t, base)
        stem, tail, _ = POST[base]
        for sfx in VAR:
            if tail and sfx not in VARP: continue
            p = stem+sfx+tail; k = f'{t}|{p}'
            if k not in m.files: continue
            w = m[k].astype(float); w /= w.sum(); v = J[f'head|{t}|all|mix'][p]
            B = np.bincount(cell_block, w, NBY*NBX); blockmass[k] = B; bo = np.argsort(-B)
            for r, b in enumerate(bo[:15]):
                la, lo = block_centre(b)
                blk_rows.append(dict(treatment=t, posterior=base, detection=sfx or 'central', rank=r+1, block_lat=round(la,2), block_lon=round(lo,2), block_km2=round(BLOCK_KM2), mass=B[b],
                                     mass_sd_approx=np.sqrt(de*B[b]*(1-B[b])/ess) if sfx=='' else np.nan, p_success=PD*B[b], existing_coverage=blk_cov[b], status=tag(blk_cov[b])))
            order = np.argsort(-w); cum = np.cumsum(w[order])
            uns = np.where(cell_cov<0.1)[0]; ou = uns[np.argsort(-w[uns])]; best_uns = w[ou[:ncell]].sum(); nx = float(v['p_in_next_oi_area_not_evidence'])
            top10 = bo[:10]; n_uns10 = int(sum(blk_cov[b]<0.1 for b in top10)); n_srch10 = int(sum(blk_cov[b]>=0.5 for b in top10))
            summ.append(dict(treatment=t, posterior=base, posterior_name=POST[base][2], detection=VAR[sfx], median_lat=v['median'], north_of_33S=v['north_of_33S'],
                             on_searched_ground=v['p_on_searched_ground'], next_area_km2=round(NEXT_KM2), next_area_mass=nx,
                             next_area_mass_sd_approx=np.sqrt(de*nx*(1-nx)/ess) if sfx=='' else np.nan, next_area_p_success=PD*nx,
                             best_equal_area_unsearched_p_success=PD*best_uns, best_unsearched_lat=float(np.average(LAT[ou[:ncell]], weights=w[ou[:ncell]])),
                             best_unsearched_lon=float(np.average(LON[ou[:ncell]], weights=w[ou[:ncell]])), ratio_best_unsearched_to_next=best_uns/nx if nx>0 else np.nan,
                             top10_blocks_unsearched=n_uns10, top10_blocks_searched=n_srch10, top_block_lat=block_centre(bo[0])[0], top_block_lon=block_centre(bo[0])[1],
                             top_block_coverage=blk_cov[bo[0]], area_km2_90pct=float((cum<0.9).sum()+1)*V.CELL_KM2))
pd.DataFrame(blk_rows).to_csv(os.path.join(OUT, 'ranked-blocks-top15.csv'), index=False)
S = pd.DataFrame(summ); S.to_csv(os.path.join(OUT, 'next-area-summary.csv'), index=False)
rows = []
for t in ['D0','D2','D3','D4']:
    for base in POST:
        w0 = m[f'{t}|{base}'].astype(float); w0 /= w0.sum()
        for b in [1.0,0.9,0.8,0.7,0.6,0.5]:
            w = np.where(w0>0, w0**b, 0.0); w /= w.sum(); cum = np.cumsum(np.sort(w)[::-1])
            nx = float((w*FRN).sum()); uns = np.where(cell_cov<0.1)[0]; ou = uns[np.argsort(-w[uns])]; bu = float(w[ou[:ncell]].sum())
            rows.append(dict(treatment=t, posterior=base, beta=b, next_area_mass_cellgrid=nx, best_unsearched_equal_area_mass=bu, ratio=bu/nx,
                             area_km2_90pct=float((cum<0.9).sum()+1)*V.CELL_KM2, on_searched_ground=float((w*cell_cov).sum()), north_of_33S=float(w[LAT>-33].sum())))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'widening-response.csv'), index=False)
for base in POST:
    stem, tail, _ = POST[base]; grid = [(t,stem+s+tail) for t in TR for s in VAR if f'{t}|{stem+s+tail}' in m.files]; freq = {}
    for t, p in grid:
        for b in np.argsort(-blockmass[f'{t}|{p}'])[:5]: freq[b] = freq.get(b,0)+1
    pd.DataFrame([dict(block_lat=round(block_centre(b)[0],2), block_lon=round(block_centre(b)[1],2), times_in_top5=n, of_cases=len(grid), existing_coverage=round(blk_cov[b],3), status=tag(blk_cov[b]))
                  for b, n in sorted(freq.items(), key=lambda x: -x[1])]).to_csv(os.path.join(OUT, f'rank-stability-top5-{base}.csv'), index=False)
print('done', OUT)
