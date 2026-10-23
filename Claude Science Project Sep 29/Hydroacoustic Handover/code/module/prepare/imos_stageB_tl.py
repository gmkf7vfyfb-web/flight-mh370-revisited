"""PRE-REGISTRATION and implementation, item 3 STAGE B: from impact source energy to the stage-A SNR at the
open IMOS loggers, so that P_D(SNR) from stage A becomes P_D(eta, tau, C_site, C_rcv, location). Committed
BEFORE any transmission loss on these paths is computed.

ENVIRONMENT: shared ocean transport paths (ruling H5; data/ocean_paths/request.json), converted by
shared_paths.py. Loggers 3315, 3376 (Perth Canyon), 3274, 3275 (Portland). Scott Reef 3250 is excluded:
blocked by the North West Shelf from every impact quantile (data/ocean_paths/imos_path_blockage.csv).
Impact points: the stand-in's 2.5/25/50/75/97.5 % latitude quantiles.

TL (this script): KRAKEN adiabatic incoherent modes (kraken_tl.py, the engine validated relatively on air9,
air8 reproduced), profiles every 5 km (air9_tl_validation.build_profiles, deep c extension by held SA/CT),
HARD bottom only (soft rejected by air9), Francois-Garrison as air9, spherical correction. Bands: third
octaves 5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40 Hz (the stage-A 5-40 Hz band). Source depths 2, 10, 30 m
(declared alternatives; impact energy is deposited near the surface). Receiver: 2 m above the seabed at
the logger, depth = min(path end depth, last profile depth) - 2 m. ADIABATIC UP-SLOPE TO A SEABED
RECEIVER (409-447 m canyon floor, 151-164 m Portland shelf) IS NOT VALIDATED by air9 (SOFAR-axis
receivers); hence C_rcv below.

MAPPING (stage B part 2, run after stage A; fixed now):
  E_ac = eta * E_imp, E_imp = impact_energy_transferred_j when end of flight provides it, else the stand-in
     reference 0.5 * 2.0e5 kg * (V)^2 with V in {120, 160, 200} m/s (declared until ImpactView carries it).
  eta: log-uniform, upper anchor 2.1e-4 (F-35A, this module's Arons inversion; Brown 2026 p. 17), over
     four decades [2.1e-8, 2.1e-4] (brief section 3, amendment).
  Source exposure at 1 m into the water half-space: SE_1m = E_ac * rho c / (2 pi) Pa^2 s (physics.rs).
  Spectrum: energy spectral density flat to f_r = 1/tau and falling as f^-2 above (alternative f^-4);
     tau = acoustic source duration, NOT end of flight's tau90 and never inferred from received data;
     swept log-uniform 0.05-10 s (brief section 'Where tau matters') unless and until ImpactView carries
     energy_transfer_tau90_s, when tau_ac = k * tau90 with k in {0.5, 1, 2}. Normalised to unit integral
     over 1-500 Hz (energy outside 5-40 Hz is lost to this band).
  Received band exposure: SE_b = SE_1m * S_b * 10^(-TL_b/10) * 10^(C_site/10) * 10^(C_rcv/10), summed over
     the 10 bands (TL interpolated in impact latitude between the five quantile paths, per logger).
  C_site ~ N(0, 10 dB) (ruling H6; the air9 common-mode term). C_rcv ~ N(0, 10 dB) (seabed receiver
     coupling, declared, unvalidated).
  Peak 1 s SPL = SE_5-40 / T_eff, where T_eff = (total 5-40 Hz energy) / (peak 1 s 5-40 Hz energy) measured
     on the stage-A templates T_C2 and T_C1 at 3315 (both reported; T_C2 primary). SNR = 10 log10(peak 1 s
     SPL / 1 uPa^2) - background median 1 s 5-40 Hz SPL of the logger (2b definition).
  P_D(location) = coverage(location) x P_D_stageA(SNR) for the nearest stage-A target (3315 uses 3376;
     3275 uses 3274); combined over loggers as 1 - prod(1 - P_D).
  Output: P_D marginal over eta, tau, C_site, C_rcv and V, and P_D at fixed eta (each decade), per impact
     quantile; the eta at which P_D(any logger) = 0.5 ('detectability threshold', brief deliverable 6).

Usage: python imos_stageB_tl.py <stubschema_dir> <at_dir> <out_dir>
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402

LOGGERS = ["3315", "3376", "3274", "3275"]
QUANTS = ["025", "250", "500", "750", "975"]
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
SRC = [2.0, 10.0, 30.0]


def main(stub, at_bin, out_dir):
    stub, out = pathlib.Path(stub), pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, wall = [], {}
    for q in QUANTS:
        for lg in LOGGERS:
            name = f"imp{q}_{lg}"
            bathy = pd.read_csv(stub / f"bathy_{name}.csv")
            ssp = pd.read_csv(stub / f"ssp_{name}.csv")
            rprof, profiles = A.build_profiles(bathy, ssp)
            L = rprof[-1]
            rd = min(float(-bathy.elevation_m.iloc[-1]), profiles[-1][0]) - 2.0
            rr = np.array([L])
            t0 = time.time()
            for fc in BANDS:
                tag = f"f{fc:g}".replace(".", "p")
                try:
                    r, tl, nm, dt = K.tl_path(out / "work" / name, tag, fc, profiles, rprof, rr, SRC, [rd], A.BOTTOMS["hard"], at_bin, fg=A.FG)
                except RuntimeError as e:
                    # DEVIATION (disclosed, 9 Oct): KRAKEN finds NO trapped mode on some profile (shelf below its
                    # modal cutoff, ~6 Hz at 150 m over the hard bottom). The band does not propagate to the
                    # receiver: recorded as tl_db = NaN, status 'no_modes', contributing zero received energy.
                    if "No modes" not in str(e) and "no modes" not in str(e).lower():
                        raise
                    for zs in SRC:
                        rows.append(dict(quantile=q, logger=lg, fc_hz=fc, src_depth_m=zs, rcv_depth_m=rd, range_km=float(L), tl_db=np.nan,
                                         status="no_modes", n_modes_first=0, n_modes_min=0, min_profile_depth_m=float(min(p[0] for p in profiles))))
                    continue
                s = K.read_shd(out / "work" / name / f"{tag}.shd")
                x = s["rr_m"] / 1000.0 / 6371.0
                sph = 10 * np.log10(x / np.sin(x))
                for js, zs in enumerate(s["sz"]):
                    tlz = -20 * np.log10(np.abs(s["p"][0, js, 0])) + sph
                    rows.append(dict(quantile=q, logger=lg, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(L),
                                     tl_db=float(tlz[-1]), status="ok", n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1,
                                     min_profile_depth_m=float(min(p[0] for p in profiles))))
            wall[name] = round(time.time() - t0, 1)
            print(name, wall[name], "s", flush=True)
    pd.DataFrame(rows).to_csv(out / "imos_tl.csv", index=False)
    (out / "imos_tl_wall.json").write_text(json.dumps(wall, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
