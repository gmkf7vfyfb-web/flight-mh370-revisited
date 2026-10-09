"""Interim deliverable 2a: Kadri (2024, Sci. Rep. 14:10102) H01W transients - reproduction from digitised data,
then a test against arrivals predicted from impact-PDF locations. PROVISIONAL.

INPUTS (provenance)
  Table 1 (19 transients, time and bearing at H01W): kadri-table1-transients.csv, extracted by a prior
    session from the published table (EXTRACTED, not digitised).
  Fig. 9 traces: kadri-2024-figure9-panel-{a,b,c}-H01W.csv and -{d,e}-H08S.csv, DIGITISED plot vertices from
    the publication PDF (metadata.json: "not raw CTBTO waveforms"), about 8,700 vertices per 10 min. Single
    channel, already filtered by Kadri (2-40 Hz band-pass, as he states) and decimated for plotting.
  Both are in 'Archive ISO Pre Sept 28/.../.sources/kadri-2024-hydroacoustics/data/'. No .md file there is read.
  Impact-PDF stand-in: the same parametric 7th-arc PDF as prepare/synthetic_composer_test.py, drawn from the
    full-scale core-only no-exhaustion-prior posterior at 00:19:37, with cross-arc N(0, 20 NM) and impact time
    00:19:37 + N(300 s, 180 s). Ruled for interim use; rerun on end-of-flight impacts when published.

WHAT CANNOT BE REPRODUCED. Bearings need the triad and are not recoverable from a single plotted channel.
Table 1 bearings are taken as published. Recorded inconsistencies in Kadri's own text: the candidate is
"recorded at 00:52 UTC" in the text but at 00:54:30 in Table 1; and Fig. 9b (00:37-00:47) is said to contain
"no observed signals", although Table 1 lists seven events in that span.

PRE-REGISTERED (fixed before the first run; do not edit after looking)
Part A - reproduction of Table 1 times on the digitised H01W traces (panels a-c, 00:27-00:57):
  Detector: STA/LTA on squared pressure, STA 1.0 s, LTA 20.0 s (trailing), trigger ratio >= 3.0, with
    triggers merged within 3 s. The trace is resampled to a uniform 20 Hz by linear interpolation of
    vertices.
  An event is REPRODUCED if a trigger lies within +/-3 s of its Table 1 time.
  Report: the fraction reproduced, per panel and overall, and the triggers with no Table 1 event.
  This is reproduction only; it carries no significance (brief section 2 rule 4).
Part B - geometry test at H01W:
  Prediction: for 200,000 stand-in impact samples, arrival t = t_imp + d/c (c = 1.482 +/- 0.006 km/s) and
    back-azimuth from the H01W centroid (WGS84 geodesic). Report the 2.5/50/97.5% quantiles of both.
  Per transient k, the geometry-only Bayes factor
    BF_k = p(t_k, theta_k | MH370 signal) / p(t_k, theta_k | background).
    Signal: the predictive density marginalised over the stand-in samples, with timing error
      sd = sqrt(10^2 + (d sd_c/c^2)^2) s and bearing error Student-t nu=3, sd 3.3 deg (DEMONSTRATED,
      brief section 5). Sensitivity row: Gaussian 0.4 deg (CLAIMED by Kadri).
    Background: uniform in time over Table 1's own span (00:38:29-00:55:07, 998 s) and uniform in
      bearing over Table 1's own sector (234.67-343.16 deg). The rate comes from the OTHER 18 transients
      (leave-one-out), so the density is 1/(998 s x 108.5 deg) per event.
  Posterior P(transient k is the signal), under the hypothesis that exactly one of the 19 is the
    signal, with equal prior per transient: BF_k / sum(BF). Under the alternative that none is, the
    result is reported conditional on a detection having occurred, which this test cannot establish.
  Information gain (bits) on the along-arc impact PDF if the main candidate (00:54:30, 306.18 deg) is
    accepted as the signal, under each bearing-error model; plus where its bearing line crosses the arc.
  Verdict wording, fixed:
    "geometrically SUPPORTED"     BF of the main candidate >= 10 under the demonstrated error model;
    "geometrically DISFAVOURED"   BF <= 0.1;
    "geometrically UNINFORMATIVE" otherwise.
  No log-likelihood leaves this script: the P_D gate (contract rule 2) is not met.

Run: python prepare/kadri_table1_test.py <kadri_data_dir> <no-exhaustion-prior-summary.json> <out_dir>
"""

import json
import pathlib
import sys

