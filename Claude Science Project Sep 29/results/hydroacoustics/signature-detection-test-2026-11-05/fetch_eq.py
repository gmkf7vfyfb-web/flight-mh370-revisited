import pandas as pd, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
OUT='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records'
rows=[]
for st,f in [('H01W','bc/out/eq_H01W_events.csv'),('H08S','bc/out/eq_H08S_events.csv')]:
    d=pd.read_csv(f); d=d[d.status=='ok']
    for _,r in d.iterrows(): rows.append((st,r.evid,r.t_pred))
print(len(rows), flush=True)
def get(a):
    st,evid,tp=a; fn=f'{OUT}/{st}1_{evid}.mseed'
    if os.path.exists(fn): return (st,evid,'cached')
    t=UTCDateTime(tp)
    for k in range(3):
        try:
            s=Client('IRIS',timeout=120).get_waveforms('IM',st+'1','*','EDH',t-1200,t+1200)
            s.write(fn,format='MSEED'); return (st,evid,'ok')
        except Exception as e:
            err=str(e)[:80]; time.sleep(3)
    return (st,evid,'fail:'+err)
with ThreadPoolExecutor(5) as ex: res=list(ex.map(get,rows))
r=pd.DataFrame(res,columns=['station','evid','status']); r.to_csv(OUT+'/fetch_log.csv',index=False)
print(r.status.str[:4].value_counts())
