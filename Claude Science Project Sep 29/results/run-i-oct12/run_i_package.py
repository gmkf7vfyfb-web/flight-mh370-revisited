"""Run I report package: summary pages, all run I charts, then the four standard family reports (no BTO-only panel)."""
import json, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt, pypdfium2 as pdfium
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
O="repo/Claude Science Project Sep 29/results/run-i-oct12"; REP="out/reports-i"; A4=(8.27,11.69)
INK="#222222"; MUTED="#555555"
def wrap(s,w=105): return "\n".join("\n".join(textwrap.wrap(p,w)) if p.strip() else "" for p in s.split("\n"))
def text_page(pdf,title,blocks):
    fig=plt.figure(figsize=A4); fig.text(0.07,0.955,title,fontsize=14,weight='bold',color=INK,va='top'); y=0.915
    for kind,body in blocks:
        if kind=='h': fig.text(0.07,y,body,fontsize=10.5,weight='bold',color=INK,va='top'); y-=0.028
        elif kind=='p':
            t=wrap(body); fig.text(0.07,y,t,fontsize=8.6,color=INK,va='top',linespacing=1.35); y-=0.0155*(t.count("\n")+1)+0.012
        elif kind=='t':
            df=body; cols=list(df.columns); n=len(df)+1; h=0.0235*n
            ax=fig.add_axes([0.07,y-h,0.86,h]); ax.axis('off')
            tb=ax.table(cellText=df.values.tolist(),colLabels=cols,loc='upper left',cellLoc='left',colLoc='left',bbox=[0,0,1,1])
            tb.auto_set_font_size(False); tb.set_fontsize(7.0)
            for (r,c),cell in tb.get_celld().items():
                cell.set_edgecolor('#cccccc'); cell.set_linewidth(0.4)
                if r==0: cell.set_text_props(weight='bold')
            y-=h+0.02
    fig.text(0.07,0.025,"Core run I report package, 12 Oct 2026. Footnotes on each chart: plain (ASD-STE100) and technical.",fontsize=7,color=MUTED)
    pdf.savefig(fig); plt.close(fig)
def image_page(pdf,png,title):
    im=Image.open(png); w,h=im.size; fig=plt.figure(figsize=A4)
    fig.text(0.07,0.965,title,fontsize=10.5,weight='bold',color=INK,va='top')
    aw=0.88; ah=aw*h/w*A4[0]/A4[1]
    if ah>0.86: ah=0.86; aw=ah*w/h*A4[1]/A4[0]
    ax=fig.add_axes([(1-aw)/2,0.94-ah,aw,ah]); ax.imshow(im); ax.axis('off'); pdf.savefig(fig,dpi=200); plt.close(fig)
fam=pd.read_csv(f"{O}/run-i-family-evidence.csv")
ft=pd.DataFrame({'Family':fam.family.str.replace(' (Davey)','',regex=False),'ln Z':fam.log_evidence.map('{:.2f}'.format),'seed sd':fam.seed_sd.map(lambda v:f'{v+1e-9:.2f}'),
  'ln BF':fam.ln_BF_vs_waypoints.map('{:+.2f}'.format),'Share':fam.posterior_share.map(lambda p:f"{100*p:.2f} %"),
  'Split-half':fam.split_half.map('{:.3f}'.format),'00:19 median':fam.median_0019_deg.map('{:.2f}°'.format)})
area=pd.read_csv(f"{O}/run-i-area-summary.csv")
at=pd.DataFrame({'Time':area.epoch,'Set':area.set.str.replace('all four families (posterior-weighted)','all four (weighted)',regex=False),'Median lat':area.median_lat.map('{:.2f}°'.format),'50 % area':area.area_50_km2.map(lambda v:f"{v/1000:.1f}k km²"),
  '90 % area':area.area_90_km2.map(lambda v:f"{v/1000:.0f}k km²"),'99 % area':area.area_99_km2.map(lambda v:f"{v/1000:.0f}k km²")})
