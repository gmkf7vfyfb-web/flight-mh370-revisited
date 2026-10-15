"""Stratified subsample of one stratum's impacts for the round-3 sensitivity arm, so the distributions can be
re-plotted after the per-seed files are removed (the disk cannot hold a second full sweep).
Keeps 50,000 rows per seed drawn with probability proportional to the stored weight, with the columns the
sensitivity needs plus the tau90 sidecar fields, and records the exact weight sums it came from.
Usage: python round3_subsample.py STRATUM_DIR OUT_NPZ"""
import sys, json, pathlib, zlib
import numpy as np

KEEP = ["parent", "family", "weight", "t_impact_s", "latitude_deg", "longitude_deg", "flight_path_angle_deg",
        "velocity_east_mps", "velocity_north_mps", "velocity_up_mps", "mass_kg", "family4_code",
        "latent:pushover_drawn", "latent:pushover_to_surface", "latent:impact_bank_deg", "latent:spiral_divergent",
        "latent:max_descent_rate_fpm", "latent:inflight_p_breakup_to_m0019b", "latent:contact_speed_feasible",
        "loglik:r600/no-offset", "loglik:both/no-offset", "loglik:both/startup-offset"]
OPTIONAL = ["latent:spiral_bank_cap_deg"]   # order (b) item 3; kept when the run has it
SIDE = ["tau90_s", "peak_rate_w", "energy_transferred_j", "decel_g", "w_steep"]
N_PER_SEED = 50_000


def main(stratum_dir, out):
    sd = sorted(p for p in pathlib.Path(stratum_dir).glob("seed-*") if p.is_dir())
    cols = json.loads((sd[0] / "run.json").read_text())["impact_columns"]
    ix = {c: i for i, c in enumerate(cols)}
    keep = KEEP + [c for c in OPTIONAL if c in ix]
    rows, meta = [], []
    for d in sd:
        a = np.load(d / "impacts32.npy", mmap_mode="r")
        w = np.asarray(a[:, ix["weight"]], dtype=np.float64)
        rng = np.random.default_rng(zlib.crc32((pathlib.Path(stratum_dir).name + "/" + d.name).encode()))
        # Efficient weighted sample without replacement (exponential race / Gumbel top-k), O(n).
        k = min(N_PER_SEED, int((w > 0).sum()))
        key = np.full(len(w), np.inf)
        pos = w > 0
        key[pos] = rng.exponential(size=int(pos.sum())) / w[pos]
        take = np.argpartition(key, k - 1)[:k]
        take.sort()
        blk = np.asarray(a[take, :])
        z = np.load(d / "tau90_v1.npz")
        rows.append(np.column_stack([blk[:, ix[c]] for c in keep] + [z[k][take] for k in SIDE]).astype(np.float32))
        meta.append(dict(seed=d.name, n=int(len(w)), weight_sum=float(w.sum()), weight_sq_sum=float(np.square(w).sum())))
        print("subsampled", d.name, flush=True)
    np.savez_compressed(out, rows=np.concatenate(rows), columns=np.array(keep + SIDE),
                        meta=np.array(json.dumps(meta)), note=np.array("weight-proportional subsample, 50k per seed"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
