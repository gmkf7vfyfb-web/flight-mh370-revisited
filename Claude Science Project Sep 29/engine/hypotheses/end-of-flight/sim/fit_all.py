"""Joint fit of the 6-DOF to all ten Boeing cases, by alternating stages, with optional leave-one-out.

    python fit_all.py <out-dir> [--rounds 3] [--workers 10] [--case-iter 200] [--shared-iter 300]
                      [--exclude caseNN] [--init state.json] [--cases case01,case03]

Each round: (A) per case, fit the nuisance parameters under the current shared physics for each control law
(1 normal-like, 2 stick-fixed) and, for short cases, each rudder-compensation flag, warm-started, and keep the
best; (B) with the nuisance fixed, fit the shared physics to the summed likelihood of the included cases.
--exclude drops one case from stage B (leave-one-out): its own nuisance is still fitted in stage A, so the
prediction it receives is of the SHARED physics only, with its timings, mass and trim offsets its own. That is
the honest scope of this check and is stated in the report.
State after every stage: <out-dir>/state.json (shared, per-case law/flag/nuisance/nll, history).
"""
import argparse, json, pathlib, time
from multiprocessing import Pool
import numpy as np
from scipy.optimize import minimize

G = {}


def _init():
    import fit as F
    from model import schedules
    F.SCHED = schedules(); G["F"] = F; G["tg"], G["data"] = F.load()


def _case_job(args):
    case, shared, law, tac, x_init, it = args
    F = G["F"]
    v, nuis, n = F.fit_case(case, G["tg"], G["data"], shared, law, tac, it, x_init)
    return case, law, tac, v, nuis


def _res_job(args):
    case, shared, nuis, law, tac = args
    return G["F"].residuals(case, G["tg"], G["data"], shared, nuis, law, tac)


def _nll_job(args):
    case, shared, nuis, law, tac = args
    return G["F"].nll(case, G["tg"], G["data"], shared, nuis, law, tac)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--rounds", type=int, default=3); ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--case-iter", type=int, default=200); ap.add_argument("--shared-iter", type=int, default=300)
    ap.add_argument("--exclude", default=None); ap.add_argument("--init", default=None); ap.add_argument("--cases", default=None)
    ap.add_argument("--shared-method", default="powell", choices=["powell", "lsq"],
                    help="lsq: trust-region least squares on the residual vector (10 Oct); powell reproduces the 9 Oct fit")
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    import fit as F
    tg, _ = F.load(); cases = a.cases.split(",") if a.cases else sorted(tg)
    st = json.loads(pathlib.Path(a.init).read_text()) if a.init else {
        "shared": {k: v[2] for k, v in F.SHARED.items()}, "cases": {}, "history": []}
    st["exclude"] = a.exclude
    with Pool(a.workers, initializer=_init) as pool:
        for rnd in range(a.rounds):
            t0 = time.time()
            jobs = []
            for c in cases:
                prev = st["cases"].get(c, {})
                combos = [(1, 0), (2, 0)] if tg[c]["regime"] == "long" else [(1, 0), (1, 1), (2, 0), (2, 1)]
                if prev and rnd > 0:   # after round 0 keep refining the chosen law and flag only
                    combos = [(prev["law"], prev["tac"])]
                for law, tac in combos:
                    jobs.append((c, st["shared"], law, tac, prev.get("nuisance"), a.case_iter))
            results = {}
            for c, law, tac, v, nuis in pool.map(_case_job, jobs):
                if c not in results or v < results[c]["nll"]:
                    results[c] = dict(law=law, tac=tac, nuisance=nuis, nll=v)
            for c, r in results.items():   # accept only if no worse than the case's current state
                if c not in st["cases"] or r["nll"] <= st["cases"][c]["nll"]:
                    st["cases"][c] = r
            st["history"].append(dict(round=rnd, stage="A", total=sum(st["cases"][c]["nll"] for c in cases), s=time.time() - t0))
            (out / "state.json").write_text(json.dumps(st, indent=1))
            incl = [c for c in cases if c != a.exclude]
            spec = F.SHARED
            def total(z):
                sh = F.to_box(z, spec)
                vals = pool.map(_nll_job, [(c, sh, st["cases"][c]["nuisance"], st["cases"][c]["law"], st["cases"][c]["tac"]) for c in incl])
                return float(sum(vals))
            t0 = time.time()
            z0 = F.from_box(st["shared"], spec); f0 = total(z0)
            if a.shared_method == "lsq":
                from scipy.optimize import least_squares
                def resid(z):
                    sh = F.to_box(z, spec)
                    return np.concatenate(pool.map(_res_job, [(c, sh, st["cases"][c]["nuisance"], st["cases"][c]["law"], st["cases"][c]["tac"]) for c in incl]))
                r = least_squares(resid, z0, method="trf", diff_step=1e-3, max_nfev=max(5, a.shared_iter // (len(spec) + 1)))
                res = type("R", (), dict(x=r.x, fun=total(r.x), nfev=int(r.nfev) * (len(spec) + 1)))()
            else:
                res = minimize(total, z0, method="Powell", options=dict(maxfev=a.shared_iter, xtol=1e-2, ftol=1e-4))
            if res.fun < f0:   # never accept a worse shared state
                st["shared"] = F.to_box(res.x, spec)
            for c, v in zip(cases, pool.map(_nll_job, [(c, st["shared"], st["cases"][c]["nuisance"], st["cases"][c]["law"], st["cases"][c]["tac"]) for c in cases])):
                st["cases"][c]["nll"] = v
            st["history"].append(dict(round=rnd, stage="B", total=sum(st["cases"][c]["nll"] for c in incl), nfev=int(res.nfev), s=time.time() - t0,
                                      f0=f0, method=a.shared_method, objective=dict(F.OBJ), case_method=__import__("os").environ.get("EOF_FIT_CASE_METHOD", "powell"),
                                      mass_box=list(F.CASE_LONG["mass"])))
            (out / "state.json").write_text(json.dumps(st, indent=1))
            print(json.dumps(st["history"][-2:]), flush=True)
        if a.exclude:
            # The held-out case's own parameters, refitted under the shared physics fitted WITHOUT it, over every
            # law and flag: this is its leave-one-out prediction. (The refit starts from the full-fit state, which
            # did see this case; only the shared physics' optimum is re-sought without it. Disclosed in the report.)
            c = a.exclude
            combos = [(1, 0), (2, 0)] if tg[c]["regime"] == "long" else [(1, 0), (1, 1), (2, 0), (2, 1)]
            res = pool.map(_case_job, [(c, st["shared"], law, tac, st["cases"][c]["nuisance"], a.case_iter) for law, tac in combos])
            best = min(res, key=lambda r: r[3])
            st["loo_prediction"] = dict(case=c, law=best[1], tac=best[2], nll=best[3], nuisance=best[4])
            (out / "state.json").write_text(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
