"""Composer views v3, view (a)(i): each evidence type's own surface evaluated at every 10 NM bin of the 7th-arc span (v2 span), convolved
with ONE fixed end-of-flight displacement distribution (impact minus 00:19:29 crossing, core D0, pooled; v2 arc-r.npz 'disp').
Sampling-free, so it reaches the whole arc span (the settled outcome sample does not: view (a)(ii) loses the unreachable share).
Searched areas: per-cell model evaluated as a POINT target at the impact point (settling not applied in this view; settled offset p90
1.8-4.6 km, settling run J); drift: dedicated arc-latitude run + run A outside 26-40 S (views3_common); Pleiades conditional on H.
Usage: python view_a_i_v3.py OUT.npz"""
import sys, json, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PROJ / 'engine/hypotheses/seabed-search/spatial'))
import views3_common as C, views_lib as VL
import score_spatial_run_j as SS
V = C.V; X = C.X
ARCR = np.load(X / 'composer/run-j-views/work/arc-r.npz')
DISP = ARCR['disp']; de_c = np.arange(-500, 500, 5) + 2.5
keep = DISP > 1e-6 * DISP.max(); ie, jn = np.where(keep); dw = DISP[keep] / DISP[keep].sum(); dE, dN = de_c[ie], de_c[jn]
SB_MID = (np.arange(V.NSB) + 0.5) * V.SBIN_NM; kb = np.where(ARCR['span'])[0]; sk = SB_MID[kb]; alat, alon = V.arc_point(sk)
PL = (alat[:, None] + dN[None] / 111.32).ravel(); PO = (alon[:, None] + dE[None] / (111.32 * np.cos(np.radians(alat[:, None] + dN[None] / 222.64)))).ravel()
W2 = np.broadcast_to(dw[None], (len(sk), len(dw))).ravel() / len(sk)
li01 = np.clip(np.searchsorted(V.L01_EDGES, PL, side='right') - 1, 0, len(V.L01_MID) - 1)
D = C.Drift(); dl = D.lnL(PL, PO); P = C.Pleiades(); pj = P.lnJ(PL, PO)
Lk = SS.Lookup(X / 'searched-areas/spatial-fields/fields.npz'); A = Lk(PL, PO); S = {n: A[:, k] for k, n in enumerate(Lk.names)}
surf = {}
for o, nm in (('off', 'D'), ('B', 'AB'), ('C', 'AC'), ('pop', 'Apop')):
    surf[nm] = [np.exp(dl[(o, 'G')] - C.LREF), np.exp(dl[(o, 'C')] - C.LREF)]
surf['P'] = [np.exp(pj['G'] - P.PREF), np.exp(pj['C'] - P.PREF)]
for nm, v in (('S', 'V1_central'), ('S_V0', 'V0_scalar'), ('S_V2', 'V2_pessimistic'), ('S_V3', 'V3_optimistic'), ('S_r0', 'V1_rho0'), ('S_r5', 'V1_rho0.25'), ('S_r10', 'V1_rho0.5')):
    surf[nm] = [SS.variant_P(S, v)[0]]
out = {'mids': V.L01_MID}; meta = {'arc_bins': int(len(sk)), 'displacement_points': int(len(dw)), 'points': int(len(PL))}
for E, Ls in surf.items():
    lam = 0.0; ncw = 0.0
    for Lm in Ls:
        ok = np.isfinite(Lm); bar = np.sum(W2[ok] * Lm[ok]) / np.sum(W2[ok]); lam = lam + np.where(ok, Lm, bar) / len(Ls); ncw += np.sum(W2[~ok]) / len(Ls)
    w = W2 * lam; h01 = np.bincount(li01, w, len(V.L01_MID)); sbm = w.reshape(len(sk), -1).sum(1); SBf = np.zeros(V.NSB); SBf[kb] = sbm
    c = np.concatenate([[0], np.cumsum(SBf)]) / SBf.sum()
    out[E] = h01; out[E + '_SB'] = SBf
    meta[E] = {'lnE_uniform_i': float(np.log(w.sum())), 'not_computed_share': float(ncw), 'median_lat': VL.quantiles(h01, V.L01_EDGES, (0.5,))[0],
               'q05': VL.quantiles(h01, V.L01_EDGES)[0], 'q95': VL.quantiles(h01, V.L01_EDGES)[2],
               'median_arc_nm': float(np.interp(0.5, c, np.arange(V.NSB + 1) * V.SBIN_NM)), 'north_of_33S': float(h01[V.L01_MID > -33].sum() / h01.sum())}
h0 = np.bincount(li01, W2, len(V.L01_MID)); out['U'] = h0
meta['U'] = {'median_lat': VL.quantiles(h0, V.L01_EDGES, (0.5,))[0], 'north_of_33S': float(h0[V.L01_MID > -33].sum() / h0.sum())}
out['meta'] = json.dumps(meta); np.savez_compressed(sys.argv[1], **out)
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: round(vv, 3) for kk, vv in v.items()}) for k, v in meta.items()}, indent=0))
