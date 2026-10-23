EX='/Users/pete/Downloads/mh370-exchange/'
MP3=np.load(EX+'composer/run-j-views-v3.2/maps-v3.npz')
NY,NX=int(MP3['NY']),int(MP3['NX'])
STEP=0.25; LAT0=-50.0; LON0=78.0; Ea=0.00669437999014; Ee=np.sqrt(Ea)
def aq(latd):
    s_=np.sin(np.radians(latd)); return (1-Ea)*(s_/(1-Ea*s_*s_)-np.log((1-Ee*s_)/(1+Ee*s_))/(2*Ee))
QS=aq(STEP)-aq(0.0); Q0=aq(LAT0)
def invq(q):
    lo_,hi_=np.full_like(q,-90.0),np.full_like(q,90.0)
    for _ in range(80):
        mid=0.5*(lo_+hi_); up=aq(mid)<q; lo_=np.where(up,mid,lo_); hi_=np.where(up,hi_,mid)
    return 0.5*(lo_+hi_)
ROW_E=invq(Q0+np.arange(NY+1)*QS); LON_E=LON0+np.arange(NX+1)*STEP
assert NY==int(np.ceil((aq(-6.0)-Q0)/QS)) and NX==152
mapS=MP3['D0|S'].astype(float).reshape(NY,NX); mapC=MP3['D0|core'].astype(float).reshape(NY,NX)
print(mapS.sum(), mapC.sum())
F_=np.load(EX+'searched-areas/spatial-fields-v2/fields.npz')
fs,fw,fst=float(F_['south']),float(F_['west']),float(F_['step'])
p2=F_['p2']; oi18=F_['oi2018']; oi25=F_['oi2025']
flat=fs+(np.arange(p2.shape[0])+0.5)*fst; flon=fw+(np.arange(p2.shape[1])+0.5)*fst
r_,c_=np.where(p2>0.5); print('p2 covered lat range', flat[r_].min(), flat[r_].max(), 'lon', flon[c_].min(), flon[c_].max())
r_,c_=np.where(oi25>0.5); print('oi25 lat range', flat[r_].min(), flat[r_].max())
PM=np.load(EX+'pleiades/run-j/maps/map-D0.npz'); post=PM['post'].astype(float); pre=PM['pre'].astype(float)
plat=-44.975+np.arange(800)*0.05; plon=78.025+np.arange(740)*0.05
r_,c_=np.unravel_index(np.argmax(post),post.shape); print('pleiades post max at', plat[r_], plon[c_], post.sum(), pre.sum())
plei=pd.read_csv(io.StringIO(subprocess.run(['git','-C','main','show','HEAD:ISO Sept 28 Status/inputs/recovered-v01/.sources/pleiades-bran2016-forward-inversion/data/pleiades-rating5-objects.csv'],capture_output=True,text=True).stdout)) if False else None