"""Plot actual weighted filter outputs; no fitted proposal enters the filter."""
from pathlib import Path
import os,json,itertools
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'assessment'/'mpl-cache'))
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.stats import wasserstein_distance
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EDGES=np.linspace(-90,90,3601)
GRID=(EDGES[1:]+EDGES[:-1])/2
BW=.35

def read(path):
    with np.load(path,allow_pickle=False) as z:
        lat=z['lat'];w=np.exp(z['logw']);roots=z['root']
        meta=json.loads(str(z['metadata']))
    w/=w.sum()
    return lat,w,roots,meta

def density(lat,w):
    h=np.histogram(lat,bins=EDGES,weights=w)[0]
    return gaussian_filter1d(h,BW/(EDGES[1]-EDGES[0]),mode='constant')/(EDGES[1]-EDGES[0])

def quantiles(lat,w):
    i=np.argsort(lat)
    return np.interp([.025,.5,.975],np.cumsum(w[i]),lat[i]).tolist()

def main():
    out=ROOT/'assessment';out.mkdir(exist_ok=True)
    rows=[];curves={'latitude_deg':GRID};groups={};comparisons=[]
    for run in sorted((ROOT/'runs').glob('mh370_*')):
        manifest=json.loads((run/'manifest.json').read_text())
        if manifest['status']!='completed':continue
        kind='BTO+BFO' if manifest['configuration']['use_bfo'] else 'BTO only'
        for epoch,index in [('00:11',10),('00:19',12)]:
            lat,w,roots,meta=read(run/f'weighted_{index:02d}.npz')
            pdf=density(lat,w);curves[f'{run.name}_{epoch}']=pdf
            group=groups.setdefault((epoch,kind),[]);group.append((run.name,lat,w,pdf))
            _,inverse=np.unique(roots,return_inverse=True)
            rootw=np.bincount(inverse,weights=w)
            rows.append({'run':run.name,'epoch':epoch,'kind':kind,'quantiles_025_50_975':quantiles(lat,w),'south_probability':float(w[lat<0].sum()),'mode_latitude_smoothed':float(GRID[np.argmax(pdf)]),'ess':float(1/np.sum(w*w)),'unique_roots':len(rootw),'effective_roots':float(1/np.sum(rootw**2)),'largest_root_weight':float(rootw.max()),'bandwidth_deg':BW})
    if not groups:raise RuntimeError('No completed accident runs yet')
    for (epoch,kind),runs in groups.items():
        for a,b in itertools.combinations(runs,2):
            cdfa=np.cumsum(a[3])*.05;cdfb=np.cumsum(b[3])*.05
            comparisons.append({'epoch':epoch,'kind':kind,'a':a[0],'b':b[0],'wasserstein_deg':float(wasserstein_distance(a[1],b[1],a[2],b[2])),'smoothed_cdf_max_difference':float(np.max(abs(cdfa-cdfb))),'smoothed_total_variation':float(np.sum(abs(a[3]-b[3]))*.025)})
    colors={'BTO only':'#2166ac','BTO+BFO':'#b2182b'}
    fig,axes=plt.subplots(2,1,figsize=(11,8))
    fig.suptitle('Numerical diagnostic — convergence not established',fontsize=11,color='#8c3b13')
    for ax,zoom in zip(axes,[False,True]):
        for kind in colors:
            runs=groups.get(('00:19',kind),[])
            for i,(name,lat,w,pdf) in enumerate(runs):
                ax.plot(GRID,pdf,color=colors[kind],ls=['-','--',':','-.'][i%4],lw=1.8,label=f'{kind}, N={int(name.split("_")[2]):,}, seed {name.split("_")[3]}')
        ax.set(xlim=(-45,-15) if zoom else (-60,60),xlabel='Latitude (degrees; negative = south)',ylabel='Probability density per degree')
        ax.grid(alpha=.2);ax.legend(fontsize=9)
        ax.set_title('Southern detail — density retains full-distribution normalization' if zoom else '00:19 airborne latitude — reconstructed Davey model with ERA5')
    fig.text(.5,.012,'Separate seeds expose Monte Carlo variation. Gaussian display bandwidth 0.35°. No power/gain, drift or terminal BFO likelihood.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.025,1,.96));fig.savefig(out/'mh370_fig10_3_analogue.png',dpi=200);plt.close(fig)
    comparator=ROOT/'evidence/refined_summary_samples.csv'
    if comparator.exists():
        frame=pd.read_csv(comparator);lat=frame.loc[frame.posterior=='without_ocean_drift','lat_deg'].to_numpy()
        refined=density(lat,np.full(len(lat),1/len(lat)));curves['refined_summary_reconstruction_00:11']=refined
        fig,ax=plt.subplots(figsize=(11,5.5))
        for i,(name,lat,w,pdf) in enumerate(groups.get(('00:11','BTO+BFO'),[])):
            ax.plot(GRID,pdf,color=colors['BTO+BFO'],ls=['-','--',':','-.'][i%4],label=f'Davey/ERA5 BTO+BFO, N={int(name.split("_")[2]):,}, seed {name.split("_")[3]}')
        ax.plot(GRID,refined,color='#333333',lw=2,label='Later refined output: summary-reconstructed proposal, no drift')
        ax.set(xlim=(-45,-15),xlabel='Latitude (degrees; negative = south)',ylabel='Probability density per degree',title='Same-epoch 00:11 comparison — different evidence and BFO models')
        ax.grid(alpha=.2);ax.legend(fontsize=9)
        fig.text(.5,.015,'Refined curve is not the missing historical particle checkpoint. Its northern mixture components were reconstructed from summaries.',ha='center',fontsize=8)
        fig.tight_layout(rect=(0,.035,1,1));fig.savefig(out/'mh370_refined_comparison_0011.png',dpi=200);plt.close(fig)
    pd.DataFrame(curves).to_csv(out/'latitude_pdfs.csv',index=False)
    (out/'posterior_summary.json').write_text(json.dumps({'runs':rows,'between_run_comparisons':comparisons},indent=2))
    print(json.dumps({'runs':rows,'between_run_comparisons':comparisons},indent=2))

if __name__=='__main__':main()
