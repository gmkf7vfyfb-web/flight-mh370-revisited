"""Figures for island-seismic-check-note.md. Run inside the python kernel after the figure-style skill's
apply_figure_style() (exec(open('scripts/11_figures.py').read())). Reads out/*.csv and data/*."""
import sys, json, glob, os, numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0,'scripts'); import geom
from obspy import read, UTCDateTime as U
from scipy.signal import butter, sosfiltfilt
NAMES={'II.COCO':'Cocos Islands','II.DGAR':'Diego Garcia','AU.XMIS':'Christmas Island 1','AU.XMI':'Christmas Island 2','G.AIS':'Amsterdam Island',
 'G.PAF':'Kerguelen','G.CRZF':'Crozet Islands','G.ROCAM':'Rodrigues','G.RER':'Reunion 1','PF.RER':'Reunion 2','II.MSEY':'Seychelles',
 'GE.KAAM':'Maldives','II.PALK':'Sri Lanka','GE.MNAI':'SW Sumatra','GE.CISI':'W Java','GE.UGM':'Central Java','GE.JAGI':'E Java','GE.PLAI':'Sumbawa',
 'GE.SOEI':'Timor','GE.MMRI':'Flores','S1.AUALB':'Albany WA','AU.GIRL':'Giralia WA','IU.NWAO':'Narrogin WA','IU.MBWA':'Marble Bar WA'}
os.makedirs('figs',exist_ok=True)
st=pd.read_csv('data/stations.csv').set_index('station')
import textwrap
def foot(fig,ste,tech,y=0.008,width=175):
    """Two-version footnote stacked from the bottom: technical (grey) below, plain above."""
    t=textwrap.wrap('Technical: '+tech,width); p=textwrap.wrap('Plain: '+ste,width); lh=0.016*7.2/fig.get_size_inches()[1]*1.0
    for k,line in enumerate(reversed(t)): fig.text(0.01,y+k*lh,line,fontsize=6,ha='left',va='bottom',color='0.3')
    for k,line in enumerate(reversed(p)): fig.text(0.01,y+(len(t)+0.6+k)*lh,line,fontsize=6,ha='left',va='bottom')
    return y+(len(t)+len(p)+0.6)*lh
# ---------- Figure 1: map ----------
G=geom; step=12
i0=0; i1=int((12-G.gh['lat0'])/G.gh['step_deg']); j0=0; j1=int((138-G.gh['lon0'])/G.gh['step_deg'])
Z=np.asarray(G.EL[i0:i1:step,j0:j1:step]).astype(float); la=G.gh['lat0']+np.arange(i0,i1,step)*G.gh['step_deg']; lo=G.gh['lon0']+np.arange(j0,j1,step)*G.gh['step_deg']
fig,ax=plt.subplots(figsize=(7.2,7.4)); fig.subplots_adjust(bottom=0.27,top=0.95,left=0.08,right=0.98); ax.set_facecolor('#eef2f6')
ax.contourf(lo,la,Z,levels=[-9000,-3000,-1000,0,9000],colors=['#dfe9f3','#c9dbeb','#b3cde0','#d9d4c7'])
ax.contour(lo,la,Z,levels=[0],colors='0.45',linewidths=0.3)
arc=np.array(geom.arc_points(-20,-40,0.25)); ax.plot(arc[:,1],arc[:,0],color='#b2182b',lw=2,label='7th arc, 20-40 S')
R=pd.read_csv('out/royer-events-island-check-summary.csv')
cls={'icequake':('^','#2166ac'),'uncertain':('o','#7f3b08'),'earthquake':('*','#1b7837')}
for c,(m,col) in cls.items():
    x=R[R.source_class==c]; ax.scatter(x.lon,x.lat,marker=m,s=40 if m!='*' else 90,color=col,edgecolor='k',lw=0.4,zorder=5,label=f'Royer 2016 located event: {c}')
