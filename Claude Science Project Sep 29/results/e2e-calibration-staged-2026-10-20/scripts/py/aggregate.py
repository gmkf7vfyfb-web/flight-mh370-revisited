"""Progress table for the staged calibration run: one row per finished case (truth, D0 ranks and HPD levels per stack, ESS, MC SD).
Usage: aggregate.py RUN_DIR  -> RUN_DIR/progress.csv, RUN_DIR/STATUS.txt"""
import sys, json, glob, os, csv, datetime
run = sys.argv[1]; rows = []
Q = ("u_lat", "u_time", "u_xarc", "hpd2d", "hpd_lat", "p_true_family", "p_true_cause", "ess_parents")
nan = float("nan")
for f in sorted(glob.glob(f"{run}/case-stats/case-*/case-stats.json")):
    S = json.load(open(f)); T = S["truth"]; tcf = f.replace("case-stats.json", "truth-core.json")
    tc = json.load(open(tcf)) if os.path.exists(tcf) else {}
    r = dict(case=S["case"], lat=round(T["impact"]["lat"], 3), lon=round(T["impact"]["lon"], 3), xarc_nm=round(T["impact"]["cross_arc_nm"], 1), family=T["family"], cause=T["cause"],
             bfo_model=T["bfo_model_0019"], ocean=T["ocean_model"], detected=T["search_detected"], truth_in_nodes=T["truth_inside_drift_nodes"],
             logZ=round(tc.get("flight_draw", {}).get("log_Z_chosen", nan), 2), acc_ess=round(tc.get("accepted_ess", nan), 1),
             drift_scored=S.get("drift_rule", {}).get("drift_scored"), mass_in_nodes=round(S.get("drift_rule", {}).get("mass_inside_drift_nodes_D0_core", nan), 4))
    for st in ("core", "core+drift", "core+searches", "all"):
        p = S["pooled"].get(f"D0|{st}"); m = S["mc_sd_between_replicates"].get(f"D0|{st}", {})
        for q in Q: r[f"{st}:{q}"] = round(p[q], 4) if p else None
        r[f"{st}:mcsd_u_lat"] = round(m.get("u_lat", nan), 4) if p else None
    rows.append(r)
if rows:
    with open(f"{run}/progress.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
n = len(rows); main = [r for r in rows if 3001 <= r["case"] <= 3100]
def cov(a, key, lvl):
    v = [r[key] for r in a if r[key] is not None]; return (sum(x < lvl for x in v), len(v))
lines = [f"updated {datetime.datetime.utcnow().isoformat()}Z", f"finished cases: {n} (tier 1a' cases 3001-: {len(main)})"]
for st in ("core", "core+searches", "core+drift", "all"):
    for lvl in (0.5, 0.9, 0.95):
        k, m = cov(main, f"{st}:hpd2d", lvl); lines.append(f"  D0 {st:14s} truth inside {int(lvl*100)}% map region: {k}/{m}")
    u = [r[f"{st}:u_lat"] for r in main if r[f"{st}:u_lat"] is not None]
    if u: lines.append(f"  D0 {st:14s} latitude rank: mean {sum(u)/len(u):.3f}, outside [0.05,0.95]: {sum(x<0.05 or x>0.95 for x in u)}/{len(u)}")
open(f"{run}/STATUS.txt", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
