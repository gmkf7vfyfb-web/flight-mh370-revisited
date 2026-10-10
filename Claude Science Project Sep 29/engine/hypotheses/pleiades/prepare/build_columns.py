"""Per-impact Pléiades columns for consumers (composer, hydroacoustics, settling), the module's own builder (v2).

v1 (architecture stand-in, 10 Oct ~19:36 UTC, adopted) used the 85-103 E, 43-25 S grid, so 1.3-3.1 % of the weight was not computed.
Composer ruling 1 carries such rows at a neutral value; for this module that is wrong, because L_H is near zero far from the objects.
v2 uses the wide surfaces (78-115 E, 45-5 S; runs/pleiades/wide, run-wide.toml), which cover every next-run impact, and exposes EVERY
object-rating x cluster-weight option through an exact cell lookup.

Writes under <out>:
  surfaces/{likelihood,cosmo}-surface.{f32,toml}     the module's exported hook (copied, sha256 recorded)
  <stratum>/seed-<k>/pleiades-lnL.npy                 v1 layout, default option (rating 5, equal cluster weights), row-aligned
                                                      with end of flight's impacts; plus `cell` (u4, lat_index * nlon + lon_index;
                                                      0xFFFFFFFF = outside the grid) for any other option via reader.py
  reader.py, README.md, SHA256SUMS, READY (last)

Conventions (the module's own, branch_eof289.build_branch): `both` = Pléiades + COSMO (all four contacts, pass-marginal) per ocean
model ("one debris field"); `_mean` = ln of the equal-weight mean of the two models' likelihoods; a model not computed in a cell counts
as zero likelihood there, so `_mean` = the other model - ln 2; `not_computed` = 1 only where BOTH models are not computed (land).

    python build_columns.py <impacts root> <surface dir> <out dir>
"""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import branch_eof289 as b  # noqa: E402
import compact_eval as ce  # noqa: E402

STRATA = {"next-descent-climb": 0, "next-free": 1, "next-repro-radar": 2, "next-routes": 3}
MSHORT = ["glorys12", "globcurrent"]
VALS = [f"lnL_{f}_{m}" for f in ("pleiades", "cosmo", "both") for m in MSHORT + ["mean"]]
DT = np.dtype([("stratum", "u1"), ("seed", "u1"), ("row", "<u4"), ("parent", "<i8"), ("cell", "<u4")]
              + [(v, "<f4") for v in VALS] + [("not_computed", "u1")])
OUTSIDE = np.uint32(0xFFFFFFFF)

