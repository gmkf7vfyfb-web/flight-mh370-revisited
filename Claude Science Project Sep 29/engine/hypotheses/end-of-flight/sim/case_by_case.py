"""Case-by-case reading of a 6-DOF fit against the ten Boeing engineering-simulator cases (ruling ~18:45 UTC 10 Oct:
the 6-DOF gate; diagnostic smoke 3: Boeing's 8-s window occupancy against our simulator under the same initial
conditions). For each case the fitted flight is re-simulated from the fit's state.json and both traces are measured
by the SAME code (smoke/boeing_calibration.py: measure + window_occupancy), so differences are the model's.

    python case_by_case.py <state.json> <out.json>
Boeing files: validation only, summary statistics only (see boeing_calibration.py header).
"""
import json, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(1, str(pathlib.Path(__file__).resolve().parents[1] / "smoke"))
import fit as F
from model import schedules
from boeing_calibration import measure

F.SCHED = schedules(); tg, data = F.load()
state = json.load(open(sys.argv[1])); shared = state["shared"]
out = {"state": sys.argv[1], "history_last": state["history"][-1] if state["history"] else None, "cases": {}}
for c in sorted(tg):
    fc = state["cases"][c]
    val, rec = F.nll(c, tg, data, shared, fc["nuisance"], fc["law"], fc["tac"], return_rec=True)
    d = data[c]
    b = measure(d["t_s"], d["x_nm"], d["y_nm"], d["alt_ft"])
    s = measure(rec[:, 0], rec[:, 1], rec[:, 2], rec[:, 3])
    # time and distance from the start to the surface (Boeing: end of record)
    b_end = float(d["t_s"][-1]); s_end = float(rec[-1, 0])
    b_dist = float(np.hypot(d["x_nm"][-1] - d["x_nm"][0], d["y_nm"][-1] - d["y_nm"][0]))
    s_dist = float(np.hypot(rec[-1, 1] - rec[0, 1], rec[-1, 2] - rec[0, 2]))
    out["cases"][c] = {"regime": tg[c]["regime"], "law": fc["law"], "tac": fc["tac"], "nll": float(val),
                       "boeing": b, "sixdof": s,
                       "end_time_s": [b_end, s_end], "distance_start_to_end_nm": [b_dist, s_dist],
                       "end_position_error_nm": float(np.hypot(rec[-1, 1] - d["x_nm"][-1], rec[-1, 2] - d["y_nm"][-1]))}
    w_b, w_s = b["windows_8s"] or {}, s["windows_8s"] or {}
    print(c, tg[c]["regime"], "nll %.0f" % val, "end t %d/%d" % (b_end, s_end), "dist %.1f/%.1f" % (b_dist, s_dist),
          "high %s/%s" % (b["high_rate"], s["high_rate"]), "peak fpm %.0f/%.0f" % (b["max_descent_fpm"], s["max_descent_fpm"]),
          "peak g %.2f/%.2f" % (b["max_down_accel_g"], s["max_down_accel_g"]),
          "H2 win %s/%s H1 win %s/%s" % (w_b.get("windows_H2"), w_s.get("windows_H2"), w_b.get("windows_H1"), w_s.get("windows_H1")))
json.dump(out, open(sys.argv[2], "w"), indent=1)
