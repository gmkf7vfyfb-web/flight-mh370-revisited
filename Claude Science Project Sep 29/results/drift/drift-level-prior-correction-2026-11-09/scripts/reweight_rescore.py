#!/usr/bin/env python3
"""Windage reweighting of the wide-windage legs, 10 Nov 2026 (ocean drift module, exterior class).

The wide legs sampled the exterior-class windage c from a truncated log-normal (median 1.2 %, sigma(log) 0.5, truncated 0.3-5 %). The drifting-object
weights of every beaching are multiplied by q(c_p) = g(c_p) / f(c_p), where f is that sampling density and g is a target density (truncated log-normal),
and q is normalised to mean 1 over the 6250 particles of the leg set. The offline rescorer then gives the coefficients of the target windage distribution
(importance sampling; the coefficients are linear in the weights). The windage c of a particle is the same in both ocean models and in every leg of a set
(same seed); it is read from the responses.json of the GLORYS12 leg of the set (GlobCurrent adds a product offset of -0.75 to -0.60 % and floors at 0).

Usage: reweight_rescore.py TARGETS.json CFGDIR OUTDIR PROCS [LEG ...]
  TARGETS.json: list of {"tag","median","sigma","lo","hi"}  (median, lo, hi as fractions of U10; "sigma" is the log-sd; "tag": "identity" = weights unchanged)
  CFGDIR: rescoring configurations <anything>--<leg>.toml (R3 layout); the arrivals and output lines and the bandwidth list are rewritten here.
  OUTDIR/<tag>/<leg>.jsonl.gz : coefficient files with the 'full' part only (half_a and half_b emptied), bandwidth 50 km only.
The reweighted arrival bytes are streamed to the rescorer through a named pipe; nothing is written to the disk apart from OUTDIR.
"""
import os, sys, json, re, glob, gzip, subprocess, time, math
import numpy as np
from multiprocessing import Pool

HOME = os.path.expanduser('~'); C = f'{HOME}/mh370/drift/coef'; RUNS = f'{C}/runs'; BIN = f'{C}/bin-rescore'
TARGETS = json.load(open(sys.argv[1])); CFGDIR = sys.argv[2]; OUTDIR = os.path.expanduser(sys.argv[3]); PROCS = int(sys.argv[4]); LEGS = sys.argv[5:]
SAMP = dict(median=0.012, sigma=0.5, lo=0.003, hi=0.05)           # sampling density of the wide legs
SAMP_H = dict(median=0.024, sigma=0.35, lo=0.008, hi=0.06)         # sampling density of the higher-windage legs (whigh-, whigh2-)
HDR = np.dtype([('magic', 'S4'), ('node', '<u4'), ('lat', '<f8'), ('lon', '<f8'), ('env_seed', '<u8'), ('cls', '<u4'), ('released', '<u4'), ('n', '<u4'), ('model_error', '<f8'), ('left_domain', '<f8')])
REC = np.dtype([('particle', '<u4'), ('w', '<f4'), ('t_days', '<f8'), ('t_leave_days', '<f4'), ('lon', '<f8'), ('lat', '<f8'), ('line', '<i4'), ('s_km', '<f8'), ('segment', '<i4')])
assert HDR.itemsize == 60 and REC.itemsize == 52

def _ncdf(x): return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def tl_pdf(c, p):
    """Density of the target windage prior at c. Log-normal (median, sigma = log-sd) or normal (mean, sd), both truncated to [lo, hi]."""
    out = np.zeros_like(c, float); ok = (c >= p['lo']) & (c <= p['hi'])
    if p.get('dist') == 'normal':
        mu, sd = p['mean'], p['sd']; z = _ncdf((p['hi'] - mu) / sd) - _ncdf((p['lo'] - mu) / sd); u = (c[ok] - mu) / sd
        out[ok] = np.exp(-0.5 * u * u) / math.sqrt(2.0 * math.pi) / (sd * z); return out
    mu, sg = math.log(p['median']), p['sigma']; a, b = (math.log(p['lo']) - mu) / sg, (math.log(p['hi']) - mu) / sg
    z = _ncdf(b) - _ncdf(a); u = (np.log(c[ok]) - mu) / sg
    out[ok] = np.exp(-0.5 * u * u) / math.sqrt(2.0 * math.pi) / (sg * c[ok] * z); return out

def setname(leg): return leg.split('-')[0]
def set_windage(leg):
    ref = f'{RUNS}/{setname(leg)}-glorys12-1/responses.json'; j = json.load(open(ref))
    return np.array(j['classes'][1]['responses'])[:, 1]

