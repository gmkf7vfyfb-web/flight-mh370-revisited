"""Build the station data package for the reverse-sensing screening track (8 Mar 2014, 00:00-03:00 UTC).

Read-only use of: hydro_data.sqlite (segment, dataset, dg_* tables) and the raw IMOS .DAT files under
~/Downloads/mh370-inputs/hydroacoustics/imos. Writes to ./station-data/.
Time axis everywhere: `utc` (datetime64 UTC) and `t_s` = seconds after 2014-03-08T00:00:00Z (true UTC).
IMOS times are clock-corrected (true UTC = logger time - e(t)), taken from the DB segment table.
"""
from __future__ import annotations
import json, sqlite3, hashlib, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal

A = Path('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63')
DB = A / 'b3b0fe8f-b907-4214-9c02-18f9a4bf778c/v321ea0f6_hydro_data.sqlite'
INPUTS = Path('/Users/pete/Downloads/mh370-inputs/hydroacoustics')
T_REF = pd.Timestamp('2014-03-08T00:00:00Z')
PKG_T0, PKG_T1 = 0.0, 3 * 3600.0           # package span, s after T_REF
OUT = Path('station-data'); OUT.mkdir(exist_ok=True)
FS, Q_W = 6000.0, 24                      # waveform: 6000 Hz -> 250 Hz (anti-alias FIR in resample_poly)
Q_B = 12                                  # band power: 6000 -> 500 Hz (same as network-search reader)
IMOS_CAL = {
    'IMOS3315': dict(cal='MH370/Calibration/52946955.DAT', sens_db=-197.8),
    'IMOS3250': dict(cal='MH370/Calibration/5236BCF7.DAT', sens_db=-197.7),
    'IMOS3376': dict(cal='MH370/Calibration/529482AC.DAT', sens_db=-196.0),
    'IMOS3274': dict(cal='Portland_MH370/calibration/54E49F6D.DAT', sens_db=-196.0),
    'IMOS3275': dict(cal='Portland_MH370/calibration/54E4975C.DAT', sens_db=-196.0),
}

con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)


def to_s(ts):
    t = pd.to_datetime(pd.Series(ts).astype(str).str.replace('Z', '', regex=False), utc=True, format='ISO8601')
    return ((t - T_REF).dt.total_seconds()).to_numpy()


def utc(t_s):
    return T_REF + pd.to_timedelta(np.asarray(t_s, float), unit='s')


def read_volts(path):
    """Port of Curtin load_loggerdatanew.m: 5 header lines, big-endian uint16, footer from 'Record'; volts, mean removed."""
    raw = Path(path).read_bytes()
    pos = 0
    for _ in range(5):
        pos = raw.index(b'\n', pos) + 1
    tail = raw[-1000:]
    end = len(raw) - (1000 - tail.index(b'Record')) - 2
    n = (end - pos) // 2
    x = np.frombuffer(raw, dtype='>u2', count=n, offset=pos).astype(np.float64) * (5.0 / 65536)
    return x - x.mean()


def gain(station):
    x = signal.resample_poly(read_volts(INPUTS / 'imos' / IMOS_CAL[station]['cal']), 1, Q_B)
    fd = FS / Q_B
    f, p = signal.welch(x, fs=fd, window='hann', nperseg=int(4 * fd), noverlap=int(2 * fd), detrend='constant')
    return f, 10 * np.log10(p) + 90.0


def band_power(volts, sens_db, g, bands=((5, 40), (10, 40)), win_s=1.0, hop_s=0.5):
    fg, G = g
    x = signal.resample_poly(volts, 1, Q_B)
    fd = FS / Q_B
    nper, nhop = int(win_s * fd), int(hop_s * fd)
    f, tt, Z = signal.stft(x, fs=fd, window='hann', nperseg=nper, noverlap=nper - nhop, detrend=False,
                           boundary=None, padded=False, scaling='psd')
    P = np.abs(Z) ** 2
    P[1:-1] *= 2.0
    Pu = P / (10 ** ((np.interp(f, fg, G) + sens_db) / 10))[:, None]
    df = f[1] - f[0]
    return tt - win_s / 2, {b: Pu[(f >= b[0]) & (f < b[1])].sum(axis=0) * df for b in bands}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


