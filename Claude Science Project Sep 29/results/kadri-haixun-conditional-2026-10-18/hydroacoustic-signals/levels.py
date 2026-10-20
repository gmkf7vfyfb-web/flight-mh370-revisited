"""Predicted received level, SNR and detection probability per station for run J impact rows in the locality L.
Source model (as kadri_predictions.py, module branch 77b4b49): SE = eta * E * rho c / (2 pi) * sum_b S_b(f_r = 1/tau, slope 2)
  * 10^(-TL_b/10), third-octave bands 5-40 Hz, source depth 10 m.  E = energy transferred (end of flight tau90_v1 sidecar,
  latent energy_transferred_j); tau = tau90 clamped 0.05-10 s.  eta swept 1e-4, 1e-3, 1e-2, 1e-1 (three decades; F-35A
  RAM-corrected median 2.7e-3 marked).  Peak pressure p_pk = sqrt(R * SE / max(tau, 1 s)), R = 3.013 /s (template T_C2).
TL (BORROWED, reach gap): no committed TL exists for any path from L. Nearest committed path (impact quantile 975,
  31.64 S 96.85 E) is used and range-adjusted by 10 log10(r / r_ref):  H01W and H08S = KRAKEN minus RAM delta (imp500);
  Perth Canyon 3376/3315 = RAM-corrected IMOS table; OHASISBIO = the H08S path as a PROXY (ridge-grazing loss NOT included).
  TL sd 7.9 dB (Blackman air9 residual) is carried as a band on every level.
Noise (background median 1 s 5-40 Hz SPL): 3376 = the detector's own role-B median (spl_max - snr of committed candidates,
  96.2 dB re 1 uPa^2); 3315 = 3376 + noise_bands difference; H01W, H08S, H08N
  = 3376 + Blackman (2004) offsets (+5.44, -0.65, -6.01 dB, module convention); OHASISBIO: NOT MEASURED -> H08S value as proxy.
SNR = 10 log10(1 + S/N), S = SE / max(tau, 1 s) (1 s SPL window). P_D: stage-A injection curves, union detector 'or',
  template T_C2, alpha 0.05 (and 0.005): 3376 curve for Perth Canyon (3315 has no background: proxy), 3274 curve + 4.8 dB for
  the IMS triads (module convention), 3274 curve without gain for OHASISBIO single hydrophones (proxy).
  H08S also by the airgun-shot criterion: exposure / median shot E_peak (0.3562, digitised panel e) against the committed
  h08s_template injection curve (false-alarm floor 0.0067)."""
import json, numpy as np, pandas as pd
HY = "hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/"
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
RHO_C = 1025.0 * 1500.0; R_PK = 3.012910065398646; ETAS = [1e-4, 1e-3, 1e-2, 1e-1]; ETA_F35 = 2.7e-3
def band_fraction(fc, f_r, slope=2.0):
    f = np.logspace(0, np.log10(500), 4000); esd = np.where(f[None, :] <= f_r[:, None], 1.0, (f[None, :] / f_r[:, None]) ** (-slope))
    tot = np.trapezoid(esd, f, axis=1); lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6); m = (f >= lo) & (f <= hi)
    return np.trapezoid(esd[:, m], f[m], axis=1) / tot
TAUG = np.logspace(np.log10(0.05), 1, 200); SBG = {fc: band_fraction(fc, 1 / TAUG) for fc in BANDS}
def tl_tables():
    k = pd.read_csv(HY + "results-data/near_limits/ims_tl_kraken.csv", dtype={"quantile": str}); rd = pd.read_csv(HY + "results-data/near_limits/ims_ram_delta.csv")
    im = pd.read_csv(HY + "results-data/ram_check/imos_tl_ramcorr.csv", dtype={"quantile": str}); T = {}
    for stn in ("H01W", "H08S"):
        g = k[(k.station == stn) & (k["quantile"] == "975") & np.isclose(k.src_depth_m, 10)].set_index("fc_hz")
        d = rd[(rd.path == f"imp500_{stn}") & np.isclose(rd.src_depth_m, 10)].set_index("fc_hz").delta_db
        T[stn] = dict(r_ref=float(g.range_km.iloc[0]), tl={fc: float(g.tl_db[fc] - np.interp(np.log10(fc), np.log10(d.index.values), d.values)) for fc in BANDS})
    for lg in (3376, 3315):
        g = im[(im.logger == lg) & (im["quantile"] == "975") & np.isclose(im.src_depth_m, 10)].set_index("fc_hz")
        T[f"PerthCanyon_{lg}"] = dict(r_ref=float(g.range_km.iloc[0]), tl={fc: float(g.tl_db[fc]) for fc in BANDS})
    return T
