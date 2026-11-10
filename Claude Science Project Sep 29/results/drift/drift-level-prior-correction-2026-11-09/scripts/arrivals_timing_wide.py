#!/usr/bin/env python3
"""Arrival-time analysis of the extended-window drift run (arrivals.bin), 9 Nov 2026.

For every find of the headline set, every release point and every ocean sample, reproduce the module's own find
coefficient (recovery.rs `coefficients`: Gaussian kernel of 50 km on the great-circle distance, exponential delay of
mean 60 d, find window [t_start, t_end), arrival counted until the particle leaves the coast again) and, in addition,
write the kernel-weighted arrival-time histogram (5-day bins) so that the timing of the arrivals can be examined.

Validation: the reproduced coefficient is compared with `sets[0].full[env][class].a` of coefficients.jsonl for the nine
stringent finds, for every node and every ocean sample of every leg (summed over the period columns).

Wide-run variant (10 Nov 2026): LEGPREFIX selects the legs (e.g. wide-,wide2-); validation maps the module's find ids to items.
Outputs (in ./out): arrivals-timing-<model>.npz, mossel-bay-kernel-arrivals-<model>.npz, validation.json, log.txt.
Run: python3 arrivals_timing.py [RUNS_DIR] [OUT_DIR] [PROCESSES]. Needs numpy.
"""
import os, sys, json, glob, math, time
import numpy as np
from multiprocessing import Pool

RUNS = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/mh370/drift/coef/runs')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'out'
NPROC = int(sys.argv[3]) if len(sys.argv) > 3 else 12
HDR = np.dtype([('magic', 'S4'), ('node', '<u4'), ('lat', '<f8'), ('lon', '<f8'), ('env_seed', '<u8'), ('cls', '<u4'),
                ('released', '<u4'), ('n', '<u4'), ('model_error', '<f8'), ('left_domain', '<f8')])
REC = np.dtype([('particle', '<u4'), ('w', '<f4'), ('t_days', '<f8'), ('t_leave_days', '<f4'), ('lon', '<f8'), ('lat', '<f8'),
                ('line', '<i4'), ('s_km', '<f8'), ('segment', '<i4')])
assert HDR.itemsize == 60 and REC.itemsize == 52
RELEASE = 1394237977.0
H_KM = 50.0; NORM = 1.0 / (H_KM * math.sqrt(2.0 * math.pi)); CUT = 6.0
BIN = 5.0; NBIN = 212
DELAY = 60.0; FRESH = 10.0; DELAY_FRESH = DELAY * FRESH / (DELAY + FRESH)
WINDOW_END = 1058.9863773148147

def day(iso, end=False):
    import datetime as dt
    t = dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc).timestamp()
    return (t - RELEASE) / 86400.0 + (1.0 if end else 0.0)

# id, class, lon, lat, first day, last day (from data/debris-evidence-audit.csv); the nine stringent finds are the module's own
ITEMS = [('reunion-right-flaperon', 0, 55.649150, -20.916180, '2015-07-29'), ('mossel-bay-engine-cowling-roy', 1, 22.149905, -34.093767, '2015-12-23'),
         ('paindane-right-flap-fairing', 1, 35.499796, -24.078057, '2015-12-27'), ('vilanculos-horizontal-stabilizer-panel', 1, 35.519020, -22.088570, '2016-02-28'),
         ('mauritius-left-outboard-flap', 1, 57.701386, -20.023383, '2016-05-10'), ('rodrigues-door-closet-panel', 2, 63.471632, -19.738711, '2016-03-30'),
         ('chidenguele-right-fan-cowling', 1, 34.196373, -24.958022, '2016-04-24'), ('antsiraka-cabin-interior-panel', 2, 49.726188, -16.862289, '2016-06-12'),
         ('pemba-right-outboard-flap', 1, 39.868086, -5.056071, '2016-06-23'), ('linga-linga-vertical-stabilizer', 1, 35.400766, -23.739314, '2016-08-26'),
         ('nautilus-bay-right-aileron', 1, 21.978754, -34.220809, '2016-12-23'), ('mpame-right-flap-fairing', 1, 29.062852, -32.097481, '2017-01-27')]
ITEM = [dict(id=i[0], cls=i[1], lon=i[2], lat=i[3], t0=day(i[4]), t1=day(i[4], True)) for i in ITEMS]
NITEM = len(ITEM); MB = 1
MB_MARCH = (day('2016-03-21'), day('2016-03-22', True))     # shadow find 'mossel-bay-refound-2016-03-21'
NINE = 9                                                     # items 0..8 are in the module's coefficient file

def gc_km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2); dl = np.radians(lon2 - lon1)
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.minimum(1.0, np.sqrt(h)))

