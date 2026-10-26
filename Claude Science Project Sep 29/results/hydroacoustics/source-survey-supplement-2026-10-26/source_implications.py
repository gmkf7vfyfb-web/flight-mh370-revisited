"""Source implications of the near-field (Metz Fig. 2) and far-field (Fig. 3) F-35A records, through the module TL.
(1) Implied source spectral slope: band excess level + TL(f, z_s) regressed on log2 f over third-octave bands 5-40 Hz with
    signal - noise >= 3 dB (route-2 rule of metz_f35a/step2_invert.py). Reported as band-energy slope (route-2 units) and
    ESD slope (= band-energy slope - 3.01 dB/octave). TL: KRAKEN (module chain) for near and far, so near/far are like-for-like.
(2) Near-field coupling, definition class D1 (project relation of step2_invert.py, unchanged):
    eta = SE_rx / [E rho c / (2 pi) * sum_b W_b s_b(tau, slope) 10^(-TL_b/10)], bands 5-40 Hz (W_40 = share of the 40 Hz
    third octave below 40 Hz, as W63 for 64 Hz), SE_rx = 4-40 Hz exposure of the digitised 1-s RMS envelope.
Usage: python source_implications.py <out_dir> <hydro_module_dir>
"""
import sys, json, pathlib
import numpy as np, pandas as pd
out, mod = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
sys.path.insert(0, str(mod / "prepare" / "metz_f35a")); sys.path.insert(0, str(mod / "prepare"))
import prereg as R
from imos_stageB_map import band_fraction
B5_40 = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
W40 = (40.0 - 40.0 / 2 ** (1 / 6)) / (40.0 * 2 ** (1 / 6) - 40.0 / 2 ** (1 / 6))
W = np.array([W40 if f == 40.0 else 1.0 for f in B5_40])
BS = pd.read_csv(out / "metz-band-spectra.csv"); DV = pd.read_csv(out / "metz-nearfield-derived.csv")
TN = pd.read_csv(out / "tl" / "nearfield_tl.csv"); TN = TN[TN.status.str.startswith("ok") & np.isfinite(TN.tl_db)]
TF = pd.read_csv(mod / "results-data/metz_f35a/step2_tl.csv"); TF = TF[TF.path.isin(["f35a-H11N", "f35a-H11S"])]
def tlv(st, z, src="P", bottom="hard"):
    if st.startswith("H11"):
        g = TF[(TF.path == f"f35a-{st[:4]}") & np.isclose(TF.src_depth_m, z)].set_index("fc_hz").tl_db
    else:
        g = TN[(TN.station == st) & (TN.source == src) & (TN.bottom == bottom) & np.isclose(TN.src_depth_m, z)].set_index("fc_hz").tl_db
    return np.array([g.get(f, np.nan) for f in B5_40])
def fit(x, y):
    ok = np.isfinite(y); x, y = x[ok], y[ok]
    if len(x) < 3: return np.nan, np.nan, len(x)
    A = np.vstack([np.ones_like(x), x]).T; c, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ c
    return float(c[1]), float(np.sqrt(np.sum(r ** 2) / max(len(y) - 2, 1) * np.linalg.inv(A.T @ A)[1, 1])), int(len(x))
rows = []
cases = [(st, "P", b) for st in ("DSOH", "KSP1", "KSP2", "KSP3") for b in ("hard", "soft")] + [(st, "W", "hard") for st in ("DSOH", "KSP1", "KSP2", "KSP3")] + [(st, "-", "hard") for st in ("H11N1", "H11S1")]
for st, src, bot in cases:
    fills = (90.0, 80.0) if not st.startswith("H11") else (80.0, 70.0)
    for fill in fills:
        b = BS[(BS.station == st) & np.isclose(BS.floor_fill_db, fill)].set_index("fc_hz").reindex(B5_40)
        keep = (b.sig_psd_db - b.noise_psd_db >= 3.0).values
        x = np.log2(np.array(B5_40))
        for z in R.SRC_DEPTHS:
            tl = tlv(st, z, src, bot)
            y = np.where(keep, b.excess_psd_db.values + tl, np.nan)                  # source ESD level (dB re 1 uPa^2 s/Hz @1 m, relative)
            s_esd, se, n = fit(x, y)
            s_tl, _, _ = fit(x, -tl)
            rows.append(dict(station=st, field="far" if st.startswith("H11") else "near", source_point=src, bottom=bot, floor_fill_db=fill,
                             src_depth_m=z, n_bands=n, rx_excess_esd_slope=fit(x, np.where(keep, b.excess_psd_db.values, np.nan))[0],
                             tl_gain_slope=s_tl, src_esd_slope_db_oct=s_esd, src_esd_slope_se=se, src_band_energy_slope_db_oct=s_esd + 3.0103,
                             minus_f2_offset_db_oct=s_esd - (-6.0206), minus_f4_offset_db_oct=s_esd - (-12.0412)))
