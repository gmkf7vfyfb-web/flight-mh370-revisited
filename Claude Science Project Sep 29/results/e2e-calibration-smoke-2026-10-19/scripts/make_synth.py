"""Truth descent (protocol 3.2), 00:19 bursts, drift finds and search outcome (3.3) for one case.
Usage: make_synth.py CASE_DIR SEED EOF_RUN_DIR BFO432_CSV FIELDS_NPZ AUDIT_CSV NODE_DIR"""
import sys, json, csv, glob, pathlib
import numpy as np
from scipy.special import logsumexp
from e2e_common import read_rows, write_rows, header_of
from e2e_terms import terms, Search, Drift, FAMNAME


def main():
    cd, seed, eof_run, base_csv, npz, audit, nodes = sys.argv[1:8]; seed = int(seed)
    rng = np.random.default_rng(seed + 77)
    T = json.load(open(f"{cd}/truth-core.json")); ch = T["chosen"]; sdname = pathlib.Path(ch["seed_dir"]).name
    sd = f"{eof_run}/prior/{sdname}"; hnpy = f"{ch['seed_dir']}/handoff-m0011/handoff.npy"
    X = terms(eof_run, sd, hnpy, f"{cd}/obs-dummy.csv")
    sel = X["parent"] == ch["row"]
    lt = X["lw"] + X["surv"] + np.logaddexp(X["c1"], X["c2"])          # D0 total, q = 1/3, C2 silent: prior x log-on-time likelihood
    lt = np.where(sel, lt, -np.inf); ok = np.isfinite(lt)
    if not ok.any(): sys.exit("no descent of the truth parent is compatible with the 00:19 log-on")
    p = np.exp(lt - lt[ok].max()); p[~ok] = 0; p /= p.sum(); ess = 1 / np.sum(p ** 2)
    k = int(rng.choice(len(p), p=p))
    pc1 = float(1 / (1 + np.exp(X["c2"][k] - X["c1"][k]))); cause = "C1" if rng.random() < pc1 else "C2"
    bias = T["bias_hz"]; bmean = float(np.load(hnpy)[ch["row"], 8])
    O = read_rows(base_csv); H = header_of(base_csv); sdv = {r["epoch_id"]: r for r in O}
    zA, zB = float(sdv["m0019a"]["bfo_hz"]), float(sdv["m0019b"]["bfo_hz"])
    predA = zA - X["i1"][k] - bmean; predB = zB - X["i2"][k] - bmean        # BFO without bias (engine: z - innovation - bias mean)
    btoA = float(sdv["m0019a"]["bto_us"]) - X["r600"][k]; btoB = float(sdv["m0019b"]["bto_us"]) - X["r1200"][k]
    u_m = np.random.default_rng([seed, 19]).random(); model = "no-offset" if u_m < 1 / 3 else ("startup-offset" if u_m < 2 / 3 else "inflated")   # own stream: the third draw of rng gave 2 for seeds 9001-9005 (smoke fault S1)
    s1, s2 = float(sdv["m0019a"]["bfo_sd_hz"]), float(sdv["m0019b"]["bfo_sd_hz"])
    if model == "no-offset": oA, oB, e1, e2 = 0.0, 0.0, rng.normal(0, s1), rng.normal(0, s2)
    elif model == "startup-offset":
        o2 = rng.uniform(17, 130); oA, oB, e1, e2 = o2 + rng.uniform(0, 6), o2, rng.normal(0, s1), rng.normal(0, s2)
    else: oA, oB, e1, e2 = 0.0, 0.0, rng.normal(0, 34.0), rng.normal(0, 34.0)
    syn = {"m0019a": dict(bto=btoA + rng.normal(0, float(sdv["m0019a"]["bto_sd_us"])), bfo=predA + bias + oA + e1),
           "m0019b": dict(bto=btoB + rng.normal(0, float(sdv["m0019b"]["bto_sd_us"])), bfo=predB + bias + oB + e2)}
    for r in O:
        e = r["epoch_id"]
        if e in T["epochs"]:
            if r["bto_us"]: r["bto_us"] = f"{T['epochs'][e]['bto_syn']:.4f}"
            if r["bfo_hz"]: r["bfo_hz"] = f"{T['epochs'][e]['bfo_syn']:.6f}"
        elif e in syn:
            r["bto_us"] = f"{syn[e]['bto']:.4f}"; r["bfo_hz"] = f"{syn[e]['bfo']:.6f}"
        r["note"] = "SYNTHETIC e2e calibration smoke"
    write_rows(f"{cd}/obs-synthetic.csv", O, H)
    lat, lon = float(X["lat"][k]), float(X["lon"][k])
    S = Search(npz); pnf = float(S.p_no_find(np.array([lat]), np.array([lon]))[0]); detected = bool(rng.random() > pnf)
    nf = {"glorys12": sorted(glob.glob(f"{nodes}/arclat-glorys12-*-nodes.csv")), "globcurrent": sorted(glob.glob(f"{nodes}/arclat-globcurrent-*-nodes.csv"))}
    Dr = Drift(nf, audit); om = ["glorys12", "globcurrent"][int(rng.integers(2))]
    finds, in_nodes = Dr.simulate(om, lat, rng)
    truth = dict(case_seed=seed, impact=dict(lat=lat, lon=lon, unix_s=float(X["t"][k]), cross_arc_nm=float(X["xarc"][k])),
                 family=FAMNAME.get(float(X["fam"][k]), str(X["fam"][k])), family4_code=float(X["fam"][k]), cause=cause, p_c1_given_descent=pc1,
                 bfo_model_0019=model, bias_hz=bias, ocean_model=om, finds=finds, finds_items=[i for i, _ in Dr.items], items_dropped=Dr.items_dropped,
                 truth_inside_drift_nodes=in_nodes, p_no_find=pnf, search_detected=detected,
                 descent_draw=dict(n_descents_of_parent=int(sel.sum()), ess=float(ess), row=k),
                 route_stratum=ch["name"], core_m0011=T["epochs"]["m0011"], synthetic_0019=syn,
                 pred_0019=dict(btoA=btoA, btoB=btoB, bfoA_nobias=float(predA), bfoB_nobias=float(predB)))
    json.dump(truth, open(f"{cd}/truth.json", "w"), indent=1, default=float)
    print(json.dumps({k_: truth[k_] for k_ in ("impact", "family", "cause", "bfo_model_0019", "ocean_model", "search_detected", "p_no_find", "truth_inside_drift_nodes", "descent_draw")}, default=float))
    print("finds", finds, "items", len(Dr.items), "dropped", Dr.items_dropped)


if __name__ == "__main__":
    main()
