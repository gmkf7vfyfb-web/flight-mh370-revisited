"""Injection-recovery into real IMS background (H01W, H08S; March..all-year 2014-2025 open data).
Each case: random event-free position in a random record; same synthetic waveform scaled to each SNR.
SNR = max 30 s band energy (5-40 Hz) of the injected signal / noise band energy in 30 s (local noise PSD).
"""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, '.')
import sigdet as SD
from score_records import load
RD='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records'
RB='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'
HOST=os.environ.get('SIG_HOST','eq')
from obspy import UTCDateTime
from multiprocessing import Pool

CLASSES = ['dive', 'ditch', 'quake', 'implosion', 'airgun', 'ship', 'ice', 'zcall', 'fin', 'realquake']
SNRS = np.arange(-20.0, 30.01, 2.5)
NPER = int(os.environ.get('SIG_NPER', 80))
SEG = 720.0          # s, noise segment for the noise spectrum
CORE = 360.0         # s, scored core
WT = SD.whale_templates()


def events():
    ev = {}
    for st in ('H01W', 'H08S'):
        d = pd.read_csv(f'bc/out/eq_{st}_events.csv'); d = d[d.status == 'ok']
        for _, r in d.iterrows():
            ev[f'{st}1_{r.evid}'] = dict(st=st, t_pred=UTCDateTime(r.t_pred), t_pk=UTCDateTime(r.t_pk) if isinstance(r.t_pk, str) else None, snr=r.snr_db)
    return ev


EV = events()


def scores_core(xseg, N, sl):
    t, P = SD.spec(xseg)
    Y = P[SD.FB][:, sl] / N[SD.FB][:, sl]
    Nf = np.median(N[SD.FB], axis=1)
    banks = SD.bank_spectral(Nf); envs = SD.bank_envelopes()
    out = {}
    for mode, shape in (('L', False), ('S', True)):
        S = SD.d1_scores(Y, banks, envs, SD.PAIRS, shape=shape)
        S['whale'] = SD.d1_whale(Y, WT, shape=shape)
        S['d0'] = SD.d0_band_energy(P[:, sl], N[:, sl])
        out[mode] = SD.combine(S)
    return t[sl], out


def real_signal(st, rng):
    """A strong real T-phase from the same station, as a 240 s waveform with energy starting near 60 s."""
    keys = [k for k, v in EV.items() if v['st'] == st and v['snr'] > 30 and v['t_pk'] is not None]
    k = keys[rng.integers(len(keys))]
    t0, x = load(f'{RD}/{k}.mseed', st)
    i = int((EV[k]['t_pk'] - t0 - 60.0) * SD.FS)        # peak at 60 s; onset is before the peak
    s = x[max(i, 0): max(i, 0) + int(240 * SD.FS)].copy()
    if len(s) < int(240 * SD.FS):
        return None, k
    # remove the pre-event noise level: taper edges
    w = np.ones(len(s)); m = int(5 * SD.FS); w[:m] = np.hanning(2 * m)[:m]; w[-m:] = np.hanning(2 * m)[m:]
    return s * w, k


def case(args):
    st, cls, seed = args
    rng = np.random.default_rng(seed)
    if HOST == 'eq':
        recs = [k for k, v in EV.items() if v['st'] == st]
    else:
        recs = sorted(os.path.basename(p)[:-6] for p in glob.glob(f'{RB}/{st}1_rnd*.mseed'))
    for _ in range(50):
        k = recs[rng.integers(len(recs))]
        t0, x = load(f'{RD if HOST == "eq" else RB}/{k}.mseed', st)
        n = len(x); T = n / SD.FS
        tev = (EV[k]['t_pred'] - t0) if HOST == 'eq' else -1e9
        tc = rng.uniform(SEG / 2 + 5, T - SEG / 2 - 5)
        if abs(tc + 60 - tev) < 420:       # keep the catalogued arrival out of the scored core
            continue
        i0 = int((tc - SEG / 2) * SD.FS); seg = x[i0: i0 + int(SEG * SD.FS)]
        if (seg == 0).mean() > 0.001:
            continue
        break
    else:
        return []
    t, P = SD.spec(seg)
    N = SD.noise_psd(P)
    sl = (t >= (SEG - CORE) / 2) & (t <= (SEG + CORE) / 2)
    jc = np.argmin(abs(t - SEG / 2))
    nb = (N[SD.FB0, jc] * (SD.F[1] - SD.F[0])).sum()           # noise mean-square in 5-40 Hz, Pa^2
    if cls == 'realquake':
        s, src = real_signal(st, rng)
        if s is None:
            return []
        tsig0 = 60.0 - 30.0       # onset taken ~30 s before the peak (look window covers it)
    else:
        s, tsig0 = SD.synth(cls, rng); src = ''
    # place signal so that its start (t0 inside synthetic) is at segment centre
    j0 = int((SEG / 2 - tsig0) * SD.FS)
    full = np.zeros_like(seg); L = min(len(s), len(seg) - j0); full[j0: j0 + L] = s[:L]
    out = []
    for snr in SNRS:
        y = seg + SD.band_snr_scale(full, nb, snr)
        tt, R = scores_core(y, N, sl)
        look = (tt >= SEG / 2 - 40) & (tt <= SEG / 2 + 80)
        rec = dict(st=st, cls=cls, seed=seed, rec=k, src=src, tc=tc, snr=snr)
        for mode in ('L', 'S'):
            C = R[mode]
            for stat in ('d0', 'd1', 'd2', 'dive', 'ditch', 'c_quake', 'c_whale', 'c_airgun', 'c_ship', 'c_ice'):
                if mode == 'S' and stat == 'd0':
                    continue
                rec[f'{mode}_{stat}'] = float(np.max(C[stat][look]))
            j = np.argmax(np.where(look, C['d1'], -np.inf))
            rec[f'{mode}_win'] = int(C['winner'][j])
        out.append(rec)
    return out


if __name__ == '__main__':
    jobs = [(st, c, 100000 * si + 1000 * ci + k) for si, st in enumerate(('H01W', 'H08S'))
            for ci, c in enumerate(CLASSES) for k in range(NPER)]
    if len(sys.argv) > 1:
        jobs = jobs[::int(sys.argv[1])]
    with Pool(16) as p:
        res = p.map(case, jobs, chunksize=2)
    df = pd.DataFrame([r for rr in res for r in rr])
    df.to_csv(f'injections_{HOST}.csv', index=False)
    print(df.shape, df.groupby(['st', 'cls']).size().unstack(0))
