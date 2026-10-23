mkdir -p "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/calibration_events/stage1b"; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; cat > kadri_crash_timing.py <<'EOF'
"""EXPLORATORY (labelled; not pre-registered, correction track 22 Oct 2026): arrival-time check of Kadri (2024) Figs. 4-5
past-crash panels against a sound-channel arrival. For each panel: impact time (Kadri S1, or BEA for AF447: 02:14:28 UTC),
impact position (S1; F-35A: the module's Metz-derived working point 40.64 N 142.96 E), receiver triad centroid
(data/stations.csv; H10S from the ocean transport path README, -8.951, -14.652), WGS84 geodesic range, predicted arrival
t = impact + range / c with c ~ N(1.482, 0.006) km/s (the module's SOFAR prior). Observed: Kadri's highlighted box (digitised
box_min in results-data/calibration_events/kadri_peaks.csv where present, else the window start + 5 min, Kadri p. 11:
"presented around the middle of a 10 min time window"). Reported: observed minus predicted (s) and the implied group speed.
Digitised times are +/- 1 px (~2.4 s at 669 px over 10 min)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from pyproj import Geod
HERE = Path(__file__).parent.parent
g = Geod(ellps="WGS84")
st = pd.read_csv(HERE / "data/stations.csv", comment="#").groupby("triad")[["latitude_deg", "longitude_deg"]].mean()
st.loc["H10S"] = (-8.951, -14.652)
def dms(d, m, s, sign): return sign * (d + m / 60 + s / 3600)
EV = {  # name: (impact UTC, lat, lon, source)
 "F-35A": ("2019-04-09T10:26:30Z", 40.64, 142.96, "S1 time; module working point (Metz et al. 2023)"),
 "Yemenia 626": ("2009-06-29T22:50:00Z", -11.3715, 43.2250, "S1 'around 22:50'; ASN site (S1 position on land, amendment 2)"),
 "Sriwijaya 182": ("2021-01-09T07:40:00Z", dms(5, 54, 54, -1), dms(107, 7, 6, 1), "S1"),
 "AF447": ("2009-06-01T02:14:28Z", dms(3, 3, 57, 1), dms(30, 33, 42, -1), "BEA impact time; S1 position"),
 "Transair 810": ("2021-07-02T11:46:00Z", dms(21, 18, 41, 1), dms(157, 54, 16, -1), "S1"),
 "Lion Air 904": ("2013-04-13T07:10:00Z", dms(8, 45, 0.96, -1), dms(115, 9, 1.01, 1), "S1"),
}
PANELS = [  # event, receiver, window start UTC (Kadri panel axis), box (min) if digitised
 ("F-35A", "H11N", "2019-04-09T10:58:00Z", (4.29, 5.71)), ("F-35A", "H11S", "2019-04-09T10:59:00Z", (4.40, 5.87)),
 ("Yemenia 626", "H08N", "2009-06-29T23:29:00Z", (4.05, 5.52)), ("Yemenia 626", "H08S", "2009-06-29T23:27:00Z", (4.25, 5.71)),
 ("Sriwijaya 182", "H08S", "2021-01-09T08:06:00Z", (4.60, 6.07)), ("AF447", "H10S", "2009-06-01T02:41:00Z", (3.98, 5.46)),
 ("Transair 810", "H11N", "2021-07-02T12:28:00Z", None), ("Transair 810", "H11S", "2021-07-02T12:27:00Z", None),
 ("Lion Air 904", "H01W", "2013-04-13T07:37:00Z", None), ("Lion Air 904", "H08S", "2013-04-13T07:58:00Z", None),
]
rows = []
for ev, rx, w0, box in PANELS:
    t0, la, lo, src = EV[ev]; _, _, d = g.inv(lo, la, st.loc[rx, "longitude_deg"], st.loc[rx, "latitude_deg"]); rkm = d / 1000
    tp = pd.Timestamp(t0) + pd.Timedelta(seconds=rkm / 1.482); sp = rkm / 1.482 ** 2 * 0.006
    lo_m, hi_m = box if box else (4.0, 6.0); tobs = pd.Timestamp(w0) + pd.Timedelta(minutes=0.5 * (lo_m + hi_m))
    rows.append(dict(event=ev, receiver=rx, range_km=round(rkm, 1), impact_utc=t0, predicted_utc=str(tp.round("s")), predicted_sd_s=round(sp, 1),
                     kadri_box_utc=f"{(pd.Timestamp(w0) + pd.Timedelta(minutes=lo_m)).strftime('%H:%M:%S')}-{(pd.Timestamp(w0) + pd.Timedelta(minutes=hi_m)).strftime('%H:%M:%S')}",
                     box_source="digitised" if box else "window+5 min (Kadri p.11)", obs_minus_pred_s=round((tobs - tp).total_seconds(), 0),
                     box_start_minus_pred_s=round((pd.Timestamp(w0) + pd.Timedelta(minutes=lo_m) - tp).total_seconds(), 0),
                     implied_speed_km_s=round(rkm / (tobs - pd.Timestamp(t0)).total_seconds(), 3), window_contains_prediction=bool(pd.Timestamp(w0) <= tp <= pd.Timestamp(w0) + pd.Timedelta(minutes=10)), source=src))
df = pd.DataFrame(rows); out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); df.to_csv(out / "kadri_crash_timing_EXPLORATORY.csv", index=False)
print(df.drop(columns=["source", "impact_utc"]).to_string())
EOF
python kadri_crash_timing.py ../results-data/calibration_events/stage1b