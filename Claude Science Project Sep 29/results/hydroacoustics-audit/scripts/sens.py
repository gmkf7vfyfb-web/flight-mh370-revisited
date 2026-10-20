"""Audit task 4: the stand-in's power check (and R_hyd) as a SENSITIVITY with the transmission loss perturbed.

The stand-in scripts (results/hydroacoustics-pleiades-test-standin/standin-scripts/, lhyd.py sha256 5000c56e...)
are imported UNCHANGED; this wrapper subclasses lhyd.Model and edits only its TL tables after construction:
  tl_ims[stn][(fc, z)]  (H01W, H08S; impact paths)      tl_imos[lg][(fc, z)]  (IMOS loggers)
and, for the 'recal' variants, its eta_cal table (etab) by repeating the F-35A inversion with the same TL change on
the H11 paths (module results-data/ram_check/h11_tl_ramcorr.csv).

VARIANT (env AUDIT_VARIANT):
  base            no change (reproduction check)
  lvl-8 / lvl+8   TL -8 / +8 dB in every band (air9 RMS residual, M1); recalibration would cancel it exactly
  tilt+ / tilt-   TL + s log2(f/25 Hz), s = +10.4 / -10.4 dB/oct, clipped to +/-15 dB (air9 H01W slope, M1)
  emp             TL + the measured air9 per-band residual at H08S (observed - model, M1, 6.3-63 Hz; 5 Hz held at
                  the 6.3 Hz value), on impact paths only (the "best-calibrated alternative", airgun-based)
  emp-recal       as emp, and the same correction applied to the H11 paths before re-inverting eta_cal
STATIONS (env AUDIT_STATIONS, default 'ims,imos'): which TL tables are perturbed.

Usage: AUDIT_VARIANT=... python sens.py power <standin_scripts_dir> <air9_residuals.csv> <module_dir> <imos_events.json> <kadri.csv> <sources.npz> <out_dir>
"""
import os
import sys

import numpy as np
import pandas as pd

mode, sdir, resid_csv = sys.argv[1:4]
sys.path.insert(0, sdir)
import lhyd  # noqa: E402

VAR = os.environ.get("AUDIT_VARIANT", "base")
WHICH = os.environ.get("AUDIT_STATIONS", "ims,imos").split(",")
R = pd.read_csv(resid_csv)
R = R[(R.model == "M1") & (R.src_depth_m == 10.0) & (R.station == "H08S")].set_index("fc_hz").residual_db


def delta(fc):
    if VAR == "base":
        return 0.0
    if VAR.startswith("lvl"):
        return float(VAR[3:])
    if VAR.startswith("tilt"):
        s = 10.4 if VAR == "tilt+" else -10.4
        return float(np.clip(s * np.log2(fc / 25.0), -15, 15))
    if VAR.startswith("emp"):
        return float(R.get(fc, R.iloc[0]))
    raise ValueError(VAR)


Base = lhyd.Model


class Model(Base):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        F = self.F
        if "ims" in WHICH:
            for stn in self.tl_ims:
                for key in self.tl_ims[stn]:
                    self.tl_ims[stn][key] = self.tl_ims[stn][key] + delta(key[0])
        if "imos" in WHICH:
            for lg in self.tl_imos:
                for key in self.tl_imos[lg]:
                    self.tl_imos[lg][key] = self.tl_imos[lg][key] + delta(key[0])
        if VAR.endswith("recal"):
            h11 = pd.read_csv(self.P / "results-data/ram_check/h11_tl_ramcorr.csv")
            taus = None; new = {}
            for z, (lx, ly) in self.etab.items():
                tau = 10 ** lx; ratio = []
                for st in ("H11N", "H11S"):
                    g = h11[(h11.station == st) & np.isclose(h11.src_depth_m, z)].set_index("fc_hz").tl_db
                    g0 = sum(self.B.band_fraction(fc, 1 / tau, 2) * 10 ** (-g[fc] / 10) for fc in F.BANDS)
                    g1 = sum(self.B.band_fraction(fc, 1 / tau, 2) * 10 ** (-(g[fc] + delta(fc)) / 10) for fc in F.BANDS)
                    ratio.append(np.log10(g0 / g1))
                new[z] = (lx, ly + np.mean(ratio, axis=0))
            self.etab = new


lhyd.Model = Model

if mode == "power":
    import power_check as PC  # noqa: E402
    PC.lhyd.Model = Model
    sys.argv = ["power_check.py"] + sys.argv[4:9]
    PC.main()

if mode == "rhyd":
    # ln R_hyd on the stand-in's 5,000-row source package (NOT the full impact rows of rhyd_result.py), scenario A
    # and A-IMOS, real event lists, K = 8 nuisance replicas per row (as power_check.K_REP), seed as power_check.
    import json, pathlib
    from scipy.special import logsumexp
    mod, evj, kd, srcp, outd = sys.argv[4:9]
    m = Model(mod, evj, kd); src = np.load(srcp)
    c = {n: i for i, n in enumerate(src["state_columns"])}; S = src["state"]
    t, la, lo, E = S[:, c["unix_s"]], S[:, c["latitude_deg"]], S[:, c["longitude_deg"]], S[:, c["kinetic_energy_j"]]
    K = 8; rep = np.repeat(np.arange(len(la)), K)
    st = m.station_terms(t[rep], la[rep], lo[rep], E[rep], np.random.default_rng(20261010), "A")
    out = {"variant": VAR, "stations": WHICH, "n_rows": int(len(la)), "K": K}
    for lab, (k0, kH) in (("reweighted", ("w_flight", "w_H")), ("fixed", ("w_flight_fixed", "w_H_fixed"))):
        w0 = np.asarray(src[k0], float)[rep]; wH = np.asarray(src[kH], float)[rep]
        for v, L in (("A", st["total"]), ("A-IMOS", sum(st[lg] for lg in m.B.LOGGERS)), ("H01W-only", st["H01W"])):
            lr = float(logsumexp(np.log(wH) + L) - np.log(wH.sum()) - (logsumexp(np.log(w0) + L) - np.log(w0.sum())))
            half = []
            for h in (0, 1):
                mk = (rep % 2) == h
                half.append(float(logsumexp(np.log(wH[mk]) + L[mk]) - np.log(wH[mk].sum()) - (logsumexp(np.log(w0[mk]) + L[mk]) - np.log(w0[mk].sum()))))
            out[f"{lab}|{v}"] = dict(lnR=lr, split_half=half)
    pathlib.Path(outd).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(outd) / "rhyd_pkg.json").write_text(json.dumps(out, indent=1))
    print(VAR, {k: round(v["lnR"], 4) for k, v in out.items() if isinstance(v, dict)})
