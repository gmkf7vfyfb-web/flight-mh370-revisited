"""Deliverable 3 (brief section 7): one sensitivity page per data option x BFO model, each with a row per family
and a pooled row.

    python3 sensitivity_page.py <terminal-out-dir> <out-dir> [--logon other|fuel-exhaustion] [--seeds 1,2,...]

Per row: weight share; effective sample size over rows and over parents, with the population beside it;
impact area of the 50/90/99 % highest-density regions (km^2, 0.05 deg cells, area-weighted); distance from
the takeover position (equal to the flame-out position for the flame-out mechanism; the flame-out position
itself is not an impact column), and from the 7th arc (`arc_distance_nm`); impact time after 00:19:37;
total and vertical kinetic energy at contact. Quantiles are 5/50/95 %, weighted. Seeds are pooled with
equal weight. Families are the module's declared families; equal Monte Carlo allocation across them is a
computational choice, and the family prior is carried in the weights.
"""
import argparse, json, pathlib
import numpy as np
from scipy.special import gammaln

T0019B = 1394237977.443
R_EARTH_KM = 6371.0088


def wq(v, w, q):
    ok = np.isfinite(v) & (w > 0)
    if not ok.any():
        return [float("nan")] * len(q)
    v, w = v[ok], w[ok]; o = np.argsort(v); v, w = v[o], w[o]; c = np.cumsum(w) / w.sum()
    return [float(np.interp(x, c, v)) for x in q]


def hpd_areas(lat, lon, w, levels=(0.5, 0.9, 0.99), cell=0.05):
    ok = np.isfinite(lat) & np.isfinite(lon) & (w > 0)
    if ok.sum() < 2:
        return [float("nan")] * len(levels)
    la, lo, w = lat[ok], lon[ok], w[ok]
    i = np.floor(la / cell).astype(np.int64); j = np.floor(lo / cell).astype(np.int64)
    key = i * 100000 + j
    u, inv = np.unique(key, return_inverse=True)
    mass = np.bincount(inv, weights=w); mass /= mass.sum()
    ci = u // 100000; lat_c = (ci + 0.5) * cell
    area = (np.radians(cell) * R_EARTH_KM) ** 2 * np.cos(np.radians(lat_c))
    o = np.argsort(-mass / area); cm = np.cumsum(mass[o]); ca = np.cumsum(area[o])
    return [float(ca[min(np.searchsorted(cm, L), len(ca) - 1)]) for L in levels]