reloc=json.load(open('data/roy16_relocation.json'))['best']
ax.scatter([reloc['lon']],[reloc['lat']],marker='x',s=40,color='k',zorder=6,label='Royer event 16, seismic location (this note)')
seis=[s for s in NAMES if s in st.index]
ax.scatter(st.loc[seis,'lon'],st.loc[seis,'lat'],marker='v',s=30,color='#fdb863',edgecolor='k',lw=0.5,zorder=6,label='Island or coastal seismometer')
for s in seis:
    if s in ('AU.XMI','PF.RER','GE.UGM','GE.JAGI','GE.PLAI','GE.MMRI','IU.MBWA','AU.GIRL'): continue
    off={'AU.XMIS':(-4,-9),'GE.CISI':(3,5),'II.COCO':(-20,-10),'GE.SOEI':(3,-8),'G.CRZF':(3,3),'IU.NWAO':(4,2),'S1.AUALB':(4,-6)}.get(s,(3,3))
    ax.annotate(NAMES[s].replace(' 1',''),(st.loc[s,'lon'],st.loc[s,'lat']),xytext=off,textcoords='offset points',fontsize=6)
ax.annotate('Java to Timor stations',(116,-8.6),xytext=(113,-14.5),fontsize=6,arrowprops=dict(arrowstyle='-',lw=0.4))
ax.annotate('Giralia and Marble Bar WA',(119.8,-21.0),xytext=(122,-18.5),fontsize=6)
h=st[st.kind=='hydrophone']; ax.scatter(h.lon,h.lat,marker='s',s=22,color='w',edgecolor='k',lw=0.7,zorder=6,label='Hydrophone (IMS or IMOS logger)')
ax.set_xlim(40,138); ax.set_ylim(-68,12); ax.axhline(-60,color='0.6',lw=0.4,ls=':'); ax.text(41,-61.5,'no bathymetry grid south of 60 S',fontsize=6,color='0.4'); ax.set_xlabel('Longitude (deg E)'); ax.set_ylabel('Latitude (deg)')
ax.set_title('Public seismometers near the search area, with the 20 sound sources that Royer located on 8 March 2014',loc='left')
fig.legend(*ax.get_legend_handles_labels(),loc='lower center',ncol=3,fontsize=6,frameon=False,bbox_to_anchor=(0.5,0.135))
foot(fig,'The map shows 24 seismometers on islands and coasts. It shows the 20 sound sources that Royer (2016) located between 23:45 and 02:05 UTC. It shows the 7th arc from 20 S to 40 S. Royer event 16 has a second position from seismic waves.',
 'Bathymetry GEBCO_2026 15" (subsampled 0.05 deg; fills <-3000, -3000 to -1000, -1000 to 0 m, land). Arc: small circle, centre 0.570 N 64.252 E, radius 44.501 deg (project arc_line_of_sight.py). Royer 2016 Table 4 positions (all 20 shown). Hydrophones: H01W, H08S, H08N, IMOS 3315/3376, 3250, 3274/3275. Seismic relocation: iasp91, 4 P + 3 S picks, best depth 35 km.')
fig.savefig('figs/fig1-station-and-royer-map.png',dpi=200); plt.close(fig)
# ---------- Figure 2: detection level ----------
A=pd.read_csv('out/island-seismic-associations.csv')
a=A[(A.source!='Royer 2016 Table 4')&A.path_class.isin(['clear','large attenuation'])&(A.dist_km>600)&A.mag.notna()&A.pred_T_utc.notna()].copy()
Lv=pd.read_csv('out/island-seismic-detection-levels.csv'); Lp=Lv[(Lv.scope=='all stations')&(Lv.p_chance_threshold==0.05)]
seen=a[(a.T_p_chance<0.05)]; ns=a[~(a.T_p_chance<0.05)]
fig,ax=plt.subplots(figsize=(7.2,5.4)); fig.subplots_adjust(bottom=0.3,top=0.93,left=0.09,right=0.98)
ax.scatter(ns.dist_km,ns.mag,s=10,facecolor='none',edgecolor='0.6',lw=0.6,label=f'T phase not seen (n={len(ns)})')
ax.scatter(seen.dist_km,seen.mag,s=22,color='#b35806',edgecolor='k',lw=0.4,label=f'T phase seen, coincidence probability < 0.05 (n={len(seen)})')
for d0,d1 in [(600,1500),(1500,3000),(3000,9000)]: ax.axvline(d0,color='0.85',lw=0.6,zorder=0)
ax.axhline(4.5,color='0.85',lw=0.6,zorder=0)
for (d0,d1,lab) in [(600,1500,'600-1500 km'),(1500,3000,'1500-3000 km'),(3000,9000,'>3000 km')]:
    r=Lp[(Lp.mag_bin=='M>=4.5')&(Lp.dist_bin==lab)].iloc[0]
    ax.text(np.sqrt(d0*min(d1,9000)),6.9,f"M>=4.5: {int(r.n_seen)}/{int(r.n_pairs)} seen\nchance level {r.frac_control:.2f}",ha='center',va='top',fontsize=6)
