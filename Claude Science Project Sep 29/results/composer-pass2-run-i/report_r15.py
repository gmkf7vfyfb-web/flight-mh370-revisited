"""Composer pass 2b (ruling 15 Oct 2026): report_pass2.main unchanged, plus the ruling's statistics.
(1) Not-computed share per factor per D x C cell: base (pre-composition) weight of rows the factor did not compute, pooled to the
    equal-prior core mixture (ruling C stratum weights, seeds by base evidence); worst single (stratum, seed) beside it; and the
    share of each headline product's composed weight that sits on carried rows.
(2) Ruling point 3: a factor whose mixture-level not-computed share exceeds 10 % of the weight in an option is a labelled sensitivity
    in that option, not a headline.
(3) Ruling point 4: per-factor split-half. Replicate k = seed k of every stratum. delta_k = ln Z_k(with) - ln Z_k(without) on the
    core mixture; s = SD over the 8 replicates (ddof 1); sigma_half = s * sqrt(1/4 + 1/4); tolerance = 2 sigma_half. Statistic as
    crates/compose: |Delta(1-4) - Delta(5-8)|, Delta pooled by evidence over the half. All 35 balanced partitions summarised beside.
Usage: python report_r15.py <code dir> <work dir> <out dir>
"""
import itertools, json, math, pathlib, sys
import numpy as np
from scipy.special import logsumexp
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, str(pathlib.Path(sys.argv[1]).resolve().parents[1] / 'engine/hypotheses/end-of-flight/smoke')); sys.path.insert(0, '/Users/pete/Downloads/mh370-exchange/pleiades/run-i')
import report_pass2 as RP

TH = 0.10
FACT = [("drift (ocean mixture)", "Dr|M|", "P1|-|"), ("drift, GLORYS12 alone", "Dr|G|", "P1|-|"), ("drift, GlobCurrent alone", "Dr|C|", "P1|-|"),
        ("searches after drift", "DrS|M|", "Dr|M|"), ("Pleiades (given H), after drift", "H|M|", "Dr|M|"), ("searches after Pleiades", "HS|M|", "H|M|"),
        ("hydro lnL_soft (sensitivity), after drift", "Dr|M|+hyd", "Dr|M|"), ("set: drift + searches", "DrS|M|", "P1|-|"),
        ("set: drift + Pleiades + searches", "HS|M|", "P1|-|")]
NCK = [("drift GLORYS12", "drift_nc_share_G", "dG"), ("drift GlobCurrent", "drift_nc_share_C", "dC"), ("Pleiades GLORYS12", "ple_nc_share_G", "pG"),
       ("Pleiades GlobCurrent", "ple_nc_share_C", "pC"), ("hydro lnL_soft", "hydro_nc_share", "Y"), ("searches", "search_nc_share", "S")]


def main(code, work, outd):
    outd = pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    RP.main(work, outd)
    S = RP.Store(work); M = RP.Mixer(S); seeds = list(range(1, 9))
    nc, sh = [], []
    for d in RP.DS:
        for c in RP.CS:
            base = f"{d}|{c}|P1|-|"; W = M.weights(base, "mixC", seeds)
            for name, key, rk in NCK:
                mix = 0.0; worst = (0.0, None); rows = 0
                for st in RP.STRATA:
                    lm = S.seeds_scal(st, base, "lnM"); mx = max(lm.values()); sw = {k: math.exp(lm[k] - mx) for k in seeds}; t = sum(sw.values())
                    v = S.seeds_scal(st, base, key); r = S.seeds_scal(st, base, "nc_rows")
                    mix += W[st] * sum(sw[k] / t * v[k] for k in seeds); rows += sum(r[k][rk] for k in seeds)
                    for k in seeds:
                        if v[k] > worst[0]:
                            worst = (v[k], f"{RP.SNAME[st]} seed {k}")
                nc.append({"D": d, "C": c, "factor": name, "base_share_mix": mix, "worst_share": worst[0], "worst_at": worst[1], "rows": rows,
                           "sensitivity_column": bool(mix > TH), "any_replicate_over": bool(worst[0] > TH)})
            if c == "T":
                for L in ("Dr", "DrS", "H", "HS"):
                    P = f"{d}|T|{L}|M|"; Wp = M.weights(P, "mixC", seeds); e = {"D": d, "product": P}
                    for key in ("nc_composed_share_drift", "nc_composed_share_ple"):
                        acc = 0.0
                        for st in RP.STRATA:
                            lm = S.seeds_scal(st, P, "lnM"); mx = max(lm.values()); sw = {k: math.exp(lm[k] - mx) for k in seeds}; t = sum(sw.values())
                            v = S.seeds_scal(st, P, key); acc += Wp[st] * sum(sw[k] / t * v[k] for k in seeds)
                        e[key] = acc
                    sh.append(e)
    # split-half per factor
    def lnZmix(P, ss):
        return float(logsumexp([math.log(RP.PCORE[st]) + S.lnZ(st, P, list(ss)) for st in RP.STRATA]))
    parts = [((1,) + cmb, tuple(k for k in seeds if k not in (1,) + cmb)) for cmb in itertools.combinations(range(2, 9), 3)]
    spl = []
    for d in RP.DS:
        for name, a, b in FACT:
            Pa, Pb = f"{d}|T|{a}", f"{d}|T|{b}"
            dk = np.array([lnZmix(Pa, [k]) - lnZmix(Pb, [k]) for k in seeds]); s = float(np.std(dk, ddof=1))
            tol = 2.0 * s * math.sqrt(0.25 + 0.25)
            inc = lambda ss: lnZmix(Pa, ss) - lnZmix(Pb, ss)
            lib = abs(inc((1, 2, 3, 4)) - inc((5, 6, 7, 8))); allp = np.array([abs(inc(h0) - inc(h1)) for h0, h1 in parts])
            spl.append({"D": d, "factor": name, "with": Pa, "without": Pb, "increment_all": inc(seeds), "seed_sd": s, "tolerance": tol,
                        "stat_1to4_vs_5to8": lib, "pass_own_tolerance": bool(lib <= tol), "pass_fixed_0p1": bool(lib <= 0.1),
                        "all35_mean": float(allp.mean()), "all35_max": float(allp.max()), "all35_frac_over_tol": float((allp > tol).mean()),
                        "per_replicate_increment": dk.tolist()})
    json.dump({"threshold": TH, "not_computed": nc, "composed_share_on_carried_rows": sh, "split_half": spl}, open(outd / "ruling-stats.json", "w"), indent=1)
    print("ruling stats done", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
