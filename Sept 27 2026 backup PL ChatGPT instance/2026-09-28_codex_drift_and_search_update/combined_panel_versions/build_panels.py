from pathlib import Path
import json,os,zipfile,hashlib
B=Path(__file__).resolve().parent;R=B.parent/'reverse_drift_v1'
os.environ['MPLCONFIGDIR']=str(B/'mpl_cache')
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
G=pd.read_csv(R/'results/source_grid.csv');Z=np.load(R/'results/conditional_pdfs.npz')
S=pd.read_csv(R/'results/summary.csv');s=S[(S.model=='equal_models')&(S.scenario=='combined50_french4_21')].iloc[0]
p=Z['equal_models__combined50_french4_21'];assert abs(p.sum()-1)<1e-12
d=p/G.cellAreaKm2.to_numpy();shape=(129,71);X=G.longitude.to_numpy().reshape(shape);Y=G.latitude.to_numpy().reshape(shape)
pl=pd.read_csv(R/'recovered/data/pleiades-rating5-objects.csv');co=pd.DataFrame(json.loads((R/'french_coordinates.json').read_text()))
arc=np.array(json.loads((R/'recovered/data/seventh_arc_fl400.geojson').read_text())['features'][0]['geometry']['coordinates'])
features=json.loads((B/'search_footprints.geojson').read_text())['features']
plt.rcParams.update({'font.size':11,'axes.titlesize':13,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def setup(ax):
 ax.set(xlim=(87.5,96),ylim=(-38,-32),xlabel='Longitude',ylabel='Latitude');ax.set_aspect(1/np.cos(np.radians(35)))
 ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:.0f}°E'));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{abs(x):.0f}°S'));ax.grid(alpha=.14)
 ax.plot(arc[:,0],arc[:,1],color='#697583',ls='--',lw=.9,zorder=3)
def observations(ax,large=False):
 ax.scatter(pl.longitude_deg,pl.latitude_deg,c='#b22266',s=35 if large else 18,marker='x',zorder=10,label='12 Pléiades rating-5 locations')
 ax.scatter(co.longitude,co.latitude,facecolors='none',edgecolors='#b35416',s=55 if large else 25,lw=1.3,zorder=10,label='Possible COSMO-SkyMed Radar (all four)')
 if large:
  for _,v in co.iterrows():ax.annotate(v.id,(v.longitude,v.latitude),xytext=(7,9),textcoords='offset points')
styles={
 'atsb_phase2_2014_2017':('#555555','-',.75,'ATSB 2014-2017: published footprint'),
 'oi2018_total_outline_approx':('#7951a2',(0,(6,3)),1.2,'OI 2018: approximate search outline'),
 'oi2024_proposed_outboard_southeast':('#d44232','-',1.8,'OI 2025-2026: recent-search band*'),
 'oi2024_proposed_inboard_northwest':('#218444',(0,(3,2)),1.8,'OI possible remaining / next band*')}
for overlay in [False,True]:
 fig,axes=plt.subplots(1,2,figsize=(16,9.4));fig.subplots_adjust(left=.065,right=.97,top=.875,bottom=.22,wspace=.22)
 for ax in axes:setup(ax)
 observations(axes[0],True);axes[0].set_title('Observation coordinates, not impact origins',pad=16);axes[0].legend(loc='lower right',fontsize=9,framealpha=.96)
 ax=axes[1];ax.pcolormesh(X,Y,np.ma.masked_where(d<d.max()*.004,d).reshape(shape),cmap='YlGnBu',vmin=0,vmax=d.max(),shading='nearest',rasterized=True,zorder=1)
 ax.contour(X,Y,d.reshape(shape),levels=[s.hpd95_threshold,s.hpd90_threshold,s.hpd50_threshold],colors=['#6389a8','#1d5279','#0c263f'],linewidths=[.7,1.1,1.5],zorder=4)
 observations(ax);ax.scatter(s.mode_lon,s.mode_lat,marker='*',s=100,c='#f19036',edgecolors='white',lw=.8,zorder=12)
 ax.set_title('Pléiades + Possible COSMO-SkyMed Radar (all four)\nEqual model mixture | COSMO: 21 March assumption',pad=12)
 ax.text(.025,.025,f'90% area: {s.hpd90_km2:,.0f} km²',transform=ax.transAxes,fontsize=10,bbox=dict(fc='white',ec='none',alpha=.92),zorder=20)
 if overlay:
  for f in features:
   k=f['properties']['id']
   if k not in styles:continue
   col,ls,lw,label=styles[k];geom=f['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
   for poly in polys:
    for ring in poly:
     a=np.array(ring);ax.plot(a[:,0],a[:,1],color=col,ls=ls,lw=lw,zorder=6)
  handles=[Line2D([],[],color=c,ls=ls,lw=lw,label=l) for c,ls,lw,l in styles.values()]
  fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.555,.177),fontsize=9,frameon=False,ncol=1,labelspacing=.5)
  fig.text(.065,.095,'* Ocean Infinity bands are approximate proposal polygons.\nSoutheast: recent-search context, not verified full sonar coverage.\nNorthwest: inferred possible remaining area, not a confirmed next boundary.\nSources and status checks: see accompanying provenance note.',fontsize=9,linespacing=1.5,color='#444')
 else:
  fig.text(.065,.14,'50:50 mixture of normalized sensor PDFs; BRAN2016, OSCAR v2 Final and GLORYS12 + WAVERYS each weighted 1/3.\nPléiades: 23 March 04:00 UTC; possible COSMO: assumed 21 March 04:00 UTC. Star: grid-cell mode; contours: 50%, 90%, 95%.',fontsize=10,linespacing=1.6,color='#444')
 fig.text(.065,.043,'Conditional transport-compatibility PDF; no debris-identity probability or background false-detection denominator. Search overlays do not reweight the PDF.',fontsize=9,color='#555')
 fig.text(.065,.015,'Dashed grey curve: FL400 seventh-arc reference. Same probability surface and colour scale in both versions.',fontsize=9,color='#555')
 name='combined_all4_21march'+('_search_overlays' if overlay else '')
 for ext in ['png','pdf','svg']:fig.savefig(B/f'{name}.{ext}',dpi=220,facecolor='white')
 plt.close(fig)
