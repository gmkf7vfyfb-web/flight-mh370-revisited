"""Received levels, SNR and the power screen on end of flight's run J (block 3, level half, of the 21 Oct 2026 work
order; block 6 noise-versus-levels charts and the updated loudness maps and illustrative traces).

PRE-REGISTERED (overnight 22 Oct 2026). Committed to hypothesis/hydroacoustics before any run on the run J impacts or
on any recording. The rules below are fixed; anything changed after the run is an amendment, committed and disclosed in
the results note. PREDICTIVE, NOT CALIBRATED: caveats C1 (propagation slope misfit, now a source-term caveat after the
TL-recalibration track's EW0112 result; +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not
calibrated; eta swept over four decades, F-35A upper anchor 2.1e-4) travel with every number. No likelihood is written.

IMPACT SET AND WEIGHTS (shared with the timing half, run_j_windows.py, prereg bc99b07; its ln_weights / p_factor are
  imported and used unchanged): run J, 74 seeds, 313,599,968 rows, four strata pooled by p_core/K; the northern supplement
  impacts-ruleB.npz (technique >= 1 rows, weight exp(lnw:comb/<D>), share s_D of the mixture); 00:19 options D0' (held
  out), D2, D3, D4; dive probability p in {0, 0.5, 1} (supplement rows keep native weights at every p: gap G-W1).
SUBSAMPLE DESIGN. Per key (option x p): N = 2,000,000 weighted draws, with replacement, n_supp = round(N s_D) from the
  supplement (probability proportional to its weight) and N - n_supp from the strata, allocated to seeds in proportion to
  p_core[s] / K_s (waypoints 24 seeds, about 73k each; the other 50 seeds about 60-150 each) and drawn within a seed with
  probability proportional to the row weight of that key. Per-draw weight at pooling: strata draw of seed s =
  (1 - s_D) m_{s,key} / n_s with m_{s,key} the seed's share of the strata mass under that key (p_core[s]/K_s x sum of row
  weights, normalised over seeds); supplement draw = s_D / n_supp. The subsample is therefore an importance-weighted
  sample of the same mixture the windows used (rule 3 of the sampling-coverage standing rule); its Kish ESS is reported
  beside the underlying posterior ESS of the windows note. rng = default_rng([20261022, 3, stratum_index, seed]);
  supplement rng([20261022, 3, 9, 0]). Fields kept per draw: latitude, longitude, t_impact, E = energy_transferred_j
  (= total kinetic energy, checked to 3e-7 on seed 1; the upper anchor, as the TL grid used), tau90, bank_deg,
  bank_source (1 = wings level by model assumption: LABEL carried, no value depends on it; this chain has no attitude
  dependence), family4_code, arc_distance_nm, pushover_to_surface.
SOURCE MODEL (per_impact_lnl / lhyd chain, second implementation as tl_grid_evidence.py): acoustic energy eta E;
  SE_1m = eta E rho c / (2 pi) Pa^2 s with rho c = 1025 x 1500; one-pole energy spectrum flat to f_r = 1/tau_ac and f^-2
  above, normalised over 1-500 Hz (imos_stageB_map.band_fraction, tabulated on lhyd.TAU_GRID and interpolated in log
  tau); PRIMARY tau_ac = tau90 clamped to 0.05-10 s (k = 1); SENSITIVITIES: k drawn from {0.5, 1, 2} per draw
  (per_impact_lnl amendment 3 mapping) and the scenario tau ~ log-U(0.05, 10 s). Source depth 10 m (the grid's reference;
  declared). eta grid {1e-2, 1e-3, 1e-4, 2.1e-4 (F-35A anchor), 1e-5, 1e-6}; eta only shifts every level by 10 log10 eta,
  so the chain is evaluated once at eta = 1 and shifted.
TRANSMISSION LOSS: the whole-arc grid (block 2, results-data/tl_grid_run_j, commits fc825c0..894a9e4), offset-0 arc line,
  linear in latitude and clamped at 41 S / 20 S (tl_grid_table.tl_at), blocked band (NaN) -> zero received energy. IMS
  H01W/H08S: raw KRAKEN minus the imp500 RAM delta (10 m, log-f interpolation; lhyd rule); H08N: raw KRAKEN, no RAM delta
  exists (LABEL: upper bound on loss); IMOS 3315/3376/3274/3275: RAM-corrected table (rule 2; extrapolated rows G-TL1
  inside); 3250: uncorrected (LABEL). Flags carried from the grid: adiabatic_suspect (TL = upper bound on loss, so the
  levels here are lower bounds before C2), ridge_source rows (32.0-31.5 S) kept, as the grid's 'keep' policy. Cross-arc
  offset is not used (latitude only, as per_impact_lnl): gap G-TL-X carried.
RECEIVED LEVEL per band b: L_b = 10 log10( SE_1m S_b(f_c, 1/tau_ac) 10^(-TL_b/10) / T_eff / 1e-12 ) dB re 1 uPa, the
  1 s-equivalent band SPL with T_eff = T_C2 = 2.683 s (stageB/pd_samples_summary.json); total 5-40 Hz level L = 10 log10
  sum_b 10^(L_b/10) over the ten third octaves 5-40 Hz. SNR = L + G - N_50 with G = 4.8 dB triad gain at the IMS stations
  (0 at the loggers) and N_50 the 5-40 Hz 1 s background median: IMOS imos2b background_spl_median; IMS = 3376 proxy +
  Blackman App. B offset (H01W 101.7, H08S 95.6, H08N 90.2 dB; digitised, May-June 2003). H01W CROSS-CHECK noise (2014):
  Kadri Fig. 9 panel (b) spectrogram median, -5.96 dB against Blackman (kadri_fig9_noise, digitised, +/-2 dB): SNR_kadri =
  SNR + 5.96 dB, reported beside. The 2-5 Hz band carries NO prediction (the grid has no TL below 5 Hz): noise only,
  labelled 'no prediction'.
KADRI CHAIN comparison condition (brief Refresh v2 section 5): his 5 Hz high-pass and 2-40 Hz band-pass are taken as
  4th-order Butterworth (order ASSUMED; he does not state it); each band's energy, signal and noise alike, is multiplied by
  the mean |H(f)|^2 over the band; the H01W/H08S panels are drawn a second time after this chain.
DETECTABILITY THRESHOLDS (weak-signal track, results/hydroacoustics-weak-signal-methods.md; model-matched upper bounds on
  real 3376 background): 'matched filter' = 7 dB (M1b envelope matched filter, P_D = 0.5 at alpha = 0.01, 6.9-8.0 dB over
  tau) and 'baseline detector' = 15 dB (STA/LTA, 13.4-15.7 dB). Detectable fraction per receiver x key x eta = weighted
  share of draws with SNR >= threshold. eta_50 per receiver x key x threshold = the eta at which the weighted median SNR
  equals the threshold: eta_50 = 10^((thr - SNR_50(eta = 1)) / 10).
POWER SCREEN (one label per receiver x option x p, from the matched-filter fraction at eta = 1e-3, five times the F-35A
  anchor): KEEP if >= 0.05; MARGINAL if 0.01-0.05; DROP if < 0.01. The fractions at every eta and both thresholds are
  tabulated regardless; a DROP receiver stays in every table (nothing is deleted). Receivers with every band blocked for a
  draw contribute SNR = -inf for that draw. BEST UNBLOCKED RECEIVER per draw = argmax SNR over the eight receivers
  (eta-independent); the loudness maps colour each impact by that SNR.
QUANTILES reported: 5/10/25/50/75/90/95 % (weighted) of L_b per band and of L and SNR; detectable fractions at both
  thresholds and six eta; eta_50; Kish ESS of the subsample per key; shares by family (A1/A2/B) and by bank_source.
IMOS NOISE PERCENTILES (statistic on recordings; this is the only data read): third-octave 1 s band SPL (1 s Hann
  periodogram, PSD bins whose centre lies in [f_c 2^-1/6, f_c 2^1/6) averaged and multiplied by the band width; calibration
  as imos_noise.py: dB re 1 uPa^2/Hz = 10 log10(V^2/Hz) - G(f) - S_h), percentiles 5/10/25/50/75/90/95 pooled over all 1 s
  segments of the selected recordings, plus the 5-40 Hz 1 s SPL (sum of 5-40 Hz bins) and the 2-5 Hz band. Recording
  sets: (i) BACKGROUND, loggers 3376/3274/3250, the pre-registered 14-day set (data/imos_background, eb83b31), every 12th
  file in name order within each day-directory listing (about 112 files per logger) - PRIMARY where it exists; (ii) 8 MARCH
  2014 role 'B' recordings (data/imos/recordings.csv) for all five loggers - PRIMARY for 3315 and 3275, cross-check for
  the others. Role 'S' recordings are never opened (asserted). The 5-40 Hz medians are compared with imos2b's medians
  (which the SNR uses); a difference above 3 dB is flagged in the note, not corrected.
CHARTS (chart rule of 10 Oct: no jargon in titles, axes or legends; footnotes (i) plain, (ii) technical): (a) per station,
  noise percentiles (median, 10-90 % band) per third octave against the predicted received level distribution (median and
  10-90 %) at eta = 1e-3, 2.1e-4, 1e-5, D0' p = 0.5, detectable fractions in the panel; one figure per station and a 2 x 4
  overview; H01W/H08S again after the Kadri chain; (b) detectable fraction against eta per station and option, p as line
  style, F-35A anchor marked; (c) loudness maps on run J: per option, impacts coloured by SNR at the best unblocked
  receiver, two eta rows, with the detectable share per panel; (d) illustrative traces: real 3376 background with the
  weak-signal track's dispersed template scaled to the median and 90th-percentile predicted level for eta = 1e-3 and
  2.1e-4, at 3376 and at the H01W proxy, matched-filter statistic beneath; labelled illustrative.
MATH CHECK: one hand-computed fixture (one draw, H01W, 10 Hz band) written out in the note, and an independent numpy
  implementation (direct quadrature of the spectrum, explicit interpolation, no imports from the chain) agreeing with the
  chain to 0.1 dB on 1,000 draws (check subcommand).
OUTPUTS: exchange /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/ (draws/<stratum>/seed-k.npz,
  draws/supplement.npz, levels/<key>.npz, tables/*.csv, noise/*.csv, run.json, SHA256SUMS); compact copy of the tables in
  results-data/levels_run_j/. Charts to results/ on claude-science-sep29 by run_j_levels_charts.py.

Usage (from prepare/, PYTHONPATH=.):
  python run_j_levels.py draw --eof <run-j root> --out <exchange> --seeds run-j-waypoints/seed-1 ...
  python run_j_levels.py supplement --supp <impacts-ruleB.npz> --out <exchange>
  python run_j_levels.py noise --out <exchange>
  python run_j_levels.py levels --eof <run-j root> --out <exchange> --repo-out <results-data/levels_run_j>
  python run_j_levels.py check --out <exchange>
"""
import argparse, csv, hashlib, json, os, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE.parent
RD = MODULE / "results-data"
sys.path.insert(0, str(HERE))
import run_j_windows as W  # noqa: E402  (ln_weights, p_factor, stratum_index, receivers, OPTIONS, PS, STRATA)

