
print([n for n in dir() if n.startswith("apply_figure") or n.startswith("panel_")])
top5p=pp.head(5).copy(); top5s=ss.head(5).copy()
foc=pp[(pp.rx_a=="H01W")&(pp.t_a=="00:52:04")&(pp.rx_b=="H08S")&(pp.t_b=="01:12:49")&(pp.det_b=="M1b")].iloc[0]
msr=MS[(MS.n_sites==2)&(MS.receivers=="H01W x H08S")&(MS.times=="00:52:04;01:12:49")&(MS.detectors=="M1b;M1b")].iloc[0]
print(foc.rank_lnLR, msr.rank_lnLR, foc.rank_p, foc.eta_pd50_all_a005, foc.locus_lat)
# E median at loci for pairs (needed for radiated energy)
def Emed_at(L_):
    m=np.abs(lat-L_)<=1.0; w=wD0[m]; return float(np.interp(0.5,np.cumsum(w[np.argsort(E[m])])/w.sum(),np.sort(E[m])))
for d in (top5p,):
    d["E_ref"]=[Emed_at(L_) for L_ in d.locus_lat]
foc_E=Emed_at(foc.locus_lat); print(foc_E, top5p[["rank_lnLR","rx_a","t_a","rx_b","t_b","eta_pd50_all_a005","E_ref"]].to_string())
EF35=9e8; RF35=EF35*ANCH; print("F35 radiated",RF35, "focal radiated multiple", foc.eta_pd50_all_a005*foc_E/RF35)
