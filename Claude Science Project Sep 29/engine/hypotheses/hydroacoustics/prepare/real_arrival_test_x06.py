"""PRE-REGISTRATION, work card X06 (proposal X06; registry defect D05; gap G-W1): FIRST REAL-ARRIVAL TEST of the module's
detectors on held IMOS raw records. Approved by Pete, 23 Oct 2026 (overnight run, item 4).

This docstring is committed BEFORE any recording sample at an event time is read by this work card. Up to this commit
the work card has read only: the registry (REGISTRY.json, INDEX.md), the module code, data/imos/recordings.csv, the
.DAT footers (start time, sub-second field), the IMOS metadata, Royer 2016 digitised tables (royer_events.csv,
royer_arrivals.csv, royer_stations.csv), the Royer cross-ID table, and the existing products' file listings and
CSV headers (ex.weak_signal injection tables, ex.searches null files). Earlier module work (items 1d/2b, run J
searches) has read some of these recordings before; their outputs (results-data/imos2b/controls.csv) are cited as a
regression check only, not used to move windows.

QUESTION. On real long-range arrivals of known events recorded by the held IMOS loggers: (1) does each detector find the
arrival at the report level alpha = 0.05 per window with the module's own window null; (2) what is the pick error
(detector pick minus reference time); (3) how does the measured detection rate compare with the injection-recovery
P_D prediction at the measured SNR (D05: P_D was measured only on model-matched templates)?

INPUTS (registry ids; read only through registry/registry.py):
  in.imos_raw (CURRENT)                 IMOS .DAT records, loggers 3315, 3376 (Perth Canyon), 3250 (Scott Reef),
                                        3274, 3275 (Portland).
  in.module_data (CURRENT)              data/imos/recordings.csv (file list, roles S/B/other from item 1d).
  code.module_prepare (CURRENT)         imos_noise.py, imos_preregistration.py, imos_detectors.py (D1, D2, Rec,
                                        null_max), searches_run_j/detectors.py (M1b, bank_env), searches_run_j/
                                        preregistration.py (bank ranges, taus, 55 s window), gates/gates.py (Land).
  results-data/imos1d/noise_bands.csv, clock_test.json (module results-data; part of the module branch).
  in.royer_2016_digitised (CURRENT)     royer_events.csv (Table 4: origin, position, standard errors), royer_arrivals.csv
                                        (Table 5 picks; implied speeds).
  art.royer_crossid (CURRENT_WITH_CAVEATS; geodesic/speed predictions, exploratory)  second source for predicted times.
  ex.searches (CURRENT_WITH_CAVEATS: D06, D24, D26)  null/null_<logger>.npz, the run J M1b window null (3315 <- 3376 and
                                        3275 <- 3274 paired-logger stand-ins, D06).
  ex.weak_signal (CURRENT_WITH_CAVEATS: D05)  templates/templates_raw.npz (M1b bank), injection/ and injection_ext/
                                        (injection scores and null maxima) for the P_D prediction.
  in.gebco_2026 (CURRENT)               land-path label (gates.Land).

KNOWN EVENTS (reference times are independent of our detectors):
  K-CMST (item a and module positive controls C1-C4 of imos_detectors.py, CMST 2014-30):
    C1 3315 01:33:44 UTC (peak energy; CMST p. 6). TIMING NOT INDEPENDENT: C1 chose the clock sign at item 1d
       (clock_test.json, +25.82 s, convention A). Its pick error is reported but kept out of the timing summary.
    C2 3315 05:03:01 (CMST p. 15/17), C3 3315 05:18:13 (CMST p. 15, 'much lower amplitude'),
    C4 3250 01:32:49 onset (CMST Scott Reef note p. 1). Reference 1-sigma: 4 s (CMST's stated +/- 4 s for C1, applied
       to all four; disclosed assumption).
  K-ROYER (item b): every Royer (2016) Table 4 solution (20 events) x IMOS logger whose PREDICTED arrival (mean) lies
    inside a held recording (time base below). Predicted arrival = origin + geodesic range (WGS84, event to logger)
    / c. c = 1.4842 km/s, sd 0.0090 km/s (Royer's own implied speeds, 143 Table 5 arrivals; recomputed by this script
    from royer_arrivals.csv as the check). 1-sigma = sqrt(sd_origin^2 + (r sd_c / c^2)^2 + (sd_range / c)^2), sd_range
    from the Table 4 lat/lon standard errors by finite difference. Sensitivity: c = 1.482 +/- 0.006 (registry c_sofar).
    Not modelled: bathymetric (non-geodesic) paths, the up-slope leg to the shallow logger, T-phase conversion.
    Pairs whose mean lies outside every recording are listed as 'not covered' with the probability that the arrival
    falls inside any recording. Royer C1 at 3315 and CMST C1 are the same arrival (counted once in counts of unique
    arrivals); Royer C2 and C3 (1.1 s and 0.07 deg apart) are counted as one arrival.
  K-OTHER (item c): no other event with an independent (catalogue or published) time is identified in the module
    notes for the held IMOS records; none is added. (Events found only by our detectors are not used.)

TIME BASE (item 1d, fixed): true UTC = footer 'First Data' + sub-second field / 65536 s - e(t) (convention A).

DETECTORS (no detector is re-implemented; module code is called):
  M1b  envelope matched filter exactly as in the run J searches (searches_run_j/detectors.imos_stats on the 500 Hz
       decimated series; 18-template bank: ranges {1800, 2200, 2376.1, 2600, 3000, 3703.5} km x tau {0.1, 1, 10} s).
       Pick = time of the maximum (template energy-peak convention, 35 s into the 50 s template).
  D1   STA/LTA of imos_detectors.Rec (5-40 Hz, STA 2 s, LTA 30 s preceding, 0.1 s step). Pick = STA centre at max.
  D2   band-power exceedance of imos_detectors.Rec (5-20 / 10-40 Hz minus 1d median, 3 s mean). Pick = 1 s frame centre.

TEST WINDOW (55 s, as the run J window length): peak-type references [t_ref - 27.5, t_ref + 27.5] s; onset-type (C4)
  [t_ref - 10, t_ref + 45] s; clipped to the part of the recording each detector can score. covered_s is reported per
  detector. Coverage probability = P(true arrival inside the scored window) under the Normal prediction.

WINDOW NULL AND p (primary, the module's own nulls):
  D1, D2: imos_detectors.null_max over the SAME logger's background recordings (role B, item 1d), sliding windows of
          the covered length, step 1 s, LEAVE-ONE-RECORDING-OUT when the tested record is in B; p = fraction >= obs.
  M1b:    the run J searches null (ex.searches null/null_<NULL_STANDIN[logger]>.npz, 'M1b', 55 s grid windows on other
          days; D06 stand-ins for 3315 and 3275); p = (k + 1) / (n + 1) as in the run J searches.
  Sensitivities (reported beside, not used for the detection call): (s1) M1b with the same-logger role-B null, sliding
  windows of the covered length, leave-one-recording-out; (s2) all three detectors with a CLEAN null that also leaves
  out every B recording holding any included reference arrival (mean +/- 3 sigma).
DETECTION: p < 0.05 per detector per window (report level, ruling 13 Oct). No other threshold. 'Any of three' is
  reported as a count only (its false-alarm rate is up to about 0.14 per window).
SNR (5-40 Hz): imos_detectors definition: max 1 s 5-40 Hz SPL in the window minus the logger's background median 1 s
  5-40 Hz SPL (dB); signal-only estimate SNR_sig = 10 log10(10^(SNR/10) - 1) (NaN if SNR <= 0; biased high near 0 dB,
  disclosed). Also reported: the same SNR statistic on the null windows (median and 95th percentile), so a reader can
  see which arrivals stand out from noise.
INJECTION P_D AT THAT SNR (D05 comparison): from ex.weak_signal injection_scores.csv + injection_scores_ext.csv and the
  null_maxima_<target>.npz of the same product (60 s windows): threshold = 95th percentile of the null maxima
  (alpha 0.05), P_D(SNR) = share of injections (pooled over tau) above it, linear in SNR between grid points
  (-15 ... 30 dB, 5 dB step), clamped at the ends. Method mapping: M1b -> M1b_mf_envelope (same statistic);
  D1 -> M0a_stalta; D2 -> M0b_bandenergy (closest weak-signal baselines; NOT identical to D1/D2, disclosed).
  Injection target: 3376 for 3315 and 3376; 3274 for 3274 and 3275; 3250 for 3250 (3315 and 3275 have no injection
  set; paired-logger targets, disclosed). P_D at alpha 0.01 from pd_vs_snr_union.csv is reported beside.
STATISTICS AND READING (fixed now):
  - Counts per detector: detected / tested, over all included windows and over unique arrivals.
  - Predicted count = sum of P_D(SNR_sig); Poisson-binomial P(N <= n_obs) and P(N >= n_obs). Reading: 'measured
    detection BELOW the injection prediction' if P(N <= n_obs) < 0.05; 'ABOVE' if P(N >= n_obs) < 0.05; else 'consistent
    with the prediction at these counts'. Fewer than 5 detected arrivals per detector: no validation claim, counts only.
  - Pick error = pick - reference time, per detected window; mean, sd, n per detector, excluding C1 (circular); also
    standardised by the prediction 1-sigma. Secondary reading on the 16 s time-base question: the mean pick error with
    its 95 % interval is compared with 0 s and with +/-16 s (GPS - UTC in 2014); no reading if n < 5.
  - Labels only (no exclusion): land path (gates.Land, GEBCO 2026), window partly in warm-up/edge, Scott Reef 3250
    path note (D03 concerns MH370 paths; here each Royer path is checked by the land label).
OUTPUTS: results-data/real_arrival_test_x06/x06_table.csv (one row per event x logger x detector), x06_summary.json,
  x06_coverage.csv (all event x logger pairs, covered or not).
COMPUTE ESTIMATE: local, about 10 min at 4 threads (about 200 recordings of 307 s read once); development 1 h.
"""
# ======================================================================================================================
# IMPLEMENTATION (amendment commit after the pre-registration commit 857aeac; nothing above is changed).
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from numpy.lib.stride_tricks import sliding_window_view  # noqa: E402
from pyproj import Geod  # noqa: E402
from scipy.stats import norm  # noqa: E402