READER = '''"""Read Pléiades per-impact log-likelihoods for ANY object-rating x cluster-weight option (exact cell lookup on the module's
surfaces). rating: index into likelihood-surface.toml `object_rating`; weight: 0 equal, 1 count; model: 0 GLORYS12, 1 GlobCurrent,
"mean" for the equal-weight model mean (missing model = zero likelihood). field: "pleiades", "cosmo" (all four contacts,
pass-marginal) or "both"."""
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent

def _meta(n):
    m = {}
    for line in (HERE / "surfaces" / f"{n}.toml").read_text().splitlines():
        k, v = line.split(" = ", 1); m[k] = json.loads(v) if v.startswith("[") else (v.strip('"') if v.startswith('"') else float(v))
    return m

def surfaces():
    mp, mc = _meta("likelihood-surface"), _meta("cosmo-surface")
    nl, nn, nm = int(mp["nlat"]), int(mp["nlon"]), len(mp["ocean_model"])
    P = np.fromfile(HERE / "surfaces/likelihood-surface.f32", "<f4").reshape(nm, len(mp["object_rating"]), 2, nl, nn)
    C = np.fromfile(HERE / "surfaces/cosmo-surface.f32", "<f4").reshape(nm, 2, 2, nl, nn).astype(float)
    Cm = np.logaddexp(C[:, 1, 0], C[:, 1, 1]) - math.log(2.0)   # all four contacts, pass-marginal
    return mp, P, Cm

def load(seed_dir, rating=0, weight=0, field="both", model="mean"):
    mp, P, Cm = surfaces()
    cell = np.load(Path(seed_dir) / "pleiades-lnL.npy", mmap_mode="r")["cell"]
    ok = cell != 0xFFFFFFFF; nn = int(mp["nlon"])
    i, j = (cell[ok] // nn).astype(np.int64), (cell[ok] % nn).astype(np.int64)
    def per(mi):
        v = {"pleiades": P[mi, rating, weight, i, j].astype(float), "cosmo": Cm[mi, i, j]}
        v["both"] = v["pleiades"] + v["cosmo"]
        return v[field]
    if model == "mean":
        s = np.stack([per(0), per(1)]); s = np.where(np.isfinite(s), s, -np.inf)
        val = np.logaddexp(s[0], s[1]) - math.log(2.0)
    else:
        val = per(model)
    out = np.full(len(cell), np.nan); out[ok] = val
    return out
'''


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def main(imp_root, surf, out):
    imp_root, surf, out = Path(imp_root), Path(surf), Path(out)
    (out / "surfaces").mkdir(parents=True, exist_ok=True)
    for f in ("likelihood-surface.f32", "likelihood-surface.toml", "cosmo-surface.f32", "cosmo-surface.toml"):
        shutil.copy2(surf / f, out / "surfaces" / f)
    (out / "reader.py").write_text(READER)
    mp, models, P, Cm = b.load_fields(surf)
    assert [m.split("+")[0][:8] for m in models] == ["glorys12", "globcurr"], models
    lon0, lat0, nlat, nlon = mp["lon0"], mp["lat0"], int(mp["nlat"]), int(mp["nlon"])
    sums, stats = [], []
    for st, code in STRATA.items():
        for sd in ce.seed_dirs(imp_root / st):
            k = int(sd.name.split("-")[1])
            cols, g, n = ce.seed_reader(sd)
            lat, lon = g("latitude_deg"), g("longitude_deg")
            j = np.floor((lon - (lon0 - b.STEP / 2)) / b.STEP).astype(np.int64)
            i = np.floor((lat - (lat0 - b.STEP / 2)) / b.STEP).astype(np.int64)
            ok = (i >= 0) & (i < nlat) & (j >= 0) & (j < nlon)
            R = np.zeros(n, DT)
            R["stratum"], R["seed"], R["row"], R["parent"] = code, k, np.arange(n, dtype=np.uint32), g("parent").astype(np.int64)
            R["cell"] = OUTSIDE; R["cell"][ok] = (i[ok] * nlon + j[ok]).astype(np.uint32)
            per = {}
            for mi, m in enumerate(MSHORT):
                lp = np.full(n, np.nan); lc = np.full(n, np.nan)
                lp[ok] = P[mi, 0, 0, i[ok], j[ok]]; lc[ok] = Cm[mi, 1, i[ok], j[ok]]
                per[m] = {"pleiades": lp, "cosmo": lc, "both": lp + lc}
            for f in ("pleiades", "cosmo", "both"):
                for m in MSHORT:
                    R[f"lnL_{f}_{m}"] = per[m][f]
                s = np.stack([per[m][f] for m in MSHORT]); s = np.where(np.isfinite(s), s, -np.inf)
                with np.errstate(invalid="ignore"):
                    mean = np.logaddexp(s[0], s[1]) - math.log(2.0)
                R[f"lnL_{f}_mean"] = np.where(np.isfinite(mean), mean, np.nan)
            R["not_computed"] = ~np.isfinite(R["lnL_both_mean"])
            d = out / st / sd.name; d.mkdir(parents=True, exist_ok=True)
            tmp = d / "pleiades-lnL.partial.npy"; np.save(tmp, R); tmp.rename(d / "pleiades-lnL.npy")
            w = g("weight"); w = np.where(np.isfinite(w), w, 0.0)
            stats.append(dict(stratum=st, seed=k, rows=int(n), outside_grid_rows=int((~ok).sum()), not_computed_rows=int(R["not_computed"].sum()),
                              not_computed_prior_weight_share=float(w[R["not_computed"].astype(bool)].sum() / w.sum())))
            sums.append(f"{sha(d / 'pleiades-lnL.npy')}  {st}/{sd.name}/pleiades-lnL.npy")
            print(st, sd.name, stats[-1]["not_computed_rows"], flush=True)
    sums += [f"{sha(out / 'surfaces' / f)}  surfaces/{f}" for f in sorted(p.name for p in (out / "surfaces").iterdir())]
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    (out / "build-stats.json").write_text(json.dumps(dict(impacts_root=str(imp_root), surfaces=str(surf), grid=dict(lon0=lon0, lat0=lat0, nlon=nlon, nlat=nlat),
                                                          ocean_models=models, object_rating=mp["object_rating"], per_seed=stats), indent=1))
    return stats


if __name__ == "__main__":
    st = main(*sys.argv[1:4])
    print("max not-computed prior-weight share", max(s["not_computed_prior_weight_share"] for s in st))
