"""Item 3 STAGE B part 2: source energy -> stage-A SNR -> P_D at the open IMOS loggers, EXACTLY as fixed in
the pre-registration docstring of imos_stageB_tl.py (64752c7). Inputs: stage-B TL (imos_tl.csv), stage-A
P_D(SNR) logistic fits (summary.json of imos_injection.py), the 2b background medians, the stand-in impacts.
Implementation choices not spelled out in 64752c7, declared here (none changes the mapping):
  - TL between the five impact-quantile paths: linear in impact latitude, clamped at the ends, per logger,
    band and source depth.
  - T_eff = (template 5-40 Hz energy above the template's own noise) / (peak 1 s 5-40 Hz energy above noise),
    noise = median 1 s energy in the template's first 8 s (pre-arrival), from the stage-A templates at 3315.
  - Primary P_D curve: template T_C2, detector 'or', alpha 0.005; alpha 0.05 and T_C1 reported as alternatives.
  - Coverage: D1-scorable span of each recording (as imos_nondetection_bits.py), convention A clock.
Outputs: <out>/pd_by_eta.csv (P_D any-logger per eta decade, marginal over the rest), pd_by_latitude.csv,
  pd_samples_summary.json (eta at which marginal P_D = 0.5 and 0.1; P_D marginal over the eta prior).
Usage: python imos_stageB_map.py <out> <imos_tl.csv> <stageA_summary.json> <stand-in summary json>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_detectors as D  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402

HERE = Path(__file__).parent.parent
LOGGERS = ["3315", "3376", "3274", "3275"]
TARGET = {"3315": "3376", "3376": "3376", "3274": "3274", "3275": "3274"}
QLAT = {"025": None, "250": None, "500": None, "750": None, "975": None}
ETA_LO, ETA_HI = 2.1e-8, 2.1e-4
RHO_C = 1025.0 * 1500.0
M_REF = 2.0e5
SEED = 20261009
N_S = 200_000


def band_fraction(fc, f_r, slope):
    """Energy fraction in the third octave around fc for an ESD flat to f_r and ~ f^-slope above, over 1-500 Hz."""
    f = np.logspace(0, np.log10(500), 4000)
    esd = np.where(f[None, :] <= f_r[:, None], 1.0, (f[None, :] / f_r[:, None]) ** (-slope))
    tot = np.trapezoid(esd, f, axis=1)
    lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
    m = (f >= lo) & (f <= hi)
    return np.trapezoid(esd[:, m], f[m], axis=1) / tot


def t_eff(meta, recs, cal):
    from scipy import signal
    out = {}
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
    for name, hms in [("T_C2", "05:03:01"), ("T_C1", "01:33:44")]:
        t = D.DAY0 + pd.Timedelta(hms)
        for _, r in recs[recs.logger == 3315].iterrows():
            f = P.IMOS / r.file
            t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
            t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta["3315"], t0))
            s = (t - t0).total_seconds()
            xd = N.decimate(N.read_volts(f))
            if 10 <= s <= len(xd) / N.FS_D - 50:
                y = signal.sosfiltfilt(sos, xd[int((s - 10) * N.FS_D): int((s + 50) * N.FS_D)]) ** 2
                e1 = y[: len(y) // N.FS_D * N.FS_D].reshape(-1, N.FS_D).sum(1)
                noise = np.median(e1[:8])
                ex = np.clip(e1 - noise, 0, None)
                out[name] = float(ex.sum() / ex.max())
                break
    return out


def main(out_dir, tl_csv, sa_json, summary):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tl = pd.read_csv(tl_csv, dtype={"quantile": str, "logger": str})
    fits = json.loads(Path(sa_json).read_text())["fits"]
    bmed = json.loads((HERE / "results-data/imos2b/summary.json").read_text())["background_spl_median"]
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    teff = t_eff(meta, recs, None)
    req = json.loads((HERE / "data/ocean_paths/request.json").read_text())
    qlat = {p["name"][3:6]: p["a"][1] for p in req["paths"] if p["name"].startswith("imp")}
    rng = np.random.default_rng(SEED)
    ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
    q, _ = P.sct.fit_small_circle(ridge)
    pr = P.sct.draw_prior(np.random.default_rng(P.sct.SEED), q, grid, dens, N_S, P.sct.BASE["sigma_x_nm"])
    n = len(pr)
    t_imp = P.sct.BASE["mu_t_s"] + rng.normal(0, P.sct.BASE["sigma_t_s"], n)
    c = rng.normal(P.C_G, P.SD_C, n)
    eta = 10 ** rng.uniform(np.log10(ETA_LO), np.log10(ETA_HI), n)
    tau = 10 ** rng.uniform(np.log10(0.05), np.log10(10), n)
    V = rng.choice([120.0, 160.0, 200.0], n)
    zs = rng.choice([2.0, 10.0, 30.0], n)
    c_site, c_rcv = rng.normal(0, 10, n), rng.normal(0, 10, n)
    E_ac = eta * 0.5 * M_REF * V ** 2
    SE1 = E_ac * RHO_C / (2 * np.pi)
    bands = sorted(tl.fc_hz.unique())
    fr = 1 / tau
    ref = (P.T_IMPACT_REF - D.DAY0).total_seconds()
    qs = sorted(qlat, key=lambda k: qlat[k])
    res = {}
    for slope in [2, 4]:
        Sb = {fc: band_fraction(fc, fr, slope) for fc in bands}
        p_none = {k: np.ones(n) for k in ["or@0.005|T_C2", "or@0.05|T_C2", "or@0.005|T_C1"]}
        for lg in LOGGERS:
            m = meta[lg]
            _, _, d = P.GEOD.inv(np.full(n, m["lon"]), np.full(n, m["lat"]), pr[:, 1], pr[:, 0])
            ta = ref + t_imp + d / 1000 / c
            r = recs[recs.logger == int(lg)]
            st = np.array([((t + pd.Timedelta(seconds=D.subsec(P.IMOS / f))) - pd.Timedelta(seconds=P.clock_err(m, t)) - D.DAY0).total_seconds()
                           for t, f in zip(r.start_logger, r.file)])
            cov = np.zeros(n, bool)
            for a, b in zip(st + 32, st + r.dur_s.values - 1):
                cov |= (ta >= a) & (ta <= b)
            SE = np.zeros(n)
            for fc in bands:
                tlb = np.zeros(n)
                for z in [2.0, 10.0, 30.0]:
                    g = tl[(tl.logger == lg) & (tl.fc_hz == fc) & np.isclose(tl.src_depth_m, z)].set_index("quantile").tl_db
                    xs = np.array([qlat[k] for k in qs])
                    ys = np.array([g[k] for k in qs])
                    mz = zs == z
                    tlb[mz] = np.interp(pr[mz, 0], xs, ys)
                SE += SE1 * Sb[fc] * np.nan_to_num(10 ** (-tlb / 10), nan=0.0)   # 'no_modes' bands carry no energy
            SE *= 10 ** ((c_site + c_rcv) / 10)
            for key in p_none:
                det, tn = key.split("|")
                dname, a = det.split("@")
                f = fits[f"{TARGET[lg]}|{tn}|{dname}|{float(a)}"]
                spl = 10 * np.log10(SE / teff[tn] / 1e-12)
                snr = spl - bmed[lg] if lg in bmed else spl - bmed[str(int(lg))]
                s = max((f["snr90"] - f["snr50"]) / np.log(9), 0.05)
                pdv = 1 / (1 + np.exp(-(snr - f["snr50"]) / s))
                p_none[key] *= 1 - cov * pdv
        for key, pn in p_none.items():
            pdany = 1 - pn
            dec = np.floor(np.log10(eta))
            res[(slope, key)] = dict(
                pd_marginal=float(pdany.mean()),
                by_eta_decade={str(int(k)): float(pdany[dec == k].mean()) for k in np.unique(dec)},
                by_lat_bin={f"{lo:.1f}": float(pdany[(pr[:, 0] >= lo) & (pr[:, 0] < lo + 1)].mean())
                            for lo in np.arange(np.floor(pr[:, 0].min()), pr[:, 0].max(), 1.0) if ((pr[:, 0] >= lo) & (pr[:, 0] < lo + 1)).sum() > 500})
            # eta where marginal P_D crosses 0.5 and 0.1 (binned in 0.25 decade)
            edges = np.arange(np.log10(ETA_LO), np.log10(ETA_HI) + 0.25, 0.25)
            mids, vals = [], []
            for lo in edges[:-1]:
                mm = (np.log10(eta) >= lo) & (np.log10(eta) < lo + 0.25)
                mids.append(lo + 0.125); vals.append(pdany[mm].mean())
            vals = np.array(vals)
            for lvl in [0.1, 0.5]:
                k = np.flatnonzero(vals >= lvl)
                res[(slope, key)][f"eta_at_pd_{lvl}"] = float(10 ** mids[k[0]]) if len(k) else None
    rows = [dict(slope=s, curve=k, **{kk: v for kk, v in r.items() if not isinstance(v, dict)}) for (s, k), r in res.items()]
    pd.DataFrame(rows).to_csv(out / "pd_summary.csv", index=False)
    pd.DataFrame([dict(slope=s, curve=k, eta_decade=e, pd=v) for (s, k), r in res.items() for e, v in r["by_eta_decade"].items()]).to_csv(out / "pd_by_eta.csv", index=False)
    pd.DataFrame([dict(slope=s, curve=k, lat_bin=e, pd=v) for (s, k), r in res.items() for e, v in r["by_lat_bin"].items()]).to_csv(out / "pd_by_latitude.csv", index=False)
    (out / "pd_samples_summary.json").write_text(json.dumps(dict(t_eff_s=teff, n=n, results={f"{s}|{k}": r for (s, k), r in res.items()}), indent=1))
    print(json.dumps(dict(t_eff_s=teff), indent=1)); print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:5])
