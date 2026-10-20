"""Merge the arc-latitude dedicated drift run (26-40 S, 15ab7c9) with its northern extension (20-26 S, order C of
20 Oct 2026). Same estimator as the 18 Oct profile/posterior code (lineage of arclat-likelihood-profile.csv and
arclat-posterior-summary.csv): two-model mixture = log of the mean of L (never of normalised maps); split-half SD per
point = sqrt(((a1-b1)/2)^2 + ((a2-b2)/2)^2)/2; posterior on the run J D0 impact histogram by inverse-distance
(6 nearest points, 1/d^2) interpolation of log-likelihood.
Usage: python merge_arclat.py <old_dir> <ext_dir|-> <old_release_csv> <ext_release_csv|-> <out_dir>
"""
import sys, os, glob
import numpy as np, pandas as pd

OPT = {'finds only': 'ln_l_lev_off', 'C (low detection)': 'ln_l_lev_C', 'B (primary)': 'ln_l',
       'populated coast only': 'ln_l_lev_populated'}
MODELS = ('globcurrent', 'glorys12')
ACC = '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz'


def halves(col):
    ha = col + '_half_a' if col != 'ln_l' else 'ln_l_half_a'
    return ha, ha.replace('half_a', 'half_b')


def load(old_dir, ext_dir, old_rp, ext_rp):
    rp_old = pd.read_csv(old_rp); rp_old['source'] = 'dedicated run 26-40 S (15ab7c9)'
    N, OV = {}, {}
    for m in MODELS:
        df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'{old_dir}/arclat-{m}-*-nodes.csv'))], ignore_index=True)
        df = df.merge(rp_old[['node', 'arc_lat', 'position', 'tier', 'source']], on='node', how='left')
        assert df.arc_lat.notna().all() and len(df) == 66, (m, len(df))
        if ext_dir != '-':
            rp_ext = pd.read_csv(ext_rp)
            de = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'{ext_dir}/arclat-ext-{m}-*-nodes.csv'))], ignore_index=True)
            de = de.merge(rp_ext[['node', 'arc_lat', 'position', 'tier']], on='node', how='left')
            assert de.arc_lat.notna().all(), m
            de['source'] = 'northern extension 20-26 S (20 Oct 2026)'
            OV[m] = de[de.arc_lat == -26.0].copy()
            de = de[de.arc_lat > -26.0 + 1e-9]
            de['node'] = de['node'].map(lambda k: f'x{k}')   # extended-grid IDs (298 x 282 lattice), kept distinct
            df = pd.concat([df, de], ignore_index=True)
        N[m] = df.sort_values(['arc_lat', 'position'], ascending=[False, True]).reset_index(drop=True)
    assert (N['globcurrent'].node.values == N['glorys12'].node.values).all()
    assert np.allclose(N['globcurrent'].lat_deg, N['glorys12'].lat_deg) and np.allclose(N['globcurrent'].lon_deg, N['glorys12'].lon_deg)
    return N, OV


def mix(a, b):
    m = np.maximum(a, b); return m + np.log(0.5 * (np.exp(a - m) + np.exp(b - m)))


def profile(N):
    g = N['globcurrent']
    prof = g[['node', 'arc_lat', 'position', 'lat_deg', 'lon_deg', 'tier', 'source']].rename(columns={'lat_deg': 'node_lat', 'lon_deg': 'node_lon'}).copy()
    for o, col in OPT.items():
        v = mix(N['globcurrent'][col].values, N['glorys12'][col].values); prof[o] = v - v.max()
    for o, col in OPT.items():
        ha, hb = halves(col)
        prof[o + '_sd'] = np.sqrt(((N['globcurrent'][ha] - N['globcurrent'][hb]) / 2) ** 2 + ((N['glorys12'][ha] - N['glorys12'][hb]) / 2) ** 2).values / 2
    for m in MODELS:  # per-model values (not renormalised) for the record
        for o, col in OPT.items():
            prof[f'{o} [{m}, ln L]'] = N[m][col].values
    prof['model_error_fraction_max'] = np.maximum(N['globcurrent'].model_error_fraction, N['glorys12'].model_error_fraction).values
    prof['left_domain_fraction_max'] = np.maximum(N['globcurrent'].left_domain_fraction, N['glorys12'].left_domain_fraction).values
    prof['state'] = N['globcurrent'].state.astype(str).values + '/' + N['glorys12'].state.astype(str).values
    return prof


