cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; grep -n "^FS_D\|^Q\b\|^Q =\|^NPER" imos_noise.py; cat > cmst_fig1_imos_overlay.py <<'EOF'
"""Overlay check (correction track 22 Oct 2026, gap G8): CMST 2014-30 Fig. 1 (Perth Canyon logger, 01:33:44 UTC signal),
DIGITISED, against the module's own calibrated read of the IMOS raw recording 3315 / 531A728A.DAT (role B; logger clock
corrected by the pre-registered clock_err, results-data/imos1d/clock_test.json: +25.82 s, verdict A).
Rule fixed before the comparison: calibrate exactly as run_j_levels_charts.charts_traces (Curtin gain file, sens_db), then two
bands: (i) 1-120 Hz (CMST's displayed spectrogram spans 0-125 Hz, i.e. fs 250 Hz; their time-series filter is not stated),
(ii) 5-40 Hz (Kadri / module band). Compare on CMST's displayed span 100-275 s after 01:30:00 UTC: peak |p| and its time,
and the 99th percentile of the column envelope outside 205-245 s (CMST digitised: peak 1.42 Pa at 224.3 s, noise p99 0.66 Pa).
Column envelope of the IMOS series is formed on CMST's own pixel grid (0.69 s per column) so the two are like for like.
DIGITISED vs MEASURED; no tuning. Usage: python cmst_fig1_imos_overlay.py <digitised_csv> <out_dir>"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
import imos_noise as N, imos_preregistration as P  # noqa: E402
HERE = Path(__file__).parent.parent

def main(dig_csv, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    pre = json.loads((HERE / "data/imos/preregistration.json").read_text()); L = pre["loggers"]["3315"]
    clk = json.loads((HERE / "results-data/imos1d/clock_test.json").read_text())["clock_err_s"]
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    r = recs[(recs.logger == 3315) & (recs.file.str.endswith("531A728A.DAT"))].iloc[0]
    calp = next(P.IMOS.glob(f"*/*alibration/{L['cal_file']}")); fg, G = N.gain_db(calp)
    xd = N.decimate(N.read_volts(P.IMOS / r.file)); fs = N.FS_D
    X = np.fft.rfft(xd); f = np.fft.rfftfreq(len(xd), 1 / fs)
    cal = 10 ** ((np.interp(f, fg, G) + L["sens_db"]) / 20); cal[f < 1] = cal[f >= 1][0]
    x_pa = np.fft.irfft(X / cal, n=len(xd)) * 1e-6
    t_utc0 = r.start_logger - pd.Timedelta(seconds=clk)
    ts = (t_utc0 - pd.Timestamp("2014-03-08T01:30:00Z")).total_seconds() + np.arange(len(x_pa)) / fs
    dig = pd.read_csv(dig_csv); dcol = float(np.median(np.diff(dig.t_s)))
    res = {"file": r.file, "clock_err_s": clk, "fs_hz": fs, "logger_start": str(r.start_logger)}
    for lab, band in (("1-120Hz", [1, 120]), ("5-40Hz", [5, 40])):
        sos = signal.butter(4, band, btype="bandpass", fs=fs, output="sos"); xb = signal.sosfiltfilt(sos, x_pa)
        edges = np.arange(100, 275 + dcol, dcol); idx = np.digitize(ts, edges)
        tc, up, lo = [], [], []
        for k in range(1, len(edges)):
            m = idx == k
            if m.sum(): tc.append(0.5 * (edges[k - 1] + edges[k])); up.append(xb[m].max()); lo.append(xb[m].min())
        tc, up, lo = map(np.array, (tc, up, lo)); env = np.where(np.abs(up) > np.abs(lo), up, lo)
        win = (tc >= 205) & (tc <= 245); i = int(np.argmax(np.abs(env)))
        res[lab] = dict(peak_pa=float(np.abs(env).max()), t_peak_s=float(tc[i]), noise_p99_pa=float(np.percentile(np.abs(env[~win]), 99)))
        pd.DataFrame(dict(t_s=tc, upper_pa=up, lower_pa=lo)).to_csv(out / f"imos3315_531A728A_{lab}_column_envelope.csv", index=False)
    de = np.where(np.abs(dig.upper) > np.abs(dig.lower), dig.upper, dig.lower); win = (dig.t_s >= 205) & (dig.t_s <= 245)
    res["cmst_digitised"] = dict(peak_pa=float(np.abs(de).max()), t_peak_s=float(dig.t_s[np.argmax(np.abs(de))]), noise_p99_pa=float(np.percentile(np.abs(de[~win]), 99)))
    for lab in ("1-120Hz", "5-40Hz"):
        res[lab]["peak_ratio_db_measured_minus_cmst"] = 20 * np.log10(res[lab]["peak_pa"] / res["cmst_digitised"]["peak_pa"])
        res[lab]["noise_ratio_db_measured_minus_cmst"] = 20 * np.log10(res[lab]["noise_p99_pa"] / res["cmst_digitised"]["noise_p99_pa"])
        res[lab]["dt_peak_s_measured_minus_cmst"] = res[lab]["t_peak_s"] - res["cmst_digitised"]["t_peak_s"]
    (out / "cmst_fig1_vs_imos3315.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:3])
EOF
python cmst_fig1_imos_overlay.py ../results-data/digitised/waveform-rasters/cmst2014_fig1_perth_canyon_DIGITISED.csv ../results-data/digitised/waveform-rasters/cmst_fig1_overlay