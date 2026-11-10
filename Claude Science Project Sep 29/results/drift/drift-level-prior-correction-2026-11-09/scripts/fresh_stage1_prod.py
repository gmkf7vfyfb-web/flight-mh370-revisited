"""FRESH-ARRIVAL SENSITIVITY (10 Nov 2026): stage 1 with the time-ashore marks swapped in one item at a time. Configs flap3, flap10, mb3, pain14, fresh3all, fresh10all (see CONF).
Stage 1 of the smoothed drift likelihood. For one drift configuration and a list of level-draw seeds (16384 draws each), write per release point and
per ocean sample (environment) the value lm = ln mean_over_draws exp(sum over items of ln term), for each ocean model. The drift log-likelihood at a point is
then ln mean_over_environments exp(lm), so bootstrap over environments, halves and any number of seeds need no further scoring.
Items: twelve identity-weighted non-circular items (mixture with unrelated debris whose background uses the Davey model + fuel core, D0). Ramp prior 0.1/0.5/1/1.
Usage: LEVELS=ramp python smooth_stage1.py CONFIG SEED [SEED ...]   CONFIG in head | au025 | butmb | au025nomb | mar (Mossel Bay at its ATSB find date, 21-23 Mar 2016) | fresh10 (arrival within 10 d of 23 Dec 2015) ; VALIDATE=1 compares with rescore_analysis.score."""
import sys, os, time, resource, numpy as np
CFG = sys.argv[1]; SEEDS = [int(s) for s in sys.argv[2:]]
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-smooth']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
ZDRAWS = 16384; t0 = time.time()
meta, recs, nenv = load('R3-allcoasts-4periods')
common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
ids = [f['id'] for f in meta.finds]
NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
HI = NINE + [f'item:{o}' for o in ('linga-linga-vertical-stabilizer', 'nautilus-bay-right-aileron', 'mpame-right-flap-fairing') if f'item:{o}' in ids]
PW = {f: GRADE_P[aud.loc[f.split(':')[1], 'official_classification']] for f in HI}; MB = 'item:mossel-bay-engine-cowling-roy'
MAR = 'shadow:mossel-bay-refound-2016-03-21'; F10 = 'shadow:mossel-bay-fresh-10d'
for _s in (MAR, F10): PW[_s] = PW[MB]  # same identity grade as the original item; only the date model changes
FL = 'item:reunion-right-flaperon'; PA = 'item:paindane-right-flap-fairing'     # fresh-arrival shadows (sensitivity, 10 Nov 2026): same identity weight as the original item
SH = {'flap3': 'shadow:flaperon-fresh-3d', 'flap10': 'shadow:flaperon-fresh-10d', 'mb3': 'shadow:mossel-bay-fresh-3d', 'mb10': 'shadow:mossel-bay-fresh-10d', 'pain14': 'shadow:paindane-fresh-14d'}
PW[SH['flap3']] = PW[SH['flap10']] = PW[FL]; PW[SH['mb3']] = PW[SH['mb10']] = PW[MB]; PW[SH['pain14']] = PW[PA]
if CFG == 'pw1': PW = {f: 1.0 for f in PW}   # sensitivity: every item certain (no mixture with unrelated debris)
if CFG == 'pwlow': PW = {f: {1.0: 1.0, 0.98: 0.9, 0.9: 0.7}.get(v, v) for f, v in PW.items()}   # sensitivity: pessimistic weights 1 / 0.9 / 0.7
swapmb = lambda new: [new if x == MB else x for x in HI]
CONF = {'pw1': (HI, mu_tiers(meta)), 'pwlow': (HI, mu_tiers(meta)), 'mbonly': ([MB], mu_tiers(meta)), 'mbonlymar': ([MAR], mu_tiers(meta)), 'mar': (swapmb(MAR), mu_tiers(meta)), 'fresh10': (swapmb(F10), mu_tiers(meta)), 'head': (HI, mu_tiers(meta)), 'au025': (HI, mu_tiers(meta, au=ruled_au(0.25))), 'butmb': ([x for x in HI if x != MB], mu_tiers(meta)),
        'au025nomb': ([x for x in HI if x != MB], mu_tiers(meta, au=ruled_au(0.25)))}
swp = lambda *pairs: [dict(pairs).get(x, x) for x in HI]
CONF.update({'flap3': (swp((FL, SH['flap3'])), mu_tiers(meta)), 'flap10': (swp((FL, SH['flap10'])), mu_tiers(meta)), 'mb3': (swp((MB, SH['mb3'])), mu_tiers(meta)), 'pain14': (swp((PA, SH['pain14'])), mu_tiers(meta)),
             'fresh3all': (swp((FL, SH['flap3']), (MB, SH['mb3']), (PA, SH['pain14'])), mu_tiers(meta)), 'fresh10all': (swp((FL, SH['flap10']), (MB, SH['mb10']), (PA, SH['pain14'])), mu_tiers(meta))})
sel, mu = CONF[CFG]; wnode = np.load('res-smooth/wnode_df.npy'); assert len(wnode) == len(common) == 84, (len(wnode), len(common))
p = np.array([PW.get(f, 1.0) for f in sel])
print('loaded', round(time.time() - t0), 's; items', len(sel), flush=True)
for seed in SEEDS:
    meta.z = np.random.default_rng(seed).standard_normal((ZDRAWS, meta.z.shape[1])); out = {}
    for m in MODELS:
        Ts = [terms(recs[m][k]['sets'][0], 'full', meta, mu, sel) for k in common]
        bj = np.zeros((ZDRAWS, len(sel)))
        for w, T in zip(wnode, Ts):
            with np.errstate(over='ignore'): bj += w * np.exp(T).mean(0)
        lb = np.log(np.maximum(bj, 1e-300)); lm = np.full((len(common), 32), np.nan)
        for i, T in enumerate(Ts):
            mix = np.logaddexp(np.log(np.where(p > 0, p, 1e-300))[None, None, :] + T, np.log(np.maximum(1 - p, 1e-300))[None, None, :] + lb[None, :, :])
            mix = np.where(p[None, None, :] >= 1.0, T, mix); s = mix.sum(2); lm[i, :s.shape[0]] = lmean(s, axis=1)
        out[m] = lm; del Ts
    if os.environ.get('VALIDATE') == '1':
        ref = score(meta, recs, nenv, common, mu, sel, PW, wnode=wnode)
        for m in MODELS:
            mine = np.array([lmean(row[np.isfinite(row)]) for row in out[m]]); print('VALIDATE', m, 'max |diff| vs rescore_analysis.score', float(np.abs(mine - ref[m]).max()), flush=True)
    np.savez(f'res-smooth/lm-{CFG}-s{seed}.npz', lm_globcurrent=out['globcurrent'], lm_glorys12=out['glorys12'], lat=lat, lon=lon, nodes=np.array(common))
    print('seed', seed, 'done', round(time.time() - t0), 's; peak RSS GB', round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2), flush=True)
