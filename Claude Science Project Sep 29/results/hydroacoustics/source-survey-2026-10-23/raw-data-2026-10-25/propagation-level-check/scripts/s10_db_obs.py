"""db_received_observation rows (same definitions as OB01-OB06): 1-s RMS peak (4-40 Hz), median 1-s RMS over the preceding
10 min, SNR, instantaneous peak (4-40 Hz), exposure = sum x^2 dt over peak +/-15 s minus median-noise^2 x 30 s (4-40 Hz)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "scripts"); import meas as M
from obspy import UTCDateTime as U
el = pd.read_csv("out/meas_elements.csv"); rows = []; n = 7
EVID = {"sj_event": "E14", "sj_charge": "E12"}
for _, e in el.iterrows():
    tr, c = M.load(f"raw/{e.event}_{e.station}.mseed", f"raw/{e.event}_resp.xml"); fs = 250.0; x = M.bp(tr.data, fs, 4, 40); env = M.rms1(x, fs)
    j = int((U(e.t_rms1_peak_4_40) - tr.stats.starttime) * fs); w = int(15 * fs)
    med = float(np.median(env[j - int(660 * fs): j - int(60 * fs)])); E = float(np.sum(x[j - w:j + w] ** 2) / fs - med ** 2 * 30)
    note = "; EXCLUDED: element reads ~30 dB below H10S2/S3 in every event (Nielsen 2021: H10S1 electronic noise, excluded from IDC processing)" if e.station == "H10S1" else ""
    rows.append(dict(obs_id=f"OB{n:02d}", evidence_id=EVID.get(e.event, "E12"), station=e.station, peak_time_utc=U(e.t_rms1_peak_4_40).strftime("%H:%M:%S"),
                     peak_1sRMS_Pa=round(e.rms1_peak_4_40_Pa, 3), median_1sRMS_Pa=round(med, 4), snr_dB=round(20 * np.log10(e.rms1_peak_4_40_Pa / med), 1),
                     instant_peak_Pa=round(e.inst_peak_4_40_Pa, 3), exposure_Pa2s_30s=round(E, 4), band_Hz="4-40", date=U(e.t_peak_utc).strftime("%Y-%m-%d"),
                     method=f"{e.event}: raw EarthScope IM EDH; full StationXML response removed (pre-filt 0.5/1/110/120 Hz); 4-pole zero-phase 4-40 Hz; 1-s moving RMS; exposure = sum x^2 dt over peak +/-15 s minus median-noise^2 x 30 s; range {e.range_km:.1f} km{note}"))
    n += 1
df = pd.DataFrame(rows); old = pd.read_csv("inputs/pkg/coupling-db-package/db_received_observation.csv")
pd.concat([old, df]).to_csv("out/db_received_observation.csv", index=False); print(len(df), "new rows"); print(df.iloc[:, :10].to_string())
