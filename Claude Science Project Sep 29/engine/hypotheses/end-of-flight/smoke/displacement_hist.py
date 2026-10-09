"""For Pleiades (relay, architecture.md ~06:45 UTC 9 Oct): 2-D weighted histograms of impact displacement from
each trajectory's OWN position at 00:19:37 (the last burst it flew through).

    python3 displacement_hist.py <terminal-out-dir> <out-dir> [--tag dive-on]

Delta-east and delta-north in NM on the local tangent plane at the 00:19:37 position (equirectangular,
1 NM = 1 arc-minute of latitude); 5 NM bins over [-110, 110] NM. Rows without a 00:19:37 position (the
takeover came after the burst, or the aircraft was down before it) are excluded, and their weight share is
reported. Per data option x log-on cause, pooled and by control axis. Each histogram is normalised to the
included weight; `included_share` gives the part of the option's posterior it represents, and
`outside_range_share` the part beyond 110 NM.
Outputs: displacement-<tag>.npz (arrays) and displacement-<tag>.json (metadata, shares, marginals).
"""
import argparse, json, pathlib
import numpy as np
from scipy.special import gammaln

EDGES = np.arange(-110.0, 110.0 + 1e-9, 5.0)
OPTIONS = ["none", "r600/inflated", "r600/no-offset", "r600/startup-offset", "r1200/inflated", "r1200/no-offset",
           "r1200/startup-offset", "both/inflated"]


def option_posteriors(run, seed_dir):
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
    for o in OPTIONS:
        if "loglik:" + o not in cols:
            continue
        base = g("loglik:" + o)
        for cause, extra in (("other", 0.0), ("fuel-exhaustion", lfe)):
            ll = np.where(np.isfinite(base), base, -np.inf) + extra
            p = w * np.exp(ll - ll[np.isfinite(ll)].max()); p = p / p.sum()
            yield f"{o.replace('/', '_')}__{cause}", p, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("out"); ap.add_argument("--tag", default="")
    a = ap.parse_args()
    run = pathlib.Path(a.run); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    fams = meta["terminal"]["module_families"]; controls = sorted({f.split("/")[2] for f in fams})
    fam_control = np.array([controls.index(f.split("/")[2]) for f in fams])
    seeds = sorted(p for p in (run / "bto-bfo").glob("seed-*") if (p / "impacts.npy").exists())
    arrays, info = {}, {"source": str(run), "seeds": [seeds[0].name], "children": meta["terminal"]["children"],
                         "bin_edges_nm": EDGES.tolist(), "controls": controls, "code_revision": meta.get("code_revision"),
                         "options": {}}
    for key, p, c in option_posteriors(run, seeds[0]):  # one seed per relay request (seed 1)
        dn, de, ctrl, has = c["dn"], c["de"], c["ctrl"], c["has"]
        rec = {"included_share": float(p[has].sum()), "ess": float(1.0 / np.sum(p ** 2))}
        inside = has & (np.abs(dn) <= 110) & (np.abs(de) <= 110)
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
