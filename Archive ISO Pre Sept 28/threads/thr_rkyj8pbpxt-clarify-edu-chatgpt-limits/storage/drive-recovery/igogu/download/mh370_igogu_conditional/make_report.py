#!/usr/bin/env python3
"""Scientific probability maps and a self-contained PDF of the conditional run."""
from pathlib import Path
import json,io,textwrap
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.special import logsumexp
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq
from pyproj import CRS,Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter,MaxNLocator
from model import ROOT,OBS,T0
from assemble_results import quantile

OUT=ROOT/'output';D=np.load(OUT/'posterior_samples.npz');S=json.loads((OUT/'summary.json').read_text());CFG=json.loads((ROOT/'inputs/prior_config.json').read_text())
WEIGHT=D['weights'];VAL=D['values'];PAR=D['physical_parameters'];TAG=D['tags'];ARC=D['arc_states'];RES=D['arc_residuals']
EXACT=np.load(OUT/'exact_endpoint_measure.npz');ENDPOINT=EXACT['endpoints'];ENDWEIGHT=EXACT['weights']
DIAGNOSTICS=json.loads((OUT/'component_diagnostics.json').read_text())
PROVISIONAL=S.get('sampling_status')=='provisional'
LAND=json.loads((ROOT/'inputs/land.geojson').read_text());PATHS=json.loads((OUT/'representative_paths.json').read_text());ARCROWS=OBS[OBS.kind.eq('arc')].reset_index(drop=True)
EP=pd.read_csv(ROOT/'inputs/satellite_ephemeris.csv')
ORBIT=CubicHermiteSpline(pd.to_datetime(EP.time_utc).astype('int64').to_numpy()/1e9-T0,EP[['x_km','y_km','z_km']].to_numpy(),EP[['vx_km_s','vy_km_s','vz_km_s']].to_numpy(),axis=0)
INK='#213446';MUTED='#526477';TEAL='#167b86';COLORS=['#b58a55','#408bb5','#173e73']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED})

def utc(t):return pd.Timestamp(T0+t,unit='s',tz='UTC').strftime('%H:%M:%S')
def percent(value,places=2):
 if 0<value<10**(-places)/100:return f'<{10**(-places):.{places}f}%'
 return f'{value:.{places}%}'
def text(fig,x,y,content,width=98,size=10,line=.024,color=INK,bold=False):
 for paragraph in content.split('\n'):
  for row in textwrap.wrap(paragraph,width=width) or ['']:
   fig.text(x,y,row,fontsize=size,color=color,fontweight='bold' if bold else 'normal',va='top');y-=line
 return y
def title(fig,main,sub):
 fig.text(.06,.952,main,fontsize=21,fontweight='bold',color=INK);fig.text(.06,.915,sub,fontsize=10.5,color=MUTED)
def footer(fig,page):
 prefix='PROVISIONAL SAMPLING | ' if PROVISIONAL else ''
 fig.text(.06,.037,prefix+'Conditional on IGOGU. SATCOM + fuel timing; no debris, drift, WSPR or search-coverage likelihood.',fontsize=8,color=MUTED)
 fig.text(.94,.037,str(page),fontsize=8,color=MUTED,ha='right')
def land(ax):
 x1,x2=ax.get_xlim();y1,y2=ax.get_ylim()
 for feature in LAND['features']:
  g=feature['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for p in polys:
   xy=np.asarray(p[0]);
   if xy[:,0].max()<x1 or xy[:,0].min()>x2 or xy[:,1].max()<y1 or xy[:,1].min()>y2:continue
   ax.add_patch(Polygon(xy,facecolor='#e9e6dc',edgecolor='#9a9e98',lw=.45,zorder=1))
def geoaxes(ax,bounds):
 ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:]);ax.set_facecolor('#f3f7f9');land(ax)
 ax.set_aspect(1/np.cos(np.radians(np.mean(bounds[2:]))))
 ax.xaxis.set_major_locator(MaxNLocator(6));ax.yaxis.set_major_locator(MaxNLocator(7))
 ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}°E'))
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{abs(y):g}°'+('N' if y>=0 else 'S')))
 ax.grid(color='#d5e0e6',lw=.6);ax.tick_params(labelsize=9)
 for spine in ax.spines.values():spine.set_color('#9aaab6')
