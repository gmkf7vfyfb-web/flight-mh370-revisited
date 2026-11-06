"""Step 1b: detection probability at the IMOS loggers for physics-based impact families (pre-registration A2, A3, B4)."""
import sys, os, pickle, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
from multiprocessing import Pool
import sigdet as SD, imosdet as ID, network14 as N
from imos_calib import null_records, COMP, WT

import __main__, imos_calib as _IC
__main__.TailMap = _IC.TailMap
cal = pickle.load(open('imos_calib.pkl', 'rb'))
Q = pd.read_csv(os.environ.get('FAMQ', 'source_model_family_quantiles.csv'))
G = pd.read_csv('grid_ext_paths.csv')
SNRS = np.arange(-20.0, 30.01, 2.5); NPER = int(os.environ.get('NPER', 60))
FAMS = ['R1', 'R2', 'R3', 'R3+sub', 'EQ real']
_RS = None


def real_quake(rng, n):
    """A strong recorded T-phase (H01W or H08S, band SNR > 30 dB), 150 s with the peak at 60 s, IMOS gain applied later."""
    global _RS
    if _RS is None:
        import inject as _RS_mod; _RS = _RS_mod
    for _ in range(20):
        s, k = _RS.real_signal(['H01W', 'H08S'][rng.integers(2)], rng)
        if s is not None:
            return s[:int(150 * ID.FS)].astype(float), k
    raise RuntimeError('no real quake')


def fq(fam, par):
    r = Q[(Q.family == fam) & (Q.parameter == par)].iloc[0]; return float(r['q05']), float(r['median']), float(r['q95'])


def draw_fc(fam, rng):
    lo, md, hi = fq(fam, 'fc'); z = rng.standard_normal()
    s = (np.log(md) - np.log(lo)) / 1.645 if z < 0 else (np.log(hi) - np.log(md)) / 1.645
    return float(np.exp(np.log(md) + s * z))


def synth(fam, rng, n, gshape, dist):
    if fam == 'EQ real':
        s, k = real_quake(rng, n); s = s - s.mean(); s *= np.hanning(len(s)) ** 0.25
        t0 = rng.uniform(40, 140); w = np.zeros(n); i0 = int((t0 - 20) * ID.FS); L = min(len(s), n - i0); w[i0:i0 + L] = s[:L]
        f = np.fft.rfftfreq(n, 1 / ID.FS); w = np.fft.irfft(np.fft.rfft(w) * np.sqrt(np.interp(f, ID.F, gshape)), n)
        return w, t0, dict(fc=np.nan, slope=np.nan, f0=np.nan, tilt=np.nan, dist_km=dist, eq_key=k)
    base = fam.split('+')[0]; fc = draw_fc(base, rng); a = rng.uniform(2.65, 3.5)
    f0 = rng.uniform(1, 4); tilt = rng.uniform(-0.5, 0.5)
    t = np.arange(n) / ID.FS; t0 = rng.uniform(40, 180)
    f = np.fft.rfftfreq(n, 1 / ID.FS)
    shape = SD.src_shape(f, fc, a) * SD.channel(f, f0=f0, R_km=dist) * np.maximum(f, 0.1) ** tilt * np.interp(f, ID.F, gshape)
    if fam == 'R3+sub':
        e = np.zeros(n); T = rng.uniform(15, 60)
        for tk in np.sort(rng.uniform(0, T, rng.integers(3, 9))):
            e += rng.lognormal(0, 0.7) ** 2 * SD.env_gamma(t - t0 - tk, rng.uniform(0.5, 3), rng.uniform(3, 12))
        e /= e.max()
    else:
        e = SD.env_gamma(t - t0, rng.uniform(0.3, 2.0), rng.uniform(3, 20))
    w = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * np.sqrt(shape), n) * np.sqrt(e)
    return w, t0, dict(fc=fc, slope=a, f0=f0, tilt=tilt, dist_km=dist)


def scale(w, x, snr):
    from scipy import signal
    b, a_ = signal.butter(4, [8.0, 40.0], btype='band', fs=ID.FS)
    xb = signal.filtfilt(b, a_, x); wb = signal.filtfilt(b, a_, w); m = int(30 * ID.FS)
    ex = np.convolve(xb ** 2, np.ones(m), 'valid')[::m // 4]
    nref = np.median(ex)                       # typical 30 s noise energy in the record (robust to loud unrelated transients)
    e = np.convolve(wb ** 2, np.ones(m), 'valid').max()
    return w * np.sqrt(10 ** (snr / 10) * nref / e), 10 * np.log10(ex.mean() / nref)


def case(args):
    lg, fam, seed = args; rng = np.random.default_rng(seed); c = cal[lg]
    X, _ = null_records(lg); x = X[rng.integers(len(X))].astype(float); x -= x.mean()
    gg = G[(G.station == lg) & (G.path_class != 'blocked')]; dist = float(gg.dist_km.values[rng.integers(len(gg))])
    w, t0, par = synth(fam, rng, len(x), c['gshape'], dist)
    wc = N.WindowCal(lg, cal=c); out = []
    for snr in SNRS:
        ws, offs = scale(w, x, snr); y = x + ws
        g = ID.record_stats(y, WT, c['gshape'], c['mu'], c['sd'], c['tau'], xref=(x if os.environ.get('XREF') == 'oracle' else None))   # review 3a: whiten from the record itself, as on real data
        F = sum(-2 * np.nan_to_num(np.log(c['maps'][k].p(g[k])), nan=0.0) for k in COMP)
        m = (ID.CENT >= t0 - 10) & (ID.CENT <= t0 + 60)
        rec = dict(station=lg, family=fam, seed=seed, snr=snr, mean_over_median_noise_db=offs, **par)
        rec['p_combined'] = wc.p(np.nanmax(F[m]), m.sum())
        for k in COMP:      # single components, point-level then window (Bonferroni over the look) for comparison
            rec['p_' + k] = float(min(1, m.sum() * np.nanmin(c['maps'][k].p(g[k][m]))))
        out.append(rec)
    return out


if __name__ == '__main__':
    jobs = [(lg, fam, 10000 * i + 100 * j + k) for i, lg in enumerate(N.LOGGERS) for j, fam in enumerate(FAMS) for k in range(NPER)]
    with Pool(16) as p:
        R = p.map(case, jobs, chunksize=2)
    D = pd.DataFrame([r for rr in R for r in rr]); D.to_csv(os.environ.get('INJ_OUT', 'imos_injections_physics.csv'), index=False)
    n20 = D[D.snr == -20]
    print('null check at -20 dB, fraction p<0.05 / 0.2:', round((n20.p_combined < 0.05).mean(), 4), round((n20.p_combined < 0.2).mean(), 4))
    for a in (0.2, 0.05):
        def s50(g):
            g = g.groupby('snr').p_combined.apply(lambda v: (v < a).mean()); x = g.index.values; y = g.values; i = np.where(y >= 0.5)[0]
            if len(i) == 0: return np.nan
            i = i[0]; return x[0] if i == 0 else x[i - 1] + (0.5 - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])
        print(f'SNR (8-40 Hz) for 50% detection, known time, p<{a}:'); print(D.groupby(['station', 'family']).apply(s50).unstack().round(1).to_string())
