"""For Pleiades (relay, architecture.md ~06:45 UTC 9 Oct): 2-D weighted histograms of impact displacement from
each trajectory's OWN position at 00:19:37 (the last burst it flew through).

    python3 displacement_hist.py <terminal-out-dir> <out-dir> [--tag dive-on]

Delta-east and delta-north in NM on the local tangent plane at the 00:19:37 position (equirectangular,
1 NM = 1 arc-minute of latitude); 5 NM bins over [-extent, extent] NM (default 110). Rows without a 00:19:37 position (the
takeover came after the burst, or the aircraft was down before it) are excluded, and their weight share is
reported. Per data option x log-on cause, pooled and by control axis. Each histogram is normalised to the
included weight; `included_share` gives the part of the option's posterior it represents, and
`outside_range_share` the part beyond 110 NM.
Outputs: displacement-<tag>.npz (arrays) and displacement-<tag>.json (metadata, shares, marginals).
"""
import argparse, json, pathlib
import numpy as np
from scipy.special import gammaln

EDGES = np.arange(-110.0, 110.0 + 1e-9, 5.0)  # default; --extent overrides
OPTIONS = ["none", "r600/inflated", "r600/no-offset", "r600/startup-offset", "r1200/inflated", "r1200/no-offset",
           "r1200/startup-offset", "both/inflated", "both/no-offset", "both/startup-offset"]


SATCOM_CSV = pathlib.Path(__file__).resolve().parents[3] / "data" / "satcom-observations.csv"
# BTO-only options declared in config/integrated.toml but not carried by every run (architecture fix 3, ~19:30
# UTC 9 Oct). Derived here, once, from the run's own `bto_residual_us:<epoch>` columns and the observation sd in
# data/satcom-observations.csv, with the core's gaussian_log_likelihood (crates/satcom/src/lib.rs:271). Checked
# 9 Oct: loglik:r600/no-offset decomposes exactly into this BTO term (sd 63 us) plus a BFO term (max residual
# 7e-10). A descent already down at the epoch has no residual and scores -inf, as in the core.
DERIVED_BTO = {"r600-bto": ["m0019a"], "both-bto": ["m0019a", "m0019b"]}


def derived_logliks(meta, g, present):
    import csv
    sd = {r["epoch_id"]: float(r["bto_sd_us"]) for r in csv.DictReader(open(SATCOM_CSV)) if r["epoch_id"] in ("m0019a", "m0019b")}
    out = {}
    for o, epochs in DERIVED_BTO.items():
        if o in present or not all(f"bto_residual_us:{e}" in meta["impact_columns"] for e in epochs):
            continue
        ll = 0.0
        for e in epochs:
            r = g(f"bto_residual_us:{e}")
            ll = ll + np.where(np.isfinite(r), -0.5 * ((r / sd[e]) ** 2 + np.log(2 * np.pi * sd[e] ** 2)), -np.inf)
        out[o] = ll
    return out


T_M0019B = 1394237977.443   # 00:19:37.443, the R1200 acknowledge: the last burst the aircraft transmitted
T_LOI_0115 = 1394241356.0   # 01:15:56, ground-station handshake with no response (Davey et al. 2015 draft, p. 6)


def constraint_log_factor(g, logon, cause, which):
    """Existence constraints on the 00:19 log-on sequence and the silence after it (architecture ~03:20 UTC 10 Oct).
    PROVISIONAL-OVERNIGHT, declared and default-off: the plain option x cause arms are unchanged.
      alive:  airborne at 00:19:37.443 (the burst exists, whatever its values are used for).
      silent: alive; not powered at 01:15:56 (the handshake went unanswered); and under `other`, no APU log-on after a
              later flame-out before impact, probability S(impact - flame-out) under the same Erlang lag. Under
              fuel-exhaustion the single flame-out IS the 00:19:29 log-on's, so it predicts no further log-on.
    Single fuel pool; with two tanks the APU log-on belongs to the second flame-out."""
    from scipy.special import gammaincc
    t = g("unix_s"); fo = g("latent:realised_flameout_unix_s")
    out = np.where(t > T_M0019B, 0.0, -np.inf)
    if which == "silent":
        powered_0115 = (t > T_LOI_0115) & (~np.isfinite(fo) | (fo > T_LOI_0115))
        out = np.where(powered_0115, -np.inf, out)
        if cause == "other":
            with np.errstate(divide="ignore", invalid="ignore"):
                surv = gammaincc(logon["lag_shape"], np.maximum(t - fo, 0.0) / logon["lag_scale_s"])
                out = out + np.where(np.isfinite(fo), np.log(surv), 0.0)
    return out


