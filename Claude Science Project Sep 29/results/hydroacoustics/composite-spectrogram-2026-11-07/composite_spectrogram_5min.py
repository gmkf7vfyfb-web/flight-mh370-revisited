"""Composite 5-minute spectrogram: six sources in real IMOS seabed-logger noise (Perth Canyon logger 3376).

One event per minute:
  0-1 min  two whale calls (synthetic): Antarctic blue whale Z-call and pygmy blue whale song unit II
  1-2 min  real earthquake T-phase (Cape Leeuwin IMS H01W1 record), IMOS gain shape applied
  2-3 min  iceberg harmonic tremor (synthetic, variable harmonic tremor)
  3-4 min  steep-dive impact, family R1 (imos_inject.synth method, median corner frequency)
  4-5 min  ditching-like impact, family R3 (same method, median corner frequency)

SNR definition = imos_inject.scale: peak 30 s signal energy over the median 30 s noise energy of the record,
8-40 Hz (4th-order Butterworth, zero phase).  Whale levels are set as received sound pressure levels
(dB re 1 uPa) from published source levels and a stated range; the resulting SNR is reported.

Run from the detector code directory (sigdet.py, imosdet.py, score_records.py, ns/ns_readers.py):
    CODE_DIR=<dir> OUT_DIR=<dir> python composite_spectrogram_5min.py
"""
import os, sys, json
import numpy as np, pandas as pd
from scipy import signal

CODE = os.environ.get('CODE_DIR', os.getcwd()); OUT = os.environ.get('OUT_DIR', os.getcwd())
sys.path.insert(0, CODE); sys.path.insert(0, os.path.join(CODE, 'ns'))
import sigdet as SD, imosdet as ID, ns_readers as RD
from score_records import load

FS = 250.0
CACHE = '/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos_250hz_cache'
EQDIR = '/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records'
LOGGER, NOISE_FILE, NOISE_IDX = 'IMOS3376', 'imos3376_background.npz', 244
EQ_FILE, EQ_ST, EQ_PEAK_S = 'H01W1_us20009xz4.mseed', 'H01W', 1203.0     # peak = centre of max 30 s 5-40 Hz window
SEED = 20261107

# ------------------------------------------------------------------ noise and calibration
z = np.load(f'{CACHE}/{NOISE_FILE}', allow_pickle=True)
x = z['x'][NOISE_IDX].astype(float); x -= x.mean(); n = len(x)
noise_label = str(z['label'][NOISE_IDX]); noise_t0 = float(z['t_start_s'][NOISE_IDX])
noise_utc = (pd.Timestamp('2014-03-08') + pd.to_timedelta(noise_t0, unit='s')).strftime('%Y-%m-%d %H:%M:%S')
fg, Gdb = RD.imos_gain(LOGGER); SENS = RD.IMOS_CAL[LOGGER]['sens_db']
gshape = ID.gain_shape(fg, Gdb)
f_n = np.fft.rfftfreq(n, 1 / FS)
H_V_per_uPa = np.sqrt(10 ** ((np.interp(f_n, fg, Gdb) + SENS) / 10))      # amplitude response, V per uPa

def to_volts(p_uPa):
    return np.fft.irfft(np.fft.rfft(p_uPa) * H_V_per_uPa, n)

def to_uPa(v):
    return np.fft.irfft(np.fft.rfft(v) / np.maximum(H_V_per_uPa, 1e-30), n)

BB = signal.butter(4, [8.0, 40.0], btype='band', fs=FS)

