"""Further reverse methods C2 (unique-transient discord), C3 (analogue-shape correlation with
energy gate) and C4 (change-point onsets, PELT) on 10 Hz dB envelopes, per station.
Specification section 7. Frozen module reverse_detectors v1.0.0 is used for MASS, NCC, PELT and S1.
Input: units.pkl (per station: observed segments, null segments, query masks, templates).
Output: c234_<station>.pkl with per-position statistics and p-values."""
import sys, pickle, math, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '.')
import reverse_detectors as rd, screen_core as SC
FS = 10.0
def ydb(e): return 20 * np.log10(np.maximum(np.asarray(e, float), 1e-30))
def clusters(pos, gap):
    pos = np.sort(pos); 
    return 0 if pos.size == 0 else int(1 + np.sum(np.diff(pos) > gap))
def s1z(env, L):
    r = SC.s1(env, FS, L); return r['t'], r['z']
def gate_at(tq, t1, z1, L):
    # S1 z of the window of length L that starts nearest at/before tq (step L/4)
    k = np.searchsorted(t1, tq, side='right') - 1
    k = np.clip(k, 0, len(z1) - 1); return z1[k]
def c2_unit(u, m_s):
    m = int(m_s * FS); step = int(FS)
    pool = np.concatenate([ydb(s['env']) for s in u['pool']])
    offs = np.cumsum([0] + [len(s['env']) for s in u['pool']])
    rr = 0.5 * math.sqrt(2 * m)
    def query(pi, i):
        g = offs[pi] + i; q = pool[g:g + m]
        if q.size < m or not np.all(np.isfinite(q)) or np.std(q) < 1e-6: return np.nan, -1
        d = rd.mass_distance(q, pool); lo, hi = max(0, g - m), min(d.size, g + m + 1); d[lo:hi] = np.inf
        hits = np.where(d <= rr)[0]
        return float(np.min(d)), clusters(hits, m)
    out = {'obs': [], 'null': []}
    for kind in ('obs', 'null'):
        for pi, i in u['queries_' + kind]:
            nn, rep = query(pi, i)
            out[kind].append((pi, i, nn, rep))
    return out
def tmpl_bank(templates):
    bank = []
    for name, y in templates.items():
        for f in (0.5, 1.0, 2.0):
            n = max(20, int(round(len(y) * f)))
            yy = np.interp(np.linspace(0, len(y) - 1, n), np.arange(len(y)), y)
            bank.append((name, f, yy))
    return bank
def c3_seg(env, bank):
    y = ydb(env); best = np.full(y.size, -np.inf); arg = np.full(y.size, -1)
    for j, (_, _, tp) in enumerate(bank):
        if tp.size >= y.size: continue
        r = rd.template_ncc(y, tp); n = r.size
        b = r > best[:n]; best[:n][b] = r[b]; arg[:n][b] = j
    return best, arg
def c4_seg(env, pen):
    y = ydb(env); y = np.where(np.isfinite(y), y, np.nanmedian(y))
    sig = rd.robust_loc_scale(np.diff(y))[1] / math.sqrt(2)
    cps = rd.pelt_mean(y, pen, sigma=sig)
    b = [0] + list(cps) + [y.size]; means = [np.mean(y[b[k]:b[k + 1]]) for k in range(len(b) - 1)]
    rsd = rd.robust_loc_scale(y)[1]
    cand = []
    for k in range(1, len(means)):
        jump = means[k] - means[k - 1]
        if jump < 2 * rsd: continue
        # a downward change within 2-120 s after
        for k2 in range(k + 1, len(means)):
            dt = (b[k2] - b[k]) / FS
            if dt > 120: break
            if dt >= 2 and means[k2] - means[k2 - 1] < 0:
                cand.append((b[k] / FS, jump / sig)); break
    return cps, cand
def run(args):
    st, u = args
    res = {'station': st}
    for m_s in (10.0, 30.0):
        res[('C2', m_s)] = c2_unit(u, m_s)
    bank = tmpl_bank(u['templates'])
    res['bank'] = [(n, f, len(t)) for n, f, t in bank]
    res['C3_obs'] = [c3_seg(s['env'], bank) for s in u['obs']]
    res['C3_null'] = [c3_seg(s['env'], bank) for s in u['null']]
    res['S1_obs'] = {L: [s1z(s['env'], L) for s in u['obs']] for L in (10.0, 30.0)}
    res['S1_null'] = {L: [s1z(s['env'], L) for s in u['null']] for L in (10.0, 30.0)}
    # PELT penalty: one change point per 600 s on the null (bisection on log penalty)
    nul = u['null'][:40]; dur = sum(len(s['env']) for s in nul) / FS
    lo, hi = 1.0, 2000.0
    for _ in range(14):
        mid = math.sqrt(lo * hi)
        n = sum(len(c4_seg(s['env'], mid)[0]) for s in nul)
        if n / dur * 600 > 1.0: lo = mid
        else: hi = mid
    pen = math.sqrt(lo * hi); res['pelt_penalty'] = pen
    res['C4_obs'] = [c4_seg(s['env'], pen)[1] for s in u['obs']]
    res['C4_null'] = [c4_seg(s['env'], pen)[1] for s in u['null']]
    res['null_dur_s'] = sum(len(s['env']) for s in u['null']) / FS
    pickle.dump(res, open(f'assoc/c234_{st}.pkl', 'wb'))
    return st, pen
if __name__ == '__main__':
    units = pickle.load(open('assoc/units.pkl', 'rb'))
    with Pool(min(len(units), 8)) as p:
        for r in p.imap_unordered(run, list(units.items())): print(r, flush=True)
