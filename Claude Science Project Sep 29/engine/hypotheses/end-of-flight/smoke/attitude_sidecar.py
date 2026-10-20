"""Impact attitude sidecar (hydroacoustics request, coordination/END_OF_FLIGHT.md 17 Oct 2026 18:52Z, option (b)).

    python attitude_sidecar.py SEED_DIR [SEED_DIR ...]

Writes <seed dir>/attitude_v1.npz, row-aligned with impacts32.npy:
  bank_deg          float32  copy of latent:impact_bank_deg
  bank_source       uint8    0 = bank from the free (uncontrolled) dynamics or a commanded turn: a continuous value;
                             1 = commanded wings level at impact. The point-mass integrator sets bank = the commanded bank
                                 (integrator.rs line 335), and the glide, Track, push-over-to-surface and ditching-leg
                                 commands hold bank 0 (profile.rs lines 1330-1383; manoeuvre.rs Hold legs). Exactly 0.0 is
                                 therefore a modelled value, not a placeholder. It has no bank dispersion: a reach gap.
  n_pulses          uint8    1 for every row (declared single-pulse model, results/eof-impact-tau-method-oct11.md)
The flag is exact: in the no-intervention arm (control_realised 2) no row has bank exactly 0.0 (checked on run J waypoints seed 1).
"""
import sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load


def main(dirs):
    for sd in map(pathlib.Path, dirs):
        if not sd.is_dir(): continue
        meta, g = load(sd); b = g("latent:impact_bank_deg")
        src = (b == 0.0).astype(np.uint8)
        np.savez(sd / "attitude_v1.npz", bank_deg=b.astype(np.float32), bank_source=src, n_pulses=np.ones(len(b), np.uint8),
                 note=np.array("bank_source 1 = commanded wings level (exact); 0 = free dynamics or commanded turn"))
        print(f"{sd}: rows {len(b)} wings-level share {src.mean():.4f}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