def weights(leg, tgt):
    c = set_windage(leg)
    if tgt['tag'] == 'identity': return np.ones(len(c)), 1.0
    q = tl_pdf(c, tgt) / tl_pdf(c, SAMP_H if leg.startswith('whigh') else SAMP); ess = float(q.sum() ** 2 / (q ** 2).sum()); return q / q.mean(), ess

def reweight_bytes(src, q):
    buf = bytearray(open(src, 'rb').read()); off = 0; n_mod = 0
    while off < len(buf):
        h = np.frombuffer(buf, HDR, 1, off)[0]; assert h['magic'] == b'ARV1', off
        off += HDR.itemsize; n = int(h['n']); r = np.frombuffer(buf, REC, n, off)
        if int(h['cls']) == 1 and n > 0:
            r['w'][:] = (r['w'].astype(np.float64) * q[r['particle']]).astype(np.float32); n_mod += n
        off += REC.itemsize * n
    return buf, n_mod

def task(args):
    import threading
    tgt, leg, cfg = args; t0 = time.time(); tag = tgt['tag']
    fifo = f'{OUTDIR}/{tag}/.{leg}.fifo'; out = f'{OUTDIR}/{tag}/{leg}.jsonl'; os.makedirs(f'{OUTDIR}/{tag}', exist_ok=True)
    q, ess = weights(leg, tgt)
    buf, n_mod = reweight_bytes(f'{RUNS}/{leg}/arrivals.bin', q)
    txt = open(cfg).read()
    txt, k1 = re.subn(r'^arrivals = .*$', f'arrivals = ["{fifo}"]', txt, flags=re.M); txt, k2 = re.subn(r'^output = .*$', f'output = "{out}"', txt, flags=re.M)
    txt, k3 = re.subn(r'^bandwidths_km = .*$', 'bandwidths_km = [50.0]', txt, flags=re.M); assert (k1, k2, k3) == (1, 1, 1), cfg
    cf = f'{OUTDIR}/{tag}/{leg}.toml'; open(cf, 'w').write(txt)
    if os.path.exists(fifo): os.remove(fifo)
    os.mkfifo(fifo)                                               # a named pipe: the reweighted bytes never touch the disk
    env = dict(os.environ, DRIFT_RESCORE=cf)
    proc = subprocess.Popen([BIN, 'rescore_entry', '--ignored', '--nocapture'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def feed():
        with open(fifo, 'wb') as f: f.write(buf)
    th = threading.Thread(target=feed, daemon=True); th.start()
    th.join(timeout=60)
    if th.is_alive():                                             # the rescorer did not open the pipe (failed early): release the writer
        try:
            fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK); os.close(fd)
        except OSError: pass
    so, se = proc.communicate(); th.join(timeout=5); os.remove(fifo); del buf
    import resource; peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss      # kB; largest child of this worker so far (upper bound)
    if proc.returncode != 0: return dict(tag=tag, leg=leg, rc=proc.returncode, err=se[-400:])
    with open(out) as f, gzip.open(out + '.gz', 'wt', compresslevel=5) as g:
        for line in f:
            d = json.loads(line)
            for s_ in d['sets']: s_['half_a'] = []; s_['half_b'] = []
            g.write(json.dumps(d, separators=(',', ':')) + '\n')
    os.remove(out); os.remove(cf)
    return dict(tag=tag, leg=leg, rc=0, ess_particles=round(ess, 1), n_modified=n_mod, peak_gb=round(peak / 1e6, 2), seconds=round(time.time() - t0, 1))

if __name__ == '__main__':
    cfgs = {}
    for f in glob.glob(f'{CFGDIR}/*.toml'):
        leg = os.path.basename(f).split('--', 1)[1][:-5]; cfgs[leg] = f
    legs = LEGS or sorted(cfgs)
    jobs = [(t, l, cfgs[l]) for t in TARGETS for l in legs if 'prefix' not in t or l.startswith(tuple(t['prefix']))]   # a target may name the leg families it applies to
    T0 = time.time(); res = []
    with Pool(PROCS) as pool:
        for r in pool.imap_unordered(task, jobs):
            res.append(r); print(json.dumps(r), flush=True)
    json.dump(res, open(f'{OUTDIR}/summary.json', 'w'), indent=1)
    print('done', round(time.time() - T0), 's; failures', sum(1 for r in res if r['rc'] != 0), flush=True)
