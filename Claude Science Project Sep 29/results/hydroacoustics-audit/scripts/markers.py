"""Audit task 3: recompute the expected-impact markers of the module's noise-vs-impact charts and add the calibration
error found by the audit.

Module arithmetic reproduced exactly (module transcript, the cell that wrote scenario_markers.json, 10 Oct 2026):
  SE_b = eta_cal(tau, z_s) E rho c / (2 pi) S_b(tau) 10^(-TL_b/10) 10^(C/10);  PSD_b = SE_b / bandwidth_b / 6 s
  eta_cal: results-data/ram_check/eta_cal_ramcorr.csv (slope 2, T_C2, E = 900 MJ, station mean in log)
  TL_b: results-data/near_limits/ims_tl_kraken.csv (median impact path, quantile '500') minus ims_ram_delta.csv
  tau ~ log-U(0.05, 10) s; z_s in {2, 10, 30} m; C ~ N(0, 10) + N(0, 3) dB; N = 40,000; seed 20261011; m = 175 t.
  Scenarios (a) v ~ U(270, 360) m/s; (b) v ~ U(60, 150) m/s, flight-path angle U(1.4, 4) deg, total or vertical KE.
One change, declared: band_fraction is tabulated on 600 log-spaced tau values and interpolated (as the stand-in's
lhyd.py does), because the direct form needs N x 4000 memory. Added scenario (c): the end-of-flight impacts of the
core run (b) source package, 00:19 option R600 BTO only, drawn with their prior (flight) weights.

Calibration error (criteria.md, audit findings): RL_true = RL_model - r_b, where r_b = observed - model TL for air9
at the same station (M1, 10 m source). Inside the air9 span the shifted interval [q10 - r_b, q90 - r_b] is reported;
outside the span (H01W below 12.5 Hz; H08S below 6.3 Hz) the shift is unknown and +/- max|r_b| over the span is used.

Usage: python markers.py <module_dir> <air9_residuals.csv> <sources.npz> <out_json>
"""
import json
import sys

import numpy as np
import pandas as pd

mdir, resid_csv, srcp, out = sys.argv[1:5]
sys.path.insert(0, f"{mdir}/prepare")
import f35a_eta_calibration as F  # noqa: E402
import imos_stageB_map as B  # noqa: E402

H = f"{mdir}/"
cal = pd.read_csv(H + "results-data/ram_check/eta_cal_ramcorr.csv"); tab = F.eta_cal_lookup(cal, 2)
kt = pd.read_csv(H + "results-data/near_limits/ims_tl_kraken.csv", dtype={"quantile": str})
rd = pd.read_csv(H + "results-data/near_limits/ims_ram_delta.csv")
TAU_GRID = np.logspace(np.log10(0.05), 1.0, 600)
SBT = {fc: B.band_fraction(fc, 1 / TAU_GRID, 2) for fc in F.BANDS}
rng = np.random.default_rng(20261011); N = 40000; M = 175000.0
tau = 10 ** rng.uniform(np.log10(0.05), 1.0, N); zs = rng.choice(F.SRC, N); Cs = rng.normal(0, 10, N) + rng.normal(0, 3, N)
eta = np.zeros(N)
for z, (lx, ly) in tab.items():
    m = zs == z; eta[m] = 10 ** np.interp(np.log10(tau[m]), lx, ly)
v_a = rng.uniform(270, 360, N); E_a = 0.5 * M * v_a ** 2
v_b = rng.uniform(60, 150, N); g_b = np.radians(rng.uniform(1.4, 4.0, N)); E_bt = 0.5 * M * v_b ** 2; E_bv = 0.5 * M * (v_b * np.sin(g_b)) ** 2
src = np.load(srcp); col = {n: i for i, n in enumerate(src["state_columns"])}; w = np.asarray(src["w_flight"], float)
E_c = src["state"][rng.choice(len(w), N, p=w / w.sum()), col["kinetic_energy_j"]]
SC = {"a": E_a, "b_total": E_bt, "b_vertical": E_bv, "c_eof_prior": E_c}
R = pd.read_csv(resid_csv); R = R[(R.model == "M1") & (R.src_depth_m == 10.0)]
res = {"E_GJ": {k: [float(np.quantile(v, q)) / 1e9 for q in (0.05, 0.5, 0.95)] for k, v in SC.items()}, "bands": F.BANDS, "stations": {}}
for stn in ("H01W", "H08S"):
    g = kt[kt.station == stn]; dd = rd[rd.path == f"imp500_{stn}"]
    r = R[R.station == stn].set_index("fc_hz").residual_db; rmax = float(r.abs().max()); lo_span = float(r.index.min())
    st = {"range_km": float(g[g["quantile"] == "500"].range_km.iloc[0]), "air9_residual_db": {str(k): float(v) for k, v in r.items()},
          "span_lo_hz": lo_span, "unknown_bound_db": rmax, "scen": {}}
    for name, E in SC.items():
        rows = []
        for fc in F.BANDS:
            tl = np.zeros(N)
            for z in F.SRC:
                zz = 30.0 if z >= 30 else 10.0; h = dd[np.isclose(dd.src_depth_m, zz)].set_index("fc_hz").delta_db
                delta = float(np.interp(np.log10(fc), np.log10(h.index.values), h.values))
                tl[zs == z] = float(g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z) & (g["quantile"] == "500")].tl_db.iloc[0]) - delta
            Sb = np.interp(np.log10(tau), np.log10(TAU_GRID), SBT[fc])
            SE = eta * E * B.RHO_C / (2 * np.pi) * Sb * 10 ** (-tl / 10) * 10 ** (Cs / 10)
            bw = fc * (2 ** (1 / 6) - 2 ** (-1 / 6))
            psd = 10 * np.log10(np.maximum(SE / bw / 6.0, 1e-300)) + 120
            q10, q50, q90 = (float(np.quantile(psd, q)) for q in (0.1, 0.5, 0.9))
            if fc in r.index:
                s = -float(r[fc]); ext = (min(q10, q10 + s), max(q90, q90 + s)); inside = True
            else:
                ext = (q10 - rmax, q90 + rmax); inside = False; s = None
            rows.append(dict(fc=fc, q10=q10, q50=q50, q90=q90, shift_db=s, ext_lo=ext[0], ext_hi=ext[1], inside_span=inside))
        st["scen"][name] = rows
    res["stations"][stn] = st
json.dump(res, open(out, "w"), indent=1)
for stn, st in res["stations"].items():
    for k, rows in st["scen"].items():
        print(stn, k, [(r_["fc"], round(r_["q50"], 1), round(r_["ext_lo"], 1), round(r_["ext_hi"], 1)) for r_ in rows[::3]])
