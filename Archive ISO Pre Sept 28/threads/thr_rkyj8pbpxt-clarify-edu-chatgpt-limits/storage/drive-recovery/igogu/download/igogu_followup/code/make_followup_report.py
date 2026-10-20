"""Read saved numerical artifacts and author exact scientific comparison figures."""
from pathlib import Path
import sys,json,textwrap
import numpy as np,pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.optimize import brentq,minimize_scalar
from scipy.spatial import cKDTree
from pyproj import CRS,Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
from audit_model import BASE,HERE,T0,OBS
from satellite_check import bto,BTO7,T7,GEOD
from assemble_results import quantile
OUT=HERE.parent/'output';QA=HERE.parent/'qa';QA.mkdir(exist_ok=True)
S=json.loads((OUT/'seventh_arc_summary.json').read_text());DS=json.loads((OUT/'due_south_summary.json').read_text())
M=np.load(OUT/'seventh_arc_measure.npz');EP=M['exhaustion_positions'];W=M['original_weights'];W7=M['weight_descent_0_fpm']
LAND=json.loads((BASE/'inputs/land.geojson').read_text())
INK='#213446';MUTED='#526477';BLUE='#276797';RED='#b45532';TEAL='#177f83'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
def title(f,main,sub):
 f.text(.055,.956,main,fontsize=20,weight='bold',color=INK);f.text(.055,.916,sub,fontsize=10,color=MUTED)
def prose(f,x,y,s,width=132,size=10,line=.024):
 for paragraph in s.split('\n'):
  for row in textwrap.wrap(paragraph,width) or ['']:
   f.text(x,y,row,fontsize=size,color=INK,va='top');y-=line
 return y
def footer(f,n):
 f.text(.055,.032,'Conditional sensitivity | Original posterior remains provisional | No 00:19 BFO used',fontsize=8,color=MUTED)
 f.text(.945,.032,str(n),ha='right',fontsize=8,color=MUTED)
def geo(ax,bounds):
 ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:]);ax.set_facecolor('#f4f7f9');ax.set_aspect(1/np.cos(np.radians(np.mean(bounds[2:]))))
 for fe in LAND['features']:
  g=fe['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for poly in polys:
   xy=np.array(poly[0]);
   if xy[:,0].max()<bounds[0] or xy[:,0].min()>bounds[1] or xy[:,1].max()<bounds[2] or xy[:,1].min()>bounds[3]:continue
   ax.add_patch(Polygon(xy,facecolor='#e7e6df',edgecolor='#a3aaa8',lw=.4,zorder=1))
 ax.grid(color='#d4dfe4',lw=.5);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}°E'));ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{abs(y):g}°'+('S' if y<0 else 'N')))
 ax.tick_params(labelsize=9)
def hpd(z,area,masses=(.99,.9,.5)):
 z=np.asarray(z);area=np.broadcast_to(area,z.shape);j=np.argsort(z.ravel())[::-1];cum=np.cumsum((z*area).ravel()[j]);cum/=cum[-1]
 return np.array([z.ravel()[j[min(np.searchsorted(cum,m),len(j)-1)]] for m in masses])
def flight_grid(w):
 crs=CRS.from_proj4('+proj=laea +lat_0=-34 +lon_0=94 +datum=WGS84 +units=km');fwd=Transformer.from_crs(4326,crs,always_xy=True);rev=Transformer.from_crs(crs,4326,always_xy=True)
 x,y=fwd.transform(EP[:,1],EP[:,0]);bx=np.arange(np.floor(x.min()/5)*5-30,np.ceil(x.max()/5)*5+35,5);by=np.arange(np.floor(y.min()/5)*5-30,np.ceil(y.max()/5)*5+35,5)
 z=gaussian_filter(np.histogram2d(x,y,bins=[bx,by],weights=w)[0].T,1);z/=z.sum()*25
 xx,yy=np.meshgrid((bx[1:]+bx[:-1])/2,(by[1:]+by[:-1])/2);lon,lat=rev.transform(xx,yy)
 return lon,lat,z,hpd(z,25)
