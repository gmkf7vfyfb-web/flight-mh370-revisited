"""Boeing dive alignment to the 00:19 satellite data. Functions copied verbatim from the 2 Nov 2026
configuration-fit session (frame 6a068bcd, cells a017ed71, 24809111, 54e03370 with sign fix 8856a764, 85a49d2a)."""
import io, zipfile, datetime as dt
import numpy as np, pandas as pd
from scipy.ndimage import uniform_filter1d as uf
from scipy.stats import gamma as gam_
z=zipfile.ZipFile('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/34abc710-f6b1-4f26-8ce8-e6a469d1fb09/v690bbe43_2018-08-19-eof-sims.zip')
T0=dt.datetime(2014,3,8,0,19,29,416000)
lag=gam_(8,scale=14.875)
import numpy as np, pandas as pd
E="repo/Claude Science Project Sep 29/engine/"
eph=pd.read_csv('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/5a18798f-c85c-43df-87e7-00a0af953e55/v737acefd_satellite-ephemeris-inmarsat.csv').set_index("epoch_id")
obs=pd.read_csv('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/ece3c693-f766-4eaa-b69a-3f96d7e18110/v3e39f547_satcom-observations.csv').set_index("epoch_id")
C=299792.458; FUP=1646652500.0; FDN=3615152500.0; PERTH=np.array([-2368.8,4881.1,-3342.0]); KMFT=0.0003048; KMSKT=1.852/3600
a_=6378.137; f_=1/298.257223563; e2=f_*(2-f_)
def lla(lat,lon,h):
    la,lo=np.radians(lat),np.radians(lon); N=a_/np.sqrt(1-e2*np.sin(la)**2)
    return np.array([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-e2)+h)*np.sin(la)])
def basis(lat,lon):
    la,lo=np.radians(lat),np.radians(lon)
    up=np.array([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)]); east=np.array([-np.sin(lo),np.cos(lo),0.]); north=np.cross(up,east)
    return north,east,up
NOM=lla(0,64.5,36210.12)
def ep(i): r=eph.loc[i]; return np.array([r.x_km,r.y_km,r.z_km]),np.array([r.vx_km_s,r.vy_km_s,r.vz_km_s]),obs.loc[i,"satellite_afc_hz"]
def bfo_nb(i,lat,lon,alt_ft,trk,gs_kt,vup_fpm):
    S,V,afc=ep(i); n,e,u=basis(lat,lon)
    hor=(n*np.cos(np.radians(trk))+e*np.sin(np.radians(trk)))*gs_kt*KMSKT; vel=hor+u*vup_fpm*KMFT/60
    ac=lla(lat,lon,alt_ft*KMFT); ts=(S-ac)/np.linalg.norm(S-ac)
    upl=-FUP/C*np.dot(V-vel,ts); g=(S-PERTH)/np.linalg.norm(S-PERTH); dn=-FDN/C*np.dot(V,g)
    fn=(lla(lat,lon,0)-NOM); fn/=np.linalg.norm(fn); comp=FUP/C*np.dot(hor,fn)
    return upl+dn+comp+afc
def bto(i,lat,lon,alt):
    S,_,_=ep(i); ac=lla(lat,lon,alt*KMFT); return 2*(np.linalg.norm(S-ac)+np.linalg.norm(S-PERTH))/C*1e6-(499962.0-4283.0)
def arc_lon(i,lat,alt,b):
    w,ea=65.0,150.0
    for _ in range(60):
        m=0.5*(w+ea); (w,ea)=(m,ea) if bto(i,lat,m,alt)<b else (w,m)
    return 0.5*(w+ea)

EP={i:ep(i) for i in ['m0011','m0019a','m0019b']}
gs_=np.array([0,0,0.])
def lla_v(lat,lon,h):
    la,lo=np.radians(lat),np.radians(lon); N=a_/np.sqrt(1-e2*np.sin(la)**2)
    return np.stack([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-e2)+h)*np.sin(la)],-1)
def basis_v(lat,lon):
    la,lo=np.radians(lat),np.radians(lon)
    up=np.stack([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)],-1); east=np.stack([-np.sin(lo),np.cos(lo),0*lo],-1); north=np.cross(up,east)
    return north,east,up
