
import sys, importlib
PK="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
for p in [PK, PK+"/..", PK+"/../weak_signal"]:
    if p not in sys.path: sys.path.insert(0,p)
import run as RUN; importlib.reload(RUN)
for lg in ("3315","3275"):
    f,info=RUN.own_8mar_outside_files(lg); print(lg, len(f), info, f[0].name, f[0].exists())
for lg in ("3376","3274","3315","3275"): print(lg, RUN.calib_offset_db(lg))
s = json.load(open(f"{RD}/blackman_noise/blackman_noise_summary.json"))["stations"]["H01W"]["psd_R_band_db"]; print(list(s))
