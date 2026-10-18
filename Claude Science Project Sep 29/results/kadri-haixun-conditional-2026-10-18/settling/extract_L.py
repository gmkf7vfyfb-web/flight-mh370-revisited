"""Extract run J impact rows within 400 km of the Kadri bearing/7th-arc crossing or the Haixun 01 contact.
Superset of locality L (strip + discs); the settling leg then selects L members itself.
Reads every seed of run-j-{waypoints,free,repro-radar,descent-climb} and run-j-joined-v2/{J0011,J2241}."""
import numpy as np, json, glob, os, sys
from multiprocessing import Pool
RJ = os.path.expanduser('~/Downloads/mh370-exchange/end-of-flight')
CX = (-25.732, 101.369)   # bearing x sea-level 7th arc (kadri_geom_output.txt)
HX = (-25.975, 101.461)   # Haixun 01 first contact (ATSB 2017 p.38)
KEEP = ['parent', 'family', 'weight', 't_impact_s', 'latitude_deg', 'longitude_deg', 'velocity_east_mps', 'velocity_north_mps',
        'velocity_up_mps', 'flight_path_angle_deg', 'mass_kg', 'loglik:r600/no-offset', 'loglik:both/no-offset',
        'loglik:both/startup-offset', 'loglik:r600/inflated', 'loglik:r600/startup-offset', 'latent:impact_heading_deg',
        'latent:breakup_p_intact', 'latent:breakup_p_broken', 'latent:breakup_p_fragmented', 'latent:debris_class',
        'bto_residual_us:m0019a', 'latent:recovery_attempted']

def hav(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))

def one(d):
    cols = json.load(open(os.path.join(d, 'run.json')))['impact_columns']
    a = np.load(os.path.join(d, 'impacts32.npy'), mmap_mode='r')
    assert a.shape[1] == len(cols), (d, a.shape, len(cols))
    il, io = cols.index('latitude_deg'), cols.index('longitude_deg')
    idx = [cols.index(k) if k in cols else -1 for k in KEEP]
    out = []; n = a.shape[0]; wsum = 0.0; wcol = cols.index('weight')
    for s in range(0, n, 400_000):
        b = np.asarray(a[s:s + 400_000])
        wsum += float(np.sum(b[:, wcol], dtype=np.float64))
        lat, lon = b[:, il], b[:, io]
        m = (lat > -30.5) & (lat < -21.0) & (lon > 96.0) & (lon < 106.5)
        if not m.any():
            continue
        c = b[m]
        dd = np.minimum(hav(c[:, il], c[:, io], *CX), hav(c[:, il], c[:, io], *HX))
        c = c[dd < 400.0]
        sel = np.full((c.shape[0], len(KEEP)), np.nan, np.float32)
        for j, k in enumerate(idx):
            if k >= 0: sel[:, j] = c[:, k]
        out.append(sel)
    rows = np.concatenate(out) if out else np.zeros((0, len(KEEP)), np.float32)
    return d, n, wsum, rows

if __name__ == '__main__':
    dirs = sorted(glob.glob(RJ + '/run-j/run-j-*/seed-*/')) + sorted(glob.glob(RJ + '/run-j-joined-v2/J*/seed-*/'))
    dirs = [d for d in dirs if os.path.exists(d + 'impacts32.npy')]
    print(len(dirs), 'seed dirs', flush=True)
    res = {}
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as p:
        for d, n, wsum, rows in p.imap_unordered(one, dirs):
            key = d.replace(RJ + '/', '').rstrip('/')
            res[key] = (n, wsum, rows); print(key, n, rows.shape[0], flush=True)
    keys = sorted(res)
    np.savez_compressed('L_rows.npz', keys=np.array(keys), n=np.array([res[k][0] for k in keys]),
                        wsum=np.array([res[k][1] for k in keys]), cols=np.array(KEEP),
                        **{f'r{i}': res[k][2] for i, k in enumerate(keys)})
    print('done')
