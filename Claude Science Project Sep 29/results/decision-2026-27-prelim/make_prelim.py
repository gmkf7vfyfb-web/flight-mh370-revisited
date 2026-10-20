"""Preliminary 2026-27 decision-table pipeline on composer views v3.2 (20 Oct 2026). Pipeline test, before calibration.
Run from 'Claude Science Project Sep 29/' with the exchange at ~/Downloads/mh370-exchange. Writes tables to results/decision-2026-27-prelim/.
"""
import sys, json, os, glob, numpy as np, pandas as pd
from matplotlib.path import Path as MPath
from scipy.stats import kendalltau
sys.path.insert(0, 'results/composer-views-run-j'); import views_common as V
X = os.path.expanduser('~/Downloads/mh370-exchange'); OUT = 'results/decision-2026-27-prelim'; os.makedirs(OUT, exist_ok=True)
GEOJSON = os.path.expanduser('~/Downloads/flight-mh370-revisited/outputs/mh370_search_evidence/search_footprints.geojson')
PD = 0.9; TR = ['D0','D1','D2','D3','D4','D5']
PRODS = {'core':'core only','D':'core + drift (no search term)','DS':'all evidence','ABS':'all evidence + Australian non-recovery (sensitivity)',
         'DS_r0':'all evidence, detection field x0','DS_r10':'all evidence, detection field x10','DS_V0':'all evidence, scalar detection base (V0)',
         'DS_V2':'all evidence, pessimistic detection (V2)','DS_V3':'all evidence, detection V3','S':'core + searched areas'}
m = np.load(f'{X}/composer/run-j-views-v3.2/maps-v3.npz'); NY, NX = int(m['NY']), int(m['NX'])
pr = pd.read_csv(f'{X}/composer/run-j-views-v3.2/products-v3.csv')
head = pr[(pr.variant=='head')&(pr.family=='all')&(pr.context=='mix')].set_index(['option','product'])
rowmid = V.ROW_MID[:NY]; lonmid = V.LON0+(np.arange(NX)+0.5)*V.STEP; LAT = np.repeat(rowmid,NX); LON = np.tile(lonmid,NY)
feat = {f['properties']['id']: f for f in json.load(open(GEOJSON))['features']}

def poly_frac(fid, n=12):
    """Fraction of each equal-area cell inside the polygon (n x n sub-points, uniform in lon and in authalic q)."""
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

# existing coverage per cell from the searched-areas per-cell fields (v2)
f = np.load(f'{X}/searched-areas/spatial-fields-v2/fields.npz')
cov = 1-(1-f['p2'])*(1-0.889*f['oi2018'])*(1-0.7808*f['oi2025']); rows_, cols_ = cov.shape; south, west, step = float(f['south']), float(f['west']), float(f['step'])
fl_lat = np.repeat(south+(np.arange(rows_)+0.5)*step, cols_); fl_lon = np.tile(west+(np.arange(cols_)+0.5)*step, rows_)
ci = V.cell_index(fl_lat, fl_lon); ok = ci < NY*NX
num = np.bincount(ci[ok], cov.ravel().astype(float)[ok], NY*NX); den = np.bincount(ci[ok], None, NY*NX); cell_cov = np.where(den>0, num/np.maximum(den,1), 0.0)
by = np.arange(NY)//2; bx = np.arange(NX)//2; NBY, NBX = by.max()+1, bx.max()+1; cell_block = np.repeat(by,NX)*NBX+np.tile(bx,NY)
blk_cov = np.bincount(cell_block, cell_cov, NBY*NBX)/np.bincount(cell_block, None, NBY*NBX); BLOCK_KM2 = 4*V.CELL_KM2
def block_centre(b):
    yb, xb = divmod(b, NBX); return float(rowmid[by==yb].mean()), float(lonmid[bx==xb].mean())
def tag(c): return 'searched' if c>=0.5 else ('partly searched' if c>=0.1 else 'unsearched')
def deff(t, p):
    r = head.loc[(t,p)]; pn, se, ess = r.north_of_33S, r.north_of_33S_se, r.kish_ess; mult = np.sqrt(pn*(1-pn)/ess)
    return (float((se/mult)**2) if se>0 and mult>0 else np.nan), float(ess)