PREP = Path(__file__).resolve().parent
MOD = PREP.parent
os.environ.setdefault("HYDRO_ROOT_MOD", str(MOD))
sys.path.insert(0, str(MOD / "registry"))
sys.path.insert(0, str(PREP / "searches_run_j"))
sys.path.insert(0, str(PREP))
from registry import Registry  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402
import imos_detectors as ID  # noqa: E402
import detectors as SD  # noqa: E402  (searches_run_j/detectors.py: M1b)
import preregistration as SR  # noqa: E402  (searches_run_j/preregistration.py: bank constants)
sys.path.insert(0, str(PREP / "gates"))
import gates  # noqa: E402

GEOD = Geod(ellps="WGS84")
DAY0 = pd.Timestamp("2014-03-08", tz="UTC")
C_PRIMARY = (1.4842, 0.0090)
C_SENS = (1.482, 0.006)
LOGGERS = [3315, 3376, 3250, 3274, 3275]
CMST = [("C1", 3315, "01:33:44", "peak"), ("C2", 3315, "05:03:01", "peak"), ("C3", 3315, "05:18:13", "peak"),
        ("C4", 3250, "01:32:49", "onset")]
CMST_SD = 4.0
INJ_TARGET = {3315: 3376, 3376: 3376, 3274: 3274, 3275: 3274, 3250: 3250}
INJ_METHOD = {"M1b": "M1b_mf_envelope", "D1": "M0a_stalta", "D2": "M0b_bandenergy"}
ALPHA = 0.05


