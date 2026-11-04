import sys, numpy as np, pandas as pd
from pathlib import Path
RS=Path(sys.argv[1]); I,N=int(sys.argv[2]),int(sys.argv[3])
sys.path.insert(0,str(RS/'code'))
import screen_core as SC
recs=pd.read_csv(RS/'cache/records_meta.csv'); out=RS/'cache/stats_s6'; out.mkdir(exist_ok=True)
for k,r in recs.iterrows():
    if k%N!=I: continue
    fn=out/(Path(r.file).stem+'_'+r.station+'.npz')
    if fn.exists(): continue
    b6=SC.s6(np.load(r.path).astype(float))
    np.savez_compressed(fn,**{f'S6|10.0|8-100 Hz|{kk}':b6[kk] for kk in ('t','stat','tile_t','tile_f')},noise_psd=b6['noise_psd'])
