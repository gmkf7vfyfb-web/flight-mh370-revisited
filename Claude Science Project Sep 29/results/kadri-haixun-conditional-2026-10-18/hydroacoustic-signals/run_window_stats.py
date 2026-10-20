"""Run the EXISTING pre-registered window statistics (prereg 6ecbb0a, kadri_northern_conditional.py, unchanged code) on the
recomputed windows of the corrected Kadri locality. Only the WINDOWS / KADRI_TIMES constants are replaced, per source set.
Levels unchanged: screen 0.3, mark 0.1, report 0.05.  Usage: python run_window_stats.py MODULE_PREPARE KADRI_DATA WINDOWS_CSV OUT"""
import sys, math, pathlib, json, time
import pandas as pd
PREP, KD, WCSV, OUT = (pathlib.Path(a) for a in sys.argv[1:5]); OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PREP))
import kadri_northern_conditional as KN
import numpy as np
W = pd.read_csv(WCSV)
hms = lambda s: f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d}"
sets = ["crossing_core", "crossing_wide", "eq4_strip_core", "locality_strip_wide", "haixun"]
shots, series, res = KN.h08s_shot_table(KD)
nb = pd.read_csv(KN.HERE / "results-data/imos1d/noise_bands.csv"); meta = KN.P.parse_meta(); cal = {}
for lg in (3315, 3376):
    m = meta[str(lg)]; fg, Gn = KN.N.gain_db(next(KN.P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
    d = nb[nb.logger == lg].set_index("band").p50_1s
    cal[lg] = dict(gain=(fg, Gn), sens=m["sens_db"], m5_20=KN.pw([d["5-10"], d["10-20"]]), m10_40=KN.pw([d["10-20"], d["20-40"]]))
KN.KADRI_TIMES = {"text": "00:52:03", "caption": "00:54:30"}
allrows = []
for s in sets:
    t0 = time.time(); win = {}
    for br, opt in (("T", "text"), ("C", "caption")):
        for stn, key in (("H08S", "h08s"), ("PerthCanyon_3376", "perth")):
            r = W[(W.branch == br) & (W.source_set == s) & (W.station == stn)].iloc[0]
            win[(opt, key)] = (hms(math.floor(r.window_start_s)), hms(math.ceil(r.window_end_s)))
    KN.WINDOWS = win
    A = KN.h08s_part(shots, series); B = KN.perth_part(cal)
    C = pd.concat([A, B], ignore_index=True); C.insert(0, "source_set", s); allrows.append(C)
    print(s, {f"{k[0]}|{k[1]}": v for k, v in win.items()}, f"{time.time()-t0:.0f}s", flush=True)
R = pd.concat(allrows, ignore_index=True); R.to_csv(OUT / "window_statistics.csv", index=False)
json.dump(dict(resolution_check=res, shots_per_panel=shots.groupby("panel").size().to_dict(), last_shot_utc=KN.utc(shots.t.max())),
          open(OUT / "window_statistics_meta.json", "w"), indent=1, default=str)
