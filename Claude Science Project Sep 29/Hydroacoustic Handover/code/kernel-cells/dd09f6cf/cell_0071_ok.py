REF_A='0.005'
def comp_surface(d,a,pk,eps=0.0):
    r=surf[(d,a,pk)]; f=lambda x: eps+(1-eps)*x
    out={}
    for k in ['strip','X50','X200']:
        out[k]=np.log(f(r[k])/f(r[k+'_comp']))
    for ak in AK: out[ak]=np.log(f(r[ak])/f(r['strip_comp']))
    return out, r
def comp_seabed(d,v):
    r=res[d]; out={}
    for k in ['strip','X50','X200']: out[k]=np.log(r[k]['Ls'][v]/r[k]['Ls_comp'][v])
    for ak in AK: out[ak]=np.log(r[ak]['Ls'][v]/r['strip']['Ls_comp'][v])
    return out
# Haixun sensitivity
hx_i=int(np.floor((-25.975-GLAT0)/GST)); hx_j=int(np.floor((101.461-GLON0)/GST)); hcell=hx_i*GNX+hx_j
rows_tab=[]
for d in DK:
    for v in ['s05','s00','s25','s50','x05']:
        sb=comp_seabed(d,v)
        for k,val in sb.items(): rows_tab.append(dict(option=d,term='seabed',case=f'rho {v[1:]}' if v[0]=='s' else 'ATSB only (no OI), rho 0.05',locality=k,lnB=val))
        LH = (int(v[1:])/100 if v[0]=='s' else 0.05) + (1-(int(v[1:])/100 if v[0]=='s' else 0.05))*(1-(0.9*0.889 if v[0]=='s' else 0.0))
        rows_tab.append(dict(option=d,term='seabed',case=f'rho {v[1:]}' if v[0]=='s' else 'ATSB only (no OI), rho 0.05',locality='Haixun point (sensitivity)',lnB=np.log(LH/res[d]['Ls_all'][v])))
    for a in ALS:
        for pk in PODK:
            for eps in (0.0,0.05,0.2):
                su,r=comp_surface(d,a,pk,eps)
                case=f'windage {float(a)*100:.1f}%, POD {pk}, floor {eps}'
                for k,val in su.items(): rows_tab.append(dict(option=d,term='surface',case=case,locality=k,lnB=val))
                Lh=eps+(1-eps)*Lgrid[(a,pk)][hcell]
                rows_tab.append(dict(option=d,term='surface',case=case,locality='Haixun point (sensitivity)',lnB=np.log(Lh/(eps+(1-eps)*r['all']))))
T=pd.DataFrame(rows_tab)
ref_sb=T[(T.term=='seabed')&(T.case=='rho 05')]; ref_su=T[(T.term=='surface')&(T.case=='windage 0.5%, POD csiro, floor 0.0')]
print(ref_sb.pivot(index='locality',columns='option',values='lnB').round(2).to_string())
print(ref_su.pivot(index='locality',columns='option',values='lnB').round(2).to_string())
print(T[(T.term=='surface')&(T.option=='D0')&(T.locality.isin(['Tcore','Ccore','strip']))].pivot(index='case',columns='locality',values='lnB').round(2).to_string())