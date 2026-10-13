"""Pilot runs of 13 Oct 2026 (full/pilot_oct13.sh). SMOKE / PILOT SCALE - NEVER EVIDENCE.

  identity  P0011 (N = 4) against run-i-dive seed 1 (N = 16): rows of the first 4 children must agree in every physics column.
  gate4     P2241: per family (A1, A2, B) and per cell, the onset-boundary statistic (weight within 60 s of the earliest permitted
            onset = the 22:41 hand-off epoch), the support-truncation fraction, the per-trajectory onset-window length, and ESS /
            effective parents / top-1 / top-10 beside each. Cells: the 22:41 analogue of D0-D4 (23:15 + 00:11 always scored in-stage)
            x log-on cause, competing-causes total q = 1/3 with C2 silent; D5 is NOT computable from stored columns at 22:41 (the bias
            variance after the in-stage 23:15 and 00:11 updates is not emitted) and is reported as a gap.
            Deliberate-onset control: sampled [1,1,1,1]; reported under that AND under the run-i-dive [0.5,0.5,0,0] by exact re-weighting.

Usage: python pilot_oct13.py identity RUN_P0011 EOF_RUNIDIVE_SEED1 OUT_JSON
       python pilot_oct13.py gate4 RUN_P2241 OUT_JSON
"""
import json, sys, pathlib, csv
import numpy as np
from scipy.special import gammaln
from compact_impacts import load as load_compact, family_labels
from displacement_hist import constraint_log_factor, SATCOM_CSV
from option_table_0019 import W_S

FAMS = (("A1", (1,)), ("A2", (2,)), ("B", (3,)), ("outside B (6)", (6,)))   # ruling 6: code 6 = deliberate onset then no intervention


def load_full(run, seed=1):
    run = pathlib.Path(run); meta = json.loads((run / "run.json").read_text())
    Y = np.load(run / "bto-bfo" / f"seed-{seed}" / "impacts.npy", mmap_mode="r"); ix = {c: i for i, c in enumerate(meta["impact_columns"])}
    return meta, (lambda n: np.asarray(Y[:, ix[n]], np.float64)), ix


def kish(lw, mask=None, parent=None):
    a = np.where(mask, lw, -np.inf) if mask is not None else lw
    fin = np.isfinite(a)
    if not fin.any(): return dict(share=0.0, ess=0.0, eff_parents=0.0, top1=float("nan"), top10=float("nan"))
    m = np.exp(a - a[fin].max()); m[~fin] = 0.0
    m = m / m.sum(); ess = 1 / np.sum(m * m); t = np.sort(m)[::-1]
    out = dict(ess=float(ess), top1=float(t[0]), top10=float(t[:10].sum()))
    if parent is not None:
        _, inv = np.unique(parent, return_inverse=True); ps = np.bincount(inv, weights=m); out["eff_parents"] = float(1 / np.sum(ps * ps))
    return out


def identity(p0011, ridseed1, outp):
    meta, g, ix = load_full(p0011)
    cm, cg = load_compact(ridseed1)
    par = g("parent").astype(np.int64); cpar = cg("parent").astype(np.int64)
    # run-i-dive rows: parent-contiguous, 16 children x 4 descents; keep the first 4 children (16 rows) of each parent
    starts = np.flatnonzero(np.r_[True, cpar[1:] != cpar[:-1]]); lens = np.diff(np.r_[starts, len(cpar)])
    pos = np.arange(len(cpar)) - np.repeat(starts, lens)
    keep = pos < 16
    res = {"rows_p0011": int(len(par)), "rows_rid_kept": int(keep.sum()), "parents_equal": bool(np.array_equal(par, cpar[keep]))}
    for c in ["unix_s", "latitude_deg", "longitude_deg", "velocity_up_mps", "latent:realised_flameout_unix_s", "loglik:r600/no-offset",
              "loglik:both/startup-offset", "latent:onset_mechanism", "latent:control_realised"]:
        a = g(c); b = cg(c)[keep]
        both = np.isfinite(a) & np.isfinite(b); d = np.abs(a[both] - b[both])
        scale = np.maximum(np.abs(a[both]), 1.0)
        res[c] = dict(nan_pattern_equal=bool(np.array_equal(np.isfinite(a), np.isfinite(b))), max_abs=float(d.max()) if d.size else 0.0,
                      max_rel=float((d / scale).max()) if d.size else 0.0)
    # weights: N=4 vs first-4-of-16 under the unnormalised rule differ by the uniform factor 16/4 within each parent
    w4 = g("weight"); w16 = cg("weight")[keep]
    r = w4 / w16; r = r[np.isfinite(r) & (w16 > 0)]
    res["weight_ratio_p0011_over_rid"] = dict(median=float(np.median(r)), min=float(r.min()), max=float(r.max()))
    json.dump(res, open(outp, "w"), indent=1); print(json.dumps(res, indent=1))