GRID0=flight_grid(W);GRID7=flight_grid(W7)
def draw_grid(ax,g,color,filled=False,ls='solid'):
 lon,lat,z,levels=g
 if filled:ax.contourf(lon,lat,z,levels=[*levels,z.max()*1.01],colors=['#e3eef6','#adcbdf','#719fbf'],alpha=.85,zorder=2)
 c=ax.contour(lon,lat,z,levels=levels,colors=color,linewidths=[.85,1.25,1.8],linestyles=ls,zorder=4)
 ax.clabel(c,fmt={v:f'{m}%' for v,m in zip(levels,[99,90,50])},fontsize=8)
def arc(ax,h=35000*.3048,color='#697485',label='R600 nominal arc, FL350',ls='--',value=BTO7,time=T7):
 lat=np.linspace(*ax.get_ylim(),240);lon=[]
 for la in lat:
  try:lon.append(brentq(lambda lo:bto(la,lo,h,time)-value,65,120))
  except ValueError:lon.append(np.nan)
 ax.plot(lon,lat,color=color,ls=ls,lw=1.1,label=label,zorder=3)
 return np.array(lon),lat
def table(ax,data,headers,widths=None,fontsize=9):
 ax.axis('off');t=ax.table(cellText=data,colLabels=headers,cellLoc='center',bbox=[0,0,1,1],colWidths=widths);t.auto_set_font_size(False);t.set_fontsize(fontsize)
 for (i,j),c in t.get_celld().items():
  c.set_edgecolor('#ccd6dd');c.set_linewidth(.45)
  if i==0:c.set_facecolor(INK);c.set_text_props(color='white',weight='bold')
  else:c.set_facecolor('#edf3f7' if i%2 else 'white')
 return t
def first_page():
 f=plt.figure(figsize=(14,10));title(f,'IGOGU conditional | Seventh-arc sensitivity','Every original positive-weight trajectory checked: 1,710,701 survivors; R600 at 00:19:29.416 UTC')
 ax=f.add_axes([.07,.23,.61,.63]);geo(ax,[91,98,-36.5,-30.4]);draw_grid(ax,GRID0,BLUE,True);draw_grid(ax,GRID7,RED,False,'dashed');arc(ax)
 top=S['largest_original_draw'];la,lo=top['endpoint'][:2];p=S['scenarios']['descent_0_fpm']['largest_original_draw']['position_at_R600']
 ax.scatter(lo,la,marker='x',color='#9c471b',s=55,zorder=8);ax.annotate('4.6% draw: rejected',xy=(lo,la),xytext=(lo-.35,la+.35),fontsize=9,color='#9c471b',ha='right',arrowprops={'arrowstyle':'-','color':'#9c471b'})
 ax.annotate('',xy=(p[1],p[0]),xytext=(lo,la),arrowprops={'arrowstyle':'->','color':'#9c471b','lw':1.5})
 ax.legend(handles=[Line2D([],[],color=BLUE,label='Original exhaustion PDF'),Line2D([],[],color=RED,ls='--',label='+ R600 check and weighting'),Line2D([],[],color='#697485',ls='--',label='Nominal R600 arc, FL350')],loc='lower left',fontsize=8)
 v=S['scenarios']['descent_0_fpm'];q=v['gaussian_and_selection'];prose(f,.72,.84,f"R600 observation\n23,000 - 4,600 = 18,400 µs\nSigma: 63 µs; gate: ±126 µs\n\nOriginal mass retained: {v['retained_original_mass']:.2%}\nSurviving raw draws: {v['survivors']:,}\n\nReweighted medians\n{abs(q['latitude_q025_50_975'][1]):.2f}°S, {q['longitude_q025_50_975'][1]:.2f}°E\n\nImportance ESS: {q['ESS']:.0f}\nLargest new weight: {q['largest_weight']:.2%}\nStill provisional",width=37,size=10,line=.031)
 prose(f,.07,.172,'The flight model stops at fuel exhaustion. This sensitivity continues the last horizontal ground speed and geodesic course to the R600 time, at unchanged altitude. It adds the R600 Gaussian likelihood and a two-sigma gate. It is a kinematic extension, not a validated post-exhaustion flight or impact model.',width=158,size=9.4,line=.023)
 prose(f,.07,.088,'The original 4.6% draw ends 99.4 km inside the arc and heads west. Its continued residual is -665.1 µs (-10.56 sigma). It fails every tested descent-rate variant.',width=158,size=9.4,line=.023);footer(f,1);return f