T0 = 1394236800.0
N_DRAWS = 2_000_000
ETAS = [1e-2, 1e-3, 2.1e-4, 1e-4, 1e-5, 1e-6]
ETA_F35A = 2.1e-4
THR = {"matched_filter": 7.0, "baseline": 15.0}
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
Z_REF = 10.0
RHO_C = 1025.0 * 1500.0
TRIAD_GAIN_DB = 4.8
TAU_LO, TAU_HI = 0.05, 10.0
RECEIVERS = ["H01W", "H08S", "H08N", "3315", "3376", "3274", "3275", "3250"]
IMS = ("H01W", "H08S", "H08N")
QS = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
SNR_GRID = np.arange(-200.0, 100.0 + 1e-9, 0.1)       # SNR at eta = 1, 0.1 dB bins
KADRI_H01W_DELTA_DB = -5.96
SCREEN_ETA = 1e-3
FIELDS = ["lat", "lon", "t", "E", "tau90", "bank_deg", "arc_nm"]
FIELDS_U8 = ["bank_source", "family4", "pushover_to_surface"]
KEYS = [f"{o}/p{p:g}" for o in W.OPTIONS for p in W.PS]
MAP_KEEP = 150_000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ draws
NEEDED = ["weight", "t_impact_s", "t_realised_flameout_s", "latent:inflight_p_breakup_to_m0019b", "loglik:r600/no-offset",
          "loglik:both/no-offset", "loglik:both/startup-offset", "latitude_deg", "longitude_deg", "arc_distance_nm",
          "latent:pushover_drawn", "latent:pushover_to_surface", "family4_code"]


