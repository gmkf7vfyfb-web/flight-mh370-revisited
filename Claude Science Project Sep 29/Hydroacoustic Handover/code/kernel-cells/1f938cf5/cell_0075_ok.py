
TAB.to_csv('out/settling_displacement_by_case_class_family.csv',index=False)
TT.to_csv('out/settling_term_off_at_haixun.csv',index=False)
INVT.to_csv('out/settling_inverse_region_haixun.csv',index=False)
SENS.to_csv('out/settling_kadri_locus_bto_altitude_sensitivity.csv',index=False)
mabs.to_csv('out/settling_prior_mass_rest_near_haixun_absolute.csv')
COND.to_csv('out/settling_prior_mass_rest_near_haixun_given_L.csv',index=False)
pd.DataFrame(summ).to_csv('out/settling_impact_conditions_in_L.csv',index=False)
# Kadri forward min distances (central geometry)
kf=[]
for br in ('T','C'):
    for cls in CLASSES:
        o=RES[f'kadri_{br}'][cls]
        d=gw.inv(o['lon'],o['lat'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        d0=gw.inv(o['lon0'],o['lat0'],np.full(N,HX[1]),np.full(N,HX[0]))[2]/1e3
        dep=o['depth']
        kf.append(dict(branch=br,cls=cls,n=N,impact_min_dist_HX_km=d0.min(),rest_min_dist_HX_km=d.min(),n_rest_le2km=int((d<=2).sum()),
                       rest_depth_p05=np.nanpercentile(dep,5),rest_depth_p50=np.nanpercentile(dep,50),rest_depth_p95=np.nanpercentile(dep,95)))
KF=pd.DataFrame(kf); KF.to_csv('out/settling_kadri_branches_forward.csv',index=False); print(KF.round(2).to_string())
print(site_df[['site','depth_m','source','gebco_tid','disc2km_min','disc2km_p50','disc2km_max']].to_string())
