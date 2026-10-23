cd leg; cp /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/*/vb051343e*royer_table5.json out/royer_table5.json 2>/dev/null || python -c "print('nf')"; ls out/royer_table5.json; cat > royer_fit.py <<'EOF'
"""Royer (2016, LDO-201608) events and picks against the corrected Kadri locality L, branches T and C (exploratory:
this comparison was not pre-registered as a statistic; it answers the task's question and is labelled exploratory).
Inputs: Royer Table 4 (typed from the PDF, pp. 14), Table 5 (royer_table5.json, artifact b051343e), windows from geometry_windows."""
import sys, json; sys.path.insert(0, "."); import numpy as np, pandas as pd
from geographiclib.geodesic import Geodesic; Gd = Geodesic.WGS84
from geometry_windows import H01W, AZ, R7, HX, T_RX, ST, pos, dist, C, DC, PICK
OUT = sys.argv[1]
s = lambda x: sum(float(a) * m for a, m in zip(x.split(":"), (3600, 60, 1)))
T4 = [(1,"Icequake","23:47:46.2",-55.400,88.173,11.348),(2,"Uncertain","00:13:09.3",-64.510,127.048,99.999),(3,"A icequake","00:16:29.4",-57.300,88.965,3.221),
      (4,"B","00:21:30.6",-35.224,99.922,1.533),(5,"Uncertain","00:28:51.5",-49.755,133.114,61.139),(6,"Uncertain","00:32:49.2",-66.090,127.043,0.334),
      (7,"C1 Unc.","00:33:43.5",-3.445,74.087,7.447),(8,"Uncertain","00:36:21.8",-60.844,78.097,15.099),(9,"Uncertain","00:37:52.4",-48.671,97.477,1.583),
      (10,"Icequake","00:56:45.5",-57.967,92.050,21.666),(11,"C2 Unc.","00:57:32.4",-26.469,80.952,2.075),(12,"C3 Unc.","00:57:33.5",-26.539,80.979,6.929),
      (13,"C4 Unc.","00:59:55.3",-55.719,87.615,46.771),(14,"D1 Unc.","01:04:39.1",-25.404,93.567,3.448),(15,"D2 Unc.","01:06:05.4",-27.856,93.460,1.439),
      (16,"Earthquake","01:15:48.0",-8.052,107.622,4.706),(17,"Icequake","01:37:39.5",-57.950,95.354,3.468),(18,"Icequake","01:49:33.0",-52.635,80.389,10.832),
      (19,"Icequake","01:58:14.2",-51.322,117.339,33.969),(20,"Earthquake","02:02:31.7",-27.149,67.307,3.426)]
T5 = json.load(open("out/royer_table5.json"))
XING = pos(AZ, R7["bto"]); IMPACT = {"T": (s("00:32:00"), s("00:34:24")), "C": (s("00:34:06"), s("00:36:51"))}
ev = []
for i, typ, t, la, lo, et in T4:
    ts = s(t) - (86400 if t.startswith("23") else 0)
    g = Gd.Inverse(H01W[0], H01W[1], la, lo); az, r = g["azi1"] % 360, g["s12"] / 1e3
    in_strip = abs(az - AZ) <= 1.0 and R7["bto"] - 60 <= r <= R7["bto"] + 250
    h = [float(np.mean([s(T5[str(i)][k]) for k in ("H01W1", "H01W2", "H01W3")]))] if T5[str(i)]["H01W1"] != "X" else [np.nan]
    ev.append(dict(event=i, type=typ, origin_utc=t, lat=la, lon=lo, err_time_s=et, h01w_az=round(az, 2), h01w_range_km=round(r),
                   km_to_crossing=round(dist((la, lo), XING)), km_to_haixun=round(dist((la, lo), HX)), in_strip=in_strip,
                   in_any_disc_400km=min(dist((la, lo), XING), dist((la, lo), HX)) <= 400,
                   origin_in_T_impact_range=IMPACT["T"][0] <= ts <= IMPACT["T"][1], origin_in_C_impact_range=IMPACT["C"][0] <= ts <= IMPACT["C"][1],
                   h01w_pick_mean_utc=(f"{int(h[0]//3600):02d}:{int(h[0]%3600//60):02d}:{h[0]%60:05.2f}" if np.isfinite(h[0]) else "X"),
                   h01w_minus_T_s=round(h[0] - T_RX["T"], 1) if np.isfinite(h[0]) else np.nan, h01w_minus_C_s=round(h[0] - T_RX["C"], 1) if np.isfinite(h[0]) else np.nan,
                   h01w_plus16_minus_T_s=round(h[0] + 16 - T_RX["T"], 1) if np.isfinite(h[0]) else np.nan, h01w_plus16_minus_C_s=round(h[0] + 16 - T_RX["C"], 1) if np.isfinite(h[0]) else np.nan))
E = pd.DataFrame(ev); E.to_csv(f"{OUT}/royer_events_vs_L.csv", index=False)
# OHASISBIO picks inside L windows
W = pd.read_csv(f"{OUT}/arrival_windows.csv"); MAP = {"MAD": "OHAS_MAD", "NCRO": "OHAS_NCRO", "WKER": "OHAS_WKER", "SSEIR": "OHAS_SSEIR", "SWAMS1": "OHAS_SWAMS1", "SWAMS2": "OHAS_SWAMS2", "SWAMS3": "OHAS_SWAMS3"}
picks = [(int(k), st, s(v)) for k, d in T5.items() for st, v in d.items() if st in MAP and v != "X"]
hits = []
for (br, ss), g in W.groupby(["branch", "source_set"]):
    for _, r in g.iterrows():
        for k, st, t in picks:
            if MAP[st] == r.station and r.window_start_s <= t <= r.window_end_s:
                hits.append(dict(branch=br, source_set=ss, station=st, royer_event=k, pick_utc=T5[str(k)][st], window=f"{r.window_start}-{r.window_end}", offset_from_centre_s=round(t - r.centre_s, 1)))
H = pd.DataFrame(hits); H.to_csv(f"{OUT}/royer_picks_in_L_windows.csv", index=False)
# chance rate per SITE from Royer's own pick density (clusters merged within 30 s; SWAMS1-3 = one site)
site = lambda st: "SWAMS" if st.startswith("SWAMS") else st
rate = {}
for S_ in ("MAD", "NCRO", "WKER", "SSEIR", "SWAMS"):
    t = np.sort([p[2] for p in picks if site(p[1]) == S_]); cl = [t[0]] if len(t) else []
    for x in t[1:]:
        if x - cl[-1] > 30: cl.append(x)
    span = s("02:05:00") + 3600 * 1.0 - s("00:00:00")   # picks span 00:06-03:02; use 00:00-03:05 conservatively below
    span = max(t.max() - t.min(), 1.0) if len(t) > 1 else np.nan
    rate[S_] = dict(n_clusters=len(cl), span_s=float(span), rate_per_s=len(cl) / span if span == span else np.nan)
chance = []
for br in ("T", "C"):
    for ss in ("crossing_core", "haixun", "eq4_strip_core", "locality_strip_wide"):
        for S_, stn in (("MAD", "OHAS_MAD"), ("NCRO", "OHAS_NCRO"), ("WKER", "OHAS_WKER"), ("SSEIR", "OHAS_SSEIR"), ("SWAMS", "OHAS_SWAMS3")):
            r = W[(W.branch == br) & (W.source_set == ss) & (W.station == stn)].iloc[0]
            lam = rate[S_]["rate_per_s"] * r.width_s
            obs = int(((H.branch == br) & (H.source_set == ss) & (H.station.map(site) == S_)).any()) if len(H) else 0
            chance.append(dict(branch=br, source_set=ss, site=S_, window_s=round(r.width_s, 1), expected_clusters=round(lam, 3), p_at_least_one=round(1 - np.exp(-lam), 3), observed_hit=obs))
CH = pd.DataFrame(chance); CH.to_csv(f"{OUT}/royer_chance_rates.csv", index=False)
# joint single-point fit for C and T on the strip using any in-window picks (exploratory)
fits = []
grid = [(a, R7["bto"] + d) for a in np.linspace(AZ - 1, AZ + 1, 21) for d in np.arange(-60, 251, 2)]
for br in ("T", "C"):
    hb = H[(H.branch == br) & (H.source_set == "locality_strip_wide")]
    if not len(hb): continue
    for combo_site, sub in hb.groupby(hb.station.map(site)):
        pass
    best = None
    # use, per site, the in-window pick nearest the crossing centre
    sel = {}
    for _, r in hb.iterrows():
        k = site(r.station); c = sel.get(k)
        if c is None or abs(r.offset_from_centre_s) < abs(c.offset_from_centre_s): sel[k] = r
    for a, rr in grid:
        p = pos(a, rr); chi = 0.0; res = {}
        for k, r in sel.items():
            la, lo, *_ = ST[MAP[r.station]]; dd = dist(p, (la, lo)) - rr; sig = np.hypot(abs(dd) * DC / C ** 2, PICK)
            tp = T_RX[br] + dd / C; res[k] = s(r.pick_utc) - tp; chi += (res[k] / sig) ** 2
        if best is None or chi < best[0]: best = (chi, a, rr, p, res)
    pred = {}
    for stn in ("OHAS_MAD", "OHAS_NCRO", "OHAS_WKER", "OHAS_SSEIR", "OHAS_SWAMS3", "H08S", "PerthCanyon_3376"):
        la, lo, *_ = ST[stn]; t = T_RX[br] + (dist(best[3], (la, lo)) - best[2]) / C; pred[stn] = f"{int(t//3600):02d}:{int(t%3600//60):02d}:{t%60:04.1f}"
    fits.append(dict(branch=br, picks_used={k: f"event {int(v.royer_event)} {v.station} {v.pick_utc}" for k, v in sel.items()}, n_sites=len(sel),
                     chi2=round(best[0], 2), az=round(best[1], 2), range_km=round(best[2], 1), lat=round(best[3][0], 3), lon=round(best[3][1], 3),
                     residuals_s={k: round(v, 1) for k, v in best[4].items()}, predicted_other_sites=pred))
json.dump(dict(rate=rate, fits=fits), open(f"{OUT}/royer_fit.json", "w"), indent=1, default=str)
print(E[["event", "type", "origin_utc", "km_to_crossing", "in_strip", "in_any_disc_400km", "origin_in_T_impact_range", "origin_in_C_impact_range", "h01w_pick_mean_utc", "h01w_minus_T_s", "h01w_plus16_minus_T_s", "h01w_minus_C_s", "h01w_plus16_minus_C_s"]].to_string(index=False))
print(H.to_string(index=False)); print(json.dumps(rate)); print(CH.groupby(["branch", "source_set"])[["expected_clusters", "observed_hit"]].sum().to_string())
print(json.dumps(fits, indent=1, default=str))
EOF
python royer_fit.py out 2>&1 | grep -v -i proj