def read_columns(sd, chunk=400_000):
    cols = (sd / "COLUMNS.txt").read_text().split(); ci = {c: i for i, c in enumerate(cols)}
    X = np.load(sd / "impacts32.npy", mmap_mode="r"); n = X.shape[0]
    out = {k: np.empty(n, np.float64) for k in NEEDED}
    idx = [ci[k] for k in NEEDED]
    for i0 in range(0, n, chunk):
        blk = np.asarray(X[i0:i0 + chunk])
        for k, j in zip(NEEDED, idx): out[k][i0:i0 + len(blk)] = blk[:, j]
    out["unix_s"] = out["t_impact_s"] + T0
    out["latent:realised_flameout_unix_s"] = out["t_realised_flameout_s"] + T0
    return out, n


def n_per_seed(eof):
    fe = json.loads((pathlib.Path(eof) / "summary" / "family-evidence-run-j.json").read_text())["p_core"]
    K = {s: len([d for d in (pathlib.Path(eof) / s).glob("seed-*") if d.is_dir()]) for s in W.STRATA}
    return {s: fe[s] / K[s] for s in W.STRATA}, fe, K


def do_draw(eof, out, seed_dirs, n_strata_by_key):
    eof = pathlib.Path(eof); out = pathlib.Path(out)
    alloc, p_core, K = n_per_seed(eof)
    for sdn in seed_dirs:
        t0 = time.time(); stratum, sname = sdn.split("/"); sd = eof / stratum / sname; k = int(sname.split("-")[1])
        od = out / "draws" / stratum; od.mkdir(parents=True, exist_ok=True)
        if (od / f"{sname}.npz").exists(): print("skip", sdn, flush=True); continue
        D, n = read_columns(sd); g = lambda key: D[key]
        meta = json.loads((sd / "run.json").read_text()); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
        z = np.load(sd / "tau90_v1.npz"); assert int(z["method"]) == 1
        E = z["energy_transferred_j"].astype(np.float32); tau = z["tau90_s"].astype(np.float32)
        att = np.load(sd / "attitude_v1.npz"); bank = att["bank_deg"].astype(np.float32); bsrc = att["bank_source"].astype(np.uint8)
        rng = np.random.default_rng([20261022, 3, W.stratum_index(stratum), k])
        res = {"n": n, "stratum": stratum, "seed": k, "sha_impacts32": sha(sd / "impacts32.npy"), "alloc": alloc[stratum],
               "code_revision": meta.get("code_revision"), "prior_track": meta.get("config", {}).get("prior", None)}
        arrays = {}; sums = {}
        for opt in W.OPTIONS:
            lnw = W.ln_weights(g, logon, opt)
            base = np.exp(np.where(np.isfinite(lnw), lnw, -np.inf)); base[~np.isfinite(base)] = 0.0
            for p in W.PS:
                key = f"{opt}/p{p:g}"; w = base * W.p_factor(g, p); tot = float(w.sum())
                ok = np.isfinite(E) & np.isfinite(tau) & np.isfinite(D["latitude_deg"]) & (w > 0)
                w = np.where(ok, w, 0.0); tot_ok = float(w.sum())
                n_s = int(round(n_strata_by_key[key] * alloc[stratum]))
                sums[key] = {"sum_w": tot, "sum_w_ok": tot_ok, "sum_w2": float((w * w).sum()), "n_draws": n_s, "share_not_ok": 1 - tot_ok / tot if tot > 0 else None}
                if n_s == 0 or tot_ok <= 0: continue
                ii = rng.choice(n, n_s, p=w / tot_ok)
                arrays[f"{key}/idx"] = ii.astype(np.int32)
                arrays[f"{key}/lat"] = D["latitude_deg"][ii].astype(np.float32); arrays[f"{key}/lon"] = D["longitude_deg"][ii].astype(np.float32)
                arrays[f"{key}/t"] = D["t_impact_s"][ii].astype(np.float32); arrays[f"{key}/E"] = E[ii]; arrays[f"{key}/tau90"] = tau[ii]
                arrays[f"{key}/bank_deg"] = bank[ii]; arrays[f"{key}/arc_nm"] = D["arc_distance_nm"][ii].astype(np.float32)
                arrays[f"{key}/bank_source"] = bsrc[ii]; arrays[f"{key}/family4"] = np.nan_to_num(D["family4_code"][ii], nan=0).astype(np.uint8)
                arrays[f"{key}/pushover_to_surface"] = np.nan_to_num(D["latent:pushover_to_surface"][ii], nan=0).astype(np.uint8)
        np.savez_compressed(od / f"{sname}.npz", meta=json.dumps({"res": res, "sums": sums}), **arrays)
        print(f"{sdn}: {n} rows, {time.time() - t0:.0f} s", flush=True)


