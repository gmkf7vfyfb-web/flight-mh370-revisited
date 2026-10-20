"""Order (b) item 4, 15 Oct 2026: the uniform-onset sensitivity for planned descent (B), as an EXACT per-row re-weighting of the
joined V2 estimate (smoke/joined_v2.py), with the parents' weights (the core posterior at 22:41) left untouched.

Target ("U1"): conditional on a deliberate onset before 00:11 (T1), the onset is uniform in clock time on [T0, min(T1, P)], where
P is the parent's predicted exhaustion; the parent's pre-00:11 deliberate prior mass M(P) is the fuel-tied one, so only the SHAPE
in time changes. The mechanism label is auxiliary: target(m, tau) = p_V2(m, tau) g(tau) / f_dlb(tau), with
f_dlb = sum over deliberate m of pi_m f_m(tau) (fuel-tied) and g = M / (min(T1, P) - T0). Rows from the 22:41 arm carry the
extra factor g / f_dlb; the 00:11 arm is unchanged.
Also reported: the coordination session's BINNED estimate (onset bins re-weighted to uniform widths using pooled prior shares),
which re-weights parents as well as onsets, for comparison.
Usage: python onset_uniform_reweight.py R2241 R0011 H2241_DIR H0011_DIR OUT_JSON SEED [--direct]"""
import sys, json, pathlib
import numpy as np
from scipy.special import logsumexp
from joined_v2 import load, stop_unix, stop_lnz, Prior, cells, family, summarise, isum_cdf, T_M0011_BURST


def pre_t1_mass(pr, P, T0, T1):
    """sum over deliberate m of pi_m P_m(tau < T1) under the fuel-tied prior (availability-renormalised at T0)."""
    n = len(P); out = np.zeros(n)
    lo, nhi = pr.lead; hi = np.minimum(nhi, np.maximum(P - T0, 0.0))
    a1, a2 = pr.a; r1, r2 = pr.r; s1, s2 = pr.s; L = [a2 - a1, r2 - r1, s2 - s1]; off = a1 - r2 - s2
    latest_cue = P - a1 + r2 + s2; earliest_cue = P - a2 + r1 + s1
    avail = np.vstack([(hi > lo) & (nhi > lo), (latest_cue >= T0) & (latest_cue >= earliest_cue), P >= T0]).T * pr.w
    tot = avail.sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pi = np.where(tot[:, None] > 0, avail / tot[:, None], 0.0)
        ant = np.clip((np.minimum(T1, P - lo) - np.maximum(T0, P - hi)) / (hi - lo), 0, 1)
        keep = isum_cdf(P - T0 - off, L)
        cue = np.clip((keep - isum_cdf(P - T1 - off, L)) / keep, 0, 1)
    return pi[:, 0] * np.nan_to_num(ant) + pi[:, 1] * np.nan_to_num(cue)


