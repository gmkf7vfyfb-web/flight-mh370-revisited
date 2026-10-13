"""Pléiades module on core run I (end of flight's run-i): the module's per-impact columns joined to end of flight's OWN 00:19
two-factor weights (smoke/option_table_0019.py, reused unchanged: D0-D5 data treatment x log-on cause C1 / C2 silent, and the
competing-causes total q = 1/3 (C2 silent), survival factor throughout; strata by core P x their own evidence, seeds pooled by
evidence). Conditional on H; no identity likelihood; no Bayes factor or P(H). Settings under H (exact cell lookup, reader.py):
  gcrel-0.25  load_rho(rho 0.25, "mean", "-gcrel")   proposed headline (both models, GlobCurrent product-relative)
  g12-0.25    load_rho(rho 0.25, 0)                  GLORYS12 only (headline in force, ruling 2)
Optional searched-areas root (per-impact ln P(no find), <prefix>-<stratum>/seed-k/seabed-lnL.npy) adds the search.
Tension: the module's measure (rerun_reference.tension) on the wide 0.05 deg grid.

    python score_runi_summary.py <eof run-i> <core run-i> <pleiades run-i> <out json> stratum=P [...] [--search <root>]
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
sys.path.append(str(HERE))
import option_table_0019 as ot  # noqa: E402
from compact_impacts import load, family_labels  # noqa: E402
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV  # noqa: E402
from scipy.special import gammaln  # noqa: E402

SETTINGS = ("none (without H)", "gcrel-0.25", "g12-0.25")
CAUSES = ("C1", "C2 silent", "total q=1/3 (C2 silent)")
NLAT, NLON = 800, 740; NCELL = NLAT * NLON


def reader(pl_root):
    spec = importlib.util.spec_from_file_location("pl_reader", Path(pl_root) / "reader.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def cell_logw(sd, handoff):
    """end of flight's per-row log weights for the cells used here (copied term by term from option_table_0019.seed_terms)."""
    import csv
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": ot.d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    C2 = -np.log(ot.W_S) + constraint_log_factor(g, logon, "other", "silent")
    p = 1 / (1 + 1 / 3)
    C = {"C1": C1, "C2 silent": C2, "total q=1/3 (C2 silent)": np.logaddexp(np.log(p) + C1, np.log(1 - p) + C2)}
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    cells = {f"{d} x {c}": lw + surv + ld + lc for d, ld in D.items() for c, lc in C.items()}
    return cells, f4, g("latitude_deg"), g("longitude_deg")


