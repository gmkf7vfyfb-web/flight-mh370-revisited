"""EXPLORATORY planning analysis (9 Oct; not a test, no recorded data examined beyond the stage A fits and
the 2b noise medians). Per-sample received SNR at the IMOS loggers AND at H01W/H08S, using EXACTLY stage C's
draws (f35a_eta_calibration.stage_c: seed, prior, tau, V, z_s, C_site, C_rcv), the RAM-corrected eta_cal
and IMOS TL (results-data/ram_check), and for H01W/H08S the stage-B-style KRAKEN TL on the five impact
quantile paths corrected by the RAM Delta of the median path. IMS noise: PROXY = the 3376 background median
1 s 5-40 Hz SPL (2b), with -5 / 0 / +5 dB variants; no IMS noise measurement is held. IMS P_D: PROXY = the
stage A logistic fit at 3274 (the quieter IMOS logger), with and without a triad gain of +4.8 dB."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
P = Path(sys.argv[1]); sys.path.insert(0, str(P))
import f35a_eta_calibration as F, imos_stageB_map as B, imos_preregistration as PR, imos_detectors as D
ram, ims, out = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]); sa_json, summary = sys.argv[5], sys.argv[6]
HERE = F.HERE
fits = json.loads(Path(sa_json).read_text())["fits"]
bmed = json.loads((HERE / "results-data/imos2b/summary.json").read_text())["background_spl_median"]
bm = lambda lg: bmed[lg] if lg in bmed else bmed[str(int(lg))]
meta = PR.parse_meta(); recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
teff = B.t_eff(meta, recs, None)
req = json.loads((HERE / "data/ocean_paths/request.json").read_text())
qlat = {p["name"][3:6]: p["a"][1] for p in req["paths"] if p["name"].startswith("imp")}
qs = sorted(qlat, key=lambda k: qlat[k]); xs = np.array([qlat[k] for k in qs])
rng = np.random.default_rng(B.SEED)
ridge, grid, dens, _ = PR.sct.ridge_and_marginal(summary); q, _ = PR.sct.fit_small_circle(ridge)
pr = PR.sct.draw_prior(np.random.default_rng(PR.sct.SEED), q, grid, dens, B.N_S, PR.sct.BASE["sigma_x_nm"]); n = len(pr)
t_imp = PR.sct.BASE["mu_t_s"] + rng.normal(0, PR.sct.BASE["sigma_t_s"], n); c = rng.normal(PR.C_G, PR.SD_C, n)
_ = rng.uniform(size=n); tau = 10 ** rng.uniform(np.log10(0.05), np.log10(10), n)
V = rng.choice([120.0, 160.0, 200.0], n); zs = rng.choice([2.0, 10.0, 30.0], n)
c_site, c_rcv = rng.normal(0, 10, n), rng.normal(0, 10, n)
cal = pd.read_csv(ram / "eta_cal_ramcorr.csv"); tab = F.eta_cal_lookup(cal, 2)
eta = np.zeros(n)
for z, (lx, ly) in tab.items():
    m = zs == z; eta[m] = 10 ** np.interp(np.log10(tau[m]), lx, ly)
SE1 = eta * 0.5 * B.M_REF * V ** 2 * B.RHO_C / (2 * np.pi)
bands = F.BANDS; Sb = {fc: B.band_fraction(fc, 1 / tau, 2) for fc in bands}
def se_from(tlget):
    SE = np.zeros(n)
    for fc in bands:
        tlb = np.zeros(n)
        for z in F.SRC:
            mz = zs == z; tlb[mz] = np.interp(pr[mz, 0], xs, tlget(fc, z))
        SE += SE1 * Sb[fc] * np.nan_to_num(10 ** (-tlb / 10), nan=0.0)
    return SE
# IMOS
tl = pd.read_csv(ram / "imos_tl_ramcorr.csv", dtype={"quantile": str, "logger": str})
ref = (PR.T_IMPACT_REF - D.DAY0).total_seconds()
res = {}
for lg in B.LOGGERS:
    g = tl[tl.logger == lg]
    SE = se_from(lambda fc, z: g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("quantile").tl_db[qs].values)
    mm = meta[lg]; _, _, d = PR.GEOD.inv(np.full(n, mm["lon"]), np.full(n, mm["lat"]), pr[:, 1], pr[:, 0]); ta = ref + t_imp + d / 1000 / c
    r = recs[recs.logger == int(lg)]
    st = np.array([((t + pd.Timedelta(seconds=D.subsec(PR.IMOS / f))) - pd.Timedelta(seconds=PR.clock_err(mm, t)) - D.DAY0).total_seconds() for t, f in zip(r.start_logger, r.file)])
    cov = np.zeros(n, bool)
    for a, b in zip(st + 32, st + r.dur_s.values - 1): cov |= (ta >= a) & (ta <= b)
    snr0 = 10 * np.log10(np.maximum(SE, 1e-300) / teff["T_C2"] / 1e-12) - bm(lg)
    res[lg] = dict(snr0=snr0, cov=cov)
# IMS
kt = pd.read_csv(ims / "ims_tl_kraken.csv", dtype={"quantile": str}); rd = pd.read_csv(ims / "ims_ram_delta.csv")
for stn in ["H01W", "H08S"]:
    g = kt[kt.station == stn]; dd = rd[rd.path == f"imp500_{stn}"]
    def tlget(fc, z, g=g, dd=dd):
        zz = 30.0 if z >= 30 else 10.0; h = dd[np.isclose(dd.src_depth_m, zz)].set_index("fc_hz").delta_db
        delta = float(np.interp(np.log10(fc), np.log10(h.index.values), h.values))
        return g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("quantile").tl_db[qs].values - delta
    SE = se_from(tlget)
    res[stn] = dict(snr0=10 * np.log10(np.maximum(SE, 1e-300) / teff["T_C2"] / 1e-12) - bm("3376"), cov=np.ones(n, bool))
def pdv(snr, lg, a):
    f = fits[f"{lg}|T_C2|or|{a}"]; s = max((f["snr90"] - f["snr50"]) / np.log(9), 0.05)
    return 1 / (1 + np.exp(-(snr - f["snr50"]) / s))
C = c_site + c_rcv
def imos_pd(a, cshift=None, cfix=False):
    pn = np.ones(n)
    for lg in B.LOGGERS:
        cc = np.zeros(n) if cfix else C
        snr = res[lg]["snr0"] + cc + (cshift or 0.0)
        pn *= 1 - res[lg]["cov"] * pdv(snr, B.TARGET[lg], a)
    return float((1 - pn).mean())
summ = {"imos": {
    "baseline_alpha0.005": imos_pd(0.005), "alpha0.05_single_window": imos_pd(0.05),
    "C_terms_fixed_0_alpha0.005": imos_pd(0.005, cfix=True), "C_terms_fixed_0_alpha0.05": imos_pd(0.05, cfix=True),
    "C_plus10dB_alpha0.005": imos_pd(0.005, 10.0), "C_plus10dB_alpha0.05": imos_pd(0.05, 10.0),
    "coverage_any": float(np.mean(np.any([res[lg]["cov"] for lg in B.LOGGERS], axis=0)))}}
ims_out = {}
Cs = c_site + rng.normal(0, 3, n)       # IMS receivers are SOFAR-axis like the calibration: C_rcv replaced by a 3 dB term (declared)
for stn in ["H01W", "H08S"]:
    o = {}
    for nv in [-5, 0, 5]:
        snr = res[stn]["snr0"] + Cs - nv
        o[f"noise{nv:+d}"] = dict(snr_q={k: float(np.quantile(snr, v)) for k, v in [("p05", .05), ("p25", .25), ("p50", .5), ("p75", .75), ("p95", .95)]},
                                  p_snr_gt={str(x): float((snr > x).mean()) for x in [0, 5, 10, 15, 20]},
                                  pd_proxy3274={f"{a}|gain{gn}": float(pdv(snr + gn, "3274", a).mean()) for a in (0.005, 0.05) for gn in (0.0, 4.8)})
    ims_out[stn] = o
both = {}
for nv in [-5, 0, 5]:
    s1 = res["H01W"]["snr0"] + Cs - nv; s2 = res["H08S"]["snr0"] + Cs - nv
    both[f"noise{nv:+d}"] = {f"{a}|gain{gn}": float((pdv(s1 + gn, "3274", a) * pdv(s2 + gn, "3274", a)).mean()) for a in (0.005, 0.05) for gn in (0.0, 4.8)}
    both[f"noise{nv:+d}"]["p_both_snr_gt_10"] = float(((s1 > 10) & (s2 > 10)).mean())
summ["ims"] = ims_out; summ["ims_both_pd_proxy"] = both
summ["notes"] = "EXPLORATORY; IMS noise and IMS P_D are proxies; C_site shared between H01W and H08S (same source)"
(out / "near_limits_summary.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ, indent=1))
