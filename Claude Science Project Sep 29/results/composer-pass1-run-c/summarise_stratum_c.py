"""Composer pass 1 (run C): per-stratum histograms of the composed products, pooled exactly as summary.rs pools replicates.

Adaptation of results/composer-pass0/summarise_stratum.py to run C: any number of seeds (halves = first and second half of the
seeds, as compose() splits them), float32 inputs, families by EoF family4_code (1 A1, 2 A2, 3 B, 6 outside B) and family_code
(0-6, B split 3/5/6), contact-speed share above 212 m/s, optional row-weight export (settling's G12 contract). The grid, pooling and
equal-area cell code are imported unchanged from summarise_stratum.py (the transcription of summary.rs and patch B).
Usage: python summarise_stratum_c.py <stratum> <input dir> <rust out dir> <out dir> <option tag> [--export <dir> <product ids, comma>]
"""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "repo/Claude Science Project Sep 29/results/composer-pass0"))
import summarise_stratum as S          # grid_bin, equal_area_cell, pooling, NPTS, NY, NX, BANDS, CELL_KM2 (pass-0 transcription)

NF = 7


def load_inputs(d, k, names):
    h = json.loads((d / f"seed-{k}.json").read_text()); c = h["columns"]
    X = np.memmap(d / f"seed-{k}.f32", dtype="<f4", mode="r", shape=(h["rows"], len(c)))
    return {n: np.array(X[:, c.index(n)], dtype=float) for n in names}, h


def kish(x):
    s2 = (x ** 2).sum()
    return float(x.sum() ** 2 / s2) if s2 > 0 else 0.0


