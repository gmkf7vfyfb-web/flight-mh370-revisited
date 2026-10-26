"""Independent checks for the review of the Kadri (2024, Sci. Rep. 14:10102) comparison. 26 Oct 2026.
POST-HOC (not pre-registered). Inputs: IMS element coordinates (EarthScope FDSN station service),
primary impact times and positions (KNKT, NTSB, press for AB 1103), Kadri box times as digitised by the
replication track (kadri_timing_checks.csv), ETOPO1 bathymetry (NOAA ERDDAP etopo180, 2-arcmin stride).
Outputs: review_geometry.csv, review_mixed_path.csv, review_inter_triad.csv."""
import io, requests, numpy as np, pandas as pd
from datetime import datetime, timedelta
from geographiclib.geodesic import Geodesic
from scipy.interpolate import RegularGridInterpolator
from obspy.taup import TauPyModel
G = Geodesic.WGS84
def dms(d, m, s, sg=1): return sg * (d + m / 60 + s / 3600)
url = "https://service.iris.edu/fdsnws/station/1/query"
cent = {}
for sta, date in [("H11N", "2021-07-02"), ("H11S", "2021-07-02"), ("H08S", "2021-01-09"), ("H01W", "2014-12-27")]:
    r = requests.get(url, params=dict(net="IM", sta=sta + "?", cha="EDH", level="channel", format="text",
                                      starttime=date, endtime=date + "T23:59:59"), timeout=60)
    d = pd.read_csv(io.StringIO(r.text), sep="|"); d.columns = [c.strip("# ").strip() for c in d.columns]
    cent[sta] = (d.Latitude.mean(), d.Longitude.mean())
T = datetime.fromisoformat
cases = [  # case, station, primary impact time, primary position, Kadri box start, box end, raw-data peak in box
 ("F-35A", "H11N", T("2019-04-09T10:26:30"), (40.64, 142.96), "11:02:15", "11:03:41", "11:03:05.5"),
 ("F-35A", "H11S", T("2019-04-09T10:26:30"), (40.64, 142.96), "11:03:22", "11:04:48", "11:04:07.0"),
 ("Transair 810", "H11N", T("2021-07-02T11:45:18"), (21.275, -158.026), "12:32:14", "12:33:40", "12:32:56.0"),
 ("Transair 810", "H11S", T("2021-07-02T11:45:18"), (21.275, -158.026), "12:31:12", "12:32:39", "12:31:42.5"),
 ("Sriwijaya 182", "H08S", T("2021-01-09T07:40:28"), (dms(5, 57, 56.21, -1), dms(106, 34, 24.86)), "08:10:35", "08:12:00", "08:11:20.0"),
 ("AB Aviation 1103", "H08S", T("2022-02-26T09:30:00"), (-12.282, 43.750), "09:40:37", "09:42:05", "09:41:10.5"),
 ("AirAsia 8501", "H01W", T("2014-12-27T23:20:35"), (dms(3, 37, 19, -1), dms(109, 42, 41)), "23:55:06", "23:56:44", "23:55:43.7"),
]
tp = TauPyModel("iasp91"); out = []
for name, sta, t0, pos, b0, b1, pk in cases:
    g = G.Inverse(pos[0], pos[1], *cent[sta]); d = g["s12"] / 1e3; baz = (g["azi2"] + 180) % 360
    def at(s):
        h, m, sec = s.split(":"); tt = t0.replace(hour=int(h), minute=int(m), second=0, microsecond=0) + timedelta(seconds=float(sec))
        if tt < t0 - timedelta(hours=1): tt += timedelta(days=1)
        return (tt - t0).total_seconds()
    tb0, tb1, tpk = at(b0), at(b1), at(pk)
    arr = tp.get_travel_times(source_depth_in_km=0.1, distance_in_degree=d / 111.195, phase_list=["P", "S"])
    out.append(dict(case=name, station=sta, range_km=round(d, 1), expected_bearing_deg=round(baz, 1),
        water_1p57_s=round(d / 1.57), water_1p48_s=round(d / 1.48), water_1p45_s=round(d / 1.45),
        all_path_3p55_s=round(d / 3.55), S_iasp91_s=round(min(a.time for a in arr if a.name == "S")),
        P_iasp91_s=round(min(a.time for a in arr if a.name == "P")),
        box_start_s=round(tb0), box_end_s=round(tb1), peak_s=round(tpk),
        implied_speed_km_s=round(d / tpk, 3), peak_minus_water_1p48_s=round(tpk - d / 1.48)))
geo = pd.DataFrame(out); geo.to_csv("review/review_geometry.csv", index=False)
tri = []
for name in ["F-35A", "Transair 810"]:
    gN = geo[(geo.case == name) & (geo.station == "H11N")].iloc[0]; gS = geo[(geo.case == name) & (geo.station == "H11S")].iloc[0]
    tri.append(dict(case=name, predicted_tN_minus_tS_s=round((gN.range_km - gS.range_km) / 1.48, 1),
                    kadri_boxes_tN_minus_tS_s=gN.box_start_s - gS.box_start_s, raw_peaks_tN_minus_tS_s=gN.peak_s - gS.peak_s))
pd.DataFrame(tri).to_csv("review/review_inter_triad.csv", index=False)
def etopo(lat0, lat1, lon0, lon1, stride=2):
    u = f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.csv?altitude%5B({lat0}):{stride}:({lat1})%5D%5B({lon0}):{stride}:({lon1})%5D"
    d = pd.read_csv(io.StringIO(requests.get(u, timeout=300).text), skiprows=[1])
    la = np.sort(d.latitude.unique()); lo = np.sort(d.longitude.unique())
    return RegularGridInterpolator((la, lo), d.pivot(index="latitude", columns="longitude", values="altitude").loc[la, lo].values, bounds_error=False)
boxes = {"Sriwijaya 182": (-10, -4, 71, 108, "H08S", cases[4][3]), "AirAsia 8501": (-36, -2, 108, 117, "H01W", cases[6][3]),
         "AB Aviation 1103": (-14, -6, 42, 74, "H08S", cases[5][3])}
rows = []
for name, (a, b, c, e, sta, p0) in boxes.items():
    f = etopo(a, b, c, e); l = G.InverseLine(p0[0], p0[1], *cent[sta]); n = int(l.s13 / 2e3) + 1
    pts = [l.Position(i * l.s13 / (n - 1)) for i in range(n)]; ds = l.s13 / 1e3 / (n - 1)
    z = f(np.c_[[p["lat2"] for p in pts], [(p["lon2"] + 180) % 360 - 180 for p in pts]]); L = n * ds
    g = geo[geo.case == name].iloc[0]
    for thr in [0, -200, -1000]:
        Lf = float(np.sum(z > thr) * ds)
        for vf, vw in [(3.55, 1.48), (8.0, 1.48), (8.0, 1.57)]:
            t = Lf / vf + (L - Lf) / vw
            rows.append(dict(case=name, fast_where_shallower_than_m=-thr, fast_km=round(Lf), v_fast_km_s=vf, v_water_km_s=vw,
                predicted_s=round(t), box_start_s=g.box_start_s, box_end_s=g.box_end_s, box_end_minus_predicted_s=round(g.box_end_s - t),
                km_fast_needed_for_box_end=round((g.range_km / vw - g.box_end_s) / (1 / vw - 1 / vf))))
pd.DataFrame(rows).to_csv("review/review_mixed_path.csv", index=False)
print(geo.to_string()); print(pd.DataFrame(tri).to_string())
