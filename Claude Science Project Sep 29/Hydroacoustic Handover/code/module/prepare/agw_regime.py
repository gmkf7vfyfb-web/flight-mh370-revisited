"""PRE-REGISTRATION and implementation: AGW-branch regime classification per impact sample (brief, 'Where tau
matters, and where it does not'). Committed before it was run on any impact set.

RULE (brief): compute the first acoustic-mode cutoff f_c = c / 4H at each sample's own water depth H, never
an assumed 4,000 m; state the regime of each sample; and carry NO tau-dependence into the AGW branch where
the sample is impulsive.

DEPTH H: GEBCO_2026 (shared ocean transport grid, gebco_2026.json + .i16, 15 arc-second), the median of
  the 3 x 3 cells around the sample (about 1.4 km), positive down. H <= 0 (land or ice surface) is labelled
  'not_ocean' and is excluded from the regime fractions (reported as a count).
SOUND SPEED c: 1,500 m/s. The depth-mean sound speed over the search area is 1,490-1,510 m/s, so f_c and
  the thresholds below move by at most 0.7 %. Declared, not propagated.
CUTOFF PERIOD T_c = 1 / f_c = 4H / c.
SOURCE DURATION tau: end of flight's energy_transfer_tau90_s when ImpactView carries it, with
  tau_ac = k tau90, k in {0.5, 1, 2} (the stage B rule); until then the brief's prior, log-uniform over
  0.05-10 s, drawn independently per sample (seed 20261009).
REGIMES (fixed now), with the stage B spectrum (energy spectral density flat to 1/tau):
  impulsive     tau <= 0.5 T_c   the spectrum is flat to >= 2 f_c, so the whole AGW band (f < f_c) is
                                 flat even for a smoother real pulse shape. The AGW branch uses the total
                                 impulse and the displaced volume only: NO tau.
  transitional  0.5 T_c < tau <= 2 T_c   the roll-off starts inside a factor of 2 of f_c. The AGW branch
                                 carries tau, labelled 'transitional'.
  tau_shaped    tau > 2 T_c      the roll-off falls well inside the AGW band (a ditching-like event). The
                                 AGW branch carries tau.
OUTPUTS: <out>/agw_regime_samples.csv (lat, lon, H, f_c, T_c, tau, regime) for at most 20,000 samples
  (every n-th sample, declared), <out>/agw_regime_summary.json (H and f_c quantiles, regime fractions under
  the tau prior, the fraction impulsive at fixed tau 0.1, 1, 3, 10 s, the not_ocean count, and the impact
  set used). Function regime(H, tau) is the composer-facing rule (to be ported to hypothesis.rs).
Usage: python agw_regime.py <out_dir> stand-in <stand-in summary json>
       python agw_regime.py <out_dir> impacts <impacts.npy> [<lat_col> <lon_col> [<tau90_col>]]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

GRID = Path("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json")
C_W = 1500.0
SEED = 20261009
TAU_LO, TAU_HI = 0.05, 10.0
N_OUT = 20_000


def depth_at(lat, lon, grid=GRID):
    g = json.loads(grid.read_text())
    el = np.memmap(grid.parent / g["elevation_file"], dtype=np.int16, mode="r", shape=(g["nlat"], g["nlon"]))
    i = np.rint((np.asarray(lat) - g["lat0"]) / g["step_deg"]).astype(int)
    j = np.rint((np.asarray(lon) - g["lon0"]) / g["step_deg"]).astype(int)
    assert (i >= 1).all() and (i < g["nlat"] - 1).all() and (j >= 1).all() and (j < g["nlon"] - 1).all(), "sample outside the grid"
    stack = np.stack([el[i + di, j + dj] for di in (-1, 0, 1) for dj in (-1, 0, 1)]).astype(float)
    return -np.median(stack, axis=0)


def cutoff(H, c=C_W):
    f_c = c / (4.0 * H)
    return f_c, 1.0 / f_c


def regime(H, tau, c=C_W):
    H, tau = np.asarray(H, float), np.asarray(tau, float)
    _, T_c = cutoff(np.where(H > 0, H, np.nan), c)
    out = np.where(tau <= 0.5 * T_c, "impulsive", np.where(tau <= 2 * T_c, "transitional", "tau_shaped"))
    return np.where(H > 0, out, "not_ocean")


def samples_standin(summary):
    import imos_preregistration as P
    ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
    q, _ = P.sct.fit_small_circle(ridge)
    pr = P.sct.draw_prior(np.random.default_rng(P.sct.SEED), q, grid, dens, 200_000, P.sct.BASE["sigma_x_nm"])
    return pr[:, 0], pr[:, 1], None, f"stand-in prior ({Path(summary).name}, the stage B draw)"


def main(out_dir, kind, src, *cols):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if kind == "stand-in":
        lat, lon, tau90, label = samples_standin(src)
    else:
        a = np.load(src, allow_pickle=False)
        names = a.dtype.names
        lc, oc = (cols[0], cols[1]) if len(cols) >= 2 else ("lat", "lon")
        lat, lon = np.asarray(a[lc], float), np.asarray(a[oc], float)
        tau90 = np.asarray(a[cols[2]], float) if len(cols) >= 3 else (np.asarray(a["energy_transfer_tau90_s"], float)
                                                                     if names and "energy_transfer_tau90_s" in names else None)
        label = f"impacts {src}"
    n = len(lat)
    H = depth_at(lat, lon)
    rng = np.random.default_rng(SEED)
    if tau90 is None:
        tau = 10 ** rng.uniform(np.log10(TAU_LO), np.log10(TAU_HI), n)
        tau_src = "prior log-uniform 0.05-10 s"
    else:
        tau = tau90 * rng.choice([0.5, 1.0, 2.0], n)
        tau_src = "k * energy_transfer_tau90_s, k in {0.5, 1, 2}"
    reg = regime(H, tau)
    ocean = H > 0
    f_c, T_c = cutoff(np.where(ocean, H, np.nan))
    qs = [0.025, 0.25, 0.5, 0.75, 0.975]
    summ = dict(impact_set=label, n=int(n), not_ocean=int((~ocean).sum()), tau_source=tau_src, c_m_s=C_W,
                H_m_quantiles={str(q): float(np.nanquantile(H[ocean], q)) for q in qs},
                f_c_hz_quantiles={str(q): float(np.nanquantile(f_c, q)) for q in qs},
                T_c_s_quantiles={str(q): float(np.nanquantile(T_c, q)) for q in qs},
                regime_fraction={r: float((reg[ocean] == r).mean()) for r in ["impulsive", "transitional", "tau_shaped"]},
                impulsive_fraction_at_fixed_tau={f"{t:g}": float((regime(H[ocean], np.full(ocean.sum(), t)) == "impulsive").mean())
                                                 for t in [0.1, 1.0, 3.0, 10.0]})
    (out / "agw_regime_summary.json").write_text(json.dumps(summ, indent=1))
    k = max(1, n // N_OUT)
    pd.DataFrame(dict(lat=lat, lon=lon, H_m=H, f_c_hz=f_c, T_c_s=T_c, tau_s=tau, regime=reg)).iloc[::k].to_csv(out / "agw_regime_samples.csv", index=False)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