def gate4(p2241, outp):
    meta, g, ix = load_full(p2241); cfg = meta["config"]; logon = cfg["hypotheses"]["end-of-flight"]["logon"]
    parent = g("parent").astype(np.int64); w = g("weight"); lw = np.log(w)
    t_ho = g("takeover_unix_s")
    onset = g("latent:onset_unix_s"); mech = g("latent:onset_mechanism"); creq = g("latent:control_requested")
    trunc = g("latent:onset_support_truncated_fraction"); pend = g("latent:predicted_endurance_at_onset_s")
    fo = g("latent:realised_flameout_unix_s")
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    T2241 = float(np.nanmin(t_ho))           # every child takes over at the hand-off epoch or later; the earliest permitted onset
    # per-trajectory window: hand-off epoch to the predicted exhaustion under continued cruise, = onset + predicted endurance at onset
    window = (onset + pend) - T2241
    f4 = family_labels(mech, g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    # deliberate-onset control re-weighting to the legacy prior [0.5, 0.5, 0, 0] (family-b-ditching, as run-i-dive); sampled [1,1,1,1]. Deliberate = mech 0/1.
    deliberate = (mech == 0) | (mech == 1)
    legacy = np.array([0.5, 0.5, 0.0, 0.0])   # family-b-ditching.toml, applied after v2-broad's [0.6,0.4,0,0] in the run-i-dive recipe
    sampled = np.full(4, 0.25); sampled = np.full(4, 0.25)
    with np.errstate(divide="ignore"):
        lr = np.where(deliberate & np.isfinite(creq), np.log(legacy[np.clip(np.nan_to_num(creq).astype(int), 0, 3)] / sampled[0]), 0.0)
    sd_bto = float(obs["m0019a"]["bto_sd_us"]); r = g("bto_residual_us:m0019a")
    r600bto = np.where(np.isfinite(r), -0.5 * ((r / sd_bto) ** 2 + np.log(2 * np.pi * sd_bto ** 2)), -np.inf)
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    base11 = col("m0011")
    D = {"D0 (23:15+00:11 only)": base11, "D1 R600 BTO": base11 + r600bto, "D2 R600 BTO+BFO": col("m0011+r600/no-offset"),
         "D3 both BFO raw": col("m0011+both/no-offset"), "D4 both BFO start-up offset": col("m0011+both/startup-offset")}
    lag = logon["logon_unix_s"] - fo
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered"); C2 = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    cause = np.logaddexp(np.log(0.75) + C1, np.log(0.25) + C2)
    cells = {"prior (nothing scored)": lw.copy()}
    for k, v in D.items():
        cells[k + " x cause total"] = lw + surv + v + cause
    out = dict(T_handoff_unix=T2241, rows=int(len(w)), parents=int(len(np.unique(parent))),
               mechanism_counts={str(int(m)): int((mech == m).sum()) for m in np.unique(mech[np.isfinite(mech)])},
               family_code_counts={str(int(c)): int((f4 == c).sum()) for c in np.unique(f4[np.isfinite(f4)])},
               truncation_finite_fraction=float(np.isfinite(trunc).mean()),
               window_s_quantiles_rows=[float(x) for x in np.nanquantile(window, [0.05, 0.25, 0.5, 0.75, 0.95])],
               cells={})
    for prior_name, extra in (("control sampled [1,1,1,1]", 0.0), ("control legacy [0.5,0.5,0,0]", lr)):
        for cname, a in cells.items():
            a2 = a + extra; row = {}
            for fname, codes in (("all", None),) + FAMS:
                m = np.ones(len(a2), bool) if codes is None else np.isin(f4, codes)
                st = kish(a2, m, parent)
                fin = np.isfinite(a2) & m
                if fin.any():
                    ww = np.exp(a2 - a2[np.isfinite(a2)].max()); ww[~np.isfinite(ww)] = 0.0; tot = ww.sum(); wf = ww * m
                    st["share"] = float(wf.sum() / tot)
                    near = m & (onset - T2241 <= 60.0)
                    st["onset_boundary_fraction"] = float(ww[near].sum() / max(wf.sum(), 1e-300))
                    tw = np.isfinite(trunc) & m
                    st["truncation_weighted_mean"] = float(np.sum(ww[tw] * trunc[tw]) / max(ww[tw].sum(), 1e-300)) if tw.any() else float("nan")
                    ok = m & np.isfinite(window); o = np.argsort(window[ok]); c = np.cumsum(wf[ok][o]); c /= c[-1]
                    st["window_s_weighted_q05_q50_q95"] = [float(window[ok][o][np.searchsorted(c, q)]) for q in (0.05, 0.5, 0.95)]
                    on = m & np.isfinite(onset); o = np.argsort(onset[on]); c = np.cumsum(wf[on][o]); c /= c[-1]
                    st["onset_min_after_handoff_q05_q50_q95"] = [float((onset[on][o][np.searchsorted(c, q)] - T2241) / 60) for q in (0.05, 0.5, 0.95)]
                row[fname] = st
            out["cells"][f"{prior_name} | {cname}"] = row
    json.dump(out, open(outp, "w"), indent=1); print("wrote", outp)


if __name__ == "__main__":
    if sys.argv[1] == "identity": identity(*sys.argv[2:5])
    else: gate4(*sys.argv[2:4])
