import pandas as pd, numpy as np, os, time
from concurrent.futures import ThreadPoolExecutor
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
OUT='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'; os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(20261105)
ranges={'H01W':(UTCDateTime('2015-01-01'),UTCDateTime('2019-07-01')),'H08S':(UTCDateTime('2015-01-01'),UTCDateTime('2025-06-01'))}
rows=[]
for st,(a,b) in ranges.items():
    for k in range(190):
        t=UTCDateTime(int(a.timestamp+rng.uniform(0,b-a)))
        rows.append((st,f'rnd{k:03d}',t))
def get(r):
    st,name,t=r; fn=f'{OUT}/{st}1_{name}.mseed'
    if os.path.exists(fn): return (st,name,str(t),'cached')
    for k in range(3):
        try:
            s=Client('EARTHSCOPE',timeout=120).get_waveforms('IM',st+'1','*','EDH',t,t+2400); s.write(fn,format='MSEED'); return (st,name,str(t),'ok')
        except Exception as e:
            err=str(e)[:60]
            if 'No data' in err or '204' in err: break
            time.sleep(3)
    return (st,name,str(t),'fail:'+err)
with ThreadPoolExecutor(5) as ex: res=list(ex.map(get,rows))
r=pd.DataFrame(res,columns=['station','name','t0','status']); r.to_csv(OUT+'/fetch_log.csv',index=False)
print(r.groupby('station').status.apply(lambda s:s.str[:4].value_counts()))
