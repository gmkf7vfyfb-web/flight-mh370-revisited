"""Impact energy-transfer duration sidecar, impact_tau_method = 1 (results/eof-impact-tau-method-oct11.md; architecture ruling 20:35 -0600
10 Oct item 2). Per row, from the contact state only (speed, |flight-path angle|, mass) and two declared random parameters drawn
reproducibly (SeedSequence of stratum name, seed number; row order):
  shallow (<= 10 deg): mean deceleration a ~ U[0.75, 3.0] g; F(t) = 1 - (1 - t/T)^2, T = v/a; t05 = (1 - sqrt .95) T, t95 = (1 - sqrt .05) T
  steep (>= 30 deg): progressive crush, L_eff ~ U[0.5, 1.0] x 63.7 m; t05 = 0.05 L/v, t95 = 0.95 L/v
  blend: log-linear in angle between 10 and 30 deg (w = 0 shallow, 1 steep).
Writes <seed dir>/tau90_v1.npz: tau90_s, t05_s, t95_s, peak_rate_w, energy_transferred_j, w_steep, decel_g, l_eff_m (row-aligned with the
compact impacts32.npy).
Usage: python tau_sidecar.py SEED_DIR [SEED_DIR ...]
"""
import sys, pathlib, zlib
import numpy as np
from compact_impacts import open_seed

G0 = 9.80665; L777 = 63.7
A_SH = (1 - np.sqrt(0.95), 1 - np.sqrt(0.05))


def tau_rows(v, theta_deg, m, rng):
    n = len(v); a = rng.uniform(0.75, 3.0, n) * G0; L = rng.uniform(0.5, 1.0, n) * L777
    with np.errstate(divide="ignore", invalid="ignore"):
        T = v / a
        sh = (A_SH[0] * T, A_SH[1] * T, m * a * v)
        ke = 0.5 * m * v ** 2
        st = (0.05 * L / v, 0.95 * L / v, ke * v / L)
        w = np.clip((theta_deg - 10.0) / 20.0, 0.0, 1.0)
        blend = [np.exp((1 - w) * np.log(x) + w * np.log(y)) for x, y in zip(sh, st)]
    t05, t95, peak = blend
    bad = ~(np.isfinite(v) & (v > 0) & np.isfinite(theta_deg) & np.isfinite(m))
    out = {"tau90_s": t95 - t05, "t05_s": t05, "t95_s": t95, "peak_rate_w": peak, "energy_transferred_j": ke,
           "w_steep": w, "decel_g": a / G0, "l_eff_m": L}
    return {k: np.where(bad, np.nan, x).astype(np.float32) for k, x in out.items()}


def main(dirs):
    for sd in map(pathlib.Path, dirs):
        meta, g = open_seed(sd, sd)
        v = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
        th = np.abs(g("flight_path_angle_deg")); m = g("mass_kg")
        stratum = sd.parent.name; k = int(sd.name.split("-")[-1])
        rng = np.random.default_rng(np.random.SeedSequence([zlib.crc32(stratum.encode()), k, 1]))
        out = tau_rows(v, th, m, rng)
        np.savez(sd / "tau90_v1.npz", **out, method=np.array(1), note=np.array("results/eof-impact-tau-method-oct11.md"))
        t = out["tau90_s"]; print(sd, "rows", len(t), "tau90 q05/q50/q95 %.3f/%.3f/%.3f s" % tuple(np.nanquantile(t, [.05, .5, .95])))


if __name__ == "__main__":
    main(sys.argv[1:])