def do_supplement(supp, out, n_total=N_DRAWS):
    z = np.load(supp); j = json.loads(pathlib.Path(str(supp)[:-4] + ".json").read_text())
    tech = z["technique"]; sel = tech >= 1
    rng = np.random.default_rng([20261022, 3, 9, 0]); arrays = {}; share = {}
    E = z["latent:impact_energy_transferred_j"].astype(np.float32)
    # tau90 is not in the reduced supplement file: declared gap G-L2; the supplement draws take tau90 from the pooled
    # strata tau90 distribution at pooling time (random, same rng stream) and are labelled.
    for opt in W.OPTIONS:
        w_all = np.exp(z[f"lnw:comb/{opt}"].astype(np.float64)); w_all[~np.isfinite(w_all)] = 0.0
        sD = float(w_all[sel].sum() / w_all.sum()); share[opt] = sD
        w = np.where(sel & np.isfinite(E), w_all, 0.0)
        for p in W.PS:
            key = f"{opt}/p{p:g}"; n_s = int(round(n_total * sD))
            ii = rng.choice(len(w), n_s, p=w / w.sum())
            arrays[f"{key}/idx"] = ii.astype(np.int32)
            arrays[f"{key}/lat"] = z["latitude_deg"][ii].astype(np.float32); arrays[f"{key}/lon"] = z["longitude_deg"][ii].astype(np.float32)
            arrays[f"{key}/t"] = z["t_impact_s"][ii].astype(np.float32); arrays[f"{key}/E"] = E[ii]
            arrays[f"{key}/tau90"] = np.full(n_s, np.nan, np.float32)
            arrays[f"{key}/bank_deg"] = z["latent:impact_bank_deg"][ii].astype(np.float32)
            arrays[f"{key}/arc_nm"] = np.full(n_s, np.nan, np.float32)
            arrays[f"{key}/bank_source"] = np.full(n_s, 255, np.uint8)      # 255 = not in file
            arrays[f"{key}/family4"] = np.nan_to_num(z["family4_code"][ii], nan=0).astype(np.uint8)
            arrays[f"{key}/pushover_to_surface"] = np.full(n_s, 255, np.uint8)
    pathlib.Path(out, "draws").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(pathlib.Path(out) / "draws" / "supplement.npz", meta=json.dumps({"share": share, "rows_in_file": int(len(tech)), "n_sel": int(sel.sum()), "sha": sha(supp), "json": j}), **arrays)
    print("supplement shares", share)
    return share


# ------------------------------------------------------------------ chain
def chain_tables():
    """S_b(f_c, 1/tau) tabulated on lhyd.TAU_GRID (600 log-spaced tau in 0.05-10 s), as lhyd/per_impact_lnl."""
    import imos_stageB_map as B
    tau_grid = np.logspace(np.log10(0.05), np.log10(10.0), 600)
    Sb = {fc: B.band_fraction(fc, 1 / tau_grid, 2) for fc in BANDS}
    return tau_grid, Sb


def tl_tables():
    import pandas as pd, tl_grid_table as TT
    xs, tabs = TT.load_table(RD / "tl_grid_run_j", BANDS, [Z_REF])
    rd = pd.read_csv(RD / "near_limits/ims_ram_delta.csv")
    out = {}
    for rec in RECEIVERS:
        col = {}
        for fc in BANDS:
            v = np.array(tabs[rec][(fc, Z_REF)], float)
            if rec in ("H01W", "H08S"):
                dd = rd[(rd.path == f"imp500_{rec}") & np.isclose(rd.src_depth_m, 10.0)].set_index("fc_hz").delta_db
                v = v - float(np.interp(np.log10(fc), np.log10(dd.index.values), dd.values))
            col[fc] = v
        out[rec] = col
    return xs, out


def noise_medians():
    bm = json.loads((RD / "imos2b/summary.json").read_text())["background_spl_median"]
    off = json.loads((RD / "blackman_noise/blackman_noise_offsets.json").read_text())
    nz = {lg: float(bm[lg]) for lg in ("3315", "3376", "3250", "3274", "3275")}
    for st in IMS: nz[st] = float(bm["3376"] + off[st])
    return nz


def kadri_chain_weights():
    """Mean |H|^2 per third octave for a 4th-order Butterworth 5 Hz high-pass times a 2-40 Hz band-pass (order ASSUMED)."""
    from scipy import signal
    f = np.logspace(0, np.log10(500), 20000)
    _, h1 = signal.freqs(*signal.butter(4, 2 * np.pi * 5.0, "highpass", analog=True), worN=2 * np.pi * f)
    _, h2 = signal.freqs(*signal.butter(4, [2 * np.pi * 2.0, 2 * np.pi * 40.0], "bandpass", analog=True), worN=2 * np.pi * f)
    H2 = np.abs(h1 * h2) ** 2
    return {fc: float(np.trapezoid(H2[(f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))], f[(f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))]) / (fc * 2 ** (1 / 6) - fc / 2 ** (1 / 6))) for fc in BANDS}


def noise_chain_shift(rec, kw):
    """10 log10 of the share of the station's 5-40 Hz noise energy that passes the Kadri chain (Blackman per-band medians x width)."""
    bs = json.loads((RD / "blackman_noise/blackman_noise_summary.json").read_text())["stations"][rec]["psd_R_band_db"]
    e = {fc: 10 ** (bs[f"{fc:g}"]["median"] / 10) * fc * (2 ** (1 / 6) - 2 ** (-1 / 6)) for fc in BANDS}
    return float(10 * np.log10(sum(e[fc] * kw[fc] for fc in BANDS) / sum(e.values())))