def sensitivity_page():
 f=plt.figure(figsize=(14,10));title(f,'R600 result and its limits','The seventh-arc check is a new, explicitly separate sensitivity; the original posterior remains recoverable.')
 rows=[]
 for key,v in S['scenarios'].items():
  q=v['gaussian_and_selection'];rows.append([str(v['descent_rate_fpm']),f"{100*v['retained_original_mass']:.3f}%",f"{abs(q['latitude_q025_50_975'][1]):.3f}°S",f"{q['longitude_q025_50_975'][1]:.3f}°E",f"{q['ESS']:.0f}",f"{v['largest_original_draw']['residual_us']:+.1f}"])
 table(f.add_axes([.065,.64,.87,.20]),rows,['Descent, ft/min','Original mass retained','Median latitude','Median longitude','ESS','4.6% draw residual, µs'])
 q=S['scenarios']['descent_0_fpm']['gaussian_and_selection'];cross=S['nominal_centre_crossing_60s_sensitivity'];env=S['altitude_envelope']
 y=prose(f,.065,.586,'Descent-rate variants preserve horizontal motion and reduce altitude, with a floor at sea level. A sea-level floor is a geometric bound; it does not establish survival to the transmission or model impact. No 00:19 BFO, bank change, glide dynamics, or probability distribution over terminal controls has been added.',width=150)
 y=prose(f,.065,y-.02,f"The constant-height case has a central sampled 95% latitude interval {abs(q['latitude_q025_50_975'][2]):.2f}-{abs(q['latitude_q025_50_975'][0]):.2f}°S and longitude interval {q['longitude_q025_50_975'][0]:.2f}-{q['longitude_q025_50_975'][2]:.2f}°E. Its two replicate medians are {abs(q['replicates'][0]['latitude_median']):.3f}°S and {abs(q['replicates'][1]['latitude_median']):.3f}°S. Largest normalized weight remains {q['largest_weight']:.2%}, above the original 1% convergence criterion.",width=150)
 y=prose(f,.065,y-.02,f"Allowing any height from sea level to exhaustion height, at the same continued horizontal position, retains {env['any_altitude_retention']:.2%} of the original mass as potentially compatible. {env['all_altitudes_retention']:.2%} passes for every height in that interval. These are compatibility bounds, not an altitude-marginalized posterior.",width=150)
 y=prose(f,.065,y-.02,f"An additional nominal arc-centre crossing within ±60 seconds retains {cross['retained_mass']:.2%} of original mass, with selection-only ESS {cross['statistics']['ESS']:.0f}. That is separate from the statistically appropriate noisy-range test at the logged epoch. Requiring all the earlier nominal-centre crossings as well remains the poorly supported legacy test reported in the original PDF.",width=150)
 y=prose(f,.065,y-.02,'The 00:19:29 R600 value is the only new SATCOM datum here. The 00:19:37 R1200 message and both final BFO values remain excluded. General R600 noise is quoted as 62 µs in the reference book; its Table 10.1 assigns 63 µs to this specific observation, which is the value used here.',width=150)
 f.text(.065,.084,'ATSB released SU logs',fontsize=9,color=TEAL,url='https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf')
 f.text(.30,.084,'Davey et al., measurement model and Table 10.1',fontsize=9,color=TEAL,url='https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf');footer(f,2);return f
