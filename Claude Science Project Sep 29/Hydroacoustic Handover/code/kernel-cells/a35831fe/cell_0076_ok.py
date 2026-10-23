print('Emed0/Eq99 at -35.7:', fE(-35.7,Emed0)/1e9, fE(-35.7,Eq99)/1e9, 6.1*fE(-35.7,Eq99)/fE(-35.7,Emed0))
g=Pc[Pc.rank_lnLR==104].iloc[0]; print('row G', g.eta_level_locus, g.eta_min, g.eta_min_xF35A, g.eta_pd50_all_a005/ANCH_OLD)
print(len(Fd), R[R.id.str.startswith('MP-')&R.group.str.contains('two-site')].verdict.value_counts().to_dict())