S = pd.DataFrame(rows); S.to_csv(out / "metz-source-slope.csv", index=False)
# near vs far, per depth (primary: P, hard, colour-floor fill)
prim = S[((S.field == "near") & (S.source_point == "P") & (S.bottom == "hard") & (S.floor_fill_db == 90.0)) | ((S.field == "far") & (S.floor_fill_db == 80.0))]
summ = {}
for z in R.SRC_DEPTHS:
    n = prim[(prim.field == "near") & np.isclose(prim.src_depth_m, z)]; f = prim[(prim.field == "far") & np.isclose(prim.src_depth_m, z)]
    wn = 1 / n.src_esd_slope_se ** 2; wf = 1 / f.src_esd_slope_se ** 2
    mn = float((n.src_esd_slope_db_oct * wn).sum() / wn.sum()); sn = float(np.sqrt(1 / wn.sum()))
    mf = float((f.src_esd_slope_db_oct * wf).sum() / wf.sum()); sf = float(np.sqrt(1 / wf.sum()))
    summ[f"{z:g}"] = dict(near_mean=mn, near_se=sn, near_station_range=[float(n.src_esd_slope_db_oct.min()), float(n.src_esd_slope_db_oct.max())],
                          far_mean=mf, far_se=sf, near_minus_far=mn - mf, near_minus_far_z=(mn - mf) / np.hypot(sn, sf),
                          near_tl_gain_slope=float(n.tl_gain_slope.mean()), far_tl_gain_slope=float(f.tl_gain_slope.mean()))
# ---------------- coupling (D1)
TAUS = [0.1, 0.3, 1.1, 3.3, 10.0]
er = []
for st in ("DSOH", "KSP1", "KSP2", "KSP3"):
    d = DV[(DV.station == st) & np.isclose(DV.floor_fill_db, 90.0)].iloc[0]
    # SE with the pre-onset noise definition (sensitivity)
    E_ = pd.read_csv(out / f"metz-fig2-digitised-{st}.csv"); t, L = E_.utc_s_of_day.values, E_.rms_db_re_1uPa.values
    se_pre = None
    Ln = d.noise_pre_onset_db; ex = np.clip(10 ** (L / 10) - 10 ** (Ln / 10), 0, None); m = (t >= d.onset_utc_s - 1.0) & (L > Ln + 1.0)
    se_pre = float(ex[m].sum() * 0.02 * 1e-12)
    for src, bot in (("P", "hard"), ("P", "soft"), ("W", "hard")):
        for z in R.SRC_DEPTHS:
            tl = tlv(st, z, src, bot)
            for slope in (2.0, 4.0):
                for tau in TAUS:
                    s = np.array([float(band_fraction(fc, np.array([1.0 / tau]), slope)[0]) for fc in B5_40])
                    for ek, E in R.E_J.items():
                        den = E * R.RHO_C / (2 * np.pi) * np.nansum(W * s * 10 ** (-tl / 10))
                        for nd, se in (("obs_py", float(d.se_pa2s)), ("pre_onset", se_pre)):
                            er.append(dict(station=st, source_point=src, bottom=bot, src_depth_m=z, slope=slope, tau_s=tau, E=ek, noise_def=nd,
                                           se_pa2s=se, eta=se / den, definition="D1: one-pole ESD normalised 1-500 Hz, KRAKEN TL with surface image at z_s, 4-40 Hz exposure / KE"))
