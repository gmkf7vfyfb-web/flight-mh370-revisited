#!/usr/bin/env python3
"""Does reading coverage at the impact position, instead of over the settled field, change anything?

    python hypotheses/seabed-search/field_coverage_check.py [--step 5] [--set A]

Settling's wreckage samples give the resting latitude and longitude of every settled element of every
drawn field (`mh370-exchange/settling/reference-289-wreckage-field/`). This module has always read the
coverage raster at ONE point, the impact position, because until now there was nothing else to read it
at. With the element positions in hand the question is answerable rather than arguable, and it is the
second regime of `results/seabed-detectable-target.md` section 6 - a field whose extent rivals the
coverage-gap scale - which settling's extent summary says is the regime we are actually in
(structural R90 p50 of 0.86-3.6 km against a 0.01 deg ~ 1.1 km raster cell).

Three treatments of the same campaign term, all using the module's OWN raster code via
`mh370 evaluate` on the element positions, so nothing is reimplemented:

  point    c_k = c_k(impact)                       what every run to date has used
  mean     c_k = mass-weighted mean of c_k(x_i)    the field is one object with a covered fraction
  any      c_k = 1 - prod_i [1 - c_k(x_i)]         some element fell on valid data

`mean` and `any` BRACKET the truth. Recognition is a campaign-level event on a recognisable
signature, not on one pixel of one element, so `any` is the optimistic bound; `mean` is the
conservative one and is what this module reports.

Only SETTLED elements count (fate 0): anything still afloat is ocean drift's evidence, not the seabed
search's. The outcomes are settling's systematic resamples, equally weighted, so the evidence is a
plain mean over them; `--step` subsamples them stride-wise to keep the stratification.

The point-target arm is asserted against the module's own `no_find_probability` column, so a change to
the likelihood that this script did not follow fails here rather than passing quietly.
"""
import argparse, csv, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
EXCHANGE = pathlib.Path("/Users/pete/Downloads/mh370-exchange/settling/reference-289-wreckage-field")
RHO, Q = 0.05, np.array([0.945, 0.900])   # run.toml's reference rho and the two campaigns' q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=5)
    ap.add_argument("--set", default="A")
    ap.add_argument("--dir", type=pathlib.Path, default=EXCHANGE)
    a = ap.parse_args()
    imp = np.memmap(a.dir / f"{a.set}_impacts.f64", dtype="<f8").reshape(-1, 14)
    el = np.memmap(a.dir / f"{a.set}_elements.f64", dtype="<f8").reshape(-1, 8)
    dr = np.load(a.dir / f"{a.set}_draws.npz")
    rows0, draws0 = dr["rows_0"].astype(np.int64), dr["draws_0"].astype(np.int64)
    key = el[:, 0].astype(np.int64) * 1000 + el[:, 1].astype(np.int64)
    ukey = np.unique(key)
    bounds = np.append(np.searchsorted(key, ukey, side="left"), len(key))
    order = np.argsort(rows0 * 1000 + draws0)
    blk = np.empty(len(rows0), np.int64)
    blk[order] = np.arange(len(rows0))
    sel = np.arange(0, len(rows0), a.step)

    fate, lat_el, lon_el, mass_el = el[:, 4], el[:, 5], el[:, 6], el[:, 7]
    idx, owner = [], []
    for i in sel:
        s, e = bounds[blk[i]], bounds[blk[i] + 1]
        keep = np.arange(s, e)[fate[s:e] == 0.0]
        idx.append(keep)
        owner.append(np.full(keep.size, i, np.int64))
    idx, owner = np.concatenate(idx), np.concatenate(owner)

    work = ROOT / "runs" / "seabed-search-analysis"
    work.mkdir(parents=True, exist_ok=True)
    csv_path = work / "field-elements.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["latitude_deg", "longitude_deg"])
        for y, x in zip(imp[rows0[sel], 1], imp[rows0[sel], 2]):
            w.writerow([f"{y:.6f}", f"{x:.6f}"])
        for y, x in zip(lat_el[idx], lon_el[idx]):
            w.writerow([f"{y:.6f}", f"{x:.6f}"])

    out = work / "field-cov"
    subprocess.run([str(ROOT / "target" / "release" / "mh370"), "evaluate", str(HERE / "run.toml"),
                    str(csv_path), str(out)], check=True, cwd=ROOT, capture_output=True)
    names = next(csv.reader(open(out / "evaluate.csv")))
    want = ["seabed-search:covered_fraction_phase2-2014-2017", "seabed-search:covered_fraction_bluefin-2014",
            "seabed-search:no_find_probability"]
    take = [names.index(c) for c in want]
    v = np.loadtxt(out / "evaluate.csv", delimiter=",", skiprows=1, usecols=take)
    n = len(sel)
    c_imp, c_el, module_p = v[:n, :2], v[n:, :2], v[:n, 2]

    pos = {o: j for j, o in enumerate(sel)}
    oidx = np.array([pos[o] for o in owner])
    mass = mass_el[idx]
    msum = np.bincount(oidx, weights=mass, minlength=n)
    c_mean, c_any = np.zeros_like(c_imp), np.zeros_like(c_imp)
    for k in range(2):
        c_mean[:, k] = np.bincount(oidx, weights=mass * c_el[:, k], minlength=n) / np.maximum(msum, 1e-12)
        lg = np.log1p(-np.clip(c_el[:, k], 0.0, 1.0 - 1e-12))
        c_any[:, k] = 1.0 - np.exp(np.bincount(oidx, weights=lg, minlength=n))

    p_no_find = lambda c: RHO + (1 - RHO) * np.prod(1.0 - c * Q, axis=1)
    if not np.allclose(p_no_find(c_imp), module_p, atol=1e-12):
        sys.exit("the point-target arm no longer matches the module's own no_find_probability column")

    report = {"set": a.set, "step": a.step, "outcomes": int(n), "settled_elements": int(idx.size), "rho": RHO}
    for name, c in (("point", c_imp), ("mean", c_mean), ("any", c_any)):
        report[name] = {"Z": float(p_no_find(c).mean()), "mass_removed": float(1 - p_no_find(c).mean()),
                        "mean_phase2_coverage": float(c[:, 0].mean())}
    d = c_mean[:, 0] - c_imp[:, 0]
    report["mean_minus_point_phase2"] = {
        "mean": float(d.mean()), "sd": float(d.std()),
        "share_abs_gt_0.05": float((np.abs(d) > 0.05).mean()),
        "share_abs_gt_0.25": float((np.abs(d) > 0.25).mean()),
        "share_point_zero_field_covered": float(((c_imp[:, 0] == 0) & (c_mean[:, 0] > 0)).mean()),
        "share_point_covered_field_zero": float(((c_imp[:, 0] > 0) & (c_mean[:, 0] == 0)).mean())}
    (work / "field-coverage-check.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
