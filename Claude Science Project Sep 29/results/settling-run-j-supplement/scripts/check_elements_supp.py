import sys, json, numpy as np, pathlib
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange/settling/run-j-supplement'); res = {}
for st in sys.argv[1:]:
    d = X / st; tag = next(d.glob('*_info.json')).name.replace('_info.json', '')
    T = np.fromfile(d / f'{tag}_impacts.f64', '<f8').reshape(-1, 14); E = np.memmap(d / f'{tag}_elements.f64', '<f8', 'r').reshape(-1, 8)
    info = json.loads((d / f'{tag}_info.json').read_text()); z = np.load(d / f'{tag}_draws.npz')
    r = E[:, 0].astype(np.int64); dr = E[:, 1].astype(np.int64); fate = E[:, 4]
    mx = np.zeros(len(T), np.int64); np.maximum.at(mx, r, dr + 1)
    key = r * (1 << 20) + dr; uk, inv = np.unique(key, return_inverse=True)
    ms = np.bincount(inv, weights=E[:, 7]); rel = ms / T[uk >> 20, 7]
    u, c = np.unique(fate, return_counts=True)
    # every product's (row, draw) outcome exists in the element file
    prod_ok = all(np.isin(z[f'rows_{j}'] * (1 << 20) + z[f'draws_{j}'], uk).all() for j in range(len(info['products'])))
    src = np.load(d / f'{tag}_source.npy')
    res[st] = dict(table_rows=int(len(T)), draws=int(T[:, 12].sum()), outcomes=int(uk.size), elements=int(len(E)), products=len(info['products']),
                   draws_match=bool(np.array_equal(mx, T[:, 12].astype(np.int64))), impacts_finite=bool(np.isfinite(T).all()),
                   elements_finite=bool(np.isfinite(E[:, [0, 1, 2, 3, 4, 7]]).all()), settled_latlon_finite=bool(np.isfinite(E[fate == 0][:, 5:7]).all()),
                   mass_ratio_min_max=[float(rel.min()), float(rel.max())], fates={str(int(a)): int(b) for a, b in zip(u, c)},
                   not_computed_or_refused_outcomes=int(np.unique(key[np.isin(fate, [2, -1])]).size), every_product_outcome_present=bool(prod_ok),
                   source_rows=int(len(src)), seeds=sorted(set(int(x) for x in src[:, 1])), lat_range=[float(T[:, 1].min()), float(T[:, 1].max())],
                   lon_range=[float(T[:, 2].min()), float(T[:, 2].max())], impact_after_0019_37=bool((T[:, 0] > 1394237977.443).all()),
                   bytes={f.name: f.stat().st_size for f in d.iterdir()})
    print(st, json.dumps({k: v for k, v in res[st].items() if k != 'bytes'}), flush=True)
json.dump(res, open('element_checks_' + '_'.join(s.replace('run-j-', '') for s in sys.argv[1:]) + '.json', 'w'), indent=1)