def noise():
    nb = pd.read_csv(HY + "results-data/imos1d/noise_bands.csv"); o = json.load(open(HY + "results-data/blackman_noise/blackman_noise_offsets.json"))
    n = {lg: float(10 * np.log10(sum(10 ** (nb[(nb.logger == lg) & (nb.band == b)].p50_1s.iloc[0] / 10) for b in ("5-10", "10-20", "20-40")))) for lg in (3376, 3315)}
    # the DETECTOR's background median (imos_detectors spl_med over role-B recordings, the SNR reference of the P_D curves) is
    # recovered from the committed candidates (spl_max_db - snr_db); 3315 is offset from it by the noise_bands difference
    c = pd.read_csv(HY + "results-data/kadri_northern/candidates.csv"); c = c[(c.station == "PerthCanyon_3376") & c.snr_db.notna()]
    m3376 = float(np.median(c.spl_max_db - c.snr_db)); n = {3376: m3376, 3315: m3376 + n[3315] - n[3376]}
    out = {"PerthCanyon_3376": n[3376], "PerthCanyon_3315": n[3315], "H01W": n[3376] + o["H01W"], "H08S": n[3376] + o["H08S"], "H08N": n[3376] + o["H08N"]}
    return out
def pd_curves():
    u = pd.read_csv(HY + "results-data/stageA/pd_vs_snr_union.csv"); C = {}
    for lg in (3376, 3274):
        for a in (0.05, 0.005):
            g = u[(u.logger == lg) & (u.template == "T_C2") & (u.detector == "or") & np.isclose(u.alpha, a)].sort_values("snr_db")
            C[(lg, a)] = (g.snr_db.values.astype(float), g.pd.values.astype(float))
    h = json.load(open(HY + "results-data/h08s_template/h08s_template.json"))["injection_pd"]
    C["h08s_shot"] = (np.array([x["snr_vs_median_shot_db"] for x in h], float), np.array([x["pd"] for x in h], float))
    return C
MED_SHOT = 0.3561858311264816
def station_levels(E, tau, rng_km, stn, T, N, C, base_tl=None):
    """Returns dict eta -> (SE Pa^2 s, p_pk Pa, SNR dB, P_D a=0.05, P_D a=0.005 [, P_D shot criterion])."""
    tau = np.clip(tau, 0.05, 10.0); key = stn if stn in T else "H08S"
    t = T[key]; adj = 10 * np.log10(np.maximum(rng_km, 1.0) / t["r_ref"])
    g = sum(np.interp(np.log10(tau), np.log10(TAUG), SBG[fc]) * 10 ** (-(t["tl"][fc] + adj) / 10) for fc in BANDS)
    nz = N.get(stn, N["H08S"]); out = {}
    for eta in ETAS:
        se = eta * E * RHO_C / (2 * np.pi) * g; s = se / np.maximum(tau, 1.0)
        snr = 10 * np.log10(1 + s / 1e-12 / 10 ** (nz / 10)); ppk = np.sqrt(R_PK * se / np.maximum(tau, 1.0))
        if stn.startswith("PerthCanyon"): lg, gain = 3376, 0.0
        elif stn in ("H01W", "H08S", "H08N"): lg, gain = 3274, 4.8
        else: lg, gain = 3274, 0.0
        pdv = {a: np.interp(snr + gain, *C[(lg, a)]) for a in (0.05, 0.005)}
        rec = dict(se=se, ppk=ppk, snr=snr, pd05=pdv[0.05], pd005=pdv[0.005])
        if stn == "H08S": rec["snr_shot"] = 10 * np.log10(se / MED_SHOT); rec["pd_shot"] = np.interp(rec["snr_shot"], *C["h08s_shot"])
        out[eta] = rec
    return out
