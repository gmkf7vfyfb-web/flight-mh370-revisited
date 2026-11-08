"""Build rescore configurations (TOML) and matching coefficient metadata (JSON) for the drift module's
offline rescoring of arrivals.bin (lib.rs rescore). The metadata has the layout drift_coef.Meta reads."""
import json, numpy as np, pandas as pd, datetime as dt

RELEASE = 1394237977.0          # module release_unix_s (00:19:37 UTC 8 Mar 2014)
CLASSES = ['flaperon', 'low_exposure_exterior', 'high_windage_interior']

def day(iso, end=False):
    t = dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc).timestamp()
    return (t - RELEASE) / 86400.0 + (1.0 if end else 0.0)

def toml_str(cfg):
    q = lambda s: json.dumps(s)
    L = [f'arrivals = [{", ".join(q(a) for a in cfg["arrivals"])}]', f'output = {q(cfg["output"])}', f'n_classes = {cfg["n_classes"]}',
         f'particles_per_class = {cfg["particles_per_class"]}', f'window_end_days = {cfg["window_end_days"]!r}',
         f'period_breaks_days = [{", ".join(repr(x) for x in cfg["period_breaks_days"])}]', f'delay_days = {cfg["delay_days"]!r}',
         f'bandwidths_km = [{", ".join(repr(x) for x in cfg["bandwidths_km"])}]', '']
    for s in cfg['segments']:
        L += ['[[segments]]', f'name = {q(s["name"])}', 'boxes = [' + ', '.join('[' + ', '.join(repr(float(v)) for v in b) + ']' for b in s['boxes']) + ']', '']
    for f in cfg['finds']:
        L += ['[[finds]]', f'id = {q(f["id"])}', f'class = {f["class"]}', f'lon = {f["lon"]!r}', f'lat = {f["lat"]!r}',
              f't_start_days = {f["t_start_days"]!r}', f't_end_days = {f["t_end_days"]!r}'] + ([f'fresh_days = {f["fresh_days"]!r}'] if f.get('fresh_days') else []) + ['']
    return '\n'.join(L)

def meta_for(cfg, z=None, sigma=1.0, seed=3, draws=256, mu_period=None, alternatives=()):
    """Coefficient metadata for a rescore output. z: standard-normal level draws (draws x blocks); new draws if None."""
    seg = [s['name'] for s in cfg['segments']]; npd = len(cfg['period_breaks_days']) + 1; nb = len(seg) * npd
    if z is None: z = np.random.default_rng(seed).standard_normal((draws, nb))
    mu_period = [0.0] * npd if mu_period is None else mu_period
    seg_index = lambda f: next(i for i, s in enumerate(cfg['segments']) if any(b[0] <= f['lon'] <= b[1] and b[2] <= f['lat'] <= b[3] for b in s['boxes']))
    finds = [dict(id=f['id'], **{'class': f['class']}, segment=seg_index(f), t_start_days=f['t_start_days'], t_end_days=f['t_end_days'], fresh_days=f.get('fresh_days')) for f in cfg['finds']]
    return dict(shadow_finds=[], segments=seg, n_periods=npd, period_breaks_days=cfg['period_breaks_days'], window_end_days=cfg['window_end_days'],
                classes=CLASSES[:cfg['n_classes']], finds=finds, particles_per_class=cfg['particles_per_class'],
                levels=dict(ln_mean_by_period=mu_period, sigma=sigma, draws=int(z.shape[0]), seed=seed, mu_primary=list(np.tile(mu_period, len(seg))),
                            alternatives=list(alternatives), z=np.asarray(z).tolist()))
