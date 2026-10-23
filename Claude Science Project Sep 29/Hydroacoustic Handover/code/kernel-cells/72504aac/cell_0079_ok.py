
src6=src6.replace("xytext=(-10,60),textcoords='offset points',fontsize=6.5,color=C_G,ha='center'","xytext=(50,-60),textcoords='offset points',fontsize=6.5,color=C_G,ha='left'")
exec(src6); fig=chart6(); save(fig,'chart6-neighbourhood-pair-g'); plt.close('all')
R=ROUTES.reshape(-1,38,2); f=RI.f150.fillna(0).values
t_route=hms2s('18:01:49')-86400+np.arange(38)*600   # seconds relative to 00:00 8 Mar (negative before midnight)
t2241=hms2s('22:41:00')-86400
k0=25  # 22:11:49
la,lo=R[:,:,0],R[:,:,1]
faz,_,dist=G84.inv(lo[:,:-1].ravel(),la[:,:-1].ravel(),lo[:,1:].ravel(),la[:,1:].ravel())
TRK=(faz%360).reshape(len(R),37); GS=(dist/600/0.514444).reshape(len(R),37)
tmid=(t_route[:-1]+300-t2241)/60
def wqs(x,w,qs):
    o=np.argsort(x); c=np.cumsum(w[o]); c/=c[-1]; return [x[o][np.searchsorted(c,q)] for q in qs]
ix=np.arange(k0,37)
band={}
for nm,w in [('near',f),('rest',1-f)]:
    band[nm]={v:np.array([wqs(A[:,i],w,[0.1,0.5,0.9]) for i in ix]) for v,A in [('trk',TRK),('gs',GS)]}
near=f>=0.5; print(near.sum(), len(f), f.sum(), (1-f).sum())
print(band['near']['trk'][:,1].round(0), band['rest']['trk'][:,1].round(0)); print(band['near']['gs'][:,1].round(0), band['rest']['gs'][:,1].round(0))
