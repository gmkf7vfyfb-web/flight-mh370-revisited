"""Score known-flight runs without using truth in their likelihoods."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter, map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core import *

ROOT=Path(__file__).resolve().parent

def main():
    truth=pd.read_csv(ROOT/'inputs/withheld_known_state_diagnostic.csv');rows=[]
    for run in sorted((ROOT/'runs').glob('mh371_*')):
        for i,path in enumerate(sorted(run.glob('weighted_*.npz'))):
            with np.load(path,allow_pickle=False) as z:
                lat=z['lat'];lon=z['lon'];w=np.exp(z['logw']);roots=z['root']
            tr=truth.iloc[i];cos=np.cos(np.radians(tr.truth_lat));x=(lon-tr.truth_lon)*111.32*cos;y=(lat-tr.truth_lat)*111.2
            bx=np.arange(np.floor(x.min()/10)*10-100,np.ceil(x.max()/10)*10+111,10);by=np.arange(np.floor(y.min()/10)*10-100,np.ceil(y.max()/10)*10+111,10)
            hist,_,_=np.histogram2d(y,x,bins=(by,bx),weights=w)
            for bandwidth in [10,25,50]:
                d=gaussian_filter(hist,bandwidth/10);d/=d.sum()
                loc=[(0-by[0])/10-.5,(0-bx[0])/10-.5]
                at=float(map_coordinates(d,np.array(loc)[:,None],order=1,mode='constant')[0])
                hpd=float(d[d>=at].sum());j,k=np.unravel_index(np.argmax(d),d.shape)
                rows.append({'run':run.name,'observation':i+1,'bandwidth_km':bandwidth,'truth_hpd_rank':hpd,'mass_within_100km':float(w[np.hypot(x,y)<100].sum()),'mode_error_km':float(np.hypot((bx[k]+bx[k+1])/2,(by[j]+by[j+1])/2)),'roots':len(np.unique(roots))})
    frame=pd.DataFrame(rows);out=ROOT/'assessment';out.mkdir(exist_ok=True);frame.to_csv(out/'mh371_validation.csv',index=False)
    last=frame[(frame.observation==8)&(frame.bandwidth_km==25)]
    print(last.to_string(index=False))
    fig,ax=plt.subplots(figsize=(10,5))
    for run,g in frame[frame.bandwidth_km==25].groupby('run'):
        ax.plot(g.observation,g.truth_hpd_rank,'o-',label=run.replace('mh371_',''))
    ax.axhline(.95,ls=':',color='gray');ax.set(xlabel='SATCOM update',ylabel='Truth HPD rank (25 km smoothing)',ylim=(0,1.02),title='MH371 reconstructed-v12 validation — lower rank places truth in denser region')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'mh371_truth_hpd.png',dpi=170);plt.close(fig)

if __name__=='__main__':main()