def subsec(path):
    t = open(path, "rb").read()[-1000:].decode("latin1")
    return int(re.search(r"First Data-\S+ \S+ - (\d+)", t).group(1)) / 65536


class Rec2(ID.Rec):
    """imos_detectors.Rec (D1, D2, SPL) plus the run J M1b series on the same decimated record."""
    def __init__(self, row, meta, cal, bank):
        super().__init__(row, meta, cal)
        x500 = N.decimate(N.read_volts(P.IMOS / row.file))
        _, e10 = SD.imos_series(x500)
        self.m1_t, self.m1 = SD.m1b_env(e10, bank)
        self.file = row.file


def win_stats(r, a, b):
    """Per detector: covered seconds, max, pick time (s after DAY0); a, b in s after DAY0."""
    t0 = (r.t0 - DAY0).total_seconds()
    out = {}
    for det, ts, s in (("D1", r.d1_t, r.d1), ("D2", r.d2_t, r.d2), ("M1b", r.m1_t, r.m1)):
        m = (ts + t0 >= a) & (ts + t0 <= b)
        if not m.any():
            out[det] = dict(covered_s=0.0, stat=np.nan, pick=np.nan)
            continue
        j = int(np.argmax(np.where(m, s, -np.inf)))
        rate = 10 if det in ("D1", "M1b") else 1
        out[det] = dict(covered_s=m.sum() / rate, stat=float(s[j]), pick=float(ts[j] + t0))
    m2 = (r.d2_t + t0 >= a) & (r.d2_t + t0 <= b)
    out["spl_max"] = float(r.spl[m2].max()) if m2.any() else np.nan
    return out


