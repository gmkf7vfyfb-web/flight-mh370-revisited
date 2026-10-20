"""F5 check: marginal 00:19 log-on likelihood of the truth's 00:11 parent, Z(parent) = sum_d w_d L_d / sum_d w_d (L = survival x
[p f_lag x C1 constraint + (1-p)/W x C2-silent constraint]), and P(C1 | parent). The smoke truth draw picked the parent WITHOUT Z(parent)
(stage 1 used the fuel-only weight; stage 2 picked a descent within the parent by L), so parents that explain the log-on poorly are over-drawn.
Usage: parent_check.py CASE_DIR"""
import sys, json, numpy as np, pathlib
from scipy.special import logsumexp
from e2e_terms import terms
cd = sys.argv[1]; T = json.load(open(f"{cd}/truth-core.json")); ch = T["chosen"]; sdn = pathlib.Path(ch["seed_dir"]).name
X = terms(f"{cd}/truth-eof", f"{cd}/truth-eof/prior/{sdn}", f"{ch['seed_dir']}/handoff-m0011/handoff.npy", f"{cd}/obs-dummy.csv")
out = {}
for r in np.unique(X["parent"]):
    s = X["parent"] == r; lw = X["lw"][s] - logsumexp(X["lw"][s])
    l1 = lw + X["surv"][s] + X["c1"][s]; l2 = lw + X["surv"][s] + X["c2"][s]
    lz = float(np.logaddexp(logsumexp(l1), logsumexp(l2))); p1 = float(np.exp(logsumexp(l1) - lz))
    out[int(r)] = dict(log_Z_parent=lz, p_C1_given_parent=p1, chosen=bool(r == ch["row"]))
print(json.dumps({"case": cd, "parents": out, "reference": {"log_Z_if_C1_at_lag_mode": float(np.log(0.75) + np.log(1/120.0)), "log_Z_if_C2_only": float(np.log(0.25) - np.log(3898.0))}}, indent=1))