def bto_v(i,lat,lon,alt_ft):
    S=EP[i][0]; ac=lla_v(lat,lon,alt_ft*KMFT)
    return 2*(np.linalg.norm(S-ac,axis=-1)+np.linalg.norm(S-PERTH))/C*1e6-(499962.0-4283.0)
def bfo_v(i,lat,lon,alt_ft,vn_kt,ve_kt,vup_fpm):
    S,V,afc=EP[i]; n,e,u=basis_v(lat,lon)
    hor=(n*vn_kt[...,None]+e*ve_kt[...,None])*KMSKT; vel=hor+u*(vup_fpm*KMFT/60)[...,None]
    ac=lla_v(lat,lon,alt_ft*KMFT); d=S-ac; ts=d/np.linalg.norm(d,axis=-1,keepdims=True)
    upl=-FUP/C*np.sum((V-vel)*ts,-1); g=(S-PERTH)/np.linalg.norm(S-PERTH); dn=-FDN/C*np.dot(V,g)
    fn=lla_v(lat,lon,0*lat)-NOM; fn/=np.linalg.norm(fn,axis=-1,keepdims=True); comp=FUP/C*np.sum(hor*fn,-1)
    return upl+dn+comp+afc

def run_raw(n):
    df=pd.read_csv(io.BytesIO(z.read(n))).dropna(); df.columns=["t","x","y","h"]
    t=df.t.values.astype(float); x=uf(df.x.values,7,mode="nearest"); y=uf(df.y.values,7,mode="nearest"); h=df.h.values.astype(float)
    ve=np.gradient(x,t)*3600; vn=np.gradient(y,t)*3600; hs=uf(h,3,mode="nearest"); vu=np.gradient(hs,t)*60
    return dict(t=t,e=x,n=y,h=h,ve=ve,vn=vn,vu=vu)
def splice(R,tu,t1=None,g=None,s_min=-1500):
    """real-time axis s (s rel. power loss) -> e,n,h,ve,vn,vu. Normal with g: cruise..., one-engine run[t1,t1+g], then run[tu:]"""
    t=R["t"]; s=np.arange(s_min,int(t[-1]-tu)-6)
    out={k:np.empty(len(s)) for k in ["e","n","h","ve","vn","vu"]}
    def seg_idx(tt): return np.clip(np.round(tt).astype(int),0,len(t)-1)
    if g is None:
        tau=s+tu; inrun=tau>=t[0]; i=seg_idx(tau)
        for k in ["h","ve","vn","vu"]: out[k]=np.where(inrun,R[k][i],R[k][0] if k!="vu" else 0.0)
        out["h"]=np.where(inrun,R["h"][i],R["h"][0])
        e0,n0=R["e"][0],R["n"][0]; dtb=np.minimum(tau-t[0],0)
        out["e"]=np.where(inrun,R["e"][i],e0+R["ve"][0]/3600*dtb); out["n"]=np.where(inrun,R["n"][i],n0+R["vn"][0]/3600*dtb)
        return s,out
    # normal with gap g (s): segment A cruise s< -g ; B one-engine s in [-g,0): tau=t1+g+s ; C s>=0: tau=tu+s
    A=s<-g; Bm=(s>=-g)&(s<0); Cm=s>=0
    iB=seg_idx(t1+g+s); iC=seg_idx(tu+s); i1=seg_idx(np.array([t1]))[0]
    for k in ["h","ve","vn","vu"]:
        out[k]=np.where(Cm,R[k][iC],np.where(Bm,R[k][iB],R[k][i1] if k!="vu" else 0.0))
    # positions: continuous chaining
    eB=R["e"][iB]-R["e"][i1]; nB=R["n"][iB]-R["n"][i1]
    iBend=seg_idx(np.array([t1+g]))[0]; eBend=R["e"][iBend]-R["e"][i1]; nBend=R["n"][iBend]-R["n"][i1]
    itu=seg_idx(np.array([tu]))[0]; eC=R["e"][iC]-R["e"][itu]+eBend; nC=R["n"][iC]-R["n"][itu]+nBend
    dtA=s+g; eA=R["ve"][i1]/3600*dtA; nA=R["vn"][i1]/3600*dtA
    out["e"]=np.where(Cm,eC,np.where(Bm,eB,eA)); out["n"]=np.where(Cm,nC,np.where(Bm,nB,nA))
    return s,out
