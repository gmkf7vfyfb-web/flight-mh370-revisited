"""00:19 two-factor table (architecture 01:45Z, rulings 02:05Z and 02:15Z, 12 Oct 2026): data treatment D0-D5 x log-on cause
C1 (fuel exhaustion + APU start: Erlang lag density from the realised flame-out) / C2 (other: uniform 1/W over the data-defined
window W = 00:10:58-01:15:56, 3,898 s), and the competing-causes total per D, L_logon = f_lag + q/W, i.e. the p-mixture with
p = 1/(1+q): q = 1/3 (p = 0.75) primary, q = 1 (p = 0.5) sensitivity. Constraints: C1 `unpowered` (= silent under that cause);
C2 `silent` PRIMARY with `unpowered` beside it. Survival factor (no in-flight breakup before 00:19:37) applied throughout.
D0 held out; D1 R600 BTO; D2 R600 BTO + R600 BFO as recorded; D3 R600 BTO + both BFOs as recorded (Holland's H2 data);
D4 both BFOs with Holland's shared start-up offset (Holland's H1 data); D5 R600 BTO + R600 BFO as recorded + R1200 BFO with a
start-up offset U[17, 130] Hz (Pete's point), COMPUTED here from stored columns (innovations, BTO residual, hand-off bias
variance) in closed form; the method reproduces the stored D2/D3/D4 columns to float32 precision. No D uses the R1200 BTO.
Strata mixed with core's P(family); seeds pooled by evidence (as holland_sweep_summary.py).
Usage: python option_table_0019.py EOF_ROOT CORE_ROOT OUT_JSON stratum=P [...]
"""
import json, sys, pathlib, csv
import numpy as np
from scipy.special import logsumexp, gammaln
from scipy.stats import norm
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV

W_S = (1394241356.0 - 1394237458.0)        # 00:10:58 to 01:15:56 UTC, 3,898 s
D_NAMES = {"D0": "held out", "D1": "R600 BTO", "D2": "R600 BTO + R600 BFO", "D3": "R600 BTO + both BFOs (Holland H2 data)",
           "D4": "R600 BTO + both BFOs, shared start-up offset (Holland H1 data)", "D5": "R600 BTO + R600 BFO + R1200 BFO with offset"}
LAT = np.linspace(-45.0, -20.0, 2501); FAMS = ((1, "A1"), (2, "A2"), (3, "B"))


def d5_loglik(g, V, obs):
    """ln p(R600 BTO, R600 BFO no offset, R1200 BFO + offset b ~ U[lo, hi]) with one shared bias (Kalman, as satcom::FinalBfo)."""
    s_bto = float(obs["m0019a"]["bto_sd_us"]); s1 = float(obs["m0019a"]["bfo_sd_hz"]); s2 = float(obs["m0019b"]["bfo_sd_hz"])
    r = g("bto_residual_us:m0019a"); i1 = g("bfo_innovation_hz:m0019a"); i2 = g("bfo_innovation_hz:m0019b")
    S1 = V + s1 ** 2; K = V / S1; S2 = V * (1 - K) + s2 ** 2; lo, hi = 17.0, 130.0
    m = i2 - K * i1; sd = np.sqrt(S2)
    with np.errstate(divide="ignore", invalid="ignore"):
        band = np.log(np.clip(norm.cdf((m - lo) / sd) - norm.cdf((m - hi) / sd), 1e-300, None)) - np.log(hi - lo)
    out = -0.5 * ((r / s_bto) ** 2 + np.log(2 * np.pi * s_bto ** 2)) + norm.logpdf(i1, 0, np.sqrt(S1)) + band
    return np.where(np.isfinite(r) & np.isfinite(i1) & np.isfinite(i2), out, -np.inf)


def run_obs(meta):
    """The 00:19 observation rows the run itself was scored with (run.json [inputs] observations, relative to engine/), so D5 uses the
    same BFO errors as the stored columns (run J: 4.3177 Hz; fault F1 of results/e2e-calibration-smoke-2026-10-19, fixed 19 Oct)."""
    p = pathlib.Path(meta["config"]["inputs"]["observations"])
    path = p if p.is_absolute() else (SATCOM_CSV.parents[1] / p).resolve()
    return {r["epoch_id"]: r for r in csv.DictReader(open(path))}


def seed_terms(sd, handoff):
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = run_obs(meta)
    w = g("weight")
    # Thinned files (both_burst_thin.py): normalise by the UNTHINNED weight total, not by the stored weights (16 Oct 2026).
    wsum = float(meta.get("thinning", {}).get("weight_sum_in", w.sum())); lw = np.log(w) - np.log(wsum)
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"), "D4": col("both/startup-offset"), "D5": d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C = {"C1": lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered"),
         "C2 silent": -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent"),
         "C2 unpowered": -np.log(W_S) + constraint_log_factor(g, logon, "other", "unpowered")}
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    li = np.clip(np.searchsorted(LAT, g("latitude_deg")), 0, len(LAT) - 1)
    cells = {}
    for d, ld in D.items():
        for c, lc in C.items():
            cells[f"{d}x{c}"] = lw + surv + ld + lc
        for q in (1 / 3, 1.0):
            p = 1 / (1 + q)
            for other in ("C2 silent", "C2 unpowered"):
                cells[f"{d} total q={q:.3g} ({other})"] = lw + surv + ld + np.logaddexp(np.log(p) + C["C1"], np.log(1 - p) + C[other])
    out = {}
    for k, a in cells.items():
        s = float(np.max(a[np.isfinite(a)])) if np.isfinite(a).any() else 0.0
        m = np.exp(a - s); m[~np.isfinite(m)] = 0.0
        two = lambda x: [float(np.log(x.sum()) + s) if x.sum() > 0 else -np.inf, float(np.log((x * x).sum()) + 2 * s) if x.sum() > 0 else -np.inf]
        out[k] = {"all": two(m), "fam": {n: two(m * (f4 == cc)) for cc, n in FAMS}, "s": s, "hist": np.bincount(li, weights=m, minlength=len(LAT))}
    return out


