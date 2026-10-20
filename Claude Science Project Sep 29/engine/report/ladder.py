#!/usr/bin/env python3
"""Summarise the evidence ladder: what each measurement set adds, and how it is sampled.

Usage: python report/ladder.py RUN_DIR [RUN_DIR ...]

For each run this reports the posterior summary the reports already carry, plus two things
the ladder is specifically for.

Out-of-sample 00:19. A rung whose likelihood stops at 00:11 still flies every particle through
to 00:19:37 and the filter still records its state there, so the 00:19 arc can be scored against
a posterior that never saw it. The residual is recomputed here from the saved final positions
with report/satcom_model.py's forward model - the same BTO equations as crates/satcom, checked
against the core's fixture to 1e-6 - rather than read from the run, so the figure is independent
of whatever the filter chose to weight. A rung fitted only to the earlier arcs should show a
wider and more biased 00:19 residual than the rung fitted through it; how much wider is the
measure of what the last arc contributes.

Where the fuel evidence bites. `fuel_exhausted_unix_s` gives the weight that ran dry before each
of the two deadlines, which is what the endurance proposal is trying to stop proposing.

Nothing here re-runs the filter; it reads runs/*/summary.json, diagnostics.json and final.npy.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import satcom_model as S

ROOT = Path(__file__).resolve().parent.parent
M0011 = 1394237459.0   # 2014-03-08T00:10:59Z
M0019B = 1394237977.0  # 2014-03-08T00:19:37Z, the filter's final step
SHOULDER = (-36.5, -34.5)


def bto_vectorised(sat, lat, lon, alt_ft):
    """satcom_model.bto over arrays, in the same equations and constants.

    The scalar form is a Python call per particle, which is minutes per run at 14 million
    particles. This evaluates the same expression with numpy and is checked against the scalar
    function on a sample every time it is used, so the speed-up cannot silently change a number.
    """
    la, lo = np.radians(lat), np.radians(lon)
    h = np.asarray(alt_ft) * S.KM_FT
    sinl, cosl = np.sin(la), np.cos(la)
    n = S.A / np.sqrt(1.0 - S.E2 * sinl**2)
    xy = (n + h) * cosl
    p = np.stack([xy * np.cos(lo), xy * np.sin(lo), (n * (1.0 - S.E2) + h) * sinl], axis=-1)
    sat = np.asarray(sat, dtype=float)
    up = np.linalg.norm(p - sat, axis=-1)
    down = np.linalg.norm(sat - S.GES)
    return 2.0 * (up + down) / S.C * 1e6 - S.OFFSET


def _check_vectorised(sat, lat, lon, alt, n=64):
    """Agreement with the scalar model on a random sample; raises if it ever drifts."""
    rng = np.random.default_rng(0)
    i = rng.choice(len(lat), size=min(n, len(lat)), replace=False)
    mine = bto_vectorised(sat, lat[i], lon[i], alt[i])
    theirs = np.array([S.bto(sat, lat[j], lon[j], alt[j]) for j in i])
    worst = float(np.max(np.abs(mine - theirs)))
    if worst > 1e-6:
        raise SystemExit(f"vectorised BTO disagrees with satcom_model.bto by {worst:.3g} us")
    return worst


def observed_bto(epoch_id):
    """The measured BTO and its stated sd for one epoch, from the observation table."""
    import csv

    with open(ROOT / "data/satcom-observations.csv") as f:
        for row in csv.DictReader(f):
            if row["epoch_id"] == epoch_id:
                return float(row["bto_us"]), float(row["bto_sd_us"])
    raise KeyError(epoch_id)


def load_final(run_dir, case):
    """Pooled (weight, columns) over every seed of a case."""
    run = json.loads((run_dir / "run.json").read_text())
    ix = {k: i for i, k in enumerate(run["final_columns"])}
    parts = sorted((run_dir / case).glob("seed-*/final.npy"))
    if not parts:
        return None, None, None
    # Kept at the stored width; promoting 56 million rows x 18 columns to float64 would cost
    # about 8 GB alongside a filter run. Only the weights are widened, because they are summed
    # over every particle.
    rows = np.concatenate([np.load(p, mmap_mode="r") for p in parts])
    w = np.asarray(rows[:, 0], dtype=np.float64)
    return rows, ix, w / w.sum()


def weighted_quantile(x, w, q):
    o = np.argsort(x)
    return float(x[o][np.searchsorted(np.cumsum(w[o]), q)])


def summarise(run_dir):
    run_dir = Path(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text())
    conv = json.loads((run_dir / "convergence.json").read_text())
    out = []
    for case, cc in zip(summary["cases"], conv["cases"]):
        rows, ix, w = load_final(run_dir, case["case"])
        rec = {
            "run": run_dir.name,
            "case": case["case"],
            "seeds": len(case["seeds"]),
            "median": case["stats"]["median"],
            "q025": case["stats"]["q025"],
            "q975": case["stats"]["q975"],
            "shoulder": case["probability"]["shoulder"],
            "overlap": case["reference_overlap"],
            "split_half": case["split_half_overlap"],
            "replicate_span_deg": cc["reported"]["replicate_median_span_deg"],
            "log_evidence": case["log_evidence"],
        }
        if rows is not None:
            lat = np.asarray(rows[:, ix["latitude_deg"]], dtype=np.float64)
            lon = np.asarray(rows[:, ix["longitude_deg"]], dtype=np.float64)
            alt = np.asarray(rows[:, ix["altitude_ft"]], dtype=np.float64)
            # Out-of-sample 00:19 BTO, recomputed from the saved final state.
            z, sd = observed_bto("m0019b")
            sat, _ = S.satstate(M0019B)
            rec["bto0019_vector_check_us"] = _check_vectorised(sat, lat, lon, alt)
            pred = bto_vectorised(sat, lat, lon, alt)
            res = z - pred
            rec["bto0019_mean_us"] = float((w * res).sum())
            rec["bto0019_rms_us"] = float(np.sqrt((w * res**2).sum()))
            rec["bto0019_sd_us"] = sd
            ex = rows[:, ix["fuel_exhausted_unix_s"]]
            if np.isfinite(ex).any():
                rec["dry_before_0011_pct"] = float(100 * w[np.isfinite(ex) & (ex < M0011)].sum())
                rec["dry_before_0019_pct"] = float(100 * w[np.isfinite(ex) & (ex < M0019B)].sum())
                rec["fuel_kg_median"] = weighted_quantile(rows[:, ix["fuel_kg"]], w, 0.5)
                rec["above_ceiling_h_mean"] = float((w * rows[:, ix["fuel_above_ceiling_s"]]).sum() / 3600)
        draws = np.array([[m["distinct_origins"] for m in json.loads(p.read_text())["modes"]]
                          for p in sorted((run_dir / case["case"]).glob("seed-*/diagnostics.json"))])
        if draws.size:
            rec["draws_mh"] = float(draws.mean(0)[1])
            rec["draws_mt"] = float(draws.mean(0)[3])
        out.append(rec)
    return out


def main():
    recs = [r for d in sys.argv[1:] for r in summarise(d)]
    keys = ["run", "case", "seeds", "median", "shoulder", "overlap", "split_half",
            "replicate_span_deg", "log_evidence", "bto0019_mean_us", "bto0019_rms_us",
            "dry_before_0011_pct", "dry_before_0019_pct", "fuel_kg_median", "draws_mh", "draws_mt"]
    print(",".join(keys))
    for r in recs:
        print(",".join("" if r.get(k) is None else
                       (r[k] if isinstance(r[k], str) else f"{r[k]:.4f}") for k in keys))
    (ROOT / "runs/ladder.json").write_text(json.dumps(recs, indent=1) + "\n")


if __name__ == "__main__":
    main()