def drift_page():
 p=HERE.parent/'inputs/pleiades';grid=pd.read_csv(p/'grid.csv');surface=pd.read_csv(p/'surfaces.csv');meta=json.loads((p/'manifest.json').read_text());ids=['bran2016','oscar_v2_final','glorys12_waverys'];components=[]
 for sid in ids:
  d=surface[surface.surface_id.eq(sid)].set_index('cell_id').loc[grid.cell_id];z=d.normalized_density_per_km2.to_numpy();assert abs(np.sum(z*grid.quadrature_area_km2)-1)<1e-10;components.append(z)
 z=np.mean(components,axis=0);saved=surface[surface.surface_id.eq('equal_transport_family_model_average')].set_index('cell_id').loc[grid.cell_id].normalized_density_per_km2.to_numpy();assert np.allclose(z,saved,rtol=1e-10,atol=1e-15)
 grid['equal_thirds_density_per_km2']=z;grid['equal_thirds_mass']=z*grid.quadrature_area_km2
 for sid,zz in zip(ids,components):grid[sid+'_density_per_km2']=zz
 grid.to_csv(OUT/'pleiades_equal_thirds_grid.csv',index=False)
 shape=(129,41);xx=grid.longitude_deg.to_numpy().reshape(shape);yy=grid.latitude_deg.to_numpy().reshape(shape);levels=hpd(z,grid.quadrature_area_km2.to_numpy());mode=int(np.argmax(z));mid=np.array([grid.iloc[mode].latitude_deg,grid.iloc[mode].longitude_deg])
 f=plt.figure(figsize=(14,10));title(f,'IGOGU flight density and Pléiades source mixture','Equal weights: 1/3 BRAN2016 + 1/3 OSCAR v2 Final + 1/3 GLORYS12/WAVERYS')
 ax=f.add_axes([.07,.20,.65,.66]);geo(ax,[89,98,-38,-30.5]);draw_grid(ax,GRID0,BLUE,True)
 c=ax.contour(xx,yy,z.reshape(shape),levels=levels,colors=RED,linewidths=[.9,1.4,2],zorder=5);ax.clabel(c,fmt={v:f'{m}%' for v,m in zip(levels,[99,90,50])},fontsize=8)
 ax.plot(np.r_[xx[0],xx[1:,-1],xx[-1,-2::-1],xx[-2:0:-1,0]],np.r_[yy[0],yy[1:,-1],yy[-1,-2::-1],yy[-2:0:-1,0]],color=RED,lw=.55,ls=':',alpha=.6,label='Computed drift domain')
 ax.scatter(mid[1],mid[0],marker='*',s=90,color=RED,zorder=6);arc(ax)
 med=np.array([quantile(EP[:,0],W,[.5])[0],quantile(EP[:,1],W,[.5])[0]]);_,_,distance=GEOD.inv(med[1],med[0],mid[1],mid[0]);ax.scatter(med[1],med[0],marker='+',s=50,color=BLUE,zorder=6)
 ax.legend(handles=[Line2D([],[],color=BLUE,label='Original flight: fuel exhaustion'),Line2D([],[],color=RED,label='Pléiades equal-thirds source mixture'),Line2D([],[],color='#697485',ls='--',label='R600 nominal arc, FL350')],loc='lower left',fontsize=8)
 prose(f,.755,.83,f"Flight coordinate medians\n{abs(med[0]):.2f}°S, {med[1]:.2f}°E\n\nPléiades mixture grid mode\n{abs(mid[0]):.2f}°S, {mid[1]:.2f}°E\n\nSeparation: {distance/1000:.0f} km\n\nContours: 50 / 90 / 99%\n\nEach transport component is normalized on the same finite source grid before averaging.",width=31,size=10,line=.03)
 prose(f,.07,.151,'Overlay only. The flight layer is an exhaustion-position density; the drift layer is a conditional source-compatibility density at 00:19. It assumes exactly one associated object among twelve rating-5 image locations. No image-object identity has been established. The layers are not multiplied, and this is not a combined wreckage posterior.',width=157,size=9.4,line=.023)
 prose(f,.07,.085,'One-third weights are declared sensitivity weights. The source handoff has no calibrated transport-family probabilities; its grid edge marks uncomputed support, not zero probability.',width=157,size=9.4,line=.023)
 (OUT/'pleiades_mixture_summary.json').write_text(json.dumps({'weights':dict.fromkeys(ids,1/3),'mixture_normalization':float(np.sum(z*grid.quadrature_area_km2)),'matches_saved_mixture':True,'mode_latitude':float(mid[0]),'mode_longitude':float(mid[1]),'distance_from_flight_coordinate_medians_km':distance/1000,'density_hpd_thresholds_99_90_50':levels.tolist(),'calibration':'Uncalibrated conditional source compatibility; no fusion with flight posterior.'},indent=2))
 footer(f,3);return f