ax.set_xscale('log'); ax.set_xticks([600,1000,2000,3000,5000,8000]); ax.set_xticklabels(['600','1k','2k','3k','5k','8k'])
ax.set_xlabel('Distance from earthquake to seismometer (km)'); ax.set_ylabel('Catalogue magnitude (mixed types)'); ax.set_ylim(2.8,7.0)
ax.set_title('Island seismometers see T phases mainly from magnitude 4.5 and larger within 1,500 km',loc='left'); fig.legend(*ax.get_legend_handles_labels(),loc='lower center',ncol=2,fontsize=6,frameon=False,bbox_to_anchor=(0.5,0.17))
foot(fig,'Each point is one earthquake and one seismometer with an open water path. A filled point means a T phase arrived at the expected time. The chance level comes from the same test at wrong times (shift of 25 and 50 min).',
 f'6-10 Mar 2014; 24 stations; catalogue earthquakes (known-events table + USGS M>=4.5), distance >600 km, GEBCO path clear or large attenuation. T predicted at 1.48 km/s water + 6 km/s seismic leg, window +/-150 s; STA/LTA detections (SNR>=2, 2-8 and 3-12 Hz). Coincidence probability = Poisson rate of detections at >= that SNR x window. Control: predictions shifted +/-1500, +/-3000 s. Magnitudes mb, MLv, ML, MS, Mw mixed.')
fig.savefig('figs/fig2-t-phase-detection-level.png',dpi=200); plt.close(fig)
# ---------- Figure 3: Royer event 16 ----------
rl=json.load(open('data/roy16_relocation.json')); PK=pd.DataFrame(rl['picks'])
chan={'.'.join(os.path.basename(f).split('.')[:2]):f for f in glob.glob('data/raw/*.20140308.mseed') if len(os.path.basename(f).split('.'))==6}
t_ref=U('2014-03-08T01:15:00'); order=['GE.CISI','GE.UGM','AU.XMIS','AU.XMI','GE.MNAI','GE.JAGI','GE.PLAI','II.COCO','GE.MMRI','AU.GIRL','GE.SOEI']
fig,(ax,ax2)=plt.subplots(1,2,figsize=(7.2,5.4),gridspec_kw=dict(width_ratios=[2.2,1])); fig.subplots_adjust(bottom=0.27,top=0.9,left=0.15,right=0.98,wspace=0.3)
t_or=t_ref+rl['best']['origin_s_after_0115']
for k,s in enumerate(order):
    tr=read(chan[s]).merge(fill_value=0)[0].slice(t_ref-30,t_ref+300).copy(); fs=tr.stats.sampling_rate
    y=sosfiltfilt(butter(4,[2,min(8,0.45*fs)],btype='band',fs=fs,output='sos'),tr.data.astype(float)-tr.data.mean())
    ax.plot(np.arange(len(y))/fs-30,k+0.42*y/np.percentile(np.abs(y),99.95),lw=0.35,color='k')
    D=geom.dist_az(rl['best']['lat'],rl['best']['lon'],st.loc[s,'lat'],st.loc[s,'lon'])[0]
    ax.text(-34,k,f"{NAMES[s]} {D:.0f} km",ha='right',va='center',fontsize=6)
    for _,p in PK[PK.station==s].iterrows():
        ax.plot([U(p.pick_utc)-t_ref]*2,[k-0.4,k+0.4],color='#b2182b' if p.phase=='P' else '#2166ac',lw=1.2)