cov_rows, files = [], {}
# ------------------------------------------------------------------ IMOS raw loggers
bp_rows = []
for st in IMOS_CAL:
    seg = pd.read_sql(f"select * from segment where dataset_id='{st.lower()}_mh370_day'", con)
    seg['t0'] = to_s(seg.t_start_utc); seg['t1'] = to_s(seg.t_end_utc)
    seg = seg[(seg.t1 > PKG_T0) & (seg.t0 < PKG_T1)].sort_values('t0').reset_index(drop=True)
    g = gain(st)
    waves, starts, ns, names, shas, cerr = [], [], [], [], [], []
    for i, r in seg.iterrows():
        p = Path(str(r.file_path).replace('INPUTS:', str(INPUTS) + '/'))
        v = read_volts(p)
        if sha(p) != r.sha256:
            sys.exit(f'SHA mismatch {p}')
        w = signal.resample_poly(v, 1, Q_W).astype(np.float32)
        waves.append(w); starts.append(r.t0); ns.append(len(w)); names.append(r.label); shas.append(r.sha256)
        cerr.append(r.clock_err_s)
        tb, bp = band_power(v, IMOS_CAL[st]['sens_db'], g)
        bp_rows.append(pd.DataFrame(dict(station=st, record=r.label, t_s=r.t0 + tb, dt=1.0,
                                         p_5_40_upa2=bp[(5, 40)], p_10_40_upa2=bp[(10, 40)])))
        cov_rows.append(dict(station=st, form='raw waveform (duty-cycled)', block=r.label, t_start_s=r.t0, t_end_s=r.t1,
                             sample_rate_hz=FS, band='8 Hz hardware high-pass to 2800 Hz', source=str(p)))
    fn = OUT / f'{st.lower()}_waveform_250hz.npz'
    np.savez_compressed(fn, volts=np.concatenate(waves), rec_start_t_s=np.array(starts), rec_n=np.array(ns),
                        rec_name=np.array(names), rec_sha256=np.array(shas), rec_clock_err_s=np.array(cerr),
                        fs_hz=FS / Q_W, gain_f_hz=g[0], gain_db=g[1], sens_db=IMOS_CAL[st]['sens_db'],
                        note=np.array('Volts at the logger input (mean removed), decimated 6000->250 Hz with '
                                      'scipy resample_poly (FIR anti-alias). Sample k of record j is at '
                                      't_s = rec_start_t_s[j] + k/250. Pressure spectral density: '
                                      'dB re 1 uPa^2/Hz = 10log10(V^2/Hz) - gain_db(f) - sens_db. '
                                      '8 Hz hardware high-pass: content below 8 Hz is not ambient noise.'))
    files[fn.name] = 'IMOS raw waveform, 250 Hz volts, per record'
bp = pd.concat(bp_rows, ignore_index=True)
bp['utc'] = utc(bp.t_s)
bp.to_parquet(OUT / 'imos_band_power_1s.parquet', index=False)
files['imos_band_power_1s.parquet'] = 'IMOS calibrated band power, 1 s Hann windows, 0.5 s hop, 5-40 and 10-40 Hz (uPa^2)'

# ------------------------------------------------------------------ Kadri 2024 Fig. 9 digitised traces
kv = []
for st, pnls in {'H01W': ['a_h01w', 'b_h01w', 'c_h01w'], 'H08S': ['d_h08s', 'e_h08s']}.items():
    for pnl in pnls:
        d = pd.read_sql(f'select utc, pressure_pa from dg_data_kadri_fig9_digitised_kadri_2024_figure9_panel_{pnl}', con)
        d['t_s'] = to_s(d.utc); d['station'] = st; d['panel'] = pnl
        kv.append(d[['station', 'panel', 't_s', 'pressure_pa']])
kv = pd.concat(kv, ignore_index=True).sort_values(['station', 't_s'])
kv['utc'] = utc(kv.t_s)
kv.to_parquet(OUT / 'kadri2024_fig9_vertices.parquet', index=False)
files['kadri2024_fig9_vertices.parquet'] = 'Kadri 2024 Fig. 9 digitised pressure vertices (5-40 Hz band-passed trace), Pa'
for (st, pnl), g_ in kv.groupby(['station', 'panel']):
    cov_rows.append(dict(station=st, form='digitised envelope (Kadri 2024 Fig. 9)', block=pnl, t_start_s=g_.t_s.min(),
                         t_end_s=g_.t_s.max(), sample_rate_hz=len(g_) / (g_.t_s.max() - g_.t_s.min()), band='5-40 Hz',
                         source=f'hydro_data.sqlite dg_data_kadri_fig9_digitised_kadri_2024_figure9_panel_{pnl}'))

# ------------------------------------------------------------------ Royer 2016 digitised spectrograms (band series)
STMAP = {'h01w2': 'H01W', 'sseir': 'SSEIR', 'swams3': 'SWAMS3', 'swams2': 'SWAMS2', 'mad': 'MAD', 'ncro': 'NCRO', 'wker': 'WKER'}
rs = []
tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'dg_royer_2016_spectrograms_%_band'")]
for t in tabs:
    key = [k for k in STMAP if f'_{k}_' in t][0]
    d = pd.read_sql(f'select * from {t}', con).dropna(subset=['t_utc_s'])
    d['station'] = STMAP[key]; d['panel'] = t.replace('dg_royer_2016_spectrograms_', '').replace('_band', '')
    rs.append(d.rename(columns={'t_utc_s': 't_s'}))