DT11=(T0-dt.datetime(2014,3,8,0,10,59)).total_seconds(); DT37=8.027
LATS=np.arange(-40,-29.95,0.1); ROT=np.arange(-30,31,2.0); LAGS=np.arange(40,401,2)
arc11={}
def arc6(lat,alt):
    k=(round(lat,2),int(alt//1000))
    if k not in arc11: arc11[k]=arc_lon('m0011',lat,alt,18040.0)
    return arc11[k]
OBS={"b11":252.0,"b29":182.0,"b37":-2.0,"T29":18400.0,"T37":18380.0}; SB=7.0; SBIAS=5.0
def score_path(s,P,version):
    res=[]
    for L in LAGS:
        i11=np.searchsorted(s,L-DT11); i29=np.searchsorted(s,L); i37=np.searchsorted(s,L+DT37)
        if i11<=0 or i37>=len(s)-1: continue
        h11=P["h"][i11]; lon0s=np.array([arc6(la,h11) for la in LATS])
        for th in ROT:
            c,sn=np.cos(np.radians(th)),np.sin(np.radians(th))
            def rot(e,n): return e*c+n*sn, -e*sn+n*c   # rotate clockwise by th (track +th)
            st={}
            for nm,i in [("11",i11),("29",i29),("37",i37)]:
                de,dn=rot(P["e"][i]-P["e"][i11],P["n"][i]-P["n"][i11]); ve,vn=rot(P["ve"][i],P["vn"][i])
                lat=LATS+dn/60.0; lon=lon0s+de/(60.0*np.cos(np.radians(LATS)))
                st[nm]=(lat,lon,P["h"][i],ve,vn,P["vu"][i])
            def pB(nm,ep_):
                lat,lon,h,ve,vn,vu=st[nm]; return bfo_v(ep_,lat,lon,np.full_like(lat,h),np.full_like(lat,vn),np.full_like(lat,ve),np.full_like(lat,vu))
            p11,p29,p37=pB("11","m0011"),pB("29","m0019a"),pB("37","m0019b")
            T29=bto_v("m0019a",st["29"][0],st["29"][1],np.full_like(LATS,st["29"][2])); T37=bto_v("m0019b",st["37"][0],st["37"][1],np.full_like(LATS,st["37"][2]))
            # profile bias (and Holland transient terms)
            D=np.zeros_like(LATS); d=np.zeros_like(LATS); b=np.full_like(LATS,150.0)
            for _ in range(8):
                y11=OBS["b11"]-p11; y29=OBS["b29"]-D-p29; y37=OBS["b37"]-D+d-p37
                b=((y11+y29+y37)/SB**2+150/SBIAS**2)/(3/SB**2+1/SBIAS**2)
                if version=="holland":
                    D=np.clip(((OBS["b29"]-p29-b)+(OBS["b37"]+d-p37-b))/2,17,136)
                    d=np.clip(D+p37+b-OBS["b37"],0,6)
            e11=OBS["b11"]-p11-b; e29=OBS["b29"]-D-p29-b; e37=OBS["b37"]-D+d-p37-b
            chi_bfo=(e11**2+e29**2+e37**2)/SB**2+((b-150)/SBIAS)**2
            chi_bto=((OBS["T29"]-T29)/63.0)**2+((OBS["T37"]-T37)/43.0)**2
            lp=-2*lag.logpdf(L)+2*lag.logpdf(lag.mean())
            tot=chi_bfo+chi_bto+lp; k=int(np.argmin(tot))
            res.append(dict(L=L,rot=th,lat11=LATS[k],tot=tot[k],chi_bfo=chi_bfo[k],chi_bto=chi_bto[k],lag_pen=lp,bias=b[k],D29=D[k],d=d[k],
                            e11=e11[k],e29=e29[k],e37=e37[k],rT29=OBS["T29"]-T29[k],rT37=OBS["T37"]-T37[k],
                            vu11=P["vu"][i11],vu29=P["vu"][i29],vu37=P["vu"][i37],h29=P["h"][i29],lat29=st["29"][0][k],lon29=st["29"][1][k],
                            trk29=(np.degrees(np.arctan2(*rot(P["ve"][i29],P["vn"][i29])))%360),gs29=np.hypot(P["ve"][i29],P["vn"][i29])))
    return pd.DataFrame(res)