def levels_eta1(lat, E, tau_ac, xs, tl, tau_grid, Sb, teff, kadri=None):
    """Per-band 1 s-equivalent SPL at eta = 1 (dB re 1 uPa), shape (n, 10); -inf where blocked."""
    import tl_grid_table as TT
    SE1 = E.astype(np.float64) * RHO_C / (2 * np.pi); lt = np.log10(tau_ac)
    L = np.full((len(lat), len(BANDS)), -np.inf)
    for j, fc in enumerate(BANDS):
        sb = np.interp(lt, np.log10(tau_grid), Sb[fc]); t = TT.tl_at(xs, tl[fc], lat)
        with np.errstate(divide="ignore", invalid="ignore"):
            v = 10 * np.log10(SE1 * sb / teff / 1e-12) - t
            if kadri is not None: v = v + 10 * np.log10(kadri[fc])
        L[:, j] = np.where(np.isfinite(t), v, -np.inf)
    return L


def wquant(x, w, qs):
    o = np.argsort(x); cw = np.cumsum(w[o]); cw /= cw[-1]
    return np.interp(qs, cw, x[o])


def load_key(out, key, eof):
    """Concatenate the draws of one key over seeds + supplement; return fields and per-draw weights."""
    out = pathlib.Path(out); alloc, p_core, K = n_per_seed(eof)
    parts = []; m = {}
    for s in W.STRATA:
        for f in sorted((out / "draws" / s).glob("seed-*.npz"), key=lambda p: int(p.stem.split("-")[1])):
            z = np.load(f); meta = json.loads(str(z["meta"])); su = meta["sums"][key]
            if f"{key}/idx" not in z.files: continue
            n_s = len(z[f"{key}/idx"]); m[(s, f.stem)] = alloc[s] * su["sum_w_ok"]
            parts.append((s, f.stem, n_s, {fld: z[f"{key}/{fld}"] for fld in FIELDS + FIELDS_U8 + ["idx"]}))
    sup = np.load(out / "draws" / "supplement.npz"); smeta = json.loads(str(sup["meta"])); sD = smeta["share"][key.split("/")[0]]
    tot_m = sum(m.values()); w_parts = []
    for s, sn, n_s, _ in parts: w_parts.append(np.full(n_s, (1 - sD) * m[(s, sn)] / tot_m / n_s))
    n_sup = len(sup[f"{key}/idx"]); w_parts.append(np.full(n_sup, sD / n_sup))
    D = {fld: np.concatenate([p[3][fld] for p in parts] + [sup[f"{key}/{fld}"]]) for fld in FIELDS + FIELDS_U8}
    D["source"] = np.concatenate([np.full(p[2], i, np.int16) for i, p in enumerate(parts)] + [np.full(n_sup, -1, np.int16)])
    w = np.concatenate(w_parts); w /= w.sum()
    # G-L2: supplement draws have no tau90; fill from the strata tau90 distribution (weighted resample), labelled
    rng = np.random.default_rng([20261022, 3, 7, KEYS.index(key)])
    miss = ~np.isfinite(D["tau90"]); have = ~miss
    if miss.any():
        D["tau90"] = D["tau90"].copy(); D["tau90"][miss] = rng.choice(D["tau90"][have], miss.sum(), p=w[have] / w[have].sum())
    info = {"n": int(len(w)), "n_supplement": int(n_sup), "s_D": sD, "kish_ess": float(w.sum() ** 2 / (w * w).sum()),
            "seeds": [(s, sn, n_s) for s, sn, n_s, _ in parts]}
    return D, w, info


