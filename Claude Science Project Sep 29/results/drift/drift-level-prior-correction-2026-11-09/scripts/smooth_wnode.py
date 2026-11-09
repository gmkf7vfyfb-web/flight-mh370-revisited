"""Core node weights for the unrelated-debris background: final 7 Nov end of flight, Davey model + fuel, treatment D0, inverse-distance weights of the six nearest release points."""
import sys, numpy as np
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-smooth']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
meta, recs, nenv = load('R3-allcoasts-4periods'); common = sorted(set(recs['globcurrent']) & set(recs['glorys12']))
lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
Z = np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz'); lw = Z['log_weight_D0'].astype(float); hw = np.exp(lw - np.nanmax(lw)); hw = np.where(np.isfinite(hw), hw, 0)
cl, cn = Z['latitude_deg'].astype(float), Z['longitude_deg'].astype(float); m = hw > 0; cl, cn, hw = cl[m], cn[m], hw[m]
nn = np.empty((len(cl), 6), int); W = np.empty((len(cl), 6))
for i in range(0, len(cl), 50000):
    a, b = cl[i:i + 50000], cn[i:i + 50000]; d = np.hypot((b[:, None] - lon[None]) * 111.2 * np.cos(np.radians(a[:, None])), (a[:, None] - lat[None]) * 111.2)
    k = np.argsort(d, 1)[:, :6]; w = 1 / np.maximum(np.take_along_axis(d, k, 1), 1.0) ** 2; nn[i:i + 50000] = k; W[i:i + 50000] = w / w.sum(1, keepdims=True)
p0 = hw / hw.sum(); wn = np.zeros(len(lat)); np.add.at(wn, nn.ravel(), (p0[:, None] * W).ravel()); wn /= wn.sum(); np.save('res-smooth/wnode_df.npy', wn)
print('rows', len(cl), 'wnode sum', wn.sum(), 'max', wn.max(), 'nodes', len(wn))
