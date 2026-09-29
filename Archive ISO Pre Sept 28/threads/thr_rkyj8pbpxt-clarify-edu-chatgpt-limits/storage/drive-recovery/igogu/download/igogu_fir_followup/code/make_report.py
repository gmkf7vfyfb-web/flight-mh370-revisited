"""Scientific figures and a concise recovery report from saved results only."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fir_model import HERE,OUT,BASE,OBS,T0,LON,LAT
sys.path.insert(0,str(HERE.parents[1]/'igogu_followup/code'))
from satellite_check import bto,T7,BTO7

INK='#203648';TEAL='#007f85';BLUE='#376bb1';ORANGE='#bc6330';PURPLE='#806194';MUTED='#536777'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelcolor':INK,'axes.titlecolor':INK,'pdf.fonttype':42})
LAND=json.loads((BASE/'inputs/land.geojson').read_text());cat=pd.read_csv(HERE.parent/'inputs/waypoint_catalog.csv').set_index('name')
grid=pd.read_csv(OUT/'early_turn_fit_grid.csv').set_index('id');epaths={r['id']:np.array(r['points']) for r in json.loads((OUT/'early_turn_paths.json').read_text())}
full=np.load(OUT/'later_gate_fit_fine.npz');par=full['parameters'];path=full['path'];tr=full['observation_states'];v=full['values']
validation=json.loads((HERE.parent/'qa/fit_numerical_validation.json').read_text());later=validation['later']
wp=pd.read_csv(OUT/'waypoint_exact_shortlist.csv').set_index('name')
def utc(t,seconds=False):return pd.Timestamp(T0+t,unit='s',tz='UTC').strftime('%H:%M:%S' if seconds else '%H:%M')
def geo(ax,b):
 ax.set(xlim=b[:2],ylim=b[2:]);ax.set_facecolor('#f5f8fa');ax.set_aspect(1/np.cos(np.radians(np.mean(b[2:]))))
 for fe in LAND['features']:
  g=fe['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for p in polys:
   xy=np.array(p[0]);
   if xy[:,0].max()<b[0] or xy[:,0].min()>b[1] or xy[:,1].max()<b[2] or xy[:,1].min()>b[3]:continue
   ax.add_patch(Polygon(xy,facecolor='#e8e8e0',edgecolor='#aab2ad',lw=.5,zorder=0))
 ax.grid(color='#dbe3e9',lw=.55);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}°E'));ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{abs(y):g}°'+('S' if y<0 else 'N')))
 ax.tick_params(labelsize=8)
def arc(ax,time,value,color=PURPLE,label=None,ls='--'):
 lat=np.linspace(*ax.get_ylim(),250);lon=[]
 for la in lat:
  try:lon.append(brentq(lambda lo:bto(la,lo,35000*.3048,time)-value,60,125))
  except ValueError:lon.append(np.nan)
 ax.plot(lon,lat,color=color,ls=ls,lw=1,label=label,zorder=2)
def points(ax,names,offsets=None):
 for name in names:
  r=cat.loc[name];ax.scatter(r.longitude,r.latitude,color=INK,s=17,marker='D',zorder=6)
  dx,dy=(offsets or {}).get(name,(5,4));ax.annotate(name,(r.longitude,r.latitude),xytext=(dx,dy),textcoords='offset points',fontsize=8,color=INK,zorder=8)
def save(f,name):
 f.savefig(OUT/(name+'.png'),dpi=190,bbox_inches='tight');f.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(f)
def early_figure():
 f=plt.figure(figsize=(12.4,7.6));ax=f.add_axes([.03,.09,.45,.84]);geo(ax,[92.7,98.2,-1.55,8.1])
 ax.plot([LON,LON,97.5],[8.1,6,6],color='#4b6452',lw=1.7,label='FIR boundary')
 ax.plot([LON,LON],[6,-1.55],color='#4b6452',lw=.85,ls=':',label='Meridian extension below 6°N')
 for i,c,label in [(13,TEAL,'Second turn free; M 0.82'),(31,ORANGE,'Second turn at 6°N; M 0.82'),(32,BLUE,'At 6°N; late M optimized')]:
  p=epaths[i];ax.plot(p[:,2],p[:,1],color=c,lw=1.8,label=label,zorder=4);r=grid.loc[i]
  ax.scatter(r.arc_lon,r.arc_lat,color=c,s=30,zorder=5);ax.scatter(r.second_turn_lon,r.second_turn_lat,color=c,s=32,marker='s',zorder=5)
 arc(ax,float(OBS.loc[OBS.kind.eq('arc'),'time_s'].iloc[0]),11500,label='19:41 nominal BTO arc, FL350')
 points(ax,['IGOGU','NOPEK','BULVA','ISBIX'],{'NOPEK':(7,0),'IGOGU':(-48,5),'BULVA':(-42,4),'ISBIX':(-35,7)})
 ax.annotate('6°N corner',(LON,6),xytext=(12,-9),textcoords='offset points',fontsize=8)
 ax.set_title('Early trajectories to 19:41',loc='left',fontweight='bold',fontsize=12)
 ax.legend(loc='lower left',bbox_to_anchor=(-.04,-.16),fontsize=7.4,frameon=False,ncol=2)
 bx=f.add_axes([.53,.53,.43,.39]);geo(bx,[93.95,96.13,6.4,7.85]);bx.plot([95.976388889,LON],[6.756388889,LAT],ls='--',color='#707b88',label='N571')
 bx.plot([LON,LON],[6.4,7.85],color='#4b6452',lw=1.4);p=epaths[13];ix=p[:,1]>6.4;bx.plot(p[ix,2],p[ix,1],color=TEAL,lw=2)
 bx.scatter(p[0,2],p[0,1],marker='s',color=TEAL,s=30);bx.annotate('Turn starts\n18:36:05',(p[0,2],p[0,1]),xytext=(35,18),textcoords='offset points',arrowprops={'arrowstyle':'-','color':TEAL},fontsize=8,color=TEAL)
 points(bx,['IGOGU','ANOKO','NOPEK','NILAM'],{'IGOGU':(-44,7),'ANOKO':(-45,3),'NOPEK':(-45,3),'NILAM':(-38,-12)})
 bx.set_title('Turn anticipated by 15.3 NM; due-south rollout at 7.260°N',fontsize=10)
 cx=f.add_axes([.56,.15,.39,.25])
 for i,c,label in [(13,TEAL,'Free second turn'),(31,ORANGE,'6°N; constant Mach'),(32,BLUE,'6°N; optimized Mach')]:
  p=epaths[i];cx.plot(p[:,0],np.degrees(p[:,5])%360,color=c,lw=1.4,label=label)
 cx.axvspan(float(OBS.iloc[0].time_s),float(OBS.loc[OBS.kind.eq('call1'),'time_s'].max()),color='#afb9c5',alpha=.35)
 cx.set(xlim=(950,4740),ylim=(175,215),ylabel='True ground course (degrees)');cx.xaxis.set_major_formatter(FuncFormatter(lambda t,_:utc(t)));cx.grid(alpha=.2);cx.set_title('Southbound during the 18:40 call',fontsize=10)
 save(f,'early_FIR_turns')
def full_figure():
 f=plt.figure(figsize=(12.4,8));ax=f.add_axes([.035,.07,.39,.88]);geo(ax,[75,111,-40,10])
 for _,r in OBS.loc[OBS.kind.eq('arc')].iterrows():arc(ax,r.time_s,r.bto_us,color='#b7a8c4')
 arc(ax,T7,BTO7,color=PURPLE,label='R600 nominal arc, FL350')
 ax.plot(path[:,2],path[:,1],color=TEAL,lw=1.8,zorder=4,label='Feasible local example')
 for ti,label in [(par[12],'Second turn'),(par[13],'Third turn')]:
  lo=np.interp(ti,path[:,0],path[:,2]);la=np.interp(ti,path[:,0],path[:,1]);ax.scatter(lo,la,s=23,marker='s',color=TEAL,zorder=6);ax.annotate(label+' '+utc(ti),(lo,la),xytext=(7,2),textcoords='offset points',fontsize=7.5)
 ax.scatter(v[7],v[6],color=TEAL,s=35,zorder=7);ax.annotate('Fuel exhausted\n00:17:30',(v[7],v[6]),xytext=(9,15),textcoords='offset points',fontsize=8)
 rp=later['R600_kinematic_position'];ax.plot([v[7],rp[1]],[v[6],rp[0]],color=ORANGE,lw=2,zorder=6);ax.scatter(rp[1],rp[0],marker='x',color=ORANGE,s=35,zorder=6)
 handles,labels=ax.get_legend_handles_labels();handles.insert(0,Line2D([],[],color='#b7a8c4',ls='--'));labels.insert(0,'Earlier arcs: 19:41 to 00:11');ax.legend(handles,labels,loc='lower left',fontsize=6.7,frameon=False);ax.set_title('Three turns total; constant FL350',fontsize=11,fontweight='bold')
 times=np.array([par[0],4668,8268,11868,15468,19068,21318]);mach=np.r_[par[2],par[20:26]]
 bx=f.add_axes([.48,.66,.47,.27]);bx.plot(times,mach,'o-',color=TEAL,lw=1.6,ms=4);bx.set(ylim=(.728,.87),ylabel='Mach');bx.grid(alpha=.22);bx.xaxis.set_major_formatter(FuncFormatter(lambda t,_:utc(t)));bx.set_title('This fit needs large speed changes',loc='left',fontsize=11,fontweight='bold')
 bx.text(.01,.94,'Largest knot changes: 5.3, 7.5 and 7.7 prior standard deviations',transform=bx.transAxes,fontsize=8,color=ORANGE,va='top')
 cx=f.add_axes([.48,.39,.47,.19]);arcsel=OBS.kind.eq('arc').to_numpy();cx.axhspan(-58,58,color='#ddecdc');cx.axhline(0,color='#778b7e',lw=.7);cx.plot(OBS.loc[arcsel,'time_s'],tr[arcsel,6]-OBS.loc[arcsel,'bto_us'],'o-',color=BLUE,ms=4);cx.set(ylabel='BTO residual (µs)',ylim=(-70,70));cx.xaxis.set_major_formatter(FuncFormatter(lambda t,_:utc(t)));cx.grid(alpha=.2)
 dx=f.add_axes([.48,.12,.47,.19]);dx.axhspan(-8.6,8.6,color='#ddecdc');dx.axhline(0,color='#778b7e',lw=.7);dx.scatter(OBS.time_s,tr[:,7]-OBS.bfo_hz,s=12,color=BLUE);dx.set(ylabel='BFO residual (Hz)',ylim=(-10,11));dx.xaxis.set_major_formatter(FuncFormatter(lambda t,_:utc(t)));dx.grid(alpha=.2)
 dx.text(.01,.95,'Every burst checked; tightest margin only 0.03 Hz',transform=dx.transAxes,va='top',fontsize=8,color=ORANGE)
 for a in [bx,cx,dx]:a.set_xlim(par[0],21318);a.set_xticks([1068,4668,8268,11868,15468,19068,21318]);a.tick_params(axis='x',labelsize=7)
 save(f,'full_FIR_feasible_example')
def waypoint_figure():
 f=plt.figure(figsize=(12.4,7.3));ax=f.add_axes([.035,.09,.39,.85]);geo(ax,[91.8,97.0,-.8,8.05])
 old=json.loads((BASE/'output/representative_paths.json').read_text())
 for item in old[:180]:
  p=np.array(item['points']);ax.plot(p[:,2],p[:,1],color=BLUE,alpha=.10,lw=.6,zorder=2)
 ax.plot([LON,LON,97.0],[8.05,6,6],color='#4b6452',lw=1.3)
 p=epaths[13];ax.plot(p[:,2],p[:,1],color=TEAL,lw=1.8,zorder=4,label='New FIR-intercept example')
 points(ax,['IGOGU','ANOKO','NOPEK','BEDAX','BULVA','ISBIX'],{'IGOGU':(-45,5),'ANOKO':(5,3),'NOPEK':(5,3),'BEDAX':(-44,3),'BULVA':(-45,3),'ISBIX':(-41,3)})
 ax.set_title('Existing paths pass BULVA and ISBIX closely',fontsize=10,fontweight='bold');ax.legend(handles=[Line2D([],[],color=BLUE,label='Selected original paths (context)'),Line2D([],[],color=TEAL,label='New FIR-intercept example')],loc='lower left',bbox_to_anchor=(-.08,-.13),fontsize=7.2,frameon=False)
 bx=f.add_axes([.52,.17,.43,.71]);names=['BULVA','ISBIX','BEDAX','ANOKO','NOPEK','MUTMI'];yy=np.arange(len(names))
 for q,(radius,c) in enumerate([(5,TEAL),(10,BLUE),(20,'#b5c5d8')]):bx.barh(yy+(q-1)*.23,[100*wp.loc[n,f'R600_within_{radius}NM'] for n in names],height=.21,color=c,label=f'Within {radius} NM')
 bx.set(yticks=yy,yticklabels=names,xlim=(0,102),xlabel='Share of the R600-weighted finite measure (%)');bx.invert_yaxis();bx.grid(axis='x',alpha=.2);bx.legend(loc='lower right',fontsize=8);bx.spines[['top','right']].set_visible(False)
 bx.set_title('Exact sums over all 1,710,701 saved survivors',fontsize=11,fontweight='bold',loc='left')
 save(f,'waypoint_proximity')

def build_pdf():
 font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
 pdfmetrics.registerFont(TTFont('DejaVu',font));pdfmetrics.registerFont(TTFont('DejaVu-Bold',bold))
 styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyX',fontName='DejaVu',fontSize=9.1,leading=13,textColor=colors.HexColor(INK),spaceAfter=8))
 styles.add(ParagraphStyle(name='SmallX',fontName='DejaVu',fontSize=8,leading=11,textColor=colors.HexColor(MUTED),spaceAfter=7))
 styles.add(ParagraphStyle(name='TitleX',fontName='DejaVu-Bold',fontSize=17,leading=21,textColor=colors.HexColor(INK),spaceAfter=10))
 styles.add(ParagraphStyle(name='SubX',fontName='DejaVu-Bold',fontSize=11,leading=15,textColor=colors.HexColor(INK),spaceAfter=7))
 story=[];W=A4[0]-76
 def P(s,style='BodyX'):return Paragraph(s,styles[style])
 def title(s):story.append(P(s,'TitleX'))
 def para(s,small=False):story.append(P(s,'SmallX' if small else 'BodyX'))
 def chart(name,h):story.append(Image(str(OUT/(name+'.png')),width=W,height=h,kind='proportional'));story.append(Spacer(1,8))
 def table(rows,widths):
  data=[[P(str(x),'SmallX') for x in row] for row in rows];t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3edf3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#8798a7')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#cbd6dd')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story.append(t);story.append(Spacer(1,10))
 title('IGOGU: anticipating the turn onto the FIR boundary')
 para('The new geometry is feasible. At Mach 0.82 and FL350, the turn begins 15.3 NM before IGOGU at 18:36:05 and rolls out at 7.260°N, 94.417°E at 18:38:35. Ground track is due south throughout the 18:40 call. These are fitted examples under a new conditional starting geometry, not a new probability density.')
 chart('early_FIR_turns',355)
 rows=[['Second-turn choice','UTC','Course at 19:41','BFO residual']]
 for i,label in [(13,'Time free, Mach 0.82'),(31,'At 6°N, Mach 0.82'),(32,'At 6°N, late Mach optimized')]:
  r=grid.loc[i];rows.append([label,pd.Timestamp(r.second_turn_utc).round('s').strftime('%H:%M:%S'),f'{r.arc_course_deg:.2f}° true',('0.00 Hz' if abs(r.BFO_1941_residual_hz)<.005 else f'{r.BFO_1941_residual_hz:+.2f} Hz')])
 table(rows,[190,80,125,W-395])
 para('All three examples fit the nominal 19:41 BTO and pass the ±8.6 Hz BFO gate. The last uses the Mach 0.74 lower bound at the arc. With second-turn timing free, the zero-residual example turns near 0.395°N: it follows the meridian beyond the FIR corner at 6°N. The FIR boundary itself turns east there.',True)
 para('The sensitivity grid contains 27 combinations of nominal IGOGU ETA, altitude and initial Mach. Eighteen finish the first turn before the call and pass the early checks; the nine 18:40-ETA cases do not finish in time. Eight separate 6°N cases also pass. Ground track is specified; ERA5 wind determines air-heading crab.',True)
 story.append(PageBreak());title('A complete continuation exists, but its speed history matters')
 para('Continuing the zero-residual 19:41 direction without another turn fails the 20:41 BTO. One locally optimized continuation with a third turn passes all original satellite checks through 00:11, fuel and modelled aircraft checks, and the separate R600 sensitivity. It is an existence example with no assigned Bayesian weight.')
 chart('full_FIR_feasible_example',368)
 table([['Quantity','Result'],['Third turn',later['third_turn_utc'][11:19]+' UTC; '+f"{later['third_angle_deg']:.2f}°"],['Fuel exhaustion / position','00:17:30 UTC; '+f"{abs(later['endpoint_lat']):.3f}°S, {later['endpoint_lon']:.3f}°E"],['Largest absolute residuals',f"BTO {max(abs(np.array(later['BTO_residuals_us']))):.2f} µs / 58 allowed; BFO {later['max_abs_BFO_hz']:.3f} Hz / 8.6 allowed"],['R600 kinematic continuation',f"Residual {later['R600_kinematic_residual_us']:+.2f} µs / 126 allowed"]],[145,W-145])
 para('The Mach sequence reaches both bounds and contains changes 5-8 times the original 0.015 prior standard deviation between successive Mach control points. It therefore should not be interpreted as a representative cruise path. Three attempts to find a smoother example with one more turn did not pass all BFO gates; that finite optimization failure is not an exclusion proof. No new posterior or evidence ratio was computed.',True)
 story.append(PageBreak());title('Which published waypoints do the original trajectories approach?')
 para('BULVA and ISBIX stand out. The table below uses the original IGOGU model, with the separately requested R600 weighting, and exact weighted sums over every saved positive-weight trajectory. IGOGU is omitted because passage through it was imposed. Inbound N571 points were conditioned on and are outside these sampled paths.')
 chart('waypoint_proximity',313)
 rows=[['Waypoint','Within 5 NM','Within 10 NM','Within 20 NM','Median distance']]
 for n in ['BULVA','ISBIX','BEDAX','ANOKO','NOPEK','MUTMI']:
  r=wp.loc[n];rows.append([n,*[f'{100*r[f"R600_within_{d}NM"]:.2f}%' for d in [5,10,20]],f'{r.R600_distance_median_nm:.2f} NM'])
 table(rows,[91,102,108,108,W-409])
 para('Distance bands are sensitivity radii, not an estimated navigation-error distribution. The broad screen examined 1,276 points with 131,072 weighted draws for each evidence scope; the ten-point shortlist was then evaluated against all 1,710,701 survivors. Independent ellipsoidal checks differed by at most 0.0007 NM in 372 comparisons.',True)
 para('These are geometric associations, not independent evidence of waypoint intent. BULVA, ISBIX and other positions come from official published lists, but the recovered India, Indonesia and Australia editions are later than March 2014. The original 2010 Malaysian coordinates remain pinned. The BULVA name is independently documented by ICAO in 2010; exact March 2014 coordinate validity and a catalog-density chance-coincidence test remain unfinished.',True)
 story.append(PageBreak());title('What was achieved, improved and preserved')
 for heading,body in [
  ('Recovered and made reproducible','The original model, independent importance runs, all 1,710,701 raw survivors, weather, satellite inputs, earlier airway/radar analyses, code, figures and machine-readable results are already preserved in four verified Drive archives. This update adds a separate FIR-intercept model, example fits, full rejection records, waypoint sources and proximity calculations.'),
  ('Resolved the seventh-arc question','The previous 4.6% draw fails the R600 test. About 95.2% of original weight survives; the separately reweighted exhaustion median is about 34.07°S, 93.75°E. Its ESS rises to about 1000, but the largest weight is still 1.71%; the density remains provisional. No 00:19 BFO was used.'),
  ('Separated route geometry from probability','The original retained paths had a median initial southbound course of 184.36° true and did not follow the FIR meridian. An anticipated turn can join the meridian before the 18:40 call. Exact 19:41 fits are not unique evidence of a route; later observations and speed priors materially restrict continuations.'),
  ('Found reproducible waypoint associations','BULVA and ISBIX receive high proximity fractions under both original and R600-weighted measures. The new FIR hypothesis passes ANOKO and NOPEK by construction. None of these findings has been multiplied into the posterior.'),
  ('Remaining work','Compute a properly normalized new posterior for the FIR-intercept hypothesis, with declared turn-start/timing priors and independent convergence checks. Replace the public-data fuel/performance approximation with validated constraints; marginalize calibration uncertainty; verify a March 2014 waypoint catalog; assess chance associations; and model post-exhaustion flight before claiming an impact PDF.')]:
  story.append(P(heading,'SubX'));para(body)
 story.append(P('Recover and continue','SubX'))
 para('Read <b>IGOGU_FIR_20260919_START_HERE.md</b> in the IGOGU conditional Drive folder. Download the listed archive parts and manifests, then run the supplied standard-library restore script. The master index identifies all prior and new archive bytes, hashes, extraction paths, build commands and continuation tasks. The final checkpoint is scheduled for 23:00 UK / 22:00 UTC on 19 September 2026.')
 para('<link href="https://drive.google.com/drive/folders/1E2wMSGz-MF_zFZ2GDvRZ1fO9aqQTT23F" color="#007f85">Open IGOGU conditional in Google Drive</link>',True)
 story.append(P('Primary geographic sources','SubX'))
 for label,url in [('Malaysia historical RNAV routes','https://aip.caam.gov.my/aip%20pdf/AIP%20AMDT%202_2010/ENR/Enr3_3.pdf'),('AAI India significant points','https://aim-india.aai.aero/eaip-v2/eAIP/EC-ENR-4.4-en-GB.pdf'),('AirNav Indonesia active waypoints','https://app-pia.airnavindonesia.co.id/navcard/active_wpt.php'),('Airservices Australia IFR waypoints, 03 SEP 2026','https://www.airservicesaustralia.com/aip/current/ersa/IFR__03SEP2026.pdf'),('ICAO RASMAG/13 IP/09, August 2010, pages 31 and 38: BULVA','https://www.icao.int/sites/default/files/sp-files/APAC/Documents/Meetings/2010/rasmag13/IP09.pdf')]:para(f'<link href="{url}" color="#007f85">{label}</link>',True)
 def foot(c,d):
  c.setFont('DejaVu',7);c.setFillColor(colors.HexColor(MUTED));c.drawString(38,23,'Conditional research | No new calibrated posterior | 19 September 2026');c.drawRightString(A4[0]-38,23,str(d.page))
 doc=SimpleDocTemplate(str(OUT/'mh370_IGOGU_FIR_and_waypoints.pdf'),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=34,bottomMargin=38,title='MH370 IGOGU FIR turn and waypoint follow-up',author='Research continuation package')
 doc.build(story,onFirstPage=foot,onLaterPages=foot)

if __name__=='__main__':
 early_figure();full_figure();waypoint_figure();build_pdf();print(str(OUT/'mh370_IGOGU_FIR_and_waypoints.pdf'))