def main(eof_root, core_root, outp, strata):
    acc = {}
    for st, P in strata.items():
        seeds = sorted(p for p in (pathlib.Path(eof_root) / st).glob("seed-*") if p.is_dir()); K = len(seeds)
        for sd in seeds:
            t = seed_terms(sd, pathlib.Path(core_root) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy"); c = np.log(P / K)
            for k, v in t.items():
                A = acc.setdefault(k, {"l1": [], "l2": [], "f1": {}, "f2": {}, "h": np.zeros(len(LAT))})
                A["l1"].append(c + v["all"][0]); A["l2"].append(2 * c + v["all"][1])
                for n, x in v["fam"].items():
                    A["f1"].setdefault(n, []).append(c + x[0]); A["f2"].setdefault(n, []).append(2 * c + x[1])
                A["h"] += v["hist"] * np.exp(c + v["s"])
                A.setdefault("seeds", []).append([st, sd.name, v["all"][0]])
            print(f"  {st} {sd.name}", flush=True)
    res = {"W_s": W_S, "D": D_NAMES, "cells": {}}
    for k, A in acc.items():
        lz = float(logsumexp(A["l1"])); hc = np.cumsum(A["h"]); hc /= hc[-1]
        res["cells"][k] = {"ln_Z": lz, "eff_impacts": float(np.exp(2 * lz - logsumexp(A["l2"]))),
                           "families": {n: {"share": float(np.exp(logsumexp(A["f1"][n]) - lz)),
                                            "eff_impacts": float(np.exp(2 * logsumexp(A["f1"][n]) - logsumexp(A["f2"][n]))) if np.isfinite(logsumexp(A["f2"][n])) else 0.0} for n in A["f1"]},
                           "latitude_q05_q50_q95": [float(LAT[np.searchsorted(hc, q)]) for q in (0.05, 0.5, 0.95)],
                           "seed_ln_Z": A["seeds"],
                           "seed_sd_ln_Z_by_stratum": {st: float(np.std([x[2] for x in A["seeds"] if x[0] == st], ddof=1)) if sum(x[0] == st for x in A["seeds"]) > 1 else None for st in strata}}
    Z = lambda k: res["cells"][k]["ln_Z"]
    res["bayes_factors"] = {
        "C1:C2 within D (C2 silent)": {d: Z(f"{d}xC1") - Z(f"{d}xC2 silent") for d in D_NAMES},
        "C1:C2 within D (C2 unpowered)": {d: Z(f"{d}xC1") - Z(f"{d}xC2 unpowered") for d in D_NAMES},
        "D3:D4 within C": {c: Z(f"D3x{c}") - Z(f"D4x{c}") for c in ("C1", "C2 silent", "C2 unpowered")},
        "D5:D3 within C": {c: Z(f"D5x{c}") - Z(f"D3x{c}") for c in ("C1", "C2 silent", "C2 unpowered")},
        "D5:D4 within C": {c: Z(f"D5x{c}") - Z(f"D4x{c}") for c in ("C1", "C2 silent", "C2 unpowered")},
        "D3:D4 total q=1/3 silent": Z("D3 total q=0.333 (C2 silent)") - Z("D4 total q=0.333 (C2 silent)"),
        "D5:D3 total q=1/3 silent": Z("D5 total q=0.333 (C2 silent)") - Z("D3 total q=0.333 (C2 silent)"),
        "D5:D4 total q=1/3 silent": Z("D5 total q=0.333 (C2 silent)") - Z("D4 total q=0.333 (C2 silent)")}
    json.dump(res, open(outp, "w"), indent=1)
    np.savez_compressed(str(outp).replace(".json", "") + "-latitude.npz", lat=LAT, **{k.replace(" ", "_").replace("=", "").replace("(", "").replace(")", "").replace("/", "_"): A["h"] / A["h"].sum() for k, A in acc.items()})
    for k, v in res["cells"].items():
        f = v["families"]
        print(f"{k:34s} lnZ {v['ln_Z']:8.3f} ESS {v['eff_impacts']:10.0f} A1/A2/B {f['A1']['share']:.2f}/{f['A2']['share']:.2f}/{f['B']['share']:.2f} A1 ESS {f['A1']['eff_impacts']:7.0f} lat {v['latitude_q05_q50_q95']}")
    print(json.dumps(res["bayes_factors"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], {a.split("=")[0]: float(a.split("=")[1]) for a in sys.argv[4:]})