def main(stratum, ind, rout, outd, tag, export=None, export_ids=()):
    ind, rout = pathlib.Path(ind), pathlib.Path(rout); outd = pathlib.Path(outd) / stratum / tag; outd.mkdir(parents=True, exist_ok=True)
    P = json.loads((rout / "products.json").read_text()); prods = {p["id"]: p for p in P["products"]}
    with_w = sorted(p.name for p in (rout / "weights").iterdir())
    seeds = sorted(r["seed"] for r in prods[with_w[0]]["replicates"]); ns = len(seeds); half = ns // 2
    cols = {}
    for k in seeds:
        d, h = load_inputs(ind, k, ["mode", "family", "family4", "latitude_deg", "longitude_deg", "speed_mps"])
        d["bin"] = S.grid_bin(d["latitude_deg"]); d["cell"] = S.equal_area_cell(d["latitude_deg"], d["longitude_deg"])
        d["fast"] = d["speed_mps"] > 212.0
        cols[k] = {x: d[x] for x in ("mode", "family", "family4", "latitude_deg", "bin", "cell", "fast")}
    res = {"stratum": stratum, "option": tag, "seeds": seeds, "cell_km2": S.CELL_KM2, "ny": S.NY, "nx": S.NX, "products": {}}
    arrays = {}
    for pid in with_w:
        p = prods[pid]; modes = [r["modes"] for r in p["replicates"]]
        fac, mp = S.pooling(modes); halves = [S.pooling(modes[:half])[0], S.pooling(modes[half:])[0]]
        lat_h = np.zeros(S.NPTS); lat_hh = [np.zeros(S.NPTS), np.zeros(S.NPTS)]
        f4_h = np.zeros((NF, S.NPTS)); f4_m = np.zeros(NF); fc_h = np.zeros((NF, S.NPTS)); fc_m = np.zeros(NF)
        f4_hh = [np.zeros((NF, S.NPTS)), np.zeros((NF, S.NPTS))]
        cell_h = np.zeros(S.NY * S.NX); cell_hh = [np.zeros(S.NY * S.NX), np.zeros(S.NY * S.NX)]
        f4_cell = np.zeros((4, S.NY * S.NX))
        mass = fast = 0.0; fast_f4 = np.zeros(NF); ess_f4, ess_fc, ess_band, ess_all = {}, {}, {}, []
        for i, k in enumerate(seeds):
            d = cols[k]
            wq = np.fromfile(rout / "weights" / pid / f"seed-{k}.f32", dtype="<f4").astype(float)
            md = d["mode"].astype(int); w = wq * fac[i][md]; hi = 0 if i < half else 1
            hw = wq * halves[hi][i if i < half else i - half][md]
            b, c = d["bin"], d["cell"]; f4 = d["family4"].astype(int); fc = d["family"].astype(int)
            okb, okc = b >= 0, c >= 0
            lat_h += np.bincount(b[okb], weights=w[okb], minlength=S.NPTS)
            lat_hh[hi] += np.bincount(b[okb], weights=hw[okb], minlength=S.NPTS)
            cell_h += np.bincount(c[okc], weights=w[okc], minlength=S.NY * S.NX)
            cell_hh[hi] += np.bincount(c[okc], weights=hw[okc], minlength=S.NY * S.NX)
            for f in range(NF):
                s4 = okb & (f4 == f); sc = okb & (fc == f)
                f4_h[f] += np.bincount(b[s4], weights=w[s4], minlength=S.NPTS); f4_m[f] += w[f4 == f].sum()
                f4_hh[hi][f] += np.bincount(b[s4], weights=hw[s4], minlength=S.NPTS)
                fc_h[f] += np.bincount(b[sc], weights=w[sc], minlength=S.NPTS); fc_m[f] += w[fc == f].sum()
                fast_f4[f] += w[(f4 == f) & d["fast"]].sum()
                ess_f4.setdefault(str(f), []).append(kish(wq[f4 == f])); ess_fc.setdefault(str(f), []).append(kish(wq[fc == f]))
            for j, f in enumerate((1, 2, 3, 6)):
                s4 = okc & (f4 == f); f4_cell[j] += np.bincount(c[s4], weights=w[s4], minlength=S.NY * S.NX)
            lat = d["latitude_deg"]
            for lo, hi_ in S.BANDS:
                ess_band.setdefault(f"{lo}..{hi_}", []).append(kish(wq[(lat >= lo) & (lat < hi_)]))
            ess_all.append(kish(wq)); mass += w.sum(); fast += w[d["fast"]].sum()
            if export and pid in export_ids:
                ed = pathlib.Path(export) / f"{tag}-{pid.split('-', 1)[1]}" / stratum; ed.mkdir(parents=True, exist_ok=True)
                w.astype("<f4").tofile(ed / f"seed-{k}.f32")          # pooled within-stratum weight (stratum mass = mass)
        res["products"][pid] = {"mass": mass, "mode_probability": mp.tolist(), "pool_factors": fac.tolist(),
                                "family4_mass": (f4_m / mass).tolist(), "family_code_mass": (fc_m / mass).tolist(),
                                "fast_share": fast / mass, "fast_share_by_family4": (fast_f4 / np.where(f4_m > 0, f4_m, 1)).tolist(),
                                "ess_rows_per_seed": ess_all, "ess_rows_per_seed_by_family4": ess_f4, "ess_rows_per_seed_by_family_code": ess_fc,
                                "ess_rows_per_seed_by_latitude_band": ess_band}
        arrays[f"{pid}|lat"] = lat_h; arrays[f"{pid}|lat_h0"] = lat_hh[0]; arrays[f"{pid}|lat_h1"] = lat_hh[1]
        arrays[f"{pid}|f4"] = f4_h; arrays[f"{pid}|fc"] = fc_h; arrays[f"{pid}|f4_h0"] = f4_hh[0]; arrays[f"{pid}|f4_h1"] = f4_hh[1]
        arrays[f"{pid}|cell"] = cell_h.astype(np.float32); arrays[f"{pid}|cell_h0"] = cell_hh[0].astype(np.float32)
        arrays[f"{pid}|cell_h1"] = cell_hh[1].astype(np.float32); arrays[f"{pid}|f4cell"] = f4_cell.astype(np.float32)
    np.savez_compressed(outd / "hist.npz", **arrays)
    (outd / "summary.json").write_text(json.dumps(res, indent=1))
    print(stratum, tag, len(with_w), "products", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    ex, ids = None, ()
    if "--export" in a:
        i = a.index("--export"); ex, ids = a[i + 1], tuple(a[i + 2].split(",")); a = a[:i]
    main(*a, export=ex, export_ids=ids)
