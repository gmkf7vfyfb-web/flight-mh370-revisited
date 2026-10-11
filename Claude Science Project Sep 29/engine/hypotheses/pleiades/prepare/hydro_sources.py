"""Source packages for the hydroacoustic test of the Pléiades hypothesis, the module's own builder (port of the adopted stand-in's
results/pleiades/hydro-test/standin-scripts/build_columns.py, section "source packages", to the run C compact format and v2 columns).

Per 00:19 option: 5,000 impacts drawn from the defensive mixture 1/2 flight posterior + 1/2 posterior under H (P + all four COSMO,
both ocean models), strata mixed by end of flight's 00:19-re-weighted P(family) (fixed beside), with the full impact state, the
Pléiades columns and the importance weights w_flight, w_H (and *_fixed) relative to the mixture, plus their ESS.

    python hydro_sources.py <impacts root> <v2 columns dir> [--options none+unpowered,...]
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import branch_eof289 as B  # noqa: E402
import closeup_styles as cs  # noqa: E402
import compact_eval as ce  # noqa: E402
from build_columns import VALS  # noqa: E402

N_SOURCES, RNG_SEED = 5000, 20261012
SLUG = {"none": "0019-held-out", "r600-bto": "0019-r600-bto-only", "r600/no-offset": "0019-r600-bto-raw-bfo"}


def option_weights(sd, option):
    """branch_eof289.histograms' weight branch (either impact format), normalised per seed."""
    cols, g, _ = ce.seed_reader(sd)
    opt_, _, cause = option.partition("@")
    base, _, con = opt_.partition("+")
    if (cause and cause != "other") or f"loglik:{base}" not in cols:
        w = B.eof_option_weights(sd, base, cause or "other", con)
    else:
        w = g("weight") * np.exp(g(f"loglik:{base}"))
        if con:
            w = w * np.exp(B.eof_constraint(sd, g, con))
    w = np.where(np.isfinite(w), w, 0.0)
    return w / w.sum()


