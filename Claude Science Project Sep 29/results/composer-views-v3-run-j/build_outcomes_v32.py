"""Composer views v3.2 on run J (northern supplement), step 1: per settling supplement folder (ruleB | a1strat), one table of SETTLED OUTCOMES with every factor (numpy).

Usage: python build_outcomes_v3.py <settling folder name> OUT.npz
Outcomes = the (row, draw) outcomes resampled by settling run J (settling/run-j/<folder>/<tag>_draws.npz) in the products
'total' x {all, A1, A2, B} of every 00:19 treatment in the folder (each outcome weight 1/N inside its product).
Per outcome:
  * seabed position: the mass-weighted settled pieces (fate 0) as sparse fractions per equal-area cell and per latitude sub-bin
    (views v2 grid); outcomes with no settled piece are carried at the impact point (counted);
  * searched areas: P(no find | settled field) per detection variant of the per-cell model (commit 237090ab; code imported from
    engine/hypotheses/seabed-search/spatial/score_spatial_run_j.py, unchanged), and the searched fraction before evidence;
    rho field scale 0x / 1x / 5x / 10x = V1_rho0 / V1_central / V1_rho0.25 / V1_rho0.5 (rho0 0 / 0.05 / 0.25 / 0.5, same terrain shape);
  * at the impact point (end-of-flight row via <tag>_source.npy): drift ln L per option and ocean model (views3_common.Drift),
    Pleiades ln J per ocean model; 00:19:29 crossing arc position (latent:last_burst_*); flight-end family (family4_code).
Checks written into the file: module Z per product for V0 and V1 (summary.json) reproduced; Pleiades cell equal to the module's
per-impact column cell (waypoints sets, where the column exists); impacts.f64 latitude equal to end-of-flight latitude.
"""
import sys, os, json, pathlib, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PROJ / 'engine/hypotheses/seabed-search/spatial'))
import views3_common as C
V = C.V
import score_spatial_run_j as SS
X = C.X
SET = sys.argv[1]; OUTP = pathlib.Path(sys.argv[2])   # SET = ruleB | a1strat  (views v3.2, run J northern supplement)
SUPP = X / 'settling/run-j-supplement'
SD = SUPP / ('ruleB-waypoints' if SET == 'ruleB' else 'a1-stratified')
RED = np.load(X / 'end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz')
VARS = list(SS.VARIANTS)
SF_VARS = ['V0_scalar', 'V1_central', 'V1_oi_uniform', 'V1_without_oi', 'V2_pessimistic']
COLS = (X / 'end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt').read_text().split(); CI = {c: i for i, c in enumerate(COLS)}
STRIDE = SS.STRIDE
# a1strat source strata: 0 reduced-table row, 1 run-j-a1branch, 2 north-k2-a1branch, 3 run-j-a1outside (seed, row into impacts32.npy)
EOF_ST = {1: 'end-of-flight/run-j-a1branch/run-j-waypoints', 2: 'end-of-flight/run-j-supplement/north-k2-a1branch', 3: 'end-of-flight/run-j-supplement/run-j-a1outside'}
PLE_ST = {1: X / 'pleiades/run-j-a1branch/run-j-waypoints', 2: X / 'pleiades/run-j-supplement/north-k2-a1branch', 3: X / 'pleiades/run-j-supplement/run-j-a1outside'}
PLE_RED = X / 'pleiades/run-j-supplement/reduced/run-j-waypoints/seed-0/pleiades-lnL.npy'
SA_SET = 'ruleB-waypoints' if SET == 'ruleB' else 'a1-stratified'
t0 = time.time()
tag = next(SD.glob('*_impacts.f64')).name[:-len('_impacts.f64')]
info = json.loads((SD / f'{tag}_info.json').read_text())
imp = np.memmap(SD / f'{tag}_impacts.f64', dtype='<f8', mode='r').reshape(-1, 14)
el = np.memmap(SD / f'{tag}_elements.f64', dtype='<f8', mode='r').reshape(-1, 8)
src = np.load(SD / f'{tag}_source.npy'); dr = np.load(SD / f'{tag}_draws.npz')
summ = json.loads((X / 'searched-areas/run-j-supplement/settled_summary.json').read_text())['sets'][SA_SET]
n_rows = imp.shape[0]
key = el[:, 0].astype(np.int64) * STRIDE + el[:, 1].astype(np.int64)
assert not np.any(np.diff(key) < 0)
newblk = np.r_[True, key[1:] != key[:-1]]; okey = key[newblk]; oidx = np.cumsum(newblk) - 1; del newblk, key
n_out = len(okey)

# products used
prods = []
for j, p in enumerate(info['products']):
    if p['cell'] != 'total':
        continue
    r, d = dr[f'rows_{j}'].astype(np.int64), dr[f'draws_{j}'].astype(np.int64)
    o = np.searchsorted(okey, r * STRIDE + d); assert np.array_equal(okey[o], r * STRIDE + d), j
    prods.append((j, p, o))
