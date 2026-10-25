"""RAM (pyram) check of the KRAKEN TL on the Transair paths, module tl_grid_ram_subset.ram_job reused unchanged
(dr 2 lambda, dz lambda/20, 9 frequencies per third octave, intensity mean over the last 500 m, hard bottom, NO absorption,
spherical correction); matched KRAKEN without absorption. Delta = RAM - KRAKEN(noabs). Usage: ta810_ram.py <path> <fc> [zs]"""
import sys, json, time, pathlib
import numpy as np, pandas as pd
WS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS / "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"))
import tl_grid_ram_subset as RS, air9_tl_validation as A, kraken_tl as K
path, fc = sys.argv[1], float(sys.argv[2]); zs = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
P = WS / "out/tl/paths"; b = pd.read_csv(P / f"bathy_{path}.csv"); s = pd.read_csv(P / f"ssp_{path}.csv")
rprof, profiles = A.build_profiles(b, s); L = float(rprof[-1]); rd = float(min(739.33 if path.endswith("H11S") else 730.67, profiles[-1][0] - 1.0))
root = f"noabs_{path}_f{fc:g}".replace(".", "p"); wd = WS / "out/tl/work_ram"
try:
    K.tl_path(wd, root, fc, profiles, rprof, np.array([L]), [zs], [rd], A.BOTTOMS["hard"], str(WS), fg=None)
    sh = K.read_shd(wd / f"{root}.shd"); x = L / 6371.0; tlk = float(-20 * np.log10(np.abs(sh["p"][0, 0, 0, -1])) + 10 * np.log10(x / np.sin(x)))
except RuntimeError as e:
    tlk = float("inf")
t0 = time.time(); r = RS.ram_job((path, P / f"bathy_{path}.csv", P / f"ssp_{path}.csv", fc, zs, rd))
r["tl_kraken_noabs_db"] = tlk; r["ram_minus_kraken_db"] = r["tl_ram_db"] - tlk
(WS / "out/tl/ram").mkdir(exist_ok=True); json.dump(r, open(WS / f"out/tl/ram/{path}_f{fc:g}_z{zs:g}.json", "w"), indent=1, default=float); print(r)
