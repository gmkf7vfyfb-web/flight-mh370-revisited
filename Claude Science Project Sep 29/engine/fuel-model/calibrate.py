#!/usr/bin/env python3
"""Calibrate the internal fuel model (fuel session, 10 Oct 2026).

Usage (from engine/):  python fuel-model/calibrate.py [SIR_TEXT] [MH371_ACARS_XLSX]
Writes results/fuel-model/internal-calibration-items.csv and internal-calibration.json (model
outputs and public / internal-evidence numbers only; no table cell is written).

Evidence groups (each gives an implied kappa = Boeing-or-measured burn / model burn at kappa = 1):
  Boeing-T3  SIR App. 1.6E Table 3 (p. 5): five segment burns from the 17:06:43 ACARS state, each
             started from Boeing's fuel at its start, printed durations. Standard day (p. 3).
  Boeing-T4  Table 4 (p. 6): 22 endurances from 73,908 lb at arc 1, Mach from TAS at ISA.
  MH371      9M-MRO's previous flight (internal, provenance unverified): constant-FL cruise segments
             at measured SAT; burn from the flowmeter-integrated gross weight (GWT, 40 lb steps) and
             from FQIS fuel (TOTFW, 100 kg steps), averaged, half their difference added as error.
Calibration set: the posterior's envelope, FL >= 250, not extrapolated above the top schedule and
not below the tables. Items flown above M0.84 fit the drag-rise term; FL150/FL030 are reported only.
Within each group a random-effects ML fit gives kappa and the residual scatter; the groups are
combined by DerSimonian-Laird, whose between-group tau goes into the trajectory factor's s.d.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import integrate  # noqa: E402
import internal  # noqa: E402
import sources  # noqa: E402
import tables  # noqa: E402

ENGINE = HERE.parent
REPO = ENGINE.parent.parent
LB = sources.LB
SIR_TXT = REPO / "ISO Sept 28 Status/inputs/end-of-flight/report-text/boeing_performance_appendix_1_6E.txt"
MH371 = REPO / "library_full_audit/MH370/mh371-acars.xlsx"
OUT = ENGINE.parent / "results/fuel-model"
W_REF = 200.0


def boeing_items(model, sir, dt=1 / 60):
    out, zfw, start = [], sir["zfw_kg"], sir["fuel0_kg"]
    ff = lambda fl, w, m, d: model.ff(fl, w, m, 0.0)
    for i, s in enumerate(sir["seg"], 1):
        target = start - s["end_lb"] * LB
        left, _, fl = integrate.fly(ff, start, zfw, s["fl"], s["mach"], hours=s["hours"], dt_h=dt)
        q = 0.001 if i in (2, 5) else 0.01
        out.append(dict(group="Boeing-T3", item=f"T3 seg {i}", fl=s["fl"], mach=s["mach"], w_t=(zfw + start - target / 2) / 1000,
                        disa=0.0, observed=target, model=start - left, quantity="burn kg", flags=",".join(sorted(fl)),
                        kappa=target / (start - left), se=q / math.sqrt(12) / s["hours"]))
        start = s["end_lb"] * LB
    for e in sir["end"]:
        m = tables.isa_mach(e["fl"], e["tas"])
        _, t, fl = integrate.fly(ff, sir["arc1_kg"], zfw, e["fl"], m, dt_h=dt)
        q = 0.01 if abs(e["hours"] * 10 - round(e["hours"] * 10)) > 1e-9 else 0.1
        out.append(dict(group="Boeing-T4", item=f"T4 FL{e['fl']:.0f} {e['tas']:.0f} kt", fl=e["fl"], mach=m,
                        w_t=(zfw + sir["arc1_kg"] / 2) / 1000, disa=0.0, observed=e["hours"], model=t, quantity="endurance h",
                        flags=",".join(sorted(fl)), kappa=t / e["hours"], se=q / math.sqrt(12) / e["hours"]))
    return pd.DataFrame(out)


def mh371_items(model, path, n=10):
    rows = sources.mh371_cruise(path)
    out = []
    for s in sources.segments(rows):
        mb, ws, ds, ms, flags = 0.0, [], [], [], set()
        for r in s:
            dt = (r["t1"] - r["t0"]) / 3600 / n
            for k in range(n):
                x = (k + 0.5) / n
                m = r["mach0"] + (r["mach1"] - r["mach0"]) * x
                sat = r["sat0"] + (r["sat1"] - r["sat0"]) * x
                w = (r["gwt0_kg"] + (r["gwt1_kg"] - r["gwt0_kg"]) * x) / 1000
                d = tables.delta_isa(r["fl"], sat)
                f, fl = model.ff(r["fl"], w, m, d)
                flags |= {k_ for k_, v in fl.items() if v is True}
                mb += f * dt
                ws.append(w), ds.append(d), ms.append(m)
        bg = s[0]["gwt0_kg"] - s[-1]["gwt1_kg"]
        bf = s[0]["fw0"] - s[-1]["fw1"]
        kg, kf = bg / mb, bf / mb
        se_g, se_f = 18.14 / math.sqrt(6) / bg, 100 / math.sqrt(6) / bf
        out.append(dict(group="MH371", item=f"MH371 FL{s[0]['fl']:.0f} {len(s) * 5} min", fl=round(s[0]["fl"]), mach=float(np.mean(ms)),
                        w_t=float(np.mean(ws)), w_hi=max(ws), w_lo=min(ws), disa=float(np.mean(ds)), observed=(bg + bf) / 2,
                        model=mb, quantity="burn kg", flags=",".join(sorted(flags)), kappa=math.sqrt(kg * kf),
                        kappa_flowmeter=kg, kappa_fqis=kf,
                        se=math.sqrt(((se_g + se_f) / 2) ** 2 + (0.5 * math.log(kg / kf)) ** 2)))
    return pd.DataFrame(out)


def re_fit(y, s, X=None):
    y, s = np.asarray(y, float), np.asarray(s, float)
    X = np.ones((len(y), 1)) if X is None else np.asarray(X, float)

    def beta_of(v):
        W = 1 / v
        return np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * y))

    def nll(ls):
        v = s**2 + np.exp(2 * ls)
        r = y - X @ beta_of(v)
        return 0.5 * np.sum(np.log(v) + r**2 / v)

    sr = math.exp(optimize.minimize_scalar(nll, bounds=(-12, -1), method="bounded").x) if len(y) > X.shape[1] else 0.0
    v = s**2 + sr**2
    cov = np.linalg.inv(X.T @ (X / v[:, None]))
    beta = cov @ (X.T @ (y / v))
    return beta, cov, sr


def dersimonian_laird(means, ses):
    y, v = np.log(means), np.asarray(ses) ** 2
    w = 1 / v
    mu_f = np.sum(w * y) / np.sum(w)
    Q = float(np.sum(w * (y - mu_f) ** 2))
    tau2 = max(0.0, (Q - (len(y) - 1)) / (np.sum(w) - np.sum(w**2) / np.sum(w)))
    ws = 1 / (v + tau2)
    return math.exp(np.sum(ws * y) / np.sum(ws)), math.sqrt(1 / np.sum(ws)), math.sqrt(tau2), Q


def calibration_set(df):
    """FL >= 250, M <= 0.84 (no drag rise), not below the tables. Extrapolation above LRC at
    FL250-290 (no M0.84 table there) and the back-side rule below the slowest schedule are kept:
    the filter flies both."""
    f = df["flags"].fillna("")
    return df[(df.fl >= 250) & (df.mach <= internal.M_DD) & ~f.str.contains("below_tables")]


def fit_c_hi(df, kappa_b):
    """Drag rise D = 1 + c (M - 0.84) (CL / 0.35)^q on the Boeing items above M0.84 at FL >= 250.
    CL at the item's mean weight (T3: segment mid-weight; T4: half the arc-1 fuel)."""
    hi = df[(df.group != "MH371") & (df.fl >= 250) & (df.mach > internal.M_DD)]
    dm = (hi.mach - internal.M_DD).values
    cl = np.array([internal.lift_coefficient(f, w, m) for f, w, m in zip(hi.fl, hi.w_t, hi.mach)])
    ratio = hi.kappa.values / kappa_b  # implied extra multiplier the drag rise must supply

    def resid(p):
        return np.log(ratio) - np.log1p(p[0] * dm * (cl / internal.CL_REF) ** p[1])

    p = optimize.least_squares(resid, [3.0, 2.0]).x
    r = resid(p)
    return float(p[0]), float(p[1]), float(np.std(r, ddof=2)), hi.item.tolist()