import numpy as np
import pandas as pd
from pyproj import Geod

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import synthetic_composer_test as sct  # noqa: E402

GEOD = Geod(ellps="WGS84")
H01W = (-34.890303, 114.142637)
DAY0 = pd.Timestamp("2014-03-08T00:00:00Z")
T_IMPACT_REF = (pd.Timestamp("2014-03-08T00:19:37Z") - DAY0).total_seconds()
STA, LTA, RATIO, MERGE, MATCH, FS = 1.0, 20.0, 3.0, 3.0, 3.0, 20.0
PICK_S, C, SD_C = 10.0, 1.482, 0.006
NU, SD_DEM, SD_CLAIM = 3.0, 3.3, 0.4
MAIN = "event_005430"


def secs(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


def part_a(kd, table):
    out, trig_rows = [], []
    tvals = table.t_s.values
    for panel in "abc":
        tr = pd.read_csv(kd / "kadri-figure-extraction" / "figure9-vector-traces" / f"kadri-2024-figure9-panel-{panel}-H01W.csv")
        t = (pd.to_datetime(tr.utc) - DAY0).dt.total_seconds().values
        o = np.argsort(t); t, p = t[o], tr.pressure_pa.values[o]
        tg = np.arange(t[0], t[-1], 1 / FS); pg = np.interp(tg, t, p); e = pg ** 2
        cs = np.concatenate([[0.0], np.cumsum(e)])
        ns, nl = int(STA * FS), int(LTA * FS)
        idx = np.arange(nl, len(e) - ns)
        sta = (cs[idx + ns] - cs[idx]) / ns
        lta = (cs[idx] - cs[idx - nl]) / nl
        r = sta / np.maximum(lta, 1e-30)
        on = idx[r >= RATIO]
        trig = []
        for i in on:
            tt = tg[i]
            if not trig or tt - trig[-1] > MERGE:
                trig.append(tt)
        lo, hi = tg[nl], tg[-ns]
        in_panel = table[(table.t_s >= lo) & (table.t_s <= hi)]
        for _, ev in in_panel.iterrows():
            d = np.min(np.abs(np.array(trig) - ev.t_s)) if trig else np.inf
            out.append(dict(panel=panel, event_id=ev.event_id, time_utc=ev.time_utc, nearest_trigger_s=float(d),
                            reproduced=bool(d <= MATCH)))
        for tt in trig:
            near = np.min(np.abs(tvals - tt))
            trig_rows.append(dict(panel=panel, trigger_utc=str(DAY0 + pd.Timedelta(seconds=float(tt)))[11:19],
                                  nearest_table1_s=float(near), unmatched=bool(near > MATCH)))
    return pd.DataFrame(out), pd.DataFrame(trig_rows)


def log_t(x, sd, nu):
    s = sd / np.sqrt(nu / (nu - 2))
    from scipy.special import gammaln
    return (gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(nu * np.pi) - np.log(s)
            - 0.5 * (nu + 1) * np.log1p((x / s) ** 2 / nu))


def log_n(x, sd):
    return -0.5 * np.log(2 * np.pi * sd * sd) - 0.5 * (x / sd) ** 2


def part_b(table, summary_path):
    rng = np.random.default_rng(sct.SEED)
    ridge, grid, dens, stats = sct.ridge_and_marginal(summary_path)
    q, _ = sct.fit_small_circle(ridge)
    pr = sct.draw_prior(rng, q, grid, dens, sct.N_PRIOR, 20.0)
    n = len(pr)
    az_bk, _, d = GEOD.inv(np.full(n, H01W[1]), np.full(n, H01W[0]), pr[:, 1], pr[:, 0])
    d = d / 1000.0; baz = np.mod(az_bk, 360.0)
    # Impact time is a nuisance: marginalised analytically (as in the composer test), so the information
    # gain is on POSITION only. (v1 drew one impact time per sample, which put the nuisance into the KL;
    # corrected 2026-10-09 to match the pre-registered definition. v1 output kept as superseded.)
    t_arr = T_IMPACT_REF + sct.BASE["mu_t_s"] + d / C
    sd_t = np.sqrt(PICK_S ** 2 + (d * SD_C / C ** 2) ** 2 + sct.BASE["sigma_t_s"] ** 2)
    t_arr_draw = t_arr + sct.BASE["sigma_t_s"] * rng.normal(size=n)   # for the reported prediction quantiles only
    q3 = lambda x: [float(v) for v in np.quantile(x, [0.025, 0.5, 0.975])]
    pred = dict(arrival_utc_q=[str(DAY0 + pd.Timedelta(seconds=v))[11:19] for v in q3(t_arr_draw)],
                backazimuth_deg_q=q3(baz), range_km_q=q3(d))
    t0, t1 = table.t_s.min(), table.t_s.max()
    b0, b1 = table.bearing_deg.min(), table.bearing_deg.max()
    bg_logdens = -np.log((t1 - t0) * (b1 - b0))
    rows = []
    for _, ev in table.iterrows():
        dt = ev.t_s - t_arr
        db = (ev.bearing_deg - baz + 180.0) % 360.0 - 180.0
        r = {}
        for name, lb in [("demonstrated_t3_3.3", log_t(db, SD_DEM, NU)), ("claimed_gauss_0.4", log_n(db, SD_CLAIM))]:
            ll = log_n(dt, sd_t) + lb
            m = ll.max(); lse = m + np.log(np.mean(np.exp(ll - m)))
            r[f"log10_BF_{name}"] = float((lse - bg_logdens) / np.log(10))
            w = np.exp(ll - m); w /= w.sum()
            w0 = 1.0 / n; nz = w > 0
            r[f"info_bits_{name}"] = float(np.sum(w[nz] * np.log2(w[nz] / w0)))
            r[f"post_lat_mean_{name}"] = float(np.sum(w * pr[:, 0]))
            r[f"post_ess_{name}"] = float(1 / np.sum(w * w))
        rows.append(dict(event_id=ev.event_id, time_utc=ev.time_utc, bearing_deg=ev.bearing_deg, **r))
    res = pd.DataFrame(rows)
    for name in ["demonstrated_t3_3.3", "claimed_gauss_0.4"]:
        bf = 10 ** res[f"log10_BF_{name}"]
        res[f"P_signal_if_one_{name}"] = bf / bf.sum()
    # where does the main candidate's bearing line cross the arc?
    ev = table[table.event_id == MAIN].iloc[0]
    lons, lats, _ = GEOD.fwd(np.full(4000, H01W[1]), np.full(4000, H01W[0]), np.full(4000, ev.bearing_deg),
                             np.linspace(0, 4.0e6, 4000))
    arc_lon, _ = sct.arc_point(q, lats)
    k = int(np.nanargmin(np.abs(lons - arc_lon)))
    cross = dict(lat=float(lats[k]), lon=float(lons[k]), range_km=float(np.linspace(0, 4000, 4000)[k]))
    core_lat = np.quantile(pr[:, 0], [0.025, 0.5, 0.975]).tolist()
    m = res[res.event_id == MAIN].iloc[0]
    lbf = m["log10_BF_demonstrated_t3_3.3"]
    verdict = ("geometrically SUPPORTED" if lbf >= 1 else "geometrically DISFAVOURED" if lbf <= -1
               else "geometrically UNINFORMATIVE")
    return res, dict(prediction_H01W=pred, background_logdensity=float(bg_logdens), main_candidate_arc_crossing=cross,
                     stand_in_impact_lat_q=core_lat, main_candidate_verdict=verdict,
                     prior_mass_north_of_crossing=float(np.mean(pr[:, 0] > cross["lat"] - 1.0)))


def main(kd, summary, out_dir):
    kd, out = pathlib.Path(kd), pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    table = pd.read_csv(kd / "kadri-table1-transients.csv")
    table["t_s"] = table.time_utc.map(secs)
    a, trig = part_a(kd, table)
    a.to_csv(out / "kadri_table1_reproduction.csv", index=False); trig.to_csv(out / "kadri_fig9_triggers.csv", index=False)
    b, meta = part_b(table, summary)
    b.to_csv(out / "kadri_table1_geometry.csv", index=False)
    meta["reproduction"] = dict(n_events_in_panels=int(len(a)), n_reproduced=int(a.reproduced.sum()),
                                by_panel={p: [int(g.reproduced.sum()), int(len(g))] for p, g in a.groupby("panel")},
                                n_triggers=int(len(trig)), n_unmatched_triggers=int(trig.unmatched.sum()) if len(trig) else 0)
    json.dump(meta, open(out / "kadri_table1_summary.json", "w"), indent=1)
    print(json.dumps(meta, indent=1))
    print(b[["event_id", "time_utc", "bearing_deg", "log10_BF_demonstrated_t3_3.3", "log10_BF_claimed_gauss_0.4",
             "P_signal_if_one_demonstrated_t3_3.3", "info_bits_demonstrated_t3_3.3"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
