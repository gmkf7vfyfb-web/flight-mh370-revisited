"""Validate output.handoff_epochs snapshots: usage  python check_snap.py <snap_run> [<stop_run>] [prior weights...]"""
import sys, json, numpy as np, glob, os, tomllib
snap = sys.argv[1]; stop = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
run = json.load(open(f"{snap}/run.json"))
prior = np.array(run['config'].get('mode_weights') or [1, 1, 1, 1, 1], float) if isinstance(run['config'], dict) else np.ones(5)
MODES = ['TrueHeading', 'MagneticHeading', 'TrueTrack', 'MagneticTrack', 'LateralNavigation']
worst = 0.0
for rep in run['replicates']:
    seed = rep['seed']; d = f"{snap}/{rep['case']}/seed-{seed}"
    for ep in ['m2241', 'm0011']:
        f = f"{d}/handoff-{ep}/handoff.npy"
        if not os.path.exists(f): continue
        a = np.load(f)
        got = np.array([a[a[:, 6] == m, 0].sum() for m in range(5)])
        # expected: prior weight x exp(evidence to the epoch), from the run's own per-epoch record
        le = []
        for m in rep['modes']:
            if not m['epochs']: le.append(-np.inf); continue
            ids = [e['epoch'] for e in m['epochs']]
            le.append(sum(e['log_evidence_increment'] for e in m['epochs'][:ids.index(ep) + 1]))
        lp = np.log(np.array([m['prior_weight'] for m in rep['modes']])) + np.array(le)
        exp_ = np.exp(lp - np.logaddexp.reduce(lp))
        # rows of a mode carry P(mode) exactly, so their sums equal it to rounding
        err = np.abs(got - exp_).max(); worst = max(worst, err)
        stopinfo = tomllib.load(open(f"{d}/handoff-{ep}/handoff.toml", 'rb'))['stop']
        print(f"seed {seed} {ep}: rows {len(a)} stop {stopinfo} | P(mode) snapshot {np.round(got,6)} | from evidence-to-date {np.round(exp_,6)} | max|diff| {err:.2e} | final_row all NaN {np.isnan(a[:,11]).all()}")
        if stop and ep == 'm0011':
            b = np.load(f"{stop}/{rep['case']}/seed-{seed}/handoff.npy")
            gotb = np.array([b[b[:, 6] == m, 0].sum() for m in range(5)])
            print(f"   stop-run P(mode) {np.round(gotb,6)} max|diff| vs snapshot {np.abs(gotb-got).max():.2e}")
            for name, c in [('lat', 1), ('lon', 2), ('alt_ft', 3), ('mach', 4)]:
                ma, mb = np.average(a[:, c], weights=a[:, 0]), np.average(b[:, c], weights=b[:, 0])
                print(f"   weighted mean {name}: snapshot {ma:.4f} stop-run {mb:.4f}")
print(f"WORST |P(mode) snapshot - evidence-to-date| = {worst:.2e}")