def run(sir_path=SIR_TXT, mh371_path=MH371, tables_path=ENGINE / "data/fuel-tables.json", temp="fppm"):
    sir = sources.parse_sir(Path(sir_path).read_text())
    tau = internal.tau_fppm if temp == "fppm" else internal.tau_none
    base = internal.Internal(tables_path, kappa=1.0, c_hi=0.0, temp=tau)
    b0 = boeing_items(base, sir)
    cal = calibration_set(b0)
    beta, cov, sr = re_fit(np.log(cal.kappa), cal.se)
    kappa_b = math.exp(beta[0])
    c_hi, q_hi, c_sd, c_items = fit_c_hi(b0, kappa_b)
    model = internal.Internal(tables_path, kappa=1.0, c_hi=c_hi, q_hi=q_hi, temp=tau)
    b = boeing_items(model, sir)
    m = mh371_items(model, mh371_path)
    items = pd.concat([b, m], ignore_index=True)
    cal = calibration_set(items)
    groups = {}
    for g, d in cal.groupby("group"):
        bb, cc, ss = re_fit(np.log(d.kappa), d.se)
        groups[g] = dict(n=len(d), kappa=math.exp(bb[0]), se=math.sqrt(cc[0, 0]), resid_sd=ss)
    bo = cal[cal.group != "MH371"]
    bb, cc, ss = re_fit(np.log(bo.kappa), bo.se)
    boeing = dict(n=len(bo), kappa=math.exp(bb[0]), se=math.sqrt(cc[0, 0]), resid_sd=ss)
    Xw = np.c_[np.ones(len(bo)), bo.w_t - W_REF]
    bw, cw, sw = re_fit(np.log(bo.kappa), bo.se, Xw)
    names = ["Boeing-T3", "Boeing-T4", "MH371"]
    mu, se_mu, tau_b, Q = dersimonian_laird([groups[n]["kappa"] for n in names], [groups[n]["se"] for n in names])
    out = dict(
        temperature_rule=temp, c_hi=c_hi, q_hi=q_hi, c_hi_resid_sd=c_sd, c_hi_items=c_items,
        boeing=boeing, boeing_weight_slope_per_10t=float(bw[1] * 10), boeing_weight_slope_se=float(math.sqrt(cw[1, 1]) * 10),
        boeing_weight_resid_sd=sw, groups=groups,
        joint=dict(kappa=mu, se=se_mu, tau_between=tau_b, Q=Q, factor_prior_sd=math.sqrt(se_mu**2 + tau_b**2)),
        audit_convention_factor_boeing=1 / boeing["kappa"], audit_convention_factor_joint=1 / mu)
    return items, out, model


