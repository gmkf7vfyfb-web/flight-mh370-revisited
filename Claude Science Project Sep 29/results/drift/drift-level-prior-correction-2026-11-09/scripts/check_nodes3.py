exec(open('offline/drift_alone_mc.py').read().split('rows = []')[0])
import json
mj = json.load(open('oldrun/conv-globcurrent-1-coefficients-meta.json')); alt = {a['name']: np.array(a['mu']) for a in mj['levels']['alternatives']}
NT = {m: pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'oldrun/conv-{m}-?-nodes.csv'))]) for m in MODELS}
metaN.z = z256; out = []; flat = mu0.copy(); flat[:18] = 0.0
print('ramp used:', np.round(mu0[:6], 3).tolist(), ' module off:', np.round(alt['off'][:6], 3).tolist())
R16 = sub(recO, 16)
for m in MODELS:
    nt = NT[m]; lc = [c for c in nt.columns if c in ('lat_deg', 'node_lat', 'lat')][0]; oc = [c for c in nt.columns if c in ('lon_deg', 'node_lon', 'lon')][0]
    ii = [int(np.argmin(np.hypot(nt[lc].values - recO[m][k]['lat'], nt[oc].values - recO[m][k]['lon']))) for k in common]
    for lab, mu in (('module off prior (ramp)', alt['off']), ('flat in time (rescore default before fix)', flat)):
        mine = np.array([lmean(terms(R16[m][k]['sets'][0], 'full', metaN, mu, NINE).sum(2).ravel()) for k in common])
        d = mine - nt['ln_l_lev_off'].values[ii]
        out.append(dict(model=m, prior=lab, diff_mean=d.mean(), diff_sd_all=d.std(), max_abs_dev=np.abs(d - d.mean()).max(), north_minus_south=d[lat > -30].mean() - d[lat < -36].mean()))
D = pd.DataFrame(out); print(D.round(6).to_string(index=False)); D.to_csv('res-alone/scorer-vs-module-node-check.csv', index=False)