ev=pd.read_csv(f"{O}/run-i-evidence-by-data-point.csv")
groups=[('Radar band VAMPI–MEKAR 18:15–18:21',['b1815','b1817','b1819','b1821']),('Radar points 18:04–18:22',['r0414','r0515','r0716','r1336','r1822']),
        ('18:25:34 BTO (log-on); 18:28 BTO+BFO',['m1825','m1828a','m1828b']),('18:39 BFO (phone call)',['m1839']),('19:41 BTO+BFO',['m1941']),('20:41 BTO+BFO',['m2041']),
        ('21:41–23:15',['m2141','m2241','m2315']),('00:11 BTO+BFO',['m0011']),('00:19 (two handshakes)',['m0019a','m0019b'])]
S=ev.set_index('epoch'); et=pd.DataFrame({'Data':[g for g,_ in groups],'Gain vs free flight (nats)':[f"{S.loc[e,'waypoints minus free flight'].sum():+.2f}" for _,e in groups]})
et.loc[len(et)]=['Total',f"{ev['waypoints minus free flight'].sum():+.2f}"]
plan=pd.read_csv(f"{O}/waypoint-plan-shares.csv").set_index('quantity')
pt=pd.DataFrame({'Waypoint plan':['SAMAK first','IGOGU first','NILAM first','ANOKO first','first leg fly-by','first-leg break-off at 40–80 %','last leg: change of mode part-way','two legs','three legs'],
  'Posterior share (seed sd)':[f"{plan.loc[q,'mean']:.3f} ({plan.loc[q,'sd']:.3f})" for q in ['first SAMAK','first IGOGU','first NILAM','first ANOKO','first leg fly-by','first leg break-off 40-80%','last leg part-way','legs=2','legs=3']]})
tr=pd.read_csv(f"{O}/traffic-separation-summary.csv")
tt=pd.DataFrame({'Family':tr.family.str.replace(' flight','',regex=False),'Turn area':tr.turn_area.str.replace(r' \(.*\)','',regex=True).str.replace('turn ','',regex=False),'Traffic':tr.traffic,'Draws':tr.draws.astype(int),
  'Median (NM)':tr.median_closest_nm.map('{:.1f}'.format),'5 % (NM)':tr.p05_closest_nm.map('{:.1f}'.format),'Close pass':tr.share_within_5nm_1000ft.map(lambda v:f"{100*v:.1f} %")})
