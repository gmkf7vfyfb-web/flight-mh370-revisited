def delta_pop_levels(path, k, c_, lams):
    df=pd.read_csv(path); p={s: np.mean([df[f'p_{cc}_{i}'] for cc in CLS],0) for i,s in enumerate(SEGS)}
    F=sum(p[s] for s in SEGS[:6]); Wp=sum(p[s] for s in POP)
    return df.node.values.astype(int), {lam: np.asarray(-k*np.log1p(lam*Wp/(c_*F))) for lam in lams}
LAMS={'pop_1x':0.1,'pop_3x':0.3,'pop_5x':0.5}
for m in ('glorys12','globcurrent'):
    pn,Dl=delta_pop_levels(R+f'australia-160E/aus160-{m}/nodes.csv',KC[m][0],KC[m][1],list(LAMS.values()))
    plat=G['lat0']+(pn//NL)*G['dlat']; plon=G['lon0']+(pn%NL)*G['dlon']
    for nm,lam in LAMS.items(): DEL[m][nm]=spread_to(plat,plon,Dl[lam],alat_n,alon_n)
# check: lam=1 equals the reconstructed populated
pn,Dl=delta_pop_levels(R+'australia-160E/aus160-glorys12/nodes.csv',KC['glorys12'][0],KC['glorys12'][1],[1.0])
print(np.nanmax(abs(spread_to(plat,plon,Dl[1.0],alat_n,alon_n)-DEL['glorys12']['populated-only (reconstructed)'])))
OPT2={'none':'none','populated (current, ~10x)':'populated-only (reconstructed)','populated 5x':'pop_5x','populated 3x':'pop_3x','populated 1x':'pop_1x','B':'B','C':'C'}
