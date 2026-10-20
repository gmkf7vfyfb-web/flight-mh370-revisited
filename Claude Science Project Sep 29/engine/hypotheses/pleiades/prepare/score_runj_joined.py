"""Pléiades module on end of flight's run-j-joined-v2 (arm V2 joined at 00:11: planned descents with onset before 00:11 scored
in-stage from the 22:41 hand-off, onsets after 00:11 from the 00:11 hand-off; run J waypoints stratum). Per seed pair k:
the joined row weights are end of flight's joined_v2.py main() reproduced line by line from its own functions (load, Prior,
cells, family), unchanged; then the Pléiades factor by exact cell lookup (as score_runj.py), and optionally the per-impact columns
(build_columns.build_seed) under <exchange>/joined-v2/{J2241,J0011}/seed-k. The joined file has cells D0-D4 under the competing-
causes total q = 1/3 (C2 silent) only (end of flight's design; D5 is not in the joined estimate). Check: the joined ln Z without H
must reproduce end of flight's joined-s<k>.json.

    python score_runj_joined.py K WORKDIR [EXCHANGE_OUT]
"""
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
sys.path.append(str(HERE))
import score_runj as SR  # noqa: E402  (sets SATCOM_CSV for displacement_hist)
import joined_v2 as JV  # noqa: E402
JV.SATCOM_CSV = SR.DH.SATCOM_CSV
import build_columns as BC  # noqa: E402
import branch_eof289 as b  # noqa: E402

JR = SR.X / "end-of-flight/run-j-joined-v2"
HO = SR.CORE / "run-j-waypoints/bto-bfo"
FAMS = {"A1": (1,), "A2": (2,), "B": (3,), "code 6": (6,)}
SET = ("none (without H)", "gcrel-0.25", "g12-0.25")


