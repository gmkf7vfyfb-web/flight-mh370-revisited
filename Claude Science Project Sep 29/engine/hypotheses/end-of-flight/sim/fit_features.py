"""6-DOF shared-physics fit to Boeing SUMMARY STATISTICS (acceptance targets), 11 Oct 2026 (results/eof-6dof-refit-oct11: the
trajectory-error objective is insensitive to the phugoid and the dive onset). Per-case nuisance, law and TAC flag are held at
the input state; only the shared multipliers move. Targets, all from smoke/boeing_calibration.measure on both traces:
  glides (long regime): number of vertical-speed extrema, phugoid period, peak bank;
  every case: peak descent rate (log ratio), high-rate end (yes/no), end time, start-to-end distance.
NOT targeted (held out for validation): the 8-s H1/H2 window counts.
    python fit_features.py <in state.json> <out dir> [--maxfev 400] [--workers 2]
"""
import json, sys, pathlib, argparse, time
import numpy as np
from multiprocessing import Pool
from scipy.optimize import minimize
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(1, str(pathlib.Path(__file__).resolve().parents[1] / "smoke"))
import fit as F
from model import schedules
from boeing_calibration import measure

SPEC = {k: v for k, v in F.SHARED.items()}
G = {}


def _init(state_path):
    F.SCHED = schedules(); G["tg"], G["data"] = F.load(); G["state"] = json.load(open(state_path))
    G["b"] = {}
    for c, d in G["data"].items():
        b = measure(d["t_s"], d["x_nm"], d["y_nm"], d["alt_ft"])
        b["end"] = float(d["t_s"][-1]); b["dist"] = float(np.hypot(d["x_nm"][-1] - d["x_nm"][0], d["y_nm"][-1] - d["y_nm"][0])); G["b"][c] = b


def case_loss(args):
    c, shared = args
    fc = G["state"]["cases"][c]
    try:
        _, rec = F.nll(c, G["tg"], G["data"], shared, fc["nuisance"], fc["law"], fc["tac"], return_rec=True)
        s = measure(rec[:, 0], rec[:, 1], rec[:, 2], rec[:, 3])
    except Exception as e:
        return c, 1e4, {"error": str(e)}
    b = G["b"][c]; s["end"] = float(rec[-1, 0]); s["dist"] = float(np.hypot(rec[-1, 1] - rec[0, 1], rec[-1, 2] - rec[0, 2]))
    terms = {"peak_fpm": (np.log(max(s["max_descent_fpm"], 1.0) / b["max_descent_fpm"]) / 0.2) ** 2,
             "high": 9.0 * (s["high_rate"] != b["high_rate"]),
             "end": ((s["end"] - b["end"]) / (0.05 * b["end"])) ** 2,
             "dist": ((s["dist"] - b["dist"]) / (0.1 * b["dist"] + 2.0)) ** 2}
    if G["tg"][c]["regime"] == "long":
        terms["n_ext"] = ((s["n_vs_extrema"] - b["n_vs_extrema"]) / 5.0) ** 2
        terms["period"] = 9.0 if s["phugoid_period_s"] is None else ((s["phugoid_period_s"] - b["phugoid_period_s"]) / 10.0) ** 2
        terms["bank"] = 0.0 if (s["max_bank_deg"] is None or b["max_bank_deg"] is None) else ((s["max_bank_deg"] - b["max_bank_deg"]) / 5.0) ** 2
    return c, float(sum(terms.values())), {"terms": terms, "sim": {k: s[k] for k in ("max_descent_fpm", "high_rate", "n_vs_extrema", "phugoid_period_s", "max_bank_deg", "end", "dist")}}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("state"); ap.add_argument("out"); ap.add_argument("--maxfev", type=int, default=400); ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    st = json.load(open(a.state)); cases = sorted(st["cases"]); hist = []; t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(a.state,)) as pool:
        def total(z, detail=False):
            sh = dict(st["shared"]); sh.update(F.to_box(z, SPEC))
            res = pool.map(case_loss, [(c, sh) for c in cases])
            tot = sum(r[1] for r in res); hist.append(tot)
            if len(hist) % 25 == 1: print(f"eval {len(hist)} loss {tot:.2f} best {min(hist):.2f} t {time.time() - t0:.0f}s", flush=True)
            return (tot, res, sh) if detail else tot
        z0 = F.from_box(st["shared"], SPEC)
        l0, r0, _ = total(z0, detail=True)
        opt = minimize(total, z0, method="Powell", options={"maxfev": a.maxfev, "xtol": 1e-2, "ftol": 1e-3})
        l1, r1, sh1 = total(opt.x, detail=True)
    st2 = dict(st); st2["shared"] = sh1
    st2["history"] = st["history"] + [{"stage": "features", "loss0": l0, "loss": l1, "nfev": int(opt.nfev), "s": time.time() - t0}]
    (out / "state.json").write_text(json.dumps(st2, indent=1))
    (out / "features.json").write_text(json.dumps({"loss0": l0, "loss": l1, "nfev": int(opt.nfev), "before": {c: d for c, _, d in r0}, "after": {c: d for c, _, d in r1},
                                                  "boeing": None}, indent=1, default=float))
    print("loss", round(l0, 2), "->", round(l1, 2), "nfev", opt.nfev, "shared", {k: round(v, 4) for k, v in sh1.items() if k in SPEC})


if __name__ == "__main__":
    main()
