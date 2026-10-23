T_REF=W.T_REF; T19A=T_REF+19*60+29
# bias variance per parent for BFO sigma
Vmap={}
for st in ['run-j-waypoints','run-j-free','run-j-repro-radar','run-j-descent-climb']:
    for s in sorted(M[M.stratum==st].seed.unique()):
        Vmap[(st,s)]=np.load(f'/Users/pete/Downloads/mh370-exchange/core/run-j/{st}/bto-bfo/seed-{s}/handoff-m0011/handoff.npy',mmap_mode='r')[:,9]
def addV(df):
    V=np.full(len(df),np.nan)
    for (st,s),idx in df.groupby(['stratum','seed']).indices.items():
        if (st,s) in Vmap: V[idx]=np.asarray(Vmap[(st,s)])[df.parent.values[idx].astype(int)]
    return V
GES=np.array([-2368.8,4881.1,-3342.0]); SAT=np.array([18178.3537,38050.8487,393.0782]); OFF=499962.0-4283.0
def bto_sl(lat,lon):
    a=6378.137; f=1/298.257223563; e2=f*(2-f); la,lo=np.radians(lat),np.radians(lon); N=a/np.sqrt(1-e2*np.sin(la)**2)
    P=np.stack([N*np.cos(la)*np.cos(lo),N*np.cos(la)*np.sin(lo),N*(1-e2)*np.sin(la)],-1)
    return 2*(np.linalg.norm(SAT-P,axis=-1)+np.linalg.norm(SAT-GES))/299792.458*1e6-OFF
def derive(df):
    df['t_imp_min']=(df.unix_s-T_REF)/60; df['t_after_0019a_min']=(df.unix_s-T19A)/60
    fo=df['latent:realised_flameout_unix_s']; df['fo_min']=(fo-T_REF)/60
    df['powered_at_impact']=~np.isfinite(fo)|(fo>df.unix_s)
    df['aloft_after_fo_min']=np.where(df.powered_at_impact,np.nan,(df.unix_s-fo)/60)
    df['fo_after_0019a']=np.isfinite(fo)&(fo>T19A)
    df['speed_mps']=np.sqrt(df.velocity_east_mps**2+df.velocity_north_mps**2+df.velocity_up_mps**2)
    df['turns']=df['latent:turns_davey_begun'].fillna(0)+df['latent:turns_terminal_begun'].fillna(0)
    df['bto_arc_us']=bto_sl(df.latitude_deg.values,df.longitude_deg.values)-18400.0
    df['along_bearing_km']=df.d_km-W.R7
    df['z_bto19a']=df['bto_residual_us:m0019a']/63.0; df['z_bto19b']=df['bto_residual_us:m0019b']/43.0
    df['vs19a']=df['latent:state_m0019a_vertical_speed_fpm']; df['vs19b']=df['latent:state_m0019b_vertical_speed_fpm']
    df['onset_min']=(df['latent:onset_unix_s']-T_REF)/60; df['takeover_min']=(df.takeover_unix_s-T_REF)/60
    return df
M=derive(M); M['V']=addV(M); s1,s2=4.3177,4.3177
M['z_bfo19a']=M['bfo_innovation_hz:m0019a']/np.sqrt(M.V+s1**2); M['z_bfo19b']=M['bfo_innovation_hz:m0019b']/np.sqrt(M.V+s2**2)
Jd=derive(Jd)
print(M[['t_imp_min','fo_min','aloft_after_fo_min','turns','bto_arc_us','z_bfo19a','z_bfo19b','vs19b']].describe().round(2).to_string())