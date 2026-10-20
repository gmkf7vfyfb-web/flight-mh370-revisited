"""Joined estimate of arm V2 (Pete's ruling 14 Oct 2026: "join with the 00:11 run"). SUMMARY CODE ONLY.

The V2 prior (onset from the 22:41 hand-off onward: anticipatory, fuel cue, flame-out-associated) is split by onset time tau at the
split epoch T1 (the 00:11 hand-off's stop time):
  S1: tau <  T1, DELIBERATE onsets only -> from the 22:41 run (takeover < T1), 23:15 and 00:11 scored IN-STAGE;
  S2: tau >= T1, and EVERY flame-out-associated onset -> from the 00:11 run, 23:15 and 00:11 scored IN THE FILTER, each row re-weighted from the 00:11 run's
                    own onset prior to the V2 prior by r = pi_0(m) p_0(tau | m) / (pi_1(m) p_1(tau | m)), both exact closed forms
                    (onset.rs: renormalised mechanism weights, uniform lead on the truncated support, fuel cue truncated exactly).
  Z(V2) / Z(22:41) = sum_S1 w L1 + exp(dlnZ_filter) sum_S2 w r L2,  dlnZ_filter = lnZ[stop m0011] - lnZ[stop m2241].
The join is attributable only because the stage reproduces the filter's 23:15 + 00:11 increment from 22:41 under cruise
(check_0011_increment.py: +0.023 +/- 0.024 nat over 8 seeds). LABEL every product "V2 joined at 00:11: onsets before 00:11 scored
in-stage, after 00:11 in the filter".
Declared approximation: the predicted exhaustion P that sets the V2 prior of an S2 row is the one computed from its 00:11 state, not
its 22:41 state (the 22:41 prediction of an S2 trajectory is not observed in the 00:11 run).
Constraint applied to S1 (as the core's require_power_until = m0011, hard reject): a row whose FINAL flame-out is before the m0011
burst cannot have answered the 00:11 handshake, so it is excluded from every cell.

Usage: python joined_v2.py RUN_2241 RUN_0011 HANDOFF_2241_TOML HANDOFF_0011_TOML OUT_JSON [--seed k] [--direct RUN_2241_UNAIMED]
"""
import json, sys, argparse, csv, pathlib, re
import numpy as np
from scipy.special import gammaln, logsumexp
from compact_impacts import family_labels
from displacement_hist import constraint_log_factor, SATCOM_CSV
from option_table_0019 import W_S

T_M0011_BURST = 1394237458.0   # 00:10:58 logged m0011 (data/satcom-observations.csv)
FAMS = (("A1", (1,)), ("A2", (2,)), ("B", (3,)), ("outside B (6)", (6,)))


def load(run, seed):
    """A full run tree (RUN/bto-bfo/seed-k/impacts.npy, RUN/run.json) or a slim seed dir (slim_impacts.py: impacts32.npy + run.json)."""
    run = pathlib.Path(run)
    slim = run / f"seed-{seed}" / "impacts32.npy"
    if slim.exists():
        meta = json.loads((run / f"seed-{seed}" / "run.json").read_text()); Y = np.load(slim, mmap_mode="r")
        ix = {c: i for i, c in enumerate(meta["impact_columns"])}; tset = set(meta["slim"]["time_columns"]); t0 = meta["slim"]["t_ref"]
        return meta, (lambda n: np.asarray(Y[:, ix[n]], np.float64) + (t0 if n in tset else 0.0)), ix
    meta = json.loads((run / "run.json").read_text())
    Y = np.load(run / "bto-bfo" / f"seed-{seed}" / "impacts.npy", mmap_mode="r"); ix = {c: i for i, c in enumerate(meta["impact_columns"])}
    return meta, (lambda n: np.asarray(Y[:, ix[n]], np.float64)), ix