def do_levels(eof, out, repo_out):
    import pandas as pd
    out = pathlib.Path(out); repo_out = pathlib.Path(repo_out); (out / "levels").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(exist_ok=True); repo_out.mkdir(parents=True, exist_ok=True)
    tau_grid, Sb = chain_tables(); xs, tl = tl_tables(); nz = noise_medians(); kw = kadri_chain_weights()
    teff = json.loads((RD / "stageB/pd_samples_summary.json").read_text())["t_eff_s"]["T_C2"]
    rows_q, rows_det, rows_band, rows_eta50, rows_cov, rows_best = [], [], [], [], [], []
    gain = {r: (TRIAD_GAIN_DB if r in IMS else 0.0) for r in RECEIVERS}
    run = {"n_draws": N_DRAWS, "etas": ETAS, "thresholds": THR, "t_eff_s": teff, "noise_median_5_40_db": nz, "kadri_chain_band_weights": kw,
           "tl_span": [float(xs.min()), float(xs.max())], "keys": {}}
    for key in KEYS:
        t0 = time.time(); D, w, info = load_key(out, key, eof); n = len(w)
        tau_ac = np.clip(D["tau90"].astype(np.float64), TAU_LO, TAU_HI)
        rng = np.random.default_rng([20261022, 3, 5, KEYS.index(key)])
        tau_k = np.clip(rng.choice([0.5, 1.0, 2.0], n) * D["tau90"], TAU_LO, TAU_HI)
        tau_sc = 10 ** rng.uniform(np.log10(TAU_LO), np.log10(TAU_HI), n)
        snr1 = {}; store = {}
        for rec in RECEIVERS:
            Lb = levels_eta1(D["lat"], D["E"], tau_ac, xs, tl[rec], tau_grid, Sb, teff)
            with np.errstate(divide="ignore"):
                L = 10 * np.log10(np.sum(10 ** (Lb / 10), axis=1))
            s = L + gain[rec] - nz[rec]; snr1[rec] = s
            fin = np.isfinite(s); wf = w[fin] / w[fin].sum() if fin.any() else None
            hist = np.histogram(np.clip(s[fin], SNR_GRID[0], SNR_GRID[-1]), bins=SNR_GRID, weights=w[fin])[0] if fin.any() else np.zeros(len(SNR_GRID) - 1)
            store[f"{rec}/snr1_hist"] = hist.astype(np.float64); store[f"{rec}/blocked_mass"] = np.array(float(w[~fin].sum()))
            # sensitivities (SNR histograms only)
            for tag, tt in (("tau_k", tau_k), ("tau_scenario", tau_sc)):
                Lb2 = levels_eta1(D["lat"], D["E"], tt, xs, tl[rec], tau_grid, Sb, teff)
                with np.errstate(divide="ignore"):
                    s2 = 10 * np.log10(np.sum(10 ** (Lb2 / 10), axis=1)) + gain[rec] - nz[rec]
                f2 = np.isfinite(s2)
                store[f"{rec}/snr1_hist_{tag}"] = np.histogram(np.clip(s2[f2], SNR_GRID[0], SNR_GRID[-1]), bins=SNR_GRID, weights=w[f2])[0] if f2.any() else np.zeros(len(SNR_GRID) - 1)
            if rec in ("H01W", "H08S"):   # Kadri chain
                Lk = levels_eta1(D["lat"], D["E"], tau_ac, xs, tl[rec], tau_grid, Sb, teff, kadri=kw)
                nz_k = nz[rec] + noise_chain_shift(rec, kw)   # noise after the chain: Blackman per-band shape, scaled to the 5-40 Hz median
                with np.errstate(divide="ignore"):
                    sk = 10 * np.log10(np.sum(10 ** (Lk / 10), axis=1)) + gain[rec] - nz_k
                fk = np.isfinite(sk)
                store[f"{rec}/snr1_hist_kadri_chain"] = np.histogram(np.clip(sk[fk], SNR_GRID[0], SNR_GRID[-1]), bins=SNR_GRID, weights=w[fk])[0]
                run.setdefault("noise_after_kadri_chain_db", {})[rec] = float(nz_k)
                for j, fc in enumerate(BANDS):
                    fb = np.isfinite(Lk[:, j])
                    if fb.any():
                        q = wquant(Lk[fb, j], w[fb], QS)
                        rows_band.append(dict(key=key, receiver=rec, chain="kadri_5_40", fc_hz=fc, eta=1.0, blocked_mass=float(w[~fb].sum()), **{f"q{int(100 * qq):02d}": float(v) for qq, v in zip(QS, q)}))
            # per-band quantiles at eta = 1 (shift by 10 log10 eta for any eta)
            for j, fc in enumerate(BANDS):
                fb = np.isfinite(Lb[:, j])
                if fb.any():
                    q = wquant(Lb[fb, j], w[fb], QS)
                    rows_band.append(dict(key=key, receiver=rec, chain="module", fc_hz=fc, eta=1.0, blocked_mass=float(w[~fb].sum()), **{f"q{int(100 * qq):02d}": float(v) for qq, v in zip(QS, q)}))
            if fin.any():
                qs = wquant(s[fin], w[fin], QS); qL = wquant(L[fin], w[fin], QS)
                for eta in ETAS:
                    sh = 10 * np.log10(eta)
                    row = dict(key=key, option=key.split("/")[0], p=float(key.split("/p")[1]), receiver=rec, eta=eta, blocked_mass=float(w[~fin].sum()),
                               **{f"snr_q{int(100 * qq):02d}": float(v + sh) for qq, v in zip(QS, qs)}, **{f"level_q{int(100 * qq):02d}": float(v + sh) for qq, v in zip(QS, qL)},
                               noise_median_db=nz[rec], gain_db=gain[rec])
                    for tn, thr in THR.items():
                        row[f"frac_{tn}"] = float(w[fin][(s[fin] + sh) >= thr].sum())
                        if rec == "H01W": row[f"frac_{tn}_kadri_noise"] = float(w[fin][(s[fin] + sh - KADRI_H01W_DELTA_DB) >= thr].sum())
                    rows_det.append(row)
                for tn, thr in THR.items():
                    rows_eta50.append(dict(key=key, option=key.split("/")[0], p=float(key.split("/p")[1]), receiver=rec, threshold=tn, thr_db=thr,
                                           snr50_eta1_db=float(qs[3]), eta_50=float(10 ** ((thr - qs[3]) / 10))))
            else:
                for eta in ETAS:
                    rows_det.append(dict(key=key, option=key.split("/")[0], p=float(key.split("/p")[1]), receiver=rec, eta=eta, blocked_mass=1.0, noise_median_db=nz[rec], gain_db=gain[rec]))
        # best unblocked receiver per draw
        S = np.stack([snr1[r] for r in RECEIVERS], axis=1); best = np.argmax(np.where(np.isfinite(S), S, -np.inf), axis=1); sbest = S[np.arange(n), best]
        fin = np.isfinite(sbest); qb = wquant(sbest[fin], w[fin], QS)
        for eta in ETAS:
            sh = 10 * np.log10(eta)
            rows_best.append(dict(key=key, option=key.split("/")[0], p=float(key.split("/p")[1]), eta=eta, **{f"snr_best_q{int(100 * qq):02d}": float(v + sh) for qq, v in zip(QS, qb)},
                                  **{f"frac_{tn}": float(w[fin][(sbest[fin] + sh) >= thr].sum()) for tn, thr in THR.items()},
                                  **{f"share_best_{r}": float(w[best == i].sum()) for i, r in enumerate(RECEIVERS)}))
        keep = rng.choice(n, min(MAP_KEEP, n), replace=False)
        store["map/lat"] = D["lat"][keep]; store["map/lon"] = D["lon"][keep]; store["map/snr_best_eta1"] = sbest[keep].astype(np.float32)
        store["map/best"] = best[keep].astype(np.int8); store["map/w"] = (w[keep] / w[keep].sum()).astype(np.float32)
        store["map/family4"] = D["family4"][keep]; store["map/bank_source"] = D["bank_source"][keep]
        store["snr_best_hist"] = np.histogram(np.clip(sbest[fin], SNR_GRID[0], SNR_GRID[-1]), bins=SNR_GRID, weights=w[fin])[0]
        # coverage
        fam = D["family4"]; bs = D["bank_source"]
        rows_cov.append(dict(key=key, n=n, n_supplement=info["n_supplement"], s_D=info["s_D"], kish_ess_subsample=info["kish_ess"],
                             share_A1=float(w[fam == 1].sum()), share_A2=float(w[fam == 2].sum()), share_B=float(w[fam == 3].sum()), share_outside_B=float(w[fam == 6].sum()),
                             share_wings_level_by_assumption=float(w[bs == 1].sum()), share_bank_not_in_file=float(w[bs == 255].sum()),
                             lat_q01=float(wquant(D["lat"], w, [0.01])[0]), lat_q99=float(wquant(D["lat"], w, [0.99])[0]),
                             share_lat_outside_grid=float(w[(D["lat"] < xs.min()) | (D["lat"] > xs.max())].sum()),
                             share_arc_abs_gt_60nm=float(w[np.abs(np.nan_to_num(D["arc_nm"], nan=0)) > 60].sum()),
                             E_q05_gj=float(wquant(D["E"], w, [0.05])[0]) / 1e9, E_q50_gj=float(wquant(D["E"], w, [0.5])[0]) / 1e9, E_q95_gj=float(wquant(D["E"], w, [0.95])[0]) / 1e9,
                             tau90_q50_s=float(wquant(D["tau90"], w, [0.5])[0]), tau_clamped_share=float(w[(D["tau90"] < TAU_LO) | (D["tau90"] > TAU_HI)].sum())))
        np.savez_compressed(out / "levels" / f"{key.replace('/', '_')}.npz", meta=json.dumps(info), **store)
        run["keys"][key] = info; print(f"{key}: n={n} ess={info['kish_ess']:.0f} {time.time() - t0:.0f} s", flush=True)
    det = pd.DataFrame(rows_det); det.to_csv(out / "tables" / "detectable.csv", index=False)
    pd.DataFrame(rows_band).to_csv(out / "tables" / "band_levels_eta1.csv", index=False)
    pd.DataFrame(rows_eta50).to_csv(out / "tables" / "eta_50.csv", index=False)
    pd.DataFrame(rows_cov).to_csv(out / "tables" / "coverage.csv", index=False)
    pd.DataFrame(rows_best).to_csv(out / "tables" / "best_receiver.csv", index=False)
    # power screen
    scr = det[np.isclose(det.eta, SCREEN_ETA)].copy()
    scr["screen"] = np.where(scr.frac_matched_filter >= 0.05, "KEEP", np.where(scr.frac_matched_filter >= 0.01, "MARGINAL", "DROP"))
    scr[["key", "option", "p", "receiver", "eta", "frac_matched_filter", "frac_baseline", "blocked_mass", "screen"]].to_csv(out / "tables" / "power_screen.csv", index=False)
    (out / "run.json").write_text(json.dumps(run, indent=1))
    import shutil
    for f in (out / "tables").glob("*.csv"): shutil.copy(f, repo_out / f.name)
    shutil.copy(out / "run.json", repo_out / "run.json")
    print(scr.pivot_table(index="receiver", columns="key", values="screen", aggfunc="first").to_string())