def null_sliding(brecs, det, L, exclude=()):
    vals = []
    for r in brecs:
        if r.file in exclude:
            continue
        x = {"D1": r.d1, "D2": r.d2, "M1b": r.m1}[det]
        rate = 10 if det in ("D1", "M1b") else 1
        w = min(max(int(round(L * rate)), 1), len(x))
        vals.append(sliding_window_view(x, w)[::rate].max(1))
    return np.concatenate(vals) if vals else np.array([])


def null_snr(brecs, L, med):
    vals = []
    for r in brecs:
        w = min(max(int(round(L)), 1), len(r.spl))
        vals.append(sliding_window_view(r.spl, w).max(1) - med)
    return np.concatenate(vals)


def poisson_binomial(p):
    pmf = np.array([1.0])
    for q in p:
        pmf = np.convolve(pmf, [1 - q, q])
    return pmf


def main(out_dir=None):
    warnings.simplefilter("ignore")
    Rg = Registry()
    used = {}
    for i in ("in.imos_raw", "in.module_data", "code.module_prepare", "in.royer_2016_digitised", "art.royer_crossid",
              "ex.searches", "ex.weak_signal", "in.gebco_2026", "note.imos_noise"):
        e = Rg.entry(i)
        used[i] = dict(status=e["status"], defects=e.get("defects", []))
    assert Path(P.IMOS) == Rg.path("in.imos_raw"), (P.IMOS, Rg.path("in.imos_raw"))
    out = Path(out_dir) if out_dir else MOD / "results-data" / "real_arrival_test_x06"
    out.mkdir(parents=True, exist_ok=True)

    recs = pd.read_csv(Rg.file("in.module_data", "imos/recordings.csv", verify=True), parse_dates=["start_logger"])
    meta = P.parse_meta()
    recs["t0u"] = [r.start_logger + pd.Timedelta(seconds=subsec(P.IMOS / r.file))
                   - pd.Timedelta(seconds=P.clock_err(meta[str(r.logger)], r.start_logger)) for r in recs.itertuples()]
    recs["s0"] = (recs.t0u - DAY0).dt.total_seconds()
    recs["s1"] = recs.s0 + recs.dur_s
    nb = pd.read_csv(MOD / "results-data/imos1d/noise_bands.csv")
    ev = pd.read_csv(Rg.file("in.royer_2016_digitised", "royer_events.csv", verify=True))
    arr = pd.read_csv(Rg.file("in.royer_2016_digitised", "royer_arrivals.csv", verify=True))
    sp = arr.implied_speed_km_s.dropna()
    speed_check = dict(n=int(len(sp)), mean=round(float(sp.mean()), 4), sd=round(float(sp.std()), 4))
    assert speed_check["n"] == 143 and abs(speed_check["mean"] - C_PRIMARY[0]) < 1e-4 and abs(speed_check["sd"] - C_PRIMARY[1]) < 1e-4, speed_check
    xid = pd.read_csv(Rg.file("art.royer_crossid", "", verify=True))
    land = gates.Land(Rg.path("in.gebco_2026") / "gebco_2026.json")

    # ---- references -----------------------------------------------------------------------------------------------
    refs = []
    for lab, lg, hms, kind in CMST:
        t = pd.Timedelta(hms).total_seconds()
        refs.append(dict(event=f"CMST-{lab}", source="CMST 2014-30", cls="CMST positive control", logger=lg, kind=kind,
                         t_ref=t, sd_ref=CMST_SD, t_ref_sens=t, range_km=np.nan, land="n/a", arrival_group=f"CMST-{lab}"))
    for e in ev.itertuples():
        for lg in LOGGERS:
            m = meta[str(lg)]
            _, _, d = GEOD.inv(m["lon"], m["lat"], e.lon_deg, e.lat_deg)
            _, _, dla = GEOD.inv(m["lon"], m["lat"], e.lon_deg, e.lat_deg + 0.01)
            _, _, dlo = GEOD.inv(m["lon"], m["lat"], e.lon_deg + 0.01, e.lat_deg)
            d, dla, dlo = d / 1e3, dla / 1e3, dlo / 1e3
            sdr = np.hypot((dla - d) / 0.01 * e.err_lat_deg, (dlo - d) / 0.01 * e.err_lon_deg)
            row = dict(event=f"Royer-{e.index}" + (f"/{e.label}" if isinstance(e.label, str) else ""), source="Royer 2016 Table 4",
                       cls=e.event_class, logger=lg, kind="peak", range_km=round(d, 1))
            for tag, (c, sc) in (("", C_PRIMARY), ("_sens", C_SENS)):
                row["t_ref" + tag] = e.origin_s_after_T0 + d / c
                row["sd_ref" + tag] = float(np.sqrt(e.err_time_s ** 2 + (d * sc / c ** 2) ** 2 + (sdr / c) ** 2))
            if e.label == "C1" and lg == 3315:
                row["arrival_group"] = "CMST-C1"          # Royer C1 at 3315 is the CMST 01:33:44 arrival
            elif e.label in ("C2", "C3"):
                row["arrival_group"] = f"Royer-C2/C3@{lg}"  # two solutions, 1.1 s and 0.07 deg apart: one arrival
            else:
                row["arrival_group"] = f"{row['event']}@{lg}"
            st, n_all, n_in = land.path(e.lat_deg, e.lon_deg, m["lat"], m["lon"])
            row["land"] = f"{st} ({n_in} of 2000 inner points above sea level)"
            x = xid[(xid.event == e.index) & (xid.rx.astype(str) == str(lg))]
            row["crossid_pred"] = x.pred.iloc[0] if len(x) else None
            row["crossid_basis"] = x.basis.iloc[0] if len(x) else None
            refs.append(row)
    refs = pd.DataFrame(refs)

    def rec_at(lg, t):
        r = recs[(recs.logger == lg) & (recs.s0 <= t) & (recs.s1 >= t)]
        return r.iloc[0] if len(r) else None

    cov = []
    for r in refs.itertuples():
        rr = recs[recs.logger == r.logger]
        pc = float(sum(norm.cdf(b, r.t_ref, r.sd_ref) - norm.cdf(a, r.t_ref, r.sd_ref) for a, b in zip(rr.s0, rr.s1)))
        hit = rec_at(r.logger, r.t_ref)
        cov.append(dict(event=r.event, logger=r.logger, t_ref_utc=str(pd.Timedelta(seconds=r.t_ref))[7:18], sd_ref_s=round(r.sd_ref, 1),
                        p_arrival_in_any_record=round(pc, 3), included=hit is not None, file=None if hit is None else hit.file,
                        role=None if hit is None else hit.role, pos_in_record_s=None if hit is None else round(r.t_ref - hit.s0, 1)))
    cov = pd.DataFrame(cov)
    cov.to_csv(out / "x06_coverage.csv", index=False)
    inc = refs[cov.included.values].reset_index(drop=True)
    inc_files = [rec_at(r.logger, r.t_ref).file for r in inc.itertuples()]
    print("included pairs", len(inc), flush=True)

    # ---- load recordings --------------------------------------------------------------------------------------------
    T = np.load(Rg.path("ex.weak_signal") / "templates" / "templates_raw.npz")
    bank, _ = SD.bank_env(T, SR.IMOS_BANK_RANGES, 100)
    cal, med, B, cache = {}, {}, {}, {}
    for lg in LOGGERS:
        m = meta[str(lg)]
        fg, Gd = N.gain_db(next(P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
        d = nb[nb.logger == lg].set_index("band").p50_1s
        cal[lg] = dict(gain=(fg, Gd), sens=m["sens_db"], m5_20=ID.pw(d["5-10"], d["10-20"]), m10_40=ID.pw(d["10-20"], d["20-40"]))

    def load(row):
        if row.file not in cache:
            cache[row.file] = Rec2(row, meta[str(row.logger)], cal[row.logger], bank)
        return cache[row.file]

    for lg in LOGGERS:
        B[lg] = [load(r) for r in recs[(recs.logger == lg) & (recs.role == "B")].itertuples()]
        med[lg] = float(np.median(np.concatenate([b.spl for b in B[lg]])))
        print("B loaded", lg, len(B[lg]), flush=True)
    runj_null = {lg: np.load(Rg.path("ex.searches") / "null" / f"null_{SR.NULL_STANDIN[str(lg)]}.npz")["M1b"] for lg in LOGGERS}

    # clean-null exclusion: every B record holding any included reference arrival (mean +/- 3 sigma)
    dirty = {lg: set() for lg in LOGGERS}
    for r in inc.itertuples():
        rr = recs[(recs.logger == r.logger) & (recs.s1 > r.t_ref - 3 * r.sd_ref) & (recs.s0 < r.t_ref + 3 * r.sd_ref)]
        dirty[r.logger] |= set(rr.file)

    # ---- injection P_D tables at alpha 0.05 --------------------------------------------------------------------------
    W = Rg.path("ex.weak_signal")
    inj = pd.concat([pd.read_csv(W / "injection" / "injection_scores.csv"), pd.read_csv(W / "injection_ext" / "injection_scores_ext.csv")])
    pdu = pd.read_csv(W / "injection_ext" / "pd_vs_snr_union.csv")
    pdtab = {}
    for tgt in set(INJ_TARGET.values()):
        nm = np.load(W / "injection" / f"null_maxima_{tgt}.npz")
        for det, meth in INJ_METHOD.items():
            thr = float(np.quantile(nm[meth], 1 - ALPHA))
            g = inj[inj.logger == tgt].groupby("snr_db")[meth].apply(lambda v: float((v > thr).mean()))
            p01 = pdu[(pdu.logger == tgt) & (pdu.method == meth) & (pdu.alpha == 0.01)].groupby("snr_db").apply(lambda q: q.k.sum() / q.n.sum())
            pdtab[(tgt, det)] = dict(snr=g.index.values.astype(float), pd05=g.values, pd01=p01.reindex(g.index).values, thr05=thr,
                                     n_inj=int((inj.logger == tgt).sum()), n_null=int(len(nm[meth])))

    def pd_at(tgt, det, snr, key):
        t = pdtab[(tgt, det)]
        if not np.isfinite(snr):
            return float(t[key][0])
        return float(np.interp(snr, t["snr"], t[key]))

    # ---- tests -------------------------------------------------------------------------------------------------------
    rows = []
    for r, f in zip(inc.itertuples(), inc_files):
        rowrec = recs[recs.file == f].iloc[0]
        rec = load(rowrec)
        a, b = (r.t_ref - 10, r.t_ref + 45) if r.kind == "onset" else (r.t_ref - 27.5, r.t_ref + 27.5)
        ws = win_stats(rec, a, b)
        snr = ws["spl_max"] - med[r.logger]
        snr_sig = 10 * np.log10(10 ** (snr / 10) - 1) if snr > 0 else np.nan
        ex = {rec.file} if rowrec.role == "B" else set()
        L2 = ws["D2"]["covered_s"]
        sn = null_snr([x for x in B[r.logger] if x.file not in ex], max(L2, 1), med[r.logger])
        for det in ("M1b", "D1", "D2"):
            w = ws[det]
            o = dict(event=r.event, source=r.source, cls=r.cls, logger=r.logger, arrival_group=r.arrival_group, file=f, role=rowrec.role,
                     ref_kind=r.kind, t_ref_utc=str(pd.Timedelta(seconds=r.t_ref))[7:18], sd_ref_s=round(r.sd_ref, 1),
                     t_ref_sens_utc=str(pd.Timedelta(seconds=r.t_ref_sens))[7:18], range_km=r.range_km, land_path=r.land,
                     win_a_utc=str(pd.Timedelta(seconds=a))[7:18], win_b_utc=str(pd.Timedelta(seconds=b))[7:18], detector=det,
                     covered_s=round(w["covered_s"], 1), statistic=w["stat"])
            o["p_cov_window"] = round(float(norm.cdf(b, r.t_ref, r.sd_ref) - norm.cdf(a, r.t_ref, r.sd_ref)), 3)
            if np.isfinite(w["stat"]):
                if det == "M1b":
                    p, n = (np.sum(runj_null[r.logger] >= w["stat"]) + 1) / (len(runj_null[r.logger]) + 1), len(runj_null[r.logger])
                    nl = null_sliding(B[r.logger], det, w["covered_s"], ex)
                    o["p_s1_same_logger_B"] = float((nl >= w["stat"]).mean())
                    o["null_primary"] = f"run J searches null_{SR.NULL_STANDIN[str(r.logger)]}.npz (55 s grid, other days)" + (" STAND-IN D06" if SR.NULL_STANDIN[str(r.logger)] != str(r.logger) else "")
                else:
                    nl = null_sliding(B[r.logger], det, w["covered_s"], ex)
                    p, n = float((nl >= w["stat"]).mean()), len(nl)
                    o["p_s1_same_logger_B"] = np.nan
                    o["null_primary"] = "imos_detectors same-logger role-B, leave-one-recording-out"
                ncl = null_sliding(B[r.logger], det, w["covered_s"], ex | dirty[r.logger])
                o["p_s2_clean_null"] = float((ncl >= w["stat"]).mean()) if len(ncl) else np.nan
                o["n_clean_null_windows"] = int(len(ncl))
                o.update(p=float(p), n_null=int(n), detected=bool(p < ALPHA), pick_utc=str(pd.Timedelta(seconds=w["pick"]))[7:18],
                         pick_error_s=round(w["pick"] - r.t_ref, 2), pick_error_sens_s=round(w["pick"] - r.t_ref_sens, 2),
                         pick_error_z=round((w["pick"] - r.t_ref) / r.sd_ref, 2))
            else:
                o.update(p=np.nan, detected=False, note="window not scorable by this detector (warm-up or record edge)")
            o.update(snr_db=round(snr, 2), snr_sig_db=round(snr_sig, 2) if np.isfinite(snr_sig) else np.nan,
                     snr_null_median_db=round(float(np.median(sn)), 2), snr_null_p95_db=round(float(np.quantile(sn, 0.95)), 2),
                     spl_max_db=round(ws["spl_max"], 2), bg_median_spl_db=round(med[r.logger], 2), injection_target=INJ_TARGET[r.logger],
                     pd_inj_a05=round(pd_at(INJ_TARGET[r.logger], det, snr_sig, "pd05"), 3),
                     pd_inj_a01=round(pd_at(INJ_TARGET[r.logger], det, snr_sig, "pd01"), 3))
            o["timing_independent"] = r.event != "CMST-C1"
            rows.append(o)
        print("tested", r.event, r.logger, flush=True)
    tab = pd.DataFrame(rows)
    tab.to_csv(out / "x06_table.csv", index=False)

    # ---- summary -----------------------------------------------------------------------------------------------------
    summ = dict(preregistration_commit="857aeac", inputs=used, speed_check=speed_check, alpha=ALPHA,
                n_pairs_all=int(len(cov)), n_pairs_included=int(len(inc)), n_unique_arrivals=int(inc.arrival_group.nunique()),
                injection_tables={f"{k[0]}/{k[1]}": dict(thr05=v["thr05"], n_inj=v["n_inj"], n_null=v["n_null"],
                                                        snr=v["snr"].tolist(), pd05=np.round(v["pd05"], 3).tolist()) for k, v in pdtab.items()},
                detectors={})
    for det, g in tab.groupby("detector"):
        sc = g[g.p.notna()]
        u = sc.sort_values("p").groupby("arrival_group").head(1)
        pmf = poisson_binomial(sc.pd_inj_a05.values)
        n_obs = int(sc.detected.sum())
        dd = sc[sc.detected & sc.timing_independent]
        e = dd.pick_error_s.values
        d0 = dict(n_tested=int(len(sc)), n_not_scorable=int(g.p.isna().sum()), n_detected=n_obs,
                  n_detected_s1=int((sc.p_s1_same_logger_B < ALPHA).sum()) if det == "M1b" else None,
                  n_detected_s2=int((sc.p_s2_clean_null < ALPHA).sum()),
                  n_unique_arrivals_tested=int(len(u)), n_unique_arrivals_detected=int(sc[sc.detected].arrival_group.nunique()),
                  expected_by_chance=round(ALPHA * len(sc), 2), predicted_by_injection=round(float(sc.pd_inj_a05.sum()), 2),
                  P_N_le_obs=round(float(pmf[: n_obs + 1].sum()), 4), P_N_ge_obs=round(float(pmf[n_obs:].sum()), 4),
                  timing=dict(n=int(len(e)), mean_s=round(float(e.mean()), 2) if len(e) else None,
                              sd_s=round(float(e.std(ddof=1)), 2) if len(e) > 1 else None,
                              median_s=round(float(np.median(e)), 2) if len(e) else None,
                              mean_ci95_s=[round(float(e.mean() - 1.96 * e.std(ddof=1) / np.sqrt(len(e))), 2),
                                           round(float(e.mean() + 1.96 * e.std(ddof=1) / np.sqrt(len(e))), 2)] if len(e) > 1 else None,
                              sd_z=round(float(dd.pick_error_z.std(ddof=1)), 2) if len(e) > 1 else None,
                              mean_sens_s=round(float(dd.pick_error_sens_s.mean()), 2) if len(e) else None))
        summ["detectors"][det] = d0
    (out / "x06_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print(json.dumps(summ["detectors"], indent=1, default=str))


# ======================================================================================================================
# AMENDMENT 2 (POST-HOC; written after the first run of main(); not pre-registered). It does not change any number of
# x06_table.csv or x06_summary.json. It reads x06_table.csv and writes x06_posthoc_a2.json:
#  (i)  arrival-group corrections seen only in the results: Royer-7/C1 at 3250 has the same window maximum (same pick)
#       as CMST-C4 (the Curtin event at Scott Reef) -> group CMST-C4; at 3274 Royer-7/C1 and Royer-C2/C3 share the
#       02:01 record and the same window maximum -> one group '3274@02:01 (Royer-7/C1 or C2/C3)'.
#  (ii) timing per detector on detected rows, timing-independent, PEAK-type references only (C4 onset removed), one row
#       per arrival group and reference source (smallest p), split by reference source (CMST observed time on the same record vs Royer
#       predicted time).
#  (iii) detection against injection P_D on the subset of arrival groups whose SNR exceeds the 95th percentile of the
#       same SNR statistic on null windows (the arrival stands out from noise in 5-40 Hz level), Poisson-binomial.
#  (iv) pooled timing over the three detectors for Royer-predicted references (per group, the pick of the smallest-p
#       detected detector), mean and 95 % interval compared with 0 s and +16 s; reading only if n >= 5.
def posthoc_a2(out_dir=None):
    out = Path(out_dir) if out_dir else MOD / "results-data" / "real_arrival_test_x06"
    t = pd.read_csv(out / "x06_table.csv")
    t["group_a2"] = t.arrival_group
    t.loc[(t.event == "Royer-7/C1") & (t.logger == 3250), "group_a2"] = "CMST-C4"
    t.loc[(t.logger == 3274) & t.event.isin(["Royer-7/C1", "Royer-11/C2", "Royer-12/C3"]), "group_a2"] = "3274@02:01 (Royer-7/C1 or C2/C3)"
    res = dict(note="POST-HOC amendment 2; not pre-registered", n_groups=int(t.group_a2.nunique()), detectors={})

    def stats(e):
        e = np.asarray(e, float)
        if len(e) == 0:
            return dict(n=0)
        d = dict(n=int(len(e)), mean_s=round(float(e.mean()), 2), values_s=[round(float(x), 2) for x in e])
        if len(e) > 1:
            sd = float(e.std(ddof=1)); d.update(sd_s=round(sd, 2), ci95_s=[round(float(e.mean() - 1.96 * sd / np.sqrt(len(e))), 2),
                                                                         round(float(e.mean() + 1.96 * sd / np.sqrt(len(e))), 2)])
        return d

    for det, g in t[t.p.notna()].groupby("detector"):
        u = g.sort_values("p").groupby("group_a2").head(1)
        us = g.assign(src=g.source.str[:4]).sort_values("p").groupby(["group_a2", "src"]).head(1)   # one row per group and reference source
        dd = us[us.detected & us.timing_independent & (us.ref_kind == "peak")]
        cm, ry = dd[dd.source.str.startswith("CMST")], dd[dd.source.str.startswith("Royer")]
        vis = u[u.snr_db > u.snr_null_p95_db]
        pmf = poisson_binomial(vis.pd_inj_a05.values); k = int(vis.detected.sum())
        res["detectors"][det] = dict(
            groups_tested=int(len(u)), groups_detected=int(u.detected.sum()),
            timing_cmst_same_record=stats(cm.pick_error_s), timing_royer_predicted=stats(ry.pick_error_s),
            timing_royer_z=stats(ry.pick_error_z),
            above_noise_subset=dict(groups=vis.group_a2.tolist(), detected=vis.detected.tolist(), p=vis.p.round(4).tolist(),
                                    snr_db=vis.snr_db.tolist(), pd_inj_a05=vis.pd_inj_a05.tolist(), n=int(len(vis)), n_detected=k,
                                    predicted=round(float(vis.pd_inj_a05.sum()), 2), P_N_le_obs=round(float(pmf[: k + 1].sum()), 4)))
    d = t[t.p.notna() & t.detected & t.timing_independent & (t.ref_kind == "peak") & t.source.str.startswith("Royer")]
    pooled = d.sort_values("p").groupby("group_a2").head(1)
    ps = stats(pooled.pick_error_s)
    ps["groups"] = pooled.group_a2.tolist(); ps["detector_used"] = pooled.detector.tolist()
    ps["reading"] = ("no reading (n < 5)" if ps["n"] < 5 else
                     f"95 % interval {'includes' if ps['ci95_s'][0] <= 0 <= ps['ci95_s'][1] else 'excludes'} 0 s and "
                     f"{'includes' if ps['ci95_s'][0] <= 16 <= ps['ci95_s'][1] else 'excludes'} +16 s")
    res["pooled_royer_timing"] = ps
    (out / "x06_posthoc_a2.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    if "--a2" in sys.argv:
        posthoc_a2(*[a for a in sys.argv[1:] if a != "--a2"][:1])
    else:
        main(*sys.argv[1:2])
