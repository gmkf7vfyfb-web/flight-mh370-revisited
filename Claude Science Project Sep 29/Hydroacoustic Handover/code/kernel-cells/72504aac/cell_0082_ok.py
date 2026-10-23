
D='out'
# loci table
rows=[]
for k,v in LOCI.items():
    rows.append(dict(label=k,description=v['txt'],lat=round(float(v['lat']),3),lon=round(float(v['lon']),3),
        density_per_deg_D0=round(float(dens(v['lat'])),4),mass_within_0p5deg=round(float(massband(v['lat'])),4),
        hpd_level_core=round(float(hpd_at(CS,v['lat'],v['lon'])),3),hpd_level_drift=round(float(hpd_at(DS_,v['lat'],v['lon'])),3)))
for i,r in TOP.iterrows():
    rows.append(dict(label=f'R{i+1}',description=f"ranked pair {int(r.rank_lnLR)} by lnLR ({r.lnLR:.2f}): {r.rx_a} {r.t_a} {r.det_a} p {r.p_a:.3f} x {r.rx_b} {r.t_b} {r.det_b} p {r.p_b:.3f}; impact {r.implied_impact_utc}",
        lat=round(r.locus_lat,3),lon=round(r.locus_lon,3),density_per_deg_D0=round(float(dens(r.locus_lat)),4),mass_within_0p5deg=round(float(massband(r.locus_lat)),4),
        hpd_level_core=round(float(hpd_at(CS,r.locus_lat,r.locus_lon)),3),hpd_level_drift=round(float(hpd_at(DS_,r.locus_lat,r.locus_lon)),3)))
LT=pd.DataFrame(rows); LT.to_csv(f'{D}/pair-g-loci.csv',index=False); print(LT[['label','lat','lon','density_per_deg_D0','mass_within_0p5deg','hpd_level_core','hpd_level_drift']].to_string())
tj=[]
for key,c,ls,lab in SEL:
    T=TJ[key]; r=T['row']
    tj.append(dict(selection=lab,seed=T['k'],route_sample=T['j'],route_to_parent_km=round(T['dd'],2),parent_row=int(r.parent),impact_utc=hms(T0+r.t_impact_s),
                   final_descent_utc=hms(T0+r.t_takeover_s),impact_lat=round(r.lat,3),impact_lon=round(r.lon,3),km_from_G=round(r.d,1),family=FAMLAB[int(r.family4_code)],
                   max_descent_fpm=round(r.max_descent_rate_fpm),weight_share=float(r.share)))
pd.DataFrame(tj).to_csv(f'{D}/pair-g-trajectories.csv',index=False)
bt=[]
for nm in ('near','rest'):
    for i,ii in enumerate(ix): bt.append(dict(group=nm,minutes_after_2241=round(float(tmid[ii]),2),**{f'{v}_q{q}':round(float(band[nm][v][i,j]),2) for v in ('trk','gs') for j,q in enumerate((10,50,90))}))
pd.DataFrame(bt).to_csv(f'{D}/pair-g-track-speed-bands.csv',index=False)
# chart sources for provenance
with open(f'{D}/charts_pair_g.py','w') as fh:
    fh.write('"""Chart functions for the pair-G updates (22 Oct 2026). Run after exec(open(\'common.py\').read()) and the data cells; see README.txt."""\n')
    for s in [inspect.getsource(hpd_grid),inspect.getsource(hpd_levels),inspect.getsource(draw_hpd),inspect.getsource(traj),inspect.getsource(draw_traj),inspect.getsource(circle),src1 if False else inspect.getsource(chart1) if False else src, src2,src3,src4,src5,src6,src7]:
        fh.write(s+'\n\n')
import shutil; shutil.copy('work/common.py',f'{D}/common.py'); shutil.copy('work/extract_seed.py',f'{D}/extract_seed.py')
print(sorted(os.listdir(D)))