# ------------------------------------------------------------------ IMOS noise percentiles
def do_noise(out):
    import pandas as pd
    from scipy import signal
    import imos_noise as N, imos_preregistration as P
    out = pathlib.Path(out); (out / "noise").mkdir(parents=True, exist_ok=True)
    pre = json.loads((MODULE / "data/imos/preregistration.json").read_text())
    recs = pd.read_csv(MODULE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    man = json.loads((MODULE / "data/imos_background/MANIFEST.json").read_text()); bg_root = pathlib.Path(man["held_at"])
    edges = {fc: (fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)) for fc in BANDS}
    rows = []; files_used = []
    for cid, L in pre["loggers"].items():
        calp = next(P.IMOS.glob(f"*/*alibration/{L['cal_file']}")); fg, G = N.gain_db(calp); Gi = lambda f: np.interp(f, fg, G)
        sets = {}
        b = recs[(recs.logger == int(cid)) & (recs.role == "B")]
        assert (recs[recs.logger == int(cid)].role != "S").sum() >= len(b)
        sets["8mar_B"] = [P.IMOS / f for f in b.file]
        if (bg_root / cid).is_dir():
            fl = []
            for day in sorted((bg_root / cid).iterdir()):
                if day.is_dir(): fl += sorted(day.glob("*.DAT"))
            sets["background"] = fl[::12]
        for sname, files in sets.items():
            acc = {fc: [] for fc in BANDS}; acc["5-40"] = []; acc["2-5"] = []
            s_files = {str(P.IMOS / f) for f in recs[(recs.logger == int(cid)) & (recs.role == "S")].file}
            for fp in files:
                assert str(fp) not in s_files, "role S recording must never be opened"
                xd = N.decimate(N.read_volts(fp)); nseg = len(xd) // N.FS_D
                f1, p1 = signal.periodogram(xd[: nseg * N.FS_D].reshape(nseg, N.FS_D), fs=N.FS_D, window="hann", detrend="constant", axis=-1)
                pu = p1 / (10 ** ((Gi(f1) + L["sens_db"]) / 10))      # uPa^2/Hz, 1 Hz bins
                for fc, (lo, hi) in edges.items():
                    m = (f1 >= lo) & (f1 < hi)
                    acc[fc].append(pu[:, m].mean(axis=1) * (hi - lo))
                acc["5-40"].append(pu[:, (f1 >= 5) & (f1 < 40)].sum(axis=1) * 1.0)
                acc["2-5"].append(pu[:, (f1 >= 2) & (f1 < 5)].mean(axis=1) * 3.0)
                files_used.append(dict(logger=cid, set=sname, file=str(fp.relative_to(P.IMOS)), n_1s=nseg))
            for band, v in acc.items():
                db = 10 * np.log10(np.concatenate(v))
                rows.append(dict(logger=cid, set=sname, band=str(band), n_files=len(files), n_1s=len(db), **{f"p{int(100 * q):02d}": round(float(np.quantile(db, q)), 2) for q in QS}))
            print(cid, sname, len(files), "files", flush=True)
    pd.DataFrame(rows).to_csv(out / "noise" / "imos_thirdoctave_percentiles.csv", index=False)
    pd.DataFrame(files_used).to_csv(out / "noise" / "files_used.csv", index=False)


