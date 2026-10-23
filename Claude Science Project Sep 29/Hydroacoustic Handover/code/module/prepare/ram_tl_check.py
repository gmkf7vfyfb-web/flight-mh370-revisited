"""PRE-REGISTRATION and implementation: parabolic-equation (RAM) cross-check of the KRAKEN adiabatic TL used
in stage B, stage C and the air8 control. Committed BEFORE any matched RAM-vs-KRAKEN comparison was
computed. (One trial pyram run on imp500-3376, 10 m source, at 10 and 40 Hz, without band averaging, was
used only to time the code and check the input format.)

QUESTION: is the adiabatic incoherent-mode TL to seabed receivers up-slope (Perth Canyon 409-447 m,
Portland shelf 151-164 m) pessimistic, as declared in the item 3 note? Does the air8 ridge blockage at H01W
survive in a model that couples modes? And how far does adiabatic TL from a source on the Japan slope to H11
differ from a coupled solution (it sets the F-35A eta calibration)?

PATHS (shared ocean transport exports, the stage B stubschema conversions):
  imp500-3376 (Perth Canyon), imp500-3274 (Portland), air8-H01W (ridge blockage control), air9-H01W
  (the validated SOFAR path: the sanity check of this set-up), f35a-H11S (calibration path).
MODELS, same environment for both: profiles every 5 km from air9_tl_validation.build_profiles (the median
  bathymetry of each 5 km window, sound speed from the shared nodes, held SA/CT below the deepest WOA23
  level), the 'hard' fluid half-space (cp 1650 m/s, rho 1.9, 0.5 dB/lambda), NO water absorption in
  EITHER model (pyram has none; KRAKEN is rerun here without Francois-Garrison), the same spherical
  correction 10 log10(x / sin x), and the same receiver depth as stage B (path end depth - 2 m; the triad
  depth for H01W and H11S).
  KRAKEN: kraken_tl.tl_path, adiabatic incoherent modes, at the band centre (as stage B).
  RAM: pyram 1.3.0 (Collins' RAM split-step Pade, 8 terms, 1 stability constraint, 20-wavelength absorbing
  layer, self-starter). Primary grid dr = 2 lambda, dz = lambda / 20 (lambda at 1500 m/s). Band value:
  intensity mean over 9 frequencies log-spaced across the third octave and over the last 500 m of range.
CONVERGENCE (decided before running): on imp500-3376 at 5 and 40 Hz, rerun with dr = lambda, dz = lambda/40.
  If any band value moves by more than 1 dB, the finer grid is used for every path.
BANDS: 5, 10, 20, 40 Hz third octaves. SOURCE DEPTHS: 10 and 30 m. (A 2 m source is below the 40 Hz depth
  step; Delta at 10 m stands for 2 m, declared.)
STATISTIC: Delta_b = TL_KRAKEN - TL_RAM (dB) per path, band and source depth. Delta > 0 means KRAKEN is
  pessimistic.
DECISION RULES, fixed now:
  (1) Set-up sanity: on air9-H01W, the median |Delta| over bands and source depths <= 3 dB. Otherwise the
      comparison is reported as NOT ASSESSED, and nothing below is applied.
  (2) IMOS correction: the stage B TL table is corrected by Delta (Perth Canyon Delta for 3315 and 3376,
      Portland Delta for 3274 and 3275; interpolated linearly in log f across the four bands, clamped at the
      ends, applied to every impact quantile; Delta at 10 m also used for 2 m; bands KRAKEN recorded as
      'no_modes' are given the interpolated RAM band value instead). The H11 TL is corrected by the
      f35a-H11S Delta (both triads). Stage C (f35a_eta_calibration.stage_c and calibrate) is then rerun on
      the corrected tables, with the same seed and draws.
  (3) Verdict: if the corrected stage C P_D(any open logger), false alarm 0.005, primary curve (f^-2), is
      below 0.1, the conclusion that IMOS cannot detect the impact is ROBUST TO THE TL MODEL. Otherwise it
      is OVERTURNED, and the item 3 note says so.
  (4) air8: if the RAM air8-H01W TL in excess of air9-H01W (Delta_H01, the band mean) is >= 20 dB, the
      blockage explanation of the air8 non-observation SURVIVES coupling. Otherwise it is WEAKENED.
OUTPUTS: <out>/ram_vs_kraken.csv, <out>/convergence.json, <out>/imos_tl_ramcorr.csv, <out>/h11_tl_ramcorr.csv,
  <out>/stageC_ramcorr_pd_summary.csv, <out>/verdicts.json.
Usage: python ram_tl_check.py <stubschema_dir> <f35a_cal_dir> <at_dir> <out_dir> <imos_tl.csv>
       <stageA summary.json> <stand-in summary json>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from pyram.PyRAM import PyRAM

sys.path.insert(0, str(Path(__file__).parent))
import air9_tl_validation as A  # noqa: E402
import f35a_eta_calibration as F  # noqa: E402
import kraken_tl as K  # noqa: E402

PATHS = {"imp500_3376": None, "imp500_3274": None, "air8_H01W": "H01W", "air9_H01W": "H01W", "f35a_H11S": "H11S"}
BANDS = [5.0, 10.0, 20.0, 40.0]
SRC = [10.0, 30.0]
BOT = A.BOTTOMS["hard"]
NF = 9


def env(stub, name):
    b = pd.read_csv(stub / f"bathy_{name}.csv")
    s = pd.read_csv(stub / f"ssp_{name}.csv")
    rprof, prof = A.build_profiles(b, s)
    nodes = A.node_profiles(s)
    keys = sorted(nodes)
    nr = np.array([nodes[k][0] for k in keys])
    z = nodes[keys[0]][1]
    C = np.vstack([nodes[k][2] for k in keys]).T
    D = np.array([p[0] for p in prof])
    if D.max() >= z[-1]:   # implementation (9 Oct): trench deeper than the c levels; hold c as build_profiles' np.interp does
        z = np.append(z, D.max() + 100.0)
        C = np.vstack([C, C[-1:]])
    st = PATHS[name]
    rd = F.receiver_depth(st) if st else min(float(-b.elevation_m.iloc[-1]), D[-1]) - 2.0
    assert rd < D[-1], (name, rd, D[-1])
    return rprof, prof, nr, z, C, D, rd


def sph(r_m):
    x = r_m / 1000.0 / 6371.0
    return 10 * np.log10(x / np.sin(x))


def ram_band(e, fc, zs, fine=False):
    rprof, _, nr, z, C, D, rd = e
    L = rprof[-1] * 1e3
    fs = fc * 2 ** (np.linspace(-1, 1, NF) / 6)
    I = []
    for f in fs:
        lam = 1500.0 / f
        dr, dz = (lam, lam / 40) if fine else (2 * lam, lam / 20)
        m = PyRAM(f, zs, rd, z, nr * 1e3, C, np.array([0.0]), np.array([0.0]), np.array([[BOT["cp"]]]), np.array([[BOT["rho"]]]),
                  np.array([[BOT["ap"]]]), np.column_stack([rprof * 1e3, D]), rmax=L, zmplt=D.max(), dr=dr, dz=dz, ndr=1, ndz=1)
        r = m.run()
        rr, tl = r["Ranges"], r["TL Line"]
        k = rr >= rr[-1] - 500.0
        I.append(np.mean(10 ** (-tl[k] / 10)))
    return float(-10 * np.log10(np.mean(I)) + sph(L))


def kraken_band(e, fc, work, at_bin):
    rprof, prof, *_, rd = e
    tag = f"f{fc:g}".replace(".", "p")
    try:
        K.tl_path(work, tag, fc, prof, rprof, np.array([rprof[-1]]), SRC, [rd], BOT, at_bin, fg=None)
    except RuntimeError as e:   # the disclosed stage-B 'no_modes' case (9e18559): no trapped mode on a shelf profile
        if "no modes" not in str(e).lower():
            raise
        return {float(z): np.nan for z in SRC}
    s = K.read_shd(work / f"{tag}.shd")
    return {float(zs): float(-20 * np.log10(np.abs(np.ravel(s["p"][0, js, 0])[-1])) + sph(np.ravel(s["rr_m"])[-1])) for js, zs in enumerate(s["sz"])}


def delta_interp(d, fcs):
    """Linear in log f over the bands where the value is defined (a KRAKEN 'no_modes' band has none), clamped."""
    ok = [b for b in BANDS if np.isfinite(d[b])]
    return np.interp(np.log10(fcs), np.log10(ok), [d[b] for b in ok])


def main(stub, cal_dir, at_bin, out_dir, tl_csv, sa_json, summary):
    stub, cal_dir, out = Path(stub), Path(cal_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    f35 = cal_dir / "stubschema"
    envs = {n: env(f35 if n.startswith("f35a") else stub, n) for n in PATHS}
    # convergence, decided before running
    conv = {}
    if (out / "convergence.json").exists():          # implementation (9 Oct): reuse a completed convergence step
        conv = json.loads((out / "convergence.json").read_text())["cases"]
    for fc in (5.0, 40.0) if not conv else ():
        for zs in SRC:
            a, b = ram_band(envs["imp500_3376"], fc, zs), ram_band(envs["imp500_3376"], fc, zs, fine=True)
            conv[f"{fc:g}|{zs:g}"] = dict(primary=a, fine=b, diff=b - a)
    fine = any(abs(v["diff"]) > 1.0 for v in conv.values())
    (out / "convergence.json").write_text(json.dumps(dict(cases=conv, use_fine=fine), indent=1))
    rows = []
    for n, e in envs.items():
        t0 = time.time()
        part = out / f"part_{n}.csv"            # implementation (9 Oct): per-path cache so a restart repeats no finished path
        if part.exists():
            rows += pd.read_csv(part).to_dict("records")
            continue
        n0 = len(rows)
        for fc in BANDS:
            kt = kraken_band(e, fc, out / "work" / n, at_bin)
            for zs in SRC:
                rt = ram_band(e, fc, zs, fine)
                rows.append(dict(path=n, fc_hz=fc, src_depth_m=zs, rcv_depth_m=e[-1], range_km=float(e[0][-1]), tl_kraken_db=kt[zs],
                                 tl_ram_db=rt, delta_db=kt[zs] - rt))
        pd.DataFrame(rows[n0:]).to_csv(part, index=False)
        print(n, round(time.time() - t0, 1), "s", flush=True)
    cmp_ = pd.DataFrame(rows)
    cmp_.to_csv(out / "ram_vs_kraken.csv", index=False)
    ver = {}
    a9 = cmp_[cmp_.path == "air9_H01W"].delta_db.abs().median()
    ver["sanity_air9_median_abs_delta_db"] = float(a9)
    ver["sanity_pass"] = bool(a9 <= 3.0)
    r8 = cmp_[cmp_.path == "air8_H01W"].groupby("fc_hz").tl_ram_db.mean() - cmp_[cmp_.path == "air9_H01W"].groupby("fc_hz").tl_ram_db.mean()
    ver["air8_ram_excess_over_air9_db_by_band"] = {f"{k:g}": float(v) for k, v in r8.items()}
    ver["air8_ram_excess_mean_db"] = float(r8.mean())
    ver["air8_blockage"] = "SURVIVES" if r8.mean() >= 20 else "WEAKENED"
    if not ver["sanity_pass"]:
        ver["imos_verdict"] = "NOT ASSESSED (set-up sanity failed)"
        (out / "verdicts.json").write_text(json.dumps(ver, indent=1))
        print(json.dumps(ver, indent=1))
        return
    # corrected stage B TL table
    tl = pd.read_csv(tl_csv, dtype={"quantile": str, "logger": str})
    grp = {"3315": "imp500_3376", "3376": "imp500_3376", "3274": "imp500_3274", "3275": "imp500_3274"}
    dl = {}
    for p in set(grp.values()):
        g = cmp_[(cmp_.path == p) & (cmp_.src_depth_m == 10.0)].set_index("fc_hz")
        dl[p] = dict(delta={b: float(g.delta_db[b]) for b in BANDS}, ram={b: float(g.tl_ram_db[b]) for b in BANDS})
    tlc = tl.copy()
    for i, r in tl.iterrows():
        p = grp[r.logger]
        g = cmp_[(cmp_.path == p) & np.isclose(cmp_.src_depth_m, 30.0 if r.src_depth_m >= 30 else 10.0)].set_index("fc_hz").delta_db
        d = float(delta_interp(g.to_dict(), [r.fc_hz])[0])
        if np.isfinite(r.tl_db):
            tlc.at[i, "tl_db"] = r.tl_db - d
        else:   # 'no_modes' in KRAKEN: the RAM band value (interpolated), plus the FG loss KRAKEN would have added (none at <=6.3 Hz)
            gr = cmp_[(cmp_.path == p) & np.isclose(cmp_.src_depth_m, 30.0 if r.src_depth_m >= 30 else 10.0)].set_index("fc_hz").tl_ram_db
            tlc.at[i, "tl_db"] = float(delta_interp(gr.to_dict(), [r.fc_hz])[0])
            tlc.at[i, "status"] = "ram_fill"
    tlc.to_csv(out / "imos_tl_ramcorr.csv", index=False)
    # corrected H11 TL and calibration
    h = pd.read_csv(cal_dir / "f35a_tl.csv")
    hc = h.copy()
    for i, r in h.iterrows():
        g = cmp_[(cmp_.path == "f35a_H11S") & np.isclose(cmp_.src_depth_m, 30.0 if r.src_depth_m >= 30 else 10.0)].set_index("fc_hz").delta_db
        hc.at[i, "tl_db"] = r.tl_db - float(delta_interp(g.to_dict(), [r.fc_hz])[0])
    hc.to_csv(out / "h11_tl_ramcorr.csv", index=False)
    R = json.loads((cal_dir / "eta_cal_summary.json").read_text())["peak_ratio"]
    cal = F.calibrate(hc, R)
    cal.to_csv(out / "eta_cal_ramcorr.csv", index=False)
    sc = F.stage_c(out, cal, out / "imos_tl_ramcorr.csv", sa_json, summary)
    for fn in ("stageC_pd_summary.csv", "stageC_pd_by_latitude.csv"):
        (out / fn).rename(out / fn.replace("stageC_", "stageC_ramcorr_"))
    prim = float(sc[(sc.slope == 2) & (sc.curve == "or@0.005|T_C2")].pd_marginal.iloc[0])
    ver["stageC_ramcorr_pd_primary"] = prim
    ver["imos_verdict"] = "ROBUST TO THE TL MODEL" if prim < 0.1 else "OVERTURNED"
    ver["delta_db_imos_10m"] = {p: v["delta"] for p, v in dl.items()}
    (out / "verdicts.json").write_text(json.dumps(ver, indent=1))
    print(json.dumps(ver, indent=1))
    print(sc.to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:8])
