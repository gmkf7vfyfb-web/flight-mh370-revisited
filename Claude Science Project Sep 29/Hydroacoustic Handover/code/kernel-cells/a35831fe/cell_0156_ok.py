from scipy.ndimage import gaussian_filter
k=SDC/C0**2
def L_tdoa(d1_,d2_):
    D=(t74-tH)-(d2_-d1_)/C0; v=SP1**2+SP2**2+(k*(d2_-d1_))**2
    return np.exp(-0.5*D**2/v)/np.sqrt(2*np.pi*v)
LD=L_tdoa(d1,d2)
# grid
gla=np.arange(-42,-29.99,0.05); glo=np.arange(84,100.001,0.05)
def hist_post(W,sm=1.0):
    H,_,_=np.histogram2d(la,lo,bins=[np.append(gla-0.025,gla[-1]+0.025),np.append(glo-0.025,glo[-1]+0.025)],weights=W)
    H=gaussian_filter(H,sm); return H/H.sum()
def hpd_lev(P,q):
    v=np.sort(P.ravel())[::-1]; c=np.cumsum(v); return v[np.searchsorted(c,q)]
res={}
for mdl in ['t3',0.4,1.0]:
    for var,LL in [('arc_tdoa',LD),('arc_time',Lt)]:
        W=wi*LL*L_bear(mdl); W=W/W.sum()
        res[(mdl,var)]=dict(W=W,ess=1/np.sum(W**2),mla=np.sum(W*la),mlo=np.sum(W*lo))
        print(mdl,var,f"ESS {res[(mdl,var)]['ess']:.0f} mean {res[(mdl,var)]['mla']:.2f} {res[(mdl,var)]['mlo']:.2f}")
# acoustic only on grid
GLO,GLA=np.meshgrid(glo,gla)
a_,_,g1=GW.inv(np.full(GLO.size,H1[1]),np.full(GLO.size,H1[0]),GLO.ravel(),GLA.ravel())
_,_,g2=GW.inv(np.full(GLO.size,P74[1]),np.full(GLO.size,P74[0]),GLO.ravel(),GLA.ravel())
g1=g1.reshape(GLO.shape)/1000; g2=g2.reshape(GLO.shape)/1000; ga=np.mod(a_.reshape(GLO.shape),360)
cellA=np.cos(np.radians(GLA))
def ac_only(mdl):
    e=wrap(ga-BRG); Lb=stats.t.pdf(e,3,scale=3.3/np.sqrt(3)) if mdl=='t3' else stats.norm.pdf(e,scale=mdl)
    P=Lb*L_tdoa(g1,g2)*cellA; return P/P.sum()
AC={mdl:ac_only(mdl) for mdl in ['t3',0.4,1.0]}
for mdl,P in AC.items(): print('acoustic only',mdl,'mean',(P*GLA).sum().round(2),(P*GLO).sum().round(2),'P mass inside grid edge rows', P[0].sum()+P[-1].sum()+P[:,0].sum()+P[:,-1].sum())