cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && python3 -c "
import numpy as np, json
cols=json.load(open('next-i-free/seed-1/run.json'))['impact_columns']
ix={c:i for i,c in enumerate(cols)}
a=np.load('next-i-free/seed-1/impacts32.npy',mmap_mode='r')[:200000]
import itertools
for c in ['weight','loglik:r600/no-offset','loglik:both/startup-offset','latent:impact_energy_transferred_j','latent:energy_transfer_tau90_s','latent:energy_transfer_peak_rate_w','latent:impact_tau_method','velocity_up_mps','flight_path_angle_deg']:
    v=np.asarray(a[:,ix[c]],dtype=np.float64)
    fin=np.isfinite(v)
    print(f'{c:42s} finite={fin.mean():.3f} min={np.nanmin(v):.4g} med={np.nanmedian(v):.4g} max={np.nanmax(v):.4g} nzero={(v==0).mean():.3f}')
z=np.load('next-i-free/seed-1/tau90_v1.npz')
for k in ['tau90_s','peak_rate_w','energy_transferred_j','decel_g']:
    v=z[k][:200000].astype(np.float64); print('npz',k, 'finite',np.isfinite(v).mean(), 'med',np.nanmedian(v), 'max',np.nanmax(v))
print('method',z['method'],'note',str(z['note'])[:300])
import glob; print('tau90 present in', len(glob.glob('*/seed-*/tau90_v1.npz')),'of',len(glob.glob('*/seed-*/impacts32.npy')))
"