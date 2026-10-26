#!/usr/bin/env python3
"""noise_caveat_calibration.py - shape ratios for reading band RMS from digitised IMS pressure traces (noise caveat fix C1,
26 Oct 2026; pre-registration results/hydroacoustics/noise-caveat-fixes-2026-10-26/PREREGISTRATION.md on claude-science-sep29).

The Kadri 2024 Fig. 9 traces are PDF vector vertices (about 14.5 per second, mostly local extrema). Their RMS is not the
signal RMS. The peak-to-peak range PP in one second is kept by any envelope-preserving plot reduction. This script measures,
on HELD raw IMS records (EarthScope FDSN, network IM, channel EDH, StationXML response removed to Pa), the ratio
k = PP / RMS over 1-s windows, for three filter variants, and two diagnostics of the plot reduction:
  * pp_retention: PP of a min/max decimation (bin = 1 / (vertex rate / 2)) over PP of the raw signal (1 = kept);
  * vrms_ratio:  RMS of the min/max-decimated vertices over the true RMS (second estimator, cross-check only).
No synthetic data. The records are re-fetchable without credentials (fdsnws dataselect; see the record table).

Amendment 1 (26 Oct 2026, pre-registration): STATION may carry a set label, STATION:SET (for example H01W:march for the
8 March 2015-2019 records in the Kadri clock windows, H01W:held for the held December 2014 record). The primary k is
the 'march' set with the zero-phase 4-pole 5-40 Hz variant. Extra columns: k_dec80 (PP after decimation to 80 samples/s
over the full-rate RMS: plotting-rate term) and vertex_kurtosis (excess kurtosis of the min/max-decimated vertices).

Usage: python noise_caveat_calibration.py --rec H01W:march <mseed> <stationxml> [--rec ...] --out <dir>
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd
import obspy
from scipy.signal import butter, sosfilt, sosfiltfilt, resample_poly
from scipy import stats

VERTEX_RATE = 14.5          # vertices per second in the Kadri Fig. 9 tables (measured on the DB tables, 26 Oct 2026)
VARIANTS = {
    "zero-phase 4-pole 5-40 Hz": lambda fs: [("ff", butter(4, [5, 40], btype="band", fs=fs, output="sos"))],
    "causal 4-pole 5-40 Hz": lambda fs: [("f", butter(4, [5, 40], btype="band", fs=fs, output="sos"))],
    "causal 2-pole HP 5 Hz + 4-pole 2-40 Hz (Kadri Methods)": lambda fs: [("f", butter(2, 5, btype="high", fs=fs, output="sos")),
                                                                         ("f", butter(4, [2, 40], btype="band", fs=fs, output="sos"))],
}
EDGE_S = 30.0               # seconds dropped at both ends of each contiguous trace (filter and taper transients)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def windows(y, fs, w=1.0):
    n = int(round(w * fs)); m = len(y) // n
    Y = y[: m * n].reshape(m, n)
    return Y


def minmax(Y, fs, binw):
    """min/max decimation inside each 1-s row: bins of binw seconds, two vertices per bin."""
    n = Y.shape[1]; b = max(1, int(round(binw * fs))); nb = n // b
    Z = Y[:, : nb * b].reshape(Y.shape[0], nb, b)
    return np.concatenate([Z.min(2), Z.max(2)], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rec", nargs=3, action="append", metavar=("STATION", "MSEED", "XML"), required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows, recs = [], []
    for station_set, ms, xml in a.rec:
        station, _, rset = station_set.partition(":"); rset = rset or "held"
        st = obspy.read(ms); inv = obspy.read_inventory(xml)
        st.merge(fill_value=None)
        st = st.split()
        recs.append(dict(station=station, set=rset, mseed=Path(ms).name, mseed_sha256=sha(ms), xml=Path(xml).name, xml_sha256=sha(xml),
                         ids=";".join(sorted({t.id for t in st})), t_start=str(min(t.stats.starttime for t in st)),
                         t_end=str(max(t.stats.endtime for t in st))))
        for tr in st:
            if tr.stats.npts / tr.stats.sampling_rate < 4 * EDGE_S:
                continue
            fs = tr.stats.sampling_rate
            t = tr.copy(); t.detrend("demean"); t.taper(0.01)
            t.remove_response(inventory=inv, output="DEF", pre_filt=(0.5, 1, 110, 120), zero_mean=True)
            e = int(EDGE_S * fs)
            for vname, mk in VARIANTS.items():
                y = t.data.astype(float)
                for mode, sos in mk(fs):
                    y = sosfiltfilt(sos, y) if mode == "ff" else sosfilt(sos, y)
                Y = windows(y[e:-e], fs)
                rms = np.sqrt((Y ** 2).mean(1)); pp = Y.max(1) - Y.min(1)
                V = minmax(Y, fs, 2.0 / VERTEX_RATE)
                pp_v = V.max(1) - V.min(1); vrms = np.sqrt((V ** 2).mean(1))
                y80 = resample_poly(y[e:-e], 8, int(round(fs / 10)))      # 250 -> 80 samples/s
                Y80 = windows(y80, 80.0); m80 = min(len(Y80), len(rms))
                pp80 = Y80[:m80].max(1) - Y80[:m80].min(1)
                rows.append(dict(station=station, set=rset, record=Path(ms).name, trace_id=tr.id, trace_start=str(tr.stats.starttime), variant=vname,
                                 n_windows=len(rms), median_rms_db=20 * np.log10(np.median(rms) / 1e-6),
                                 k_median=float(np.median(pp / rms)), k_p5=float(np.percentile(pp / rms, 5)), k_p95=float(np.percentile(pp / rms, 95)),
                                 k_ratio_of_medians=float(np.median(pp) / np.median(rms)),
                                 pp_retention_median=float(np.median(pp_v / pp)), vrms_ratio_median=float(np.median(vrms / rms)),
                                 k_dec80=float(np.median(pp80 / rms[:m80])), vertex_kurtosis=float(stats.kurtosis(V.ravel()))))
    R = pd.DataFrame(rows)
    # pool per station and variant, weighting each trace segment by its window count
    pool = []
    for (s, rs, v), g in R.groupby(["station", "set", "variant"]):
        w = g.n_windows / g.n_windows.sum()
        pool.append(dict(station=s, set=rs, variant=v, n_windows=int(g.n_windows.sum()), n_segments=len(g), k_median=float((g.k_median * w).sum()),
                         k_min_segment=float(g.k_median.min()), k_max_segment=float(g.k_median.max()),
                         pp_retention_median=float((g.pp_retention_median * w).sum()), vrms_ratio_median=float((g.vrms_ratio_median * w).sum()),
                         k_dec80=float((g.k_dec80 * w).sum()), vertex_kurtosis=float((g.vertex_kurtosis * w).sum())))
    PL = pd.DataFrame(pool)
    R.to_csv(out / "pp_rms_calibration_segments.csv", index=False)
    PL.to_csv(out / "pp_rms_calibration.csv", index=False)
    pd.DataFrame(recs).to_csv(out / "pp_rms_calibration_records.csv", index=False)
    summ = {}
    for s, g in PL.groupby("station"):
        prim = "march" if (g.set == "march").any() else "held"
        ref = g[(g.variant == "zero-phase 4-pole 5-40 Hz") & (g.set == prim)].iloc[0]
        allk = g.k_median            # spread (b): filter variants x record sets, pooled per set
        summ[s] = dict(primary_set=prim, k=float(ref.k_median), k_min=float(allk.min()), k_max=float(allk.max()),
                       k_sigma_db=float(20 * np.log10(allk.max() / allk.min()) / 2),
                       k_dec80=float(ref.k_dec80), plot_rate_sigma_db=float(abs(20 * np.log10(ref.k_median / ref.k_dec80)) / 2),
                       pp_retention=float(ref.pp_retention_median), vrms_ratio=float(ref.vrms_ratio_median),
                       vertex_kurtosis=float(ref.vertex_kurtosis))
    (out / "pp_rms_calibration_summary.json").write_text(json.dumps(dict(vertex_rate_per_s=VERTEX_RATE, edge_s=EDGE_S,
                                                                          variants=list(VARIANTS), stations=summ), indent=1))
    print(PL.to_string()); print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