def initial_page():
 f=plt.figure(figsize=(14,10));title(f,'Initial paths after IGOGU','The original run imposed a southerly course distribution, not an exact FIR-following track.')
 ax=f.add_axes([.075,.18,.49,.66]);geo(ax,[93.0,95.3,5.7,7.9]);geojson=json.loads((BASE/'inputs/geography.json').read_text())
 for b in geojson['fir_boundaries']:
  xy=np.array(b['coordinates']);ax.plot(xy[:,0],xy[:,1],color='#61557e',lw=1.8,ls='--',zorder=5)
 paths=json.loads((BASE/'output/representative_paths.json').read_text());lons=[]
 for row in paths:
  p=np.asarray(row['points']);sub=p[p[:,1]>5.7];ax.plot(sub[:,2],sub[:,1],color=BLUE,alpha=.09,lw=.6,zorder=3)
  j=np.flatnonzero(p[:,1]<6)
  if len(j):
   j=j[0];fraction=(p[j-1,1]-6)/(p[j-1,1]-p[j,1]);lons.append(p[j-1,2]+fraction*(p[j,2]-p[j-1,2]))
 due=json.loads((OUT/'due_south_paths.json').read_text());p=np.array(due[0]['points']);p=p[p[:,1]>5.7];ax.plot(p[:,2],p[:,1],color=RED,lw=1.6,zorder=6)
 lon,lat=geojson['waypoints']['IGOGU'];ax.scatter(lon,lat,marker='*',s=110,color=INK,zorder=7);ax.text(lon+.06,lat+.04,'IGOGU',fontsize=10,color=INK)
 ax.annotate('FIR turns east at 6°N',xy=(lon,6),xytext=(93.18,5.85),arrowprops={'arrowstyle':'-','color':'#61557e'},fontsize=9,color='#61557e')
 ax.legend(handles=[Line2D([],[],color=BLUE,label='Original weighted representative paths'),Line2D([],[],color=RED,label='One exact-due-south diagnostic'),Line2D([],[],color='#61557e',ls='--',label='Saved FIR boundary')],loc='lower left',fontsize=8)
 q=S['initial_course_degrees_q025_50_975'];lm=float(np.median(lons));_,_,dx=GEOD.inv(lm,6,lon,6)
 prose(f,.62,.83,f"Original initial-course prior\nNormal 180° ±15°, truncated 150-210°\n\nSampled initial-course distribution\nMedian {q[1]:.2f}° true ground course\nCentral 95%: {q[0]:.2f}-{q[2]:.2f}°\nWithin 1° of due south: {S['initial_course_within_one_degree_due_south_mass']:.2%}\n\nThe displayed path sample crosses 6°N near {lm:.3f}°E (median), about {dx/1000:.0f} km west of the FIR boundary at 94°25'E.",width=49,size=10.5,line=.03)
 prose(f,.62,.39,'The turn begins at IGOGU with finite bank and roll limits. It therefore moves west during the turn before reaching its southerly course. Even an exact 180° course after that maneuver follows a meridian west of the FIR boundary. Following the boundary itself would require a different turn/intercept rule.',width=49,size=10.5,line=.03)
 prose(f,.075,.112,'Course means direction of motion over the ground. ERA5 winds determine the air heading needed to hold it. FIR coordinates are inherited from the historical chart inputs, with their original provenance limitations preserved.',width=150,size=9.4,line=.023)
 (OUT/'initial_path_summary.json').write_text(json.dumps({'posterior_initial_course_quantiles_deg':q,'displayed_paths':len(paths),'displayed_path_median_longitude_at_6N':lm,'displayed_path_median_offset_from_FIR_km':dx/1000,'six_north_statistic':'Representative display-path statistic, not a new independent sample or exact weighted quantile.'},indent=2));footer(f,4);return f
