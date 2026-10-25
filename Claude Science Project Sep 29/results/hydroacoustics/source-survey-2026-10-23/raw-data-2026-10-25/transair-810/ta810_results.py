"""Transair 810 results tables from saved intermediates (deterministic). Writes out/tables/*.csv and out/summary.json.
eta relation = step2_invert.py (unchanged): eta = SE / [E rho c/(2 pi) sum_b W_b s_b(tau, slope) 10^(-TL_b/10)], bands 5-63 Hz
third octaves, W63, band_fraction from imos_stageB_map. Reproduction check: CV02 = 2.26e-3 from the module F-35A files."""
import sys, json, glob, pathlib
import numpy as np, pandas as pd
from scipy.optimize import curve_fit
WS = pathlib.Path(__file__).resolve().parent.parent; MOD = WS / "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sys.path.insert(0, str(MOD / "prepare")); from imos_stageB_map import band_fraction
OUT = WS / "out/tables"; OUT.mkdir(parents=True, exist_ok=True)
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
W63 = (64.0 - 63.0 / 2 ** (1 / 6)) / (63.0 * 2 ** (1 / 6) - 63.0 / 2 ** (1 / 6)); Wb = np.array([W63 if f == 63.0 else 1.0 for f in BANDS]); RHO_C = 1025.0 * 1500.0
TRI = ["H11N", "H11S"]
def sb(tau, slope): return np.array([float(band_fraction(fc, np.array([1.0 / tau]), slope)[0]) for fc in BANDS])
def eta(se, tl, E, tau, slope):
    ok = np.isfinite(tl); return float(se / (E * RHO_C / (2 * np.pi) * np.sum((Wb * sb(tau, slope) * 10 ** (-tl / 10))[ok])))
# ---------------- reproduction check (CV02)
d = pd.read_csv(MOD / "results-data/ram_check/ram_vs_kraken.csv"); d = d[d.path == "f35a_H11S"]
def f35_delta(zs):
    g = d[np.isclose(d.src_depth_m, 30.0 if zs == 30.0 else 10.0)].sort_values("fc_hz"); c = (g.tl_ram_db - g.tl_kraken_db).values
    return np.interp(np.log(BANDS), np.log(g.fc_hz.values), c, left=c[0], right=c[-1])
TL2 = pd.read_csv(MOD / "results-data/metz_f35a/step2_tl.csv"); O = json.load(open(MOD / "results-data/metz_f35a/obs_summary.json"))["triads"]
cv02 = float(np.exp(np.mean([np.log(eta(O[s]["se_pa2s"], TL2[(TL2.path == f"f35a-{s}") & np.isclose(TL2.src_depth_m, 10.0)].set_index("fc_hz").reindex(BANDS).tl_db.values + f35_delta(10.0), 900e6, 10.0, 2.0)) for s in TRI])))
# ---------------- energies (Monte Carlo, NTSB inputs)
rng = np.random.default_rng(2021); N = 200000; LB = 0.45359237; KT = 1852 / 3600
m = (93557 - rng.uniform(300, 1500, N)) * LB; gs = rng.normal(114.6, 2.0, N) * KT; vz = rng.uniform(3.8, 6.5, N)
KE = 0.5 * m * (gs ** 2 + vz ** 2); KEv = 0.5 * m * vz ** 2
q = lambda a: [float(x) for x in np.quantile(a, [0.05, 0.5, 0.95])]
EN = dict(mass_t=q(m / 1e3), groundspeed_ms=q(gs), vertical_speed_ms=q(vz), KE_total_MJ=q(KE / 1e6), KE_vertical_MJ=q(KEv / 1e6))
# ---------------- detection: observed windows, L50
obs = pd.read_csv(WS / "out/observed_windows.csv"); R = pd.read_csv(WS / "out/injection_results.csv")
meta = json.load(open(WS / "out/f35a_templates.json")); M = meta["meta"]; chk = {c["element"]: c for c in meta["check"]}
OB = pd.read_csv(WS / "inputs/pkg/coupling-db-package/db_received_observation.csv").set_index("station")
ratio = {t: float(OB.loc[f"{t}1", "exposure_Pa2s_30s"] / chk[f"{t}1"]["se_5_40_pa2s"]) for t in TRI}
kse = {t: M[t]["wave_se_pm15"] / M[t]["wave_rms_peak"] ** 2 for t in TRI}
evn = {t: float(obs[(obs.triad == t) & (obs.window == "PW")].noise_rms1s_median_pa.iloc[0]) for t in TRI}
def logistic(x, m_, s, c, f): return f + (c - f) / (1 + np.exp(-(x - m_) / s))
def l50(sub, thr):
    g = sub[sub.kind == "grid"].groupby("level")["p_M1b"].apply(lambda p: float((p < thr).mean())); x = np.log10(g.index.values); y = g.values
    f0 = float((sub[sub.kind == "zero"].p_M1b < thr).mean())
    (m_, s, c), _ = curve_fit(lambda x, m_, s, c: logistic(x, m_, s, c, f0), x, y, p0=[np.log10(0.05), 0.1, 0.9], bounds=([-3, 0.01, 0.5], [0, 1, 1]))
    return float(10 ** (m_ - s * np.log((c - f0) / (0.5 - f0) - 1))), float(c), f0