def calibrate_model(model, cal_tab):
    """Recompute the groups and the joint factor for a given model (the grid), with c_hi from cal_tab."""
    sir = sources.parse_sir(SIR_TXT.read_text())
    items = pd.concat([boeing_items(model, sir), mh371_items(model, MH371)], ignore_index=True)
    cal = calibration_set(items)
    groups = {}
    for g, d in cal.groupby("group"):
        bb, cc, ss = re_fit(np.log(d.kappa), d.se)
        groups[g] = dict(n=len(d), kappa=math.exp(bb[0]), se=math.sqrt(cc[0, 0]), resid_sd=ss)
    bo = cal[cal.group != "MH371"]
    bb, cc, ss = re_fit(np.log(bo.kappa), bo.se)
    Xw = np.c_[np.ones(len(bo)), bo.w_t - W_REF]
    bw, cw, sw = re_fit(np.log(bo.kappa), bo.se, Xw)
    names = ["Boeing-T3", "Boeing-T4", "MH371"]
    mu, se_mu, tau_b, Q = dersimonian_laird([groups[n]["kappa"] for n in names], [groups[n]["se"] for n in names])
    out = dict(model="grid", temperature_rule=cal_tab["temperature_rule"], c_hi=cal_tab["c_hi"], q_hi=cal_tab["q_hi"],
               c_hi_resid_sd=cal_tab["c_hi_resid_sd"], c_hi_items=cal_tab["c_hi_items"],
               boeing=dict(n=len(bo), kappa=math.exp(bb[0]), se=math.sqrt(cc[0, 0]), resid_sd=ss),
               boeing_weight_slope_per_10t=float(bw[1] * 10), boeing_weight_slope_se=float(math.sqrt(cw[1, 1]) * 10),
               groups=groups, joint=dict(kappa=mu, se=se_mu, tau_between=tau_b, Q=Q, factor_prior_sd=math.sqrt(se_mu**2 + tau_b**2)),
               audit_convention_factor_boeing=1 / math.exp(bb[0]), audit_convention_factor_joint=1 / mu)
    return items, out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    res = {}
    for temp in ("fppm", "none"):
        items, out, _ = run(*(args[:2] if args else ()), temp=temp)
        res[temp] = out
        items.assign(temperature_rule=temp).to_csv(OUT / f"internal-calibration-items-{temp}.csv", index=False, float_format="%.6g")
    (OUT / "internal-calibration.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in res.items():
        print(k, json.dumps(v["joint"]), "boeing", json.dumps(v["boeing"]))


if __name__ == "__main__":
    main()
