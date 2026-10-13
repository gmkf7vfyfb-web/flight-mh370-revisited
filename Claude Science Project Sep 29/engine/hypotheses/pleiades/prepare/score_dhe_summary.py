"""Pléiades module on end of flight's run D-he (H1/H2 sweep): the module's per-impact columns joined to end of flight's own per-option
weights, for every standard 00:19 option INCLUDING Holland H1 and H2. Conditional on H; no identity likelihood; no Bayes factor or P(H).

Option weights are end of flight's, reused unchanged (smoke/holland_sweep_summary.seed_terms recipe: derived_logliks + log-on lag
term for the fuel-exhaustion cause + constraint 'unpowered'; PRIMARY = x (1 - latent:inflight_p_breakup_to_m0019b), the adopted survival
factor; SENSITIVITY = without it). Row mass = P_s / K_s x w_i L_i / sum_k w (strata by core P x their own evidence, as end of flight).
Under H each row is multiplied by L_H from pleiades/next-run-d-he (exact cell lookup):
  as-run      lnL_both_mean (rho 0, both models, GlobCurrent as run)
  gcrel-0.25  reader.load_rho(rho 0.25, "mean", "-gcrel")   (proposed headline)
  g12-0.25    reader.load_rho(rho 0.25, 0)                  (GLORYS12 only, headline in force)
Before seabed search (searched areas' run D-he columns are not yet published); reported as such.

    python score_dhe_summary.py <eof next-run-d-he> <pleiades next-run-d-he> <out json> [<searched-areas next-run-d-he>]
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

HERE = Path(__file__).resolve().parent
EOF_SMOKE = HERE.parents[1] / "end-of-flight" / "smoke"
sys.path.insert(0, str(EOF_SMOKE))
sys.path.append(str(HERE))
from compact_impacts import load, family_labels  # noqa: E402
from displacement_hist import derived_logliks, constraint_log_factor  # noqa: E402
from smoke_compare import CORE  # noqa: E402
from scipy.special import gammaln  # noqa: E402

NM = 1.852
FAMS = ((1, "A1"), (2, "A2"), (3, "B"))
SETTINGS = ("none (without H)", "as-run", "gcrel-0.25", "g12-0.25")
NLAT, NLON = 800, 740; NCELL = NLAT * NLON


def reader(pl_root):
    spec = importlib.util.spec_from_file_location("pl_reader", Path(pl_root) / "reader.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def seed_rows(sd, plsd, R, sasd=None):
    meta, g = load(sd)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    pb19 = np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1)
    lat, lon = g("latitude_deg"), g("longitude_deg")
    col = np.load(Path(plsd) / "pleiades-lnL.npy", mmap_mode="r")
    cell = np.asarray(col["cell"]); inside = cell != 0xFFFFFFFF
    assert len(col) == len(w), (sd, len(col), len(w))
    LH = {"none (without H)": np.zeros(len(w)), "as-run": np.asarray(col["lnL_both_mean"], float),
          "gcrel-0.25": R.load_rho(plsd, 0.25, "mean", "-gcrel"), "g12-0.25": R.load_rho(plsd, 0.25, 0)}
    LH = {k: np.where(np.isfinite(v), v, -np.inf) for k, v in LH.items()}
    lsea = 0.0
    if sasd is not None:   # searched areas' own per-impact ln P(no find | impact), row-aligned (Phase 2 + Bluefin-21)
        lsea = np.load(Path(sasd) / "seabed-lnL.npy", mmap_mode="r"); assert len(lsea) == len(w); lsea = np.asarray(lsea, float)
    out = {}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll0 = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
        for ver, extra in (("primary", np.log1p(-pb19)), ("without survival factor", 0.0)):
            for st in SETTINGS:
                with np.errstate(divide="ignore"):
                    a = lw + ll0 + extra + LH[st] + lsea
                s = float(a[np.isfinite(a)].max()); m = np.exp(a - s); m[~np.isfinite(a)] = 0.0
                t = dict(s=s, S=m.sum(), S2=(m * m).sum(), lat=(m * lat).sum(), lon=(m * lon).sum(),
                         fam={n: [(m * (f4 == c)).sum(), ((m * (f4 == c)) ** 2).sum()] for c, n in FAMS})
                if st == SETTINGS[0]:   # flight-only mass per wide-grid cell, for the tension (before search)
                    t["hist"] = np.bincount(cell[inside].astype(np.int64), weights=m[inside], minlength=NCELL)
                out[(name, ver, st)] = t
    return out


def main(eof_root, pl_root, outp, sa_root=None):
    eof_root, pl_root = Path(eof_root), Path(pl_root)
    R = reader(pl_root)
    sj = eof_root / "summary/holland-sweep-summary.json"
    if sj.exists():
        strata = json.loads(sj.read_text())["strata_weights"]
    else:   # single-stratum runs (run H: next-h-routes only): weight 1 each, declared in the output
        names = sorted(d.name for d in eof_root.iterdir() if d.is_dir() and (d / "READY").exists())
        strata = {n: 1.0 / len(names) for n in names}
    acc = {}
    for st, P in strata.items():
        seeds = sorted(p for p in (eof_root / st).glob("seed-*") if p.is_dir()); K = len(seeds)
        for sd in seeds:
            c = math.log(P / K)
            sasd = None
            if sa_root:   # searched areas name their stratum dirs <run prefix>-<stratum> (d-he-, h-)
                hit = [d for d in Path(sa_root).iterdir() if d.is_dir() and d.name.endswith("-" + st)]
                assert len(hit) == 1, (st, hit)
                sasd = hit[0] / sd.name
            for key, t in seed_rows(sd, pl_root / st / sd.name, R, sasd).items():
                acc.setdefault(key, []).append((c, t))
            print(st, sd.name, flush=True)
    res = {"strata_weights_core": strata, "settings": list(SETTINGS), "search": ("after Phase 2 + Bluefin-21 (searched areas next-run-d-he, rho 0.05, official only)" if sa_root else "before seabed search"), "options": {}}
    for (name, ver, stg), L in acc.items():
        ls = [c + t["s"] for c, t in L]; M = max(ls); f = [math.exp(x - M) for x in ls]
        S = sum(fi * t["S"] for fi, (c, t) in zip(f, L))
        S2 = sum((math.exp(2 * (c + t["s"] - M))) * t["S2"] for c, t in L)
        r = dict(ln_Z=float(M + math.log(S)), eff_impacts=float(S * S / S2),
                 mean_lat=float(sum(fi * t["lat"] for fi, (c, t) in zip(f, L)) / S), mean_lon=float(sum(fi * t["lon"] for fi, (c, t) in zip(f, L)) / S))
        fam = {}
        for _, n in FAMS:
            a1 = sum(fi * t["fam"][n][0] for fi, (c, t) in zip(f, L)); a2 = sum(math.exp(2 * (c + t["s"] - M)) * t["fam"][n][1] for c, t in L)
            fam[n] = dict(share=float(a1 / S), eff_impacts=float(a1 * a1 / a2) if a2 > 0 else 0.0)
        r["families"] = fam
        res["options"].setdefault(name, {}).setdefault(ver, {})[stg] = r
    # tension of H against the flight PDF of each option (the module's measure, rerun_reference.tension), wide grid, before search
    import branch_eof289 as b
    from rerun_reference import tension
    from headline_splithalf import rho_L
    surf = Path(pl_root) / "surfaces"
    mp, models, P, Cm = b.load_fields(surf)
    assert (int(mp["nlat"]), int(mp["nlon"])) == (NLAT, NLON)
    glat = mp["lat0"] + b.STEP * np.arange(NLAT); glon = mp["lon0"] + b.STEP * np.arange(NLON)
    area = b.area_km2(np.meshgrid(glat, glon, indexing="ij")[0]); z = np.zeros_like(area, dtype=bool)
    Lg = {"as-run": np.nan_to_num(b.build_branch(models, P, Cm)["P+C4"]["both models"]),
          "gcrel-0.25": rho_L(surf, 0.25, "mean", "-gcrel"), "g12-0.25": rho_L(surf, 0.25, 0, "")}
    for (name, ver, stg), L in acc.items():
        if stg != SETTINGS[0]:
            continue
        ls = [c + t["s"] for c, t in L]; M = max(ls)
        pc = sum(math.exp(x - M) * t["hist"] for x, (c, t) in zip(ls, L)).reshape(NLAT, NLON)
        pc = pc / pc.sum()
        for k, Lk in Lg.items():
            tt = tension(pc, Lk, area, glat, glon, z, z, z)
            res["options"][name][ver][k].update({kk: float(tt[kk]) for kk in ("ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90", "cond_hdr90_km2", "uncond_hdr90_km2")})
    for name, d in res["options"].items():
        for ver, e in d.items():
            z0 = e["none (without H)"]
            for stg, r in e.items():
                r["ln_mean_LH_under_option"] = r["ln_Z"] - z0["ln_Z"]
                dy = (r["mean_lat"] - z0["mean_lat"]) * 60.0; dx = (r["mean_lon"] - z0["mean_lon"]) * 60.0 * math.cos(math.radians(z0["mean_lat"]))
                r["mean_shift_nm_from_without_H"] = float(math.hypot(dx, dy))
    Path(outp).write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    res = main(*sys.argv[1:5])
    for name, d in res["options"].items():
        for stg, r in d["primary"].items():
            print(f"{name:26s} {stg:17s} lnZ {r['ln_Z']:9.3f} lnE[L_H] {r['ln_mean_LH_under_option']:7.3f} ESS {r['eff_impacts']:12.0f} "
                  f"mean {r['mean_lat']:.2f} {r['mean_lon']:.2f} shift {r['mean_shift_nm_from_without_H']:5.0f} NM  "
                  + " ".join(f"{n} {v['share']:.2f}/{v['eff_impacts']:.0f}" for n, v in r["families"].items())
                  + (f"  lnS {r['ln_S']:+.2f} p {r['tension_p']:.2f} shiftT {r['mean_shift_nm']:.0f} uncin90 {r['uncond_in_cond_hdr90']:.2f}" if "ln_S" in r else ""))
