"""The conditional branch on end of flight's impacts: p(x0 | P, H), p(x0 | C3, H), p(x0 | C4, H),
p(x0 | P+C3, H), p(x0 | P+C4, H), before and after the seabed-search evidence (architecture ~18:30 UTC
9 Oct), each reported WITH its tension against the flight posterior, plus the common-origin test
between the Pléiades and COSMO-SkyMed likelihoods.

    python branch_eof289.py <impacts root> <eval root> <surface dir> <out dir> [option] [label]

<impacts root>/seed-<k>/impacts.npy  end of flight's impacts (exchange directory), with COLUMNS.txt
<eval root>/seed-<k>/evaluate.npy    `mh370 evaluate` of seabed-search + pleiades on those impacts
<surface dir>/{likelihood,cosmo}-surface.{f32,toml}  this module's hook exported on a 0.05 deg grid

Weights: impact weight x exp(loglik:<option>) (end of flight's 00:19 data option, default `none`, as
searched areas uses). `<option>+alive` / `+silent` adds end of flight's existence constraint (its own code). The search evidence is the searched-areas module's own per-impact column
(`seabed-search:loglik`, run.toml base: Phase 2 + Bluefin-21, rho 0.05), never recomputed here.
Model averaging: L_F = mean_m L_F,m, with P+C formed per ocean model (L_P,m x L_C,m) before averaging,
because one ocean drives both. COSMO pass: equal weight on dawn-20Mar and dusk-21Mar, inside each model.
No Bayes factor and no P(H | D) is computed (P1): every field is a conditional on H.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from rerun_reference import tension, hdr_mask, dist_nm  # noqa: E402

STEP = 0.05


def read_toml_meta(p):
    meta = {}
    for line in Path(p).read_text().splitlines():
        k, v = line.split(" = ", 1)
        meta[k] = json.loads(v) if v.startswith("[") else (v.strip('"') if v.startswith('"') else float(v))
    return meta


def load_fields(surf):
    mp = read_toml_meta(surf / "likelihood-surface.toml")
    mc = read_toml_meta(surf / "cosmo-surface.toml")
    assert mp["ocean_model"] == mc["ocean_model"] and mp["lon0"] == mc["lon0"] and mp["nlat"] == mc["nlat"]
    models, nlat, nlon = mp["ocean_model"], int(mp["nlat"]), int(mp["nlon"])
    P = np.fromfile(surf / "likelihood-surface.f32", "<f4").reshape(len(models), len(mp["object_rating"]), 2, nlat, nlon).astype(float)
    C = np.fromfile(surf / "cosmo-surface.f32", "<f4").reshape(len(models), 2, 2, nlat, nlon).astype(float)
    # pass-marginal per model and set (log-mean-exp)
    Cm = np.logaddexp(C[:, :, 0], C[:, :, 1]) - math.log(2.0)
    return mp, models, P, Cm


def build_branch(models, P, Cm, rating=0, weight=0):
    """ln L per field and per model; then the model marginal. Fields: P, C3, C4, P+C3, P+C4."""
    per = {}
    for mi, m in enumerate(models):
        lp, c3, c4 = P[mi, rating, weight], Cm[mi, 0], Cm[mi, 1]
        per[m] = {"P": lp, "C3": c3, "C4": c4, "P+C3": lp + c3, "P+C4": lp + c4}
    out = {}
    for f in ["P", "C3", "C4", "P+C3", "P+C4"]:
        stack = np.stack([per[m][f] for m in models])
        mx = stack.max(axis=0)
        stack = np.where(np.isfinite(stack), stack, -np.inf)  # not computed (25 S edge) -> zero likelihood
        mx = stack.max(axis=0)
        mxs = np.where(np.isfinite(mx), mx, 0.0)
        out[f] = {"both models": np.exp(mxs) * np.exp(stack - mxs).mean(axis=0)}
        for mi, m in enumerate(models):
            out[f][m] = np.exp(stack[mi])
    return out


def _eof_module():
    import importlib.util
    f = Path(__file__).resolve().parents[2] / "end-of-flight" / "smoke" / "displacement_hist.py"
    spec = importlib.util.spec_from_file_location("eof_displacement_hist", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def eof_option_weights(seed_dir, base, cause, con=""):
    """Impact weights for an end-of-flight arm with a log-on cause other than `other` (e.g. `fuel-exhaustion`, which
    adds EoF's Erlang APU log-on lag density), taken from EoF's own `option_posteriors` (read-only), so the arm is
    exactly theirs. Option syntax here: `<option>[+<constraint>]@<cause>`."""
    m = _eof_module()
    key = f"{base.replace('/', '_')}__{cause}" + (f"+{con}" if con else "")
    for k, p, _ in m.option_posteriors(Path(seed_dir), Path(seed_dir), constraints=((con,) if con else ())):
        if k == key:
            return p
    raise KeyError(f"{key} not produced by end of flight's option_posteriors for {seed_dir}")


def eof_constraint(seed_dir, A, cols, which):
    """End of flight's declared existence constraint (`alive` / `silent`, PROVISIONAL-OVERNIGHT, 10 Oct ~04:05 UTC),
    called read-only from its own code (hypotheses/end-of-flight/smoke/displacement_hist.py) so that the factor is
    theirs, passed straight through, never re-implemented. Log-on cause `other`, as everywhere in this branch."""
    import importlib.util
    f = Path(__file__).resolve().parents[2] / "end-of-flight" / "smoke" / "displacement_hist.py"
    spec = importlib.util.spec_from_file_location("eof_displacement_hist", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    logon = json.loads((seed_dir / "run.json").read_text())["config"]["hypotheses"]["end-of-flight"]["logon"]
    g = lambda k: np.asarray(A[:, cols.index(k)], float)
    return m.constraint_log_factor(g, logon, "other", which)


def histograms(imp_root, eval_root, mp, option):
    lon0, lat0, nlat, nlon = mp["lon0"], mp["lat0"], int(mp["nlat"]), int(mp["nlon"])
    elon = lon0 - STEP / 2 + STEP * np.arange(nlon + 1)
    elat = lat0 - STEP / 2 + STEP * np.arange(nlat + 1)
    pre, post, seeds, outside, total = [], [], [], [], []
    for sd in sorted(Path(imp_root).glob("seed-*")):
        cols = [l.split("\t")[1] for l in (sd / "COLUMNS.txt").read_text().splitlines()]
        A = np.load(sd / "impacts.npy", mmap_mode="r")
        ev_dir = Path(eval_root) / sd.name
        ej = json.loads((ev_dir / "evaluate.json").read_text())
        E = np.load(ev_dir / "evaluate.npy", mmap_mode="r")
        ec = ej["columns"]
        ks = [i for i, c in enumerate(ec) if c.startswith("seabed-search:loglik")]
        assert len(ks) == 1, ec[:10]
        lat, lon = np.asarray(A[:, cols.index("latitude_deg")]), np.asarray(A[:, cols.index("longitude_deg")])
        opt_, _, cause = option.partition("@")
        base, _, con = opt_.partition("+")
        if (cause and cause != "other") or f"loglik:{base}" not in cols:
            # a non-default log-on cause, or an option end of flight derives rather than stores (e.g. r600-bto)
            w = eof_option_weights(sd, base, cause or "other", con)
        else:
            w = np.asarray(A[:, cols.index("weight")]) * np.exp(np.asarray(A[:, cols.index(f"loglik:{base}")]))
            if con:
                w = w * np.exp(eof_constraint(sd, A, cols, con))
        w = np.where(np.isfinite(w), w, 0.0)
        s = np.exp(np.asarray(E[:, ks[0]]))
        s = np.where(np.isfinite(s), s, 1.0)
        h0 = np.histogram2d(lat, lon, bins=[elat, elon], weights=w)[0]
        h1 = np.histogram2d(lat, lon, bins=[elat, elon], weights=w * s)[0]
        total.append(w.sum())
        outside.append(1 - h0.sum() / w.sum())
        pre.append(h0 / w.sum())
        post.append(h1 / w.sum())  # same normaliser: post sums to Z_search inside the grid
        seeds.append(sd.name)
    return seeds, np.array(pre), np.array(post), outside, elat, elon


def area_km2(lat_c):
    return (STEP * 111.19492664455873) ** 2 * np.cos(np.radians(lat_c))


def summarise(pc, L, area, lat, lon, inside30, inside50, box):
    r = tension(pc, L, area, lat, lon, inside30, inside50, box)
    pcn = pc / pc.sum()
    pj = pcn * L
    pj = pj / pj.sum()
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    r["cond_median_lat"] = float(np.interp(0.5, np.cumsum(pj.sum(axis=1)), lat))
    r["cond_mean_lat"], r["cond_mean_lon"] = float((pj * LAT).sum()), float((pj * LON).sum())
    return r


def run(imp_root, eval_root, surf, out, option="none", label="289.7 prior (reference-289)"):
    surf, out = Path(surf), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    mp, models, P, Cm = load_fields(surf)
    seeds, pre, post, outside, elat, elon = histograms(imp_root, eval_root, mp, option)
    lat = 0.5 * (elat[1:] + elat[:-1])
    lon = 0.5 * (elon[1:] + elon[:-1])
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    area = area_km2(LAT)
    dummy = np.zeros_like(area, dtype=bool)
    rows = []
    reps = [("pooled", pre.mean(axis=0), post.mean(axis=0))] + [(s, a, b) for s, a, b in zip(seeds, pre, post)]
    for rating in range(P.shape[1]):
        for weight in range(2):
            br = build_branch(models, P, Cm, rating, weight)
            for f, by in br.items():
                for m, L in by.items():
                    for rep, a, b in reps:
                        for stage, pc in [("before search", a), ("after search", b)]:
                            r = summarise(pc, L, area, lat, lon, dummy, dummy, dummy)
                            z_h = float((pc / a.sum() * L).sum() / (a / a.sum() * L).sum()) if stage == "after search" else 1.0
                            r.update(field=f, ocean_model=m, object_rating=mp["object_rating"][rating] if "P" in f else "n/a",
                                     cluster_weight=["equal", "count"][weight] if "P" in f else "n/a", replicate=rep, stage=stage,
                                     search_retained_under_H=z_h, search_retained_unconditional=float(pc.sum() / a.sum()),
                                     uncond_mass_in_grid=float(a.sum()))
                            for k in ("uncond_mode", "cond_mode"):
                                r[k + "_lat"], r[k + "_lon"] = r.pop(k)
                            rows.append(r)
    import pandas as pd
    d = pd.DataFrame(rows)
    d = d.drop_duplicates(subset=["field", "ocean_model", "object_rating", "cluster_weight", "replicate", "stage"])
    d["label"], d["option"] = label, option
    d.to_csv(out / "branch.csv", index=False)
    # common origin: Pleiades vs COSMO likelihoods on a flat prior over the grid, per model and both
    co = []
    for rating in range(P.shape[1]):
        for weight in range(2):
            br = build_branch(models, P, Cm, rating, weight)
            for cset in ("C3", "C4"):
                for m in list(br["P"].keys()):
                    LP, LC = br["P"][m], br[cset][m]
                    pa = LC * area / (LC * area).sum()  # 'posterior A' = COSMO-alone on a flat prior
                    r = tension(pa, LP, area, lat, lon, dummy, dummy, dummy)
                    for k in ("uncond_mode", "cond_mode"):
                        r[k + "_lat"], r[k + "_lon"] = r.pop(k)
                    r.update(pair=f"P vs {cset}", ocean_model=m, object_rating=mp["object_rating"][rating], cluster_weight=["equal", "count"][weight], prior="flat over grid")
                    co.append(r)
    pd.DataFrame(co).to_csv(out / "common-origin.csv", index=False)
    info = dict(label=label, option=option, seeds=seeds, uncond_mass_outside_grid=outside, models=models,
                impacts_root=str(Path(imp_root).resolve()), eval_root=str(Path(eval_root).resolve()),
                grid=dict(lon0=mp["lon0"], lat0=mp["lat0"], nlon=int(mp["nlon"]), nlat=int(mp["nlat"]), step=STEP))
    (out / "branch.json").write_text(json.dumps(info, indent=1))
    np.savez_compressed(out / "branch-maps.npz", lat=lat, lon=lon, area=area, pre=pre.mean(axis=0), post=post.mean(axis=0),
                        **{f"L_{f}": br0["both models"] for f, br0 in build_branch(models, P, Cm, 0, 0).items()})
    return d


if __name__ == "__main__":
    run(*sys.argv[1:5], *sys.argv[5:7])
