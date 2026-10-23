Z=np.load('smoke-rowcond.npz')
pre='run-j-waypoints|seed-1'
def L_of(vec,den,m,opt='none'):
    Ln=node_L(m,'h50',opt); return np.log(np.nansum(vec*np.nan_to_num(Ln))/den)+LREF
for v in ['none','T_core','T_wide','C_core','C_wide']:
    k=f'{pre}|D0|{v}'
    s=float(Z[k+'|s']); tot=float(Z[k+'|sum']); ess=tot**2/float(Z[k+'|sum2'])
    vals={m:round(L_of(Z[k+'|vec_'+m],float(Z[k+'|den_'+m]),m),3) for m in ('glorys12','globcurrent','mean')}
    print(v, 'lnS', round(s+np.log(tot),2), 'ESS', round(ess,1), 'valid share mean', round(float(Z[k+'|den_mean'])/tot,4), vals,
          {kk:(Z[k+'|'+kk].tolist() if kk in ('parents99','rows99','lat_mean','lon_mean') else None) for kk in ('parents99','rows99','lat_mean','lon_mean') if k+'|'+kk in Z})
print(Z[f'{pre}|D0|T_core|fam'])
