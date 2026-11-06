import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
import sigdet as SD, sigcorr as SC
from score_records import load
from multiprocessing import Pool
RB='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'
def addpe(fn):
    z=dict(np.load(fn)); k=os.path.basename(fn)[:-4]; st=k[:4]
    if 'corr_rnd' in fn: _,x=load(f'{RB}/{k}.mseed',st)
    else:
        i=int(k.split('_g')[1]); rng=np.random.default_rng(1000*(st=='H08S')+i)
        Nmed=np.median([np.load(f)['Nmed'] for f in sorted(glob.glob(f'scores_rnd/{st}1_*.npz'))[:60]],0)
        n=int(2400*SD.FS); f=np.fft.rfftfreq(n,1/SD.FS); x=np.fft.irfft(np.fft.rfft(rng.standard_normal(n))*np.sqrt(np.interp(f,SD.F,Nmed)),n)
    y=SC.envelope_db(x); tau=SC.TAU[st]; z['pe']=SC.persistence(y,z['c'],tau); z['tau']=tau
    np.savez_compressed(fn,**z)
if __name__=='__main__':
    fs=sorted(glob.glob('corr_rnd/*.npz')+glob.glob('corr_gauss/*.npz'))
    with Pool(16) as p: p.map(addpe,fs,chunksize=4)
    norm={}
    for kind in ('rnd','gauss'):
        for st in ('H01W','H08S'):
            Z=np.concatenate([np.load(f)['z'] for f in glob.glob(f'corr_{kind}/{st}1_*.npz')])
            Z=Z[np.isfinite(Z).all(1)]
            norm[f'{st}_mu' if kind=='rnd' else f'g{st}_mu']=np.median(Z,0)
            norm[f'{st}_sd' if kind=='rnd' else f'g{st}_sd']=1.4826*np.median(np.abs(Z-np.median(Z,0)),0)
            print(kind,st,'lag1 mu',norm[(f'{st}' if kind=='rnd' else f'g{st}')+'_mu'][0].round(2),'sd med',np.median(norm[(f'{st}' if kind=='rnd' else f'g{st}')+'_sd']).round(2))
    np.savez('corr_norm.npz',**norm)
    # background looks (2 min blocks) for corr stats, real and gauss
    rows=[]
    for kind in ('rnd','gauss'):
        for fn in sorted(glob.glob(f'corr_{kind}/*.npz')):
            z=np.load(fn); st=os.path.basename(fn)[:4]; pre='' if kind=='rnd' else 'g'
            za,zi=SC.corr_stats(z['z'],norm[pre+st+'_mu'],norm[pre+st+'_sd'],z['Wb'])
            c=z['c']; pe=z['pe']
            for b0 in np.arange(c[0],c[-1]-120,120.0):
                m=(c>=b0)&(c<b0+120)
                if m.sum()<20 or not np.isfinite(za[m]).all(): continue
                rows.append(dict(kind=kind,st=st,rec=os.path.basename(fn)[:-4],b0=b0,C_any=za[m].max(),C_imp=zi[m].max(),E_pers=np.nanmax(pe[m])))
    B=pd.DataFrame(rows); B.to_csv('corr_background_looks.csv',index=False)
    print(B.groupby(['kind','st'])[['C_any','C_imp','E_pers']].quantile([0.5,0.95,1-1/720]).round(2))