def main(r2241, r0011, h2241, h0011, outp, seed):
    T0, T1 = stop_unix(h2241), stop_unix(h0011); dlnz = stop_lnz(h0011) - stop_lnz(h2241)
    m1, g1, _ = load(r2241, seed); m2, g2, _ = load(r0011, seed)
    p1 = Prior(m1["config"]["hypotheses"]["end-of-flight"]["onset"]); p2 = Prior(m2["config"]["hypotheses"]["end-of-flight"]["onset"])
    tk1 = g1("takeover_unix_s"); fo1 = g1("latent:realised_flameout_unix_s"); mech1 = g1("latent:onset_mechanism")
    s1 = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & ~(np.isfinite(fo1) & (fo1 < T_M0011_BURST))
    tau1 = g1("latent:onset_unix_s"); P1 = tau1 + g1("latent:predicted_endurance_at_onset_s")
    with np.errstate(invalid="ignore", divide="ignore"):
        lr1 = np.where(s1, p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0), -np.inf)
        nn = lambda x: np.where(np.isnan(x), -np.inf, x)   # a cue density 0/0 where the cue is unavailable reads NaN: it is 0
        f_dlb = np.logaddexp(nn(p2.log_density(np.zeros_like(mech1), tau1, P1, T0)), nn(p2.log_density(np.ones_like(mech1), tau1, P1, T0)))
        M = pre_t1_mass(p2, P1, T0, T1)
        width = np.minimum(T1, P1) - T0
        lg = np.where((tau1 >= T0) & (tau1 < np.minimum(T1, P1)) & (width > 0), np.log(M) - np.log(width), -np.inf)
    s1 = s1 & np.isfinite(lr1)
    lw1 = np.log(g1("weight")) + np.where(s1, lr1, 0.0)
    with np.errstate(invalid="ignore"):
        adj = np.where(s1, lg - f_dlb, 0.0)
    n_bad = int((s1 & ~np.isfinite(f_dlb)).sum())     # sampled deliberate rows with zero fuel-tied density: must be none
    lw1u = lw1 + np.where(np.isnan(adj), -np.inf, adj)
    c1 = cells(m1, g1, "m0011+")
    tau2 = g2("latent:onset_unix_s"); P2 = tau2 + g2("latent:predicted_endurance_at_onset_s"); mech2 = g2("latent:onset_mechanism")
    with np.errstate(invalid="ignore"):
        lr = p2.log_density(mech2, tau2, P2, T0) - p2.log_density(mech2, tau2, P2, T1)
    s2 = np.isfinite(lr) & (P2 >= T1)
    lw2 = np.log(g2("weight")) + np.where(s2, lr, -np.inf); c2 = cells(m2, g2, "")
    fam = np.r_[family(g1), family(g2)]; lat = np.r_[g1("latitude_deg"), g2("latitude_deg")]
    # Prior check: the U1 factor must leave each parent's pre-00:11 deliberate mass unchanged (E over the 22:41 deliberate rows).
    # Prior check on the PRIOR rows (every deliberate onset before T1, before the outcome-based power cut at the 00:11 burst):
    # E_FE[g / f_dlb] must be 1 up to Monte Carlo, because g and f_dlb both integrate to M(P) on [T0, min(T1, P)].
    pr_rows = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & (tau1 < T1)
    with np.errstate(invalid="ignore", divide="ignore"):
        lp_all = np.log(g1("weight")) + p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0)
        adj_all = lg - f_dlb
    lp_all = np.where(np.isnan(lp_all), -np.inf, lp_all); adj_all = np.where(np.isnan(adj_all), -np.inf, adj_all)
    ratio = float(np.exp(logsumexp((lp_all + adj_all)[pr_rows]) - logsumexp(lp_all[pr_rows]))) if pr_rows.any() else float("nan")
    # The coordination session's binned estimate (15 Oct): each onset bin re-weighted from its pooled fuel-tied prior share to its
    # share of clock time. As a row factor u_b / prior_b on the 22:41 deliberate rows. This re-weights parents as well as onsets.
    edges = T0 + np.array([0.0, 19.0, 34.0, 49.0, 64.0, 79.0]) * 60.0
    edges = np.r_[edges, T1]
    b = np.clip(np.searchsorted(edges, tau1, side="right") - 1, 0, len(edges) - 2)
    wpr = np.exp(lp_all - np.max(lp_all[pr_rows])); wpr[~pr_rows] = 0.0
    prior_b = np.bincount(b, weights=wpr, minlength=len(edges) - 1); prior_b = prior_b / prior_b.sum()
    width_b = np.diff(edges) / (T1 - T0)
    with np.errstate(divide="ignore"):
        lw1b = lw1 + np.where(s1 & (tau1 < T1), np.log(width_b[b]) - np.log(prior_b[b]), 0.0)
    out = dict(T0=T0, T1=T1, seed=seed, binned_prior_shares=prior_b.tolist(), binned_widths=width_b.tolist(), prior_mass_ratio_U1_over_FE=ratio, rows_zero_fe_density=n_bad, cells={})
    for k in c1:
        res = {}
        for name, a in (("fe_tied", lw1), ("uniform_U1", lw1u), ("binned_coordination", lw1b)):
            lwk = np.r_[np.where(s1, a + c1[k], -np.inf), lw2 + dlnz + c2[k]]
            s = summarise(lwk, fam, lat); s["S1_share"] = float(np.exp(logsumexp(lwk[:len(lw1)]) - logsumexp(lwk)))
            # pre-00:11 B effective impacts
            p = np.exp(lwk[:len(lw1)] - np.max(lwk)); p[~np.isfinite(p)] = 0
            s["S1_ess"] = float(p.sum() ** 2 / max(np.square(p).sum(), 1e-300))
            res[name] = s
        out["cells"][k] = res
        print(f"seed {seed} {k}: B share FE {res['fe_tied']['B']['share']:.4f} -> U1 {res['uniform_U1']['B']['share']:.4f}; "
              f"pre-00:11 share {res['fe_tied']['S1_share']:.4f} -> {res['uniform_U1']['S1_share']:.4f}; lnZ {res['fe_tied']['lnZ']:.3f} -> {res['uniform_U1']['lnZ']:.3f}; "
              f"S1 ESS {res['fe_tied']['S1_ess']:.0f} / {res['uniform_U1']['S1_ess']:.0f}; binned B {res['binned_coordination']['B']['share']:.4f}", flush=True)
    print(f"seed {seed}: prior-mass check (must be 1 up to Monte Carlo): {ratio:.4f}; rows with zero fuel-tied density {n_bad}")
    json.dump(out, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6]))
