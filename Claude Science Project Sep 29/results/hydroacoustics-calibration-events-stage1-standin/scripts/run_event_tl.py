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


def path_tl(exp, name, rd, out):
    """Copy of CE.path_tl with ONE change (disclosed): the receiver-range index [..., -1] is added to
    s["p"][0, js, 0], which is a length-1 array; float() of it raises TypeError under this numpy. Same
    indexing as f35a_eta_calibration.f35a_tl (tlz[-1]) and the audit's sus_tl.py. No other change."""
    stub = out / "stubschema"; stub.mkdir(parents=True, exist_ok=True)
    CE.SP.convert(Path(exp), stub, name)
    tag_ = name.replace("-", "_")
    bathy = pd.read_csv(stub / f"bathy_{tag_}.csv"); ssp = pd.read_csv(stub / f"ssp_{tag_}.csv")
    rprof, profiles = CE.A.build_profiles(bathy, ssp)
    rows = []
    for fc in CE.F.BANDS:
        tag = f"f{fc:g}".replace(".", "p")
        r, tl, nm, dt = CE.K.tl_path(out / "work" / name, tag, fc, profiles, rprof, np.array([rprof[-1]]), CE.F.SRC, [rd],
                                     CE.A.BOTTOMS["hard"], CE.AT_BIN, fg=CE.A.FG)
        s = CE.K.read_shd(out / "work" / name / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0
        sph = 10 * np.log10(x / np.sin(x))
        for js, zs in enumerate(s["sz"]):
            rows.append(dict(path=name, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(rprof[-1]),
                             tl_db=float(-20 * np.log10(np.abs(s["p"][0, js, 0, -1])) + sph[-1]),
                             n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1))
    return pd.DataFrame(rows), np.nan
CE.AT_BIN = sys.argv[2]
CE.F.SRC = [2.0, 10.0, 30.0, 33.0]   # 33 m added: the San Juan charge depth fixed in the prereg (Vergoz 2021); 2-30 m are the module grid
if len(sys.argv) > 5:
    CE.F.BANDS = [float(b) for b in sys.argv[5:]]
paths, out = Path(sys.argv[3]), Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
dfs = []
for name, rd in RD.items():
    t0 = time.time()
    d, _ = path_tl(paths, name, rd, out)
    b = pd.read_csv(paths / f"bathy_{name}.csv")
    d["source_water_depth_m"] = float(-b.elevation_m.iloc[0])
    dfs.append(d)
    print(name, f"{time.time() - t0:.0f} s", flush=True)
    pd.concat(dfs).to_csv(out / "event_tl.csv", index=False)