def core():
    A = np.load(ACC); H = A['H_D0_all'].astype(float)
    hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
    hlat = hl0 + (np.arange(H.shape[0]) + 0.5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + 0.5) * hg
    ii, jj = np.nonzero(H > 0)
    return hlat[ii], hlon[jj], H[ii, jj]


def posterior(N, cl, cn, hw):
    core_mean = (hw * cl).sum() / hw.sum()
    plat, plon = N['globcurrent'].lat_deg.values, N['globcurrent'].lon_deg.values
    dx = (cn[:, None] - plon[None]) * 111.2 * np.cos(np.radians(cl[:, None])); dy = (cl[:, None] - plat[None]) * 111.2
    dist = np.hypot(dx, dy); nn = np.argsort(dist, 1)[:, :6]; dd = np.take_along_axis(dist, nn, 1)
    W = 1 / np.maximum(dd, 1.0) ** 2; W /= W.sum(1, keepdims=True)
    cellLn = lambda v: (W * v[nn]).sum(1)

    def post(model, col):
        if model == 'mean':
            a = cellLn(N['globcurrent'][col].values); b = cellLn(N['glorys12'][col].values); m = max(a.max(), b.max())
            L = 0.5 * (np.exp(a - m) + np.exp(b - m))
        else:
            a = cellLn(N[model][col].values); m = a.max(); L = np.exp(a - m)
        p = hw * L; p /= p.sum(); o = np.argsort(cl); cdf = np.cumsum(p[o])
        q = [cl[o][np.searchsorted(cdf, x)] for x in (0.05, 0.5, 0.95)]
        return dict(mean=(p * cl).sum(), shift=(p * cl).sum() - core_mean, q05=q[0], q50=q[1], q95=q[2],
                    s3738=100 * p[(cl >= -38) & (cl < -37)].sum(), sN33=100 * p[cl >= -33].sum(),
                    sN26=100 * p[cl >= -26].sum(), sN22=100 * p[cl >= -22].sum(),
                    lnBF=np.log((hw * L).sum() / hw.sum()) + m), p
    res, POST = [], {}
    for o, col in OPT.items():
        for mod in ('globcurrent', 'glorys12', 'mean'):
            s, p = post(mod, col); POST[(o, mod)] = p
            ha, hb = halves(col); sa, _ = post(mod, ha); sb, _ = post(mod, hb)
            res.append(dict(option=o, model=mod, shift=s['shift'], shift_halfdiff=abs(sa['shift'] - sb['shift']), median=s['q50'],
                            q05=s['q05'], q95=s['q95'], share_37_38=s['s3738'], share_N33=s['sN33'], share_N26=s['sN26'],
                            share_N22=s['sN22'], share_N26_halfdiff=abs(sa['sN26'] - sb['sN26']), lnBF=s['lnBF']))
    return pd.DataFrame(res), POST, core_mean


if __name__ == '__main__':
    old_dir, ext_dir, old_rp, ext_rp, out = sys.argv[1:6]
    os.makedirs(out, exist_ok=True)
    N, OV = load(old_dir, ext_dir, old_rp, ext_rp)
    prof = profile(N); prof.to_csv(f'{out}/profile.csv', index=False)
    cl, cn, hw = core(); R, POST, cm = posterior(N, cl, cn, hw); R.to_csv(f'{out}/posterior.csv', index=False)
    print(len(prof), 'points; core mean', round(cm, 3))
    print(R[R.model == 'mean'].round(3).to_string(index=False))