# ------------------------------------------------------------------ math check
def do_check(out, eof):
    """Independent implementation: direct quadrature of the one-pole spectrum per band, explicit linear interpolation."""
    import pandas as pd
    out = pathlib.Path(out); D, w, info = load_key(out, "D0/p0.5", eof)
    rng = np.random.default_rng(20261022); ii = rng.choice(len(w), 1000, replace=False)
    tau_grid, Sb = chain_tables(); xs, tl = tl_tables(); nz = noise_medians()
    teff = json.loads((RD / "stageB/pd_samples_summary.json").read_text())["t_eff_s"]["T_C2"]
    lat, E, tau = D["lat"][ii].astype(float), D["E"][ii].astype(float), np.clip(D["tau90"][ii].astype(float), TAU_LO, TAU_HI)
    res = {}
    for rec in ("H01W", "H08S", "3376", "3275"):
        A = levels_eta1(lat, E, tau, xs, tl[rec], tau_grid, Sb, teff)              # chain
        Bm = np.full_like(A, -np.inf)                                               # independent
        f = np.linspace(1.0, 500.0, 200001)
        for i in range(len(ii)):
            fr = 1.0 / tau[i]; esd = np.where(f <= fr, 1.0, (f / fr) ** -2); tot = np.trapezoid(esd, f)
            for j, fc in enumerate(BANDS):
                lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6); m = (f >= lo) & (f <= hi); frac = np.trapezoid(esd[m], f[m]) / tot
                col = tl[rec][fc]; la = min(max(lat[i], xs[0]), xs[-1]); k = np.searchsorted(xs, la); k = min(max(k, 1), len(xs) - 1)
                t0_, t1_ = col[k - 1], col[k]
                if not (np.isfinite(t0_) and np.isfinite(t1_)): continue
                tlv = t0_ + (t1_ - t0_) * (la - xs[k - 1]) / (xs[k] - xs[k - 1]) if la > xs[k - 1] else t0_
                Bm[i, j] = 10 * np.log10(E[i] * RHO_C / (2 * np.pi) * frac * 10 ** (-tlv / 10) / teff / 1e-12)
        both = np.isfinite(A) & np.isfinite(Bm); d = np.abs(A[both] - Bm[both])
        res[rec] = dict(n_pairs=int(both.sum()), max_abs_diff_db=float(d.max()), rms_db=float(np.sqrt((d ** 2).mean())), blocked_agree=bool(np.array_equal(np.isfinite(A), np.isfinite(Bm))))
    # fixture: first draw, H01W, 10 Hz band, eta = F-35A
    i = 0; fc = 10.0; fr = 1 / tau[i]; f = np.linspace(1.0, 500.0, 200001); esd = np.where(f <= fr, 1.0, (f / fr) ** -2)
    lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6); m = (f >= lo) & (f <= hi); frac = float(np.trapezoid(esd[m], f[m]) / np.trapezoid(esd, f))
    import tl_grid_table as TT
    tlv = float(TT.tl_at(xs, tl["H01W"][fc], np.array([lat[i]]))[0])
    SE1 = ETA_F35A * E[i] * RHO_C / (2 * np.pi); SEb = SE1 * frac * 10 ** (-tlv / 10); Lb = 10 * np.log10(SEb / teff / 1e-12)
    fix = dict(lat=float(lat[i]), E_j=float(E[i]), tau_s=float(tau[i]), f_r_hz=float(fr), S_b=frac, tl_db=tlv, eta=ETA_F35A, rho_c=RHO_C, SE1_pa2s=float(SE1), SEb_pa2s=float(SEb),
               t_eff_s=teff, L_b_db=float(Lb), L_b_chain_db=float(levels_eta1(lat[:1], E[:1], tau[:1], xs, tl["H01W"], tau_grid, Sb, teff)[0, BANDS.index(fc)] + 10 * np.log10(ETA_F35A)),
               noise_5_40_db=nz["H01W"], gain_db=TRIAD_GAIN_DB, note="SNR in the note is on the 5-40 Hz total, not this single band")
    (out / "tables" / "math_check.json").write_text(json.dumps(dict(second_implementation=res, fixture=fix), indent=1))
    print(json.dumps(res, indent=1)); print(json.dumps(fix, indent=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["draw", "supplement", "noise", "levels", "check"])
    ap.add_argument("--eof", default="/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j"); ap.add_argument("--out", required=True)
    ap.add_argument("--supp", default="/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz")
    ap.add_argument("--seeds", nargs="*"); ap.add_argument("--repo-out", default=str(RD / "levels_run_j"))
    a = ap.parse_args()
    if a.cmd == "supplement": do_supplement(a.supp, a.out)
    elif a.cmd == "draw":
        sup = np.load(pathlib.Path(a.out) / "draws" / "supplement.npz"); share = json.loads(str(sup["meta"]))["share"]
        n_strata = {k: N_DRAWS - int(round(N_DRAWS * share[k.split("/")[0]])) for k in KEYS}
        do_draw(a.eof, a.out, a.seeds, n_strata)
    elif a.cmd == "noise": do_noise(a.out)
    elif a.cmd == "levels": do_levels(a.eof, a.out, a.repo_out)
    elif a.cmd == "check": do_check(a.out, a.eof)


if __name__ == "__main__":
    main()
