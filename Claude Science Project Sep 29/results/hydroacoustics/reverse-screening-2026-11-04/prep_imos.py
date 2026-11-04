"""Decimate IMOS raw 6 kHz records to 500 Hz (spec section 2.3) and cache them.
Event day: every record of 8 Mar 2014 (N1 and the arrival windows).
Background: 1-14 Mar 2014 records whose clock time lies within the station's
union arrival window +/- 2 h (N2)."""
import sqlite3, numpy as np, pandas as pd, os, sys, json, hashlib
from pathlib import Path
from scipy import signal
import concurrent.futures as cf
DB=os.environ['HYDRO_DB']   # path to hydro_data.sqlite (artifact store)
INPUTS=os.environ.get('HYDRO_INPUTS',os.path.expanduser('~/Downloads/mh370-inputs/hydroacoustics/'))
OUT=Path(sys.argv[1]); AW=pd.read_csv(sys.argv[2])
AW=AW[AW.subset=='unblocked grid points'].set_index('station')
def read_volts(path):
    raw=Path(path).read_bytes(); pos=0
    for _ in range(5): pos=raw.index(b'\n',pos)+1
    tail=raw[-1000:]; fb=1000-tail.index(b'Record'); end=len(raw)-fb-2
    n=(end-pos)//2
    x=np.frombuffer(raw,dtype='>u2',count=n,offset=pos).astype(np.float64)*(5.0/65536)
    return x-x.mean(), hashlib.sha256(raw).hexdigest()
con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
seg=pd.read_sql("select dataset_id,label,t_start_utc,duration_s,clock_err_s,sample_rate_hz,n_samples,file_path,sha256 from segment where dataset_id like 'imos3%'",con)
seg['station']=seg.dataset_id.str.extract(r'(imos\d+)')[0].str.upper()
seg['kind']=np.where(seg.dataset_id.str.contains('background'),'background','eventday')
seg['t0']=pd.to_datetime(seg.t_start_utc,utc=True)
rows=[]
for _,r in seg.iterrows():
    if r.kind=='eventday': rows.append(r); continue
    lo,hi=AW.loc[r.station,'earliest_s']-7200-60, AW.loc[r.station,'latest_s']+7200+60
    tod=(r.t0-r.t0.normalize()).total_seconds()
    tods=[tod,tod-86400,tod+86400]
    if any(lo-r.duration_s<=x<=hi for x in tods): rows.append(r)
sel=pd.DataFrame(rows)
print(sel.groupby(['station','kind']).size().to_string(),flush=True)
def work(r):
    st=r['station']; d=OUT/st; d.mkdir(parents=True,exist_ok=True)
    fn=d/f"{r['kind']}_{r['t0'].strftime('%Y%m%dT%H%M%S')}_{r['label'].replace('.DAT','')}.npy"
    if fn.exists(): return str(fn),'have',''
    p=r['file_path'].replace('INPUTS:',INPUTS)
    try:
        x,h=read_volts(p)
    except Exception as e:
        return str(fn),'readfail',str(e)
    y=signal.resample_poly(x,1,12).astype(np.float32)
    np.save(fn,y)
    return str(fn),'ok' if h==r['sha256'] else 'shamismatch',''
recs=sel.to_dict('records')
I,N=int(sys.argv[3]),int(sys.argv[4])
if I>=0:
    for k,r in enumerate(recs):
        if k%N==I: work(r)
    sys.exit(0)
res=[work(r) for r in recs]
meta=sel[['station','kind','label','t_start_utc','duration_s','clock_err_s','n_samples','sha256']].copy()
meta['file']=[r[0] for r in res]; meta['status']=[r[1] for r in res]; meta['err']=[r[2] for r in res]
meta.to_csv(OUT/'records.csv',index=False)
print(meta.groupby(['station','kind','status']).size().to_string())
