"""Variants of the wide-class run on the southern release points, same ocean samples (seeds 217-232): ocean-error length scale 50 and 200 km (base 100 km), and an independent particle set (master seed 23, base 22; legs 2 and 3).
Paired by (release point, ocean sample, model). Metrics, core-weighted over the release points present in the variant, two ocean models with equal weight:
 early fraction of the Mossel Bay kernel arrivals by day 655 and 745; probability that the model find date is as early as observed (ramp, delay 60 d) for the three earliest exterior finds; mean Mossel Bay find coefficient.
Uncertainty: bootstrap over the ocean samples (2000 draws, the same resampled indices for variant and base)."""
import numpy as np, pandas as pd, datetime as dt
RELEASE = 1394237977.0
def day(iso, end=False): return (dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc).timestamp() - RELEASE) / 86400.0 + (1.0 if end else 0.0)
BIN = 5.0; NB = 212; TC = (np.arange(NB) + 0.5) * BIN; DAYS = np.arange(0, 1060)
B1, B2 = day('2015-07-29'), day('2016-02-29', True); NU = np.where(DAYS < B1, 0.1, np.where(DAYS < B2, 0.5, 1.0))
l = np.load('res-smooth/lm-head-s31.npz'); LAT, LON = l['lat'], l['lon']; Wn = np.load('res-smooth/wnode_df.npy'); Wn = Wn / Wn.sum()
ITEMS = ['mossel-bay-engine-cowling-roy', 'paindane-right-flap-fairing', 'vilanculos-horizontal-stabilizer-panel']
FIND = {'mossel-bay-engine-cowling-roy': '2015-12-23', 'paindane-right-flap-fairing': '2015-12-27', 'vilanculos-horizontal-stabilizer-panel': '2016-02-28'}
def pit_curve(h, delay=60.0):
    g = np.zeros(len(DAYS))
    for k in np.nonzero(h > 0)[0]:
        x = DAYS - TC[k]; g += np.where(x > 0, h[k] * np.exp(-np.maximum(x, 0) / delay) / delay, 0.0)
    return g * NU
def cdf_at(g, t): c = np.cumsum(g); return float(c[int(t)] / c[-1]) if c[-1] > 0 else np.nan
def node_idx(lat, lon):
    return np.array([int(((LAT - a) ** 2 + (LON - b) ** 2).argmin()) for a, b in zip(lat, lon)])
def load(path, model):
    z = np.load(path, allow_pickle=True); items = [str(x) for x in z['items']]
    return dict(node=node_idx(z['lat'], z['lon']), env=z['env_seed'].astype(int), hist=z['hist'].astype(float), a60=z['a60'], items=items)
def table(d, idx, nodes, envs, w):
    # idx: ocean-sample subset; returns metrics from core-weighted histogram over (nodes, selected envs)
    m = np.isin(d['node'], nodes) & np.isin(d['env'], envs)
    ww = np.array([w[n] for n in d['node'][m]]); ww = ww / ww.sum()
    return d, m, ww
base = {mod: load(f'arr-wide/arrivals-timing-{mod}.npz', mod) for mod in ('globcurrent', 'glorys12')}
rows = []
rng = np.random.default_rng(5)
for var in ('wls50', 'wls200', 'wseed23'):
    V = {mod: load(f'arr-var/{var}/arrivals-timing-{mod}.npz', mod) for mod in ('globcurrent', 'glorys12')}
    nodes = np.unique(np.concatenate([V[m]['node'] for m in V])); envs = np.arange(217, 233)
    W = {n: Wn[n] for n in nodes}; sw = sum(W.values())
    def metrics(D, sel_envs, mods=('globcurrent', 'glorys12')):
        # core-weighted (over the variant's release points) mean histogram per item, mean over the selected ocean samples, equal weight per model
        H = {}
        for mod in mods:
            d = D[mod]; m = np.isin(d['node'], nodes) & np.isin(d['env'], sel_envs); acc = {}
            for n in nodes:
                s = m & (d['node'] == n)
                if s.sum() == 0: continue
                acc[n] = d['hist'][s].mean(0)
            H[mod] = sum(W[n] / sw * acc[n] for n in acc)
        h = 0.5 * (H['globcurrent'] + H['glorys12']); it = {n: i for i, n in enumerate(base['globcurrent']['items'])}
        out = {}
        mb = h[it['mossel-bay-engine-cowling-roy']]; out['mb_early655'] = mb[:131].sum() / mb.sum(); out['mb_early745'] = mb[:149].sum() / mb.sum(); out['mb_mass'] = mb.sum()
        for name in ITEMS:
            t = 0.5 * (day(FIND[name]) + day(FIND[name], True)); out['pit_' + name.split('-')[0]] = cdf_at(pit_curve(h[it[name]]), t)
        return out
    # restrict the base to the same nodes and ocean samples
    m0 = metrics(base, envs); m1 = metrics(V, envs)
    # bootstrap over ocean samples (paired)
    bs = []
    for b in range(300):
        sel = rng.choice(envs, size=len(envs), replace=True)
        # np.isin cannot repeat; emulate by weighting: build resampled datasets via index lists
        def boot(D):
            H = {}
            for mod in ('globcurrent', 'glorys12'):
                d = D[mod]; acc = {}
                for n in nodes:
                    rows_n = [np.nonzero((d['node'] == n) & (d['env'] == e))[0] for e in sel]; rows_n = [r[0] for r in rows_n if len(r)]
                    if rows_n: acc[n] = d['hist'][rows_n].mean(0)
                H[mod] = sum(W[n] / sw * acc[n] for n in acc)
            h = 0.5 * (H['globcurrent'] + H['glorys12']); it = {n: i for i, n in enumerate(base['globcurrent']['items'])}
            mb = h[it['mossel-bay-engine-cowling-roy']]; return mb[:131].sum() / mb.sum(), cdf_at(pit_curve(mb), 0.5 * (day('2015-12-23') + day('2015-12-23', True)))
        a = boot(base); v = boot(V); bs.append((v[0] - a[0], v[1] - a[1]))
        if b >= 59: break
    bs = np.array(bs)
    r = dict(variant=var, release_points=len(nodes), ocean_samples=len(envs), **{f'base_{k}': v for k, v in m0.items()}, **{f'variant_{k}': v for k, v in m1.items()},
             diff_mb_early655=m1['mb_early655'] - m0['mb_early655'], diff_mb_early655_boot_sd=float(bs[:, 0].std()), diff_pit_mb=m1['pit_mossel'] - m0['pit_mossel'], diff_pit_mb_boot_sd=float(bs[:, 1].std()))
    rows.append(r)
df = pd.DataFrame(rows); df.round(4).to_csv('overnight-variants-vs-base.csv', index=False); pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
print(df[['variant', 'release_points', 'base_mb_early655', 'variant_mb_early655', 'diff_mb_early655', 'diff_mb_early655_boot_sd', 'base_pit_mossel', 'variant_pit_mossel', 'diff_pit_mb', 'diff_pit_mb_boot_sd', 'base_pit_paindane', 'variant_pit_paindane', 'base_pit_vilanculos', 'variant_pit_vilanculos']].round(4).T.to_string())