with PdfPages(f"{O}/run-i-report-package.pdf") as pdf:
    text_page(pdf,"Core run I: free flight against the waypoint family",[
      ('p',"Run I tests a fair comparison of free flight and the reset waypoint family at equal family prior, together with the descent-climb family and the exact Davey reproduction. Every family has 8 seeds (7M particles per seed for free flight and waypoints, 3.5M for descent-climb and reproduction) and writes 100,000 hand-off rows per seed at 22:41 and 00:11 for end of flight. All inputs are staged at mh370-exchange/core/run-i/ (READY, 340 files, SHA-256 checked). 00:19 treatment: core, Davey both-BTO, no BFO."),
      ('h',"1. Family result (equal prior over four families)"),('t',ft),
      ('p',"Mixture over the four families: 00:19 median −37.17°, 90 % interval −37.57° to −34.77°. No family reaches the 8-seed split-half floor of 0.924; waypoints is closest (0.916). The family log-evidences are stable to ±0.35 nats across seeds, so the ranking is robust; the shape of each latitude curve is not settled."),
      ('h',"2. Why the waypoint family takes 99.8 %"),('t',et),
      ('p',"The sequential log-evidence increments sum exactly to each family's ln Z, so the difference splits by data item (each increment is conditional on the earlier data). About a third of the lead (+2.38) comes from the radar band between VAMPI and MEKAR: the waypoint family flies that published segment exactly, and the band is scored across that line with sd 1.5 NM. The rest comes mainly from the 18:39 BFO (+1.74) and the 19:41 arc (+1.29): a turn at about 18:38 followed by a steady great circle fits them. Approximate sensitivity (dropping an item's increment): without the radar band the waypoint share is 0.981; also without 18:39, 0.90; also without 19:41, 0.73."),
      ('p',"Turn timing is not forced. There is no time term in the prior. SAMAK, IGOGU and ANOKO lie 130–152 NM from MEKAR on the 94.42°E line, so at 450–510 kt the aircraft reaches them at 18:37–18:42; a fly-by starts about 2 minutes early. Earlier turns are in the prior (NILAM first at about 18:25; break-off at 20/40/60/80 % of the first leg at about 18:25, 18:29, 18:33, 18:37). The prior's turn times are discrete and most of its mass is at 18:37–18:42, so part of the 18:39 gain reflects where the fixes are. The paper should state this."),
    ])
    text_page(pdf,"Run I: settings, waypoint plans, areas, traffic",[
      ('h',"3. Settings (Pete's rulings, 11–12 Oct 2026)"),
      ('p',"Speeds: free flight, waypoints and descent-climb use Mach 0.45–0.87 within 210–330 KCAS until 18:40, then cruise Mach 0.70–0.87 within 210–330 KCAS; physics limits take precedence. The reproduction family stays exactly Davey (Mach 0.73–0.84 throughout, no cruise CAS clip)."),
      ('p',"Waypoint family: VAMPI then MEKAR to 18:21, then a random route through the 26 approved 2014-epoch fixes (tiers A+B; tier C as sensitivity only). Fly-by and fly-over both sampled. Break-off 50/50 at 20/40/60/80 % on any leg; mean 3 legs, maximum 8. Equator: stop or continue 50/50; fixes allowed to 4.5°S. On the last leg the change of flight mode is 50/50 at the fix or uniform along the leg west of 96°E (no prior on when). After the change: Davey great-circle LNAV."),
      ('p',"Common stack (all families): run D stack (run C sampler; fuel fixes s7 one-engine, s8 hold-then-taper, inop-flow fix; two tanks; Inmarsat ephemeris; radar in the likelihood; look-ahead hand-offs). Differences from Davey et al. (2016) are listed on the parameter page of each family report that follows."),
      ('h',"4. Waypoint plans (posterior, 8 seeds)"),('t',pt),
      ('h',"5. Area of the position at 00:11 and 00:19 (sensitivity to the family)"),('t',at),
    ])
    text_page(pdf,"Run I: traffic and other checks",[
      ('h',"6. Separation from other traffic, 18:25–18:39"),('t',tt),
      ('p',"Closest lateral approach of each posterior draw (2,000 per seed, 40 s trace). Close pass: within 5 NM laterally and 1,000 ft vertically. IGO053 positions are estimated (Langkawi SSR fit, back-propagated); UAE343 is ADS-C. Destination diagnostic (post-run only): no final great circle passes within 100 NM of NZFX; closeness to the South Pole is geometric. A particle refresh at 23:15 did not improve convergence (Δ ln Z −0.01, surviving lineages unchanged); more particles is the remedy for free flight."),
    ])
    for png,title in [("run-i-0019-latitude.png","Figure A. 00:19 latitude: four families together, and each on its own"),
                      ("run-i-0019-latitude-zoom.png","Figure B. 00:19 latitude, 39°S–34°S, with Davey Fig. 10.3"),
                      ("run-i-evidence-by-data-point.png","Figure C. Where the waypoint family gains its evidence"),
                      ("run-i-area-maps.png","Figure D. Area of the position at 00:11 and 00:19: all families, waypoints only, free flight only"),
                      ("run-i-turn-zoom.png","Figure E. Posterior paths 18:22–18:42 on the en-route chart"),
                      ("run-i-logon-1825-zoom.png","Figure F. Paths around the 18:25:34 log-on, MEKAR to NILAM")]:
        image_page(pdf,f"{O}/{png}",title)
out=pdfium.PdfDocument(f"{O}/run-i-report-package.pdf")
for f in ("waypoints","free","repro","descent-climb"):
    src=pdfium.PdfDocument(f"{REP}/run-i-{f}-report.pdf"); out.import_pages(src)
out.save(f"{O}/run-i-report-package.pdf.tmp"); import os; os.replace(f"{O}/run-i-report-package.pdf.tmp",f"{O}/run-i-report-package.pdf")
print(len(pdfium.PdfDocument(f"{O}/run-i-report-package.pdf")))
