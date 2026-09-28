from pathlib import Path
import os,json
B=Path(__file__).resolve().parent;R=B.parent/'reverse_drift_v1';P=B.parent/'combined_panel_versions'
os.environ['MPLCONFIGDIR']=str(B/'mpl_cache')
import numpy as np,pandas as pd
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.stats import qmc
from matplotlib.path import Path as MPath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
G=pd.read_csv(B/'source_grid.csv');A=G.cellAreaKm2.to_numpy();N=len(G);shape=(129,71)
X=G.longitude.to_numpy().reshape(shape);Y=G.latitude.to_numpy().reshape(shape)
base=np.load(B/'base_input.npz')['equal_models__combined50_french4_21'];assert abs(base.sum()-1)<1e-12
fs=json.loads((B/'search_footprints.geojson').read_text())['features'];fd={f['properties']['id']:f for f in fs}
ids=['atsb_phase2_2014_2017','oi2018_total_outline_approx','oi2024_proposed_outboard_southeast','oi2024_proposed_inboard_northwest']
mask=np.asarray(Image.open(B/'atsb_phase2_coverage_mask_z8.png'));print('mask',mask.shape,flush=True)
if mask.ndim==3:mask=mask[:,:,0]
def subfractions(n):
 u=(np.arange(n)+.5)/n
 ai=G.alongIndex.to_numpy();ci=G.crossIndex.to_numpy()
 loA=np.where(ai==0,0,-.5);hiA=np.where(ai==128,0,.5);loC=np.where(ci==0,0,-.5);hiC=np.where(ci==70,0,.5)
 counts=np.zeros((N,16));fut=np.zeros(N)
 for v in u:
  aa=ai[:,None]+loA[:,None]+(hiA-loA)[:,None]*v
  cc=ci[:,None]+loC[:,None]+(hiC-loC)[:,None]*u[None,:]
  aa=np.broadcast_to(aa,cc.shape);coord=np.array([aa.ravel(),cc.ravel()])
  lon=map_coordinates(X,coord,order=1,mode='nearest');lat=map_coordinates(Y,coord,order=1,mode='nearest');pts=np.column_stack([lon,lat])
  px=np.floor((lon+180)/360*65536).astype(int)-47872;py=np.floor((1-np.arcsinh(np.tan(np.radians(lat)))/np.pi)/2*65536).astype(int)-36864
  valid=(px>=0)&(px<mask.shape[1])&(py>=0)&(py<mask.shape[0]);a=np.zeros(len(lon),bool);a[valid]=mask[py[valid],px[valid]]>0
  code=a.astype(np.uint8)
  for k,key in enumerate(ids[1:],1):code |= MPath(np.array(fd[key]['geometry']['coordinates'][0])).contains_points(pts).astype(np.uint8)*(2**k)
  for k in range(16):counts[:,k]+=(code.reshape(N,n)==k).sum(axis=1)
 return counts/n**2
# Subcell integration avoids treating coarse 5 NM cells as wholly searched.
f10=subfractions(10);F=subfractions(20);assert np.allclose(F.sum(axis=1),1)
np.savez_compressed(B/'coverage_pattern_fractions.npz',fractions_20=F,fractions_10=f10)
bits=((np.arange(16)[:,None]>>np.arange(4))&1).astype(float)
rng=qmc.Sobol(5,scramble=True,seed=3702026).random_base2(13)
# Explicit sensitivity distributions, NOT estimated campaign performance posteriors.
qa=.90+.09*rng[:,0];c18=.60+.35*rng[:,1];q18=.85+.14*rng[:,2];c25=.50+.45*rng[:,3];q25=.85+.14*rng[:,4]
eff=np.column_stack([qa,c18*q18,c25*q25])
def pat(e,ind=False):
 v=e[:,None,:]*bits[None,:,:3]
 return np.prod(1-v,axis=2) if ind else 1-v.max(axis=2)
# Strong dependence: nested detection events; independent: conditional product.
lik={'original':np.ones(16),'ATSB_only':1-.945*bits[:,0],
 'marginal_dependent':pat(eff).mean(axis=0),'marginal_independent':pat(eff,True).mean(axis=0),
 'weak_dependent':pat(np.array([[.90,.60*.85,.50*.85]]))[0],
 'strong_dependent':pat(np.array([[.99,.95*.99,.95*.99]]))[0]}
outside=bits[:,:3].sum(axis=1)==0
pdfs={};rows=[]
for name,l in lik.items():
 cellL=F@l;z=float(base@cellL);mass=base*cellL/z;pdfs[name]=mass
 density=mass/A;order=np.argsort(-density);cs=np.cumsum(mass[order]);r={'scenario':name,'no_detection_predictive':z,'mean_lat':float(mass@G.latitude),'mean_lon':float(mass@G.longitude),'mode_lat':float(G.latitude.iloc[density.argmax()]),'mode_lon':float(G.longitude.iloc[density.argmax()]),'outside_envelopes_mass':float(np.sum(base*(F@(l*outside)))/z),'possible_next_band_mass':float(np.sum(base*(F@(l*bits[:,3])))/z),'west_of_91E_mass':float(mass[G.longitude<91].sum())}
 for q in [.5,.9,.95]:
  k=np.searchsorted(cs,q);r[f'hpd{int(q*100)}_km2']=float(A[order[:k+1]].sum());r[f'hpd{int(q*100)}_threshold']=float(density[order[k]])
 rows.append(r)
