"""Raw vs published: (1) Nielsen 2021 Fig 5c (digitised PSD, H10N triad mean) against raw ESD -> implied PSD window T;
(2) raw PSD by Welch on the same 60 s window for a like-for-like check; (3) peak in several bands vs Vergoz 2021 printed
peaks and Brown 2026 Table A.4 (as digitised in the ground-truth table); (4) D2 Arons-relative ratios."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "scripts"); import meas as M
from obspy import UTCDateTime as U
from scipy.signal import welch
el = pd.read_csv("out/meas_elements.csv"); tb = pd.read_csv("out/triad_bands.csv")
ni = pd.read_csv("repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/calibration_events/nielsen_fig5cd_bands.csv"); ni = ni[ni.station == "H10N"].set_index("fc_hz")
ni_sig = 10 * np.log10(10 ** (ni.signal_db / 10) - 10 ** (ni.noise_db / 10))
r = tb[(tb.event == "sj_charge") & (tb.triad == "H10N") & (tb.window == "W60")].set_index("fc_hz")
out = []
# raw Welch PSD, triad mean, on the 20 s window centred on the peak (signal) and the preceding 20 s (noise), nperseg 4 s
for s in ("H10N1", "H10N2", "H10N3"):
    tr, c = M.load(f"raw/sj_charge_{s}.mseed", "raw/sj_charge_resp.xml"); fs = 250.0
    k = int((U(el[(el.event == "sj_charge") & (el.station == s)].t_peak_utc.iloc[0]) - tr.stats.starttime) * fs)
    for lab, a, b in (("sig20", k - int(10 * fs), k + int(10 * fs)), ("noise20", k - int(40 * fs), k - int(20 * fs)), ("sig60", k - int(30 * fs), k + int(30 * fs)), ("noise60", k - int(100 * fs), k - int(40 * fs))):
        f, p = welch(tr.data[a:b], fs=fs, nperseg=int(4 * fs)); out.append((s, lab, f, p))
rows = []
for fc in ni.index:
    lo, hi = M.band_edges(fc)
    def band(lab):
        v = [np.mean(p[(f >= lo) & (f < hi)]) for s, l, f, p in out if l == lab]; return 10 * np.log10(np.mean(v)) + 120
    rows.append(dict(fc_hz=fc, nielsen_signal_psd_dB=ni.signal_db[fc], nielsen_noise_psd_dB=ni.noise_db[fc], nielsen_sig_minus_noise_psd_dB=ni_sig[fc],
                     raw_welch_psd_sig20_dB=band("sig20"), raw_welch_psd_noise20_dB=band("noise20"), raw_welch_psd_sig60_dB=band("sig60"), raw_welch_psd_noise60_dB=band("noise60"),
                     raw_esd_W60_dB=r.esd_dB[fc], implied_T_s=10 ** ((r.esd_dB[fc] - ni_sig[fc]) / 10)))
cmp = pd.DataFrame(rows); cmp.to_csv("out/nielsen_fig5c_vs_raw.csv", index=False); print(cmp.round(1).to_string())
# peaks in several bands
pk = []
BANDS = {"1-60": (1, 60), "2-40": (2, 40), "4-40": (4, 40), "4-9": (4, 9), "2-8": (2, 8), "5-20": (5, 20), "3-30": (3, 30), "broadband 1-110": (1, 110)}
for _, e in el.iterrows():
    tr, c = M.load(f"raw/{e.event}_{e.station}.mseed", f"raw/{e.event}_resp.xml"); fs = 250.0; k = int((U(e.t_peak_utc) - tr.stats.starttime) * fs); w = int(30 * fs)
    d = dict(event=e.event, station=e.station, range_km=e.range_km)
    for n, (a, b) in BANDS.items():
        x = M.bp(tr.data, fs, a, b) if b < 110 else tr.data
        d[f"peak_{n}_Pa"] = float(np.max(np.abs(x[k - w:k + w])))
    pk.append(d)
pk = pd.DataFrame(pk); pk.to_csv("out/peaks_by_band.csv", index=False)
pk["triad"] = pk.station.str[:4]; good = pk[pk.station != "H10S1"]
print(good.groupby(["event", "triad"])[[c for c in pk.columns if c.startswith("peak_")]].median().round(2).to_string())
