"""EXPLORATORY (planning analysis, 9 Oct): TL from the five impact quantiles to H01W and H08S, as stage B
(KRAKEN adiabatic, hard bottom, Francois-Garrison, 5-40 Hz, sources 2/10/30 m, triad hydrophone depth),
plus the RAM-vs-KRAKEN Delta on the median path (ram_tl_check functions), applied as for IMOS."""
import sys, time, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
import air9_tl_validation as A, kraken_tl as K, f35a_eta_calibration as F, ram_tl_check as RC
stub, at_bin, out = Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; SRC = [2.0, 10.0, 30.0]
rows = []
for st in ["H01W", "H08S"]:
    rd = F.receiver_depth(st)
    for q in ["025", "250", "500", "750", "975"]:
        b = pd.read_csv(stub / f"bathy_imp{q}_{st}.csv"); s = pd.read_csv(stub / f"ssp_imp{q}_{st}.csv")
        rprof, prof = A.build_profiles(b, s); t0 = time.time()
        for fc in BANDS:
            tag = f"f{fc:g}".replace(".", "p")
            K.tl_path(out / "work" / f"{q}_{st}", tag, fc, prof, rprof, np.array([rprof[-1]]), SRC, [rd], A.BOTTOMS["hard"], at_bin, fg=A.FG)
            sh = K.read_shd(out / "work" / f"{q}_{st}" / f"{tag}.shd")
            for js, zs in enumerate(sh["sz"]):
                rows.append(dict(station=st, quantile=q, fc_hz=fc, src_depth_m=float(zs), range_km=float(rprof[-1]),
                                 tl_db=float(-20 * np.log10(np.abs(np.ravel(sh["p"][0, js, 0])[-1])) + RC.sph(rprof[-1] * 1e3))))
        print(st, q, round(time.time() - t0, 1), "s", flush=True)
pd.DataFrame(rows).to_csv(out / "ims_tl_kraken.csv", index=False)
RC.PATHS.update({"imp500_H01W": "H01W", "imp500_H08S": "H08S"})
rr = []
for n in ["imp500_H08S", "imp500_H01W"]:
    e = RC.env(stub, n); t0 = time.time()
    for fc in RC.BANDS:
        kt = RC.kraken_band(e, fc, out / "work_ram" / n, at_bin)
        for zs in RC.SRC:
            rt = RC.ram_band(e, fc, zs)
            rr.append(dict(path=n, fc_hz=fc, src_depth_m=zs, tl_kraken_db=kt[zs], tl_ram_db=rt, delta_db=kt[zs] - rt))
    pd.DataFrame(rr).to_csv(out / "ims_ram_delta.csv", index=False)
    print(n, round(time.time() - t0, 1), "s", flush=True)
