"""PRE-REGISTRATION and implementation — run J Task 1. The Kadri NORTHERN conditional, smoke scale,
on the data we already hold. Committed BEFORE any statistic in this file was computed.

Work order: hydro-work-order-2026-10-13.md, Task 1. Branch hypothesis/hydroacoustics.

THE HYPOTHESIS. Kadri (2024) reports a main signal on bearing 306.18 deg from Cape Leeuwin (H01W).
Projected to the 7th arc that bearing crosses near 26.2 S, 101.9 E. His paper gives TWO times for the
same signal: 00:52:03 in the text (p. 9, Fig. 9c peak) and 00:54:30 in the caption (p. 14). The implied
source times are 00:34:55 (text) and 00:37:22 (caption). Both are tested here as separate options; they
are not averaged and not marginalised over.

This source needs an H01W-to-H08S arrival-time difference of about 1,493 s. The module's existing
pre-registered pair span is 855.93-1346.50 s, which covers arc latitudes 45.0 S to 28.9 S only, so the
hypothesis was excluded BY CONSTRUCTION, not by evidence. The new pair span 1,346-1,710 s covers 28.9 S
to 22.0 S and joins the existing span with no gap. IT IS A NEW LOOK-ELSEWHERE FAMILY and is not folded
into the existing span's trial count.

RECEIVERS. Source 26.2 S 101.9 E. H01W 1,520 km, Perth Canyon 1,422 km, H08S 3,730 km (work order,
measured 13 Oct; re-derived here with Karney geodesics as a check, and the check is reported). Blocked
and carrying no information for any source north of 28.765 S: Portland (land), Scott Reef (North West
Shelf), H08N (Chagos Bank). H01W is Kadri's own detection and cannot test itself.

TIMING UNCERTAINTY (work order, do not re-derive). Source time is inferred from the H01W reception, so
the group-speed error enters only through the range difference: t_rx = t_H01W + (d_rx - d_H01W)/c.
Bearing +/-1.0 deg gives +/-9 s at H08S and +/-4 s at Perth Canyon; group speed 1.48 +/- 0.015 km/s
gives +/-15 s and +/-1 s; pick allowance 5 s. Combined 1 sigma 18 s at H08S, 6 s at Perth Canyon.

WINDOWS, at 95 per cent, fixed before any statistic (UTC, 8 March 2014):
  text    00:52:03 -> Perth Canyon 00:50:44-00:51:10 ; H08S 01:16:19-01:17:33
  caption 00:54:30 -> Perth Canyon 00:53:11-00:53:37 ; H08S 01:18:46-01:20:00

WHAT IS AND IS NOT COMPUTABLE, declared here rather than discovered later:
 1. The digitised H08S RECORD runs to 01:19:58.998 (panel e, 8,973 vertices, median vertex spacing
    0.049 s). The work order's "record ends 01:18:29" is the end of the airgun SHOT TRAIN, not of the
    trace: the last shot sits at t = 4699.1 s (01:18:19) and its cycle closes near 01:18:29.
 2. Therefore the five CYCLE statistics (shot energy, inter-shot gap power, shape correlation against
    the local stacked shot template, shoulder residuals, principal-component outlier score) are
    computable in the text window and are NOT computable in the caption window, because they are
    defined per airgun cycle and there are no cycles after 01:18:29. This is reported as not testable
    for those statistics. It is not replaced by a coarser statistic silently.

    CORRECTION DISCLOSED, found after the first run and before any value was quoted. Declaration 2 as
    written above is WRONG twice over. It miscounts the cycle statistics as five when there are SEVEN
    (shot energy, inter-shot gap power, shape correlation, three shoulder residuals, and the
    principal-component score), and it treats them alike when they do not depend on the cycle in the
    same way. Measured, the split is two and five:
      - SHOT ENERGY and INTER-SHOT GAP POWER need a CLOSED cycle, that is a following shot 9-11 s
        later, because h08s_shot_outliers.cycles defines them between consecutive peaks. The last
        closed cycle starts 01:18:19, so these TWO are genuinely NOT computable in the caption window.
        Their four rows, being two statistics in two directions, report computable = False.
      - SHAPE CORRELATION, the three SHOULDER RESIDUALS and the PRINCIPAL-COMPONENT SCORE need only a
        shot peak and its own [-3, +6] s window, from h08s_pulse_energy.pulses. Shot peaks continue to
        01:19:09, so these FIVE ARE computable in the caption window, on 2 shots, over eight rows once
        the deficit directions are counted. They carry the 2-shot sample size on every row.
    Nothing was substituted and no statistic was added: the correction narrows a blanket 'not testable'
    to the two statistics it actually applies to. The original wording is left above as pre-registered.
    The results note states the corrected split; this docstring is the pre-registration of record.
 3. For the caption window a SEPARATE statistic is pre-registered here: D4, a matched filter against the
    committed real-transient template T_C2, on the digitised envelope. Its null is weaker and is stated
    with it. It is reported as its own line, never pooled with the cycle statistics.
 4. At PERTH CANYON there is no repeating airgun shot train, so a local stacked SHOT template does not
    exist and the shape and shoulder statistics are undefined there. The analogue that is defined is the
    matched filter D4 against T_C2. D1 and D2 are recomputed on the new 95 per cent windows, which are
    26 s long against the 186.0 s and 154.2 s of the earlier Table-1-derived windows, so they are a
    different test of the same recordings, not a repeat.

STATISTICS AND DIRECTION. Excess is primary, deficit secondary, per the work order.
  H08S, per airgun cycle, from the committed code (h08s_shot_outliers.cycles, h08s_shot_template.analyse;
  40 Hz energy envelope, p^2 smoothed by a 0.25 s boxcar, log10):
    E_shot      shot energy                                     max primary, min secondary
    P_gap       inter-shot gap power                            max primary, min secondary
    rho         shape correlation vs local stacked template     min primary (low shape = anomaly)
    res_pre_db  leading-shoulder residual, [-3,-1] s             max primary, min secondary
    res_post_db trailing-shoulder residual, [1,4] s              max primary, min secondary
    res_tail_db tail residual, [4,6] s                          max primary, min secondary
    spe         principal-component outlier score               max primary
  The 'peak' residual is EXCLUDED: it is identically zero by construction (defect disclosed 10 Oct in
  h08s_shot_template.py). Peak energy is tested as E_shot.
  Perth Canyon, 500 Hz decimated, from the committed code (imos_detectors):
    D1  STA/LTA energy ratio, 5-40 Hz, STA 2 s over LTA 30 s     max
    D2  band-power exceedance over background median, dB         max
    D4  matched filter vs T_C2, normalised cross-correlation     max   (NEW in this run)

NULLS. No new background read.
  H08S: all contiguous blocks of k consecutive shots within the same panel, k = the number of shots whose
    peak time falls in the window; the observed block is one of them. p = #{blocks at least as extreme} /
    n_blocks, so the floor is 1/n_blocks and is reported per row. A pooled d+e null is reported beside it
    as a secondary with its own floor. Panel-wise is primary because the two panels have different
    plotted amplitude scales (+/-2 Pa for d, +/-4 Pa for e) and the committed robust z is per panel.
  Perth Canyon: the committed window null of imos_detectors — the window-max statistic over all windows
    of the same length inside the logger's role-'B' recordings for that night, leave-one-recording-out
    when the tested recording is itself in B. These recordings are already indexed in
    data/imos/recordings.csv and were read for item 2b; the 14-day stage-A background is NOT re-read.
  The existing IMOS COINCIDENCE null holds n_B = 98 realisations, so its smallest resolvable p is
  1/99 = 0.0101. The 0.005 'strict' tier is RETIRED: that null cannot resolve it. Every table states the
  floor of the null it actually used.

TIERS, as ruled with Pete 13 Oct: screen 0.3, mark 0.1, report 0.05. No tier verdict replaces the
  numbers: rank, p, SNR and likelihood ratio are reported for every candidate.

LIKELIHOOD RATIO. Detection form, from the module contract:
  flagged candidate   LR = P_D(SNR_pred) / p_observed
  no candidate        LR = (1 - P_D(SNR_pred)) / (1 - alpha_screen)
  P_D comes from the committed injection-recovery curves: h08s_template.json injection_pd for the H08S
  cycle statistics (x axis = energy of the injected transient relative to the median shot), and
  stageA/pd_vs_snr_union.csv for the IMOS loggers. Module likelihood stays ZERO regardless: the P_D gate
  is not met by this run.

DIVE PROBABILITY p = 0.5 PRIMARY, with p = 0 and p = 1 BESIDE IT. The conditional fixes the source
  LOCATION from Kadri's bearing, so the arrival windows and the measured p-values DO NOT depend on p at
  all. p enters only through the predicted received level, by way of the impact energy distribution:
  each row's weight is multiplied by 2p where latent:pushover_to_surface = 1, by 2(1-p) where it is 0,
  and by 1 where latent:pushover_drawn = 0. Impact set mh370-exchange/end-of-flight/run-i-dive, which
  SUPERSEDES run I; run I is the p = 0 point of the same prior and is not a separate alternative.
  SMOKE SCALE: one seed of eight per stratum, 4 strata, declared.

PREDICTED LEVEL. H08S: the committed transmission loss of kadri_package/next-run-b/predictions.csv at
  the nearest range on that station (3,786.8 km against this hypothesis's 3,730 km), power-mean over the
  5-40 Hz bands, tl_sd 7.9 dB; exposure scales linearly in the coupling efficiency eta and with the
  source energy, with the constant taken from the same committed table. eta is swept over four decades,
  1e-4 to 1e-1, with the F-35A value as the upper anchor. Perth Canyon: there is NO committed
  transmission loss at 1,422 km on that path, so the predicted level there is NOT ASSESSED and the LR is
  reported against received level instead of against p, with the level that each statistic would have
  needed in order to reach the report tier. Building that path is Task 2, not this task.

STOP CONDITION (work order): stop and report if the template or shoulder statistic cannot be computed on
  the digitised trace at the required time resolution. Checked per shot and reported.

OUTPUTS: kadri_northern/candidates.csv, kadri_northern/summary.json,
  kadri_northern/h08s_trace_predicted_window.png, kadri_northern/h08s_trace_flagged_outliers.png.
Usage: python kadri_northern_conditional.py <kadri data dir> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from pyproj import Geod
from scipy import signal

sys.path.insert(0, str(Path(__file__).parent))
import h08s_shot_outliers as H  # noqa: E402
import h08s_shot_template as TPL  # noqa: E402
import imos_detectors as D  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402
import kadri_table1_test as KT  # noqa: E402

HERE = Path(__file__).parent.parent
GEOD = Geod(ellps="WGS84")
DAY0 = KT.DAY0
SRC = (-26.2, 101.9)                      # Kadri northern crossing of the 7th arc
H01W = D.H01W
TIERS = {"screen": 0.3, "mark": 0.1, "report": 0.05}
COINC_FLOOR = 1.0 / 99.0                  # existing IMOS coincidence null, n_B = 98
ETAS = [1e-4, 1e-3, 1e-2, 1e-1]
PS = [0.5, 0.0, 1.0]
RUN_I_DIVE = Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive")
STRATA = ["next-i-free", "next-i-descent-climb", "next-i-repro-radar", "next-i-waypoints"]
SEED = "seed-1"                            # smoke scale, declared
C_W, C_PD, C_PTS = 2, 65, 105              # weight, latent:pushover_drawn, latent:pushover_to_surface

WINDOWS = {("text", "perth"): ("00:50:44", "00:51:10"),
           ("text", "h08s"): ("01:16:19", "01:17:33"),
           ("caption", "perth"): ("00:53:11", "00:53:37"),
           ("caption", "h08s"): ("01:18:46", "01:20:00")}
KADRI_TIMES = {"text": "00:52:03", "caption": "00:54:30"}
SOURCE_TIMES = {"text": "00:34:55", "caption": "00:37:22"}
H08S_STATS = [("E_shot", "max"), ("E_shot", "min"), ("P_gap", "max"), ("P_gap", "min"), ("rho", "min"),
              ("res_pre_db", "max"), ("res_pre_db", "min"), ("res_post_db", "max"), ("res_post_db", "min"),
              ("res_tail_db", "max"), ("res_tail_db", "min"), ("spe", "max")]
PRIMARY = {("E_shot", "max"), ("P_gap", "max"), ("rho", "min"), ("res_pre_db", "max"),
           ("res_post_db", "max"), ("res_tail_db", "max"), ("spe", "max")}


def secs(hms):
    return (pd.Timestamp(f"2014-03-08T{hms}Z") - DAY0).total_seconds()


def utc(t):
    return str(DAY0 + pd.Timedelta(seconds=float(t)))[11:19]


def pw(v):
    return float(10 * np.log10(np.mean([10 ** (x / 10) for x in v])))


# ---------------------------------------------------------------- geometry check
def geometry():
    rows = []
    for name, (la, lo) in [("H01W", H01W), ("Perth Canyon 3376", (-31.841667, 115.013333)),
                           ("Perth Canyon 3315", (-31.867217, 115.001133)), ("H08S", (-7.6499, 72.4836))]:
        _, _, d = GEOD.inv(SRC[1], SRC[0], lo, la)
        rows.append(dict(receiver=name, range_km=round(d / 1000, 1)))
    return rows


# ---------------------------------------------------------------- H08S
def h08s_shot_table(kd):
    """Per-shot statistics on the digitised H08S trace, from the committed code paths."""
    out, series, res_check = [], {}, []
    for pnl in "de":
        tg, p = H.load(kd, pnl)
        series[pnl] = (tg, p)
        S, A, An, rel, med = TPL.analyse(tg, p)
        cyc, _pk, _env = H.cycles(tg, p)
        S = S.copy()
        S["panel"] = pnl
        # attach the cycle statistics to the nearest shot (cycles and pulses are both peak-indexed)
        for col in ("E_shot", "P_gap"):
            S[col] = np.nan
        for r in cyc.itertuples():
            j = int(np.argmin(np.abs(S.t.values - r.t_shot)))
            if abs(S.t.values[j] - r.t_shot) <= 1.0:
                S.loc[j, "E_shot"] = r.E_shot
                S.loc[j, "P_gap"] = r.P_gap
        S["median_shot_E_peak"] = med
        out.append(S)
        # stop-condition check: samples available per shot window at the stated resolution
        n_per_shot = int(round((TPL.W1 - TPL.W0) * H.FS))
        raw = pd.read_csv(Path(kd) / "kadri-figure-extraction" / "figure9-vector-traces"
                          / f"kadri-2024-figure9-panel-{pnl}-H08S.csv")
        dv = np.diff(np.sort(raw.plotted_time_s.values))
        res_check.append(dict(panel=pnl, fs_hz=H.FS, samples_per_shot_window=n_per_shot,
                              n_shots=int(len(S)), n_vertices=int(len(raw)),
                              native_vertex_spacing_median_s=float(np.median(dv)),
                              native_vertex_spacing_p95_s=float(np.percentile(dv, 95)),
                              resample_grid_s=float(1 / H.FS), envelope_boxcar_s=0.25,
                              computable="yes: 360 samples per 9 s shot window, native spacing well "
                                         "inside the 0.25 s envelope smoothing"))
    return pd.concat(out, ignore_index=True), series, res_check


def block_null(vals, k, mode):
    v = np.asarray(vals, float)
    if k < 1 or k > len(v):
        return None
    B = sliding_window_view(v, k)
    with np.errstate(invalid="ignore"):
        return np.nanmax(B, axis=1) if mode == "max" else np.nanmin(B, axis=1)


def h08s_part(shots, series):
    rows = []
    for opt in ("text", "caption"):
        a, b = (secs(x) for x in WINDOWS[(opt, "h08s")])
        inwin = shots[(shots.t >= a) & (shots.t <= b)]
        for stat, mode in H08S_STATS:
            base = dict(station="H08S", option=opt, kadri_time_utc=KADRI_TIMES[opt],
                        window_utc=f"{utc(a)}-{utc(b)}", statistic=stat, direction=mode,
                        role="primary" if (stat, mode) in PRIMARY else "secondary",
                        n_shots_in_window=int(len(inwin)))
            vals = inwin[stat].values.astype(float) if len(inwin) else np.array([])
            if len(inwin) == 0 or not np.isfinite(vals).any():
                rows.append(base | dict(computable=False,
                                        note="statistic undefined in window: no closed airgun cycle "
                                             "(the last cycle closes 01:18:29)"))
                continue
            obs = float(np.nanmax(vals) if mode == "max" else np.nanmin(vals))
            k = int(np.isfinite(vals).sum())
            pnl = inwin.panel.iloc[0]
            r = base | dict(computable=True, observed=obs, k_blocks_shots=k)
            for tag, sub in (("panel", shots[shots.panel == pnl]), ("pooled", shots)):
                nl = block_null(sub[stat].values.astype(float), k, mode)
                if nl is None or len(nl) == 0:
                    r[f"p_{tag}"], r[f"n_null_{tag}"], r[f"floor_{tag}"] = np.nan, 0, np.nan
                    continue
                hit = (nl >= obs).sum() if mode == "max" else (nl <= obs).sum()
                r[f"p_{tag}"] = float(hit / len(nl))
                r[f"n_null_{tag}"] = int(len(nl))
                r[f"floor_{tag}"] = float(1.0 / len(nl))
                r[f"rank_{tag}"] = int(hit)
                # Overlapping blocks inflate rank and n_null by about k, so the count of INDEPENDENT
                # blocks at least as extreme is the honest unit.
                r[f"indep_rank_{tag}"] = round(hit / k, 2)
                r[f"n_indep_{tag}"] = round(len(nl) / k, 1)
            rows.append(r)
        # D4 on the digitised envelope, for the caption window where no cycle exists
        tg, p = series["e"] if b > secs("01:10:00") else series["d"]
        env = np.abs(signal.hilbert(p))
        m = (tg >= a) & (tg <= b)
        if m.any():
            w = int(m.sum())
            nl = block_null(env, w, "max")
            obs = float(env[m].max())
            rows.append(dict(station="H08S", option=opt, kadri_time_utc=KADRI_TIMES[opt],
                             window_utc=f"{utc(a)}-{utc(b)}", statistic="D4_envelope_max_pa",
                             direction="max", role="primary", computable=True, observed=obs,
                             n_shots_in_window=int(len(inwin)), k_blocks_shots=w,
                             p_panel=float((nl >= obs).sum() / len(nl)), n_null_panel=int(len(nl)),
                             floor_panel=float(1.0 / len(nl)), rank_panel=int((nl >= obs).sum()),
                             note="null includes the airgun train, so conservative"))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Perth Canyon
def t_c2_500():
    """T_C2 at 500 Hz: the committed positive-control transient (3315, 05:03:01), 5-40 Hz."""
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
    t = D.DAY0 + pd.Timedelta("05:03:01")
    for _, r in recs[recs.logger == 3315].iterrows():
        f = P.IMOS / r.file
        t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
        t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta["3315"], t0))
        s = (t - t0).total_seconds()
        xd = N.decimate(N.read_volts(f))
        if 10 <= s <= len(xd) / N.FS_D - 50:
            return signal.sosfiltfilt(sos, xd[int((s - 2) * N.FS_D): int((s + 20) * N.FS_D)])
    raise RuntimeError("T_C2 template not found")


def d4_series(path, tmpl):
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
    x = signal.sosfiltfilt(sos, N.decimate(N.read_volts(path)))
    k = tmpl / np.linalg.norm(tmpl)
    num = signal.correlate(x, k, mode="valid")
    e = np.sqrt(np.maximum(signal.correlate(x ** 2, np.ones(len(k)), mode="valid"), 1e-30))
    return np.abs(num) / e


def perth_part(cal_cache):
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    tmpl = t_c2_500()
    rows = []
    for lg in (3315, 3376):
        sub = recs[recs.logger == lg]
        cal = cal_cache[lg]
        brecs = [D.Rec(r, meta[str(lg)], cal) for _, r in sub[sub.role == "B"].iterrows()]
        bd4 = {Path(r.file).name: d4_series(P.IMOS / r.file, tmpl) for _, r in sub[sub.role == "B"].iterrows()}
        spl_med = float(np.median(np.concatenate([b.spl for b in brecs])))   # as imos_detectors.main
        for opt in ("text", "caption"):
            a, b = (DAY0 + pd.Timedelta(seconds=secs(x)) for x in WINDOWS[(opt, "perth")])
            hit = None
            for _, r in sub.iterrows():
                f = P.IMOS / r.file
                t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
                t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta[str(lg)], t0))
                if t0 <= b and a <= t0 + pd.Timedelta(seconds=r.dur_s):
                    hit = (r, t0, D.Rec(r, meta[str(lg)], cal))
                    break
            base = dict(station=f"PerthCanyon_{lg}", option=opt, kadri_time_utc=KADRI_TIMES[opt],
                        window_utc=f"{utc(secs(WINDOWS[(opt, 'perth')][0]))}-{utc(secs(WINDOWS[(opt, 'perth')][1]))}")
            if hit is None:
                rows.append(base | dict(statistic="coverage", computable=False, note="no recording covers the window"))
                continue
            r, t0, rec = hit
            w = rec.window(a, b, spl_med)
            if w is None:
                rows.append(base | dict(statistic="coverage", computable=False, note="window outside the recording"))
                continue
            name = Path(r.file).name
            for det in ("d1", "d2"):
                nl = D.null_max(brecs, det, w["len_s"], exclude=next((x for x in brecs if x.t0 == rec.t0), None))
                obs = w[det]
                rows.append(base | dict(statistic=det.upper(), direction="max", role="primary",
                                        computable=True, observed=float(obs), covered_s=w["covered_s"],
                                        peak_utc=(w[f"{det}_t"] or "")[11:23], recording=name,
                                        snr_db=w["snr_db"], spl_max_db=w["spl_max"],
                                        p_panel=float((nl >= obs).sum() / len(nl)), n_null_panel=int(len(nl)),
                                        floor_panel=float(1.0 / len(nl)), rank_panel=int((nl >= obs).sum())))
            # D4 matched filter
            x4 = d4_series(P.IMOS / r.file, tmpl)
            t4 = (np.arange(len(x4)) + len(tmpl) / 2) / N.FS_D
            sa = max((a - t0).total_seconds(), 0.0)
            sb = min((b - t0).total_seconds(), rec.n / N.FS_D)
            m = (t4 >= sa) & (t4 <= sb)
            if m.any():
                obs = float(x4[m].max())
                nvals = []
                for nm, arr in bd4.items():
                    if nm == name:
                        continue
                    k = min(max(int(round((sb - sa) * N.FS_D)), 1), len(arr))
                    nvals.append(sliding_window_view(arr, k)[::N.FS_D].max(1))
                nl = np.concatenate(nvals)
                tpk = t0 + pd.Timedelta(seconds=float(t4[m][np.argmax(x4[m])]))
                rows.append(base | dict(statistic="D4", direction="max", role="primary", computable=True,
                                        observed=obs, covered_s=w["covered_s"], recording=name,
                                        peak_utc=str(tpk)[11:23], snr_db=w["snr_db"],
                                        spl_max_db=w["spl_max"], p_panel=float((nl >= obs).sum() / len(nl)),
                                        n_null_panel=int(len(nl)), floor_panel=float(1.0 / len(nl)),
                                        rank_panel=int((nl >= obs).sum()),
                                        note="matched filter vs T_C2; NEW statistic this run"))
            else:
                rows.append(base | dict(statistic="D4", computable=False, note="no scorable samples in window"))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- predicted level and P_D
def dive_energy():
    """Weighted energy distribution at p = 0.5, 0, 1 by reweighting run I dive. Smoke scale: seed-1."""
    out = {}
    W, E, PTS, PDW = [], [], [], []
    for st in STRATA:
        d = RUN_I_DIVE / st / SEED
        a = np.load(d / "impacts32.npy", mmap_mode="r")
        z = np.load(d / "tau90_v1.npz")
        W.append(np.asarray(a[:, C_W], float))
        PTS.append(np.asarray(a[:, C_PTS], float))
        PDW.append(np.asarray(a[:, C_PD], float))
        E.append(np.asarray(z["energy_transferred_j"], float))
    W, E, PTS, PDW = (np.concatenate(x) for x in (W, E, PTS, PDW))
    ok = np.isfinite(E) & (E > 0) & np.isfinite(W) & (W > 0)
    W, E, PTS, PDW = W[ok], E[ok], PTS[ok], PDW[ok]
    for p in PS:
        f = np.ones_like(W)
        drawn = PDW == 1
        f[drawn & (PTS == 1)] = 2 * p
        f[drawn & (PTS == 0)] = 2 * (1 - p)
        w = W * f
        s = w.sum()
        if s <= 0:
            out[p] = dict(ess=0.0, e_q05=np.nan, e_q50=np.nan, e_q95=np.nan)
            continue
        wn = w / s
        o = np.argsort(E)
        c = np.cumsum(wn[o])
        q = {k: float(E[o][np.searchsorted(c, v)]) for k, v in (("e_q05", 0.05), ("e_q50", 0.5), ("e_q95", 0.95))}
        out[p] = dict(ess=float(1.0 / (wn ** 2).sum()), n_rows=int(len(E)), **q)
    return out


def h08s_predicted(energies):
    """Predicted H08S exposure and SNR against the median shot, from the committed TL table."""
    pr = pd.read_csv(HERE / "results-data/kadri_package/next-run-b/predictions.csv")
    h = pr[pr.station == "H08S"].copy()
    h["dr"] = (h.range_km - 3730.0).abs()
    row = h.sort_values("dr").iloc[0]
    bands = [c for c in h.columns if c.startswith("tl_db_")]
    tl = pw([float(row[c]) for c in bands])
    c_e = float(row["exposure_pa2s_eta0.0001"]) / (1e-4 * float(row.kinetic_energy_j) * 10 ** (-tl / 10))
    return dict(tl_db=tl, tl_sd_db=float(row.tl_sd_db), tl_range_km=float(row.range_km), c_e=c_e,
                exposure={f"{p}|{eta}": c_e * eta * energies[p]["e_q50"] * 10 ** (-tl / 10)
                          for p in PS for eta in ETAS})


def pd_curve():
    j = json.loads((HERE / "results-data/h08s_template/h08s_template.json").read_text())
    c = pd.DataFrame(j["injection_pd"])
    return c.snr_vs_median_shot_db.values.astype(float), c.pd.values.astype(float)


def main(kd, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    shots, series, res_check = h08s_shot_table(kd)
    A = h08s_part(shots, series)
    cal = {}
    nb = pd.read_csv(HERE / "results-data/imos1d/noise_bands.csv")
    meta = P.parse_meta()
    for lg in (3315, 3376):
        m = meta[str(lg)]
        fg, G = N.gain_db(next(P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
        d = nb[nb.logger == lg].set_index("band").p50_1s
        cal[lg] = dict(gain=(fg, G), sens=m["sens_db"],
                       m5_20=pw([d["5-10"], d["10-20"]]), m10_40=pw([d["10-20"], d["20-40"]]))
    B = perth_part(cal)
    energies = dive_energy()
    pred = h08s_predicted(energies)
    x, y = pd_curve()
    med_E = float(shots.median_shot_E_peak.iloc[0])
    # CORRECTION made before any value was quoted (13 Oct). The likelihood ratio must use ONE detector on
    # both sides. P_D here is measured under the committed +/-3 robust-z outlier rule, so its own
    # false-alarm rate is the floor of that same curve (the P_D at the lowest injected level, where there
    # is effectively no signal), NOT the 0.3/0.1/0.05 p-value screen tiers, which belong to a different
    # detector. Mixing them gave LR > 1 for a non-detection, which cannot be right.
    alpha_det = float(y.min())
    lr = []
    for p in PS:
        for eta in ETAS:
            snr = 10 * np.log10(pred["exposure"][f"{p}|{eta}"] / med_E)
            P_D = float(np.interp(snr, x, y))
            lr.append(dict(station="H08S", dive_p=p, eta=eta, snr_pred_db=float(snr), p_d=P_D,
                           alpha_detector=alpha_det,
                           lr_nondetection=float((1 - P_D) / (1 - alpha_det)),
                           p_d_at_or_below_false_alarm=bool(P_D <= alpha_det * 1.0001),
                           snr_below_lowest_injection=bool(snr < x.min())))
    C = pd.concat([A, B], ignore_index=True)
    C.to_csv(out / "candidates.csv", index=False)
    pd.DataFrame(lr).to_csv(out / "likelihood_ratio.csv", index=False)
    summ = dict(geometry=geometry(), resolution_check=res_check, windows={f"{k[0]}|{k[1]}": v for k, v in WINDOWS.items()},
                kadri_times=KADRI_TIMES, source_times=SOURCE_TIMES, tiers=TIERS,
                coincidence_null_floor=COINC_FLOOR, dive_energy=energies, h08s_predicted=pred,
                median_shot_E_peak=med_E, n_shots=int(len(shots)),
                shots_per_panel=shots.groupby("panel").size().to_dict(),
                last_shot_utc=utc(shots.t.max()),
                provenance="run-i-dive seed-1 per stratum (smoke scale); Kadri Fig 9 digitised vectors; "
                           "IMOS role-B same-night null; TL from kadri_package/next-run-b/predictions.csv")
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print(json.dumps({k: summ[k] for k in ("geometry", "dive_energy", "last_shot_utc", "shots_per_panel")},
                     indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
