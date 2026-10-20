"""Scientific figures and a clearly qualified analysis report."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,datetime
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from scipy.ndimage import gaussian_filter
from scipy.interpolate import LinearNDInterpolator
from pyproj import Transformer,Geod
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1];O=R/'output';F=R/'figures';F.mkdir(exist_ok=True);D=R/'output/pdf';D.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
purple='#76528f';blue='#007e91';orange='#c7742b';grey='#607484'
g=pd.read_csv(R/'inputs/pleiades_equal_thirds_grid.csv');shape=(g.along_index.max()+1,g.cross_index.max()+1);glon=g.longitude_deg.to_numpy().reshape(shape);glat=g.latitude_deg.to_numpy().reshape(shape);gd=g.equal_thirds_density_per_km2.to_numpy().reshape(shape)
ix=np.argsort(g.equal_thirds_density_per_km2.to_numpy())[::-1];cm=np.cumsum(g.equal_thirds_mass.to_numpy()[ix]);thresholds={p:float(g.equal_thirds_density_per_km2.iloc[ix[np.searchsorted(cm,p)]]) for p in [.5,.9]}
interp=LinearNDInterpolator(g[['longitude_deg','latitude_deg']],g.equal_thirds_density_per_km2,fill_value=0)
polys=[];historic=[];arc7=[]
for pm in ET.parse(R/'inputs/caption_search_areas.kml').findall('.//{*}Placemark'):
 name=pm.find('{*}name')
 if name is not None and name.text=='Ocean Infinity proposed 2024 area':
  for c in pm.findall('.//{*}coordinates'):polys.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))
 elif name is not None and name.text in ['Ocean Infinity 2018 search','Australia/China/Malaysia 2014-2017 search']:
  for c in pm.findall('.//{*}coordinates'):historic.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))
 elif name is not None and name.text=='Arc 7 at 20000ft':
  for c in pm.findall('.//{*}coordinates'):arc7.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))
proj=Transformer.from_crs(4326,'+proj=laea +lat_0=-35 +lon_0=93 +datum=WGS84 +units=m',always_xy=True);inv=Transformer.from_crs(proj.target_crs,4326,always_xy=True)
def axes(ax):
 ax.set(xlim=(88,99),ylim=(-39,-31),xlabel='Longitude (°E)',ylabel='Latitude (°)');ax.grid(alpha=.2);ax.set_aspect(1/np.cos(np.radians(35)))
 for p in historic:ax.plot(p[:,0],p[:,1],color='#92a2a8',lw=.7,alpha=.8)
 for p in arc7:ax.plot(p[:,0],p[:,1],color='#384653',lw=.8,ls=':')
 for p in polys:ax.plot(p[:,0],p[:,1],color=orange,ls='--',lw=1.4)
 ax.contour(glon,glat,gd,levels=[thresholds[.9],thresholds[.5]],colors=purple,linewidths=[1.3,2],linestyles=['--','-'])
def density(ax,lat,lon,w,color=blue,label=''):
 ok=(w>0)&np.isfinite(lat)&np.isfinite(lon);lat=lat[ok];lon=lon[ok];w=w[ok];w=w/w.sum();x,y=proj.transform(lon,lat);edgesx=np.arange(-700000,710001,10000);edgesy=np.arange(-800000,810001,10000)
 h,_,_=np.histogram2d(x,y,bins=[edgesx,edgesy],weights=w);h=gaussian_filter(h,2,mode='constant');vals=np.sort(h.ravel())[::-1];cs=np.cumsum(vals);levels=[]
 for m in [.9,.5]:
  if cs[-1]>=m:levels.append(vals[min(np.searchsorted(cs,m),len(vals)-1)])
 xx,yy=np.meshgrid((edgesx[:-1]+edgesx[1:])/2,(edgesy[:-1]+edgesy[1:])/2);lo,la=inv.transform(xx,yy)
 if levels and max(levels)>0:ax.contour(lo,la,h.T,levels=sorted(set(levels)),colors=color,linewidths=[1.1,1.8][:len(set(levels))])
 return {'regional_grid_mass':float(h.sum()),'Pleiades50_mass':float(w@(interp(lon,lat)>=thresholds[.5])),'Pleiades90_mass':float(w@(interp(lon,lat)>=thresholds[.9])),'weighted_mean_latitude':float(w@lat),'weighted_mean_longitude':float(w@lon)}
def save(fig,name):fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
legend=[Line2D([0],[0],color=blue,label='Flight ensemble: 50% / 90% contours'),Line2D([0],[0],color=purple,label='Pléiades: 50% / 90% contours'),Line2D([0],[0],color=orange,ls='--',label='2024 proposal sketches'),Line2D([0],[0],color='#92a2a8',label='Historic search outlines (sketches)')]
main=json.loads((O/'main_summary.json').read_text()) if (O/'main_summary.json').exists() else None;stats={}
if main:
 z=np.load(O/'main_exhaustion_states.npz');fig,ax=plt.subplots(figsize=(9,6.6));axes(ax);ww=z['weights'];dd=interp(z['end'][:,2],z['end'][:,1]);stats['main_fuel']={'status':'Density unresolved','Pleiades50_mass':float(ww@(dd>=thresholds[.5])),'Pleiades90_mass':float(ww@(dd>=thresholds[.9]))};ax.scatter(z['end'][:,2],z['end'][:,1],s=1,alpha=.055,color=grey);sel=np.argsort(ww)[-180:];ax.scatter(z['end'][sel,2],z['end'][sel,1],s=2+260*ww[sel]/ww.max(),alpha=.65,color=blue);ax.set_title(f"Main route: weighted contributions, density unresolved\nImportance ESS {main['weight_concentration_ESS']:.1f}; largest weight {main['largest_weight']:.1%}");ax.legend(handles=[Line2D([0],[0],marker='o',ls='',color=blue,label='Weighted fuel locations')]+legend[1:],fontsize=9,loc='lower left');fig.text(.12,.015,'Blue sizes show the 180 largest contributions; grey shows the sampled cloud. Density unresolved.',fontsize=8);save(fig,'main_fuel_overlay')
for source,label in [('baseline_eof_a','Earlier IGOGU baseline'),('main_exhaustion_states_eof','Main waypoint route')]:
 f=O/(source+'.npz')
 if not f.exists():continue
 z=np.load(f);fig,axs=plt.subplots(1,2,figsize=(10,5.8));stats[source]={}
 for ax,key,sub in zip(axs,['weights','BFO_envelope_weights'],['R600 range likelihood','Range + final-BFO feasibility envelope']):
  axes(ax);w=z[key]
  if w.sum():stats[source][key]=density(ax,z['values'][:,1],z['values'][:,2],w)
  ax.set_title(sub.replace(' + ',' +\n'),fontsize=11)
 fig.suptitle(label+' — trial impact mixture',fontsize=14)
 if source.startswith('main'):fig.text(.5,.88,'Parent importance ESS 4.8: contours are exploratory',ha='center',fontsize=10,color='#984d28')
 fig.legend(handles=legend,loc='lower center',ncol=2,fontsize=9);fig.subplots_adjust(bottom=.18,top=.81,wspace=.30);save(fig,source+'_overlay')
sp=pd.read_csv(O/'spatial_controls.csv');dest=pd.read_csv(O/'destination_alignment.csv');top=dest[dest.angle_tolerance_deg==1].head(5)
fig,axs=plt.subplots(1,2,figsize=(10,4.7));ss=sp[(sp.radius_nm==5)&(sp.measure=='R600')];
for control,col,label in [('pair_translation',blue,'Fixed BULVA-ISBIX pair'),('full_catalog_rotation_best_ordered_pair',orange,'Best comparable catalog pair')]:
 s=ss[ss.control==control].sort_values('halfwidth_degree_equivalent');axs[0].plot(s.halfwidth_degree_equivalent,s.p,'o-',color=col,label=label)
axs[0].axhline(.05,color=grey,ls=':');axs[0].set(xlabel='Control displacement half-width (degrees)',ylabel='Conditional randomization p',title='Waypoint selection changes the control');axs[0].legend(fontsize=8)
short=top.label.replace({'Vostok Skiway':'Vostok','Amundsen–Scott South Pole Station Airport':'South Pole','Union Glacier Blue-Ice Runway':'Union Glacier','Patriot Hills Airport':'Patriot Hills'})
axs[1].barh(short.iloc[::-1],top.weighted_alignment_fraction.iloc[::-1],color=blue);axs[1].set(xlabel='Weighted fraction within 1°',title='Distant alignment: earlier IGOGU ensemble',xlim=(0,.5));axs[1].tick_params(axis='y',labelsize=8);fig.tight_layout();save(fig,'controls_and_destinations')
# Route witness, exact points from a fine navigation integration.
import sys
sys.path.insert(0,str(R/'code'))
from model import Engine,OBS
witness=np.load(O/'main_route_witness.npz');eng=Engine(1,30,fine=True);v,tr,path=eng.trace_physical(witness['physical'],3,0);np.savez_compressed(O/'main_route_witness_trace.npz',values=v,observations=tr,path=path)
rows=OBS.copy();rows['predicted_bto_us']=tr[:,6];rows['predicted_bfo_hz']=tr[:,7];rows['bto_residual_us']=tr[:,6]-OBS.bto_us;rows['bfo_residual_hz']=tr[:,7]-OBS.bfo_hz;rows.to_csv(O/'main_route_witness_residuals.csv',index=False)
fig,ax=plt.subplots(figsize=(7,8));land=json.loads((R/'inputs/land.geojson').read_text())
for feature in land['features']:
 geom=feature['geometry'];pp=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
 for p in pp:ax.add_patch(Polygon(p[0],fc='#e9eded',ec='#bac5c8',lw=.4))
ax.plot(path[:,2],path[:,1],color=blue,lw=1.6);cat=pd.read_csv(R/'inputs/waypoint_catalog.csv').set_index('name');names=['MEKAR','NILAM','IGOGU','BULVA','ISBIX','RUNUT']
for name in names:
 q=cat.loc[name];ax.scatter(q.longitude,q.latitude,s=24,color=orange if name=='RUNUT' else '#25394e');offset={'MEKAR':(28,18),'NILAM':(-55,14),'IGOGU':(-65,27),'BULVA':(15,-7),'ISBIX':(15,-6),'RUNUT':(-55,0)}[name];ax.annotate(name,(q.longitude,q.latitude),xytext=offset,textcoords='offset points',fontsize=9,arrowprops=dict(arrowstyle='-',lw=.5,color=grey))
ax.scatter(v[7],v[6],marker='x',s=55,color=blue);ax.set(xlim=(82,110),ylim=(-41,11),xlabel='Longitude (°E)',ylabel='Latitude (°)',title='A feasible route witness\nExample only - not a posterior mode');ax.set_aspect(1);ax.grid(alpha=.2);save(fig,'main_route_witness')
(O/'map_statistics.json').write_text(json.dumps(stats,indent=2))

# Separate destination panels use the same catalog and rotation control.
mdest=pd.read_csv(O/'main_destination_alignment.csv');mtop=mdest[mdest.angle_tolerance_deg==1].head(4)
fig,axs=plt.subplots(1,2,figsize=(10,4.4))
for ax,tab,title in [(axs[0],top.head(4),'Earlier IGOGU ensemble'),(axs[1],mtop,'Main route — exploratory')]:
 labels=tab.label.replace({'Vostok Skiway':'Vostok','Amundsen–Scott South Pole Station Airport':'South Pole','Union Glacier Blue-Ice Runway':'Union Glacier','Patriot Hills Airport':'Patriot Hills','Navaid':'South Pole navaid'})
 ax.barh(labels.iloc[::-1],tab.weighted_alignment_fraction.iloc[::-1],color=blue);ax.set(xlim=(0,.6),xlabel='Fraction within 1°',title=title);ax.tick_params(axis='y',labelsize=9)
fig.tight_layout();save(fig,'destination_comparison')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';pdfmetrics.registerFont(TTFont('DV',font));pdfmetrics.registerFont(TTFont('DVB',bold))
from reportlab.platypus import Table,TableStyle
W,H=595.28,841.89;c=canvas.Canvas(str(D/'MH370_waypoint_hypotheses.pdf'),pagesize=(W,H));c.setTitle('MH370: waypoint hypotheses, RUNUT and conditional impact maps');page=[0];layout=[]
style=ParagraphStyle('body',fontName='DV',fontSize=10,leading=15,textColor=HexColor('#24384b'))
main=json.loads((O/'main_summary.json').read_text());audit=json.loads((R/'qa/final_audit.json').read_text());eof={name:json.loads((O/(name+'_summary.json')).read_text()) for name in ['baseline_eof_a','main_exhaustion_states_eof']}
assert all('weather_sha256' in x for x in eof.values()),'Wait for complete weather-extended EoF results'
def para(text,y,size=10):
 st=ParagraphStyle('x',parent=style,fontSize=size,leading=size*1.47);p=Paragraph(text,st);ww,hh=p.wrap(W-84,1000);p.drawOn(c,42,y-hh);return y-hh-12
def start(title,kicker='MH370 / conditional analysis'):
 page[0]+=1;c.setFillColor(HexColor('#607484'));c.setFont('DVB',8);c.drawString(42,H-40,kicker.upper());c.setFillColor(HexColor('#172f46'));c.setFont('DVB',19);c.drawString(42,H-73,title);return H-100
def finish(y):
 assert y>42,(page[0],y)
 layout.append({'page':page[0],'lowest_content_y':y});c.setFont('DV',7);c.setFillColor(HexColor('#607484'));c.drawString(42,25,'19 September 2026 | Conditional research analysis; no calibrated wreckage claim');c.drawRightString(W-42,25,str(page[0]));c.showPage()
def pic(name,y,height=310):
 from PIL import Image
 p=F/(name+'.png');im=Image.open(p);width=min(W-84,height*im.width/im.height);hh=width*im.height/im.width;c.drawImage(str(p),(W-width)/2,y-hh,width,hh);return y-hh-14
def table(rows,y,widths=None):
 st=ParagraphStyle('cell',parent=style,fontSize=8.5,leading=12)
 data=[[Paragraph(str(v),st) for v in row] for row in rows];t=Table(data,colWidths=widths or [(W-84)/len(rows[0])]*len(rows[0]),hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e9eff2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.6,HexColor('#607484')),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#d8e0e4'))]));ww,hh=t.wrap(W-84,1000);t.drawOn(c,42,y-hh);return y-hh-14

y=start('What the calculations establish')
y=para('<b>The main waypoint route is feasible, but its probability density is not yet reliable.</b> A trajectory through MEKAR–NILAM–IGOGU–BULVA–ISBIX, with three subsequent turns, passes the declared pre-exhaustion gates at a one-second integration step. Its exhaustion point is approximately 35.20°S, 92.40°E.',y)
y=para(f"The final independent calculation used {main['total_proposals']:,} proposals and retained {main['retained_contributions']:,} positive contributions. Their effective sample size (ESS) is only {main['weight_concentration_ESS']:.1f}, and one trajectory carries {main['largest_weight']:.1%} of the weight. That is insufficient for a stable search probability map.",y)
y=pic('main_route_witness',y,340)
y=para('<b>RUNUT remains unresolved:</b> no tested candidate passes all its additional conditions. <b>Distant alignment:</b> the strongest main-route candidate is not unusual after searching the full catalog. End-of-flight maps below are conditional sensitivity calculations and inherit the weak main-route sampling.',y,9)
finish(y)

y=start('Fuel exhaustion and the Pléiades PDF')
y=pic('main_fuel_overlay',y,365)
y=table([['Present trial weights inside Pléiades regions','50% region','90% region'],['Fuel exhaustion','8.7%','78.1%'],['Impact: R600 only / also BFO envelope','7.8% / 1.9%','40.3% / 14.2%']],y,[290,110,111])
y=para('Blue points are weighted contributions, not credible-region boundaries. The apparent concentration near the southern Indian Ocean is compatible geometrically with parts of the Pléiades source contours, but the route calculation cannot yet establish the amount of probability overlap reliably.',y)
y=para('Purple lines show 50% and 90% regions of the archived equal-third BRAN2016, OSCAR v2 Final and GLORYS12/WAVERYS source mixture. This is conditional on the proposed Pléiades object association and the source-model assumptions. It is overlaid, not multiplied into the satellite/fuel likelihood.',y)
y=para('Orange lines are 2024 proposal sketches; grey lines are historical search outlines from the supplied caption map. Neither is a detection-quality coverage mask or the authoritative boundary of the latest remaining search area. The dotted line is that map’s 20,000-ft seventh arc.',y,9)
finish(y)

y=start('Estimator rules and numerical checks')
y=table([['Quantity','Declared model / gate'],['Route and turns','Finite-bank waypoint guidance; 0–4 extra turns after ISBIX, equal prior mass. Anticipated IGOGU fly-by, not exact coordinate overflight.'],['Mach and altitude','Initial Mach 0.76–0.85; later knots bounded 0.74–0.86. Initial altitude 31,000–37,000 ft. Constant altitude or two 1,000–2,000-ft climbs, equal prior mass.'],['BTO and arc timing','Trusted early E/F/G BTO plus later observations; R1200 range gate ±58 µs. Cross each nominal frozen range surface within ±60 s of its observation.'],['Pre-exhaustion BFO','Every retained residual within ±8.6 Hz. A/F/G early BFO retained; E excluded for oscillator warm-up. Calls use one mean likelihood each, with individual residual gates.'],['Fuel exhaustion','Triangular timing factor: 00:16:00–00:19:00 UTC, mode 00:17:30. Inverse fuel-to-time transformation retains its Jacobian.'],['RUNUT only','Extra geometric condition: exhaustion outside the nominal 00:11 surface and inside the nominal 00:19 surface, at the exhaustion altitude.']],y,[125,W-84-125])
y=para('Importance proposals have full prior support; ordered-turn and coordinate Jacobians, proposal densities and randomized fine-evaluation inclusion probabilities are retained. Final A/B integration draws are separate from proposal-training draws. Equal prior weights over the ten turn/altitude classes are preserved.',y,9)
a=audit['main_numerics'];y=para(f"<b>Numerical check:</b> the 48 largest contributions contain {a['checked_weight']:.1%} of sampled weight. All 48 still pass at one-second integration. Maximum endpoint change is {a['max_endpoint_difference_m']:.0f} m, maximum BFO change {a['max_BFO_Hz_difference']:.4f} Hz and maximum arc-crossing change {a['max_nominal_crossing_sec_difference']:.3f} s.",y,9)
r=main['replicates'];y=para(f"<b>Sampling check fails:</b> replicas have ESS {r[0]['weight_concentration_ESS']:.1f} and {r[1]['weight_concentration_ESS']:.1f}; their estimated normalizing constants differ by a factor of {np.exp(abs(r[0]['log_evidence_estimate']-r[1]['log_evidence_estimate'])):.1f}. Earlier refinement rounds continued finding much higher-weight regions. Zero hits for 0–2 turns do not prove those classes impossible.",y,9)
finish(y)

y=start('Main route: conditional impact mixture')
y=pic('main_exhaustion_states_eof_overlay',y,315)
e=eof['main_exhaustion_states_eof'];y=table([['Calculation','Result'],['Parent resampling / simulations',f"{e['parent_draws']:,} parent draws × 12 families = {e['integrations']:,} integrations"],['Impact / final-range-compatible',f"{e['impact_count']:,} modeled impacts; {e['range_pass_count']:,} also airborne at first contact and within the R600 range gate"],['Range + final-BFO envelope',f"{e['range_and_BFO_envelope_count']:,} satisfy both final BFOs for some allowed oscillator offsets"],['Independent information',f"Source ESS {e['source_weight_ess']:.1f}; source-group ESS after R600 weighting {e['source_group_ess']:.1f}. Many descents from one parent do not create new flight-path information."]],y,[160,W-84-160])
y=para('Each exhaustion state is combined with each EoF family and sampled control histories. Impact weights are proportional to parent weight × family prior × terminal likelihood, then normalized over modeled, admissible impacts. The family prior is explicitly 1/12: a sensitivity mixture, not calibrated probabilities of pilot actions or aircraft behavior.',y,9)
y=para(f"Unresolved integrations: {e['status_counts']['3']:,} reach the speed/altitude envelope and {e['status_counts']['5']:,} reach the near-vertical coordinate limit. Weather-coverage failures: {e['status_counts']['4']}. These cases have no modeled impact distribution; normalization conditions on the retained model domain.",y,9)
finish(y)

y=start('EoF controls and the earlier baseline')
y=pic('baseline_eof_a_overlay',y,300)
e=eof['baseline_eof_a'];y=para(f"For comparison, the earlier IGOGU baseline, reweighted to the revised exhaustion-time factor, supplies {e['integrations']:,} EoF integrations: {e['range_pass_count']:,} pass the final range test and {e['range_and_BFO_envelope_count']:,} also pass the BFO feasibility envelope. Its original importance ESS was about 345; resampling does not increase that information. This baseline is shown separately from the new route hypothesis.",y,9)
y=table([['EoF dimension','Recovered range used'],['Aerodynamics / controls','Two drag polars × initial trim, best glide, 1/3/6 positive-lift targets, or 6 signed-lift targets = 12 families.'],['Control limits','Bank ±60°; CL targets 0.05–1.2 or −0.3–1.2; later changes 10–900 s; CL rate 0.05/s; roll rate 3°/s.'],['Integration domain','One-hour maximum, 500–60,000-ft ERA5 weather with 500-ft weather held below that level; TAS 50–700 m/s; attached-flow point mass. APU restart disabled.']],y,[135,W-84-135])
y=para('The weather extension uses genuine archived ERA5 pressure-level data through 02:00 UTC; every overlapping value agrees exactly with the pinned cruise grid. RK4 step 0.125 s versus 0.03125 s gives identical outcomes in 48 check cases and at most 0.45 m impact-position change.',y,9)
finish(y)

y=start('RUNUT: a separate conditional test')
y=para('The main ensemble was never forced through RUNUT. Three checks distinguish a direct ISBIX–RUNUT leg, free-turn trajectories that naturally pass nearby, and a targeted detour search. Absence from a poorly sampled ensemble is not a probability-zero result.',y)
r=audit['RUNUT_detour'];y=table([['Test','Observed outcome'],['Direct ISBIX–RUNUT prefix','Best numerical compromise still misses the 19:41 nominal arc within the ±60 s window by about 37.4 µs in range, and slightly violates an early gate. This is a failed fit, not a certified constrained minimum.'],['Natural passage in main sample','No retained contribution passes within 5, 10 or 20 NM of RUNUT. Main-source ESS is only 4.8; no reliable upper bound on true passage probability follows.'],['Four-turn targeted detour',f"Closest approach {r['closest_nm']:.3f} NM, just outside 5 NM. Maximum BFO residual {r['maximum_BFO_residual_Hz']:.2f} Hz exceeds the 8.6-Hz gate. It also fails arc-crossing criteria."],['Fuel time / geometric strip','The detour exhausts at 00:17:30 and lies between the nominal 00:11 and 00:19 arcs. Passing these two conditions does not repair its other failures.']],y,[130,W-84-130])
y=para(f"The strip check evaluates both frozen range surfaces at the exhaustion latitude, longitude and altitude. The tested detour is +{r['0011_frozen_BTO_residual_us']:.1f} µs outside the 00:11 surface and {abs(r['0019_frozen_BTO_residual_us']):.1f} µs inside the 00:19 surface. Time membership alone was not used as a substitute for this geometry.",y,9)
y=para('<b>Final-contact treatment:</b> EoF trajectories must be airborne at 00:19:29.416. Corrected R600 BTO is 18,400 µs, sigma 63 µs, gate ±126 µs. Final BFOs at 00:19:29.416 and 00:19:37.443 use logged carriers 36F8 and 36F6.',y,9)
y=para('The extra BFO panel requires some decaying oscillator offsets 0 ≤ b₂ ≤ b₁ ≤ 130 Hz that leave both residuals within ±8.6 Hz. This is an existence test, not an assumed probability law for oscillator warm-up. Neither this envelope nor the finite RUNUT searches establish an impossibility proof.',y,9)
finish(y)

y=start('Ordered-waypoint controls')
y=pic('controls_and_destinations',y,245)
y=para('In the earlier IGOGU-conditioned ensemble, about 99.1% of weighted paths pass BULVA then ISBIX within 5 NM. Controls translate that fixed pair locally, or rotate the whole catalog and select its best comparable ordered pair. The latter accounts for having noticed the pair after inspecting the trajectories.',y)
y=table([['±5° control; 5-NM radius','Original weights','R600 weights'],['Fixed-pair translation p','0.0019','0.0021'],['Best catalog pair p','0.0449','0.0618'],['Catalog p using larger-sample observed statistic','0.0670','0.0663']],y,[280,115,116])
y=para('Each setting uses 10,000 spatial controls. Catalog geometry is preserved under common longitude rotations; the search includes ordered pairs separated by 150–400 NM, excluding the conditioning point IGOGU. ±1°/±2° windows and 10/20-NM radii are retained as sensitivities.',y,9)
y=para('The last row shows sensitivity to a small resampling shift in the observed passage fraction; it is not a calibrated bootstrap correction. The near-0.05 result is therefore not robust. The full synthetic-data generation and trajectory-reconstruction null has not been completed: a reliable reconstruction estimator is needed before that calibration would be meaningful.',y,9)
finish(y)

y=start('Distant destinations and the control')
y=pic('destination_comparison',y,255)
y=table([['Ensemble / candidate','Within 1°','Catalog-adjusted p'],['Main / Patriot Hills','48.6%','0.355'],['Main / Union Glacier','48.0%','0.397'],['Main / South Pole','35.1%','1.000'],['Earlier baseline / Vostok','39.3%','0.474']],y,[290,100,121])
y=para('The screen extends the final ground course beyond exhaustion and tests 6,587 regional waypoints, worldwide medium/large airports and Antarctic facilities. Candidates must be 1–12,000 km beyond exhaustion. The control uses 2,000 common longitude rotations and takes the maximum over the complete catalog each time.',y,9)
y=para('The primary tolerance is 1°, with 2° and 5° sensitivities. WGS84 checks give 48.7% toward Patriot Hills and 39.0% toward Vostok, close to the spherical screen. The main calculation uses a systematic weighted resample; its source ESS remains 4.8. These percentages are therefore descriptive of the present numerical sample.',y,9)
y=para('<b>No supported destination inference emerges.</b> A large alignment fraction can occur for some Antarctic location after selecting among many candidates. These controls do not support intended flight to Patriot Hills, Vostok or the South Pole, and a directional alignment makes no claim about reachability or landing capability. Catalog entries are current, not a fully authenticated 2014 inventory.',y,9)
finish(y)

y=start('Search status, limits and reproducibility')
y=para('<b>Latest verified official plan:</b> Malaysia’s 29 June 2026 statement extends the agreement through 30 June 2027, identifies 7,428.54 km² remaining, and anticipates assets in the November 2026–April 2027 weather window. An authoritative georeferenced polygon for the remaining area and a detection-quality coverage mask were not available. An exact latest-search overlap percentage cannot be computed from the supplied sketches.',y)
y=para('<b>Primary references</b><br/>• <link href="https://www.mot.gov.my/my/Kenyataan%20Media/Tahun%202026/29%20JUN%2026_KENYATAAN%20MEDIA%20MENTERI%20PENGANGKUTAN%20PERLANJUTAN%20PERJANJIAN%20ANTARA%20KERAJAAN%20MALAYSIA%20%26%20OCEAN%20INFINITY%20BAGI%20MENGESAN%20BANGKAI%20PESAWAT%20MH370.pdf">Malaysian Ministry of Transport, 29 June 2026 extension</link>.<br/>• <link href="https://www.atsb.gov.au/sites/default/files/media/5773389/ae-2014-054_mh370-search-and-debris-update_aug2017.pdf">ATSB, Search and debris examination update</link>: final-contact descent and oscillator analysis.<br/>• <link href="https://ourairports.com/data/">OurAirports</link>: candidate inventory.<br/>• Archived user-supplied Pléiades numerical grids, prior IGOGU estimator and EoF configuration: identifiers and source files retained in the analysis bundle.',y,9)
y=para('<b>Reproduce and inspect:</b> README.md distinguishes final importance draws from training and pilot runs. The bundle includes source code, priors, fixed proposals, raw weighted contributions, terminal controls, null distributions, source maps and numerical checks. CHECKPOINT.json records file hashes and any restored dependencies. The frozen archive is the result of this run, not a background computation that continues after delivery.',y,9)
y=para('Main outputs: main_summary.json; main_exhaustion_states.npz; main_exhaustion_states_eof.npz; spatial_controls.csv; main_destination_alignment.csv; and qa/final_audit.json. Figures are also provided separately. Impact contours use 20-km smoothing in an equal-area projection; that smoothing is visual, not additional evidence.',y,9)
y=para('<b>Remaining limits:</b> weak and unstable main importance weights; unvisited-mode risk; no complete synthetic reconstruction calibration; simplified fuel/thrust and attached-flow flight physics; out-of-model terminal trajectories; unauthenticated historical waypoint validity; uncertain Pléiades object association; and unavailable latest search/detection polygons. Feasibility has been demonstrated for the main route. A calibrated location PDF and a definitive RUNUT exclusion have not.',y,9)
finish(y);c.save();(R/'qa/report_layout.json').write_text(json.dumps(layout,indent=2));print(str(D/'MH370_waypoint_hypotheses.pdf'))