def south_page():
 f=plt.figure(figsize=(14,10));title(f,'100 exact-due-south trajectories | Where rejection occurs','50 constant-altitude and 50 step-climb cases, drawn before BTO/BFO selection; feasible fuel and physical states only')
 a=np.load(OUT/'due_south_100.npz');tr=a['observation_states'];v=a['values'];arcix=np.flatnonzero(OBS.kind.eq('arc'));r=tr[:,arcix,6]-OBS.iloc[arcix].bto_us.to_numpy()
 ax=f.add_axes([.075,.53,.50,.31]);times=['19:41','20:41','21:41','22:41','00:11'];x=np.arange(5)
 for row in r:ax.plot(x,row,color=BLUE,alpha=.13,lw=.65)
 ax.axhspan(-58,58,color='#d9ebdb',alpha=.85);ax.axhline(0,color='#607667',lw=.6);ax.set(xticks=x,xticklabels=times,ylabel='Predicted minus observed BTO (µs)');ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
 ax=f.add_axes([.65,.50,.28,.36]);geo(ax,[88,96.5,-40,-33]);arc(ax);ax.scatter(v[:,7],v[:,6],c=np.repeat([BLUE,RED],50),s=16,alpha=.65,zorder=5);ax.set_title('Positions at fuel exhaustion',fontsize=10);ax.legend(fontsize=7,loc='lower left')
 d=pd.read_csv(OUT/'due_south_100.csv');q=DS['signed_arc_distance_km_min_median_max'];rows=[['18:40 call BFO','100 / 100','Within ±8.6 Hz'],['19:41 BTO','0 / 100',f"{d.first_failure_BTO_us.min():+.1f} to {d.first_failure_BTO_us.max():+.1f} µs; allowed ±58"],['All pre-00:19 SATCOM checks','0 / 100','Earliest rejection always 19:41'],['Continued 00:19 R600 check','0 / 100',f"{d.continued_0019_BTO_residual_us.min():+.1f} to {d.continued_0019_BTO_residual_us.max():+.1f} µs"]]
 table(f.add_axes([.075,.28,.85,.145]),rows,['Check','Passes','Reason / residual'],[.32,.15,.53],9)
 prose(f,.075,.222,f"Exhaustion latitude: {abs(DS['endpoint_latitude_min_median_max'][2]):.2f}-{abs(DS['endpoint_latitude_min_median_max'][0]):.2f}°S; median {abs(DS['endpoint_latitude_min_median_max'][1]):.2f}°S. Longitude: {DS['endpoint_longitude_min_median_max'][0]:.3f}-{DS['endpoint_longitude_min_median_max'][2]:.3f}°E. Distance from the nominal R600 arc at each trajectory's exhaustion altitude: {q[0]:.1f}-{q[2]:.1f} km, median {q[1]:.1f} km, on the longer-range side. These are endpoint geometry comparisons, not the observation-time likelihood.",width=155,size=9.5,line=.023)
 prose(f,.075,.105,'These 100 cases are a diagnostic ensemble, not posterior survivors. Original fuel timing and physical restrictions are retained, and all cases use an exact 180° true ground track after the finite initial turn. Complete parameters, all observation residuals, paths and rejection records are supplied.',width=155,size=9.5,line=.023);footer(f,5);return f