def stop_lnz(path):
    import gzip
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            m = re.match(r"(unix_s|log_evidence) = (\S+)", line)
            if m and m.group(1) == "log_evidence": return float(m.group(2))
    raise ValueError(path)


def stop_unix(path):
    import gzip
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            m = re.match(r"unix_s = (\S+)", line)
            if m: return float(m.group(1))


def span(r):
    return (float(r), float(r)) if not isinstance(r, list) else (float(r[0]), float(r[1]))


def isum_cdf(x, L):
    L = [l for l in L if l > 0]; n = len(L)
    if n == 0: return np.where(x >= 0, 1.0, 0.0)
    tot = sum(L); out = np.zeros_like(x, dtype=float); fact = float(np.prod(range(1, n + 1))); prod = float(np.prod(L))
    for mask in range(1 << n):
        sub = sum(L[i] for i in range(n) if mask >> i & 1); par = -1.0 if bin(mask).count("1") % 2 else 1.0
        t = np.clip(x - sub, 0, None); out += par * t ** n
    return np.clip(np.where(x <= 0, 0.0, np.where(x >= tot, 1.0, out / (fact * prod))), 0, 1)


def isum_pdf(x, L):
    L = [l for l in L if l > 0]; n = len(L)
    fact = float(np.prod(range(1, n))) if n > 1 else 1.0; prod = float(np.prod(L)); out = np.zeros_like(x, dtype=float)
    for mask in range(1 << n):
        sub = sum(L[i] for i in range(n) if mask >> i & 1); par = -1.0 if bin(mask).count("1") % 2 else 1.0
        t = np.clip(x - sub, 0, None); out += par * (t ** (n - 1) if n > 1 else (t > 0).astype(float))
    return np.clip(out / (fact * prod), 0, None)


class Prior:
    """The module's onset prior (onset.rs) for hand-off time E and predicted exhaustion P, per mechanism: availability-renormalised
    weight pi(m) and the onset density p(tau | m) (anticipatory: uniform lead on the truncated support; fuel cue: exact truncation)."""
    def __init__(self, onset_cfg):
        self.lead = onset_cfg["anticipatory_lead_s"]; self.w = np.asarray(onset_cfg["mechanism_weights"], float)
        self.a = span(onset_cfg["fuel_caution_lead_s"]); self.r = span(onset_cfg["recognition_delay_s"]); self.s = span(onset_cfg["response_delay_s"])
        assert onset_cfg.get("fuel_cue_truncation", "clamp") == "exact", "the join needs exact fuel-cue truncation in both runs"
    def log_density(self, mech, tau, P, E):
        lo, nhi = self.lead; hi = np.minimum(nhi, np.maximum(P - E, 0.0))
        a1, a2 = self.a; r1, r2 = self.r; s1, s2 = self.s; L = [a2 - a1, r2 - r1, s2 - s1]
        latest_cue = P - a1 + r2 + s2; earliest_cue = P - a2 + r1 + s1
        avail = np.vstack([(hi > lo) & (nhi > lo), (latest_cue >= E) & (latest_cue >= earliest_cue), P >= E]).T * self.w
        tot = avail.sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            pi = np.where(tot > 0, avail[np.arange(len(mech)), mech.astype(int)] / tot, 0.0)
            lp = np.log(pi)
            ant = np.where((P - tau >= lo) & (P - tau <= hi) & (tau >= E), -np.log(hi - lo), -np.inf)
            keep = 1.0 - (1.0 - isum_cdf(P - E - a1 + r2 + s2, L))      # P(onset >= E) = F_Z(P - E - a1 + r2 + s2)
            fy = isum_pdf((P - tau) - (a1 - r2 - s2), L)
            cue = np.where(tau >= E, np.log(fy) - np.log(keep), -np.inf)
            fo = np.where(np.abs(tau - np.maximum(P, E)) < 1.0, 0.0, -np.inf)
        dens = np.select([mech == 0, mech == 1, mech == 2], [ant, cue, fo], -np.inf)
        return lp + dens