def density(lat,lon,weight=WEIGHT):
 la=float(quantile(lat,weight,[.5])[0]);lo=float(quantile(lon,weight,[.5])[0])
 crs=CRS.from_proj4(f'+proj=laea +lat_0={la} +lon_0={lo} +datum=WGS84 +units=km')
 fwd=Transformer.from_crs('EPSG:4326',crs,always_xy=True);rev=Transformer.from_crs(crs,'EPSG:4326',always_xy=True)
 x,y=fwd.transform(lon,lat);pad=30.;step=5.
 bx=np.arange(np.floor((x.min()-pad)/step)*step,np.ceil((x.max()+pad)/step)*step+step,step)
 by=np.arange(np.floor((y.min()-pad)/step)*step,np.ceil((y.max()+pad)/step)*step+step,step)
 hist=np.histogram2d(x,y,bins=[bx,by],weights=weight)[0].T
 prob=gaussian_filter(hist,1.,mode='constant');prob/=prob.sum();den=prob/25
 order=np.argsort(den.ravel())[::-1];cum=np.cumsum(prob.ravel()[order]);levels=[];areas=[]
 for mass in [.99,.9,.5]:
  idx=min(np.searchsorted(cum,mass),len(order)-1);threshold=den.ravel()[order[idx]];levels.append(threshold);areas.append(float((den>=threshold).sum()*25))
 xx,yy=np.meshgrid((bx[:-1]+bx[1:])/2,(by[:-1]+by[1:])/2);glon,glat=rev.transform(xx,yy)
 return glon,glat,den,np.array(levels),areas
def map_density(ax,lat,lon,weight=WEIGHT):
 qlat=quantile(lat,weight,[.0005,.9995]);qlon=quantile(lon,weight,[.0005,.9995]);ym=(qlat[0]+qlat[1])/2;xm=(qlon[0]+qlon[1])/2
 sy=max(1.5,(qlat[1]-qlat[0])*1.3);sx=max(1.5,(qlon[1]-qlon[0])*1.3)
 sx=max(sx,sy*1.3/np.cos(np.radians(ym)));sy=max(sy,sx*np.cos(np.radians(ym))/1.9)
 bounds=[xm-sx/2,xm+sx/2,ym-sy/2,ym+sy/2];geoaxes(ax,bounds)
 lonmesh,latmesh,z,lev,areas=density(lat,lon,weight)
 ax.contourf(lonmesh,latmesh,z,levels=[lev[0],lev[1],lev[2],z.max()*1.001],colors=['#e4edf3','#a1c7dc','#477da6'],alpha=.92,zorder=3)
 con=ax.contour(lonmesh,latmesh,z,levels=lev,colors=COLORS,linewidths=[1.0,1.25,1.5],zorder=4)
 ax.clabel(con,fmt={v:s for v,s in zip(lev,['99%','90%','50%'])},fontsize=8,inline=True)
 ax.scatter(quantile(lon,weight,[.5]),quantile(lat,weight,[.5]),s=28,marker='+',color=INK,zorder=6,label='Coordinate medians')
 return areas
def nominal_arc(ax,row,h):
 sat=ORBIT(float(row.time_s));ground=np.array([-2368.8,4881.1,-3342.]);e2=.0066943799901413165
 def bt(lat,lon):
  lat,lon=np.radians([lat,lon]);n=6378.137/np.sqrt(1-e2*np.sin(lat)**2);hk=h/1000
  p=np.array([(n+hk)*np.cos(lat)*np.cos(lon),(n+hk)*np.cos(lat)*np.sin(lon),(n*(1-e2)+hk)*np.sin(lat)])
  return 2e6*(np.linalg.norm(p-sat)+np.linalg.norm(ground-sat))/299792.458-495679-row.bto_us
 lats=np.linspace(*ax.get_ylim(),240);lons=[]
 for lat in lats:
  try:lons.append(brentq(lambda lon:bt(lat,lon),64.5,160))
  except ValueError:lons.append(np.nan)
 ax.plot(lons,lats,ls='--',lw=.9,color='#646c77',zorder=5,label='Nominal BTO arc at median altitude')
 ax.legend(loc='lower left',fontsize=8,framealpha=.9)
