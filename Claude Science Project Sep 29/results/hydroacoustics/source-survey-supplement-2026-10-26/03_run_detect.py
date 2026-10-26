"""Run detect.py over every station with 5 day files (6-10 Mar 2014). Writes data/det/<sta>.csv and
data/det/<sta>_snr.npz (1-s SNR series per band, used for background statistics and figures)."""
import sys, glob, os, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import detect
from concurrent.futures import ThreadPoolExecutor
from obspy import UTCDateTime as U
os.makedirs('data/det',exist_ok=True)
T0,T1=U('2014-03-06T00:00:00'),U('2014-03-11T00:00:00')
keys=sorted(set('.'.join(os.path.basename(f).split('.')[:4]) for f in glob.glob('data/raw/*.mseed') if len(os.path.basename(f).split('.'))==6))
only=sys.argv[1:]
def run(k):
    net,sta,loc,cha=k.split('.'); key=f'{net}.{sta}'
    if only and key not in only: return f'{k} skipped'
    if os.path.exists(f'data/det/{key}.csv'): return f'{k} done before'
    files=sorted(glob.glob(f'data/raw/{k}.*.mseed'))
    try:
        tr,mask=detect.load(files,f'data/resp/{key}.xml',T0,T1)
        out=[]; snrs={}
        for b in detect.BANDS:
            d,s=detect.detect(tr,mask,b)
            if d is None: continue
            d.insert(0,'station',key); d.insert(1,'channel',f'{loc}.{cha}'); d.insert(2,'fs_hz',tr.stats.sampling_rate); out.append(d); snrs[b]=s[0].astype(np.float32); t0=s[1]
        D=pd.concat(out,ignore_index=True); D.to_csv(f'data/det/{key}.csv',index=False)
        np.savez_compressed(f'data/det/{key}_snr.npz',t0=t0,gapfrac=float(mask.mean()),**{('b'+b.replace('-','_')):v for b,v in snrs.items()})
        return f'{k} n={len(D)} files={len(files)} gapfrac={mask.mean():.4f} fs={tr.stats.sampling_rate}'
    except Exception as e:
        return f'{k} ERROR {type(e).__name__} {e}'
with ThreadPoolExecutor(5) as ex:
    for r in ex.map(run,keys): print(r,flush=True)
