mkdir -p .tmp/standin && cat > .tmp/standin/run_event_tl.py <<'EOF'
"""Stand-in driver (architecture stand-in for hydroacoustics, 11 Oct 2026). Runs the module's OWN
calibration_events.path_tl (prereg 23add102 + amendments 8ae22727, f240d00a; implementation unchanged) on the
ocean-transport calibration path sections (mh370-exchange/ocean-transport/paths-calibration, READY, dafb0d1).

Only change (path/format, disclosed): the sections are delivered already in the stub schema that
shared_paths.convert writes (bathy_*/ssp_* with range_km, elevation_m, ...), under hyphenated names. So
SP.convert is replaced by a copy to the underscore names path_tl reads. No physics or method change.
Receiver depths: EarthScope FDSN IM.H10N1-3 (847, 845, 850 m) and IM.H10S1-3 (865, 852, 863 m), triad means
(H10 is not in the module's data/stations.csv, which lists 2014 triads only).

Usage: python run_event_tl.py <module_prepare_dir> <at_bin> <paths_dir> <out_dir> [bands...]
"""
import shutil, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
import calibration_events as CE  # noqa: E402

RD = {"af447-H10S": (865 + 852 + 863) / 3.0, "sanjuan-charge-H10N": (847 + 845 + 850) / 3.0}

def copy_convert(exp, stub, name):
    t = name.replace("-", "_")
    for k in ("bathy", "ssp"):
        shutil.copy(Path(exp) / f"{k}_{name}.csv", Path(stub) / f"{k}_{t}.csv")

CE.SP.convert = copy_convert
CE.AT_BIN = sys.argv[2]
if len(sys.argv) > 5:
    CE.F.BANDS = [float(b) for b in sys.argv[5:]]
paths, out = Path(sys.argv[3]), Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
dfs = []
for name, rd in RD.items():
    t0 = time.time()
    d, _ = CE.path_tl(paths, name, rd, out)
    b = pd.read_csv(paths / f"bathy_{name}.csv")
    d["source_water_depth_m"] = float(-b.elevation_m.iloc[0])
    dfs.append(d)
    print(name, f"{time.time() - t0:.0f} s", flush=True)
    pd.concat(dfs).to_csv(out / "event_tl.csv", index=False)
EOF
cp -r ".tmp/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" .tmp/standin/module_prepare; echo ok