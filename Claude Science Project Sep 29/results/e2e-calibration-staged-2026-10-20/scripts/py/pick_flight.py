"""S2 fix: choose the truth flight among the flown candidates with weight x Z(parent), where Z(parent) is the marginal 00:19
log-on likelihood of the candidate's hand-off row (survival x [C1 fuel-exhaustion term + C2-silent term], q = 1/3), from the
end-of-flight stage that flew every candidate. make_synth.py then draws the descent within the chosen parent with weight x L,
so (flight, descent) is drawn jointly from prior x log-on likelihood. Writes CASE_DIR/truth-core.json in pick_truth.py's schema.
Usage: pick_flight.py CASE_DIR"""
import sys, json
import numpy as np
from scipy.special import logsumexp
from e2e_terms import terms


def main():
    cd = sys.argv[1]; C = json.load(open(f"{cd}/truth-candidates.json")); run = f"{cd}/truth-eof"
    rng = np.random.default_rng([C["case_seed"], 5])
    lz = np.full(len(C["candidates"]), -np.inf); pc1 = np.full(len(C["candidates"]), np.nan); nd = np.zeros(len(C["candidates"]), int)
    for i, c in enumerate(C["candidates"]):
        try:
            X = terms(run, f"{run}/prior/seed-{c['seed']}", f"{c['seed_dir']}/handoff-m0011/handoff.npy", f"{cd}/obs-dummy.csv")
        except Exception as e:
            c["eof_error"] = str(e)[:200]; continue
        s = X["parent"] == c["row"]; nd[i] = int(s.sum())
        if not s.any(): continue
        lw = X["lw"][s] - logsumexp(X["lw"][s]); l1 = lw + X["surv"][s] + X["c1"][s]; l2 = lw + X["surv"][s] + X["c2"][s]
        a1, a2 = logsumexp(l1), logsumexp(l2)
        if np.isfinite(a1) or np.isfinite(a2): lz[i] = float(np.logaddexp(a1, a2)); pc1[i] = float(np.exp(a1 - lz[i]))
    lwt = np.log([c["wt"] for c in C["candidates"]]) + lz; ok = np.isfinite(lwt)
    if not ok.any(): sys.exit("no candidate flight has a finite 00:19 log-on likelihood")
    p = np.exp(lwt - lwt[ok].max()); p[~ok] = 0; p /= p.sum(); ess = float(1 / np.sum(p ** 2)); k = int(rng.choice(len(p), p=p))
    c = C["candidates"][k]; fin = lz[np.isfinite(lz)]
    res = dict(case_seed=C["case_seed"], generator="pool+joint (A2, S2 fix, 20 Oct 2026)", pool=C["pool"], n_candidates=C["n_candidates"], candidate_ess=C["candidate_ess"],
               data_event=C["data_event"], n_accepted=C["n_accepted"], accepted_ess=C["accepted_ess"], event_rate_weighted=C["event_rate_weighted"],
               flight_draw=dict(n_flown=len(lz), n_finite_Z=int(np.isfinite(lz).sum()), ess_weight_times_Z=ess, log_Z_chosen=float(lz[k]), p_C1_given_chosen_parent=float(pc1[k]),
                                n_descents_chosen_parent=int(nd[k]), log_Z_quantiles_10_50_90=[float(q) for q in np.quantile(fin, [0.1, 0.5, 0.9])] if len(fin) else None,
                                log_Z_weighted_mean=float(np.sum(p[ok] * lz[ok]))),
               chosen=dict(seed_dir=c["seed_dir"], seed=c["seed"], stratum=c["stratum"], name=c["name"], row=c["row"], log_w=c["log_w"], wt=c["wt"]),
               bias_hz=c["bias_hz"], epochs=c["epochs"], handoff_row=c["handoff_row"])
    json.dump(res, open(f"{cd}/truth-core.json", "w"), indent=1)
    print(json.dumps({q: v for q, v in res.items() if q not in ("epochs", "handoff_row")}))


if __name__ == "__main__":
    main()
