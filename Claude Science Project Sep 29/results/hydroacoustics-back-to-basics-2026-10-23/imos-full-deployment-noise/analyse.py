"""QC, 8 March window ranks and diel statistics from the per-record table (rows_all.parquet).

QC (a record is excluded from statistics when any flag is set):
  qc_error      processing or download error
  qc_water      outside the metadata in-water window (3274 before 2013-12-29 23:30 UTC; 3250 after the
                'start last sample in water' 2014-06-02 04:15:01 UTC)
  qc_dc         |mean counts - logger median| > 200 counts (hardware fault: DC jumps of ~29-32 k counts or
                all-zero records; normal DC is stable to +/- 4 counts)
  qc_nonfinite  any band level not finite
  flag_clip     n_clip > 0 (kept, flagged)
  flag_overwritten  footer 'Data Validity - overwritten' (kept, flagged; levels and DC normal)
WINDOWS (true UTC, record start):
  W1 event window   2014-03-08 00:00-08:00 (span of the module's signal and background sets)
  W2 flight night   2014-03-07 16:00 - 2014-03-08 02:00
  W3 UTC day        2014-03-08 00:00-24:00
RANKS: for each logger and statistic X (5-40 Hz SPL and the band levels), the window median of X over
QC-passed records is ranked (i) among the same-clock-window medians of every other deployment day with
>= 80 % record coverage ('day-window rank', diel-controlled), for the deployment and for March 2014; and
(ii) within the pooled per-record distribution of the deployment and of March ('record rank').
Percentile rank = 100 * (#{x < v} + 0.5 #{x == v}) / n.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SITES = {"3376": dict(name="Perth Canyon", lon=115.013733, lat=-31.842167),
         "3274": dict(name="Portland", lon=141.247567, lat=-38.536967),
         "3250": dict(name="Scott Reef", lon=121.251, lat=-15.483367)}
IN_WATER = {"3274": (pd.Timestamp("2013-12-29T23:30:01Z"), None),
            "3250": (None, pd.Timestamp("2014-06-02T04:15:01Z")),
            "3376": (None, None)}
BANDCOLS = ["L_2_5", "L_5_10", "L_10_20", "L_20_40", "L_40_80", "L_80_160", "L_160_240", "L_5_40"]
STATS = ["SPL_5_40"] + BANDCOLS
WINDOWS = {"W1 event window 08 Mar 00:00-08:00 UTC": ("2014-03-08T00:00Z", "2014-03-08T08:00Z"),
           "W2 flight night 07 Mar 16:00 - 08 Mar 02:00 UTC": ("2014-03-07T16:00Z", "2014-03-08T02:00Z"),
           "W3 UTC day 08 Mar": ("2014-03-08T00:00Z", "2014-03-09T00:00Z")}


def qc(R: pd.DataFrame) -> pd.DataFrame:
    R = R.copy()
    R["t_utc"] = pd.to_datetime(R.start_utc_unix, unit="s", utc=True)
    R["qc_error"] = R.error.fillna("").ne("")
    R["qc_water"] = False
    for lg, (a, b) in IN_WATER.items():
        m = R.logger == lg
        if a is not None:
            R.loc[m & (R.t_utc < a), "qc_water"] = True
        if b is not None:
            R.loc[m & (R.t_utc > b), "qc_water"] = True
    med = R.groupby("logger").mean_counts.transform("median")
    R["dc_offset_counts"] = R.mean_counts - med
    R["qc_dc"] = R.dc_offset_counts.abs() > 200
    R["qc_nonfinite"] = ~np.isfinite(R[STATS + ["kurt_wave_5_40"]]).all(axis=1)
    R["flag_clip"] = R.n_clip.fillna(0) > 0
    R["flag_overwritten"] = R.validity.fillna("").eq("overwritten")
    R["qc_pass"] = ~(R.qc_error | R.qc_water | R.qc_dc | R.qc_nonfinite)
    lon = R.logger.map({k: v["lon"] for k, v in SITES.items()})
    R["local_solar_hour"] = ((R.t_utc.dt.hour + R.t_utc.dt.minute / 60 + R.t_utc.dt.second / 3600 + lon / 15) % 24)
    R["month"] = R.t_utc.dt.strftime("%Y-%m")
    return R


def prank(x, v):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return 100.0 * ((x < v).sum() + 0.5 * (x == v).sum()) / len(x), len(x)


def window_ranks(R: pd.DataFrame) -> pd.DataFrame:
    out = []
    Q = R[R.qc_pass]
    for lg, D in Q.groupby("logger"):
        for wname, (a, b) in WINDOWS.items():
            a, b = pd.Timestamp(a), pd.Timestamp(b)
            dur = (b - a).total_seconds()
            nexp = dur / 900.0
            win = D[(D.t_utc >= a) & (D.t_utc < b)]
            # same-clock window on every deployment day
            off = (D.t_utc - a.normalize()).dt.total_seconds()
            secs_a = (a - a.normalize()).total_seconds()
            rel = (off - secs_a) % 86400.0
            inw = rel < dur
            day0 = (D.t_utc - pd.to_timedelta(rel, unit="s")).dt.floor("D")
            g = D[inw].assign(wday=day0[inw])
            for st in STATS:
                v = float(np.median(win[st])) if len(win) else np.nan
                dm = g.groupby("wday")[st].agg(["median", "size"])
                dm = dm[dm["size"] >= 0.8 * nexp]
                ref_day = a.normalize()
                others = dm[dm.index != ref_day]
                mar = others[others.index.strftime("%Y-%m") == "2014-03"]
                r_dep, n_dep = prank(others["median"], v)
                r_mar, n_mar = prank(mar["median"], v)
                rr_dep, nr_dep = prank(D[st], v)
                rr_mar, nr_mar = prank(D[D.month == "2014-03"][st], v)
                out.append(dict(logger=lg, site=SITES[lg]["name"], window=wname, statistic=st, n_rec_window=len(win),
                                window_median=round(v, 2),
                                day_window_rank_deployment=round(r_dep, 1), n_days_deployment=n_dep,
                                day_window_rank_march=round(r_mar, 1), n_days_march=n_mar,
                                record_rank_deployment=round(rr_dep, 1), n_rec_deployment=nr_dep,
                                record_rank_march=round(rr_mar, 1), n_rec_march=nr_mar,
                                deployment_p5=round(float(np.percentile(D[st], 5)), 2),
                                deployment_p50=round(float(np.percentile(D[st], 50)), 2),
                                deployment_p95=round(float(np.percentile(D[st], 95)), 2),
                                march_p50=round(float(np.percentile(D[D.month == "2014-03"][st], 50)), 2)))
    return pd.DataFrame(out)


def diel(R: pd.DataFrame, st="SPL_5_40") -> pd.DataFrame:
    Q = R[R.qc_pass].copy()
    Q["h"] = np.floor(Q.local_solar_hour).astype(int)
    rows = []
    for (lg, h), d in Q.groupby(["logger", "h"]):
        for scope, dd in (("deployment", d), ("2014-03", d[d.month == "2014-03"])):
            if len(dd):
                rows.append(dict(logger=lg, scope=scope, local_solar_hour=h, n=len(dd),
                                 p10=np.percentile(dd[st], 10), p25=np.percentile(dd[st], 25),
                                 p50=np.percentile(dd[st], 50), p75=np.percentile(dd[st], 75),
                                 p90=np.percentile(dd[st], 90)))
    return pd.DataFrame(rows)


def diel_amplitude(R: pd.DataFrame, st="SPL_5_40") -> pd.DataFrame:
    """Peak-to-trough of hourly medians and a Kruskal-Wallis test of hour-of-day, per month and logger."""
    from scipy import stats
    Q = R[R.qc_pass].copy()
    Q["h"] = np.floor(Q.local_solar_hour).astype(int)
    rows = []
    for (lg, mo), d in Q.groupby(["logger", "month"]):
        hm = d.groupby("h")[st].median()
        if len(hm) < 24:
            continue
        H, p = stats.kruskal(*[g[st].values for _, g in d.groupby("h")])
        rows.append(dict(logger=lg, month=mo, n=len(d), hourly_median_range_db=round(hm.max() - hm.min(), 2),
                         peak_hour=int(hm.idxmax()), trough_hour=int(hm.idxmin()), kruskal_H=round(H, 1), p_value=p))
    return pd.DataFrame(rows)