ax.axvline(48.0,color='#7f3b08',ls='--',lw=0.8); ax.text(49,len(order)-0.4,'Royer origin',fontsize=6,color='#7f3b08')
ax.axvline(t_or-t_ref,color='k',ls=':',lw=0.8); ax.text(t_or-t_ref-1,len(order)-0.4,'seismic origin',fontsize=6,ha='right')
ax.set_yticks([]); ax.set_xlabel('Time after 01:15:00 UTC, 8 March 2014 (s)'); ax.set_xlim(-30,300); ax.set_ylim(-0.8,len(order)+0.2)
ax.set_title('Royer event 16 is a real earthquake south of West Java',loc='left')
ax.plot([],[],color='#b2182b',lw=1.2,label='P pick'); ax.plot([],[],color='#2166ac',lw=1.2,label='S pick'); ax.legend(loc='lower right',fontsize=6)
ax2.contour(lo,la,Z,levels=[0],colors='0.45',linewidths=0.5)
ax2.scatter([107.622],[-8.052],marker='*',s=90,color='#1b7837',edgecolor='k',lw=0.4,label='Royer 2016 (hydroacoustic)')
ax2.scatter([rl['best']['lon']],[rl['best']['lat']],marker='x',s=50,color='k',label='This note (seismic)')
rg=rl['region_dchi2_4']; ax2.add_patch(plt.Rectangle((rg['lon_min'],rg['lat_min']),rg['lon_max']-rg['lon_min'],rg['lat_max']-rg['lat_min'],fill=False,lw=0.6,ls='--'))
ax2.scatter(st.loc[['GE.CISI','GE.UGM'],'lon'],st.loc[['GE.CISI','GE.UGM'],'lat'],marker='v',s=25,color='#fdb863',edgecolor='k',lw=0.5,label='Seismometer')
ax2.set_xlim(106.8,110.8); ax2.set_ylim(-9.2,-6.8); ax2.set_xlabel('Longitude (deg E)'); ax2.set_ylabel('Latitude (deg)'); ax2.legend(loc='lower left',fontsize=6)
ax2.set_title('Positions 30 km apart',loc='left')
foot(fig,'Four seismometers record the P and S waves of Royer event 16. The seismic position is 30 km from the position from sound. The seismic origin time is 25 s earlier. A sound-based origin marks when sound starts in the water, so a later time is expected.',
 f"Band-pass 2-8 Hz, traces normalised. AIC picks (P weight 0.5 s, S 2 s), iasp91 grid search 0.02 deg, depths 5-70 km: best {abs(rl['best']['lat']):.2f} S {rl['best']['lon']:.2f} E, {rl['best']['depth_km']} km, origin 01:15:{rl['best']['origin_s_after_0115']:.1f}, chi2 {rl['best']['chi2']:.2f} (7 picks). Dashed box: delta chi2 <= 4 at 35 km depth. Royer: 8.052 S 107.622 E, 01:15:48.0.")