rows = []
for t in TRI:
    a = R[R.tri == t]; nm = a[(np.abs(20 * np.log10(a.noise_pa / evn[t])) <= 1.5) | (a.kind == "zero")]
    for cond, sub in (("pre-registered (14 days)", a), ("noise within 1.5 dB of event day (sensitivity)", nm)):
        for thr, lab in ((0.05, "report"), (0.1, "mark"), (0.3, "screen")):
            L, c, f0 = l50(sub, thr)
            rows.append(dict(triad=t, condition=cond, label=lab, p_threshold=thr, L50_rms1s_pa=L, pd_ceiling=c, pd_no_injection=f0,
                             SE50_4_40_pa2s=L ** 2 * kse[t] * ratio[t], n_injections=int((sub.kind == "grid").sum())))
L50 = pd.DataFrame(rows); L50.to_csv(OUT / "detection_probability_L50.csv", index=False)
pd_curve = R[R.kind != "zero"].groupby(["tri", "kind", "level"]).agg(pd_report=("p_M1b", lambda p: float((p < 0.05).mean())), pd_mark=("p_M1b", lambda p: float((p < 0.1).mean())),
          pd_screen=("p_M1b", lambda p: float((p < 0.3).mean())), pd_D1_report=("p_D1", lambda p: float((p < 0.05).mean())), n=("p_M1b", "size")).reset_index()
pd_curve.to_csv(OUT / "detection_probability_curve.csv", index=False)
# ---------------- TL and RAM delta
TLT = pd.read_csv(WS / "out/tl/ta810_tl.csv")
ram = pd.DataFrame([json.load(open(f)) for f in glob.glob(str(WS / "out/tl/ram/*.json"))]); ram.to_csv(OUT / "ram_vs_kraken_transair.csv", index=False)
def ram_delta(t):
    g = ram[(ram.tag == f"ta810s3km-{t}") & np.isclose(ram.src_depth_m, 10.0) & np.isfinite(ram.ram_minus_kraken_db)]
    src = t
    if len(g) < 3:      # declared: H11S offset-path delta stands in where H11N has fewer than 3 bands
        g2 = ram[(ram.tag == "ta810s3km-H11S") & np.isclose(ram.src_depth_m, 10.0)]; g = pd.concat([g, g2[~g2.fc_hz.isin(g.fc_hz)]]); src = f"{t} + H11S fill"
    g = g.sort_values("fc_hz"); return np.interp(np.log(BANDS), np.log(g.fc_hz.values), g.ram_minus_kraken_db.values, left=g.ram_minus_kraken_db.values[0], right=g.ram_minus_kraken_db.values[-1]), src, g.fc_hz.tolist()
RD = {t: ram_delta(t) for t in TRI}
ZS = [0.5, 1.0, 2.0, 5.0, 10.0]; TAUS = [0.3, 1.0, 3.0, 10.0]
E_OPT = {"KE_total": EN["KE_total_MJ"][1] * 1e6, "KE_vertical": EN["KE_vertical_MJ"][1] * 1e6}
U = []
for _, lr in L50[L50.label == "report"].iterrows():
    t = lr.triad
    for se_ in ("ta810s3km", "ta810s6km", "ta810s10km"):
        for zs in ZS:
            tlk = TLT[(TLT.path == f"{se_}-{t}") & np.isclose(TLT.src_depth_m, zs)].set_index("fc_hz").reindex(BANDS).tl_db.values.astype(float)
            for chain, tl in (("MODULE_KRAKEN_ONLY", tlk), ("MODULE_KRAKEN_RAM", tlk + RD[t][0])):
                for slope in (2.0, 4.0):
                    for tau in TAUS:
                        for ek, E in E_OPT.items():
                            U.append(dict(triad=t, L50_condition=lr.condition, source_end=se_.replace("ta810", "").replace("s", "seaward ").replace("km", " km"), z_eff_m=zs,
                                          chain=chain, slope=slope, tau_s=tau, energy=ek, E_J=E, SE50_pa2s=lr.SE50_4_40_pa2s, eta_rad_UL50=eta(lr.SE50_4_40_pa2s, tl, E, tau, slope)))
