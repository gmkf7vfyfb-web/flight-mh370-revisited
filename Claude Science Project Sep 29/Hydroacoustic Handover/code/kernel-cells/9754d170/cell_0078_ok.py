
h11=pd.read_csv(HB+"results-data/ram_check/h11_tl_ramcorr.csv"); cal=pd.read_csv(HB+"results-data/ram_check/eta_cal_ramcorr.csv")
F35B=[5.0,6.3,8.0,10.0,12.5,16.0,20.0,25.0,31.5,40.0]
def bandfrac(fc,fr,slope):
    f=np.logspace(0,np.log10(500),20001)
    esd=np.where(f<=fr,1.0,(f/fr)**(-slope)); tot=np.trapezoid(esd,f)
    m=(f>=fc*2**(-1/6))&(f<=fc*2**(1/6)); return np.trapezoid(esd[m],f[m])/tot
RHO_C=1025*1500.; R={'T_C2':3.012910065398646,'T_C1':1.4198208271811392}
chk=[]
for st in ['H11N','H11S']:
    for zs in [2.0,10.0,30.0]:
        g=h11[(h11.station==st)&(h11.src_depth_m==zs)].set_index('fc_hz').tl_db
        for tau in [0.05, 1.0, 10.0]:
            gain=sum(bandfrac(fc,1/tau,2)*10**(-g[fc]/10) for fc in F35B)
            eta=(0.7**2/R['T_C2'])/(900e6*RHO_C/(2*np.pi)*gain)
            c=cal[(cal.slope==2)&(cal.station==st)&(cal.src_depth_m==zs)&(cal.template=='T_C2')&(cal.E_case=='mid')]
            ce=float(np.interp(np.log10(tau),np.log10(c.tau_s),np.log10(c.eta_cal)))
            chk.append((st,zs,tau,eta,10**ce,10*(np.log10(eta)-ce)))
chk=pd.DataFrame(chk,columns=['st','zs','tau','eta_audit','eta_module','diff_dB']); print(chk.to_string())
# Brown arithmetic
W=(3.3e6/ (52.4e6/0.7)**(1/1.13))**3; print('Brown Arons W kg TNT',W,'E J',W*4.184e6,'eta',W*4.184e6/900e6)
