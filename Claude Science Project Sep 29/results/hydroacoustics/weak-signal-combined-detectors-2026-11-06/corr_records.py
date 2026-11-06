import sys, os, glob, numpy as np
sys.path.insert(0, os.getcwd())
import sigdet as SD, sigcorr as SC
from score_records import load, SCALE
from multiprocessing import Pool
RB='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'
os.makedirs('corr_rnd',exist_ok=True); os.makedirs('corr_gauss',exist_ok=True); os.makedirs('scores_gauss',exist_ok=True)
WT=SD.whale_templates()
def run(fn):
    k=os.path.basename(fn)[:-6]; st=k[:4]; o=f'corr_rnd/{k}.npz'
    if os.path.exists(o): return k
    t0,x=load(fn,st)
    c=np.arange(330.0,len(x)/SD.FS-330.0,5.0)
    z=SC.local_lags(x,c); Wb=SC.record_bank(x)
    y=SC.envelope_db(x); tau=SC.thin_lag(y); pe=SC.persistence(y,c,tau)
    np.savez_compressed(o,c=c,z=z.astype(np.float32),Wb=Wb.astype(np.float32),gapfrac=np.mean(x==0),pe=pe,tau=tau)
    return k
def gauss(args):
    st,i=args; o=f'corr_gauss/{st}1_g{i:03d}.npz'
    if os.path.exists(o): return o
    rng=np.random.default_rng(1000*(st=='H08S')+i)
    Nmed=np.median([np.load(f)['Nmed'] for f in sorted(glob.glob(f'scores_rnd/{st}1_*.npz'))[:60]],0)
    n=int(2400*SD.FS); f=np.fft.rfftfreq(n,1/SD.FS)
    amp=np.sqrt(np.interp(f,SD.F,Nmed))
    x=np.fft.irfft(np.fft.rfft(rng.standard_normal(n))*amp,n)
    t,P,N,S,Ss=SD.all_scores(x,wt=WT); C=SD.combine(S); Cs=SD.combine(Ss)
    np.savez_compressed(f'scores_gauss/{st}1_g{i:03d}.npz',t=t,start='1970-01-01T00:00:00',gap=np.zeros(len(t),bool),Nmed=np.median(N,1),
        **{k:v.astype(np.float32) for k,v in C.items() if k!='winner' and not k.startswith('c_')},winner=C['winner'].astype(np.int8),
        **{'cls_'+k:SD.lag_max(v,40).astype(np.float32) for k,v in S.items() if k!='d0'},
        **{'s_'+k:v.astype(np.float32) for k,v in Cs.items() if k not in ('winner','d0') and not k.startswith('c_')},s_winner=Cs['winner'].astype(np.int8),
        **{'scls_'+k:SD.lag_max(v,40).astype(np.float32) for k,v in Ss.items() if k!='d0'})
    c=np.arange(330.0,2400-330.0,5.0); z=SC.local_lags(x,c); Wb=SC.record_bank(x)
    y=SC.envelope_db(x); tau=SC.thin_lag(y); pe=SC.persistence(y,c,tau)
    np.savez_compressed(o,c=c,z=z.astype(np.float32),Wb=Wb.astype(np.float32),gapfrac=0.0,pe=pe,tau=tau)
    return o
if __name__=='__main__':
    fs=sorted(glob.glob(RB+'/*.mseed'))
    with Pool(16) as p:
        r1=p.map(run,fs,chunksize=2)
        r2=p.map(gauss,[(st,i) for st in ('H01W','H08S') for i in range(60)],chunksize=2)
    print(len(r1),len(r2))
