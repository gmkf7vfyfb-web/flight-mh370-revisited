
import os, sys, json, numpy as np, pandas as pd, time
WS = os.getcwd()
MOD = os.path.join(WS, "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics")
PREP = os.path.join(MOD, "prepare")
for p in [PREP, PREP+"/composition_run_j", PREP+"/searches_run_j"]:
    sys.path.insert(0, p)
import prereg as RC
import common as CM
import preregistration as RS, detectors as D, common_rows as CR
import imos_noise as N, imos_preregistration as P
import run_j_windows as W
t0=time.time()
M = CM.Machinery(imos_ramgrid=True)
print(round(time.time()-t0,1), M.ramgrid_covered_share, M.rxpos)
SR = "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches"
pairs = pd.read_csv(f"{SR}/coincidence/pairs.csv", dtype={"rx_a":str,"rx_b":str})
ic = pd.read_csv(f"{SR}/imos/imos_candidates.csv", dtype={"receiver":str})
pc = pd.read_csv(f"{SR}/panels/panel_candidates.csv")
print(pairs.family.value_counts().to_dict())
pm = pairs[pairs.family=="primary_M1b"].sort_values("max_p")
print(pm[["rx_a","rx_b","t_a","p_a","t_b","p_b","lag_s","max_p","p_perm"]].head(10).to_string())
