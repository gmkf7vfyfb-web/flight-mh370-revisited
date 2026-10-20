"""One-off patch of score_case.py for amendment A4 (adopted 20 Oct 2026): the drift stacks (core+drift, all) are scored for a
case only if the pooled D0 core posterior puts >= 0.999 of its mass inside the drift node span. This is a function of the data only,
so the rank statistics of the scored cases stay valid. truth_inside_drift_nodes is recorded as a diagnostic, never as a rule."""
import sys
p = sys.argv[1]; s = open(p).read()
if "A4 data-only drift rule" in s: print("already patched"); sys.exit(0)
old1 = ('        for st, a in (("core", a0), ("core+drift", a0 + ldf), ("core+searches", a0 + cat["ls"]), ("all", a0 + ldf + cat["ls"])):\n'
        '            pooled[f"{d}|{st}"] = stats(Xc, a, T, par)\n')
new1 = old1 + '        if d == "D0": mass_inside = float(wv[~nan_d].sum() / max(wv.sum(), 1e-300))   # A4 data-only drift rule\n'
assert s.count(old1) == 1, "pooled loop not found"
s = s.replace(old1, new1)
old2 = '    res = dict(case=T["case_seed"],'
new2 = ('    drift_scored = bool(mass_inside >= 0.999)\n'
        '    if not drift_scored:\n'
        '        for key in list(pooled):\n'
        '            if "drift" in key or key.endswith("|all"): pooled[key] = None\n'
        '    drift_rule = dict(rule="A4 (adopted 20 Oct 2026): drift stacks scored only if the pooled D0 core posterior mass inside the drift node span is >= 0.999 (data-only)",\n'
        '                      mass_inside_drift_nodes_D0_core=mass_inside, threshold=0.999, drift_scored=drift_scored, truth_inside_drift_nodes_diagnostic=bool(T["truth_inside_drift_nodes"]))\n'
        '    res = dict(drift_rule=drift_rule, case=T["case_seed"],')
assert s.count(old2) == 1, "res dict not found"
s = s.replace(old2, new2)
open(p, "w").write(s); print("patched", p)