U = np.unique(np.concatenate([o for _, _, o in prods])); nU = len(U)
pos = np.full(n_out, -1, np.int64); pos[U] = np.arange(nU)
urow = okey[U] // STRIDE; udraw = okey[U] % STRIDE

# settled pieces of the union outcomes
L = SS.Lookup(X / 'searched-areas/spatial-fields/fields.npz'); nv = len(L.names)
fate = np.asarray(el[:, 4]); keep = (fate == 0.0) & (pos[oidx] >= 0); sel = np.where(keep)[0]; del fate, keep
acc = np.zeros((nU, nv)); msum = np.zeros(nU); latm = np.zeros(nU); lonm = np.zeros(nU)
NC = V.NY * V.NX + 1; pc_key, pc_w, ps_key, ps_w = [], [], [], []
CH = 4_000_000
for s0 in range(0, len(sel), CH):
    ee = sel[s0:s0 + CH]; la = np.asarray(el[ee, 5]); lo = np.asarray(el[ee, 6]); m = np.asarray(el[ee, 7]); o = pos[oidx[ee]]
    Vv = L(la, lo)
    msum += np.bincount(o, m, nU); latm += np.bincount(o, m * la, nU); lonm += np.bincount(o, m * lo, nU)
    for k in range(nv):
        acc[:, k] += np.bincount(o, m * Vv[:, k], nU)
    kc = o * NC + V.cell_index(la, lo); u, inv = np.unique(kc, return_inverse=True); pc_key.append(u); pc_w.append(np.bincount(inv, m))
    ks = o * (V.NSUB + 1) + V.sub_index(la); u, inv = np.unique(ks, return_inverse=True); ps_key.append(u); ps_w.append(np.bincount(inv, m))
del sel, oidx
ilat = np.asarray(imp[urow, 1]); ilon = np.asarray(imp[urow, 2])
carried = msum <= 0
S_arr = np.where(carried[:, None], L(ilat, ilon), acc / np.maximum(msum, 1e-300)[:, None]); S = {n: S_arr[:, k] for k, n in enumerate(L.names)}
latm = np.where(carried, ilat, latm / np.maximum(msum, 1e-300)); lonm = np.where(carried, ilon, lonm / np.maximum(msum, 1e-300))
def merge(keys, ws, base):
    k = np.concatenate(keys); w = np.concatenate(ws); u, inv = np.unique(k, return_inverse=True); w = np.bincount(inv, w)
    o = u // base; b = u % base; return o, b, w
co, cb, cw = merge(pc_key, pc_w, NC); so, sb, sw = merge(ps_key, ps_w, V.NSUB + 1); del pc_key, pc_w, ps_key, ps_w
# carried outcomes: impact point, fraction 1
if carried.any():
    ci = np.where(carried)[0]
    co = np.r_[co, ci]; cb = np.r_[cb, V.cell_index(ilat[ci], ilon[ci])]; cw = np.r_[cw, np.ones(len(ci))]
    so = np.r_[so, ci]; sb = np.r_[sb, V.sub_index(ilat[ci])]; sw = np.r_[sw, np.ones(len(ci))]
cw = cw / np.bincount(co, cw, nU)[co]; sw = sw / np.bincount(so, sw, nU)[so]

Pv, SFv = {}, {}
for v in VARS:
    P, sf = SS.variant_P(S, v); Pv[v] = P; SFv[v] = sf

# checks: module Z per product reproduced (per-outcome P, product mean)
chk = {'set': SET, 'n_rows': int(n_rows), 'n_outcomes_folder': int(n_out), 'n_outcomes_used': int(nU), 'carried_outcomes': int(carried.sum())}
zmax = 0.0; nchk = 0
EW = json.loads((SUPP / 'a1-stratified/eof-convention-weights.json').read_text())
SPD = {(q['D'], q['subset']): q for q in summ['products'] if q['cell'] == 'total'}
for (j, p, o) in prods:
    sp = SPD.get((p['D'], p['subset']))
    if sp is None:
        continue
    w = np.ones(len(o))
    if sp.get('eof_convention_weighted'):
        w = np.where(src[urow[pos[o]], 0] == 0, EW[p['D']]['outcome_weight_for_rest_rows_nonA1'], 1.0)
    zref = sp['base_rho0.05'].get('Z_settled_resample')
    if zref is not None:
        zmax = max(zmax, abs(float((w * Pv['V0_scalar'][pos[o]]).sum() / w.sum()) - zref)); nchk += 1
chk['module_Z_V0_checked_products'] = nchk
chk['module_Z_max_abs_diff'] = zmax