S=pd.DataFrame(rows);S.to_csv(B/'summary.csv',index=False);np.savez_compressed(B/'residual_pdfs.npz',**pdfs)
T=G.copy()
for name,m in pdfs.items():T[name+'_mass']=m
for k,key in enumerate(ids):T[key+'_fraction']=F@bits[:,k]
T.to_csv(B/'cell_probabilities.csv.gz',index=False)
coverage={key:float(base@(F@bits[:,k])) for k,key in enumerate(ids)}
coverage['union_past_envelopes']=float(base@(F@(~outside)))
old=S.iloc[0];high=(base/A)>=old.hpd50_threshold
coverage['past_envelope_overlap_fraction_of_original_50pct_HPD_mass']=float((base*(F@(~outside)))[high].sum()/base[high].sum())
check={}
for name in ['marginal_dependent','marginal_independent']:
 m=base*(f10@lik[name]);m/=m.sum();check[name+'_10_vs_20_subcell_TV']=float(abs(m-pdfs[name]).sum()/2)
 l=pat(eff[:4096],name.endswith('independent')).mean(axis=0);m=base*(F@l);m/=m.sum();check[name+'_4096_vs_8192_parameter_TV']=float(abs(m-pdfs[name]).sum()/2)
assert max(check.values())<.01
(B/'validation.json').write_text(json.dumps({'coverage_mass_before_search':coverage,'numerical_checks':check,'probability_sums':{k:float(v.sum()) for k,v in pdfs.items()},'parameters':{'ATSB_q':[.9,.99],'OI2018_coverage':[.6,.95],'OI2018_q':[.85,.99],'OI2025_coverage':[.5,.95],'OI2025_q':[.85,.99]},'samples':8192,'seed':3702026},indent=2))
print(S.to_string(index=False));print(json.dumps(coverage,indent=2));print(check)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
arc=np.array(json.loads((B/'seventh_arc_fl400.geojson').read_text())['features'][0]['geometry']['coordinates'])
fig,axs=plt.subplots(1,3,figsize=(18,8.8));fig.subplots_adjust(left=.05,right=.90,bottom=.24,top=.83,wspace=.22)
names=['original','marginal_dependent','marginal_independent'];titles=['Before search evidence','After search: dependent misses','After search: independent misses']
vmax=max((pdfs[k]/A).max() for k in names)
for ax,name,title in zip(axs,names,titles):
 m=pdfs[name];d=m/A;r=S[S.scenario==name].iloc[0]
 im=ax.pcolormesh(X,Y,np.ma.masked_where(d<vmax*.003,d).reshape(shape),cmap='YlGnBu',vmin=0,vmax=vmax,shading='nearest',rasterized=True)
 ax.contour(X,Y,d.reshape(shape),levels=[r.hpd90_threshold,r.hpd50_threshold],colors=['#416681','#122a3b'],linewidths=[.8,1.2])
 ax.plot(arc[:,0],arc[:,1],ls='--',lw=.8,color='#777');ax.scatter(r.mode_lon,r.mode_lat,marker='*',s=80,c='#f29327',edgecolors='white',lw=.5,zorder=10)
 for key,col,ls in [(ids[1],'#8c718e','--'),(ids[2],'#be5145','-'),(ids[3],'#268550','--')]:
  a=np.array(fd[key]['geometry']['coordinates'][0]);ax.plot(a[:,0],a[:,1],color=col,ls=ls,lw=.8,alpha=.85)
 ax.set(xlim=(87.5,96),ylim=(-38,-32),xlabel='Longitude',ylabel='Latitude');ax.set_aspect(1/np.cos(np.radians(35)));ax.grid(alpha=.12)
 ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:.0f}°E'));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{abs(x):.0f}°S'));ax.set_title(title,fontsize=13,pad=12)
 ax.text(.025,.025,f'90% area: {r.hpd90_km2:,.0f} km²\nOutside past envelopes: {r.outside_envelopes_mass:.1%}',transform=ax.transAxes,fontsize=9,bbox=dict(fc='white',ec='none',alpha=.92))
cb=fig.colorbar(im,cax=fig.add_axes([.924,.30,.011,.46]));cb.set_label('Conditional source probability density / km²');cb.formatter.set_powerlimits((0,0));cb.update_ticks()
fig.suptitle('Residual origin density after searches found no wreckage',x=.05,ha='left',y=.965,fontsize=18,color='#16344b')
fig.text(.05,.91,'Pléiades + all four Possible COSMO-SkyMed Radar contacts | COSMO: 21 March | equal three-model mixture',fontsize=12)
fig.text(.05,.17,'Both updates marginalize illustrative coverage and detection ranges. Dependent misses give no extra detection credit for overlapping campaigns;\nindependent misses multiply campaign failure probabilities. Neither treatment deletes searched areas or applies future searches as negative evidence.',fontsize=10,linespacing=1.5)
fig.legend(handles=[Line2D([],[],color=c,ls=ls,label=l) for c,ls,l in [('#8c718e','--','OI 2018 envelope'),('#be5145','-','OI recent southeast band'),('#268550','--','Possible remaining northwest band')]],loc='lower left',bbox_to_anchor=(.045,.085),ncol=3,frameon=False,fontsize=10)
fig.text(.05,.065,'OI outlines are approximate; ATSB coverage is incorporated from the published footprint mask. Contours: 50%, 90%; star: grid-cell mode. Same colour scale.',fontsize=9,color='#555')
fig.text(.05,.03,'Conditional sensitivity analysis, not a calibrated MH370 location posterior. Unknown debris identity, search geometry and spatial detection quality remain material.',fontsize=10,color='#555')
for ext in ['png','pdf','svg']:fig.savefig(B/f'residual_comparison.{ext}',dpi=210,facecolor='white')
plt.close(fig)