fig.savefig('figs/fig3-royer-event16-seismic.png',dpi=200); plt.close(fig)
# ---------- Figure 4: impact windows ----------
Wt=pd.read_csv('out/island-impact-windows.csv'); Ct=pd.read_csv('out/island-impact-window-unexplained.csv'); Dd=pd.read_csv('out/island-seismic-detections.csv')
sel=['II.COCO','AU.XMIS','AU.XMI','II.DGAR','G.AIS','G.ROCAM','G.RER','II.MSEY','G.PAF','IU.NWAO']
fig,axs=plt.subplots(len(sel),1,figsize=(7.2,9.6),sharex=True); fig.subplots_adjust(bottom=0.19,top=0.96,left=0.2,right=0.98,hspace=0.12)
t0p=U('2014-03-08T00:00'); 
for ax,s in zip(axs,sel):
    z=np.load(f'data/det/{s}_snr.npz'); t0=U(str(z['t0'])); i=int(t0p-t0); b='b3_12' if 'b3_12' in z.files else 'b2_8'; y=z[b][i:i+4*3600].astype(float)
    ax.plot(np.arange(len(y))/3600,y,lw=0.4,color='0.35')
    for case,col in [('main 00:15-01:05','#fee0b6'),('tail 01:05-02:00','#d8daeb')]:
        w=Wt[(Wt.station==s)&(Wt.case==case)]
        if len(w) and isinstance(w.window_start_utc.iloc[0],str): ax.axvspan((U(w.window_start_utc.iloc[0])-t0p)/3600,(U(w.window_end_utc.iloc[0])-t0p)/3600,color=col,zorder=0,lw=0)
    c=Ct[(Ct.station==s)]
    for _,r in c.drop_duplicates('onset_utc').iterrows():
        x=(U(r.onset_utc)-t0p)/3600; mk='o' if r.p_value>0.3 else ('s' if r.p_value>0.05 else 'D')
        bad=isinstance(r.get('partner_check',''),str) and r.partner_check.startswith('NOT')
        ax.scatter([x],[min(r.peak_snr,9.5)],marker=mk,s=14 if mk=='o' else 26,facecolor='none' if bad else ('#b35806' if mk!='o' else 'w'),edgecolor='k',lw=0.5,zorder=5)
    d=Dd[(Dd.station==s)&(Dd.assigned.notna())&(Dd.assigned!='')]; d=d[(pd.to_datetime(d.onset_utc,format='ISO8601')>=pd.Timestamp('2014-03-08'))&(pd.to_datetime(d.onset_utc,format='ISO8601')<pd.Timestamp('2014-03-08T04:00'))]
    for _,r in d.iterrows(): ax.scatter([(U(r.onset_utc)-t0p)/3600],[min(r.peak_snr,9.5)],marker='|',s=40,color='#1b7837',zorder=4)
    ax.set_ylim(0,10); ax.set_yticks([0,5]); ax.text(-0.05,0.5,NAMES[s],transform=ax.transAxes,ha='right',va='center',fontsize=7)
axs[-1].set_xlabel('Hours after 00:00 UTC, 8 March 2014'); axs[-1].set_xlim(0,4)
axs[0].set_title('No unexplained arrival in the impact windows passes the reporting level and the co-located check',loc='left')
fig.text(0.015,0.58,'STA/LTA amplitude SNR (each row 0-10)',rotation=90,va='center',fontsize=7)
from matplotlib.lines import Line2D
hs=[plt.Rectangle((0,0),1,1,color='#fee0b6'),plt.Rectangle((0,0),1,1,color='#d8daeb'),Line2D([],[],marker='|',ls='',color='#1b7837',ms=8),
    Line2D([],[],marker='o',ls='',mfc='w',mec='k',ms=4),Line2D([],[],marker='s',ls='',mfc='#b35806',mec='k',ms=4),Line2D([],[],marker='D',ls='',mfc='#b35806',mec='k',ms=4),Line2D([],[],marker='D',ls='',mfc='none',mec='k',ms=4)]
fig.legend(hs,['window, impact 00:15-01:05','window, impact 01:05-02:00','arrival from a known source','unexplained, p > 0.3','unexplained, 0.05 < p <= 0.3','unexplained, p <= 0.05','fails co-located check (open marker)'],
           loc='lower center',ncol=4,fontsize=6,bbox_to_anchor=(0.55,0.095),frameon=False)
foot(fig,'Each row is one seismometer. Shaded bands show when sound from an impact on the 7th arc can arrive. Marks show arrivals that no known source explains. This test is exploratory. The background uses the same stations on 6-10 March.',
 'SNR 1-s series, 3-12 Hz (2-8 Hz at 20 sps), clipped at 9.5. Windows: arc 20-40 S (0.5 deg), open GEBCO paths, 1.48 km/s + 6 km/s seismic leg, +/-150 s. p = (1+#background windows with max unexplained SNR >= candidate)/(n+1), n = 73-121 windows; p floor 1/(n+1) = 0.008-0.014. Screen 0.3, mark 0.1, report 0.05. No likelihood ratio (no signal model).',y=0.0)
fig.savefig('figs/fig4-impact-window-arrivals.png',dpi=200); plt.close(fig)
print('figures done')