def main(k, work, exch=None):
    t0 = time.time(); work = Path(work); work.mkdir(parents=True, exist_ok=True)
    outp = work / f"joined_{k}.npz"
    if outp.exists():
        return
    h2241 = HO / f"seed-{k}/handoff-m2241/handoff.toml.gz"; h0011 = HO / f"seed-{k}/handoff-m0011/handoff.toml.gz"
    # ---- joined_v2.main(), weights only (verbatim logic)
    T0, T1 = JV.stop_unix(h2241), JV.stop_unix(h0011); dlnz = JV.stop_lnz(h0011) - JV.stop_lnz(h2241)
    m1, g1, _ = JV.load(JR / "J2241", k); m2, g2, _ = JV.load(JR / "J0011", k)
    p1 = JV.Prior(m1["config"]["hypotheses"]["end-of-flight"]["onset"]); p2 = JV.Prior(m2["config"]["hypotheses"]["end-of-flight"]["onset"])
    assert p1.lead == p2.lead and p1.a == p2.a and p1.r == p2.r and p1.s == p2.s
    assert np.all(p2.w > 0)
    tk1 = g1("takeover_unix_s"); fo1 = g1("latent:realised_flameout_unix_s")
    mech1 = g1("latent:onset_mechanism")
    s1 = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & ~(np.isfinite(fo1) & (fo1 < JV.T_M0011_BURST))
    tau1 = g1("latent:onset_unix_s"); P1 = tau1 + g1("latent:predicted_endurance_at_onset_s")
    with np.errstate(invalid="ignore"):
        lr1 = np.where(s1, p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0), -np.inf)
    s1 = s1 & np.isfinite(lr1)
    lw1 = np.log(g1("weight")) + np.where(s1, lr1, 0.0); c1 = JV.cells(m1, g1, "m0011+")
    tau2 = g2("latent:onset_unix_s"); P2 = tau2 + g2("latent:predicted_endurance_at_onset_s"); mech2 = g2("latent:onset_mechanism")
    with np.errstate(invalid="ignore"):
        lr = p2.log_density(mech2, tau2, P2, T0) - p2.log_density(mech2, tau2, P2, T1)
    s2 = np.isfinite(lr) & (P2 >= T1)
    lw2 = np.log(g2("weight")) + np.where(s2, lr, -np.inf); c2 = JV.cells(m2, g2, "")
    fam = np.r_[JV.family(g1), JV.family(g2)]
    lat = np.r_[g1("latitude_deg"), g2("latitude_deg")]; lon = np.r_[g1("longitude_deg"), g2("longitude_deg")]
    arcd = np.r_[g1("arc_distance_nm"), g2("arc_distance_nm")]
    n1 = len(lw1)
    # ---- columns (optional)
    sums = []
    if exch:
        mp, models, P, Cm = b.load_fields(SR.SURF)
        for st, g in (("J2241", g1), ("J0011", g2)):
            sd = JR / st / f"seed-{k}"
            stat, line = BC.build_seed(sd, st, Path(exch) / "joined-v2", (mp, P, Cm), g=g); sums.append([stat, line])
        del P, Cm
    # ---- Pléiades factor
    L, (lat0, lon0, step) = SR.surfaces()
    i = np.floor((lat - (lat0 - step / 2)) / step).astype(np.int64); j = np.floor((lon - (lon0 - step / 2)) / step).astype(np.int64)
    inside = (i >= 0) & (i < SR.NLAT) & (j >= 0) & (j < SR.NLON); cell = np.where(inside, i * SR.NLON + j, 0)
    LH = {"none (without H)": np.zeros(len(lat)), "gcrel-0.25": np.where(inside, L["gcrel-0.25"][cell], -np.inf),
          "g12-0.25": np.where(inside, L["g12-0.25"][cell], -np.inf)}
    fk = {nm: np.isin(fam, c) for nm, c in FAMS.items()}
    in30, in50 = arcd <= -30, arcd <= -50
    res = dict(k=k, T0=T0, T1=T1, dlnZ_filter=dlnz, s1_rows=int(s1.sum()), s2_rows=int(s2.sum()), rows=len(lat),
               outside_grid_rows=int((~inside).sum()), columns=sums, cells={})
    H = {}
    for d in c1:
        a0 = np.r_[np.where(s1, lw1 + c1[d], -np.inf), lw2 + dlnz + c2[d]]
        res["cells"][d] = {}
        fin0 = np.isfinite(a0); s0 = float(a0[fin0].max()); m0 = np.where(fin0, np.exp(a0 - s0), 0.0)
        for kk, lh in LH.items():
            with np.errstate(invalid="ignore"):
                a = a0 + lh
            fin = np.isfinite(a); s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0); S = m.sum()
            res["cells"][d][kk] = dict(lnZ=float(math.log(S) + s), ess=float(S * S / (m * m).sum()), S1_share=float(m[:n1].sum() / S),
                                       mean_lat=float((m * lat).sum() / S), mean_lon=float((m * lon).sum() / S),
                                       in30=float(m[in30].sum() / S), in50=float(m[in50].sum() / S),
                                       fam={nm: dict(share=float(m[x].sum() / S), ess=float(m[x].sum() ** 2 / max((m[x] ** 2).sum(), 1e-300)),
                                                     pre0011_share=float(m[:n1][x[:n1]].sum() / S)) for nm, x in fk.items()},
                                       not_computed_core_share=float(m0[~np.isfinite(lh)].sum() / m0.sum()))
        H[f"{d}|s"] = s0
        H[f"{d}|map"] = np.bincount(cell[inside & fin0], weights=m0[inside & fin0], minlength=SR.NCELL).astype(np.float32)
        for nm in ("B",):
            sel = inside & fin0 & fk[nm]
            H[f"{d}|map_{nm}"] = np.bincount(cell[sel], weights=m0[sel], minlength=SR.NCELL).astype(np.float32)
    ref = json.loads((JR / "summary" / f"joined-s{k}.json").read_text()) if (JR / "summary" / f"joined-s{k}.json").exists() else None
    res["check_lnZ_vs_eof"] = {d: res["cells"][d]["none (without H)"]["lnZ"] - ref["cells"][d]["lnZ"] for d in c1} if ref else None
    res["wall_s"] = time.time() - t0
    tmp = work / f"joined_{k}.partial.npz"
    np.savez_compressed(tmp, res=json.dumps(res), **H); os.replace(tmp, outp)
    print(f"joined seed {k}: {res['wall_s']:.0f} s; check {res['check_lnZ_vs_eof']}", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
