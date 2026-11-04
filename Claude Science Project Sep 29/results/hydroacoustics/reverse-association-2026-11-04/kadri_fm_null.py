"""Form-matched null for the Kadri envelopes (task item 5d).
Stationary block bootstrap (Politis & Romano 1994) of the 8 March record:
Cape Leeuwin from the off-window part of panel a (before arrival window - 60 s);
Diego Garcia South from each panel itself (no off-window part exists).
Pseudo-panels of 600 s; envelope statistics exactly as the screening (screen_core.envelope_stats, lag 1).
usage: kadri_fm_null.py OUT.pkl MEANBLOCK_S NPANELS"""
import sys, pickle, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, '.')
import reverse_detectors as rd, screen_core as SC
FS = 10.0
LAG = {'H01W': 1, 'H08S': 7}  # S2 thinning lags used by the screening run (reproduced)
def d1_flag(filled):
    out = np.zeros_like(filled); n = len(filled); i = 0
    while i < n:
        if filled[i]:
            j = i
            while j < n and filled[j]: j += 1
            if j - i >= 3: out[i:j] = True
            i = j
        else: i += 1
    return out
def panels():
    kv = pd.read_parquet('pkg/station-data/kadri2024_fig9_vertices.parquet'); P = {}
    for p, d in kv.groupby('panel'):
        t0 = np.floor(d.t_s.min()); t1 = np.ceil(d.t_s.max())
        tg, env, filled = rd.vertices_to_envelope(d.t_s.values, d.pressure_pa.values, FS, t0, t1)
        P[p] = dict(station=d.station.iloc[0], t=tg, env=env, flag=d1_flag(filled))
    return P
def sources(P, cl_off_end=2120.6245 - 60.0):
    S = {}
    a = P['a_h01w']; m = a['t'] < cl_off_end
    S['H01W'] = [(a['env'][m], a['flag'][m])]
    S['H08S'] = [(P[k]['env'], P[k]['flag']) for k in ('d_h08s', 'e_h08s')]
    return S
def boot(src, n, meanblock, rng):
    env, flag = src; N = env.size; out_e = np.empty(n); out_f = np.empty(n, bool); i = 0
    p = 1.0 / meanblock
    while i < n:
        s = rng.integers(N); L = min(rng.geometric(p), n - i)
        idx = (s + np.arange(L)) % N
        out_e[i:i + L] = env[idx]; out_f[i:i + L] = flag[idx]; i += L
    return out_e, out_f
def work(args):
    st, k, seed, meanblock = args
    rng = np.random.default_rng(seed)
    P = panels(); S = sources(P)
    srcs = S[st]; src = srcs[k % len(srcs)]
    e, f = boot(src, 6000, meanblock, rng)
    o = SC.envelope_stats(e, FS, LAG[st], flagged=f)
    return st, k % len(srcs), {key: v['stat'] for key, v in o.items()}
if __name__ == '__main__':
    out, mb, npn = sys.argv[1], float(sys.argv[2]) * FS, int(sys.argv[3])
    jobs = [(st, k, 1000 * i + k + (0 if st == 'H01W' else 7), mb) for i, st in enumerate(['H01W', 'H08S']) for k in range(npn)]
    with Pool(16) as pool:
        res = pool.map(work, jobs, chunksize=4)
    pickle.dump(res, open(out, 'wb'))
    print('done', len(res))