print('Two panels exported: PNG, PDF and SVG. 90% area:',s.hpd90_km2)
# Preserve the original search provenance alongside the recovered geometries.
with zipfile.ZipFile('/Users/pete/Downloads/MH370_complete_project_2026-08-14.zip') as z:
 prefix='MH370_complete_download_2026-08-14/flight-mh370-revisited/outputs/mh370_search_evidence/'
 for name in ['source_register.csv','MH370_searched_area_evidence_audit.md']:(B/name).write_bytes(z.read(prefix+name))
(B/'PROVENANCE.md').write_text('''# Two combined imagery-origin panels

The left panel is the same observation map in both figures. The right panel uses saved `equal_models__combined50_french4_21` cell masses: a 50:50 pool of the normalized Pléiades and four Possible COSMO-SkyMed Radar PDFs within each transport family, then an equal mixture of BRAN2016, OSCAR v2 Final and GLORYS12 + WAVERYS. Pléiades uses 23 March; possible COSMO uses 21 March (assumed 04:00 UTC). No transport rerun or search non-detection update was performed. All four possible COSMO observations are retained.

Search overlays occur only on the right. Geometry was recovered unchanged from `MH370_complete_project_2026-08-14.zip`, member `MH370_complete_download_2026-08-14/flight-mh370-revisited/outputs/mh370_search_evidence/search_footprints.geojson`. Its original source register and evidence audit accompany this note. ATSB's footprint was reconstructed by the earlier project from its published coverage layer; OI 2018 is an approximate envelope, not a complete swath mask. Bluefin-21 is outside this map extent. Surface-search boxes and the broad planning envelope are intentionally not represented as seabed coverage.

The two recent OI bands are community reconstructions of the March 2024 presentation. The southeast band's association with the 2025-2026 search and the northwest band's possible remaining status are interpretations, not official audited coverage polygons. The latter is not a published confirmed next-search boundary. Reconstructed areas are about 9,768 and 6,072 km² respectively and should not be substituted for contract totals.

Checked 28 September 2026:
- [MH370-CAPTION geometry provenance](https://www.mh370-caption.net/index.php/2025-armada-78-06-paths/): explicitly says exact OI-band coordinates are unknown and were drawn from the tenth-anniversary presentation.
- [Ocean Infinity statement](https://oceaninfinity.com/news/conclusion-of-the-search-for-malaysian-airlines-flight-mh370/): latest deployment departed on 23 January 2026.
- [Minister's extension announcement reported 29 June 2026](https://www.malaymail.com/news/malaysia/2026/06/29/cabinet-greenlights-mh370-deep-sea-search-extension-with-ocean-infinity-for-another-year-search-to-resume-july-1-says-anthony-loke/225653): remaining 7,428.54 km²; anticipated deployment November 2026-April 2027. This confirms an intended continuation, not the exact northwest-band boundary.

The contours and colours describe the conditional origin model, not the probability that any observation was MH370 debris. Search geometry is purely contextual and has not reduced, masked, or renormalized the probability surface.
''')