U = pd.DataFrame(U); U.to_csv(OUT / "eta_rad_upper_limit_grid.csv", index=False)
prim = U[(U.L50_condition.str.startswith("pre")) & (U.source_end == "seaward 3 km") & (U.chain == "MODULE_KRAKEN_RAM") & (U.slope == 2.0) & (U.tau_s == 1.0) & (U.energy == "KE_total")]
# energy uncertainty (90 %) and source-end spread
spread = []
for t in TRI:
    for zs in ZS:
        s = U[(U.triad == t) & (U.z_eff_m == zs) & (U.L50_condition.str.startswith("pre")) & (U.chain == "MODULE_KRAKEN_RAM") & (U.slope == 2.0) & (U.tau_s == 1.0) & (U.energy == "KE_total")]
        p0 = float(s[s.source_end == "seaward 3 km"].eta_rad_UL50.iloc[0])
        spread.append(dict(triad=t, z_eff_m=zs, eta_UL50=p0, eta_UL50_E_low=p0 * EN["KE_total_MJ"][1] / EN["KE_total_MJ"][2], eta_UL50_E_high=p0 * EN["KE_total_MJ"][1] / EN["KE_total_MJ"][0],
                           source_end_min=float(s.eta_rad_UL50.min()), source_end_max=float(s.eta_rad_UL50.max()),
                           slope4=float(U[(U.triad == t) & (U.z_eff_m == zs) & (U.L50_condition.str.startswith("pre")) & (U.source_end == "seaward 3 km") & (U.chain == "MODULE_KRAKEN_RAM") & (U.slope == 4.0) & (U.tau_s == 1.0) & (U.energy == "KE_total")].eta_rad_UL50.iloc[0]),
                           kraken_only=float(U[(U.triad == t) & (U.z_eff_m == zs) & (U.L50_condition.str.startswith("pre")) & (U.source_end == "seaward 3 km") & (U.chain == "MODULE_KRAKEN_ONLY") & (U.slope == 2.0) & (U.tau_s == 1.0) & (U.energy == "KE_total")].eta_rad_UL50.iloc[0]),
                           vertical_KE=float(U[(U.triad == t) & (U.z_eff_m == zs) & (U.L50_condition.str.startswith("pre")) & (U.source_end == "seaward 3 km") & (U.chain == "MODULE_KRAKEN_RAM") & (U.slope == 2.0) & (U.tau_s == 1.0) & (U.energy == "KE_vertical")].eta_rad_UL50.iloc[0]),
                           tau_0p3=float(U[(U.triad == t) & (U.z_eff_m == zs) & (U.L50_condition.str.startswith("pre")) & (U.source_end == "seaward 3 km") & (U.chain == "MODULE_KRAKEN_RAM") & (U.slope == 2.0) & (U.tau_s == 0.3) & (U.energy == "KE_total")].eta_rad_UL50.iloc[0])))
SP = pd.DataFrame(spread)
ridge = {2.0: 0.054, 10.0: 0.00226, 30.0: 0.00034}       # CV01-CV03 (E01, KRAKEN+RAM, slope 2)
lz = np.log(list(ridge)); lv = np.log(list(ridge.values()))
SP["F35A_ridge_same_z"] = np.exp(np.interp(np.log(SP.z_eff_m), lz, lv, left=None, right=None)); SP.loc[SP.z_eff_m < 2, "F35A_ridge_same_z"] = np.exp(lv[0] + (lv[1] - lv[0]) / (lz[1] - lz[0]) * (np.log(SP.z_eff_m[SP.z_eff_m < 2]) - lz[0]))
SP["UL_over_F35A_ridge"] = SP.eta_UL50 / SP.F35A_ridge_same_z; SP["UL_over_raindrop_1e-5"] = SP.eta_UL50 / 1e-5; SP["UL_over_iceblock_8e-7"] = SP.eta_UL50 / 8e-7
SP.to_csv(OUT / "eta_rad_upper_limit_primary.csv", index=False)
summ = dict(cv02_reproduced=cv02, energies=EN, exposure_ratio_4_40_over_5_40=ratio, template_se_over_rms2_s=kse, event_noise_rms_pa=evn,
            ram_delta_db={t: dict(values=[float(v) for v in RD[t][0]], source=RD[t][1], bands_run=RD[t][2]) for t in TRI})
json.dump(summ, open(WS / "out/summary.json", "w"), indent=1)
pd.set_option("display.width", 250)
print("CV02 reproduced %.4e" % cv02); print(json.dumps(EN)); print(L50.round(4).to_string(index=False)); print(SP.to_string(float_format="%.3g")); print({t: (RD[t][1], RD[t][2], np.round(RD[t][0], 2).tolist()) for t in TRI})
