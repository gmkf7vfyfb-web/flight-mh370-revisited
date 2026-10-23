sys.path.insert(0, MODP+'/searches_run_j')
import imos_noise as NN, imos_preregistration as PP
import importlib.util
spec=importlib.util.spec_from_file_location('srch_prereg', MODP+'/searches_run_j/preregistration.py'); SR=importlib.util.module_from_spec(spec); spec.loader.exec_module(SR)
import re
from scipy import signal as sg
print(SR.IMOS_ROOT)
meta=PP.parse_meta(); print({k:{kk:meta[k][kk] for kk in list(meta[k])[:4]} for k in meta})
recs=pd.read_csv(SR.MODULE/'data'/'imos'/'recordings.csv'); recs['logger']=recs.logger.astype(str)
cal=pd.read_csv(SR.RD/'imos1d'/'calibration_gain.csv'); cal['logger']=cal.logger.astype(str)
def subsec(path):
    t=open(path,'rb').read()[-1000:].decode('latin1'); return int(re.search(r"First Data-\S+ \S+ - (\d+)",t).group(1))/65536
_rec_cache={}
def imos_rec(lg, t_utc):
    """return (t_rel_s_after_midnight array, pressure Pa band 5-40 Hz) for the record covering t_utc (s after 00:00), or None"""
    m=meta[lg]; g=cal[cal.logger==lg]; Gd=10*np.log10(np.mean([10**(g[g.band==b].gain_db.iloc[0]/10) for b in ('5-10','10-20','20-40')]))
    div=10**((Gd+m['sens_db'])/10)
    for _,r in recs[recs.logger==lg].iterrows():
        f=SR.IMOS_ROOT/r.file
        key=str(f)
        if key not in _rec_cache:
            fs,first,n,_=PP.header(f); ts=first.timestamp()+subsec(f)-PP.clock_err(m,first)-T0
            _rec_cache[key]=(fs,ts,n)
        fs,ts,n=_rec_cache[key]
        if ts<=t_utc<=ts+n/fs:
            v=NN.read_volts(f); x=v/np.sqrt(div)*1e-6   # Pa
            sos=sg.butter(4,[5,40],btype='band',fs=fs,output='sos'); y=sg.sosfiltfilt(sos,x)
            return ts+np.arange(len(y))/fs, y, fs
    return None
out=imos_rec('3315', hms('01:33:42'))
print(None if out is None else (fmt(out[0][0]), out[2], np.std(out[1])))