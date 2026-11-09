"""Build the paper summary table from results/eof-results-metrics-davey-fuel.csv and data/eof-treatments.csv.
Adds 90 % region areas for the waypoint model (same arc-aligned method). Run from any folder: python make_tables.py"""
import os, json, numpy as np, pandas as pd
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eofmaps as E
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "..", "results"); DATA = os.path.join(HERE, "..", "data")
M = pd.read_csv(os.path.join(RES, "eof-results-metrics-davey-fuel.csv")).set_index("code")
T = pd.read_csv(os.path.join(DATA, "eof-treatments.csv"))
TW = T[T["route family"] == "Waypoints"].set_index("code")
KEY = ["D13", "D7", "D8", "D9", "D10", "D11"]
# waypoint 90 % areas, same density method
Zw = E.load("wp"); aw = {}
for D in KEY:
    w = E.weights(Zw, D); p = E.density(Zw, w); aw[D] = E.hpd_area_km2(p, 0.9)
LNB = {"D9": "0 (reference)", "D10": "+0.31 (+0.18 to +0.46)", "D11": "−0.43 (−0.60 to −0.27)"}
rows = []
for D in KEY:
    m = M.loc[D]
    rows.append({
        "Treatment of the 00:19 data": m["treatment"],
        "Effective samples": f"{m['effective_samples_run']:,.0f}",
        "ln B against both BFOs as observed (90 % seed interval)": LNB.get(D, "not compared (different data)"),
        "Median impact latitude (°S)": f"{-m['latitude_q50']:.1f}",
        "Median impact latitude, waypoint model (°S)": f"{-TW.loc[D, 'latitude q50']:.1f}",
        "90 % region area (km²)": f"{round(m['area90_km2'], -3):,.0f}",
        "90 % region area, waypoint model (km²)": f"{round(aw[D], -3):,.0f}",
        "Within 25 NM of the 7th arc (%)": f"{100 * m['within_25nm']:.0f}",
        "95th percentile distance from the 7th arc (NM)": f"{m['abs_distance_q95_nm']:.0f}",
        "Median time from 00:19:29 to impact (min)": f"{m['minutes_to_impact_q50']:.1f}",
        "Median impact kinetic energy (GJ)": f"{m['energy_gj_q50']:.1f}",
        "Inside the previously searched area (coverage only, %)": f"{100 * m['inside_previously_searched_area']:.0f}",
        "Mapped": "no (effective samples below 1,000)" if m["effective_samples_run"] < 1000 else "yes"})
S = pd.DataFrame(rows); S.to_csv(os.path.join(RES, "eof-results-summary-table.csv"), index=False)
json.dump({D: aw[D] for D in KEY}, open(os.path.join(RES, "area90-km2-waypoint-model.json"), "w"), indent=1)
print(S.T.to_string())