def main(eof_root, core_root, pl_root, outp, strata, sa_root=None):
    eof_root, core_root, pl_root = Path(eof_root), Path(core_root), Path(pl_root)
    R = reader(pl_root); acc = {}; H = {}   # H: streaming (log scale, sum) of flight-only cell mass per D x C cell
    for st, P in strata.items():
        seeds = sorted(p for p in (eof_root / st).glob("seed-*") if p.is_dir()); K = len(seeds)
        for sd in seeds:
            cells, f4, lat, lon = cell_logw(sd, core_root / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
            plsd = pl_root / st / sd.name
            colm = np.load(plsd / "pleiades-lnL.npy", mmap_mode="r"); assert len(colm) == len(f4)
            cell = np.asarray(colm["cell"]); inside = cell != 0xFFFFFFFF
            LH = {"none (without H)": np.zeros(len(f4)), "gcrel-0.25": R.load_rho(plsd, 0.25, "mean", "-gcrel"), "g12-0.25": R.load_rho(plsd, 0.25, 0)}
            LH = {k: np.where(np.isfinite(v), v, -np.inf) for k, v in LH.items()}
            lsea = 0.0
            if sa_root:
                hit = [d for d in Path(sa_root).iterdir() if d.is_dir() and d.name.endswith("-" + st) or d.name == st]
                assert len(hit) == 1, (st, hit)
                lsea = np.asarray(np.load(hit[0] / sd.name / "seabed-lnL.npy", mmap_mode="r"), float); assert len(lsea) == len(f4)
            c = math.log(P / K)
            for ck, a0 in cells.items():
                for stg in SETTINGS:
                    with np.errstate(invalid="ignore"):
                        a = a0 + LH[stg] + lsea
                    fin = np.isfinite(a)
                    if not fin.any():
                        continue
                    s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
                    t = dict(s=c + s, S=m.sum(), S2=(m * m).sum(), lat=(m * lat).sum(), lon=(m * lon).sum(),
                             fam={n: [(m * (f4 == cc)).sum(), ((m * (f4 == cc)) ** 2).sum()] for cc, n in ot.FAMS})
                    if stg == SETTINGS[0]:
                        h = np.bincount(cell[inside].astype(np.int64), weights=m[inside], minlength=NCELL)
                        if ck not in H:
                            H[ck] = [c + s, h]
                        elif c + s > H[ck][0]:
                            H[ck] = [c + s, H[ck][1] * math.exp(H[ck][0] - c - s) + h]
                        else:
                            H[ck][1] += h * math.exp(c + s - H[ck][0])
                    acc.setdefault((ck, stg), []).append(t)
            print(st, sd.name, flush=True)
    import branch_eof289 as b
    from rerun_reference import tension
    from headline_splithalf import rho_L
    surf = pl_root / "surfaces"
    mp = {}
    for line in (surf / "likelihood-surface.toml").read_text().splitlines():
        k, v = line.split(" = ", 1); mp[k] = v
    glat = float(mp["lat0"]) + b.STEP * np.arange(NLAT); glon = float(mp["lon0"]) + b.STEP * np.arange(NLON)
    area = b.area_km2(np.meshgrid(glat, glon, indexing="ij")[0]); z = np.zeros_like(area, dtype=bool)
    Lg = {"gcrel-0.25": rho_L(surf, 0.25, "mean", "-gcrel"), "g12-0.25": rho_L(surf, 0.25, 0, "")}
    res = {"strata_P": strata, "settings": list(SETTINGS), "search": f"after {sa_root}" if sa_root else "before seabed search", "cells": {}}
    for (ck, stg), L in acc.items():
        M = max(t["s"] for t in L); f = [math.exp(t["s"] - M) for t in L]
        S = sum(fi * t["S"] for fi, t in zip(f, L)); S2 = sum(fi * fi * t["S2"] for fi, t in zip(f, L))
        r = dict(ln_Z=float(M + math.log(S)), eff_impacts=float(S * S / S2),
                 mean_lat=float(sum(fi * t["lat"] for fi, t in zip(f, L)) / S), mean_lon=float(sum(fi * t["lon"] for fi, t in zip(f, L)) / S))
        r["families"] = {}
        for _, n in ot.FAMS:
            a1 = sum(fi * t["fam"][n][0] for fi, t in zip(f, L)); a2 = sum(fi * fi * t["fam"][n][1] for fi, t in zip(f, L))
            r["families"][n] = dict(share=float(a1 / S), eff_impacts=float(a1 * a1 / a2) if a2 > 0 else 0.0)
        if stg == SETTINGS[0]:
            pc = H[ck][1].reshape(NLAT, NLON); pc = pc / pc.sum()
            for k, Lk in Lg.items():
                tt = tension(pc, Lk, area, glat, glon, z, z, z)
                res["cells"].setdefault(ck, {}).setdefault(k, {})["tension"] = {kk: float(tt[kk]) for kk in
                    ("ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90", "cond_hdr90_km2", "uncond_hdr90_km2")}
        res["cells"].setdefault(ck, {}).setdefault(stg, {}).update(r)
    for ck, e in res["cells"].items():
        z0 = e[SETTINGS[0]]
        for stg in SETTINGS[1:]:
            if stg in e and "ln_Z" in e[stg]:
                e[stg]["ln_mean_LH"] = e[stg]["ln_Z"] - z0["ln_Z"]
    Path(outp).write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    args = sys.argv[1:]; sa = None
    if "--search" in args:
        i = args.index("--search"); sa = args[i + 1]; args = args[:i] + args[i + 2:]
    strata = {k: float(v) for k, v in (x.split("=") for x in args[4:])}
    res = main(*args[:4], strata, sa)
    ref = {stg: res["cells"]["D0 x total q=1/3 (C2 silent)"][stg]["ln_mean_LH"] for stg in SETTINGS[1:]}
    for ck, e in res["cells"].items():
        for stg in SETTINGS[1:]:
            r = e[stg]; t = r.get("tension", {})
            print(f"{ck:28s} {stg:11s} ESS {r['eff_impacts']:10.0f} ({e[SETTINGS[0]]['eff_impacts']:10.0f}) mean {r['mean_lat']:.2f} {r['mean_lon']:.2f} "
                  f"lnE[L_H]-D0 {r['ln_mean_LH'] - ref[stg]:+.2f} lnS {t.get('ln_S', float('nan')):+.2f} p {t.get('tension_p', float('nan')):.2f} "
                  f"shift {t.get('mean_shift_nm', float('nan')):.0f} A1 {r['families']['A1']['eff_impacts']:.0f}")
