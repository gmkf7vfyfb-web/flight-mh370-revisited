
RXN={"H01W":"Cape Leeuwin H01W","H08S":"Diego Garcia S. H08S","3376":"Perth Canyon 3376","3315":"Perth Canyon 3315","3274":"Portland 3274","3275":"Portland 3275","3250":"Scott Reef 3250"}
DETN={"M1b":"matched filter","D1":"STA/LTA","BE":"band energy","Z_res":"residual envelope","M1b_res":"residual matched filter"}
pp=pd.read_csv(f"{OUTX}/ranked_pairs.csv",dtype={"rx_a":str,"rx_b":str}); ss=pd.read_csv(f"{OUTX}/ranked_singles.csv",dtype={"rx":str}); tt=pd.read_csv(f"{OUTX}/ranked_triples.csv")
ms=[]
for r in pp.itertuples():
    ms.append(dict(n_sites=2,receivers=f"{r.rx_a} x {r.rx_b}",times=f"{r.t_a};{r.t_b}",detectors=f"{r.det_a};{r.det_b}",bands=f"{r.band_a};{r.band_b}",
        p_values=f"{r.p_a:.3g};{r.p_b:.3g}",p_B=f"{'' if pd.isna(r.pB_a) else f'{r.pB_a:.3g}'};{'' if pd.isna(r.pB_b) else f'{r.pB_b:.3g}'}",max_p=r.max_p,
        lags=f"{r.lag_s:.0f} s in [{r.lag_lo_s:.0f}, {r.lag_hi_s:.0f}]",lnLR=r.lnLR,ln_ftime=r.ln_ftime,ln_f_amp_given_time=r.ln_f_amp_given_time,lnB=r.lnB,
        lnLR_D2=r.lnLR_D2,lnLR_D3=r.lnLR_D3,lnLR_D4=r.lnLR_D4,locus_lat=r.locus_lat,locus_lon=r.locus_lon,implied_impact_utc=r.implied_impact_utc,
        locus_D0_mass_within_1deg=r.locus_D0_mass_within_1deg,kernel_source=r.kernel_source,eta_pd50_all_a005=r.eta_pd50_all_a005,eta_x_F35A=r.eta_x_F35A,
        eta_level_locus=r.eta_level_locus,eta_level_x_F35A=r.eta_level_x_F35A,F35A_anchor=ANOTE,bearing_consistency=r.bearing_consistency,label_searches=r.label_searches,caveats=r.caveats))
for r in tt.itertuples():
    ms.append(dict(n_sites=3,receivers=r.rxs.replace("x"," x "),times=r.times,detectors=r.dets,bands=r.bands,p_values=r.ps,p_B=r.pBs if isinstance(r.pBs,str) else "",max_p=r.max_p,lags=r.lags,
        lnLR=r.lnLR,ln_ftime=r.ln_ftime,ln_f_amp_given_time=r.ln_f_amp_given_time,lnB=r.lnB,lnLR_D2=r.lnLR_D2,lnLR_D3=r.lnLR_D3,lnLR_D4=r.lnLR_D4,
        locus_lat=r.locus_lat,locus_lon=r.locus_lon,implied_impact_utc=r.implied_impact_utc,locus_D0_mass_within_1deg=r.locus_D0_mass_within_1deg,kernel_source=r.kernel_source,
        eta_pd50_all_a005=r.eta_pd50_all_a005,eta_x_F35A=r.eta_x_F35A,eta_level_locus=r.eta_level_locus,eta_level_x_F35A=r.eta_level_x_F35A,F35A_anchor=ANOTE,
        bearing_consistency=r.bearing_consistency,label_searches=r.label_searches,caveats=r.caveats))
MS=pd.DataFrame(ms).sort_values(["lnLR","max_p"],ascending=[False,True]).reset_index(drop=True)
MS.insert(0,"rank_lnLR",MS.lnLR.rank(ascending=False,method="min").astype(int)); MS.insert(2,"rank_p",MS.max_p.rank(method="min").astype(int))
MS["status"]="EXPLORATORY; PREDICTIVE, NOT CALIBRATED"
MS.to_csv(f"{OUTX}/ranked_multisite.csv.tmp",index=False); os.replace(f"{OUTX}/ranked_multisite.csv.tmp",f"{OUTX}/ranked_multisite.csv")
print(len(MS)); print(MS.head(15)[["rank_lnLR","n_sites","receivers","times","detectors","p_values","lnLR","eta_x_F35A","locus_lat","implied_impact_utc"]].to_string())
print(ss.head(8)[["rank_lnLR","rx","time_utc","det","band","p","p_B","lnLR","eta_needed","eta_x_F35A","implied_source","implied_impact_utc"]].to_string())
print(ss[(ss.rx=="H01W")][["rank_lnLR","time_utc","p","lnLR","lnLR_no_bearing","eta_needed","bearing_consistency"]].to_string())