def scale(w, xn, snr):
    """imos_inject.scale, same logic."""
    xb = signal.filtfilt(*BB, xn); wb = signal.filtfilt(*BB, w); m = int(30 * FS)
    ex = np.convolve(xb ** 2, np.ones(m), 'valid')[::m // 4]
    nref = np.median(ex); e = np.convolve(wb ** 2, np.ones(m), 'valid').max()
    return w * np.sqrt(10 ** (snr / 10) * nref / e)

def snr_of(w, xn):
    xb = signal.filtfilt(*BB, xn); wb = signal.filtfilt(*BB, w); m = int(30 * FS)
    nref = np.median(np.convolve(xb ** 2, np.ones(m), 'valid')[::m // 4])
    return 10 * np.log10(np.convolve(wb ** 2, np.ones(m), 'valid').max() / nref)

def band_spl_30s(v, lo=8.0, hi=40.0, peak=True):
    """Calibrated 30 s mean-square level in a band, dB re 1 uPa (peak window, or median window for noise)."""
    p = to_uPa(v); b = signal.butter(4, [lo, hi], btype='band', fs=FS); pb = signal.filtfilt(*b, p); m = int(30 * FS)
    e = np.convolve(pb ** 2, np.ones(m), 'valid') / m
    return 10 * np.log10(e.max() if peak else np.median(e[::m // 4]))

t = np.arange(n) / FS

def taper(tt, T, r):
    """Cosine on/off ramps of r s for a unit of duration T (tt = time from unit start)."""
    w = ((tt >= 0) & (tt <= T)).astype(float)
    a = (tt >= 0) & (tt < r); w[a] = 0.5 * (1 - np.cos(np.pi * tt[a] / r))
    b = (tt > T - r) & (tt <= T); w[b] = 0.5 * (1 - np.cos(np.pi * (T - tt[b]) / r))
    return w

def tl_db(R_km):
    """Orientation only: spherical spreading to 1 km, cylindrical beyond (absorption < 0.1 dB at 20 Hz)."""
    return 60.0 + 10 * np.log10(R_km)

rng = np.random.default_rng(SEED)
EV = []

# ------------------------------------------------------------------ 0-1 min: whale calls (pressure, uPa)
# Antarctic blue whale Z-call (Gavrilov et al. 2012; Leroy et al. 2016; Sirovic et al. 2007 source level)
Z = dict(start=4.0, fA=26.05, TA=9.0, Tsw=1.5, fB0=18.8, fB1=18.3, TB=9.0, SL=189.0, R_km=1000.0)
tt = t - Z['start']; T = Z['TA'] + Z['Tsw'] + Z['TB']; on = (tt >= 0) & (tt <= T)
fi = np.where(tt < Z['TA'], Z['fA'], np.where(tt < Z['TA'] + Z['Tsw'], Z['fA'] + (Z['fB0'] - Z['fA']) * (tt - Z['TA']) / Z['Tsw'],
              Z['fB0'] + (Z['fB1'] - Z['fB0']) * (tt - Z['TA'] - Z['Tsw']) / Z['TB']))
zc = np.sin(2 * np.pi * np.cumsum(np.where(on, fi, 0)) / FS) * taper(tt, T, 0.5)
RLz = Z['SL'] - tl_db(Z['R_km'])                 # rms over the call
zc *= np.sqrt(10 ** (RLz / 10) / np.mean(zc[on] ** 2))
EV.append(dict(key='zcall', label='Antarctic blue whale Z-call', start_s=Z['start'], dur_s=T, w=to_volts(zc),
               freq='26.05 Hz for 9 s, 1.5 s down-sweep, then 18.8 to 18.3 Hz for 9 s; no harmonics',
               level_rule=f"source level {Z['SL']:.0f} dB re 1 uPa at 1 m, range {Z['R_km']:.0f} km, TL = 60 + 10 log10(R/1 km) dB",
               rl_call=RLz,
               src='Gavrilov, McCauley & Gedamke 2012 JASA 131:4476 (call shape; 0.135 Hz/yr decline); Leroy et al. 2016 PLoS ONE 11:e0163587 (unit A 26.05 Hz for 2014; units 7-12 s); Sirovic et al. 2007 JASA 122:1208 (source level 189 dB)'))

# Pygmy blue whale (south-east Indian Ocean population) song unit II: frequency-modulated up-sweep with harmonics
P = dict(start=31.0, f0=19.5, f1=25.5, T=23.0, harm=(1.0, 0.7, 0.5), SL=179.0, R_km=100.0)
tt = t - P['start']; on = (tt >= 0) & (tt <= P['T'])
f1t = P['f0'] + (P['f1'] - P['f0']) * np.clip(tt, 0, P['T']) / P['T']
ph = 2 * np.pi * np.cumsum(np.where(on, f1t, 0)) / FS
pb = sum(a * np.sin(k * ph) for k, a in enumerate(P['harm'], 1)) * taper(tt, P['T'], 1.0)
RLp = P['SL'] - tl_db(P['R_km'])
pb *= np.sqrt(10 ** (RLp / 10) / np.mean(pb[on] ** 2))
EV.append(dict(key='pygmy', label='Pygmy blue whale song unit II', start_s=P['start'], dur_s=P['T'], w=to_volts(pb),
               freq='fundamental up-sweep 19.5 to 25.5 Hz over 23 s; harmonics 2 and 3 at -3 and -6 dB (to 76.5 Hz)',
               level_rule=f"source level {P['SL']:.0f} dB re 1 uPa at 1 m, range {P['R_km']:.0f} km, TL = 60 + 10 log10(R/1 km) dB",
               rl_call=RLp,
               src='Jolliffe et al. 2019 PLoS ONE 14:e0208619 (unit II 20 to 26 Hz over 23 s in 2010, harmonics to 72 Hz); Gavrilov et al. 2011 JASA 130:3651 (0.12 Hz/yr decline, so 2014 values 0.5 Hz lower); McCauley et al. 2001 Mar. Mamm. Sci. 17:235 (source level 179 dB)'))

# ------------------------------------------------------------------ 1-2 min: real earthquake T-phase (imos_inject.synth 'EQ real')
EQ_SNR, EQ_PEAK_CHART = 10.0, 90.0
t0e, xe = load(f'{EQDIR}/{EQ_FILE}', EQ_ST)
i = int((EQ_PEAK_S - 60.0) * FS); s = xe[i:i + int(240 * FS)].copy()                # inject.real_signal: peak at 60 s
wt = np.ones(len(s)); m5 = int(5 * FS); wt[:m5] = np.hanning(2 * m5)[:m5]; wt[-m5:] = np.hanning(2 * m5)[m5:]; s *= wt
s = s[:int(150 * FS)]; s = s - s.mean(); s *= np.hanning(len(s)) ** 0.25          # imos_inject.real_quake / synth
w = np.zeros(n); j0 = int((EQ_PEAK_CHART - 60.0) * FS); L = min(len(s), n - j0); w[j0:j0 + L] = s[:L]
w_eq = np.fft.irfft(np.fft.rfft(w) * np.sqrt(np.interp(f_n, ID.F, gshape)), n)
w_eq = scale(w_eq, x, EQ_SNR)
EV.append(dict(key='eq', label='Earthquake T-phase (recorded)', start_s=EQ_PEAK_CHART - 60.0, dur_s=150.0, w=w_eq,
               freq='broadband; recorded at Cape Leeuwin IMS H01W1 (flat 1-100 Hz), IMOS gain shape then applied',
               level_rule=f'scaled to SNR {EQ_SNR:+.0f} dB; 150 s segment with the peak at chart {EQ_PEAK_CHART:.0f} s; Hann^0.25 taper',
               rl_call=np.nan,
               src='USGS event us20009xz4: 2017-07-19 12:16:23.56 UTC, Mww 6.0, Mauritius-Reunion region, 17.415 S 66.484 E, depth 10 km; epicentre to H01W 5,087 km; record IM.H01W1..EDH (EarthScope FDSN); band SNR at H01W 43.2 dB (30 s, 5-40 Hz)'))

# ------------------------------------------------------------------ 2-3 min: iceberg harmonic tremor (variable harmonic tremor)
I = dict(start=125.0, T=50.0, f0=7.0, wander=0.03, Twander=40.0, nh=7, R_km=3800.0, chan_f0=2.5)
ICE_SNR = 6.0
tt = t - I['start']; on = (tt >= 0) & (tt <= I['T'])
f0t = I['f0'] * (1 + I['wander'] * np.sin(2 * np.pi * np.clip(tt, 0, None) / I['Twander']))
ph = 2 * np.pi * np.cumsum(np.where(on, f0t, 0)) / FS
ice = sum(np.sin(k * ph + rng.uniform(0, 2 * np.pi)) / np.sqrt(k) for k in range(1, I['nh'] + 1)) * taper(tt, I['T'], 5.0)
ice = np.fft.irfft(np.fft.rfft(ice) * np.sqrt(SD.channel(f_n, f0=I['chan_f0'], R_km=I['R_km'])), n)
EV.append(dict(key='ice', label='Iceberg harmonic tremor', start_s=I['start'], dur_s=I['T'], w=scale(to_volts(ice), x, ICE_SNR),
               freq='fundamental 7.0 Hz with +-3 % slow wander (40 s period); 7 harmonics to 49 Hz, amplitude k^-0.5; 50 s excerpt with 5 s ramps',
               level_rule=f'scaled to SNR {ICE_SNR:+.0f} dB; deep-channel transfer sigdet.channel (f0 2.5 Hz, R 3,800 km)',
               rl_call=np.nan,
               src='Chapp et al. 2005 G-cubed 6:Q06003 (Indian Ocean sound-channel variable harmonic tremor: fundamental 4-10 Hz, up to 10 harmonic bands); Talandier et al. 2002 EPSL 203:519; MacAyeal et al. 2008 JGR 113:F03011'))

# ------------------------------------------------------------------ 3-5 min: impacts (imos_inject.synth, fixed parameters)
Q = pd.read_csv(os.path.join(CODE, 'source_model_family_quantiles.csv'))
def qmed(fam, par): return float(Q[(Q.family == fam) & (Q.parameter == par)]['median'].iloc[0])
G = pd.read_csv(os.path.join(CODE, 'grid_ext_paths_wide.csv'))
DIST = float(G[(G.station == LOGGER) & (G.path_class != 'blocked')].dist_km.median())
IMP = dict(slope=3.08, f0=2.5, tilt=0.0, rise=1.15, decay=11.5, dist_km=DIST)   # synth draws slope U(2.65,3.5), f0 U(1,4), tilt U(-0.5,0.5), rise U(0.3,2), decay U(3,20): mid-range values used
def impact(fam, t0, seed):
    r = np.random.default_rng(seed); fc = qmed(fam, 'fc')
    shape = SD.src_shape(f_n, fc, IMP['slope']) * SD.channel(f_n, f0=IMP['f0'], R_km=IMP['dist_km']) * np.maximum(f_n, 0.1) ** IMP['tilt'] * np.interp(f_n, ID.F, gshape)
    e = SD.env_gamma(t - t0, IMP['rise'], IMP['decay'])
    return np.fft.irfft(np.fft.rfft(r.standard_normal(n)) * np.sqrt(shape), n) * np.sqrt(e), fc
for fam, key, lab, t0i, sd in (('R1', 'r1', 'Steep-dive impact (R1)', 190.0, SEED + 1), ('R3', 'r3', 'Ditching-like impact (R3)', 250.0, SEED + 2)):
    wi, fc = impact(fam, t0i, sd)
    EV.append(dict(key=key, label=lab, start_s=t0i, dur_s=np.nan, w=scale(wi, x, 0.0),
                   freq=f'flat to corner {fc:.3f} Hz then f^-{IMP["slope"]}; deep-channel transfer (f0 {IMP["f0"]} Hz, Thorp absorption over {DIST:.0f} km); IMOS gain shape',
                   level_rule=f'scaled to SNR 0 dB; envelope env_gamma rise {IMP["rise"]} s, decay {IMP["decay"]} s (power e-fold); spectral tilt {IMP["tilt"]}',
                   rl_call=np.nan, fc_hz=fc, KE_J=qmed(fam, 'KE'), tau_s=qmed(fam, 'tau'),
                   src=f'source_model_family_quantiles.csv family {fam}: median fc {fc:.4f} Hz, median KE {qmed(fam, "KE") / 1e9:.3g} GJ, median tau {qmed(fam, "tau"):.4f} s, median slope n {qmed(fam, "n"):.3f}; method imos_inject.synth with sigdet.src_shape and sigdet.channel'))

# ------------------------------------------------------------------ assemble, measure
y = x + sum(e['w'] for e in EV)
NL = band_spl_30s(x, peak=False)
rows = []
for e in EV:
    rows.append(dict(event=e['label'], chart_start_s=round(e['start_s'], 2),
                     duration_s=(round(e['dur_s'], 1) if np.isfinite(e['dur_s']) else 'onset envelope; power decay e-fold 11.5 s'),
                     snr_db_8_40Hz_30s=round(snr_of(e['w'], x), 2) + 0.0,
                     received_spl_peak30s_8_40Hz_dB_re_1uPa=round(band_spl_30s(e['w']), 1),
                     received_rms_over_call_dB_re_1uPa=(round(e['rl_call'], 1) if np.isfinite(e['rl_call']) else ''),
                     frequency_content=e['freq'], level_setting=e['level_rule'],
                     corner_frequency_hz=(round(e['fc_hz'], 4) if 'fc_hz' in e else ''),
                     kinetic_energy_GJ=(round(e['KE_J'] / 1e9, 3) if 'KE_J' in e else ''),
                     parameter_source=e['src']))
noise_row = dict(event=f'Noise: {LOGGER} Perth Canyon, record {noise_label}, {noise_utc} UTC', chart_start_s=0.0, duration_s=round(n / FS, 1),
                 snr_db_8_40Hz_30s='', received_spl_peak30s_8_40Hz_dB_re_1uPa=f'{NL:.1f} (median 30 s window)', received_rms_over_call_dB_re_1uPa='',
                 frequency_content='real noise; 250 samples/s; 8 Hz hardware high-pass', level_setting='as recorded; calibrated with the logger gain table and sensitivity',
                 corner_frequency_hz='', kinetic_energy_GJ='', parameter_source=f'imos_250hz_cache/{NOISE_FILE} index {NOISE_IDX}; sensitivity {SENS} dB re 1 V/uPa')
T = pd.concat([pd.DataFrame([noise_row]), pd.DataFrame(rows)], ignore_index=True)
T.to_csv(os.path.join(OUT, 'composite_spectrogram_5min_events.csv'), index=False)

# spectrogram and 1 s band power, normalised by the noise-only record median (shift against the composite's own median reported)
fS, tS, PS = signal.spectrogram(y, fs=FS, nperseg=512, noverlap=384)
_, _, PX = signal.spectrogram(x, fs=FS, nperseg=512, noverlap=384)
mS = (fS >= 2) & (fS <= 100)
medX = np.median(PX[mS], axis=1, keepdims=True); medY = np.median(PS[mS], axis=1, keepdims=True)
Pd = 10 * np.log10(PS[mS] / medX)
SOS = signal.butter(4, [8, 60], btype='band', fs=FS, output='sos')
def p1s(v):
    b = signal.sosfiltfilt(SOS, v); k = int(FS); return (b[:len(b) // k * k].reshape(-1, k) ** 2).mean(1)
ey, ex = p1s(y), p1s(x); tb = 0.5 + np.arange(len(ey)); Eb = 10 * np.log10(ey / np.median(ex))
np.savez_compressed(os.path.join(OUT, 'composite_spectrogram_5min_data.npz'), f=fS[mS], t=tS, Pd=Pd, tb=tb, Eb=Eb, Ex=10 * np.log10(ex / np.median(ex)))
META = dict(noise_logger=LOGGER, noise_record=noise_label, noise_utc=noise_utc, noise_spl_8_40=NL, dist_km=DIST, imp=IMP, seed=SEED,
            median_shift_db_max=float(np.max(np.abs(10 * np.log10(medY / medX)))),
            noise_1s_p99_db=float(np.percentile(10 * np.log10(ex / np.median(ex)), 99)),
            fc_times_tau={fam: qmed(fam, 'fc') * qmed(fam, 'tau') for fam in ('R1', 'R2', 'R3')},
            inband_vs_F35A_db={fam: qmed(fam, 'inband_dB_vs_F35A') for fam in ('R1', 'R3')},
            gain_db_at={str(fq): float(10 * np.log10(np.interp(fq, ID.F, gshape))) for fq in (5, 7, 8, 10, 20, 40, 60)},
            events=[{k: v for k, v in e.items() if k != 'w'} for e in EV])
json.dump(META, open(os.path.join(OUT, 'composite_spectrogram_5min_meta.json'), 'w'), indent=1, default=float)


# ------------------------------------------------------------------ figures
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
SNR = {e['key']: round(snr_of(e['w'], x), 1) + 0.0 for e in EV}
SLOTS = [(0, 'Whale calls', f"Z-call {SNR['zcall']:+.1f} dB, pygmy {SNR['pygmy']:+.1f} dB"),
         (60, 'Earthquake T-phase', f"recorded, scaled to {SNR['eq']:+.0f} dB"),
         (120, 'Iceberg tremor', f"{SNR['ice']:+.0f} dB"),
         (180, 'Steep-dive impact', f"{abs(SNR['r1']):.0f} dB"),
         (240, 'Ditching-like impact', f"{abs(SNR['r3']):.0f} dB")]
SLOTS_JON = [(0, 'Whale calls', ''), (60, 'Earthquake', ''), (120, 'Iceberg tremor', ''), (180, 'Steep-dive\nimpact', ''), (240, 'Ditching-like\nimpact', '')]

STE = ("This chart shows six sounds added to real ocean noise from one seabed recorder (Perth Canyon logger 3376). "
       "Only the earthquake is a real recording. The other sounds are made from published values. "
       "The two aircraft impacts have the same loudness relative to the noise, and they look almost the same.")
TECH = (f"Noise: logger {LOGGER[4:]} (Perth Canyon), record {noise_label}, {noise_utc} UTC, 306.8 s at 250 samples/s, 8 Hz hardware high-pass; "
        f"the quietest of 1,342 background records 1-15 March 2014 (largest 1 s, 8-60 Hz power 1.6 dB over the record median); 8-40 Hz noise level {NL:.1f} dB re 1 µPa. "
        "Signal-to-noise ratio (SNR) as in the project injection test: peak 30 s signal energy over the median 30 s noise energy, 8-40 Hz. "
        f"Antarctic blue whale Z-call: 26.05 Hz for 9 s, 1.5 s down-sweep, 18.8 to 18.3 Hz for 9 s (Gavrilov et al. 2012; Leroy et al. 2016); source level 189 dB re 1 µPa at 1 m (Širović et al. 2007) at 1,000 km gives 99 dB re 1 µPa, SNR {SNR['zcall']:+.1f} dB. "
        f"Pygmy blue whale song unit II: up-sweep 19.5 to 25.5 Hz over 23 s with two harmonics (Jolliffe et al. 2019; Gavrilov et al. 2011); source level 179 dB re 1 µPa at 1 m (McCauley et al. 2001) at 100 km gives 99 dB re 1 µPa, SNR {SNR['pygmy']:+.1f} dB. Spreading loss for the whales: spherical to 1 km, then cylindrical (orientation only). "
        "Earthquake: USGS us20009xz4, 19 July 2017, Mww 6.0, Mauritius-Réunion region, 5,087 km from Cape Leeuwin; Cape Leeuwin IMS record (43 dB SNR there) scaled down to +10 dB, with the logger response applied. "
        "Iceberg tremor: fundamental 7 Hz with ±3 % wander, 7 harmonics, 50 s excerpt of a longer episode (Chapp et al. 2005; Talandier et al. 2002), +6 dB. "
        f"Impacts: project source model, steep dive (family R1, median kinetic energy {qmed('R1','KE')/1e9:.1f} GJ, corner {qmed('R1','fc'):.2f} Hz) and ditching-like (family R3, median {qmed('R3','KE')/1e9:.2f} GJ, corner {qmed('R3','fc'):.2f} Hz); "
        f"spectrum falls as f^-3.08 above the corner; deep sound-channel path of {DIST:,.0f} km (median clear path from the 7th arc to this logger); rise 1.15 s, decay 11.5 s; both at 0 dB SNR. "
        "At a fixed SNR the energy sets only the scale. The corner frequency depends on the source duration (corner × duration ≈ 0.19), not on energy. Both corners are far below 8 Hz, so the two families have the same 8-40 Hz shape. "
        f"At the family median energies the ditching-like impact is {qmed('R1','inband_dB_vs_F35A')-qmed('R3','inband_dB_vs_F35A'):.0f} dB weaker in band than the steep dive, so a 0 dB ditching needs a much shorter range or a larger energy. "
        f"Spectrogram: 2.05 s Hann segments, 75 % overlap, dB over the median of the noise record at each frequency (the median of the composite itself differs by up to {META['median_shift_db_max']:.1f} dB, because the events fill much of the 5 min). "
        "Lower panel: 8-60 Hz power in 1 s steps over the noise median; grey line: the noise alone. "
        "Short faint tonal sounds near 66 Hz (about 1:15 and 4:20) and 23 Hz (about 4:35) are in the real noise record; their source is not identified (possibly distant whale calls).")

def draw(fname, jon=False):
    if jon:
        W = 127 / 25.4; fig = plt.figure(figsize=(W, 3.35))
        gsp = GridSpec(3, 2, figure=fig, height_ratios=[0.20, 1.0, 0.42], width_ratios=[1, 0.022], hspace=0.10, wspace=0.03,
                       left=0.105, right=0.90, top=0.985, bottom=0.12)
        cmap = 'Greys'; fs = (7, 6.5, 6); slots = SLOTS_JON
    else:
        fig = plt.figure(figsize=(11, 9.4))
        gsp = GridSpec(4, 2, figure=fig, height_ratios=[0.16, 1.0, 0.40, 0.66], width_ratios=[1, 0.015], hspace=0.10, wspace=0.02,
                       left=0.07, right=0.93, top=0.93, bottom=0.02)
        cmap = 'magma'; fs = (9, 8, 7); slots = SLOTS
    axL = fig.add_subplot(gsp[0, 0]); axS = fig.add_subplot(gsp[1, 0], sharex=axL); axP = fig.add_subplot(gsp[2, 0], sharex=axL); cax = fig.add_subplot(gsp[1, 1])
    im = axS.pcolormesh(tS, fS[mS], Pd, vmin=-3, vmax=15, cmap=cmap, shading='auto', rasterized=True)
    axS.set_ylim(2, 100); axS.set_ylabel('Frequency (Hz)', fontsize=fs[0])
    cb = fig.colorbar(im, cax=cax); cb.set_label('dB over noise median', fontsize=fs[1]); cb.ax.tick_params(labelsize=fs[2])
    if not jon:
        axS.axhline(8, color='w', lw=0.6, ls=':')
        axS.text(2, 9.5, 'Recorder high-pass, 8 Hz', ha='left', va='bottom', fontsize=fs[2], color='w')
    axP.plot(tb, META_EX, color='0.70', lw=0.8, label='Noise alone')
    axP.plot(tb, Eb, color=('k' if jon else '#15803d'), lw=0.9, label='Noise and added sounds')
    axP.set_ylabel('8-60 Hz power,\n1 s (dB)', fontsize=fs[0]); axP.set_xlabel('Time (min:s)', fontsize=fs[0])
    lg = axP.legend(loc='upper right', fontsize=fs[2] if jon else fs[1], frameon=True, ncol=(1 if jon else 2), handlelength=1.5, framealpha=1.0, borderaxespad=0.3)
    lg.get_frame().set_edgecolor('none'); lg.set_zorder(5)
    lo, hi = np.floor(min(Eb.min(), META_EX.min())) - 1, np.ceil(Eb.max()) + (6 if jon else 3); axP.set_ylim(lo, hi)
    for a in (axS, axP):
        for b in (60, 120, 180, 240):
            a.axvline(b, color=('0.35' if (jon or a is axP) else 'w'), lw=0.6, ls='--')
        a.tick_params(labelsize=fs[2])
    axL.set_ylim(0, 1); axL.axis('off')
    for t0s, lab, sub in slots:
        axL.text(t0s + 30, 0.62 if sub else 0.45, lab, ha='center', va='center', fontsize=fs[0] if not jon else fs[1], fontweight=('bold' if not jon else 'normal'))
        if sub: axL.text(t0s + 30, 0.15, sub, ha='center', va='center', fontsize=fs[1])
    axS.set_xlim(0, 300); ticks = np.arange(0, 301, 30)
    axP.set_xticks(ticks); axP.set_xticklabels([f'{int(v // 60)}:{int(v % 60):02d}' for v in ticks])
    plt.setp(axS.get_xticklabels(), visible=False); plt.setp(axL.get_xticklabels(), visible=False)
    if not jon:
        fig.suptitle('How six different sounds look in real seabed-recorder noise at Perth Canyon', x=0.07, ha='left', fontsize=fs[0], y=0.975)
        axF = fig.add_subplot(gsp[3, :]); axF.axis('off')
        import textwrap
        txt = '\n'.join(textwrap.wrap(STE, 190)) + '\n\n' + '\n'.join(textwrap.wrap(TECH, 196))
        axF.text(0.0, 0.86, txt, ha='left', va='top', fontsize=fs[2], transform=axF.transAxes, linespacing=1.22)
    fig.savefig(os.path.join(OUT, fname), dpi=300 if jon else 200)
    if jon:
        from PIL import Image                                     # true single-channel greyscale for the journal
        Image.open(os.path.join(OUT, fname)).convert('L').save(os.path.join(OUT, fname), dpi=(300, 300))
        tif = os.path.join(OUT, fname.replace('.png', '_800dpi.tif'))
        fig.savefig(tif, dpi=800); Image.open(tif).convert('L').save(tif, dpi=(800, 800), compression='tiff_lzw')
    return fig

META_EX = 10 * np.log10(ex / np.median(ex))

if __name__ == '__main__':
    print(T[['event', 'chart_start_s', 'snr_db_8_40Hz_30s', 'received_spl_peak30s_8_40Hz_dB_re_1uPa', 'received_rms_over_call_dB_re_1uPa']].to_string())
    print({k: v for k, v in META.items() if k != 'events'})
    try:
        apply_figure_style()
    except NameError:
        pass
    draw('composite_spectrogram_5min.png')
    import matplotlib as mpl; mpl.rcParams['image.cmap'] = 'Greys'
    draw('composite_spectrogram_5min_jon.png', jon=True)
