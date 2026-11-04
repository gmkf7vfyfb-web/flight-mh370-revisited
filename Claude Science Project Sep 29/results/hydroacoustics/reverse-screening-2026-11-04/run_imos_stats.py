"""Per-record screening statistics for IMOS raw records (S1-S6).
usage: run_imos_stats.py RS_DIR shard N"""
import sys, json, numpy as np, pandas as pd
from pathlib import Path
RS=Path(sys.argv[1]); I,N=int(sys.argv[2]),int(sys.argv[3])
sys.path.insert(0,str(RS/'code'))
import screen_core as SC
lags={tuple(k.split('|')):v for k,v in json.load(open(RS/'cache/s2_lags_imos.json')).items()}
recs=pd.read_csv(RS/'cache/records_meta.csv')
out=RS/'cache/stats_imos'; out.mkdir(exist_ok=True)
for k,r in recs.iterrows():
    if k%N!=I: continue
    fn=out/(Path(r.file).stem+'_'+r.station+'.npz')
    if fn.exists(): continue
    x=np.load(r.path).astype(float)
    E=SC.raw_envelopes(x)
    d={}
    for b,e in E.items():
        o=SC.envelope_stats(e,SC.FS_ENV,lags[(r.station,b)])
        for (det,L),v in o.items():
            for kk,vv in v.items(): d[f'{det}|{L}|{b}|{kk}']=np.asarray(vv,float)
    a=SC.s5(x)
    d['S5|10.0|8-100 Hz|t']=a['t']; d['S5|10.0|8-100 Hz|stat']=a['stat']; d['S5|10.0|8-100 Hz|f_peak']=a['f_peak']
    d['S5|10.0|8-100 Hz|tk']=SC.tk_ratio(x,SC.FS_RAW,a['t'])
    b6=SC.s6(x)
    for kk in ('t','stat','tile_t','tile_f'): d[f'S6|10.0|8-100 Hz|{kk}']=b6[kk]
    d['noise_psd']=b6['noise_psd']
    np.savez_compressed(fn,**d)