blk_rows, summ, blockmass = [], [], {}
for t in TR:
    for p in PRODS:
        k = f'{t}|{p}'
        if k not in m.files: continue
        w = m[k].astype(float); w /= w.sum(); de, ess = deff(t, p)
        B = np.bincount(cell_block, w, NBY*NBX); blockmass[k] = B; bo = np.argsort(-B)
        for r, b in enumerate(bo[:15]):
            la, lo = block_centre(b)
            blk_rows.append(dict(treatment=t, product=p, rank=r+1, block_lat=round(la,2), block_lon=round(lo,2), block_km2=round(BLOCK_KM2), mass=B[b],
                                 mass_sd_approx=np.sqrt(de*B[b]*(1-B[b])/ess), p_success=PD*B[b], p_success_per_1000km2=PD*B[b]/(BLOCK_KM2/1000), existing_coverage=blk_cov[b], status=tag(blk_cov[b])))
        order = np.argsort(-w); cum = np.cumsum(w[order]); best_any = w[order][:ncell].sum()
        uns = np.where(cell_cov<0.1)[0]; ou = uns[np.argsort(-w[uns])]; best_uns = w[ou[:ncell]].sum()
        nx_exact = float(head.loc[(t,p)].p_in_next_oi_area_not_evidence); nx_cell = float((w*FRN).sum())
        summ.append(dict(treatment=t, product=p, product_name=PRODS[p], kish_ess=ess, design_effect=de, next_area_km2=round(NEXT_KM2), next_area_mass=nx_exact, next_area_mass_cellgrid=nx_cell,
            next_area_mass_sd_approx=np.sqrt(de*nx_exact*(1-nx_exact)/ess), next_area_p_success=PD*nx_exact, next_area_p_success_per_1000km2=PD*nx_exact/(NEXT_KM2/1000),
            best_equal_area_any_mass=best_any, best_equal_area_any_p_success=PD*best_any, best_equal_area_unsearched_mass=best_uns, best_equal_area_unsearched_p_success=PD*best_uns,
            best_unsearched_cells_lat=float(np.average(LAT[ou[:ncell]], weights=w[ou[:ncell]])), best_unsearched_cells_lon=float(np.average(LON[ou[:ncell]], weights=w[ou[:ncell]])),
            ratio_best_unsearched_to_next=best_uns/nx_exact if nx_exact>0 else np.nan, mass_on_searched_ground_cov_weighted=float((w*cell_cov).sum()),
            area_km2_50pct=float((cum<0.5).sum()+1)*V.CELL_KM2, area_km2_90pct=float((cum<0.9).sum()+1)*V.CELL_KM2))
pd.DataFrame(blk_rows).to_csv(f'{OUT}/ranked-blocks-top15.csv', index=False); pd.DataFrame(summ).to_csv(f'{OUT}/next-area-summary.csv', index=False)

# widening response
rows = []
for t in ['D0','D3','D4']:
    for p in ['DS','ABS']:
        w0 = m[f'{t}|{p}'].astype(float); w0 /= w0.sum()
        for b in [1.0,0.9,0.8,0.7,0.6,0.5]:
            w = np.where(w0>0, w0**b, 0.0); w /= w.sum(); cum = np.cumsum(np.sort(w)[::-1])
            nx = float((w*FRN).sum()); uns = np.where(cell_cov<0.1)[0]; ou = uns[np.argsort(-w[uns])]; bu = float(w[ou[:ncell]].sum())
            rows.append(dict(treatment=t, product=p, beta=b, next_area_mass_cellgrid=nx, next_area_p_success=PD*nx, best_unsearched_equal_area_p_success=PD*bu, ratio=bu/nx,
                             area_km2_90pct=float((cum<0.9).sum()+1)*V.CELL_KM2, mass_on_searched_ground=float((w*cell_cov).sum()), north_of_33S=float(w[LAT>-33].sum())))
pd.DataFrame(rows).to_csv(f'{OUT}/widening-response.csv', index=False)

# rank stability
grid = [(t,p) for t in TR for p in ['DS','ABS','DS_r0','DS_r10','DS_V2'] if f'{t}|{p}' in m.files]; ref = blockmass['D0|DS']; top = ref>0; freq = {}; taus = []
for t, p in grid:
    B = blockmass[f'{t}|{p}']
    for b in np.argsort(-B)[:5]: freq[b] = freq.get(b,0)+1
    taus.append(dict(treatment=t, product=p, kendall_tau_vs_D0_all=kendalltau(ref[top], B[top]).correlation, top_block_lat=block_centre(np.argmax(B))[0], top_block_lon=block_centre(np.argmax(B))[1], top_block_coverage=blk_cov[np.argmax(B)]))
pd.DataFrame([dict(block_lat=round(block_centre(b)[0],2), block_lon=round(block_centre(b)[1],2), times_in_top5=n, of_cases=len(grid), existing_coverage=round(blk_cov[b],3), status=tag(blk_cov[b]))
              for b, n in sorted(freq.items(), key=lambda x: -x[1])]).to_csv(f'{OUT}/rank-stability-top5.csv', index=False)
pd.DataFrame(taus).to_csv(f'{OUT}/kendall-tau.csv', index=False)

# smoke statistics (mechanics only)
base = 'results/e2e-calibration-smoke-2026-10-19/case-stats'; srows = []
for d in sorted(glob.glob(base+'/case-*')):
    if not os.path.exists(d+'/case-stats.json'): continue
    s = json.load(open(d+'/case-stats.json')); t = json.load(open(d+'/truth.json')) if os.path.exists(d+'/truth.json') else s.get('truth', {}); imp = t.get('impact', {})
    for stack in ['core','core+searches','all']:
        key = f'D0|{stack}'
        if key not in s['pooled']: continue
        po = s['pooled'][key]; sd = s['mc_sd_between_replicates'].get(key, {})
        srows.append(dict(case=os.path.basename(d), truth_lat=imp.get('lat'), truth_cross_arc_nm=imp.get('cross_arc_nm'), family=t.get('family'), cause=t.get('cause'), stack=stack,
                          map_level_at_truth=po.get('hpd2d'), map_level_sd_replicates=sd.get('hpd2d'), latitude_rank=po.get('u_lat'), cross_arc_rank=po.get('u_xarc'), p_true_cause=po.get('p_true_cause'), ess_parents=po.get('ess_parents')))
pd.DataFrame(srows).to_csv(f'{OUT}/smoke-case-statistics-D0.csv', index=False)
print('done', OUT)
