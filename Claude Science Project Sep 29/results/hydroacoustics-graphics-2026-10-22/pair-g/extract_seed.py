"""Per-seed extraction for the pair-G graphics (run J waypoints stratum, 00:19 Held Out D0', p = 0.5).
Weights: run_j_windows.ln_weights(...,'D0') x p_factor(0.5) (module re-implementation of EoF's two-factor table).
Outputs work/seed-K.npz: per-parent sums (all, within 150 km of G) and the rows within 300 km of G."""
import sys, json, pathlib, numpy as np, time
PREP = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(PREP))
import run_j_windows as W
GLAT, GLON = -33.564949768575076, 94.50869477928312
EOF = pathlib.Path('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints')
def hav(lat, lon, la, lo):
    p1, p2 = np.radians(lat), np.radians(la); dl = np.radians(lo - lon)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))
def run(k):
    t0 = time.time(); sd = EOF / f'seed-{k}'
    g, meta, n = W.load_seed(sd)
    logon = meta['config']['hypotheses']['end-of-flight']['logon']
    lnw = W.ln_weights(g, logon, 'D0')
    w = np.exp(np.where(np.isfinite(lnw), lnw, -np.inf)); w[~np.isfinite(w)] = 0.0
    w = w * W.p_factor(g, 0.5)
    par = g('parent').astype(np.int64); lat, lon = g('latitude_deg'), g('longitude_deg')
    d = hav(lat, lon, GLAT, GLON); npar = int(par.max()) + 1
    Wp = np.bincount(par, w, npar); W150 = np.bincount(par, w * (d < 150), npar)
    sel = d < 300
    cols = ['t_impact_s', 't_takeover_s', 't_onset_s', 't_realised_flameout_s', 'takeover_latitude_deg', 'takeover_longitude_deg',
            'takeover_altitude_ft', 'family4_code', 'latent:last_burst_latitude_deg', 'latent:last_burst_longitude_deg',
            'latent:impact_heading_deg', 'latent:max_descent_rate_fpm', 'flight_path_angle_deg']
    cn = (sd / 'COLUMNS.txt').read_text().split(); X = np.load(sd / 'impacts32.npy', mmap_mode='r'); ci = {c: i for i, c in enumerate(cn)}
    keep = {c.replace('latent:', '').replace(':', '_'): np.asarray(X[sel, ci[c]], dtype=np.float64) for c in cols}
    np.savez_compressed(f'work/seed-{k}.npz', Wp=Wp, W150=W150, wsum=w.sum(), n=n, row=np.nonzero(sel)[0], parent=par[sel], w=w[sel],
                        lat=lat[sel], lon=lon[sel], d=d[sel], **keep)
    return k, n, float(w.sum()), int(sel.sum()), time.time() - t0
if __name__ == '__main__':
    import os
    from multiprocessing import Pool
    ks = [int(x) for x in sys.argv[2].split(',')]
    with Pool(int(sys.argv[3])) as p:
        for r in p.imap_unordered(run, ks): print(r, flush=True)