# impact-point factors per row
D = C.Drift(); dl = D.lnL(ilat, ilon); PL = C.Pleiades(); pj = PL.lnJ(ilat, ilon)
srcs = src[urow, 0].astype(np.int64); erow = src[urow, 2].astype(np.int64)
seed = np.zeros(nU, np.int64); fam4 = np.full(nU, -1, np.int64); elat = np.full(nU, np.nan); blat = np.full(nU, np.nan); blon = np.full(nU, np.nan)
pcell_mis = 0; pcell_n = 0
red = (srcs == 0) if SET == 'a1strat' else np.ones(nU, bool)
if red.any():
    ix = erow[red]; tech = RED['technique'][ix].astype(np.int64)
    seed[red] = np.where(tech == 0, 0, 1) * 10000 + RED['seed'][ix].astype(np.int64)   # group 0 production seeds 1-24, group 1 supplement seeds 1001-1016
    fam4[red] = RED['family4_code'][ix].astype(np.int64); elat[red] = RED['latitude_deg'][ix]
    cell = np.load(PLE_RED, mmap_mode='r')['cell']; cc = np.asarray(cell[ix]).astype(np.int64)
    pi, pj_, ok = PL.cell(ilat[red], ilon[red]); mine = np.where(ok, pi * PL.nn + pj_, 0xFFFFFFFF); pcell_mis += int((mine != cc).sum()); pcell_n += len(cc)
for st in (1, 2, 3):
    for k in np.unique(src[urow[srcs == st], 1]) if SET == 'a1strat' else []:
        rk = np.where((srcs == st) & (src[urow, 1] == k))[0]; ix = erow[rk]; o_ = np.argsort(ix); ixs = ix[o_]
        A = np.asarray(np.load(X / EOF_ST[st] / f'seed-{int(k)}' / 'impacts32.npy', mmap_mode='r')[ixs])
        blat[rk[o_]] = A[:, CI['latent:last_burst_latitude_deg']]; blon[rk[o_]] = A[:, CI['latent:last_burst_longitude_deg']]
        fam4[rk[o_]] = A[:, CI['family4_code']].astype(np.int64); elat[rk[o_]] = A[:, CI['latitude_deg']]; seed[rk] = (st + 1) * 10000 + int(k)
        pf = PLE_ST[st] / f'seed-{int(k)}' / 'pleiades-lnL.npy'
        if pf.exists():
            cc = np.asarray(np.load(pf, mmap_mode='r')['cell'][ixs]).astype(np.int64); pi, pj_, ok = PL.cell(ilat[rk[o_]], ilon[rk[o_]])
            mine = np.where(ok, pi * PL.nn + pj_, 0xFFFFFFFF); pcell_mis += int((mine != cc).sum()); pcell_n += len(cc)
chk['eof_latitude_max_abs_diff'] = float(np.nanmax(np.abs(elat - ilat)))
chk['pleiades_cell_mismatch'] = [pcell_mis, pcell_n]
chk['crossing_available_share'] = float(np.isfinite(blat).mean())
noburst = ~(np.isfinite(blat) & np.isfinite(blon))
sarc = np.where(noburst, np.nan, V.arc_s(np.where(noburst, 0.0, blat), np.where(noburst, 0.0, blon)))
fam = np.full(nU, -1, np.int8); fam[fam4 == 1] = 0; fam[fam4 == 2] = 1; fam[np.isin(fam4, (3, 6))] = 2
chk['family_other_outcomes'] = int((fam < 0).sum()); chk['drift_inside_dedicated_span_share'] = float(dl['inside_dedicated_span'].mean())

out = {'seed': seed.astype(np.int32), 'src': srcs.astype(np.int8), 'erow': erow, 'fam': fam, 'sarc': sarc, 'ilat': ilat, 'ilon': ilon, 'slat': latm, 'slon': lonm,
       'carried': carried, 'drift_inside': dl['inside_dedicated_span'],
       'cell_o': co.astype(np.int32), 'cell_b': cb.astype(np.int32), 'cell_w': cw, 'sub_o': so.astype(np.int32), 'sub_b': sb.astype(np.int32), 'sub_w': sw,
       'chk': json.dumps(chk), 'products': json.dumps([{**{k: p[k] for k in ('option', 'D', 'cell', 'subset', 'N', 'row_ess_kish', 'share_of_option')}, 'j': j} for j, p, _ in prods])}
for j, p, o in prods:
    out[f'prod_{j}'] = pos[o].astype(np.int32)
for v in VARS:
    out[f'P|{v}'] = Pv[v]
for v in SF_VARS:
    out[f'SF|{v}'] = SFv[v]
for (o_, t_), arr in dl.items() if False else [(k, v) for k, v in dl.items() if k != 'inside_dedicated_span']:
    out[f'drift|{o_}|{t_}'] = arr
for t_ in ('G', 'C'):
    out[f'ple|{t_}'] = pj[t_]
out['PREF'] = PL.PREF
tmp = OUTP.with_suffix('.tmp.npz'); np.savez(tmp, **out); os.replace(tmp, OUTP)
chk['wall_s'] = time.time() - t0
print(json.dumps(chk), flush=True)