def cells(meta, g, prefix):
    """Per-row log-likelihood of each D cell's post-stop data (prefix = 'm0011+' for a 22:41 run, '' for a 00:11 run) plus the log-on
    cause total (q = 1/3, C2 silent) and the survival factor."""
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    sd = float(obs["m0019a"]["bto_sd_us"]); r = g("bto_residual_us:m0019a")
    r600 = np.where(np.isfinite(r), -0.5 * ((r / sd) ** 2 + np.log(2 * np.pi * sd ** 2)), -np.inf)
    base = col("m0011") if prefix else np.zeros(len(r))
    D = {"D0": base, "D1": base + r600, "D2": col(prefix + "r600/no-offset"), "D3": col(prefix + "both/no-offset"), "D4": col(prefix + "both/startup-offset")}
    fo = g("latent:realised_flameout_unix_s"); lag = logon["logon_unix_s"] - fo
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered"); C2 = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    cause = np.logaddexp(np.log(0.75) + C1, np.log(0.25) + C2)
    return {k: v + cause + surv for k, v in D.items()}


def family(g):
    return family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]


def summarise(lw, fam, lat):
    fin = np.isfinite(lw)
    if not fin.any(): return dict(lnZ=-np.inf)
    s = lw[fin].max(); m = np.where(fin, np.exp(lw - s), 0.0); Z = m.sum(); p = m / Z
    out = dict(lnZ=float(np.log(Z) + s), ess=float(1 / np.sum(p * p)), top1=float(p.max()))
    o = np.argsort(lat); c = np.cumsum(p[o]); out["lat_q05_q50_q95"] = [float(lat[o][np.searchsorted(c, q)]) for q in (0.05, 0.5, 0.95)]
    for n, codes in FAMS:
        k = np.isin(fam, codes); out[n] = dict(share=float(p[k].sum()), ess=float(p[k].sum() ** 2 / max(np.sum(p[k] ** 2), 1e-300)))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("r2241"); ap.add_argument("r0011"); ap.add_argument("h2241"); ap.add_argument("h0011"); ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--direct", default=None)
    a = ap.parse_args()
    T0, T1 = stop_unix(a.h2241), stop_unix(a.h0011); dlnz = stop_lnz(a.h0011) - stop_lnz(a.h2241)
    m1, g1, _ = load(a.r2241, a.seed); m2, g2, _ = load(a.r0011, a.seed)
    p1 = Prior(m1["config"]["hypotheses"]["end-of-flight"]["onset"]); p2 = Prior(m2["config"]["hypotheses"]["end-of-flight"]["onset"])
    # The V2 prior is the 00:11 run's onset configuration (all three mechanisms). The 22:41 run may sample deliberate onsets only
    # (mechanism_weights [1, 1, 0], to spend no children on flame-out onsets it does not use); its rows then carry the exact factor
    # pi_V2(m) / pi_run(m) from the renormalised mechanism weights at T0 (the onset densities are the same and cancel).
    assert p1.lead == p2.lead and p1.a == p2.a and p1.r == p2.r and p1.s == p2.s, "the two runs must share the onset supports"
    assert np.all(p2.w > 0), "the 00:11 run defines the V2 prior and must carry all three mechanisms"
    # S1: 22:41 rows with onset before T1, powered at the m0011 burst
    tk1 = g1("takeover_unix_s"); fo1 = g1("latent:realised_flameout_unix_s")
    # Flame-out-associated onsets (families A1, A2) are taken ENTIRELY from the 00:11 run: their onset is the predicted exhaustion,
    # which each hand-off predicts from its own state, so splitting them at T1 double-counts the trajectories whose 22:41 prediction
    # falls before T1 and whose 00:11 prediction falls after it (+0.38 nat in D0 on the seed-1 pilot). Under the power requirement at
    # 00:11 they all cruise through 00:11 on the core dynamics, which is what the filter scores (check_0011_increment.py).
    mech1 = g1("latent:onset_mechanism")
    s1 = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & ~(np.isfinite(fo1) & (fo1 < T_M0011_BURST))
    tau1 = g1("latent:onset_unix_s"); P1 = tau1 + g1("latent:predicted_endurance_at_onset_s")
    with np.errstate(invalid="ignore"):
        lr1 = np.where(s1, p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0), -np.inf)
    s1 = s1 & np.isfinite(lr1)
    lw1 = np.log(g1("weight")) + np.where(s1, lr1, 0.0); c1 = cells(m1, g1, "m0011+")
    # S2: 00:11 rows (takeover >= T1 by construction), re-weighted to the V2 prior from T0
    tau2 = g2("latent:onset_unix_s"); P2 = tau2 + g2("latent:predicted_endurance_at_onset_s"); mech2 = g2("latent:onset_mechanism")
    with np.errstate(invalid="ignore"):
        lr = p2.log_density(mech2, tau2, P2, T0) - p2.log_density(mech2, tau2, P2, T1)   # V2 prior at T0 over the 00:11 run's prior at T1
    s2 = np.isfinite(lr) & (P2 >= T1)
    lw2 = np.log(g2("weight")) + np.where(s2, lr, -np.inf); c2 = cells(m2, g2, "")
    fam = np.r_[family(g1), family(g2)]; lat = np.r_[g1("latitude_deg"), g2("latitude_deg")]
    out = dict(T0=T0, T1=T1, dlnZ_filter=dlnz, s1_pi_factor_quantiles=[float(x) for x in np.quantile(np.exp(lr1[s1]), [0.01, 0.5, 0.99])] if s1.any() else [], s1_rows=int(s1.sum()), s2_rows=int(s2.sum()), s2_rows_dropped=int((~s2).sum()),
               r_quantiles=[float(x) for x in np.quantile(np.exp(lr[s2]), [0.01, 0.5, 0.99])], cells={})
    for k in c1:
        lwk = np.r_[np.where(s1, lw1 + c1[k], -np.inf), lw2 + dlnz + c2[k]]
        out["cells"][k] = summarise(lwk, fam, lat)
        out["cells"][k]["S1_share"] = float(np.exp(logsumexp(lwk[:len(lw1)]) - logsumexp(lwk)))
    if a.direct:
        m3, g3, _ = load(a.direct, a.seed); c3 = cells(m3, g3, "m0011+"); lw3 = np.log(g3("weight"))
        fo3 = g3("latent:realised_flameout_unix_s"); ok3 = ~(np.isfinite(fo3) & (fo3 < T_M0011_BURST))
        out["direct"] = {k: summarise(np.where(ok3, lw3 + v, -np.inf), family(g3), g3("latitude_deg")) for k, v in c3.items()}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("T0", "T1", "dlnZ_filter", "s1_rows", "s2_rows", "s2_rows_dropped", "r_quantiles")}))
    for k in out["cells"]:
        j = out["cells"][k]; d = out.get("direct", {}).get(k)
        line = f"{k}: joined lnZ {j['lnZ']:.3f} S1 {j['S1_share']:.3f} A1/A2/B/out {j['A1']['share']:.3f}/{j['A2']['share']:.3f}/{j['B']['share']:.3f}/{j['outside B (6)']['share']:.3f} ESS {j['ess']:.0f} (B {j['B']['ess']:.0f}) lat50 {j['lat_q05_q50_q95'][1]:.2f}"
        if d: line += f"  || direct lnZ {d['lnZ']:.3f} A1/A2/B/out {d['A1']['share']:.3f}/{d['A2']['share']:.3f}/{d['B']['share']:.3f}/{d['outside B (6)']['share']:.3f} ESS {d['ess']:.0f} (B {d['B']['ess']:.0f}) lat50 {d['lat_q05_q50_q95'][1]:.2f}"
        print(line)


if __name__ == "__main__":
    main()
