def hav(lat1,lon1,lat2,lon2):
    R=6371.0; p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1); dp=p2-p1
    a=np.sin(dp/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2; return 2*R*np.arcsin(np.sqrt(a))
HX=(-25.975,101.461); XC=(-25.732,101.369)
def boxdist(r,P):
    la=min(max(P[0],r.latmin),r.latmax); lo=min(max(P[1],r.lonmin),r.lonmax); return hav(P[0],P[1],la,lo)
df["d_haixun_km"]=df.apply(lambda r: boxdist(r,HX),axis=1); df["d_cross_km"]=df.apply(lambda r: boxdist(r,XC),axis=1)
print(df.groupby("date")[["d_haixun_km","d_cross_km"]].min().round(0))
print("Perth-Haixun km",round(hav(-31.95,115.86,*HX),0),"Perth-crossing",round(hav(-31.95,115.86,*XC),0))
os.makedirs("out",exist_ok=True)
df.to_csv("out/csda_maxar_records_SE_indian_ocean_2014.csv",index=False)