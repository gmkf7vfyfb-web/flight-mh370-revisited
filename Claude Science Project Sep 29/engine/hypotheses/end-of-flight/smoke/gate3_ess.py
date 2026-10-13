"""Gate 3 (contract v7 section 7; work order 13 Oct 2026): effective sample size at the hand-off and child counts we intend to use,
measured BEFORE any end-of-flight run, per seed and per family, with weight concentration beside it (section 2 rule 6).

Measured by SUBSAMPLING an existing full sweep, so it costs no descents: for each seed, keep a random P of the hand-off parents and the
first N of each parent's children (all of each child's descents), and recompute the cell weights exactly as option_table_0019.py does
(D0-D5 x log-on cause, competing-causes total at q = 1/3 with C2 silent primary, survival factor). Dropping children uniformly per
parent is exact under the unnormalised within-parent rule (core request 9): every kept row in a parent is rescaled by the same factor.

Reports per (P, N, seed, cell): effective impacts (Kish), effective parents (Kish over per-parent sums), largest single impact share and
top-ten share, total and per family (A1, A2, B). These are SAMPLER diagnostics only - never evidence for an impact distribution.

Usage: python gate3_ess.py EOF_STRATUM_DIR CORE_STRATUM_DIR OUT_JSON [--P 100000,25000,10000] [--N 16,8,4] [--seeds 1,2,...]
"""
import json, sys, pathlib, csv, argparse
import numpy as np
from scipy.special import gammaln
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV
from option_table_0019 import d5_loglik, W_S

FAMS = (((1,), "A1"), ((2,), "A2"), ((3,), "B"), ((6,), "outside B"))   # family4 codes per ruling 6: 6 = deliberate onset then no intervention, OUTSIDE B
CELLS = ["D0 total", "D1 total", "D2 total", "D3 total", "D4 total", "D5 total", "D3xC2 silent", "D4xC1"]


def row_logweights(sd, handoff):
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w)
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    parent = g("parent").astype(np.int64)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[parent]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    C2s = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    p = 0.75
    base = lw + surv
    out = {f"{d} total": base + ld + np.logaddexp(np.log(p) + C1, np.log(1 - p) + C2s) for d, ld in D.items()}
    out["D3xC2 silent"] = base + D["D3"] + C2s
    out["D4xC1"] = base + D["D4"] + C1
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    return parent, out, f4


def child_index(parent):
    """Row position within its parent's block, and the block length; rows of a parent must be contiguous."""
    starts = np.flatnonzero(np.r_[True, parent[1:] != parent[:-1]])
    lens = np.diff(np.r_[starts, len(parent)])
    assert len(np.unique(parent[starts])) == len(starts), "parent rows are not contiguous"
    pos = np.arange(len(parent)) - np.repeat(starts, lens)
    return pos, lens


def stats(lw, parent, keep):
    a = lw[keep]; pr = parent[keep]
    fin = np.isfinite(a)
    if not fin.any():
        return dict(ess=0.0, eff_parents=0.0, top1=float("nan"), top10=float("nan"), n=int(keep.sum()))
    m = np.exp(a - a[fin].max()); m[~fin] = 0.0; s = m.sum(); m /= s
    ess = 1.0 / np.sum(m * m)
    _, inv = np.unique(pr, return_inverse=True); ps = np.bincount(inv, weights=m)
    top = np.sort(m)[::-1]
    return dict(ess=float(ess), eff_parents=float(1.0 / np.sum(ps * ps)), top1=float(top[0]), top10=float(top[:10].sum()), n=int(keep.sum()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("eof"); ap.add_argument("core"); ap.add_argument("out")
    ap.add_argument("--P", default="100000,25000,10000"); ap.add_argument("--N", default="16,8,4"); ap.add_argument("--seeds", default="")
    a = ap.parse_args()
    Ps = [int(x) for x in a.P.split(",")]; Ns = [int(x) for x in a.N.split(",")]
    seeds = [int(x) for x in a.seeds.split(",")] if a.seeds else sorted(int(p.name.split("-")[1]) for p in pathlib.Path(a.eof).glob("seed-*") if p.is_dir())
    rows = []
    for k in seeds:
        sd = pathlib.Path(a.eof) / f"seed-{k}"; ho = pathlib.Path(a.core) / "bto-bfo" / f"seed-{k}" / "handoff-m0011" / "handoff.npy"
        parent, cells, f4 = row_logweights(sd, ho)
        pos, lens = child_index(parent)
        dpc = int(json.loads((sd / "run.json").read_text())["config"]["hypotheses"]["end-of-flight"]["descents_per_child"])
        child = pos // dpc; n_children = int(np.median(lens)) // dpc
        uparents = np.unique(parent); rng = np.random.default_rng(1000 + k)
        print(f"seed {k}: rows {len(parent):,} parents {len(uparents):,} children/parent {n_children} descents/child {dpc}", flush=True)
        for P in Ps:
            chosen = uparents if P >= len(uparents) else rng.choice(uparents, P, replace=False)
            in_p = np.isin(parent, chosen)
            for N in Ns:
                if N > n_children: continue
                keep = in_p & (child < N)
                for c in CELLS:
                    r = dict(seed=k, P=int(min(P, len(uparents))), N=N, cell=c, **stats(cells[c], parent, keep))
                    for code, name in FAMS:
                        r[name] = stats(np.where(np.isin(f4, code), cells[c], -np.inf), parent, keep)
                    rows.append(r)
        json.dump(dict(eof=a.eof, core=a.core, rows=rows), open(a.out, "w"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
