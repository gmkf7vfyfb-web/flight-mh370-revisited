"""Pre-registered measurement (out/prereg.md M1-M8) on raw H10 records. Writes out/meas_elements.csv, out/meas_bands.csv, out/meas_baz.csv."""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, "scripts"); import meas as M
from obspy import UTCDateTime as U
SRC = {"sj_event": ("2017-11-15T13:51:05", -45.950, -59.773), "sj_charge": ("2017-12-01T20:04:30", -45.666, -59.240),
       "fsst16_1": ("2016-06-10T17:10:48.64", 30.0335, -79.6406), "fsst16_2": ("2016-06-23T17:20:29.45", 29.9948, -79.449),
       "fsst16_3": ("2016-07-16T20:00:10.22", 29.7651, -79.4341), "fsst16_4": ("2016-09-04T18:29:29.80", 30.0952, -79.5416),
       "fsst16_5": ("2016-09-21T16:30:52.90", 30.0745, -79.5044), "fsst21_1": ("2021-06-18T19:48:39.595", 29.7433, -79.3493),
       "fsst21_2": ("2021-07-16T17:48:33.533", 30.0852, -79.3251), "fsst21_3": ("2021-08-08T19:55:18.252", 30.1465, -79.6066)}
STAS = ["H10N1", "H10N2", "H10N3", "H10S1", "H10S2", "H10S3"]
WINS = {"W60": (-30, 30), "W20": (-10, 10), "W120": (-40, 80)}
el_rows, band_rows, baz_rows = [], [], []
for ev, (o, la, lo) in SRC.items():
    o = U(o); traces = {}; coords = {}; starts = {}
    for s in STAS:
        try:
            tr, c = M.load(f"raw/{ev}_{s}.mseed", f"raw/{ev}_resp.xml")
        except FileNotFoundError:
            continue
        fs = tr.stats.sampling_rate; x = tr.data
        _, _, d = M.G.inv(lo, la, c["lon"], c["lat"]); d /= 1000.0
        a = o + d / 1.500 - 60; b = o + d / 1.460 + 60
        x240 = M.bp(x, fs, 2, 40); env = M.rms1(x240, fs)
        t = tr.stats.starttime; i0 = max(0, int((a - t) * fs)); i1 = min(len(x), int((b - t) * fs))
        k = i0 + int(np.argmax(env[i0:i1])); tpk = t + k / fs
        x440 = M.bp(x, fs, 4, 40); x160 = M.bp(x, fs, 1, 60); e440 = M.rms1(x440, fs)
        r = dict(event=ev, station=s, triad=s[:4], lat=c["lat"], lon=c["lon"], depth_m=c["depth_m"], unit=c["unit"], gap_samples=c["gap_samples"],
                 range_km=d, t_peak_utc=str(tpk), travel_s=tpk - o, group_speed_km_s=d / (tpk - o),
                 env_peak_2_40_Pa=float(env[k]), env_noise_median_2_40_Pa=float(np.median(env[max(0, k - int(660 * fs)):k - int(60 * fs)])) if k > int(660 * fs) else np.nan)
        w = int(30 * fs)
        r["inst_peak_1_60_Pa"] = float(np.max(np.abs(x160[k - w:k + w]))); r["inst_peak_4_40_Pa"] = float(np.max(np.abs(x440[k - w:k + w])))
        j = k - w + int(np.argmax(e440[k - w:k + w])); r["rms1_peak_4_40_Pa"] = float(e440[j]); r["t_rms1_peak_4_40"] = str(t + j / fs)
        r["rms1_noise_median_4_40_Pa"] = float(np.median(e440[max(0, k - int(660 * fs)):k - int(60 * fs)])) if k > int(660 * fs) else np.nan
        r["snr_rms1_4_40_dB"] = 20 * np.log10(r["rms1_peak_4_40_Pa"] / r["rms1_noise_median_4_40_Pa"])
        for wn, (u0, u1) in WINS.items():
            s0 = k + int(u0 * fs); s1 = k + int(u1 * fs); L = s1 - s0
            sig, tot = M.band_exposure(x[s0:s1], fs)
            noises = []
            for q in range(10):
                n1 = s0 - int(60 * fs) - q * L; n0 = n1 - L
                if n0 < int(5 * fs): break
                noises.append(M.band_exposure(x[n0:n1], fs)[0])
            for fc in M.FC_ALL:
                nv = np.array([nn[fc] for nn in noises]); nmed = float(np.median(nv)) if len(nv) else np.nan
                Es = sig[fc] - nmed
                band_rows.append(dict(event=ev, station=s, window=wn, fc_hz=fc, E_total_Pa2s=sig[fc], E_noise_med_Pa2s=nmed,
                                      E_noise_p16=float(np.quantile(nv, .16)) if len(nv) else np.nan, E_noise_p84=float(np.quantile(nv, .84)) if len(nv) else np.nan,
                                      n_noise=len(nv), E_signal_Pa2s=Es, snr_dB=10 * np.log10(sig[fc] / nmed) if nmed > 0 else np.nan,
                                      esd_signal_dB=M.db_esd(Es, fc) if Es > 0 else np.nan))
        el_rows.append(r); traces[s] = x440; coords[s] = c; starts[s] = (t, k)
        print(ev, s, f"{d:.1f} km", str(tpk)[11:22], f"c={r['group_speed_km_s']:.4f}", f"pk1-60={r['inst_peak_1_60_Pa']:.3f} Pa", f"rms1={r['rms1_peak_4_40_Pa']:.3f}", f"snr={r['snr_rms1_4_40_dB']:.1f} dB", flush=True)
    for tri in ("H10N", "H10S"):
        ss = [s for s in traces if s.startswith(tri)]
        if len(ss) < 3: continue
        t0 = max(starts[s][0] for s in ss)
        al = {s: traces[s][int((t0 - starts[s][0]) * 250):] for s in ss}
        kk = int(np.median([starts[s][1] - int((t0 - starts[s][0]) * 250) for s in ss]))
        bz = M.baz_fit(al, coords, 250.0, kk - 2500, kk + 2500)
        lat0 = np.mean([coords[s]["lat"] for s in ss]); lon0 = np.mean([coords[s]["lon"] for s in ss])
        geo_baz = M.G.inv(lon0, lat0, SRC[ev][2], SRC[ev][1])[0] % 360
        baz_rows.append(dict(event=ev, triad=tri, baz_obs_deg=bz["baz_deg"], baz_geodesic_deg=geo_baz, baz_resid_deg=(bz["baz_deg"] - geo_baz + 180) % 360 - 180,
                             app_speed_km_s=bz["app_speed_km_s"], min_pair_cc=min(bz["pair_cc"]), resid_rms_s=bz["resid_rms_s"]))
        print(ev, tri, {k: round(v, 3) if isinstance(v, float) else v for k, v in baz_rows[-1].items()})
pd.DataFrame(el_rows).to_csv("out/meas_elements.csv", index=False); pd.DataFrame(band_rows).to_csv("out/meas_bands.csv", index=False); pd.DataFrame(baz_rows).to_csv("out/meas_baz.csv", index=False)