def cdf(d, mean):
    d = np.asarray(d, float); return np.where(d <= 0, 0.0, 1.0 - np.exp(-np.maximum(d, 0) / mean))

def coef(t, w, tl, k, t0, t1, mean, n):
    """module coefficient a for one find: (1/N) sum w K [cdf(b - t) - cdf(t0 - t)] / width, b = min(t1, t_leave); skip t >= b or b <= t0."""
    b = np.minimum(t1, tl.astype(float)); ok = (t < b) & (b > t0)
    v = w * k * (cdf(b - t, mean) - cdf(t0 - t, mean)) / (t1 - t0)
    return float(np.sum(v[ok]) / n)

def read_blocks(path):
    mm = np.memmap(path, dtype=np.uint8, mode='r'); off = 0; size = mm.shape[0]
    while off < size:
        h = np.frombuffer(mm, HDR, 1, off)[0]; off += HDR.itemsize
        assert h['magic'] == b'ARV1', (path, off)
        n = int(h['n']); r = np.frombuffer(mm, REC, n, off); off += REC.itemsize * n
        yield h, r

def leg_worker(leg):
    t0 = time.time(); name = os.path.basename(leg)
    model = 'globcurrent' if 'globcurrent' in name else 'glorys12'
    resp_files = glob.glob(os.path.join(leg, '*responses.json')); R = json.load(open(resp_files[0]))
    resp = {i: np.array(c['responses']) for i, c in enumerate(R['classes'])}      # per class: (particles, 5): a_stokes, c_wind, wind_angle, leeway_angle, leeway_speed
    rows = {}; mbk = []
    nrec = 0; nleave = 0
    for h, r in read_blocks(os.path.join(leg, 'arrivals.bin')):
        key = (round(float(h['lat']), 6), round(float(h['lon']), 6), int(h['env_seed'])); cl = int(h['cls']); n = int(h['released'])
        row = rows.setdefault(key, dict(hist=np.zeros((NITEM, NBIN), np.float32), a60=np.zeros(NITEM), a9=np.zeros(NITEM), amar=0.0, seg=np.zeros((6, NBIN), np.float32),
                                        nodeid=int(h['node']), leaves=0, recs=0))
        nrec += len(r); row['recs'] += len(r)
        if len(r) == 0: continue
        fin = np.isfinite(r['t_leave_days']); nleave += int(fin.sum()); row['leaves'] += int(fin.sum())
        t = r['t_days']; w = r['w'].astype(float); tl = r['t_leave_days']
        for j, it in enumerate(ITEM):
            if it['cls'] != cl: continue
            d = gc_km(it['lon'], it['lat'], r['lon'], r['lat']); z = d / H_KM; m = z <= CUT
            if not m.any(): continue
            k = NORM * np.exp(-0.5 * z[m] ** 2)
            tt, ww, ll = t[m], w[m], tl[m]
            row['a60'][j] += coef(tt, ww, ll, k, it['t0'], it['t1'], DELAY, n)
            row['a9'][j] += coef(tt, ww, ll, k, it['t0'], it['t1'], DELAY_FRESH, n)
            if j == MB:
                row['amar'] += coef(tt, ww, ll, k, MB_MARCH[0], MB_MARCH[1], DELAY, n)
                idx = np.nonzero(m)[0]
                mbk.append(np.column_stack([np.full(len(idx), key[0]), np.full(len(idx), key[2]), r['particle'][idx], tt, ww * k / n, d[m],
                                            resp[cl][r['particle'][idx], 1], resp[cl][r['particle'][idx], 2], np.where(np.isfinite(ll), ll, -1.0)]))
            bi = np.minimum((tt // BIN).astype(int), NBIN - 1); ok = tt < WINDOW_END + 1
            row['hist'][j] += np.bincount(bi[ok], weights=(ww * k / n)[ok], minlength=NBIN).astype(np.float32)
        if cl == 1:
            for s in range(6):
                ms = r['segment'] == s
                if ms.any():
                    bi = np.minimum((t[ms] // BIN).astype(int), NBIN - 1); row['seg'][s] += np.bincount(bi, weights=w[ms] / n, minlength=NBIN).astype(np.float32)
    # validation against the module's coefficients
    mp = glob.glob(os.path.join(leg, '*coefficients-meta.json')); cp = glob.glob(os.path.join(leg, '*coefficients.jsonl'))
    val = dict(leg=name, compared=0, max_rel=0.0, max_abs_zero=0.0, worst=None, n_zero_mismatch=0)
    if mp and cp:
        meta = json.load(open(mp[0])); seeds = [e['seed'] for e in meta['envs']]
        order = {}
        for fi, f in enumerate(meta['finds']): order.setdefault(f['class'], []).append(fi)
        idmap = {it['id']: k for k, it in enumerate(ITEM)}
        fidx = [idmap[f['id'].split(':')[1]] for f in meta['finds']]          # meta find index -> ITEM index (wide legs: class-1 finds only)
        for k_, f in zip(fidx, meta['finds']):
            assert abs(ITEM[k_]['t0'] - f['t_start_days']) < 1e-6 and abs(ITEM[k_]['t1'] - f['t_end_days']) < 1e-6, ('window', ITEM[k_]['id'])
        for line in open(cp[0]):
            rec = json.loads(line); lat, lon = round(rec['lat'], 6), round(rec['lon'], 6)
            for e, seed in enumerate(seeds):
                mine = rows.get((lat, lon, seed))
                if mine is None: continue
                for c, cd in enumerate(rec['sets'][0]['full'][e]):
                    if cd is None: continue
                    for ri, fm in enumerate(order.get(c, [])):
                        fi = fidx[fm]; exp = float(sum(cd['a'][ri])); got = float(mine['a60'][fi])
                        if exp > 0:
                            rel = abs(got - exp) / exp; val['compared'] += 1
                            if rel > val['max_rel']: val['max_rel'] = rel; val['worst'] = (lat, seed, ITEM[fi]['id'], exp, got)
                        else:
                            val['max_abs_zero'] = max(val['max_abs_zero'], abs(got)); val['n_zero_mismatch'] += int(got != 0.0)
    keys = sorted(rows.keys())
    out = dict(model=model, leg=name, keys=keys, nodeid=[rows[k]['nodeid'] for k in keys], hist=np.stack([rows[k]['hist'] for k in keys]) if keys else None,
               a60=np.stack([rows[k]['a60'] for k in keys]), a9=np.stack([rows[k]['a9'] for k in keys]), amar=np.array([rows[k]['amar'] for k in keys]),
               seg=np.stack([rows[k]['seg'] for k in keys]), recs=int(nrec), leaves=int(nleave), mbk=np.concatenate(mbk) if mbk else np.zeros((0, 9)), val=val,
               secs=round(time.time() - t0))
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); T0 = time.time()
    legs = sorted(d for d in glob.glob(os.path.join(RUNS, '*')) if os.path.isfile(os.path.join(d, 'arrivals.bin')) and os.path.basename(d).startswith(tuple(os.environ.get('LEGPREFIX', 'ext-,ext2-').split(','))))
    log = open(os.path.join(OUT, 'log.txt'), 'w')
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s, flush=True); log.write(s + '\n'); log.flush()
    P('legs', len(legs), [os.path.basename(x) for x in legs], 'numpy', np.__version__)
    with Pool(min(NPROC, len(legs))) as pool: res = pool.map(leg_worker, legs, chunksize=1)
    vals = [r['val'] for r in res]; P('validation per leg', json.dumps(vals, default=str))
    for model in ('globcurrent', 'glorys12'):
        rs = [r for r in res if r['model'] == model]
        keys = [k for r in rs for k in r['keys']]
        np.savez_compressed(os.path.join(OUT, f'arrivals-timing-{model}.npz'), lat=np.array([k[0] for k in keys]), lon=np.array([k[1] for k in keys]), env_seed=np.array([k[2] for k in keys]),
                            hist=np.concatenate([r['hist'] for r in rs]), a60=np.concatenate([r['a60'] for r in rs]), a9=np.concatenate([r['a9'] for r in rs]),
                            amar=np.concatenate([r['amar'] for r in rs]), seg=np.concatenate([r['seg'] for r in rs]), items=np.array([i['id'] for i in ITEM]),
                            bin_days=BIN, leg=np.array([r['leg'] for r in rs for _ in r['keys']]))
        np.savez_compressed(os.path.join(OUT, f'mossel-bay-kernel-arrivals-{model}.npz'), cols=np.array(['node_lat', 'env_seed', 'particle', 't_days', 'kernel_mass', 'distance_km', 'c_wind', 'wind_angle_deg', 't_leave_days']),
                            data=np.concatenate([r['mbk'] for r in rs]))
        P(model, 'rows', len(keys), 'records', sum(r['recs'] for r in rs), 'with refloat', sum(r['leaves'] for r in rs))
    json.dump(dict(validation=vals, seconds=round(time.time() - T0), nproc=NPROC), open(os.path.join(OUT, 'validation.json'), 'w'), default=str, indent=1)
    import resource
    P('peak RSS of the largest worker, GB', round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1e6, 2))
    P('done', round(time.time() - T0), 's')