def option_posteriors(run, seed_dir, constraints=()):
    """Yield (key, normalised posterior weights, columns) per data option x log-on cause for one seed.
    Weight = hand-off weight x burst likelihood (x the section 6 log-on lag density for fuel-exhaustion)."""
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    fams = meta["terminal"]["module_families"]; controls = sorted({f.split("/")[2] for f in fams})
    fam_control = np.array([controls.index(f.split("/")[2]) for f in fams])
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    X = np.load(seed_dir / "impacts.npy", mmap_mode="r")
    g = lambda k: np.asarray(X[:, cols[k]], float)
    w = g("weight"); lat, lon = g("latitude_deg"), g("longitude_deg")
    bl, bo = g("latent:last_burst_latitude_deg"), g("latent:last_burst_longitude_deg")
    c = {"lat": lat, "lon": lon, "dn": (lat - bl) * 60.0, "de": (lon - bo) * 60.0 * np.cos(np.radians(bl)),
         "ctrl": fam_control[g("family").astype(int)], "controls": controls,
         "spiral_divergent": g("latent:spiral_divergent") if "latent:spiral_divergent" in cols else np.zeros_like(w)}
    c["has"] = np.isfinite(c["dn"]) & np.isfinite(c["de"])
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    # Every option the run carries, read from its own columns (OPTIONS fixes only the order of the known ones),
    # so that no loglik column can be silently dropped. Fixed 9 Oct after Searched Areas found both/no-offset and
    # both/startup-offset missing.
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    derived = derived_logliks(meta, g, present)
    for o in [o for o in OPTIONS if o in present] + [o for o in present if o not in OPTIONS] + list(derived):
        base = derived[o] if o in derived else g("loglik:" + o)
        for cause, extra in (("other", 0.0), ("fuel-exhaustion", lfe)):
            for con in ("",) + tuple(constraints):
                ll = np.where(np.isfinite(base), base, -np.inf) + extra
                if con:
                    ll = ll + constraint_log_factor(g, logon, cause, con)
                if not np.isfinite(ll).any():
                    continue
                p = w * np.exp(ll - ll[np.isfinite(ll)].max()); p = p / p.sum()
                yield f"{o.replace('/', '_')}__{cause}" + (f"+{con}" if con else ""), p, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("out"); ap.add_argument("--tag", default=""); ap.add_argument("--extent", type=float, default=110.0); ap.add_argument("--runs", nargs="*", default=[], help="extra terminal dirs to pool (equal weight per seed)")
    a = ap.parse_args()
    global EDGES
    EDGES = np.arange(-a.extent, a.extent + 1e-9, 5.0)
    run = pathlib.Path(a.run); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    fams = meta["terminal"]["module_families"]; controls = sorted({f.split("/")[2] for f in fams})
    fam_control = np.array([controls.index(f.split("/")[2]) for f in fams])
    seeds = sorted(p for p in (run / "bto-bfo").glob("seed-*") if (p / "impacts.npy").exists())
    arrays, info = {}, {"source": str(run), "children": meta["terminal"]["children"],
                         "bin_edges_nm": EDGES.tolist(), "controls": controls, "code_revision": meta.get("code_revision"),
                         "options": {}}
    sources = [(run, seeds[0])] + [(pathlib.Path(d), s) for d in a.runs for s in sorted(pathlib.Path(d, "bto-bfo").glob("seed-*"))
                                   if (s / "impacts.npy").exists()]
    info["seeds"] = [f"{r.name}/{s.name}" for r, s in sources]
    gens = [option_posteriors(r, s) for r, s in sources]
    for parts in zip(*gens):  # same option order in every seed
        key = parts[0][0]
        assert all(q[0] == key for q in parts)
        n = len(parts)
        p = np.concatenate([q[1] for q in parts]) / n
        c = {f: np.concatenate([q[2][f] for q in parts]) for f in ("dn", "de", "ctrl", "has")}
        dn, de, ctrl, has = c["dn"], c["de"], c["ctrl"], c["has"]
        rec = {"included_share": float(p[has].sum()), "ess": float(sum(1.0 / np.sum(q[1] ** 2) for q in parts))}
        inside = has & (np.abs(dn) <= a.extent) & (np.abs(de) <= a.extent)
        rec["outside_range_share"] = float(p[has & ~inside].sum() / max(p[has].sum(), 1e-300))
        for name, sel in [("pooled", has)] + [(cn, has & (ctrl == k)) for k, cn in enumerate(controls)]:
            H, _, _ = np.histogram2d(dn[sel], de[sel], bins=[EDGES, EDGES], weights=p[sel])
            tot = p[sel].sum()
            arrays[f"{key}__{name}"] = H / tot if tot > 0 else H
            rec[f"{name}_weight_share"] = float(tot)
            if tot > 0:
                r = np.hypot(dn[sel], de[sel]); o_ = np.argsort(r); cc = np.cumsum(p[sel][o_]) / tot
                rec[f"{name}_radius_nm_50_90_99"] = [float(np.interp(q, cc, r[o_])) for q in (0.5, 0.9, 0.99)]
        info["options"][key] = rec
    tag = f"-{a.tag}" if a.tag else ""
    np.savez_compressed(out / f"displacement{tag}.npz", **arrays)
    (out / f"displacement{tag}.json").write_text(json.dumps(info, indent=1))
    print("wrote", out / f"displacement{tag}.npz", len(arrays), "histograms")


if __name__ == "__main__":
    main()