rs = pd.concat(rs, ignore_index=True)
rs['utc'] = utc(rs.t_s)
rs.to_parquet(OUT / 'royer2016_spectrogram_bands.parquet', index=False)
files['royer2016_spectrogram_bands.parquet'] = ('Royer 2016 spectrogram colour readings, band-mean PSD dB re 1 uPa^2/Hz '
                                                '(5-40, 10-15, 2-60 Hz); colour scale saturates; offset uncalibrated')
segR = pd.read_sql("select s.*, d.site_id from segment s join dataset d using(dataset_id) where dataset_id like 'royer2016_spectrograms_%'", con)
for _, r in segR.iterrows():
    cov_rows.append(dict(station=r.site_id, form='digitised spectrogram (Royer 2016)', block=r.label,
                         t_start_s=to_s([r.t_start_utc])[0], t_end_s=to_s([r.t_end_utc])[0], sample_rate_hz=r.sample_rate_hz,
                         band=f'{r.band_lo_hz:.2f}-{r.band_hi_hz:.1f} Hz (plot axis)', source=r.file_path))

# ------------------------------------------------------------------ CMST 2014 digitised traces (short, 01:31-01:36)
cm = []
for t, st, lab in [('dg_waveform_rasters_cmst2014_fig1_perth_canyon_digitised', 'IMOS3315', 'CMST Fig. 1 Perth Canyon trace'),
                   ('dg_waveform_rasters_cmst2014_fig2_ha01_h1_band_digitised', 'H01W', 'CMST Fig. 2 element 1'),
                   ('dg_waveform_rasters_cmst2014_fig2_ha01_h2_band_digitised', 'H01W', 'CMST Fig. 2 element 2'),
                   ('dg_waveform_rasters_cmst2014_fig2_ha01_h3_band_digitised', 'H01W', 'CMST Fig. 2 element 3')]:
    d = pd.read_sql(f'select * from {t}', con)
    d.insert(0, 'trace', lab); d.insert(0, 'station', st)
    cm.append(d)
cm = pd.concat(cm, ignore_index=True)
cm.columns = [str(c) for c in cm.columns]
cm.to_parquet(OUT / 'cmst2014_digitised_traces.parquet', index=False)
files['cmst2014_digitised_traces.parquet'] = 'CMST 2014 Figs 1-2 digitised traces, 01:31:40-01:35:50 (columns as imported)'
for _, r in pd.read_sql("select s.*, d.site_id from segment s join dataset d using(dataset_id) where dataset_id in ('cmst2014_fig1_imos3315','cmst2014_fig2_h01w')", con).iterrows():
    cov_rows.append(dict(station=r.site_id, form='digitised trace (CMST 2014)', block=r.dataset_id + ' ' + r.label,
                         t_start_s=to_s([r.t_start_utc])[0], t_end_s=to_s([r.t_end_utc])[0], sample_rate_hz=r.sample_rate_hz,
                         band=('5-40 Hz' if 'h01w' in r.dataset_id else 'as plotted'), source=r.file_path))

# ------------------------------------------------------------------ OHASISBIO / Royer picks and figure marks
pk = pd.read_sql("select * from pick where dataset_id in ('royer2016_table5_picks','royer2016_figure_marks','kadri2024_table1',"
                 "'cmst2014_fig5_ha01_detections','cmst2014_fig7_ha08s_detections','h08s_airgun_shots','kadri2019_table3')", con)
pk['t_s'] = to_s(pk.t_utc)
pk['utc'] = utc(pk.t_s)
pk.to_parquet(OUT / 'picks_all.parquet', index=False)
files['picks_all.parquet'] = 'All point picks held: Royer Table 5 + figure marks, Kadri tables, CMST detections, H08S airgun shots'

cov = pd.DataFrame(cov_rows)
cov['start_utc'] = utc(cov.t_start_s).strftime('%H:%M:%S.%f').str[:-3]
cov['end_utc'] = utc(cov.t_end_s).strftime('%H:%M:%S.%f').str[:-3]
cov.to_csv(OUT / 'coverage_blocks.csv', index=False)
files['coverage_blocks.csv'] = 'one row per data block (record or figure panel): station, form, UTC start/end, rate, band, source'
json.dump(files, open(OUT / 'MANIFEST.json', 'w'), indent=1)
print(len(cov), {k: (OUT / k).stat().st_size for k in files})