def haversine_nm(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1))) / 1.852


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("out")
    ap.add_argument("--logon", default="other", choices=["other", "fuel-exhaustion"])
    ap.add_argument("--seeds", default="")
    a = ap.parse_args()
    run = pathlib.Path(a.run); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((run / "run.json").read_text())
    cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    fams = meta["terminal"]["module_families"]
    opts = [c for c in meta["impact_columns"] if c.startswith("loglik:")]
    seeds = sorted(p for p in (run / "bto-bfo").glob("seed-*") if (p / "impacts.npy").exists())
    if a.seeds:
        keep = {f"seed-{s}" for s in a.seeds.split(",")}; seeds = [p for p in seeds if p.name in keep]
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    need = ["weight", "parent", "family", "latitude_deg", "longitude_deg", "takeover_latitude_deg", "takeover_longitude_deg",
            "arc_distance_nm", "unix_s", "kinetic_energy_j", "vertical_kinetic_energy_j", "latent:realised_flameout_unix_s"]
    pages = {}
    for o in opts:
        rows = []
        per_seed = []
        for sd in seeds:
            X = np.load(sd / "impacts.npy", mmap_mode="r")
            d = {k: np.asarray(X[:, cols[k]], float) for k in need}
            L = np.asarray(X[:, cols[o]], float)
            extra = 0.0
            if a.logon == "fuel-exhaustion":
                lag = logon["logon_unix_s"] - d["latent:realised_flameout_unix_s"]
                with np.errstate(divide="ignore", invalid="ignore"):
                    extra = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
                extra = np.where(np.isfinite(lag) & (lag > 0), extra, -np.inf)
            ll = np.where(np.isfinite(L), L, -np.inf) + extra
            m = ll[np.isfinite(ll)].max() if np.isfinite(ll).any() else 0.0
            pw = d["weight"] * np.exp(ll - m); pw = pw / pw.sum() if pw.sum() > 0 else pw
            d["post"] = pw / len(seeds); d["seed"] = np.full(len(pw), int(sd.name.split("-")[1]))
            per_seed.append(d)
        D = {k: np.concatenate([p[k] for p in per_seed]) for k in per_seed[0]}
        D["parent_key"] = D["seed"] * 10_000_000 + D["parent"].astype(np.int64)
        D["d_takeover_nm"] = haversine_nm(D["takeover_latitude_deg"], D["takeover_longitude_deg"], D["latitude_deg"], D["longitude_deg"])
        D["t_after_0019b_min"] = (D["unix_s"] - T0019B) / 60.0
        groups = [("pooled", np.ones(len(D["post"]), bool))] + [(f, D["family"].astype(int) == k) for k, f in enumerate(fams)]
        for name, sel in groups:
            w = D["post"][sel]
            if not (w.sum() > 0 and (w ** 2).sum() > 0):
                rows.append({"family": name, "weight_share": 0.0, "population_rows": int(sel.sum())}); continue
            u, inv = np.unique(D["parent_key"][sel], return_inverse=True); pp = np.bincount(inv, weights=w)
            rows.append({
                "family": name, "weight_share": float(w.sum() / D["post"].sum()),
                "ess_rows": float(w.sum() ** 2 / (w ** 2).sum()), "ess_parents": float(pp.sum() ** 2 / (pp ** 2).sum()),
                "population_rows": int(sel.sum()), "population_parents": int(len(u)),
                "area_km2_50_90_99": hpd_areas(D["latitude_deg"][sel], D["longitude_deg"][sel], w),
                "d_takeover_nm_5_50_95": wq(D["d_takeover_nm"][sel], w, [.05, .5, .95]),
                "d_7th_arc_nm_5_50_95": wq(D["arc_distance_nm"][sel], w, [.05, .5, .95]),
                "t_after_0019b_min_5_50_95": wq(D["t_after_0019b_min"][sel], w, [.05, .5, .95]),
                "ke_GJ_5_50_95": [x / 1e9 for x in wq(D["kinetic_energy_j"][sel], w, [.05, .5, .95])],
                "vke_GJ_5_50_95": [x / 1e9 for x in wq(D["vertical_kinetic_energy_j"][sel], w, [.05, .5, .95])],
                "latitude_5_50_95": wq(D["latitude_deg"][sel], w, [.05, .5, .95]),
            })
        pages[o] = rows
        f3 = lambda v: " / ".join("–" if not np.isfinite(x) else (f"{x:,.0f}" if abs(x) >= 100 else f"{x:.1f}") for x in v)
        md = [f"# Sensitivity page: {o.split(':', 1)[1]}, log-on cause = {a.logon}", "",
              f"Source `{run}`, seeds {', '.join(p.name for p in seeds)} pooled equally. Generated by `smoke/sensitivity_page.py`.",
              "Distances from takeover equal distances from flame-out only for the flame-out mechanism.", "",
              "| family | weight | ESS rows / parents (population) | area 50/90/99 %, km² | from takeover, NM | from 7th arc, NM | after 00:19:37, min | KE, GJ | vertical KE, GJ |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            if "ess_rows" not in r:
                md.append(f"| {r['family']} | 0 | – ({r['population_rows']:,}) | | | | | | |"); continue
            md.append(f"| {r['family']} | {r['weight_share']:.3f} | {r['ess_rows']:,.0f} / {r['ess_parents']:,.0f} ({r['population_rows']:,} / {r['population_parents']:,}) | "
                      f"{f3(r['area_km2_50_90_99'])} | {f3(r['d_takeover_nm_5_50_95'])} | {f3(r['d_7th_arc_nm_5_50_95'])} | {f3(r['t_after_0019b_min_5_50_95'])} | "
                      f"{f3(r['ke_GJ_5_50_95'])} | {f3(r['vke_GJ_5_50_95'])} |")
        (out / f"page-{o.split(':', 1)[1].replace('/', '_')}-{a.logon}.md").write_text("\n".join(md) + "\n")
    (out / f"sensitivity-{a.logon}.json").write_text(json.dumps(pages, indent=1))
    print("wrote", out, len(pages), "pages")


if __name__ == "__main__":
    main()
