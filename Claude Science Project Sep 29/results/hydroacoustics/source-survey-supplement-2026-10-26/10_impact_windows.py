"""Impact-window search at island/coastal seismometers (EXPLORATORY; returns no likelihood to the composer).
Arc: the project's 7th arc (registry/data_db/arc_line_of_sight.py): spherical small circle, centre 0.570 N 64.252 E,
radius 44.501 deg, eastern branch, sampled every 0.5 deg latitude from 20.0 S to 40.0 S (41 points).
Impact times: main 00:15-01:05 UTC, tail 01:05-02:00 UTC, 8 Mar 2014.
Per station and arc point with an open path (clear or large attenuation): predicted T = impact + water/1.48 + seismic/6.
Station window = [start + min tt - 150 s, end + max tt + 150 s] over open-path arc points.
Candidates: detections in the window that are not assigned to a known source (catalogue earthquakes P/S/T,
Royer 2016 events, the seismic relocation of Royer event 16); detections overlapping in the two bands are merged
(max SNR kept). For each candidate the arc latitudes whose own window contains the onset are listed.
Background: windows of the same length tiled end to end over 6-10 Mar 2014, excluding any window that overlaps
7 Mar 23:00 - 8 Mar 04:00 UTC. Statistic per window = max SNR of unassigned merged detections.
p = (1 + number of background windows with statistic >= candidate SNR) / (n_background + 1); p floor = 1/(n+1).
Rank = rank of the candidate SNR among the candidates in that station window (1 = highest).
Background windows had only catalogue sources removed (no Royer-type located set exists for them), so they hold
more unexplained transients than the 8 Mar window; p-values are therefore conservative (biased high).
Co-located partner check: AU.XMI/AU.XMIS (5.2 km apart) and G.RER/PF.RER (same site): max SNR at the partner from
onset-30 s to end+30 s; below 2 means the candidate is a local or instrumental transient.
No likelihood ratio is computed: there is no signal amplitude model for island stations (column states this)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
from obspy import UTCDateTime as U
D=pd.read_pickle('data/det_resolved.pkl'); st=pd.read_csv('data/stations.csv').set_index('station')
toS=lambda s: pd.to_datetime(s,format='ISO8601').values.astype('datetime64[ms]').astype(np.int64)/1000.
D['on_s']=toS(D.onset_utc); D['off_s']=toS(D.end_utc)
arc=geom.arc_points(-20.0,-40.0,0.5)
seis=[s for s in st.index if st.loc[s,'kind']=='seismometer' and s in set(D.station)]
W=150.; T0=U('2014-03-06').timestamp; T1=U('2014-03-11').timestamp; EX0=U('2014-03-07T23:00').timestamp; EX1=U('2014-03-08T04:00').timestamp
CASES={'main 00:15-01:05':(U('2014-03-08T00:15').timestamp,U('2014-03-08T01:05').timestamp),'tail 01:05-02:00':(U('2014-03-08T01:05').timestamp,U('2014-03-08T02:00').timestamp)}
# merged detections per station: union of overlapping detections across bands
def merged(g):
    g=g.sort_values('on_s'); out=[]
    for _,r in g.iterrows():
        if out and r.on_s<=out[-1]['off_s']:
            m=out[-1]; m['off_s']=max(m['off_s'],r.off_s); m['assigned']=m['assigned'] or r.assigned
            if r.peak_snr>m['peak_snr']: m.update(peak_snr=r.peak_snr,band=r.band,peak_utc=r.peak_utc,peak_freq_hz=r.peak_freq_hz,hf_lf_rel=r.hf_lf_rel)
            m['duration_s']=m['off_s']-m['on_s']
        else: out.append(dict(on_s=r.on_s,off_s=r.off_s,onset_utc=r.onset_utc,peak_utc=r.peak_utc,peak_snr=r.peak_snr,band=r.band,duration_s=r.duration_s,
                             peak_freq_hz=r.peak_freq_hz,hf_lf_rel=r.hf_lf_rel,assigned=r.assigned))
    return pd.DataFrame(out)
M={s:merged(D[D.station==s]) for s in seis}
geo=[]
for s in seis:
    for la,lo in arc:
        p=geom.path(la,lo,st.loc[s,'lat'],st.loc[s,'lon'],step_km=2.0)
        geo.append(dict(station=s,arc_lat=la,arc_lon=lo,dist_km=p['D'],baz_deg=p['baz'],path_class=p['cls'],tt_s=geom.t_travel(p)))
G=pd.DataFrame(geo); G.to_csv('out/island-impact-arc-paths.csv',index=False,float_format='%.5g')
wins=[]; cands=[]
for s in seis:
    g=G[(G.station==s)&G.path_class.isin(['clear','large attenuation'])]
    if not len(g): wins.append(dict(station=s,case='all',n_open_arc_points=0,note='no open path from the arc')); continue
    m=M[s]
    for case,(a,b) in CASES.items():
        w0=a+g.tt_s.min()-W; w1=b+g.tt_s.max()+W; L=w1-w0
        # background
        starts=np.arange(T0,T1-L,L); bg=[]
        un=m[m.assigned=='']
        for t in starts:
            if t<EX1 and t+L>EX0: continue
            x=un[(un.on_s>=t)&(un.on_s<t+L)]; bg.append(x.peak_snr.max() if len(x) else 0.0)
        bg=np.array(bg); n=len(bg)
        inw=m[(m.on_s>=w0)&(m.on_s<=w1)]; c=inw[inw.assigned=='']
        stat=c.peak_snr.max() if len(c) else 0.0
        pwin=(1+(bg>=stat).sum())/(n+1) if len(c) else np.nan
        wins.append(dict(station=s,case=case,n_open_arc_points=len(g),open_arc_lat_min=g.arc_lat.min(),open_arc_lat_max=g.arc_lat.max(),
            window_start_utc=str(U(w0))[:19],window_end_utc=str(U(w1))[:19],window_s=L,n_detections_in_window=len(inw),n_assigned=int((inw.assigned!='').sum()),
            n_unexplained=len(c),max_unexplained_snr=stat,p_window_max=pwin,n_background_windows=n,p_floor=1/(n+1),
            background_median_max_snr=float(np.median(bg)) if n else np.nan,background_p90_max_snr=float(np.percentile(bg,90)) if n else np.nan))
        c=c.sort_values('peak_snr',ascending=False).reset_index(drop=True)
        for i,r in c.iterrows():
            lat_ok=[f'{abs(x.arc_lat):.1f}' for _,x in g.iterrows() if a+x.tt_s-W<=r.on_s<=b+x.tt_s+W]
            p=(1+(bg>=r.peak_snr).sum())/(n+1)
            cands.append(dict(station=s,case=case,rank_in_window=i+1,onset_utc=r.onset_utc,peak_utc=r.peak_utc,duration_s=r.duration_s,peak_snr=r.peak_snr,band=r.band,
                peak_freq_hz=r.peak_freq_hz,hf_lf_rel=r.hf_lf_rel,p_value=p,p_floor=1/(n+1),n_background_windows=n,
                level='report (p<=0.05)' if p<=0.05 else ('mark (p<=0.1)' if p<=0.1 else ('screen (p<=0.3)' if p<=0.3 else 'below screen')),
                likelihood_ratio='not computed: no signal amplitude model for island stations',
                consistent_arc_lat_S=';'.join(lat_ok),n_consistent_arc_points=len(lat_ok),
                implied_impact_utc_range='' if not lat_ok else f"{str(U(r.on_s-g.tt_s.max()))[11:19]}-{str(U(r.on_s-g.tt_s.min()))[11:19]}"))
Wt=pd.DataFrame(wins); Ct=pd.DataFrame(cands)
# co-located partner check: a T phase converted at the island must also reach the partner seismometer
PART={'AU.XMI':'AU.XMIS','AU.XMIS':'AU.XMI','G.RER':'PF.RER','PF.RER':'G.RER'}
def partner(r):
    q=PART.get(r.station)
    if q is None: return pd.Series(dict(partner_station='',partner_max_snr_pm30s=np.nan,partner_check='no co-located partner'))
    z=np.load(f'data/det/{q}_snr.npz'); t0=U(str(z['t0'])); i=int(round(U(r.onset_utc)-t0))
    v=max(float(z[k][max(i-30,0):i+int(r.duration_s)+30].max()) for k in z.files if k.startswith('b'))
    return pd.Series(dict(partner_station=q,partner_max_snr_pm30s=v,partner_check='seen at partner' if v>=2 else 'NOT seen at partner: local or instrumental transient'))
if len(Ct): Ct=pd.concat([Ct,Ct.apply(partner,axis=1)],axis=1)
Wt.to_csv('out/island-impact-windows.csv',index=False,float_format='%.5g'); Ct.to_csv('out/island-impact-window-unexplained.csv',index=False,float_format='%.5g')
pd.set_option('display.width',250)
print(Wt[['station','case','n_open_arc_points','window_start_utc','window_end_utc','n_detections_in_window','n_assigned','n_unexplained','max_unexplained_snr','p_window_max','n_background_windows','p_floor']].to_string())
print('candidates',len(Ct)); print(Ct.level.value_counts().to_dict())
print(Ct[Ct.p_value<=0.3][['station','case','rank_in_window','onset_utc','duration_s','peak_snr','peak_freq_hz','p_value','p_floor','level','n_consistent_arc_points','partner_station','partner_max_snr_pm30s','partner_check']].to_string())
