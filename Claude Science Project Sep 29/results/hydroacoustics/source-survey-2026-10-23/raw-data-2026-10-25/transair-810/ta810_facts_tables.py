"""NTSB primary facts and path geometry tables for Transair 810 (values copied from the docket texts read in this
session; each row names its document). Geometry recomputed with pyproj WGS84."""
import pathlib, sys, pandas as pd, numpy as np
from pyproj import Geod
WS = pathlib.Path(__file__).resolve().parent.parent; G = Geod(ellps="WGS84")
F = [
 ("accident number", "DCA21FA174", "NTSB final report (CAROL, 45 pp.) cover table", "Aviation Safety Network record; Wikipedia"),
 ("water impact time", "01:45:17 HST = 11:45:17 UTC", "final report p.18: CVR 'sounds consistent with impact at 0145:17'", "APG study: ADS-B ends 11:45:17.902 UTC; FDR CSV ends 01:45:16.94 HST"),
 ("impact position (ADS-B)", "21.27616 N, 158.02565 W", "Aircraft Performance Group study, Table 4, row 'Estimated water impact'", "Wikipedia 21.275 N 158.026 W; wreck (fwd fuselage) 21 16'39.40\"N 158 01'30.79\"W, 167 m away (S&R factual Table 1)"),
 ("groundspeed at impact", "114.6 kt (58.96 m/s)", "APG Table 4 (ADS-B)", "Kadri S1 'about 215 km/h' = 59.7 m/s"),
 ("calibrated airspeed", "123 kt", "APG Table 4", "EGPWS factual: CAS decreasing ~160 -> 122 kt over the last 3 min 37 s"),
 ("vertical speed at contact", "ADS-B -764 fpm (3.9 m/s); EGPWS radio altitude 55.0 -> 42.5 -> 26.5 ft at 1-s steps (3.8, 4.9 m/s)", "APG Table 4; EGPWS specialist factual App. A", "modelled U(3.8, 6.5) m/s (extrapolation over ~1-1.5 s at ~1-2 m/s^2)"),
 ("attitude", "pitch +12.3 deg, bank -14.9 deg (left wing down), magnetic heading 6.1 deg", "APG Table 4 (FDR)", "flaps 1, gear up (APG s.5)"),
 ("weight", "takeoff 93,557 lb (42.44 t); basic empty 59,720 lb; fuel 14,000 lb; cargo 19,897 lb", "final report, weight and balance section; APG Table 1", "impact mass 42.0 t (TOW less 300-1,500 lb burned, declared)"),
 ("water depth", "wreck 340-364 ft (104-111 m)", "Search & Recovery factual Table 1", "GEBCO_2026: 117 m at wreck, 108-178 m at the ADS-B impact point (steep slope)"),
 ("break-up", "fuselage fractured near BS 540 (forward spar): two pieces; both engines separated; wings attached; tail floated, then sank", "S&R factual pp. 10-11; final report, wreckage section", "first officer saw two pieces on egress (survival factual); b737.org.uk"),
 ("Kadri S1 position", "21 18'41\"N 157 54'16\"W (21.3114 N, 157.9044 W): near HNL airport, 13 km from the NTSB point", "Kadri 2024 S1 p.2", "Kadri S1 ref 5 is the Atlas Air 3591 report (AAR2201), not Transair"),
]
pd.DataFrame(F, columns=["item", "value", "primary_source", "cross_check"]).to_csv(WS / "out/tables/ntsb_primary_facts.csv", index=False)
st = pd.read_csv(WS / "data/transair_H11_resp.xml".replace("transair_H11_resp.xml", "download_log.csv"))
from obspy import read_inventory
inv = read_inventory(str(WS / "data/transair_H11_resp.xml")); SRC = (21.27616, -158.02565); rows = []
for net in inv:
    for sta in net:
        ch = sta[0]; az, _, d = G.inv(ch.longitude, ch.latitude, SRC[1], SRC[0]); tt = d / 1e3 / 1.482
        rows.append(dict(element=sta.code, lat=ch.latitude, lon=ch.longitude, depth_m=-ch.elevation, dist_km=d / 1e3, back_azimuth_deg=az % 360, tt_s=tt, tt_sd_s=d / 1e3 / 1.482 ** 2 * 0.006,
                         arrival_utc=(pd.Timestamp("2021-07-02T11:45:17Z") + pd.Timedelta(seconds=tt)).strftime("%H:%M:%S.%f")[:-4]))
pd.DataFrame(rows).round(4).to_csv(WS / "out/tables/arrival_geometry.csv", index=False); print(pd.DataFrame(rows).round(3).to_string())
