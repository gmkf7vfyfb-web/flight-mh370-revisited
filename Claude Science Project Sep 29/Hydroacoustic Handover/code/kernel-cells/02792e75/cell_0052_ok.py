try:
    from geographiclib.geodesic import Geodesic; print("geographiclib ok")
except Exception as e: print("no geographiclib",e)
G=Geodesic.WGS84
C=299792.458; GES=np.array([-2368.8,4881.1,-3342.0]); OFF=499962.0-4283.0
SAT=np.array([18178.3537,38050.8487,393.0782]); a_=6378.137; f_=1/298.257223563; e2=f_*(2-f_)
def ecef(lat,lon,h=0):
    la,lo=np.radians(lat),np.radians(lon); N=a_/np.sqrt(1-e2*np.sin(la)**2)
    return np.stack([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-e2)+h)*np.sin(la)],-1)
def bto(lat,lon,h=0):
    p=ecef(lat,lon,h); return 2*(np.linalg.norm(SAT-p,axis=-1)+np.linalg.norm(SAT-GES))/C*1e6-OFF
print("check crossing bto",bto(-25.732,101.369), "Haixun",bto(-25.975,101.461))
H01=(-34.8903,114.1426)
def bearing_line(az,s0=1200,s1=1900,n=200):
    L=G.Line(H01[0],H01[1],az); pts=[L.Position(s*1e3) for s in np.linspace(s0,s1,n)]; return np.array([[p['lat2'],p['lon2']] for p in pts])
# second contact: 3 km west of first (ATSB 2017 p.38)
p=G.Direct(HX[0],HX[1],270,3000); HX2=(p['lat2'],p['lon2'])
inv=lambda A,B: G.Inverse(A[0],A[1],B[0],B[1])
geo={"haixun1":HX,"haixun2_3kmW":HX2,"crossing":XC,
 "d_h1_cross_km":inv(HX,XC)['s12']/1e3,"d_h2_cross_km":inv(HX2,XC)['s12']/1e3,
 "az_h01_to_h1":inv(H01,HX)['azi1'],"az_h01_to_h2":inv(H01,HX2)['azi1'],
 "range_h01_h1_km":inv(H01,HX)['s12']/1e3,"range_h01_h2_km":inv(H01,HX2)['s12']/1e3,
 "bto_h1":float(bto(*HX)),"bto_h2":float(bto(*HX2)),"perth_h1_km":inv((-31.9505,115.8605),HX)['s12']/1e3}
print({k:(np.round(v,4) if not isinstance(v,tuple) else tuple(np.round(v,4))) for k,v in geo.items()})