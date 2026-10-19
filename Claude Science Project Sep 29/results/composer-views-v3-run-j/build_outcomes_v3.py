"""Composer views v3 on run J, step 1: per settling folder, one table of SETTLED OUTCOMES with every factor (numpy).

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
SET = sys.argv[1]; OUTP = pathlib.Path(sys.argv[2])
SD = X / ('settling/run-j-a1branch/run-j-waypoints' if SET == 'run-j-a1branch-waypoints' else f'settling/run-j/{SET}')
EOF_ROOT = {'run-j-waypoints': 'end-of-flight/run-j/run-j-waypoints', 'run-j-free': 'end-of-flight/run-j/run-j-free',
            'run-j-descent-climb': 'end-of-flight/run-j/run-j-descent-climb', 'run-j-repro-radar': 'end-of-flight/run-j/run-j-repro-radar',
            'run-j-both-burst-waypoints': 'end-of-flight/run-j-both-burst/run-j-waypoints',
            'run-j-a1branch-waypoints': 'end-of-flight/run-j/run-j-waypoints'}[SET]
# A1-branch folder (v3.1): two sources, source stratum 0 = production waypoints, 1 = A1-branch pass (settling rja1_source.npy)
EOF_SRC = {0: EOF_ROOT, 1: 'end-of-flight/run-j-a1branch/run-j-waypoints'}
PLE_SRC = {0: X / 'pleiades/run-j/run-j-waypoints', 1: X / 'pleiades/run-j-a1branch/run-j-waypoints'}
PLE_ROOT = {'run-j-waypoints': X / 'pleiades/run-j/run-j-waypoints', 'run-j-both-burst-waypoints': X / 'pleiades/run-j/both-burst/run-j-waypoints'}.get(SET)
VARS = list(SS.VARIANTS)
SF_VARS = ['V0_scalar', 'V1_central', 'V1_oi_uniform', 'V1_without_oi', 'V2_pessimistic']   # searched fraction depends only on grid / OI mode
COLS = (X / EOF_ROOT / 'seed-1' / 'COLUMNS.txt').read_text().split()
CI = {c: i for i, c in enumerate(COLS)}
STRIDE = SS.STRIDE

t0 = time.time()
tag = next(SD.glob('*_impacts.f64')).name[:-len('_impacts.f64')]
info = json.loads((SD / f'{tag}_info.json').read_text())
imp = np.memmap(SD / f'{tag}_impacts.f64', dtype='<f8', mode='r').reshape(-1, 14)
el = np.memmap(SD / f'{tag}_elements.f64', dtype='<f8', mode='r').reshape(-1, 8)
src = np.load(SD / f'{tag}_source.npy'); dr = np.load(SD / f'{tag}_draws.npz')
summ = json.loads(((X / 'searched-areas/run-j-a1branch/settled_summary.json') if SET == 'run-j-a1branch-waypoints' else (X / 'searched-areas/run-j-spatial' / SET / 'summary.json')).read_text())
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
zmax = 0.0
for (j, p, o), sp in zip(prods, [q for q in summ['products'] if q['cell'] == 'total']):
    assert sp['D'] == p['D'] and sp['subset'] == p['subset']
    for v in ('V0_scalar', 'V1_central', 'V2_pessimistic', 'V3_optimistic', 'V1_rho0.5'):
        zref = sp['variants_vs_V0'][v]['Z'] if 'variants_vs_V0' in sp else sp[v]['Z']
        zmax = max(zmax, abs(float(Pv[v][pos[o]].mean()) - zref))
chk['module_Z_max_abs_diff'] = zmax

# impact-point factors per row
D = C.Drift(); dl = D.lnL(ilat, ilon); PL = C.Pleiades(); pj = PL.lnJ(ilat, ilon)
srcs = src[urow, 0].astype(np.int64); seed = src[urow, 1].astype(np.int64) + 100 * srcs; erow = src[urow, 2].astype(np.int64)
blat = np.full(nU, np.nan); blon = np.full(nU, np.nan); fam4 = np.full(nU, -1, np.int64); elat = np.full(nU, np.nan)
pcell_mis = 0; pcell_n = 0
for k in np.unique(seed):
    rk = np.where(seed == k)[0]; sk_, kk_ = int(k) // 100, int(k) % 100
    I32 = np.load(X / (EOF_SRC[sk_] if SET == 'run-j-a1branch-waypoints' else EOF_ROOT) / f'seed-{kk_}' / 'impacts32.npy', mmap_mode='r')
    ix = erow[rk]; o_ = np.argsort(ix); ixs = ix[o_]
    A = np.asarray(I32[ixs])
    blat[rk[o_]] = A[:, CI['latent:last_burst_latitude_deg']]; blon[rk[o_]] = A[:, CI['latent:last_burst_longitude_deg']]
    fam4[rk[o_]] = A[:, CI['family4_code']].astype(np.int64); elat[rk[o_]] = A[:, CI['latitude_deg']]
    PR_ = PLE_SRC[sk_] if SET == 'run-j-a1branch-waypoints' else PLE_ROOT
    if PR_ is not None and (PR_ / f'seed-{kk_}' / 'pleiades-lnL.npy').exists():
        cell = np.load(PR_ / f'seed-{kk_}' / 'pleiades-lnL.npy', mmap_mode='r')['cell']
        cc = np.asarray(cell[ixs]).astype(np.int64); pi, pj_, ok = PL.cell(ilat[rk[o_]], ilon[rk[o_]])
        mine = np.where(ok, pi * PL.nn + pj_, 0xFFFFFFFF); pcell_mis += int((mine != cc).sum()); pcell_n += len(cc)
chk['eof_latitude_max_abs_diff'] = float(np.nanmax(np.abs(elat - ilat)))
chk['pleiades_cell_mismatch'] = [pcell_mis, pcell_n]
noburst = ~(np.isfinite(blat) & np.isfinite(blon))
sarc = np.where(noburst, np.nan, V.arc_s(np.where(noburst, 0.0, blat), np.where(noburst, 0.0, blon)))
fam = np.full(nU, -1, np.int8); fam[fam4 == 1] = 0; fam[fam4 == 2] = 1; fam[np.isin(fam4, (3, 6))] = 2
chk['family_other_outcomes'] = int((fam < 0).sum()); chk['drift_inside_dedicated_span_share'] = float(dl['inside_dedicated_span'].mean())

out = {'seed': seed.astype(np.int16), 'src': srcs.astype(np.int8), 'erow': erow, 'fam': fam, 'sarc': sarc, 'ilat': ilat, 'ilon': ilon, 'slat': latm, 'slon': lonm,
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