def ess(x):
    return float(x.sum() ** 2 / (x ** 2).sum()) if x.sum() > 0 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imp"); ap.add_argument("cols")
    ap.add_argument("--options", default="none+unpowered,r600-bto+unpowered,r600/no-offset+unpowered")
    a = ap.parse_args()
    IMP, OUT = Path(a.imp), Path(a.cols)
    strata = sorted(d.name for d in IMP.iterdir() if d.is_dir() and ce.seed_dirs(d))
    fe = next(iter(sorted((IMP / "summary").glob("family-evidence-*.json"))), None)
    assert fe, "end of flight's family-evidence file is needed for P(family)"
    F = json.loads(fe.read_text()); pcore = F["p_core"]
    summary = dict(family_evidence=str(fe), p_core=pcore, sources=[])
    for o in a.options.split(","):
        pr = cs.reweighted_pfam(str(fe), o)
        pf = {"reweighted": {s: (pr or pcore)[s] for s in strata}, "fixed": {s: pcore[s] for s in strata}}
        keys = [(s, sd) for s in strata for sd in ce.seed_dirs(IMP / s)]
        nseed = {s: sum(1 for ss, _ in keys if ss == s) for s in strata}
        pw, Lb, mH = {}, {}, {k: {} for k in pf}
        for key in keys:
            s, sd = key
            pw[key] = option_weights(sd, o)
            R = np.load(OUT / s / sd.name / "pleiades-lnL.npy", mmap_mode="r")
            Lb[key] = np.where(R["not_computed"].astype(bool), 0.0, np.exp(np.asarray(R["lnL_both_mean"], float)))
            for kind in pf:
                mH[kind][key] = pf[kind][s] / nseed[s] * float((pw[key] * Lb[key]).sum())
        ZH = {kind: sum(mH[kind].values()) for kind in pf}
        rng = np.random.default_rng(RNG_SEED)
        nh = N_SOURCES // 2
        mF = np.array([pf["reweighted"][s] / nseed[s] for s, _ in keys])
        cF = rng.multinomial(nh, mF / mF.sum())
        cH = rng.multinomial(N_SOURCES - nh, np.array([mH["reweighted"][k] for k in keys]) / ZH["reweighted"])
        rows = []
        for j, key in enumerate(keys):
            p = pw[key]
            for comp, cnt, prob in ((0, cF[j], p), (1, cH[j], p * Lb[key])):
                if cnt:
                    idx = rng.choice(len(p), size=cnt, replace=True, p=prob / prob.sum())
                    rows += [(j, int(i), comp) for i in idx]
        rows.sort()
        kj, ri, comp = (np.array(x) for x in zip(*rows))
        qF = {k: np.empty(len(ri)) for k in pf}; qH = {k: np.empty(len(ri)) for k in pf}
        lnl = {x: np.empty(len(ri), np.float32) for x in VALS}
        ncs = np.empty(len(ri), np.uint8); parent = np.empty(len(ri), np.int64); stc = np.empty(len(ri), np.uint8); sk = np.empty(len(ri), np.uint8)
        state, state_cols = None, None
        for j, key in enumerate(keys):
            sel = np.where(kj == j)[0]
            if not len(sel):
                continue
            s, sd = key; i = ri[sel]
            cols, g, _ = ce.seed_reader(sd)
            if state is None:
                state_cols = cols; state = np.empty((len(ri), len(cols)))
            assert cols == state_cols
            for c_i, c in enumerate(cols):
                state[sel, c_i] = g(c)[i]
            R = np.load(OUT / s / sd.name / "pleiades-lnL.npy", mmap_mode="r"); r = R[i]
            assert np.all(r["row"] == i) and np.all(r["parent"] == state[sel, cols.index("parent")].astype(np.int64))
            parent[sel] = r["parent"]; stc[sel] = r["stratum"]; sk[sel] = int(sd.name.split("-")[1]); ncs[sel] = r["not_computed"]
            for x in VALS:
                lnl[x][sel] = r[x]
            for kind in pf:
                qF[kind][sel] = pf[kind][s] / nseed[s] * pw[key][i]
                qH[kind][sel] = qF[kind][sel] * Lb[key][i] / ZH[kind]
        qM = 0.5 * qF["reweighted"] + 0.5 * qH["reweighted"]
        W = {}
        for kind in pf:
            sfx = "" if kind == "reweighted" else "_fixed"
            W[f"w_flight{sfx}"], W[f"w_H{sfx}"] = qF[kind] / qM, qH[kind] / qM
        E = {f"ess_{k}": ess(v) for k, v in W.items()}
        base = o.split("+")[0]
        rec = dict(option=o, option_name=cs.describe_option(o, short=True), n=len(ri), n_from_flight=int((comp == 0).sum()),
                   n_from_H=int((comp == 1).sum()), unique_rows=int(len(set(zip(kj.tolist(), ri.tolist())))),
                   family_key=cs.eof_family_key(o) if pr else None, **E)
        summary["sources"].append(rec); print(json.dumps(rec), flush=True)
        payload = dict(stratum=stc, stratum_names=np.array(strata), seed=sk, row=ri.astype(np.uint32), parent=parent,
                       component=comp.astype(np.uint8), state=state, state_columns=np.array(state_cols), q_mixture=qM, not_computed=ncs,
                       **W, **{k: np.float64(v) for k, v in E.items()}, **lnl,
                       p_family_reweighted=np.array([pf["reweighted"][s] for s in strata]), p_family_fixed=np.array([pf["fixed"][s] for s in strata]),
                       option=np.array(o), option_name=np.array(rec["option_name"]), rng_seed=np.int64(RNG_SEED))
        nm = f"sources-{SLUG[base]}.npz"
        np.savez(OUT / (nm + ".partial.npz"), **payload); (OUT / (nm + ".partial.npz")).rename(OUT / nm)
    (OUT / "sources-summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