def bound_page():
 g=json.loads((OUT/'due_south_geometric_bound.json').read_text());f=plt.figure(figsize=(14,10));title(f,'Can an exact due-south continuation fit this model?','The 100-case failure is supported by a conservative geometric bound, conditional on the frozen model.')
 ax=f.add_axes([.075,.46,.44,.36]);t=pd.Timestamp('2014-03-07T19:41:02.906Z').timestamp()-T0
 lons=np.linspace(93.7,94.5,120);mins=[minimize_scalar(lambda la:bto(la,lo,41000*.3048,t)-11500,bounds=(-89.9,89.9),method='bounded').fun for lo in lons]
 ax.plot(lons,mins,color=TEAL,lw=1.8,label='Best possible BTO residual at FL410')
 ax.axhspan(-58,58,color='#d9ebdb',alpha=.7,label='Allowed ±58 µs');ax.axhline(58,color='#5b885e',lw=.8)
 ax.axvspan(g['conservative_western_longitude_bound'],94.5,color=RED,alpha=.07)
 ax.axvline(g['conservative_western_longitude_bound'],color=RED,lw=1.5,label='Western limit after prescribed turn');ax.axvline(94.4166667,color='#67557d',ls='--',lw=1,label='IGOGU / FIR meridian')
 ax.set(xlabel='Longitude east (degrees)',ylabel='Minimum 19:41 BTO residual (µs)',xlim=(93.7,94.5),ylim=(-60,310));ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=7.5);ax.spines[['top','right']].set_visible(False)
 prose(f,.57,.82,f"1. The first-turn duration is at most {g['turn_duration_upper_bound_s']:.1f} s.\n\n2. A deliberately loose weather/Mach bound puts ground speed below {g['groundspeed_upper_bound_m_s']:.1f} m/s in the turn.\n\n3. Even pretending its full {g['turn_path_length_upper_bound_km']:.1f} km length is westward, it cannot finish west of {g['conservative_western_longitude_bound']:.4f}°E.\n\n4. A due-south course then holds that longitude. But the easternmost 19:41-compatible point at any latitude, even at FL410, is {g['maximum_compatible_longitude_at_any_latitude_and_FL410']:.4f}°E.",width=49,size=10,line=.027)
 prose(f,.075,.376,f"Thus no exact-due-south continuation of this specified initial turn can satisfy the 19:41 ±58 µs BTO gate within the frozen model. At the conservative longitude bound, the best possible residual is still +{g['minimum_possible_1941_BTO_residual_at_bound_us']:.1f} µs. This conclusion does not depend on a finite random sample missing a rare speed/fuel combination.",width=155,size=10.5,line=.025)
 prose(f,.075,.252,'The scope matters: this does not rule out a different initial turn, a different starting point, later turns, a broader measurement-error model, altered timing calibration, or other flight-model assumptions. It also does not prove that the whole zero-extra-turn class with initial courses 150-210° is impossible. It addresses the exact due-south scenario in question.',width=155,size=10.5,line=.025)
 prose(f,.075,.12,'The bound uses the full bracketing ERA5 cells around IGOGU; trilinear interpolation cannot exceed their temperature/wind component bounds. Its turn-distance bound remains inside that weather box. Code and intermediate bounds are included for independent review.',width=155,size=9.4,line=.023);footer(f,6);return f
def main():
 pages=[first_page(),sensitivity_page(),drift_page(),initial_page(),south_page(),bound_page()]
 names=['seventh_arc_filtered','seventh_arc_assumptions','pleiades_mixture_overlay','initial_paths_FIR','due_south_100','due_south_geometric_bound']
 with PdfPages(OUT/'mh370_igogu_followup.pdf') as pdf:
  for i,(f,name) in enumerate(zip(pages,names)):
   pdf.savefig(f);f.savefig(OUT/(name+'.png'),dpi=150);plt.close(f)
 print(json.dumps({'report':str(OUT/'mh370_igogu_followup.pdf'),'pages':len(pages),'charts':names}))
if __name__=='__main__':main()
