"""Associate island/coastal detections with predicted arrivals (T, P, S) of catalogued events and Royer 2016 events.
Step 1 (first pass): T window = predicted T +/- 180 s (onset in window, or the detection spans the prediction).
         P and S: onset must lie in the window, or the detection spans the prediction with its peak within
         the window (+30 s); P/S are predicted only for catalogued earthquakes and the
         seismic relocation of Royer event 16 (ROY16S), not for acoustically located Royer events.
         P window = predicted P -10/+20 s; S window = predicted S -20/+40 s. Use the highest-SNR detection.
Step 2 (calibration): per station, T residual (onset - predicted) for first-pass matches with chance probability
         < 0.02, distance > 1000 km and path not blocked. Station offset = median residual (if >= 3 matches, else
         the all-station median); spread = 1.4826*MAD (floor 30 s).
Step 3 (final): T window = predicted +/- 150 s (a priori; steps 1-2 kept as a diagnostic only).
Chance probability of each match: p_chance = 1 - exp(-rate(SNR >= matched SNR) * window length), with the rate
taken from the station's own 6-10 March detection list in the same band (a Poisson coincidence probability,
not a detection p-value).
Royer events and CMST detections are not used for the calibration."""
import sys, glob, numpy as np, pandas as pd
P=pd.read_csv('data/pred_arrivals.csv'); E=pd.read_csv('data/events_all.csv')
D=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('data/det/*.csv'))],ignore_index=True)
toS=lambda s: pd.to_datetime(s,format='ISO8601').values.astype('datetime64[ms]').astype(np.int64)/1000.
D['on']=toS(D.onset_utc); D['off']=toS(D.end_utc); D['pk']=toS(D.peak_utc)
D['det_id']=D.station+'|'+D.band+'|'+D.onset_utc
SPAN=5*86400.
stas=sorted(D.station.unique())
P=P[P.station.isin(stas)].merge(E[['event_id','origin_utc','mag','magtype','source','source_class','depth_km','place']],on='event_id')
for c in ['pred_T_utc','pred_P_utc','pred_S_utc']: P[c.split('_')[1]]=np.where(P[c].notna()&(P[c]!=''),toS(P[c].fillna('2000-01-01')),np.nan)
byst={(s,b):g.sort_values('on') for (s,b),g in D.groupby(['station','band'])}
snrsorted={k:np.sort(g.peak_snr.values) for k,g in byst.items()}
def rate_ge(k,snr): a=snrsorted[k]; return (len(a)-np.searchsorted(a,snr))/SPAN
def match(st,t,lo,hi,span=True):
    best=None
    for b in ['2-8','3-12']:
        g=byst.get((st,b))
        if g is None: continue
        m=g[((g.on>=t+lo)&(g.on<=t+hi))|(span&(g.on<=t)&(g.off>=t)&(g.on>=t+lo-600))|((not span)&(g.on<=t)&(g.off>=t)&(g.pk>=t+lo)&(g.pk<=t+hi+30))]
        if len(m):
            r=m.loc[m.peak_snr.idxmax()]
            pc=1-np.exp(-rate_ge((st,b),r.peak_snr)*(hi-lo))
            if best is None or pc<best[1]: best=(r,pc,b)
    return best
def assoc(P,off,spr,first):
    out=[]
    for _,r in P.iterrows():
        row=r.to_dict()
        for ph,(lo,hi) in [('T',(0,0)),('P',(-10,20)),('S',(-20,40))]:
            t=r[ph]
            if not np.isfinite(t): continue
            if ph in ('P','S') and not (r.source_class=='earthquake' and r.source!='Royer 2016 Table 4'): continue   # no P/S for acoustically located Royer events
            if ph=='T':
                o=off.get(r.station,0.) if not first else 0.
                w=180. if first else max(60.,2.5*spr.get(r.station,60.))
                t=t+o; lo,hi=-w,w
            m=match(r.station,t,lo,hi,span=(ph=='T'))
            if m is not None:
                d,pc,b=m
                row.update({f'{ph}_det_id':d.det_id,f'{ph}_band':b,f'{ph}_onset_utc':d.onset_utc,f'{ph}_resid_s':d.on-r[ph],f'{ph}_snr':d.peak_snr,
                            f'{ph}_dur_s':d.duration_s,f'{ph}_fpk_hz':d.peak_freq_hz,f'{ph}_hflf':d.hf_lf_rel,f'{ph}_p_chance':pc,f'{ph}_win_s':hi-lo})
            else: row[f'{ph}_win_s']=hi-lo
        out.append(row)
    return pd.DataFrame(out)
A1=assoc(P,{},{},True)
cal=A1[(~A1.source.isin(['Royer 2016 Table 4','seismic relocation of Royer event 16']))&(A1.T_p_chance<0.02)&(A1.dist_km>1000)&(A1.path_class!='blocked')&A1.T_resid_s.notna()]
allmed=cal.T_resid_s.median() if len(cal) else 0.
off={};spr={};calrows=[]
for s in stas:
    c=cal[cal.station==s].T_resid_s
    if len(c)>=3: off[s]=c.median(); spr[s]=max(30.,1.4826*np.median(np.abs(c-c.median())))
    else: off[s]=allmed; spr[s]=max(30.,1.4826*np.median(np.abs(cal.T_resid_s-allmed))) if len(cal)>=3 else 60.
    calrows.append(dict(station=s,n_cal=len(c),offset_s=off[s],spread_s=spr[s],offset_source='station' if len(c)>=3 else 'all-station median'))
C=pd.DataFrame(calrows); C.to_csv('data/station_T_calibration.csv',index=False); print(C.to_string())
print('all-station median',allmed,'n',len(cal))
# Final windows use an a priori rule (the empirical calibration above is contaminated by chance matches and is
# kept only as a diagnostic): offset 0 s, half-width 150 s (about 3.3 x the 46 s SD of the 1.48 km/s rule
# against IDC T arrivals at H01W1/H08S1, 6-10 Mar 2014). spread is set so that max(60, 2.5*spread) = 150.
off={s:0.0 for s in stas}; spr={s:60.0 for s in stas}
A=assoc(P,off,spr,False)
A['T_offset_s']=A.station.map(off); A['T_spread_s']=A.station.map(spr)
A.to_csv('data/assoc_all.csv',index=False)
print('pairs',len(A),'T matches p<0.05',(A.T_p_chance<0.05).sum(),'P',(A.P_p_chance<0.05).sum(),'S',(A.S_p_chance<0.05).sum())

# Control: shift every predicted arrival by +/-1500 s and +/-3000 s and repeat the final association (chance-match rate)
ctl=[]
for sh in [-3000,-1500,1500,3000]:
    Q=P.copy()
    for ph in ['T','P','S']: Q[ph]=Q[ph]+sh
    q=assoc(Q,off,spr,False); q['shift_s']=sh; ctl.append(q)
Ctl=pd.concat(ctl,ignore_index=True); Ctl.to_csv('data/assoc_control_shifted.csv',index=False)
print('control T matches p<0.05 per shift',(Ctl.T_p_chance<0.05).sum()/4)