ER = pd.DataFrame(er); ER.to_csv(out / "metz-nearfield-eta.csv", index=False)
gm = lambda x: float(np.exp(np.log(x).mean()))
q = lambda **k: ER[np.logical_and.reduce([np.isclose(ER[c], v) if isinstance(v, float) else (ER[c] == v) for c, v in k.items()])]
FE = pd.read_csv(mod / "results-data/metz_f35a/step2_eta.csv")
far = lambda z, tl, slope=2.0: gm(FE[(FE.path == "primary") & np.isclose(FE.src_depth_m, z) & (FE.tl == tl) & np.isclose(FE.tau_s, 1.1, atol=0.01) & (FE.slope == slope) & (FE.E == "mid")].eta)
eta = {}
for z in R.SRC_DEPTHS:
    p = q(source_point="P", bottom="hard", src_depth_m=z, slope=2.0, tau_s=1.1, E="mid", noise_def="obs_py")
    eta[f"{z:g}"] = dict(near_primary=gm(p.eta), near_by_station={r.station: float(r.eta) for r in p.itertuples()},
                         near_station_spread_factor=float(p.eta.max() / p.eta.min()),
                         near_soft_bottom=gm(q(source_point="P", bottom="soft", src_depth_m=z, slope=2.0, tau_s=1.1, E="mid", noise_def="obs_py").eta),
                         near_working_point=gm(q(source_point="W", bottom="hard", src_depth_m=z, slope=2.0, tau_s=1.1, E="mid", noise_def="obs_py").eta),
                         near_pre_onset_noise=gm(q(source_point="P", bottom="hard", src_depth_m=z, slope=2.0, tau_s=1.1, E="mid", noise_def="pre_onset").eta),
                         near_slope4=gm(q(source_point="P", bottom="hard", src_depth_m=z, slope=4.0, tau_s=1.1, E="mid", noise_def="obs_py").eta),
                         near_tau={f"{t:g}": gm(q(source_point="P", bottom="hard", src_depth_m=z, slope=2.0, tau_s=t, E="mid", noise_def="obs_py").eta) for t in TAUS},
                         far_kraken=far(z, "kraken"), far_ram=far(z, "ram"), far_kraken_slope4=far(z, "kraken", 4.0),
                         near_over_far_kraken=gm(p.eta) / far(z, "kraken"),
                         near_over_far_kraken_slope4=gm(q(source_point="P", bottom="hard", src_depth_m=z, slope=4.0, tau_s=1.1, E="mid", noise_def="obs_py").eta) / far(z, "kraken", 4.0))
json.dump(dict(slope_near_vs_far=summ, eta=eta, W40=W40), open(out / "metz-source-implications.json", "w"), indent=1)
print(json.dumps(summ, indent=0)); print(json.dumps(eta, indent=0))
# ---------------- in-band (D4) radiated energy 5-40 Hz third octaves: E_ac = 2 pi / (rho c) * sum_b SE_rx_b 10^(TL_b/10)
d4 = {}
RB = pd.read_csv(mod / "results-data/metz_f35a/step2_routeB.csv")
for z in R.SRC_DEPTHS:
    vals = {}
    for st in ("DSOH", "KSP1", "KSP2", "KSP3"):
        b = BS[(BS.station == st) & np.isclose(BS.floor_fill_db, 90.0)].set_index("fc_hz").reindex(B5_40)
        bw = np.array([f * (2 ** (1 / 6) - 2 ** (-1 / 6)) for f in B5_40]); wgt = W * bw * 10 ** (b.excess_psd_db.values / 10)
        share = wgt / wgt.sum(); se = float(DV[(DV.station == st) & np.isclose(DV.floor_fill_db, 90.0)].se_pa2s.iloc[0])
        tl = tlv(st, z, "P", "hard"); ok = np.isfinite(tl)
        vals[st] = float(2 * np.pi / R.RHO_C * np.sum((share * se * 10 ** (tl / 10))[ok]) / R.E_J["mid"])
    far_ = {}
    for el in ("H11N1", "H11S1"):
        g = RB[(RB.element == el) & np.isclose(RB.floor_db, 80.0) & np.isclose(RB.src_depth_m, z) & (RB.tl == "kraken") & (RB.fc_hz > 0) & (RB.fc_hz <= 40.0)]
        far_[el] = float(2 * np.pi / R.RHO_C * np.sum(g.se_rx_pa2s * 10 ** (g.tl_db / 10)) / R.E_J["mid"])
    d4[f"{z:g}"] = dict(near_by_station=vals, near_gm=gm(list(vals.values())), near_gm_excl_KSP2=gm([v for k, v in vals.items() if k != "KSP2"]),
                        far_kraken_5_40=far_, far_gm=gm(list(far_.values())))
J = json.load(open(out / "metz-source-implications.json")); J["eta_D4_in_band_5_40"] = d4; json.dump(J, open(out / "metz-source-implications.json", "w"), indent=1)
print(json.dumps(d4, indent=0))
