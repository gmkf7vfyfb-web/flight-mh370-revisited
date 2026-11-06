import sys, os, sqlite3, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.getcwd(),'ns'))
from scipy import signal
from multiprocessing import Pool
import ns_readers as RD
OUT='/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos_250hz_cache'; os.makedirs(OUT,exist_ok=True)
NS=76700   # 306.8 s at 250 Hz
con=sqlite3.connect(f'file:{RD.DB}?mode=ro',uri=True)
seg=pd.read_sql("select dataset_id,label,t_start_utc,duration_s,file_path from segment where dataset_id like 'imos3%'",con)
seg['t_start_s']=RD.to_s(seg.t_start_utc); seg['path']=seg.file_path.str.replace('INPUTS:',str(RD.INPUTS)+'/',regex=False)
def one(r):
    try:
        x=RD.read_volts(r['path']); y=signal.resample_poly(x,1,24).astype(np.float32)
        z=np.zeros(NS,np.float32); n=min(NS,len(y)); z[:n]=y[:n]; return z, n
    except Exception as e:
        return np.zeros(NS,np.float32), 0
if __name__=='__main__':
    for ds,g in seg.groupby('dataset_id'):
        fn=f'{OUT}/{ds}.npz'
        if os.path.exists(fn): continue
        g=g.sort_values('t_start_s'); rows=g.to_dict('records')
        with Pool(16) as p: res=p.map(one,rows,chunksize=8)
        X=np.stack([a for a,_ in res]); nn=np.array([b for _,b in res])
        np.savez(fn,x=X,n=nn,t_start_s=g.t_start_s.values,label=g.label.values.astype(str))
        print(ds,X.shape,'bad',(nn<NS*0.95).sum(),flush=True)