def context(fig,current_lat,current_lon):
 ax=fig.add_axes([.78,.19,.18,.27]);geoaxes(ax,[60,115,-50,12]);ax.tick_params(labelsize=6)
 for item in PATHS[::max(1,len(PATHS)//120)]:
  p=np.asarray(item['points']);ax.plot(p[:,2],p[:,1],color=TEAL,lw=.35,alpha=.09,zorder=2)
 ax.scatter(94.4166667,7.5169444,marker='*',s=35,color=INK,zorder=4);ax.text(95.5,7.5,'IGOGU',fontsize=6,color=INK)
 j=np.searchsorted(np.cumsum(WEIGHT),(np.arange(1200)+.5)/1200).clip(0,len(WEIGHT)-1)
 ax.scatter(current_lon[j],current_lat[j],s=.5,color='#173e73',alpha=.08,zorder=3)
 ax.set_title('Geographic context',fontsize=9,color=INK,pad=7)
def style_table(table,size=9):
 table.auto_set_font_size(False);table.set_fontsize(size)
 for (i,j),cell in table.get_celld().items():
  cell.set_edgecolor('#d4dfe6');cell.set_linewidth(.45)
  if i==0:cell.set_facecolor(INK);cell.set_text_props(color='white',weight='bold')
  else:cell.set_facecolor('#f1f5f7' if i%2 else 'white');cell.set_text_props(color=INK)

def endpoint_page():
 fig=plt.figure(figsize=(15,10),facecolor='white');title(fig,'MH370 | Conditional IGOGU density','Position at fuel exhaustion | 00:15-00:19 UTC, likelihood peak at 00:17:30 | 8 March 2014')
 if PROVISIONAL:fig.text(.07,.868,'PROVISIONAL — convergence checks failed; see pages 3–4.',fontsize=10.5,fontweight='bold',color='#9b5f27')
 ax=fig.add_axes([.07,.16,.65,.68]);areas=map_density(ax,ENDPOINT[:,0],ENDPOINT[:,1],ENDWEIGHT)
 if ENDWEIGHT.max()>.01:
  j=int(np.argmax(ENDWEIGHT));xy=(ENDPOINT[j,1],ENDPOINT[j,0])
  ax.scatter(*xy,marker='x',s=45,color='#a66020',zorder=7)
  toleft=xy[0]>np.mean(ax.get_xlim())
  ax.annotate(f'One draw carries {ENDWEIGHT[j]:.1%} of the weight',xy=xy,xytext=(-12 if toleft else 12,18),textcoords='offset points',ha='right' if toleft else 'left',
       fontsize=8.5,color='#8f521a',bbox=dict(facecolor='white',alpha=.9,edgecolor='none',pad=3),
       arrowprops=dict(arrowstyle='-',color='#a66020',lw=.8),zorder=8)
 ax.legend(loc='lower left',fontsize=8,framealpha=.9)
 byturn=[sum(r['posterior_weight'] for r in S['model_weights'] if r['turns']==k) for k in range(5)]
 fig.text(.78,.83,'ADDITIONAL TURNS',fontsize=11,weight='bold',color=INK)
 for j,(k,w) in enumerate(enumerate(byturn)):
  label=percent(w,1) if w>0 else 'no sampled support'
  fig.text(.78,.79-j*.033,f'{k} turns: {label}',fontsize=10,color=INK)
 alt=sum(r['posterior_weight'] for r in S['model_weights'] if r['altitude_class']==1)
 text(fig,.78,.595,f'Cruise step climbs: {alt:.1%}\nConstant altitude: {1-alt:.1%}',width=32,size=9.5,line=.028)
 medlat=S['endpoint_latitude_quantiles'][1];medlon=S['endpoint_longitude_quantiles'][1]
 fig.text(.78,.515,f'Medians: {abs(medlat):.2f}°'+('S' if medlat<0 else 'N')+f', {medlon:.2f}°E',fontsize=9.3,color=INK)
 warning='Sampling remains provisional; contour probabilities describe the sampled approximation. ' if PROVISIONAL else ''
 text(fig,.07,.111,warning+'Contours enclose 50%, 90% and 99% of the conditional density. This is the position at modeled fuel exhaustion; subsequent descent, glide and wreckage drift are not modeled.',width=151,size=9,line=.021)
 context(fig,VAL[:,6],VAL[:,7]);footer(fig,1)
 return fig,areas

def assumptions_page():
 fig=plt.figure(figsize=(15,10),facecolor='white');title(fig,'Conditions, priors and measurement treatment','The result is conditional on reaching IGOGU; it does not estimate the probability of that hypothesis.')
 blocks=[('Starting state','Exact IGOGU coordinate 7°31′01″N, 94°25′E. Arrival time is a normal prior centred at 18:38 UTC with 60-second standard deviation, truncated to 18:36-18:40. This broadens the corrected earlier 18:37-18:39 estimates; it is not a measured arrival-time posterior. Initial altitude is uniform 31,000-37,000 ft.'),
 ('Turns and navigation','The required first left turn starts immediately at IGOGU and must finish before the first call burst at 18:39:55.354. Initial southerly ground course is truncated normal 180° ±15°, bounded 150-210°. Additional turn count has prior 20% each for 0,1,2,3,4. Additional turn times are ordered uniform after the first call through 00:15; signed angles are uniform -180° to +180°. Turns have finite bank and roll limits; geodesic course evolution between maneuvers is not counted as another turn.'),
 ('Cruise altitude and speed','Altitude class is 50% constant and 50% two normal step climbs. Each climb is 1,000-2,000 ft at 600 ft/min with smooth ramps; timing windows are 1-2.5 and 3-4.5 hours after IGOGU. Initial Mach is uniform 0.76-0.85. Six subsequent hourly Mach knots follow a truncated-normal random walk, standard deviation 0.015, bounded 0.74-0.86, with smooth speed changes between knots. ERA5 winds determine groundspeed and crab.'),
 ('Fuel and physical checks','The inherited 18:28 fuel prior is uniform 32,524-34,524 kg, with log-uniform fuel-flow factor 0.9-1.1 and no jettison. A triangular likelihood constrains calculated exhaustion to 00:15-00:19, peaking at 00:17:30. Sampling that narrow time window uses an inverse fuel map with its Jacobian retained. The public-data fuel/thrust approximation is a sensitivity model, not a calibrated manufacturer performance deck. Mach, stall, thrust, bank and roll checks are applied throughout.'),
 ('Satellite observations','Five R1200 BTO/BFO epochs from 19:41 to 00:11 are evaluated at their exact logged times, plus every receive BFO in the 18:40 and 23:14 calls. BTO σ=29 µs; BFO σ=4.3 Hz. Correlated call bursts contribute one mean-residual likelihood per call. Final selection requires every BTO within ±58 µs and every BFO within ±8.6 Hz. The oscillator calibration remains fixed at 152.5 Hz. Pre-IGOGU and all 00:19 BTO/BFO are excluded from this conditional run.'),
 ('Two inherited issues corrected','C-channel carrier identifiers now come from the hexadecimal carrier field, not the trailing bitrate field. The old extra ±60-second crossing test against each nominal arc centre is recorded only as a diagnostic: near a tangent it can demand roughly 1 µs agreement despite 29 µs BTO noise. The likelihood and selection instead use the measured range at the exact transmission time.')]
 y=.858
 for heading,body in blocks:
  fig.text(.065,y,heading,fontsize=11.5,fontweight='bold',color=INK);y-=.027
  y=text(fig,.065,y,body,width=167,size=9.4,line=.021)-.016
 text(fig,.065,.112,'Sources: released Inmarsat/ATSB SATCOM log; historical Malaysia AIP coordinates; pinned public satellite-state workbook transcription; archived ERA5 grid and the saved public aircraft/fuel model. Full identifiers, inputs and code are supplied with the reproducible package.',width=170,size=8.6,line=.020,color=MUTED)
 for x,label,url in [(.065,'Released SATCOM log','https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf'),(.27,'Historical Malaysia AIP','https://aip.caam.gov.my/aip%20pdf/AIP%20AMDT%202_2010/ENR/Enr3_3.pdf'),(.50,'Bayesian Methods in the Search for MH370','https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf')]:
  fig.text(x,.06,label,color=TEAL,fontsize=8.2,url=url)
 footer(fig,2);return fig

def diagnostics_page():
 fig=plt.figure(figsize=(15,10),facecolor='white');title(fig,'Posterior weights and sampling checks','Fresh independent importance draws use the same frozen proposals, priors, observations and physical model.')
 ax=fig.add_axes([.08,.56,.38,.28]);x=np.arange(5);nr=len(S['replicates'])
 for i,r in enumerate(S['replicates']):ax.bar(x+(i-(nr-1)/2)*.28,r['turn_count_weights'],width=.27,label=r['name'],color=['#277f8e','#c09655','#785b91'][i%3])
 ax.axhline(.2,ls='--',color='#899ba7',lw=1,label='Prior 20% each');ax.set(xticks=x,xlabel='Additional turns',ylabel='Posterior probability',ylim=(0,1));ax.legend(fontsize=8,frameon=False);ax.spines[['top','right']].set_visible(False)
 ax=fig.add_axes([.56,.56,.36,.28]);bins=np.linspace(0,240,31);ax.hist(PAR[:,7]-21168,bins=bins,weights=WEIGHT,density=True,color='#5594a5',alpha=.8)
 t=np.linspace(0,240,241);tri=np.where(t<150,2*t/(240*150),2*(240-t)/(240*90));ax.plot(t,tri,color='#af6c3e',lw=1.3,label='Specified triangular likelihood')
 ax.set(xlabel='Seconds after 00:15 UTC',ylabel='Density per second');ax.legend(fontsize=8,frameon=False);ax.spines[['top','right']].set_visible(False)
 rows=[]
 for r in S['replicates']:
  lat=r['endpoint_latitude_quantiles'];lon=r['endpoint_longitude_quantiles'];rows.append([r['name'],f'{lat[1]:.2f}°',f'{lat[0]:.2f} to {lat[2]:.2f}°',f'{lon[1]:.2f}°',f'{lon[0]:.2f} to {lon[2]:.2f}°',f"{r['model_log_evidence']:.2f}"])
 ax=fig.add_axes([.075,.355,.85,.12]);ax.axis('off');tb=ax.table(cellText=rows,colLabels=['Ensemble','Median latitude','95% latitude interval','Median longitude','95% longitude interval','Log evidence'],cellLoc='center',bbox=[0,0,1,1],colWidths=[.13,.14,.21,.15,.22,.15]);style_table(tb,9)
 arrival=S['arrival_seconds_since_182212_quantiles'];fuel=S['fuel_exhaustion_seconds_since_182212_quantiles']
 checks=S['fine_resolution_validation'];valid=[r for r in checks if 'max_BTO_change_us' in r]
 delta=max([r['max_BTO_change_us'] for r in valid],default=float('nan'));df=max([r['max_BFO_change_hz'] for r in valid],default=float('nan'))
 y=text(fig,.08,.306,f"{S['total_independent_proposal_draws']:,} independent final proposals; {S['total_trajectory_evaluations']:,} final trajectory evaluations; {S['exploration_and_proposal_training_trajectory_evaluations']:,} additional evaluations for exploration and proposal training. Effective importance sample size {S['independent_importance_ess']:,.0f}; largest individual normalized weight {S['largest_individual_importance_weight']:.2%}. Resampled display points are not independent samples.",width=159,size=10,line=.024)
 y=text(fig,.08,y-.01,f"Arrival time: median {utc(arrival[1])}, central 95% {utc(arrival[0])}-{utc(arrival[2])} UTC. Exhaustion: median {utc(fuel[1])}, central 95% {utc(fuel[0])}-{utc(fuel[2])} UTC. Maximum retained errors: BTO {S['maximum_retained_BTO_sigmas']*29:.2f} µs, BFO {S['maximum_retained_BFO_error_hz']:.2f} Hz.",width=159,size=10,line=.024)
 text(fig,.08,y-.01,f"Numerical check: {sum(bool(q['passes_at_30s']) for q in checks)}/{len(checks)} selected samples retain all checks at a 30-second step. Maximum computed changes: BTO {delta:.3f} µs, BFO {df:.4f} Hz. The independent observation implementation agrees to floating-point precision. Maps use a 5 km equal-area grid and a 5 km Gaussian display kernel; contours enclose normalized sampled probability masses.",width=159,size=9.5,line=.023)
 footer(fig,3);return fig

def sampling_page():
 fig=plt.figure(figsize=(15,10),facecolor='white')
 status='PROVISIONAL: the reported Monte Carlo checks are not all satisfied.' if PROVISIONAL else 'The reported Monte Carlo checks pass; remote undiscovered modes remain possible.'
 title(fig,'What the sampling supports',status)
 rows=[]
 for k in range(5):
  for a in [0,1]:
   ds=[d for d in DIAGNOSTICS if d['turns']==k and d['altitude_class']==a]
   mass=sum(d['pooled_component_weight'] for d in ds)
   ess=[d.get('importance_ess',0) for d in ds]
   logs=[d['log_evidence'] for d in ds]
   rows.append([str(k),'Two step climbs' if a else 'Constant altitude','10%',percent(mass,2),
                ' / '.join(f'{x:.0f}' for x in ess) or 'No survivors',
                ' / '.join(f'{x:.2f}' for x in logs) or 'Not estimated'])
 ax=fig.add_axes([.065,.54,.87,.30]);ax.axis('off')
 tb=ax.table(cellText=rows,colLabels=['Extra turns','Altitude class','Joint prior','Pooled weight','ESS by replicate','Log evidence by replicate'],cellLoc='center',bbox=[0,0,1,1],colWidths=[.10,.19,.10,.14,.20,.27]);style_table(tb,9)
 y=text(fig,.065,.506,f"Pooled relative standard error of evidence: {S['pooled_relative_evidence_se']:.1%}. Difference between independent evidence estimates: {S.get('replicate_evidence_difference_standard_errors',float('nan')):.2f} estimated standard errors. Largest difference in turn-count probabilities between replicates: {S.get('replicate_turn_weight_maximum_difference',float('nan')):.1%}.",width=168,size=10,line=.024)
 y=text(fig,.065,y-.018,'The exploratory sequential Monte Carlo populations disagreed materially and were not used as the final probability measure. Proposal training used both populations, four small adaptive importance rounds, and two larger pilot batches. Empirical Student-t mixture refinement then improved coverage. The fresh final batches retain a 10% full-prior proposal component. Weights include the full proposal density, logit Jacobian, ordered-turn-time prior density and fuel-time change of variable.',width=169,size=9.5,line=.023)
 y=text(fig,.065,y-.018,'The checks flag a run as provisional if pooled ESS is below 1,000, an individual weight exceeds 1%, evidence differs by more than three estimated standard errors, or a turn-count probability or coordinate cumulative distribution differs by more than five percentage points between replicates. These checks test numerical stability; they cannot validate the physical model or establish that every remote branch was found.',width=169,size=9.5,line=.023)
 y=text(fig,.065,y-.018,'Zero sampled support is not proof of impossibility. Every class retained its equal prior weight; a zero in this table means that the finite run found no trajectory meeting every declared check. Interpretation depends on the chosen turn, Mach, altitude, oscillator and public fuel-model assumptions. These are exhaustion-position densities, with no subsequent glide or descent.',width=169,size=9.5,line=.023)
 c=S['legacy_nominal_crossing_test']
 text(fig,.065,y-.018,f"Legacy crossing-test sensitivity: additionally requiring every nominal arc-centre crossing within ±60 seconds retains {100*c['weighted_retention_fraction']:.3g}% of the weighted mass, with ESS {c['effective_sample_size']:.1f}. This is insufficient to estimate a reliable PDF under that stricter rule. Primary maps use range uncertainty at the exact logged epochs.",width=169,size=9.5,line=.023)
 footer(fig,4);return fig

def arc_page(j,page):
 row=ARCROWS.iloc[j];time=row.timestamp_utc[11:19];lat=ARC[:,j,0];lon=ARC[:,j,1]
 fig=plt.figure(figsize=(15,10),facecolor='white');title(fig,f'MH370 | Conditional spatial PDF at {time} UTC','Smoothed position density: all selected SATCOM observations and the exhaustion-time likelihood are used')
 if PROVISIONAL:fig.text(.07,.868,'PROVISIONAL — convergence checks failed; see pages 3–4.',fontsize=10.5,fontweight='bold',color='#9b5f27')
 ax=fig.add_axes([.07,.16,.65,.68]);areas=map_density(ax,lat,lon)
 qlat=quantile(lat,WEIGHT,[.025,.5,.975]);qlon=quantile(lon,WEIGHT,[.025,.5,.975]);gs=quantile(ARC[:,j,3]*3600/1852,WEIGHT,[.025,.5,.975]);h=quantile(ARC[:,j,2]/.3048,WEIGHT,[.025,.5,.975])
 nominal_arc(ax,row,h[1]*.3048)
 fig.text(.78,.83,'OBSERVED',fontsize=11,fontweight='bold',color=INK)
 fig.text(.78,.792,f'BTO {row.bto_us:,.0f} µs',fontsize=10,color=INK);fig.text(.78,.759,f'BFO {row.bfo_hz:.0f} Hz',fontsize=10,color=INK)
 y=text(fig,.78,.705,f'Median latitude: {qlat[1]:.2f}°\nMedian longitude: {qlon[1]:.2f}°E\nMedian groundspeed: {gs[1]:.0f} kt\n95% GS: {gs[0]:.0f}-{gs[2]:.0f} kt\nMedian altitude: {h[1]:,.0f} ft',width=35,size=9.6,line=.028)
 context(fig,lat,lon)
 bt=quantile(RES[:,j,0],WEIGHT,[.025,.5,.975]);bf=quantile(RES[:,j,1],WEIGHT,[.025,.5,.975])
 text(fig,.07,.111,f'Central 95% residual intervals at the logged epoch: BTO {bt[0]:+.1f} to {bt[2]:+.1f} µs; BFO {bf[0]:+.2f} to {bf[2]:+.2f} Hz. Residual = predicted minus observed. Contours enclose 50%, 90% and 99% of the conditional density.',width=151,size=9,line=.021)
 footer(fig,page);return fig,areas

def main():
 figs=[];fig,areas=endpoint_page();figs.append(fig);grid_summary={'fuel_endpoint_HPD_areas_km2_99_90_50':areas}
 figs.extend([assumptions_page(),diagnostics_page(),sampling_page()])
 for j in range(5):fig,areas=arc_page(j,j+5);figs.append(fig);grid_summary[ARCROWS.timestamp_utc.iloc[j]]=areas
 pdf=OUT/'mh370_igogu_conditional_posterior.pdf';buffer=io.BytesIO()
 with PdfPages(buffer,metadata={'Title':'MH370 conditional IGOGU trajectory posterior','Author':'MH370 research project','Subject':'Equal 0-4 additional-turn priors; altitude mixture; SATCOM and fuel constraints'}) as pages:
  for i,fig in enumerate(figs):
   pages.savefig(fig)
   if i==0:fig.savefig(OUT/'mh370_igogu_fuel_exhaustion_pdf.png',dpi=180,facecolor='white')
   if i==len(figs)-1:fig.savefig(OUT/'mh370_igogu_0011_pdf.png',dpi=180,facecolor='white')
   plt.close(fig)
 data=buffer.getvalue();assert data.rstrip().endswith(b'%%EOF');pdf.write_bytes(data)
 (OUT/'density_grid_summary.json').write_text(json.dumps(grid_summary,indent=2)+'\n');print(pdf)
if __name__=='__main__':main()
