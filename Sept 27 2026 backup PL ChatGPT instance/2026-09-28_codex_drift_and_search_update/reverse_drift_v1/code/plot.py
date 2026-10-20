"""Plot saved probability arrays only; transport is computed separately."""
from pathlib import Path
import json,os
B=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(B/'mpl_cache'))
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape,A4
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO

O=B/'results';F=B/'figures';F.mkdir(exist_ok=True)
g=pd.read_csv(O/'source_grid.csv');z=np.load(O/'conditional_pdfs.npz');summ=pd.read_csv(O/'summary.csv');comp=pd.read_csv(O/'sensitivity_comparisons.csv');conv=pd.read_csv(O/'seed_convergence.csv')
mods=['bran2016','oscar_v2_final','glorys12_waverys','equal_models'];labels=['BRAN2016','OSCAR v2 Final','GLORYS12 + WAVERYS','Equal model mixture']
shape=(129,71);X=g.longitude.to_numpy().reshape(shape);Y=g.latitude.to_numpy().reshape(shape);area=g.cellAreaKm2.to_numpy()
french=pd.DataFrame(json.loads((B/'french_coordinates.json').read_text()));pl=pd.read_csv(B/'recovered/data/pleiades-rating5-objects.csv')
arc=np.array(json.loads((B/'recovered/data/seventh_arc_fl400.geojson').read_text())['features'][0]['geometry']['coordinates'])
plt.rcParams.update({'font.size':9,'axes.titlesize':11,'axes.labelsize':9,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def p(m,n):return z[m+'__'+n]
def row(m,n):return summ[(summ.model==m)&(summ.scenario==n)].iloc[0]
def setup(ax):
    ax.plot(arc[:,0],arc[:,1],color='#5c6571',ls='--',lw=.8,zorder=5)
    ax.set(xlim=(87.5,96.0),ylim=(-38.0,-32.0),xlabel='Longitude',ylabel='Latitude')
    ax.set_aspect(1/np.cos(np.radians(35)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:.0f}°E'))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{abs(x):.0f}°S'))
    ax.grid(alpha=.15)
def panel(ax,m,n,vmax,showpoints=True):
    mass=p(m,n);d=mass/area;v=np.ma.masked_where(d< vmax*.004,d).reshape(shape)
    im=ax.pcolormesh(X,Y,v,cmap='YlGnBu',vmin=0,vmax=vmax,shading='nearest',rasterized=True)
    r=row(m,n);levels=[r.hpd95_threshold,r.hpd90_threshold,r.hpd50_threshold]
    ax.contour(X,Y,d.reshape(shape),levels=levels,colors=['#6389a8','#1d5279','#0c263f'],linewidths=[.6,1,1.3])
    ax.scatter(r.mode_lon,r.mode_lat,marker='*',s=45,c='#e67e22',edgecolors='white',linewidth=.5,zorder=8)
    setup(ax)
    if showpoints:
        if n=='pleiades' or n.startswith('combined'):ax.scatter(pl.longitude_deg,pl.latitude_deg,s=10,c='#b22266',marker='x',zorder=7)
        if n!='pleiades':
            obs=french.iloc[:3] if 'eastern3' in n else french
            ax.scatter(obs.longitude,obs.latitude,s=14,facecolors='none',edgecolors='#a54415',zorder=7)
    ax.text(.025,.025,f'90% area: {r.hpd90_km2:,.0f} km²',transform=ax.transAxes,fontsize=8,bbox=dict(fc='white',ec='none',alpha=.9))
    return im
def finish(fig,title,subtitle):
    fig.suptitle(title,fontsize=14,x=.055,ha='left',y=.98,color='#16344b')
    fig.text(.055,.925,subtitle,fontsize=10)
    fig.text(.055,.025,'Conditional on a selected detection being relevant debris and the stated transport/support model. No background false-detection likelihood.',fontsize=9,color='#555')
def save(pdf,fig,name):
    pdf.savefig(fig);fig.savefig(F/(name+'.png'),dpi=150);plt.close(fig)

with PdfPages(F/'maps.pdf') as pdf:
    fig,axes=plt.subplots(1,2,figsize=(13.8,8));fig.subplots_adjust(left=.06,right=.96,top=.85,bottom=.12,wspace=.22)
    ax=axes[0];setup(ax);ax.scatter(pl.longitude_deg,pl.latitude_deg,c='#b22266',s=30,marker='x',label='12 Pléiades rating-5 locations')
    ax.scatter(french.longitude,french.latitude,facecolors='none',edgecolors='#b35416',s=50,label='Possible COSMO-SkyMed Radar (four locations)')
    for _,r in french.iterrows():ax.annotate(r.id,(r.longitude,r.latitude),xytext=(6,7),textcoords='offset points')
    ax.legend(loc='lower right',fontsize=8);ax.set_title('Observation coordinates, not impact origins')
    panel(axes[1],'equal_models','pleiades',max(p('equal_models','pleiades')/area));axes[1].set_title('Reproduced Pléiades, expanded source support')
    finish(fig,'Detection geometry and the Pléiades reference','Dashed line: FL400 seventh-arc reference only. Star: grid-cell mode. Contours: 50%, 90%, 95% source probability.')
    save(pdf,fig,'01_observations_and_reference')
    for day in [21,23]:
        for combined in [False,True]:
            names=[f'{"combined50_" if combined else ""}{k}_{day}' for k in ['eastern3','french4']]
            vmax=max(np.max(p(m,n)/area) for m in mods for n in names)
            fig,axes=plt.subplots(2,4,figsize=(16,9));fig.subplots_adjust(left=.055,right=.885,top=.87,bottom=.12,hspace=.30,wspace=.24)
            for i,n in enumerate(names):
                for j,m in enumerate(mods):
                    im=panel(axes[i,j],m,n,vmax);axes[i,j].set_title(labels[j]+('\nEastern three' if i==0 else '\nAll four'))
            cb=fig.colorbar(im,cax=fig.add_axes([.908,.20,.014,.60]));cb.set_label('Source probability density / km²');cb.formatter.set_powerlimits((0,0));cb.update_ticks()
            title=f'{"Pléiades + Possible COSMO-SkyMed Radar: 50:50 mixture" if combined else "Possible COSMO-SkyMed Radar"} | {day} March assumption'
            finish(fig,title,'Possible COSMO-SkyMed Radar clock time assumed 04:00 UTC; Pléiades fixed at 23 March 04:00 UTC. Model weights fixed at 1/3.')
            save(pdf,fig,f'{"combined" if combined else "french"}_{day}')
    fig,axes=plt.subplots(2,2,figsize=(13.8,10));fig.subplots_adjust(left=.08,right=.96,top=.88,bottom=.12,hspace=.32,wspace=.23)
    for j,group in enumerate(['eastern3','french4']):
        ax=axes[0,j];setup(ax)
        for day,col in [(21,'#b45416'),(23,'#155d92')]:
            n=f'{group}_{day}';r=row('equal_models',n);ax.contour(X,Y,(p('equal_models',n)/area).reshape(shape),levels=[r.hpd90_threshold],colors=[col],linewidths=1.6)
        r=row('equal_models','pleiades');ax.contour(X,Y,(p('equal_models','pleiades')/area).reshape(shape),levels=[r.hpd90_threshold],colors=['#a12b6b'],linestyles='--')
        ax.set_title(('Eastern three' if j==0 else 'All four')+' | 90% contours')
        ax.legend(handles=[Line2D([],[],color=c,label=l,ls=ls) for c,l,ls in [('#b45416','Possible COSMO-SkyMed Radar: 21 March','-'),('#155d92','Possible COSMO-SkyMed Radar: 23 March','-'),('#a12b6b','Pléiades','--')]],fontsize=8)
        ax=axes[1,j];edges=np.arange(31.5,40.1,.08)
        for n,col,label in [('pleiades','#a12b6b','Pléiades'),(group+'_21','#b45416','Possible COSMO-SkyMed Radar: 21 March'),(group+'_23','#155d92','Possible COSMO-SkyMed Radar: 23 March'),('combined50_'+group+'_21','#446344','50:50 combined, 21 March')]:
            h,_=np.histogram(-g.latitude,bins=edges,weights=p('equal_models',n));ax.plot((edges[1:]+edges[:-1])/2,h/.08,label=label,c=col)
        ax.set(xlim=(32,38),xlabel='Southern latitude (degrees S)',ylabel='Probability density / degree');ax.grid(alpha=.2);ax.legend(fontsize=8)
    finish(fig,'Date and fourth-object sensitivities','Equal fixed mixture of the three transport families. Latitude histograms use 0.08° bins; no extra smoothing.')
    save(pdf,fig,'sensitivity_overview')
    fig,axes=plt.subplots(1,2,figsize=(13.8,8));fig.subplots_adjust(left=.08,right=.96,top=.85,bottom=.18,wspace=.3)
    colors_=['#a54d15','#2476a0','#347253']
    for j,group in enumerate(['eastern3','french4']):
        ax=axes[j]
        for i,m in enumerate(mods):
            r=comp[(comp.model==m)&(comp.kind=='date')&(comp['first']==group+'_21')].iloc[0]
            ax.bar(i,r.mean_shift_km,color=colors_[i] if i<3 else '#494949');ax.text(i,r.mean_shift_km+1,f'{r.mean_shift_km:.1f}',ha='center')
        ax.set_xticks(range(4),['BRAN2016','OSCAR','GLORYS12\n+ WAVERYS','Equal\nmixture']);ax.set(ylabel='Shift in probability-weighted mean (km)',title=('Eastern three' if j==0 else 'All four')+': 21 to 23 March');ax.set_ylim(0,max(comp[comp.kind=='date'].mean_shift_km)*1.2);ax.grid(axis='y',alpha=.2)
    finish(fig,'How much does the assumed date move the result?','Mean shifts summarize changes in location; total variation and HPD areas in the CSV tables also describe changes in shape.')
    save(pdf,fig,'date_mean_shifts')

styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=14
from reportlab.lib.styles import ParagraphStyle
styles.add(ParagraphStyle('SmallLabel',fontName='Helvetica',fontSize=8,leading=10))
story=[]
def para(t):story.append(Paragraph(t,styles['BodyText']));story.append(Spacer(1,8))
story.append(Paragraph('MH370: conditional imagery-origin analysis',styles['Title']));story.append(Spacer(1,12))
para('Recovered provenance and reproducible extension | 28 September 2026')
para('<b>Interpretation.</b> These normalized origin densities are conditional transport-compatibility results. They do not estimate the probability that an image object was MH370 debris. No sensor search-footprint denominator, background false-detection process, calibrated identity prior, flight likelihood or seabed non-detection likelihood is included.')
para('<b>Date verification.</b> Victor Iannello used 21 March 2014 for the three COSMO-SkyMed coordinates and 23 March for Pléiades. His July 2021 study selected matching BRAN2015 virtual drifters; it is separate from this recovered three-model analysis. The supplied briefing slide labels four coordinates as French satellite images sighted on 23 March. Sensor attribution, the fourth point\'s relationship to COSMO, and acquisition UTC remain unverified.')
para('<b>Recovery.</b> The August 2026 forward-inversion bundle was recovered from MH370-review-research-03.zip. It contains five checksum-matching forcing arrays, source and observation tables, executable code, three seeds, probability grids, sensitivity results and plots. Three referenced source PDFs were absent from that archive. The complete recovery inventory and checksum audit accompany this atlas.')
para('<b>Numerical method.</b> Start 8 March 2014 at 00:19 UTC; forward midpoint advection at three-hour steps. Each cell has 64 particles per windage value (0%, 1.2%, 3%), each weighted one third, for three fixed seeds. Random walk: two-dimensional daily RMS 5 NM. Endpoint kernel: isotropic Gaussian, sigma 10 km. GLORYS12 includes explicit WAVERYS surface Stokes drift. Possible COSMO-SkyMed Radar times use an assumed 04:00 UTC on either 21 or 23 March.')
para('<b>Source support.</b> A uniform-area prior on a 5 NM grid follows the FL400 reference arc between 32 and 39 degrees S. The original cross-arc range was -100 to +100 NM. Here it is expanded to -250 to +100 NM (west negative), because the old western edge clips the fourth-point and some Pléiades source density. Outside the computed support is unassessed, not impossible.')
para('<b>Mixtures.</b> Within a sensor, the score averages candidate kernels: a latent one-of-N association, not simultaneous proof that every object shares an origin. The primary combined result pools normalized Pléiades and Possible COSMO-SkyMed Radar densities 50:50 within each family, then pools families with fixed 1/3 weights. An equal-object likelihood-pooling sensitivity is also provided. These weights are choices, not fitted posterior model probabilities.')
story.append(PageBreak());story.append(Paragraph('Numerical overview: equal model mixture',styles['Title']));story.append(Spacer(1,12))
rows=[['Scenario','Mode (S, E)','Mean (S, E)','90% area km²']]
for n,label in [('pleiades','Pléiades'),('eastern3_21','Possible COSMO-SkyMed Radar<br/>3 targets: 21 March'),('eastern3_23','Possible COSMO-SkyMed Radar<br/>3 targets: 23 March'),('french4_21','Possible COSMO-SkyMed Radar<br/>4 targets: 21 March'),('french4_23','Possible COSMO-SkyMed Radar<br/>4 targets: 23 March'),('combined50_eastern3_21','Combined 3: 21 March'),('combined50_eastern3_23','Combined 3: 23 March'),('combined50_french4_21','Combined 4: 21 March'),('combined50_french4_23','Combined 4: 23 March')]:
    r=row('equal_models',n);rows.append([Paragraph(label,styles['SmallLabel']),f'{-r.mode_lat:.3f}, {r.mode_lon:.3f}',f'{-r.mean_lat:.3f}, {r.mean_lon:.3f}',f'{r.hpd90_km2:,.0f}'])
t=Table(rows,colWidths=[155,120,120,110]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#16344b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f4f7'),colors.white])]));story.append(t);story.append(Spacer(1,16))
v=json.loads((O/'validation.json').read_text())
para(f'<b>Validation.</b> The nine repeated Pléiades model/seed runs reproduce saved likelihoods with maximum absolute error {v["max_reproduction_absolute_error"]:.2g}. All {v["source_cells"]:,} source cells have 192 valid trajectories per seed and model/date run. Every delivered PDF grid integrates to one. The largest probability in the outer two grid bands is {100*v["max_boundary_mass"]:.4f}%.')
para('<b>Precision.</b> Modes are grid-cell maxima and may jump between nearby cells or separate lobes. Coordinates are displayed for reproducibility, not metre-level certainty. Read mean locations, highest-density areas, model differences and seed convergence together. The daily-wind time-knot convention and end-of-array clamping are inherited for faithful reproduction; the recovered independent audit found this convention can change shapes and OSCAR modes. This extension is not a new forcing calibration.')
para('<b>References.</b> Iannello (23 July 2021), <i>Italian Satellite May Have Detected MH370 Floating Debris</i>, mh370.radiantphysics.com/2021/07/23/italian-satellite-may-have-detected-mh370-floating-debris/; Minchin et al. (2017), GA Record 2017/13, DOI 10.11636/Record.2017.013; Griffin &amp; Oke (2017), <i>The search for MH370 and ocean surface drift - Part III</i>, DOI 10.4225/08/599344b9beead. Full input URLs and hashes are preserved in the recovered manifests.')
story.append(PageBreak());story.append(Paragraph('Sensor nationality and the reported handoff',styles['Title']));story.append(Spacer(1,12))
para('<b>Display label.</b> The four briefing coordinates are now labelled <b>Possible COSMO-SkyMed Radar</b>, including their eastern-three subset. This is a conditional attribution, not authentication of a satellite product. Historical wording is retained when discussing the slide. Numerical results and mixture weights are unchanged; existing F1-F4 and french4 file/data identifiers remain stable for reproducibility.')
para('<b>Italian system; French access.</b> COSMO-SkyMed is Italian. CNES identifies it as the radar component of the Franco-Italian ORFEO programme, alongside the optical Pléiades component. A French Senate report on the bilateral agreement describes French access to imagery from the four Italian radar satellites. This makes French delivery of Italian imagery plausible; it does not establish the specific upstream handling of these contacts. [1, 2]')
para('<b>Reported March 2014 chain.</b> The Malaysian minister\'s 24 March statement said radar imagery acquired on 21 March reached Malaysia on the evening of 22 March and was relayed to RCC Australia on the morning of 23 March. It separately described camera imagery acquired on 23 March, received on 24 March and also relayed to Australia. The statement called the satellites French but did not name COSMO-SkyMed. Thus the documented account supports France as the supplying country, Malaysia as recipient and relay, and RCC Australia as search coordinator. It does not authenticate the four-coordinate slide as the 21 March radar product. [3]')
para('<b>Why the slide may say French.</b> A supplier-based label is a plausible explanation, given the sharing arrangement. Conflation with the separate Pléiades acquisition or use of a reporting date also remain possible. No verified original product or complete Italian-to-French-to-Malaysian chain for these four coordinates has been recovered. The 21/23 March sensitivity therefore remains appropriate.')
para('<b>Are radar returns images?</b> Yes. Synthetic-aperture radar produces images from processed radar returns, rather than optical photographs. Radar imagery is a valid term; a coordinate list of interpreted targets is a derived detection product. The public briefing graphic alone does not tell us whether Australia received full imagery, selected extracts, coordinates, or some combination.')
para('<b>Sources.</b><br/>[1] CNES, <link href="https://cnes.fr/en/projects/pleiades" color="blue">Pléiades: project description</link>.<br/>[2] French Senate, <link href="https://www.senat.fr/rap/l02-443/l02-4430.html" color="blue">Report 443 (2002-2003), Franco-Italian Earth-observation agreement</link>.<br/>[3] Hishammuddin Hussein, <link href="https://malaysia.news.yahoo.com/mh370-press-briefing-by-hishammuddin-hussein--24-march-2014--530pm-101214741.html" color="blue">24 March 2014, 5:30 pm briefing, transcript reproduced by Yahoo Newsroom</link>.')
SimpleDocTemplate(str(F/'front.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=38).build(story)
writer=PdfWriter()
for fn in ['front.pdf','maps.pdf']:
    for page in PdfReader(F/fn).pages:writer.add_page(page)
for i,page in enumerate(writer.pages):
    stream=BytesIO();w,h=float(page.mediabox.width),float(page.mediabox.height)
    stamp=canvas.Canvas(stream,pagesize=(w,h));stamp.setFont('Helvetica',8);stamp.setFillColor(colors.HexColor('#66717a'));stamp.drawRightString(w-20,12,f'{i+1} / {len(writer.pages)}');stamp.save();stream.seek(0)
    page.merge_page(PdfReader(stream).pages[0])
with (B/'conditional_origin_atlas.pdf').open('wb') as f:writer.write(f)
print('Atlas pages',len(writer.pages))
