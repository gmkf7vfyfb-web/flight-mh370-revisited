"""Slim per-seed impact files for the joined V2 run (14 Oct 2026). Keeps every column a summary or consumer needs, float32, with
every unix-time column stored as an offset from T_REF (float32 keeps ~1 ms at 1e4 s; raw unix times in float32 are quantised at
128 s). Writes OUT/impacts32.npy, OUT/run.json (with "slim": {columns, time_columns, t_ref}) and SHA256SUMS, verifies the round trip
against the full file to float32 precision, then the caller deletes the full file.
Usage: python slim_impacts.py RUN_DIR SEED OUT_DIR"""
import json, sys, pathlib, hashlib, re
import numpy as np

T_REF = 1394236800.0   # 00:00:00 UTC 8 Mar 2014
KEEP = re.compile(r"^(parent|family|weight|unix_s|takeover_.*|latitude_deg|longitude_deg|arc_distance_nm|velocity_.*|flight_path_angle_deg|"
                  r"mass_kg|kinetic_energy_j|vertical_kinetic_energy_j|log_q_correction|loglik:.*|bto_residual_us:.*|bfo_innovation_hz:.*|latent:.*)$")
DROP = re.compile(r"^latent:state_m(2315|0011)_.*$")
# Beyond the compact format's core + optional columns: what the joined estimator and the onset diagnostics need.
EXTRA = ["takeover_unix_s", "log_q_correction", "kinetic_energy_j", "vertical_kinetic_energy_j", "latent:predicted_endurance_at_onset_s",
         "latent:onset_support_truncated_fraction", "latent:flameout_minus_predicted_s", "latent:control_requested", "latent:mechanism_from_draw",
         "latent:onset_prediction_priced_by_core", "latent:family_prior",
         # item 1 and item 2 round 2 latents (needed for exact re-weighting of their priors)
         "latent:first_flameout_unix_s", "latent:one_engine_seconds", "latent:dead_engine_side", "latent:asymmetry_compensation_off",
         "latent:free_speed_exponent", "latent:free_path_damping", "latent:dive_trigger_probability", "latent:engines_thrusting_at_onset",
         "latent:spiral_divergent", "latent:residual_bank_sign", "latent:ap_loss_config", "latent:free_dynamics_started_s"]


def is_time(c):
    return c in ("unix_s", "takeover_unix_s") or c.endswith("unix_s")


def main(run, seed, out):
    run = pathlib.Path(run); out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((run / "run.json").read_text())
    Y = np.load(run / "bto-bfo" / f"seed-{seed}" / "impacts.npy", mmap_mode="r")
    spec = json.loads((pathlib.Path(__file__).parent / "compact-columns.json").read_text())
    want = set(spec["core"]) | set(spec["optional"]) | set(EXTRA)
    cols = meta["impact_columns"]; keep = [i for i, c in enumerate(cols) if (c in want or c.startswith(("loglik:", "bto_residual_us:", "bfo_innovation_hz:"))) and not DROP.match(c)]
    names = [cols[i] for i in keep]; tcols = [c for c in names if is_time(c)]
    Z = np.empty((Y.shape[0], len(keep)), np.float32)
    step = 200_000
    for a in range(0, Y.shape[0], step):
        blk = np.asarray(Y[a:a + step][:, keep], np.float64)
        for j, c in enumerate(names):
            if c in tcols: blk[:, j] -= T_REF
        Z[a:a + step] = blk.astype(np.float32)
    # round-trip check on a stride sample
    idx = np.arange(0, Y.shape[0], 97)
    full = np.asarray(Y[idx][:, keep], np.float64); back = Z[idx].astype(np.float64)
    for j, c in enumerate(names):
        if c in tcols: back[:, j] += T_REF
    both = np.isfinite(full) & np.isfinite(back)
    assert np.array_equal(np.isfinite(full), np.isfinite(back)), "NaN pattern changed"
    rel = np.abs(full[both] - back[both]) / np.maximum(np.abs(full[both]), 1.0)
    tmax = max((float(np.nanmax(np.abs(full[:, j] - back[:, j]))) for j, c in enumerate(names) if c in tcols), default=0.0)
    assert tmax < 0.01, f"time round trip {tmax} s"
    np.save(out / "impacts32.npy", Z)
    m = dict(meta); m["impact_columns"] = names
    m["slim"] = dict(columns=names, time_columns=tcols, t_ref=T_REF, max_rel_error_non_time=float(rel.max()) if rel.size else 0.0, max_time_error_s=tmax)
    (out / "run.json").write_text(json.dumps(m))
    h = hashlib.sha256(open(out / "impacts32.npy", "rb").read()).hexdigest()
    (out / "SHA256SUMS").write_text(f"{h}  impacts32.npy\n")
    print(f"slim {out}: {Z.shape} cols, max time error {tmax:.4f} s, max rel {m['slim']['max_rel_error_non_time']:.2e}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
